#!/usr/bin/env python3
"""
J.A.R.V.I.S. Text-to-Speech (TTS) Module
Uses Piper for local, fast, high-quality synthesis.
"""

import os
import tempfile
import subprocess
import threading
import time
from pathlib import Path
from typing import Callable, Optional, Generator
import numpy as np


class PiperTTS:
    """Local text-to-speech using Piper."""
    
    # Piper voice models (download from https://huggingface.co/rhasspy/piper-voices)
    VOICES = {
        "en_US-lessac-medium": "en_US-lessac-medium.onnx",
        "en_US-lessac-low": "en_US-lessac-low.onnx",
        "en_US-lessac-high": "en_US-lessac-high.onnx",
        "en_US-libritts-high": "en_US-libritts-high.onnx",
        "en_GB-northern_english_male-medium": "en_GB-northern_english_male-medium.onnx",
        "en_GB-alan-low": "en_GB-alan-low.onnx",
        "en_GB-alan-medium": "en_GB-alan-medium.onnx",
        "en_GB-alan-high": "en_GB-alan-high.onnx",
        "en_GB-semaine-medium": "en_GB-semaine-medium.onnx",
        "en_US-ryan-low": "en_US-ryan-low.onnx",
        "en_US-ryan-medium": "en_US-ryan-medium.onnx",
        "en_US-ryan-high": "en_US-ryan-high.onnx",
    }
    
    # J.A.R.V.I.S. persona: British male, calm, measured
    # Recommended: en_GB-alan-medium (British male, calm) or en_GB-northern_english_male-medium
    JARVIS_VOICE = "en_GB-alan-medium"
    
    def __init__(
        self,
        voice: str = JARVIS_VOICE,
        voice_dir: Optional[str] = None,
        length_scale: float = 1.0,  # Speed control (1.0 = normal, >1 = slower)
        noise_scale: float = 0.667,
        noise_w: float = 0.8,
        on_audio_ready: Optional[Callable[[np.ndarray], None]] = None
    ):
        """
        Initialize Piper TTS.
        
        Args:
            voice: Voice model name (must match downloaded .onnx file)
            voice_dir: Directory containing voice models
            length_scale: Speech speed (1.0 = normal)
            noise_scale: Variation in speech
            noise_w: Phoneme variation
            on_audio_ready: Callback with generated audio (float32 numpy array)
        """
        self.voice = voice
        self.voice_dir = Path(voice_dir) if voice_dir else Path.home() / ".local/share/piper"
        self.length_scale = length_scale
        self.noise_scale = noise_scale
        self.noise_w = noise_w
        self.on_audio_ready = on_audio_ready
        
        self.voice_path = self.voice_dir / f"{voice}.onnx"
        self.config_path = self.voice_dir / f"{voice}.onnx.json"
        self.piper_bin = None
        self._find_piper()
    
    def _find_piper(self):
        """Find piper executable."""
        # Try to find piper in PATH or common locations
        import shutil
        self.piper_bin = shutil.which("piper")
        if not self.piper_bin:
            # Check common install locations
            for path in [
                "/usr/local/bin/piper",
                "/usr/bin/piper",
                str(Path.home() / ".local/bin/piper"),
                "/opt/data/jarvis/venv/bin/piper",
            ]:
                if Path(path).exists():
                    self.piper_bin = path
                    break
    
    def check_voice(self) -> bool:
        """Check if voice model exists."""
        return self.voice_path.exists() and self.config_path.exists()
    
    def download_voice(self, voice: Optional[str] = None) -> bool:
        """
        Download voice model from Hugging Face.
        Note: Requires internet and huggingface_hub.
        """
        voice = voice or self.voice
        try:
            from huggingface_hub import hf_hub_download
            self.voice_dir.mkdir(parents=True, exist_ok=True)
            
            # Download .onnx model
            model_path = hf_hub_download(
                repo_id="rhasspy/piper-voices",
                filename=f"{voice}.onnx",
                local_dir=self.voice_dir
            )
            
            # Download .onnx.json config
            config_path = hf_hub_download(
                repo_id="rhasspy/piper-voices",
                filename=f"{voice}.onnx.json",
                local_dir=self.voice_dir
            )
            
            print(f"Voice {voice} downloaded to {self.voice_dir}")
            return True
        except Exception as e:
            print(f"Failed to download voice {voice}: {e}")
            return False
    
    def synthesize(self, text: str) -> Optional[np.ndarray]:
        """
        Synthesize text to audio.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Float32 numpy array (sample_rate=22050 typically) or None on failure
        """
        if not self.check_voice():
            print(f"Voice {self.voice} not found. Attempting download...")
            if not self.download_voice():
                return None
        
        if not self.piper_bin:
            print("Piper executable not found. Install with: pip install piper-tts")
            return None
        
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                output_file = tmp.name
            
            # Run piper
            cmd = [
                self.piper_bin,
                "--model", str(self.voice_path),
                "--config", str(self.config_path),
                "--output_file", output_file,
                "--length_scale", str(self.length_scale),
                "--noise_scale", str(self.noise_scale),
                "--noise_w", str(self.noise_w),
            ]
            
            result = subprocess.run(
                cmd,
                input=text.encode(),
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"Piper synthesis failed: {result.stderr.decode()}")
                return None
            
            # Load generated WAV
            import wave
            with wave.open(output_file, 'rb') as wf:
                sample_rate = wf.getframerate()
                n_frames = wf.getnframes()
                audio_bytes = wf.readframes(n_frames)
            
            # Convert to float32 numpy array
            audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0
            
            # Cleanup
            try:
                os.unlink(output_file)
            except:
                pass
            
            if self.on_audio_ready:
                self.on_audio_ready(audio_float32)
            
            return audio_float32
            
        except subprocess.TimeoutExpired:
            print("Piper synthesis timed out")
            return None
        except Exception as e:
            print(f"Synthesis error: {e}")
            return None
    
    def synthesize_streaming(self, text: str) -> Generator[np.ndarray, None, None]:
        """
        Synthesize text and yield audio chunks for streaming playback.
        
        Args:
            text: Text to synthesize
            
        Yields:
            Float32 numpy array chunks
        """
        audio = self.synthesize(text)
        if audio is not None:
            # Yield in chunks for streaming
            chunk_size = 4096
            for i in range(0, len(audio), chunk_size):
                yield audio[i:i + chunk_size]


