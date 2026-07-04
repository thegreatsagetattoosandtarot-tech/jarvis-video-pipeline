#!/usr/bin/env python3
"""
J.A.R.V.I.S. Complete Voice Pipeline
Integrates: Wake Word -> STT -> Intent -> TTS -> Audio Out
With real-time interruption handling (barge-in)
"""

import os
import sys
import threading
import time
import queue
import signal
from pathlib import Path
from typing import Callable, Optional, Generator
from dataclasses import dataclass
from enum import Enum
import numpy as np
import sounddevice as sd

# Import our modules
sys.path.insert(0, str(Path(__file__).parent))
from wake_porcupine import WakeWordDetector
from stt_whisper import WhisperSTT, StreamingSTT
from tts_piper import PiperTTS, StreamingTTS


class PipelineState(Enum):
    """Voice pipeline states."""
    IDLE = "idle"                    # Waiting for wake word
    LISTENING = "listening"          # Wake word detected, listening for speech
    PROCESSING = "processing"        # Processing STT
    THINKING = "thinking"            # Generating response (LLM/agent)
    SPEAKING = "speaking"            # Playing TTS response
    INTERRUPTED = "interrupted"      # User interrupted (barge-in)


@dataclass
class PipelineConfig:
    """Voice pipeline configuration."""
    # Wake word
    wake_keyword: str = "jarvis"
    wake_sensitivity: float = 0.7
    access_key: Optional[str] = None
    custom_keyword_path: Optional[str] = None
    
    # STT
    stt_model: str = "base"  # tiny, base, small, medium, large
    stt_language: str = "en"
    stt_device: str = "cpu"
    
    # TTS
    tts_voice: str = "en_GB-alan-medium"  # British male
    tts_length_scale: float = 1.0
    
    # VAD (Voice Activity Detection)
    vad_aggressiveness: int = 2
    min_speech_duration: float = 0.5
    max_silence_duration: float = 1.5
    
    # Interruption
    enable_interruption: bool = True
    interruption_threshold: float = 0.3  # VAD threshold during playback
    
    # Audio
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    sample_rate: int = 16000


