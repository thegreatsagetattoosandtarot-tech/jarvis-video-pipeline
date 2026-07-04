#!/bin/bash
# vLLM Setup for Nemotron Models (Requires NVIDIA GPU)
# Run this when you have GPU access

set -euo pipefail

echo "════════════════════════════════════════════════"
echo "  vLLM + Nemotron Setup (GPU Required)"
echo "════════════════════════════════════════════════"

# Check for NVIDIA GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ NVIDIA GPU not detected"
    echo "This script requires NVIDIA GPU with CUDA support"
    echo ""
    echo "When you have GPU access, run:"
    echo "  1. Install Docker with NVIDIA runtime"
    echo "  2. Run vLLM container with Nemotron model"
    exit 1
fi

nvidia-smi

# Available Nemotron models for vLLM
cat << 'MODELS'
Available Nemotron models for vLLM:
  - nvidia/Nemotron-3-Ultra-550B (requires 8x H100 80GB)
  - nvidia/Nemotron-3-Super-120B (requires 4x A100 80GB)  
  - nvidia/Nemotron-3-Nano-30B (requires 1-2x A100 40GB)
  - nvidia/Nemotron-3-Nano-4B (requires 1x RTX 3090/4090)

Recommended for consumer GPU:
  nvidia/Nemotron-3-Nano-4B  (~8GB VRAM with 4-bit quantization)
MODELS

read -p "Enter model to deploy (default: nvidia/Nemotron-3-Nano-4B): " MODEL
MODEL="${MODEL:-nvidia/Nemotron-3-Nano-4B}"

# Create vLLM docker-compose
cat > /opt/data/JARVIS_OS/deploy/docker-compose.vllm.yml <<DOCKER
version: '3.8'

services:
  vllm-nemotron:
    image: vllm/vllm-openai:latest
    container_name: jarvis-vllm-nemotron
    restart: unless-stopped
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - HUGGING_FACE_HUB_TOKEN=\${HF_TOKEN:-}
    command: >
      --model $MODEL
      --dtype auto
      --quantization awq
      --max-model-len 8192
      --gpu-memory-utilization 0.9
      --tensor-parallel-size 1
      --host 0.0.0.0
      --port 8000
      --api-key \${VLLM_API_KEY:-nemotron-local}
    ports:
      - "8000:8000"
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s

networks:
  default:
    name: jarvis-network
DOCKER

echo "✅ Created docker-compose.vllm.yml"
echo ""
echo "To deploy when GPU is available:"
echo "  cd /opt/data/JARVIS_OS/deploy"
echo "  export HF_TOKEN=your_huggingface_token"
echo "  export VLLM_API_KEY=nemotron-local"
echo "  docker compose -f docker-compose.vllm.yml up -d"
echo ""
echo "Then update integrations.yaml:"
echo "  nemotron_local:"
echo "    enabled: true"
echo "    base_url: \"http://localhost:8000/v1\""
echo "    api_key: \"nemotron-local\""
echo "    models: [\"$MODEL\"]"
