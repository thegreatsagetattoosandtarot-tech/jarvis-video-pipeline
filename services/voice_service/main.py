#!/usr/bin/env python3
"""
J.A.R.V.I.S. OS - Voice Pipeline Service
Unified voice service integrating: Wake Word -> STT -> Intent -> TTS -> Audio Out
With real-time interruption handling (barge-in)
"""

import os
import sys
import asyncio
import threading
import time
import signal
from pathlib import Path
from typing import Callable, Optional, Dict, Any, Generator
from dataclasses import dataclass
from enum import Enum
import numpy as np

# Add paths
JARVIS_ROOT = Path("/opt/data/JARVIS_OS")
sys.path.insert(0, str(JARVIS_ROOT))
sys.path.insert(0, str(JARVIS_ROOT / "skills" / "core" / "voice-pipeline"))

# Configuration
from config.voice import load_voice_config


class PipelineState(Enum):
    """Voice pipeline states."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    THINKING = "thinking"
    SPEAKING = "speaking"
    INTERRUPTED = "interrupted"


@dataclass
class VoiceConfig:
    """Voice pipeline configuration."""
    # Wake word
    wake_keyword: str = "jarvis"
    wake_sensitivity: float = 0.7
    access_key: Optional[str] = None
    custom_keyword_path: Optional[str] = None

    # STT
    stt_model: str = "base"
    stt_language: str = "en"
    stt_device: str = "cpu"

    # TTS
    tts_voice: str = "en_GB-alan-medium"
    tts_length_scale: float = 1.0

    # VAD
    vad_aggressiveness: int = 2
    min_speech_duration: float = 0.5
    max_silence_duration: float = 1.5

    # Interruption
    enable_interruption: bool = True
    interruption_threshold: float = 0.3

    # Audio
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    sample_rate: int = 16000


class WakeWordDetector:
    """Wake word detection using Porcupine."""

    BUILTIN_KEYWORDS = ["jarvis", "hey google", "alexa", "porcupine", "bumblebee", "computer", "hey siri", "ok google", "picovoice", "terminator"]

    def __init__(self, config: VoiceConfig, on_detected: Optional[Callable] = None):
        self.config = config
        self.on_detected = on_detected
        self.access_key = config.access_key or os.environ.get("PICOVOICE_ACCESS_KEY")
        self.handle = None
        self.sample_rate = None
        self.frame_length = None
        self._stream = None
        self._stop_event = threading.Event()
        self._worker_thread = None
        self.input_device = config.input_device

    def initialize(self) -> bool:
        """Initialize Porcupine."""
        try:
            import pvporcupine

            if self.config.wake_keyword == "custom" and self.config.custom_keyword_path:
                self.handle = pvporcupine.create(
                    access_key=self.access_key,
                    keyword_paths=[self.config.custom_keyword_path],
                    sensitivities=[self.config.wake_sensitivity]
                )
            else:
                self.handle = pvporcupine.create(
                    access_key=self.access_key,
                    keywords=[self.config.wake_keyword],
                    sensitivities=[self.config.wake_sensitivity]
                )

            self.sample_rate = self.handle.sample_rate
            self.frame_length = self.handle.frame_length
            print(f"Porcupine initialized: keyword='{self.config.wake_keyword}', sample_rate={self.sample_rate}")
            return True
        except Exception as e:
            print(f"Porcupine initialization failed: {e}")
            return False

    def start(self) -> bool:
        """Start wake word detection."""
        if not self.handle:
            if not self.initialize():
                return False

        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self._worker_thread.start()
        print(f"Wake word detection started: '{self.config.wake_keyword}'")
        return True

    def stop(self):
        """Stop wake word detection."""
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=2.0)
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        print("Wake word detection stopped")

    def _detection_loop(self):
        """Main detection loop."""
        try:
            import sounddevice as sd

            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=self.frame_length,
                device=self.input_device,
                channels=1,
                dtype='int16',
                callback=self._audio_callback
            )

            with self._stream:
                while not self._stop_event.is_set():
                    time.sleep(0.1)
        except Exception as e:
            print(f"Detection loop error: {e}")

    def _audio_callback(self, indata, frames, time_info, status):
        """Process audio frames for wake word detection."""
        if status:
            print(f"Audio callback status: {status}")

        pcm = indata[:, 0] if indata.ndim > 1 else indata

        try:
            result = self.handle.process(pcm)
            if result >= 0:
                print(f"Wake word detected! (index: {result})")
                if self.on_detected:
                    self.on_detected()
        except Exception as e:
            print(f"Processing error: {e}")


class WhisperSTT:
    """Local speech-to-text using Whisper."""

    MODEL_SIZES = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]

    def __init__(self, config: VoiceConfig, on_transcription: Optional[Callable[[str], None]] = None):
        if config.stt_model not in self.MODEL_SIZES:
            raise ValueError(f"model_size must be one of {self.MODEL_SIZES}")

        self.config = config
        self.on_transcription = on_transcription
        self.model = None
        self.is_loaded = False
        self._load_lock = threading.Lock()
        self.sample_rate = 16000

    def load_model(self) -> bool:
        """Load Whisper model (thread-safe, loads once)."""
        with self._load_lock:
            if self.is_loaded:
                return True

            try:
                import whisper
                print(f"Loading Whisper model: {self.config.stt_model} on {self.config.stt_device}...")
                self.model = whisper.load_model(self.config.stt_model, device=self.config.stt_device)
                self.is_loaded = True
                print("Whisper model loaded successfully")
                return True
            except Exception as e:
                print(f"Failed to load Whisper model: {e}")
                return False

    def transcribe_audio(self, audio_data: np.ndarray) -> Optional[str]:
        """Transcribe numpy audio array."""
        if not self.is_loaded:
            if not self.load_model():
                return None

        try:
            import warnings
            # Ensure audio is float32 and normalized
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            if np.max(np.abs(audio_data)) > 1.0:
                audio_data = audio_data / 32768.0

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = self.model.transcribe(
                    audio_data,
                    language=self.config.stt_language if self.config.stt_language != "auto" else None,
                    fp16=(self.config.stt_device == "cuda"),
                    verbose=False
                )

            text = result.get("text", "").strip()

            if text and self.on_transcription:
                self.on_transcription(text)

            return text if text else None

        except Exception as e:
            print(f"Transcription error: {e}")
            return None


class StreamingSTT:
    """Streaming STT with VAD integration."""

    def __init__(
        self,
        stt: WhisperSTT,
        config: VoiceConfig,
        on_speech_start: Optional[Callable] = None,
        on_speech_end: Optional[Callable[[str], None]] = None
    ):
        self.stt = stt
        self.config = config
        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end

        self.vad = None
        self.sample_rate = 16000
        self.frame_duration = 30  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)

        self._initialize_vad()

    def _initialize_vad(self):
        """Initialize WebRTC VAD."""
        try:
            import webrtcvad
            self.vad = webrtcvad.Vad(self.config.vad_aggressiveness)
        except Exception as e:
            print(f"VAD initialization failed: {e}")

    def process_stream(self, audio_stream: Generator[bytes, None, None], stop_event: threading.Event):
        """Process audio stream with VAD + STT."""
        if not self.vad:
            return

        speech_buffer = []
        silence_frames = 0
        speech_frames = 0
        in_speech = False
        max_silence_frames = int(self.config.max_silence_duration * 1000 / self.frame_duration)
        min_speech_frames = int(self.config.min_speech_duration * 1000 / self.frame_duration)

        for frame_bytes in audio_stream:
            if stop_event.is_set():
                break

            try:
                is_speech = self.vad.is_speech(frame_bytes, self.sample_rate)
            except:
                is_speech = False

            if is_speech:
                if not in_speech:
                    in_speech = True
                    silence_frames = 0
                    speech_frames = 0
                    if self.on_speech_start:
                        self.on_speech_start()

                speech_buffer.append(frame_bytes)
                speech_frames += 1
            else:
                silence_frames += 1

                if in_speech:
                    speech_buffer.append(frame_bytes)

                    if silence_frames >= max_silence_frames:
                        # End of utterance
                        if speech_frames >= min_speech_frames:
                            self._process_utterance(speech_buffer)

                        speech_buffer = []
                        silence_frames = 0
                        speech_frames = 0
                        in_speech = False

    def _process_utterance(self, frames: list):
        """Process accumulated speech frames."""
        try:
            audio_bytes = b"".join(frames)
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            text = self.stt.transcribe_audio(audio_data)
            if text and self.on_speech_end:
                self.on_speech_end(text)
        except Exception as e:
            print(f"Utterance processing error: {e}")


class PiperTTS:
    """Text-to-speech using Piper."""

    JARVIS_VOICE = "en_GB-alan-medium"

    def __init__(
        self,
        config: VoiceConfig,
        on_audio_ready: Optional[Callable[[np.ndarray], None]] = None
    ):
        self.config = config
        self.on_audio_ready = on_audio_ready
        self.voice = config.tts_voice
        self.length_scale = config.tts_length_scale
        self._piper_binary = None
        self._voice_path = None

    def check_voice(self) -> bool:
        """Check if voice model exists."""
        try:
            from piper import PiperVoice
            voice = PiperVoice.load(self.voice)
            self._voice_path = voice.config_path
            return True
        except:
            return False

    def download_voice(self) -> bool:
        """Download voice model."""
        try:
            import urllib.request
            from piper import PiperVoice
            voice = PiperVoice.load(self.voice)
            print(f"Voice {self.voice} downloaded")
            return True
        except Exception as e:
            print(f"Voice download failed: {e}")
            return False

    def synthesize(self, text: str) -> Optional[np.ndarray]:
        """Synthesize text to audio."""
        try:
            from piper import PiperVoice
            import soundfile as sf
            import io

            voice = PiperVoice.load(self.voice)

            # Synthesize to bytes
            audio_bytes = io.BytesIO()
            with sf.SoundFile(audio_bytes, mode='w', samplerate=voice.config.sample_rate, channels=1, format='WAV') as f:
                voice.synthesize(text, f, length_scale=self.length_scale)

            # Read back as numpy
            audio_bytes.seek(0)
            with sf.SoundFile(audio_bytes) as f:
                audio_data = f.read(dtype=np.float32)

            if self.on_audio_ready:
                self.on_audio_ready(audio_data)

            return audio_data

        except Exception as e:
            print(f"Synthesis error: {e}")
            return None


class StreamingTTS:
    """Streaming TTS with playback."""

    def __init__(
        self,
        tts: PiperTTS,
        on_playback_start: Optional[Callable] = None,
        on_playback_end: Optional[Callable] = None
    ):
        self.tts = tts
        self.on_playback_start = on_playback_start
        self.on_playback_end = on_playback_end
        self._queue = asyncio.Queue()
        self._worker_task = None
        self._stop_event = asyncio.Event()

    async def start(self):
        """Start streaming TTS worker."""
        self._stop_event.clear()
        self._worker_task = asyncio.create_task(self._worker())

    async def stop(self):
        """Stop streaming TTS worker."""
        self._stop_event.set()
        await self._queue.put(None)  # Sentinel
        if self._worker_task:
            await self._worker_task

    async def queue_text(self, text: str):
        """Queue text for synthesis and playback."""
        await self._queue.put(text)

    async def _worker(self):
        """Background worker for synthesis and playback."""
        import sounddevice as sd

        while not self._stop_event.is_set():
            try:
                text = await asyncio.wait_for(self._queue.get(), timeout=0.1)
                if text is None:
                    break

                if self.on_playback_start:
                    self.on_playback_start()

                # Synthesize
                audio = self.tts.synthesize(text)

                if audio is not None:
                    # Play audio
                    sd.play(audio, samplerate=22050)
                    sd.wait()

                if self.on_playback_end:
                    self.on_playback_end()

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"TTS worker error: {e}")


class VoicePipelineService:
    """Complete J.A.R.V.I.S. voice pipeline service."""

    def __init__(self, config: VoiceConfig, response_generator: Optional[Callable[[str], str]] = None):
        self.config = config
        self.response_generator = response_generator or self._default_response
        self.state = PipelineState.IDLE

        # Callbacks
        self.on_wake: Optional[Callable] = None
        self.on_listening: Optional[Callable] = None
        self.on_transcription: Optional[Callable[[str], None]] = None
        self.on_response: Optional[Callable[[str], None]] = None
        self.on_state_change: Optional[Callable[[PipelineState], None]] = None

        # Components
        self.wake_detector: Optional[WakeWordDetector] = None
        self.stt: Optional[WhisperSTT] = None
        self.streaming_stt: Optional[StreamingSTT] = None
        self.tts: Optional[PiperTTS] = None
        self.streaming_tts: Optional[StreamingTTS] = None

        # Interruption
        self._interruption_detected = False
        self._interruption_thread = None
        self._vad = None

        # Threading
        self._stop_event = threading.Event()
        self._main_thread = None

    def _default_response(self, user_input: str) -> str:
        """Default response generator."""
        responses = {
            "hello": "Yes Sir. How may I assist you?",
            "time": "The current time is...",
            "status": "All systems operational, Sir.",
            "shutdown": "Shutting down. Good night, Sir.",
        }
        user_lower = user_input.lower().strip()
        for key, resp in responses.items():
            if key in user_lower:
                return resp
        return f"Understood. You said: {user_input}. How shall I proceed?"

    def _set_state(self, state: PipelineState):
        """Update pipeline state."""
        if self.state != state:
            print(f"[STATE] {self.state.value} -> {state.value}")
            self.state = state
            if self.on_state_change:
                self.on_state_change(state)

    def initialize(self) -> bool:
        """Initialize all pipeline components."""
        print("Initializing J.A.R.V.I.S. Voice Pipeline Service...")

        # 1. Wake Word Detector
        print("  [1/4] Wake Word Detector...")
        self.wake_detector = WakeWordDetector(self.config, on_detected=self._on_wake_detected)
        if not self.wake_detector.initialize():
            return False

        # 2. STT
        print("  [2/4] Speech-to-Text (Whisper)...")
        self.stt = WhisperSTT(self.config, on_transcription=self._on_transcription)
        if not self.stt.load_model():
            return False

        self.streaming_stt = StreamingSTT(
            self.stt,
            self.config,
            on_speech_start=self._on_speech_start,
            on_speech_end=self._on_speech_end
        )

        # 3. TTS
        print("  [3/4] Text-to-Speech (Piper)...")
        self.tts = PiperTTS(self.config, on_audio_ready=self._on_tts_audio)

        if not self.tts.check_voice():
            print(f"  Downloading voice: {self.config.tts_voice}...")
            if not self.tts.download_voice():
                print("  Warning: Voice download failed, continuing anyway")

        # 4. Streaming TTS
        self.streaming_tts = StreamingTTS(
            self.tts,
            on_playback_start=self._on_playback_start,
            on_playback_end=self._on_playback_end
        )

        # 5. Interruption VAD
        print("  [4/4] Interruption Detection...")
        self._init_interruption_vad()

        # 6. Audio devices
        self._check_audio_devices()

        print("Voice Pipeline Service initialized successfully!")
        return True

    def _init_interruption_vad(self):
        """Initialize VAD for interruption detection."""
        try:
            import webrtcvad
            self._vad = webrtcvad.Vad(self.config.vad_aggressiveness)
        except Exception as e:
            print(f"Interruption VAD init failed: {e}")

    def _check_audio_devices(self):
        """Check available audio devices."""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            print("  Available input devices:")
            for i, d in enumerate(devices):
                if d['max_input_channels'] > 0:
                    print(f"    [{i}] {d['name']} ({d['max_input_channels']} ch)")
            print("  Available output devices:")
            for i, d in enumerate(devices):
                if d['max_output_channels'] > 0:
                    print(f"    [{i}] {d['name']} ({d['max_output_channels']} ch)")
        except Exception as e:
            print(f"Device check failed: {e}")

    async def start(self):
        """Start the voice pipeline service."""
        if self._main_thread and self._main_thread.is_alive():
            return

        self._stop_event.clear()
        self._set_state(PipelineState.IDLE)

        # Start wake word detection
        if self.wake_detector:
            self.wake_detector.start()

        # Start streaming TTS
        if self.streaming_tts:
            await self.streaming_tts.start()

        # Start main loop
        self._main_thread = threading.Thread(target=self._main_loop, daemon=True)
        self._main_thread.start()

        print("Voice Pipeline Service started. Say 'Jarvis' to activate.")

    async def stop(self):
        """Stop the voice pipeline service."""
        print("Stopping Voice Pipeline Service...")
        self._stop_event.set()

        if self.wake_detector:
            self.wake_detector.stop()

        if self.streaming_tts:
            await self.streaming_tts.stop()

        if self._main_thread:
            self._main_thread.join(timeout=3.0)

        print("Voice Pipeline Service stopped")

    def _main_loop(self):
        """Main monitoring loop."""
        while not self._stop_event.is_set():
            time.sleep(0.5)

    # --- Wake Word Callback ---
    def _on_wake_detected(self):
        """Wake word detected - transition to listening."""
        if self.state != PipelineState.IDLE:
            return

        self._set_state(PipelineState.LISTENING)

        if self.on_wake:
            self.on_wake()
        if self.on_listening:
            self.on_listening()

        # Start streaming STT
        self._start_streaming_stt()

    def _start_streaming_stt(self):
        """Start streaming STT from microphone."""
        try:
            import sounddevice as sd

            def audio_generator():
                with sd.RawInputStream(
                    samplerate=self.config.sample_rate,
                    blocksize=int(self.config.sample_rate * 30 / 1000),
                    device=self.config.input_device,
                    channels=1,
                    dtype='int16'
                ) as stream:
                    while self.state in (PipelineState.LISTENING, PipelineState.PROCESSING) and not self._stop_event.is_set():
                        data, overflow = stream.read(int(self.config.sample_rate * 30 / 1000))
                        if overflow:
                            print("Audio overflow")
                        yield bytes(data)

            # Run streaming STT in thread
            stt_thread = threading.Thread(
                target=self.streaming_stt.process_stream,
                args=(audio_generator(), self._stop_event),
                daemon=True
            )
            stt_thread.start()

        except Exception as e:
            print(f"Failed to start streaming STT: {e}")
            self._set_state(PipelineState.IDLE)

    # --- STT Callbacks ---
    def _on_speech_start(self):
        """User started speaking."""
        if self.state == PipelineState.LISTENING:
            self._set_state(PipelineState.PROCESSING)

    def _on_speech_end(self, text: str):
        """User finished speaking - process transcription."""
        if self.state != PipelineState.PROCESSING:
            return

        if self.on_transcription:
            self.on_transcription(text)

        # Generate response
        self._generate_response(text)

    def _on_transcription(self, text: str):
        """Transcription callback."""
        pass  # Handled by _on_speech_end

    # --- Response Generation ---
    def _generate_response(self, user_input: str):
        """Generate and speak response."""
        self._set_state(PipelineState.THINKING)

        try:
            response = self.response_generator(user_input)

            if self.on_response:
                self.on_response(response)

            # Speak response
            self._speak_response(response)

        except Exception as e:
            print(f"Response generation error: {e}")
            self._set_state(PipelineState.IDLE)

    # --- TTS Callbacks ---
    def _on_tts_audio(self, audio: np.ndarray):
        """TTS audio ready."""
        pass

    def _on_playback_start(self):
        """TTS playback started."""
        self._set_state(PipelineState.SPEAKING)
        self._interruption_detected = False
        self._start_interruption_monitor()

    def _on_playback_end(self):
        """TTS playback ended."""
        if self.state == PipelineState.SPEAKING:
            self._set_state(PipelineState.IDLE)

    def _speak_response(self, text: str):
        """Queue text for TTS playback."""
        if self.streaming_tts:
            asyncio.run_coroutine_threadsafe(
                self.streaming_tts.queue_text(text),
                asyncio.get_event_loop()
            )

    # --- Interruption Handling ---
    def _start_interruption_monitor(self):
        """Monitor microphone during playback for barge-in."""
        if not self.config.enable_interruption or not self._vad:
            return

        def monitor():
            try:
                import sounddevice as sd
                with sd.RawInputStream(
                    samplerate=16000,
                    blocksize=480,
                    device=self.config.input_device,
                    channels=1,
                    dtype='int16'
                ) as stream:
                    while self.state == PipelineState.SPEAKING and not self._stop_event.is_set():
                        data, _ = stream.read(480)
                        try:
                            is_speech = self._vad.is_speech(bytes(data), 16000)
                            if is_speech:
                                self._interruption_detected = True
                                self._handle_interruption()
                                break
                        except:
                            pass
            except Exception as e:
                print(f"Interruption monitor error: {e}")

        self._interruption_thread = threading.Thread(target=monitor, daemon=True)
        self._interruption_thread.start()

    def _handle_interruption(self):
        """Handle user interruption (barge-in)."""
        print("INTERRUPTION DETECTED - User barged in")
        self._set_state(PipelineState.INTERRUPTED)

        # Stop current playback
        try:
            import sounddevice as sd
            sd.stop()
        except:
            pass

        # Immediately start listening again
        self._set_state(PipelineState.LISTENING)
        if self.on_listening:
            self.on_listening()
        self._start_streaming_stt()


async def main():
    """Main entry point for voice service."""
    # Load configuration
    config = load_voice_config()

    # Create service
    service = VoicePipelineService(config)

    # Set up callbacks for demo
    def on_wake():
        print(">>> WAKE WORD DETECTED <<<")

    def on_listening():
        print("[LISTENING...]")

    def on_transcription(text):
        print(f"YOU: {text}")

    def on_response(text):
        print(f"JARVIS: {text}")

    def on_state(state):
        print(f"STATE: {state.value}")

    service.on_wake = on_wake
    service.on_listening = on_listening
    service.on_transcription = on_transcription
    service.on_response = on_response
    service.on_state_change = on_state

    # Initialize
    if service.initialize():
        print("\nVoice service ready. Say 'Jarvis' to test.")
        print("Press Ctrl+C to exit.\n")

        try:
            await service.start()
            # Keep running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            await service.stop()
    else:
        print("Voice service initialization failed")


def load_voice_config() -> VoiceConfig:
    """Load voice configuration from YAML."""
    config_path = JARVIS_ROOT / "config" / "voice.yaml"
    if config_path.exists():
        import yaml
        with open(config_path) as f:
            data = yaml.safe_load(f)
            voice_data = data.get("voice", {})
            return VoiceConfig(
                wake_keyword=voice_data.get("wake_word", {}).get("keywords", [{}])[0].get("name", "jarvis"),
                wake_sensitivity=voice_data.get("wake_word", {}).get("keywords", [{}])[0].get("sensitivity", 0.7),
                access_key=voice_data.get("wake_word", {}).get("access_key"),
                custom_keyword_path=voice_data.get("wake_word", {}).get("custom_keyword_path"),
                stt_model=voice_data.get("stt", {}).get("model", "base"),
                stt_language=voice_data.get("stt", {}).get("language", "en"),
                stt_device=voice_data.get("stt", {}).get("device", "cpu"),
                tts_voice=voice_data.get("tts", {}).get("voice", {}).get("piper", {}).get("model", "en_GB-alan-medium"),
                tts_length_scale=voice_data.get("tts", {}).get("voice", {}).get("piper", {}).get("length_scale", 1.0),
                vad_aggressiveness=voice_data.get("stt", {}).get("vad_aggressiveness", 2),
                min_speech_duration=voice_data.get("stt", {}).get("min_speech_duration", 0.5),
                max_silence_duration=voice_data.get("stt", {}).get("max_silence_duration", 1.5),
                enable_interruption=voice_data.get("interrupt", {}).get("enabled", True),
                interruption_threshold=voice_data.get("interrupt", {}).get("vad_threshold", 0.3),
                input_device=voice_data.get("audio", {}).get("input_device"),
                output_device=voice_data.get("audio", {}).get("output_device"),
                sample_rate=voice_data.get("audio", {}).get("input_sample_rate", 16000),
            )
    return VoiceConfig()


if __name__ == "__main__":
    asyncio.run(main())