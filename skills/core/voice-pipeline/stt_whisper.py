#!/usr/bin/env python3
"""
J.A.R.V.I.S. Speech-to-Text (STT) Module
Uses Whisper (openai-whisper) for local transcription.
"""

import os
import tempfile
import threading
import time
import warnings
from pathlib import Path
from typing import Callable, Optional, BinaryIO
import numpy as np
import whisper


class WhisperSTT:
    """Local speech-to-text using Whisper."""
    
    MODEL_SIZES = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
    # tiny: ~39M params, ~1GB VRAM, fastest, least accurate
    # base: ~74M params, ~1GB VRAM, good balance
    # small: ~244M params, ~2GB VRAM, better accuracy
    # medium: ~769M params, ~5GB VRAM, good accuracy
    # large: ~1.5B params, ~10GB VRAM, best accuracy
    
    def __init__(
        self,
        model_size: str = "base",
        language: str = "en",
        device: str = "cpu",  # "cpu" or "cuda"
        on_transcription: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize Whisper STT.
        
        Args:
            model_size: Whisper model size (tiny/base/small/medium/large)
            language: Language code (en, es, fr, etc.) or "auto" for detection
            device: "cpu" or "cuda"
            on_transcription: Callback with transcribed text
        """
        if model_size not in self.MODEL_SIZES:
            raise ValueError(f"model_size must be one of {self.MODEL_SIZES}")
        
        self.model_size = model_size
        self.language = language if language != "auto" else None
        self.device = device
        self.on_transcription = on_transcription
        
        self.model = None
        self.is_loaded = False
        self._load_lock = threading.Lock()
        
        # Audio recording parameters
        self.sample_rate = 16000
        self.chunk_duration = 30  # Whisper processes up to 30s chunks
        
    def load_model(self) -> bool:
        """Load Whisper model (thread-safe, loads once)."""
        with self._load_lock:
            if self.is_loaded:
                return True
            
            try:
                print(f"Loading Whisper model: {self.model_size} on {self.device}...")
                self.model = whisper.load_model(self.model_size, device=self.device)
                self.is_loaded = True
                print("Whisper model loaded successfully")
                return True
            except Exception as e:
                print(f"Failed to load Whisper model: {e}")
                return False
    
    def transcribe_audio(self, audio_data: np.ndarray) -> Optional[str]:
        """
        Transcribe numpy audio array.
        
        Args:
            audio_data: Float32 numpy array, shape (n_samples,), sample_rate=16000
            
        Returns:
            Transcribed text or None on failure
        """
        if not self.is_loaded:
            if not self.load_model():
                return None
        
        try:
            # Ensure audio is float32 and normalized
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Normalize if needed
            if np.max(np.abs(audio_data)) > 1.0:
                audio_data = audio_data / 32768.0
            
            # Transcribe
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    fp16=(self.device == "cuda"),
                    verbose=False
                )
            
            text = result.get("text", "").strip()
            
            if text and self.on_transcription:
                self.on_transcription(text)
            
            return text if text else None
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
    
    def transcribe_file(self, file_path: str) -> Optional[str]:
        """Transcribe audio file directly."""
        if not self.is_loaded:
            if not self.load_model():
                return None
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = self.model.transcribe(
                    file_path,
                    language=self.language,
                    fp16=(self.device == "cuda"),
                    verbose=False
                )
            
            text = result.get("text", "").strip()
            
            if text and self.on_transcription:
                self.on_transcription(text)
            
            return text if text else None
            
        except Exception as e:
            print(f"File transcription error: {e}")
            return None
    
    def transcribe_realtime(self, audio_queue, stop_event: threading.Event):
        """
        Real-time transcription from audio queue.
        
        Args:
            audio_queue: Queue of audio chunks (numpy arrays)
            stop_event: Threading event to signal stop
        """
        if not self.is_loaded:
            if not self.load_model():
                return
        
        buffer = []
        buffer_duration = 0.0
        target_duration = 5.0  # Process every 5 seconds
        
        while not stop_event.is_set():
            try:
                # Get audio chunk with timeout
                chunk = audio_queue.get(timeout=0.1)
                if chunk is None:  # Sentinel
                    break
                
                buffer.append(chunk)
                buffer_duration += len(chunk) / self.sample_rate
                
                # Process when buffer reaches target duration
                if buffer_duration >= target_duration:
                    audio_data = np.concatenate(buffer)
                    self.transcribe_audio(audio_data)
                    buffer = []
                    buffer_duration = 0.0
                    
            except Exception as e:
                if not stop_event.is_set():
                    print(f"Real-time transcription error: {e}")
                continue
        
        # Process remaining buffer
        if buffer:
            audio_data = np.concatenate(buffer)
            self.transcribe_audio(audio_data)


class StreamingSTT:
    """Streaming STT with voice activity detection integration."""
    
    def __init__(
        self,
        stt: WhisperSTT,
        vad_aggressiveness: int = 2,  # 0-3, higher = more aggressive
        min_speech_duration: float = 0.5,  # seconds
        max_silence_duration: float = 1.5,  # seconds
        on_speech_start: Optional[Callable] = None,
        on_speech_end: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize streaming STT with VAD.
        
        Args:
            stt: WhisperSTT instance
            vad_aggressiveness: WebRTC VAD aggressiveness (0-3)
            min_speech_duration: Minimum speech duration to process
            max_silence_duration: Max silence before ending utterance
            on_speech_start: Callback when speech detected
            on_speech_end: Callback with transcribed text when speech ends
        """
        self.stt = stt
        self.vad_aggressiveness = vad_aggressiveness
        self.min_speech_duration = min_speech_duration
        self.max_silence_duration = max_silence_duration
        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end
        
        self.vad = None
        self.sample_rate = 16000
        self.frame_duration = 30  # ms (WebRTC VAD requires 10, 20, or 30ms)
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        
    def initialize_vad(self):
        """Initialize WebRTC VAD."""
        try:
            import webrtcvad
            self.vad = webrtcvad.Vad(self.vad_aggressiveness)
            return True
        except Exception as e:
            print(f"VAD initialization failed: {e}")
            return False
    
    def process_stream(self, audio_stream, stop_event: threading.Event):
        """
        Process audio stream with VAD + STT.
        
        Args:
            audio_stream: Generator yielding audio frames (int16 bytes)
            stop_event: Threading event to signal stop
        """
        if not self.vad:
            if not self.initialize_vad():
                return
        
        speech_buffer = []
        silence_frames = 0
        speech_frames = 0
        in_speech = False
        max_silence_frames = int(self.max_silence_duration * 1000 / self.frame_duration)
        min_speech_frames = int(self.min_speech_duration * 1000 / self.frame_duration)
        
        for frame_bytes in audio_stream:
            if stop_event.is_set():
                break
            
            # Check if frame has speech
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
                    
                    # End of utterance?
                    if silence_frames >= max_silence_frames:
                        if speech_frames >= min_speech_frames:
                            # Process accumulated speech
                            audio_data = self._frames_to_audio(speech_buffer)
                            text = self.stt.transcribe_audio(audio_data)
                            if text and self.on_speech_end:
                                self.on_speech_end(text)
                        
                        # Reset
                        speech_buffer = []
                        silence_frames = 0
                        speech_frames = 0
                        in_speech = False
    
    def _frames_to_audio(self, frames) -> np.ndarray:
        """Convert VAD frames to float32 numpy array."""
        # Concatenate all frame bytes
        all_bytes = b"".join(frames)
        # Convert to int16 array
        audio_int16 = np.frombuffer(all_bytes, dtype=np.int16)
        # Convert to float32 normalized
        audio_float32 = audio_int16.astype(np.float32) / 32768.0
        return audio_float32


if __name__ == "__main__":
    # Test STT
    print("Testing Whisper STT...")
    
    def on_transcribe(text):
        print(f"Transcribed: {text}")
    
    stt = WhisperSTT(model_size="base", language="en", on_transcription=on_transcribe)
    
    if stt.load_model():
        print("Model loaded. Create a test audio file or use microphone input.")
        print("For microphone testing, use the StreamingSTT class with PyAudio.")
    else:
        print("Failed to load model")