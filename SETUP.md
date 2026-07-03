# 🛠️ Setup Guide — JARVIS Video Pipeline

## Prerequisites
- A GitHub account (thegreatsagetattoosandtarot-tech)
- A HuggingFace account (free at huggingface.co)
- Optionally: FAL.ai or Replicate account for better free credits

---

## Step 1 — Create the GitHub Repository

1. Go to **github.com** and log in as `thegreatsagetattoosandtarot-tech`
2. Click **New repository** (green button, top right)
3. Name it: `jarvis-video-pipeline`
4. Set visibility: **Public** (required for free Actions minutes on free plan)
5. Click **Create repository**

---

## Step 2 — Upload the Pipeline Files

### Option A — Upload via GitHub Web UI
1. In the new repo, click **uploading an existing file**
2. Upload all files from this folder (`github-video-pipeline/`)
3. For the workflow file, you need to create `.github/workflows/` — do this via the web editor:
   - Click **Create new file**
   - Type the path: `.github/workflows/generate-video.yml`
   - Paste the contents from `generate-video.yml`
   - Commit

### Option B — Upload via Git (Recommended)
```bash
git init
git remote add origin https://github.com/thegreatsagetattoosandtarot-tech/jarvis-video-pipeline.git
git add .
git commit -m "Initial JARVIS video pipeline"
git push -u origin main
```

---

## Step 3 — Get Your API Keys

### HuggingFace Token (Required — Free)
1. Go to **huggingface.co** → Log in / Sign up
2. Click your profile picture → **Settings**
3. Left sidebar → **Access Tokens**
4. Click **New token** → Name it "jarvis-video-pipeline"
5. Select **Read** permissions (sufficient for inference)
6. Copy the token (starts with `hf_...`)

### FAL.ai Key (Optional — $1 Free Credit at Signup)
1. Go to **fal.ai** → Sign up with Google/email
2. Dashboard → **API Keys** → **Create new key**
3. Copy the key

### Replicate Token (Optional — $10 Free Credit at Signup)
1. Go to **replicate.com** → Sign up
2. Account Settings → **API tokens** → **Create token**
3. Copy the token

---

## Step 4 — Add Secrets to GitHub

1. In your GitHub repo → **Settings** tab
2. Left sidebar → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each:

| Secret Name | Value | Required? |
|---|---|---|
| `HF_TOKEN` | Your HuggingFace token (`hf_...`) | ✅ Required |
| `FAL_KEY` | Your FAL.ai key | Optional (but recommended) |
| `REPLICATE_API_TOKEN` | Your Replicate token | Optional |

---

## Step 5 — Run Your First Video

1. In your repo → **Actions** tab
2. Click **Generate Video with AI** (left sidebar)
3. Click **Run workflow** (right side, blue button)
4. Fill in:
   - **Video prompt**: Your description (see examples below)
   - **Duration**: `5` (seconds)
   - **Model**: `cogvideox` or `ltx`
5. Click **Run workflow**

---

## Step 6 — Download Your Video

1. After the workflow completes (green checkmark), click on the run
2. Scroll down to **Artifacts** section
3. Click **generated-video-[number]** to download as ZIP
4. Unzip to get your `video.mp4`

---

## Triggering from JARVIS (No Manual Steps)

JARVIS can trigger this via GitHub API automatically:

```bash
# JARVIS runs this behind the scenes when you say "generate a video"
curl -X POST \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/thegreatsagetattoosandtarot-tech/jarvis-video-pipeline/actions/workflows/generate-video.yml/dispatches" \
  -d '{
    "ref": "main",
    "inputs": {
      "prompt": "Tattooed hands pulling The Star tarot card, candlelight, cinematic",
      "duration": "5"
    }
  }'
```

---

## Free Tier Limits

| Service | Monthly Free | Estimated Videos |
|---|---|---|
| **GitHub Actions** | 2,000 minutes | ~200–400 jobs |
| **HuggingFace** | $0.10 credits | ~1–5 clips |
| **FAL.ai (signup)** | $1.00 credit | ~5–10 clips |
| **Replicate (signup)** | $10.00 credit | ~50–100 clips |

> 💡 **Tip:** Get one-time signup credits from FAL.ai ($1) + Replicate ($10) for the best free experience. Total: ~60–110 free videos.

---

## Prompt Examples for The Great Sage

```
Tattooed hands pulling The Star tarot card from a deck, candlelight, dark mystical atmosphere, cinematic, photorealistic

Close-up of tattooed hands working on an intricate mandala tattoo, needle in motion, studio lighting, slow-motion, photorealistic

Tattooed hands arranging amethyst crystals in a sacred geometry grid, incense smoke, candlelight, mystical atmosphere, photorealistic

Full moon rising through dark clouds with sacred geometry light patterns, deep blues and silvers, cinematic, atmospheric

Tattooed hands spreading tarot cards in a fan on dark velvet, candlelight catching the foil, The Moon card revealed, cinematic
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Workflow not triggering | Check that the repo is Public; private repos need a paid plan for Actions |
| HF_TOKEN error | Regenerate token at huggingface.co → Settings → Access Tokens |
| No video in artifacts | Check the Actions log for error messages |
| "Credits exhausted" | Add FAL_KEY or REPLICATE_API_TOKEN as backup provider |
| Slow generation (10+ min) | Normal for free tier — HF Spaces queues can be long |
