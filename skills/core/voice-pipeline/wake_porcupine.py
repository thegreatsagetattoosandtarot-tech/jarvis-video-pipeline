#!/usr/bin/env python3
"""
J.A.R.V.I.S. Wake Word Detection Module
Uses Porcupine (Picovoice) for accurate, low-latency wake word detection.
Wake word: "Wake up Jarvis"
"""

import os
import struct
import threading
import time
from pathlib import Path
from typing import Callable, Optional, Generator
import pvporcupine
import sounddevice as sd
import numpy as np


class WakeWordDetector:
    """Wake word detection using Porcupine."""
    
    # Custom wake word: "Wake up Jarvis"
    # Note: Custom keywords require Picovoice Console (free tier allows 3 custom keywords)
    # For now, use built-in "jarvis" or "hey google" as approximation
    BUILTIN_KEYWORDS = [
        "jarvis",
        "hey google",
        "alexa",
        "porcupine",
        "bumblebee",
        "computer",
        "hey siri",
        "ok google",
        "picovoice",
        "terminator",
    ]
    
    def __init__(
        self,
        keyword: str = "jarvis",
        sensitivity: float = 0.7,
        on_detected: Optional[Callable] = None,
        access_key: Optional[str] = None,
        custom_keyword_path: Optional[str] = None
    ):
        """
        Initialize wake word detector.
        
        Args:
            keyword: Built-in keyword or "custom" for custom keyword
            sensitivity: Detection sensitivity (0.0-1.0)
            on_detected: Callback when wake word detected
            access_key: Picovoice access key (required for Porcupine)
            custom_keyword_path: Path to .ppn file for custom keyword
        """
        self.keyword = keyword
        self.sensitivity = sensitivity
        self.on_detected = on_detected
        self.access_key = access_key or os.environ.get("PICOVOICE_ACCESS_KEY")
        self.custom_keyword_path = custom_keyword_path
        
        self.handle = None
        self.sample_rate = None
        self.frame_length = None
        self._stream = None
        self._stop_event = threading.Event()
        self._worker_thread = None
        
        # Audio input config
        self.input_device = None
        self.input_channels = 1
    
    def initialize(self) -> bool:
        """Initialize Porcupine."""
        try:
            if self.keyword == "custom" and self.custom_keyword_path:
                # Custom keyword
                self.handle = pvporcupine.create(
                    access_key=self.access_key,
                    keyword_paths=[self.custom_keyword_path],
                    sensitivities=[self.sensitivity]
                )
            else:
                # Built-in keyword
                self.handle = pvporcupine.create(
                    access_key=self.access_key,
                    keywords=[self.keyword],
                    sensitivities=[self.sensitivity]
                )
            
            self.sample_rate = self.handle.sample_rate
            self.frame_length = self.handle.frame_length
            print(f"Porcupine initialized: keyword='{self.keyword}', sample_rate={self.sample_rate}, frame_length={self.frame_length}")
            return True
        except Exception as e:
            print(f"Porcupine initialization failed: {e}")
            return False
    
    def start(self, input_device: Optional[int] = None) -> bool:
        """Start wake word detection."""
        if not self.handle:
            if not self.initialize():
                return False
        
        self.input_device = input_device
        self._stop_event.clear()
        
        self._worker_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self._worker_thread.start()
        print(f"Wake word detection started: '{self.keyword}'")
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
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=self.frame_length,
                device=self.input_device,
                channels=self.input_channels,
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
        
        # Convert to int16 array
        pcm = indata[:, 0] if indata.ndim > 1 else indata
        
        # Process with Porcupine
        try:
            result = self.handle.process(pcm)
            if result >= 0:
                print(f"Wake word detected! (index: {result})")
                if self.on_detected:
                    self.on_detected()
        except Exception as e:
            print(f"Processing error: {e}")
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        if self.handle:
            self.handle.delete()


class CustomWakeWordGenerator:
    """Helper to generate custom wake word .ppn file via Picovoice Console."""
    
    @staticmethod
    def get_console_url() -> str:
        return "https://console.picovoice.ai/"
    
    @staticmethod
    def instructions() -> str:
        return """
To create custom wake word "Wake up Jarvis":

1. Go to https://console.picovoice.ai/
2. Sign up for free account (3 custom keywords free)
3. Click "Create Keyword"
4. Enter phrase: "Wake up Jarvis"
5. Select language: English
6. Train and download .ppn file
7. Place .ppn file at /opt/data/jarvis/config/wake_up_jarvis.ppn
8. Set WakeWordDetector(keyword="custom", custom_keyword_path="...")

Note: Requires Picovoice Access Key (free tier: 3 keywords, unlimited usage)
Get access key at console.picovoice.ai -> AccessKey
        """


if __name__ == "__main__":
    print("Wake Word Detector Test")
    print("=" * 40)
    
    # Check for access key
    access_key = os.environ.get("PICOVOICE_ACCESS_KEY")
    if not access_key:
        print("No PICOVOICE_ACCESS_KEY found in environment")
        print(CustomWakeWordGenerator.instructions())
        print("\nUsing built-in 'jarvis' keyword for testing...")
    
    def on_wake():
        print(">>> WAKE WORD DETECTED! <<<")
    
    detector = WakeWordDetector(
        keyword="jarvis",
        sensitivity=0.7,
        on_detected=on_wake,
        access_key=access_key
    )
    
    if detector.initialize():
        print("Say 'Jarvis' to test...")
        detector.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            detector.stop()
    else:
        print("Failed to initialize detector")