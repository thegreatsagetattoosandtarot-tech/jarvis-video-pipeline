# 🎬 JARVIS Video Pipeline — GitHub Actions + HuggingFace

**Owner:** The Great Sage Tattoos & Tarot (@thegreatsagetattoosandtarot-tech)  
**Cost:** FREE within monthly limits  
**Architecture:** GitHub Actions orchestration → HuggingFace Inference API → Video artifact

---

## Overview

This pipeline uses **GitHub Actions free tier (2,000 min/month)** as an orchestrator
and **HuggingFace Inference Providers** for AI video generation — completely free within limits.

```
You (chat) 
  → GitHub Actions workflow_dispatch (via API or manual click)
    → Python script: generate_video.py
      → HuggingFace Inference API (FAL.ai or WaveSpeedAI provider)
        → CogVideoX-2B / HunyuanVideo / LTX-Video
          → Video .mp4 saved as GitHub Actions Artifact (7-day retention)
```

---

## Free Tier Limits

| Service | Free Allowance | Estimated Video Capacity |
|---|---|---|
| GitHub Actions | 2,000 min/month | ~200–400 video jobs/month |
| HuggingFace Inference | $0.10 credits/month (free) | ~1–5 short clips |
| HuggingFace Inference PRO | $2.00 credits/month ($9/mo) | ~10–20 clips |
| FAL.ai (own key) | $1 signup credit | ~5–10 clips |
| Replicate (own key) | $10 signup credit | ~50–100 clips |

**Best free strategy:** Use your own FAL.ai or Replicate key in GitHub Secrets — GitHub Actions minutes are free, and these providers give $1–10 in free credits to new accounts.

---

## Repository Structure

```
jarvis-video-pipeline/
├── .github/
│   └── workflows/
│       └── generate-video.yml    ← GitHub Actions workflow
├── generate_video.py             ← Main generation script
├── README.md                     ← This file
├── SETUP.md                      ← Step-by-step setup guide
└── output/                       ← Generated videos (gitignored)
```

---

## Quick Start

See [SETUP.md](SETUP.md) for full step-by-step instructions.

1. Fork/clone this repo to `thegreatsagetattoosandtarot-tech/jarvis-video-pipeline`
2. Add secrets: `HF_TOKEN`, optionally `FAL_KEY` or `REPLICATE_API_TOKEN`
3. Go to **Actions** tab → **Generate Video with AI** → **Run workflow**
4. Enter your prompt and click **Run workflow**
5. Download video from **Artifacts** section once the job completes

---

## Triggering via JARVIS (API)

JARVIS can trigger this workflow programmatically via the GitHub API:

```bash
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/thegreatsagetattoosandtarot-tech/jarvis-video-pipeline/actions/workflows/generate-video.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "prompt": "Tattooed hands pulling The Star tarot card from a deck, candlelight, dark mystical atmosphere, cinematic",
      "duration": "5"
    }
  }'
```

---

## Recommended Prompts for The Great Sage

### Tarot Reveal
```
Extreme close-up of heavily tattooed hands with intricate dark ink sacred geometry 
slowly revealing a tarot card face-down on dark velvet. Candlelight illuminates the scene. 
The Star card revealed. Cinematic lighting, photorealistic, 8K detail.
```

### Tattoo Process
```
Close-up of tattooed hands working on an intricate mandala tattoo, needle in motion, 
fresh ink glistening under bright studio light. Slow-motion, cinematic, photorealistic.
```

### Crystal Grid
```
Tattooed hands arranging amethyst and clear quartz crystals into a sacred geometry grid 
on dark cloth. Candles flickering, incense smoke rising, mystical atmosphere, photorealistic.
```

---

## Models Available (2025)

| Model | Provider | Quality | Speed | Free? |
|---|---|---|---|---|
| LTX-Video-0.9.8-13B | FAL.ai | ⭐⭐⭐⭐ | Fast | With own key |
| HunyuanVideo | FAL.ai / WaveSpeedAI | ⭐⭐⭐⭐⭐ | Slow | With own key |
| CogVideoX-2B | HF Inference | ⭐⭐⭐ | Medium | $0.10 credit |
| Wan-2.1 480p | Replicate | ⭐⭐⭐⭐ | Medium | $10 signup |

---

## Support

Built by JARVIS (J.A.R.V.I.S. AI Agent) for The Great Sage content pipeline.
