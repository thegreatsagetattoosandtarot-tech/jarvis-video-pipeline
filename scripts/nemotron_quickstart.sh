#!/bin/bash
# Nemotron Quickstart - Unified Access for JARVIS OS
# Choose your Nemotron deployment path

set -euo pipefail

echo "═════════════════════════════════════════════════════"
echo "  NEMOTRON QUICKSTART - JARVIS OS"
echo "═════════════════════════════════════════════════════"
echo ""
echo "Nemotron Model Options:"
echo ""
echo "  1️⃣  OPENROUTER (Free/Cloud) - RECOMMENDED"
echo "      → nvidia/nemotron-3-ultra-550b-a55b:free"
echo "      → No GPU needed, instant access"
echo "      → Rate limited, internet required"
echo ""
echo "  2️⃣  LOCAL OLLAMA (qwen3:0.6b only)"
echo "      → Already running: qwen3:0.6b (522 MB)"
echo "      → Nemotron not available on Ollama (42GB only)"
echo ""
echo "  3️⃣  VLLM + NEURON (Requires NVIDIA GPU)"
echo "      → nvidia/Nemotron-3-Nano-4B (8GB VRAM)"
echo "      → Full control, no rate limits"
echo "      → Run ./scripts/setup_vllm_nemotron.sh"
echo ""
echo "  4️⃣  HUGGINGFACE INFERENCE API"
echo "      → Serverless, pay-per-token"
echo "      → Good for testing"
echo ""
read -p "Choose option (1-4): " CHOICE

case $CHOICE in
    1)
        echo "Setting up OpenRouter..."
        /opt/data/JARVIS_OS/scripts/setup_openrouter.sh
        ;;
    2)
        echo "Using local qwen3:0.6b via Ollama"
        echo "Model: qwen3:0.6b (already running)"
        echo "Endpoint: http://localhost:11434"
        ;;
    3)
        echo "Setting up vLLM for Nemotron (GPU required)..."
        /opt/data/JARVIS_OS/scripts/setup_vllm_nemotron.sh
        ;;
    4)
        echo "HuggingFace Inference API setup..."
        read -p "Enter HF_TOKEN: " HF_TOKEN
        if [[ -n "$HF_TOKEN" ]]; then
            sed -i "s|huggingface:\n    enabled: false|huggingface:\n    enabled: true|" /opt/data/JARVIS_OS/config/integrations.yaml
            sed -i "s|token: \"\${HF_TOKEN}\"|token: \"$HF_TOKEN\"|" /opt/data/JARVIS_OS/config/integrations.yaml
            echo "✅ HuggingFace configured"
        fi
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "═════════════════════════════════════════════════════"
echo "  Current Model Status:"
echo "═════════════════════════════════════════════════════"

# Check Ollama
if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama: $(curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; print(json.load(sys.stdin)['models'][0]['name'])" 2>/dev/null)"
else
    echo "❌ Ollama: Not running"
fi

# Check OpenRouter
if grep -q "enabled: true" /opt/data/JARVIS_OS/config/integrations.yaml -A 5 | grep -q "openrouter"; then
    echo "✅ OpenRouter: Enabled"
else
    echo "⚠️  OpenRouter: Disabled (run option 1)"
fi

# Check HuggingFace
if grep -q "enabled: true" /opt/data/JARVIS_OS/config/integrations.yaml -A 3 | grep -q "huggingface"; then
    echo "✅ HuggingFace: Enabled"
else
    echo "⚠️  HuggingFace: Disabled"
fi

# Check vLLM
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ vLLM: Running on port 8000"
else
    echo "⚠️  vLLM: Not running (run option 3 with GPU)"
fi

echo "═════════════════════════════════════════════════════"
