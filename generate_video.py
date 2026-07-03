#!/usr/bin/env python3
"""
JARVIS Video Generation Script
Tries multiple free/cheap inference providers in priority order:
  1. FAL.ai (if FAL_KEY set) — LTX-Video or HunyuanVideo
  2. HuggingFace Inference API (if HF_TOKEN set) — CogVideoX-2B
  3. Replicate (if REPLICATE_API_TOKEN set) — Wan-2.1
  4. HuggingFace Spaces direct call (no key needed, queue-based)

Usage:
    python generate_video.py --prompt "..." --duration 5 --output output/video.mp4
"""

import argparse
import os
import sys
import requests
import time
import json
import urllib.request


# ─────────────────────────────────────────────
# 1. FAL.ai — LTX-Video (fastest) or HunyuanVideo
# ─────────────────────────────────────────────
def generate_via_fal(prompt: str, duration: int, output_path: str) -> bool:
    """Generate video via FAL.ai. Requires FAL_KEY env var."""
    fal_key = os.environ.get('FAL_KEY', '')
    if not fal_key:
        print("FAL_KEY not set — skipping FAL.ai")
        return False

    try:
        import fal_client
    except ImportError:
        print("fal-client not installed — skipping FAL.ai")
        return False

    # Use LTX-Video for speed, HunyuanVideo for quality
    model = "fal-ai/ltx-video"  # fast, good quality
    print(f"[FAL.ai] Submitting to {model}...")

    try:
        handler = fal_client.submit(
            model,
            arguments={
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": "9:16",
                "negative_prompt": "blurry, low quality, cartoon, CGI, anime, distorted",
            }
        )
        print("[FAL.ai] Waiting for result (30–120s typical)...")
        result = handler.get()

        video_url = result.get("video", {}).get("url") or result.get("url")
        if not video_url:
            print(f"[FAL.ai] No video URL in response: {list(result.keys())}")
            return False

        print(f"[FAL.ai] Downloading from {video_url[:60]}...")
        urllib.request.urlretrieve(video_url, output_path)
        size = os.path.getsize(output_path)
        print(f"[FAL.ai] ✅ Saved to {output_path} ({size:,} bytes)")
        return True

    except Exception as e:
        print(f"[FAL.ai] Error: {e}")
        return False


# ─────────────────────────────────────────────
# 2. HuggingFace Inference API — CogVideoX-2B
#    NOTE: As of 2025, HF Inference (hf-inference provider) focuses on CPU tasks.
#    For video, FAL.ai provider via HF InferenceClient is the right path.
# ─────────────────────────────────────────────
def generate_via_hf_inference(prompt: str, hf_token: str) -> bytes | None:
    """Try HuggingFace Inference API for video generation (CogVideoX-2B)."""
    if not hf_token:
        print("[HF Inference] HF_TOKEN not set — skipping")
        return None

    # Try via huggingface_hub InferenceClient with FAL provider
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(
            provider="fal-ai",
            api_key=hf_token,
        )
        print("[HF Inference] Submitting to LTX-Video via FAL provider...")
        result = client.text_to_video(
            "Lightricks/LTX-Video-0.9.8-13B-distilled",
            prompt=prompt,
        )
        # result is bytes or a FileObject
        if hasattr(result, 'read'):
            return result.read()
        elif isinstance(result, bytes):
            return result
        else:
            print(f"[HF Inference] Unexpected result type: {type(result)}")
            return None

    except Exception as e:
        print(f"[HF Inference] FAL provider failed: {e}")

    # Direct CogVideoX-2B fallback
    api_url = "https://api-inference.huggingface.co/models/THUDM/CogVideoX-2b"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {
        "inputs": prompt,
        "parameters": {"num_frames": 49, "fps": 8}
    }
    print(f"[HF Inference] Direct API: CogVideoX-2B...")
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=300)
        if response.status_code == 200:
            return response.content
        else:
            print(f"[HF Inference] {response.status_code}: {response.text[:300]}")
            return None
    except Exception as e:
        print(f"[HF Inference] Request error: {e}")
        return None


