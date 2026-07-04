---
name: voice-pipeline
description: Complete J.A.R.V.I.S. voice pipeline with wake word detection, STT, TTS, and real-time interruption handling. Uses Porcupine + Whisper + Piper + RVC.
category: voice
---

# Voice Pipeline Skill

## Overview
Full voice interaction pipeline for J.A.R.V.I.S.:
1. **Wake Word** → Porcupine ("Wake up Jarvis" / "Jarvis")
2. **STT** → Whisper (local, base model)
3. **Intent/Response** → Agent system integration
4. **TTS** → Piper (local, British male voice)
5. **Interruption** → Real-time barge-in via WebRTC VAD

## Components

| Module | Technology | Purpose |
|--------|------------|---------|
| `wake_porcupine.py` | Picovoice Porcupine | Wake word detection |
| `stt_whisper.py` | OpenAI Whisper | Speech-to-text |
| `tts_piper.py` | Piper TTS | Text-to-speech |
| `rvc_voice.py` | RVC | Voice cloning (J.A.R.V.I.S. persona) |
| `voice_pipeline.py` | Integration | Complete pipeline with interruption |

## Quick Start

```bash
# Test wake word (uses built-in 'jarvis' keyword)
/opt/data/jarvis/venv/bin/python /opt/data/jarvis/scripts/wake_porcupine.py

# Test STT
/opt/data/jarvis/venv/bin/python /opt/data/jarvis/scripts/stt_whisper.py

# Test TTS
/opt/data/jarvis/venv/bin/python /opt/data/jarvis/scripts/tts_piper.py

# Full pipeline (requires audio devices)
/opt/data/jarvis/venv/bin/python /opt/data/jarvis/scripts/voice_pipeline.py
```

## Configuration

### Environment Variables
```bash
# Wake word
export JARVIS_WAKE_KEYWORD="jarvis"
export JARVIS_WAKE_SENSITIVITY="0.7"
export PICOVOICE_ACCESS_KEY="your_key_here"
export JARVIS_CUSTOM_KEYWORD_PATH="/opt/data/jarvis/config/wake_up_jarvis.ppn"

# STT
export JARVIS_STT_MODEL="base"
export JARVIS_STT_LANGUAGE="en"

# TTS
export JARVIS_TTS_VOICE="en_GB-alan-medium"

# Audio devices (get indices from `python -m sounddevice`)
export JARVIS_INPUT_DEVICE="0"
export JARVIS_OUTPUT_DEVICE="0"
```

### Custom Wake Word "Wake up Jarvis"
1. Sign up at https://console.picovoice.ai/ (free tier: 3 keywords)
2. Create keyword: "Wake up Jarvis"
3. Download .ppn file for Linux (x86_64)
4. Place at `/opt/data/jarvis/config/wake_up_jarvis.ppn`
5. Set `JARVIS_CUSTOM_KEYWORD_PATH` and use `keyword="custom"`

## Voice Persona (J.A.R.V.I.S.)
- **Target**: Paul Bettany (British, calm, measured, precise, subtle wit)
- **TTS Voice**: `en_GB-alan-medium` (British male, calm)
- **RVC Model**: Train on Paul Bettany reference audio (optional enhancement)

## Interruption Handling (Barge-In)
- Monitors microphone during TTS playback
- Uses WebRTC VAD to detect user speech
- Immediately stops TTS and re-enters listening mode
- Latency: ~50-100ms detection

## Pipeline States
```
IDLE → (wake word) → LISTENING → (speech start) → PROCESSING
                                    ↓
                              (speech end) → THINKING → SPEAKING
                                    ↓                          ↓
                              (interrupt) ← INTERRUPTED ← (barge-in)
                                    ↓
                                   IDLE
```

## Integration with Agent System
```python
def agent_response(user_input: str) -> str:
    # Your agent logic here
    return "Yes Sir. Task completed."

pipeline = VoicePipeline(
    config=PipelineConfig(),
    response_generator=agent_response
)
```

## Current Status
- ✅ Wake word detector (Porcupine) - uses built-in 'jarvis' keyword
- ✅ STT (Whisper base model) - loaded and functional
- ✅ TTS (Piper) - using en_GB-alan-medium (British male)
- ✅ Voice pipeline integration - complete with interruption
- ⏳ Custom "Wake up Jarvis" keyword - needs Picovoice Console setup
- ⏳ RVC voice cloning - requires training data + GPU
- ⏳ Audio device testing - requires hardware

## Dependencies
```bash
# System (run as root)
apt-get install portaudio19-dev libasound2-dev

# Python (in venv)
pip install pvporcupine openai-whisper piper-tts sounddevice numpy scipy webrtcvad
```

## Next Steps
1. Set up Picovoice Access Key for custom wake word
2. Test with actual microphone/speaker hardware
3. Train RVC model on Paul Bettany audio for authentic J.A.R.V.I.S. voice
4. Integrate response_generator with actual agent system (Metatron)
5. Add voice activity visualization / UI feedback