class VoicePipeline:
    """Complete J.A.R.V.I.S. voice pipeline with interruption handling."""
    
    def __init__(
        self,
        config: PipelineConfig,
        on_wake: Optional[Callable] = None,
        on_listening: Optional[Callable] = None,
        on_transcription: Optional[Callable[[str], None]] = None,
        on_response: Optional[Callable[[str], None]] = None,
        on_state_change: Optional[Callable[[PipelineState], None]] = None,
        response_generator: Optional[Callable[[str], str]] = None
    ):
        """
        Initialize voice pipeline.
        
        Args:
            config: PipelineConfig object
            on_wake: Callback when wake word detected
            on_listening: Callback when starting to listen
            on_transcription: Callback with transcribed text
            on_response: Callback with generated response text
            on_state_change: Callback when pipeline state changes
            response_generator: Function that takes user input and returns response
        """
        self.config = config
        self.response_generator = response_generator or self._default_response
        
        # Callbacks
        self.on_wake = on_wake
        self.on_listening = on_listening
        self.on_transcription = on_transcription
        self.on_response = on_response
        self.on_state_change = on_state_change
        
        # Components
        self.wake_detector = None
        self.stt = None
        self.streaming_stt = None
        self.tts = None
        self.streaming_tts = None
        
        # State
        self.state = PipelineState.IDLE
        self._stop_event = threading.Event()
        self._main_thread = None
        
        # Audio for interruption detection during playback
        self._playback_stream = None
        self._interruption_detected = False
        
        # VAD for interruption detection
        self._vad = None
        self._init_vad()
    
    def _init_vad(self):
        """Initialize VAD for interruption detection."""
        try:
            import webrtcvad
            self._vad = webrtcvad.Vad(self.config.vad_aggressiveness)
        except Exception as e:
            print(f"VAD init failed (interruption detection disabled): {e}")
    
    def _set_state(self, state: PipelineState):
        """Update pipeline state."""
        if self.state != state:
            print(f"[STATE] {self.state.value} -> {state.value}")
            self.state = state
            if self.on_state_change:
                self.on_state_change(state)
    
    def _default_response(self, user_input: str) -> str:
        """Default response generator (placeholder for LLM/agent integration)."""
        # This is where you'd integrate with your agent system
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
    
    def initialize(self) -> bool:
        """Initialize all pipeline components."""
        print("Initializing J.A.R.V.I.S. Voice Pipeline...")
        
        # 1. Wake Word Detector
        print("  [1/4] Wake Word Detector...")
        self.wake_detector = WakeWordDetector(
            keyword=self.config.wake_keyword,
            sensitivity=self.config.wake_sensitivity,
            on_detected=self._on_wake_detected,
            access_key=self.config.access_key,
            custom_keyword_path=self.config.custom_keyword_path
        )
        if not self.wake_detector.initialize():
            return False
        
        # 2. STT
        print("  [2/4] Speech-to-Text (Whisper)...")
        self.stt = WhisperSTT(
            model_size=self.config.stt_model,
            language=self.config.stt_language,
            device=self.config.stt_device,
            on_transcription=self._on_transcription
        )
        if not self.stt.load_model():
            return False
        
        # Streaming STT with VAD
        self.streaming_stt = StreamingSTT(
            stt=self.stt,
            vad_aggressiveness=self.config.vad_aggressiveness,
            min_speech_duration=self.config.min_speech_duration,
            max_silence_duration=self.config.max_silence_duration,
            on_speech_start=self._on_speech_start,
            on_speech_end=self._on_speech_end
        )
        
        # 3. TTS
        print("  [3/4] Text-to-Speech (Piper)...")
        self.tts = PiperTTS(
            voice=self.config.tts_voice,
            length_scale=self.config.tts_length_scale,
            on_audio_ready=self._on_tts_audio
        )
        
        if not self.tts.check_voice():
            print(f"  Downloading voice: {self.config.tts_voice}...")
            if not self.tts.download_voice():
                print("  Warning: Voice download failed, continuing anyway")
        
        self.streaming_tts = StreamingTTS(
            tts=self.tts,
            on_playback_start=self._on_playback_start,
            on_playback_end=self._on_playback_end
        )
        
        # 4. Audio setup
        print("  [4/4] Audio devices...")
        self._check_audio_devices()
        
        print("Voice Pipeline initialized successfully!")
        return True
    
    def _check_audio_devices(self):
        """Check available audio devices."""
        devices = sd.query_devices()
        print("  Available input devices:")
        for i, d in enumerate(devices):
            if d['max_input_channels'] > 0:
                print(f"    [{i}] {d['name']} ({d['max_input_channels']} ch)")
        
        print("  Available output devices:")
        for i, d in enumerate(devices):
            if d['max_output_channels'] > 0:
                print(f"    [{i}] {d['name']} ({d['max_output_channels']} ch)")
    
    def start(self):
        """Start the voice pipeline."""
        if self._main_thread and self._main_thread.is_alive():
            return
        
        self._stop_event.clear()
        self._set_state(PipelineState.IDLE)
        
        # Start wake word detection
        if self.wake_detector:
            self.wake_detector.start(input_device=self.config.input_device)
        
        # Start TTS streaming worker
        if self.streaming_tts:
            self.streaming_tts.start()
        
        self._main_thread = threading.Thread(target=self._main_loop, daemon=True)
        self._main_thread.start()
        print("Voice Pipeline started. Say 'Wake up Jarvis' (or 'Jarvis') to activate.")
    
    def stop(self):
        """Stop the voice pipeline."""
        print("Stopping Voice Pipeline...")
        self._stop_event.set()
        
        if self.wake_detector:
            self.wake_detector.stop()
        
        if self.streaming_tts:
            self.streaming_tts.stop()
        
        if self._main_thread:
            self._main_thread.join(timeout=3.0)
        
        print("Voice Pipeline stopped")
    
    def _main_loop(self):
        """Main pipeline loop (mostly for monitoring)."""
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
                    blocksize=int(self.config.sample_rate * 30 / 1000),  # 30ms frames
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
        """Transcription callback (also called by streaming STT)."""
        pass  # Handled by _on_speech_end
    
    # --- Response Generation ---
    def _generate_response(self, user_input: str):
        """Generate and speak response."""
        self._set_state(PipelineState.THINKING)
        
        try:
            # Generate response (integrate with agent system here)
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
            self.streaming_tts.queue_text(text)
    
    # --- Interruption Handling ---
    def _start_interruption_monitor(self):
        """Monitor microphone during playback for barge-in."""
        if not self.config.enable_interruption or not self._vad:
            return
        
        def monitor():
            try:
                with sd.RawInputStream(
                    samplerate=16000,
                    blocksize=480,  # 30ms at 16kHz
                    device=self.config.input_device,
                    channels=1,
                    dtype='int16'
                ) as stream:
                    while self.state == PipelineState.SPEAKING and not self._stop_event.is_set():
                        data, _ = stream.read(480)
                        # Check for speech during playback
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
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def _handle_interruption(self):
        """Handle user interruption (barge-in)."""
        print("INTERRUPTION DETECTED - User barged in")
        self._set_state(PipelineState.INTERRUPTED)
        
        # Stop current playback
        try:
            sd.stop()
        except:
            pass
        
        # Immediately start listening again
        self._set_state(PipelineState.LISTENING)
        if self.on_listening:
            self.on_listening()
        self._start_streaming_stt()


def create_pipeline_from_env() -> VoicePipeline:
    """Create pipeline from environment variables."""
    config = PipelineConfig(
        wake_keyword=os.getenv("JARVIS_WAKE_KEYWORD", "jarvis"),
        wake_sensitivity=float(os.getenv("JARVIS_WAKE_SENSITIVITY", "0.7")),
        access_key=os.getenv("PICOVOICE_ACCESS_KEY"),
        custom_keyword_path=os.getenv("JARVIS_CUSTOM_KEYWORD_PATH"),
        stt_model=os.getenv("JARVIS_STT_MODEL", "base"),
        stt_language=os.getenv("JARVIS_STT_LANGUAGE", "en"),
        tts_voice=os.getenv("JARVIS_TTS_VOICE", "en_GB-alan-medium"),
        input_device=int(os.getenv("JARVIS_INPUT_DEVICE")) if os.getenv("JARVIS_INPUT_DEVICE") else None,
        output_device=int(os.getenv("JARVIS_OUTPUT_DEVICE")) if os.getenv("JARVIS_OUTPUT_DEVICE") else None,
    )
    
    return VoicePipeline(config)


if __name__ == "__main__":
    print("J.A.R.V.I.S. Voice Pipeline")
    print("=" * 50)
    
    # Callbacks for demo
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
    
    # Create pipeline
    config = PipelineConfig()
    pipeline = VoicePipeline(
        config=config,
        on_wake=on_wake,
        on_listening=on_listening,
        on_transcription=on_transcription,
        on_response=on_response,
        on_state_change=on_state
    )
    
    # Initialize
    if pipeline.initialize():
        print("\nPipeline ready. Say 'Jarvis' to test.")
        print("Press Ctrl+C to exit.\n")
        
        try:
            pipeline.start()
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            pipeline.stop()
    else:
        print("Pipeline initialization failed")