# ─────────────────────────────────────────────
# 3. Replicate — Wan-2.1 480p
# ─────────────────────────────────────────────
def generate_via_replicate(prompt: str, output_path: str) -> bool:
    """Generate via Replicate API. Requires REPLICATE_API_TOKEN."""
    token = os.environ.get('REPLICATE_API_TOKEN', '')
    if not token:
        print("[Replicate] REPLICATE_API_TOKEN not set — skipping")
        return False

    try:
        import replicate
    except ImportError:
        print("[Replicate] replicate package not installed — skipping")
        return False

    print("[Replicate] Submitting Wan-2.1 480p...")
    try:
        output = replicate.run(
            "wavespeed-ai/wan-2.1-t2v-480p",
            input={
                "prompt": prompt,
                "num_frames": 81,
                "fps": 16,
                "guidance_scale": 6.0,
            }
        )
        if isinstance(output, str):
            urllib.request.urlretrieve(output, output_path)
        elif hasattr(output, '__iter__'):
            url = list(output)[0]
            urllib.request.urlretrieve(str(url), output_path)
        else:
            with open(output_path, 'wb') as f:
                f.write(output.read())

        size = os.path.getsize(output_path)
        print(f"[Replicate] ✅ Saved to {output_path} ({size:,} bytes)")
        return True

    except Exception as e:
        print(f"[Replicate] Error: {e}")
        return False


# ─────────────────────────────────────────────
# 4. HuggingFace Spaces — Gradio API (no key needed, queue-based)
# ─────────────────────────────────────────────
def generate_via_hf_space(prompt: str, output_path: str) -> bool:
    """
    Submit to a public HuggingFace Space running CogVideoX via Gradio API.
    Queue-based, can take 5-30 minutes. No API key required.
    """
    print("[HF Space] Trying public CogVideoX Space (queue-based, may be slow)...")
    try:
        from huggingface_hub import InferenceClient
        # Try the THUDM CogVideoX Space
        space_url = "https://thudm-cogvideox-5b-space.hf.space"
        response = requests.post(
            f"{space_url}/run/predict",
            json={
                "data": [prompt, None, 49, 6.0, 50, "euler", True, 42]
            },
            timeout=600
        )
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]:
                video_path = data["data"][0]
                if isinstance(video_path, str) and video_path.startswith("http"):
                    urllib.request.urlretrieve(video_path, output_path)
                    size = os.path.getsize(output_path)
                    print(f"[HF Space] ✅ Saved to {output_path} ({size:,} bytes)")
                    return True
    except Exception as e:
        print(f"[HF Space] Error: {e}")

    print("[HF Space] Direct Space submission failed.")
    print("Manual alternative: Visit https://huggingface.co/spaces/THUDM/CogVideoX-2b")
    return False


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="JARVIS Video Generation — Multi-provider")
    parser.add_argument('--prompt', required=True, help='Video generation prompt')
    parser.add_argument('--duration', default='5', type=int, help='Duration in seconds')
    parser.add_argument('--model', default='cogvideox',
                        choices=['cogvideox', 'ltx', 'hunyuan', 'wan'],
                        help='Preferred model (falls back if unavailable)')
    parser.add_argument('--output', default='output/video.mp4', help='Output path')
    args = parser.parse_args()

    hf_token = os.environ.get('HF_TOKEN', '')
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)

    print(f"\n{'='*60}")
    print(f"JARVIS VIDEO GENERATION")
    print(f"Prompt: {args.prompt[:80]}...")
    print(f"Duration: {args.duration}s | Model preference: {args.model}")
    print(f"{'='*60}\n")

    # Try providers in priority order
    success = False

    # 1. Try FAL.ai (best quality + speed, needs own key)
    if not success:
        success = generate_via_fal(args.prompt, args.duration, args.output)

    # 2. Try HuggingFace Inference
    if not success:
        video_bytes = generate_via_hf_inference(args.prompt, hf_token)
        if video_bytes and len(video_bytes) > 1000:
            with open(args.output, 'wb') as f:
                f.write(video_bytes)
            print(f"[HF Inference] ✅ Saved to {args.output} ({len(video_bytes):,} bytes)")
            success = True

    # 3. Try Replicate
    if not success:
        success = generate_via_replicate(args.prompt, args.output)

    # 4. Try HuggingFace Space (last resort)
    if not success:
        success = generate_via_hf_space(args.prompt, args.output)

    if success:
        print(f"\n✅ Video generation complete: {args.output}")
        sys.exit(0)
    else:
        print("\n❌ All providers failed. See messages above for details.")
        print("\nManual options:")
        print("  - https://huggingface.co/spaces/THUDM/CogVideoX-2b (free, web UI)")
        print("  - https://fal.ai (get free $1 credit at signup)")
        print("  - https://replicate.com (get free $10 credit at signup)")
        sys.exit(1)


if __name__ == '__main__':
    main()