class StreamingTTS:
    """Streaming TTS with queue for real-time playback."""
    
    def __init__(
        self,
        tts: PiperTTS,
        on_playback_start: Optional[Callable] = None,
        on_playback_end: Optional[Callable] = None
    ):
        """
        Initialize streaming TTS.
        
        Args:
            tts: PiperTTS instance
            on_playback_start: Callback when playback starts
            on_playback_end: Callback when playback ends
        """
        self.tts = tts
        self.on_playback_start = on_playback_start
        self.on_playback_end = on_playback_end
        
        self._queue = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._worker_thread = None
    
    def queue_text(self, text: str):
        """Add text to synthesis queue."""
        with self._lock:
            self._queue.append(text)
    
    def start(self):
        """Start synthesis worker."""
        if self._worker_thread and self._worker_thread.is_alive():
            return
        
        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()
    
    def stop(self):
        """Stop synthesis worker."""
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=2.0)
    
    def _worker(self):
        """Worker thread for synthesis queue."""
        import sounddevice as sd
        
        while not self._stop_event.is_set():
            with self._lock:
                if not self._queue:
                    time.sleep(0.1)
                    continue
                text = self._queue.pop(0)
            
            if self.on_playback_start:
                self.on_playback_start()
            
            # Synthesize and play
            audio = self.tts.synthesize(text)
            if audio is not None:
                try:
                    sd.play(audio, samplerate=22050)
                    sd.wait()
                except Exception as e:
                    print(f"Playback error: {e}")
            
            if self.on_playback_end:
                self.on_playback_end()


if __name__ == "__main__":
    print("Testing Piper TTS...")
    
    def on_audio(audio):
        print(f"Audio generated: {len(audio)} samples")
    
    tts = PiperTTS(voice=PiperTTS.JARVIS_VOICE, on_audio_ready=on_audio)
    
    if tts.check_voice() or tts.download_voice():
        print("Voice available. Testing synthesis...")
        audio = tts.synthesize("Yes Sir. J.A.R.V.I.S. systems online.")
        if audio is not None:
            print(f"Success: {len(audio)} samples at 22050 Hz")
        else:
            print("Synthesis failed")
    else:
        print("Voice not available and download failed")