# Voice Cloning Options (Saved for Later)

## ElevenLabs Alternatives (Local, Free, Open-Source)

| Option | Repo | Quality | Voice Cloning | License |
|--------|------|---------|---------------|---------|
| **XTTS v2 (Coqui)** | `github.com/coqui-ai/TTS` | ★★★★★ | ✅ Zero-shot | MIT |
| **OpenVoice** | `github.com/myshell-ai/OpenVoice` | ★★★★★ | ✅ Instant cloning | MIT |
| **Bark (Suno)** | `github.com/suno-ai/bark` | ★★★★☆ | ❌ | MIT |
| **RVC v2** | `github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI` | ★★★★★ | ✅ Singing + speech | MIT |
| **VITS** | `github.com/jaywalnut310/vits` | ★★★★☆ | ✅ | MIT |
| **VALL-E X** | `github.com/Plachtaa/VALL-E-X` | ★★★★★ | ✅ Zero-shot | MIT |

## Quick Start Commands (When Needed)

```bash
# XTTS v2 (Coqui) - Best all-rounder
pip install TTS
# tts --text "Hello" --model_name tts_models/multilingual/multi-dataset/xtts_v2 --speaker_wav reference.wav

# OpenVoice - Fastest cloning
# git clone https://github.com/myshell-ai/OpenVoice
# pip install -r requirements.txt

# RVC v2 - Best for singing/character voices
# git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI

# VALL-E X - Microsoft's zero-shot TTS
# git clone https://github.com/Plachtaa/VALL-E-X
```

## Current J.A.R.V.I.S. Voice Stack (Active)

| Component | Model | Status |
|-----------|-------|--------|
| **TTS** | Piper `en_GB-alan-medium` | ✅ Active |
| **STT** | Whisper `base` | ✅ Active |
| **Wake Word** | Porcupine `jarvis` (built-in) | ⏳ Needs Access Key |
| **Custom Wake** | Porcupine `Wake up Jarvis` | ⏳ Needs .ppn + Access Key |
| **Voice Clone** | RVC pipeline | ⏳ Future |

## Notes
- All local, free, no API keys required
- Piper + Whisper working perfectly now
- ElevenLabs official API available if needed later (pay-per-use)
- No jailbreaking - all legitimate open-source alternatives