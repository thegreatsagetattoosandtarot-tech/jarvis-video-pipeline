#!/bin/bash
# OpenRouter API Key Configuration for JARVIS OS
# Run this to configure Nemotron access via OpenRouter

set -euo pipefail

CONFIG_DIR="/opt/data/JARVIS_OS/config"
INTEGRATIONS_FILE="$CONFIG_DIR/integrations.yaml"
ENV_FILE="/opt/data/JARVIS_OS/deploy/.env"

echo "════════════════════════════════════════════════"
echo "  OpenRouter API Configuration for Nemotron"
echo "════════════════════════════════════════════════"

# Get API key from user
read -p "Enter your OpenRouter API key (or press Enter to skip): " OPENROUTER_KEY

if [[ -z "$OPENROUTER_KEY" ]]; then
    echo "Skipping OpenRouter configuration"
    exit 0
fi

# Update integrations.yaml
echo "Updating integrations.yaml..."
sed -i "s|openrouter:\n    enabled: false|openrouter:\n    enabled: true|" "$INTEGRATIONS_FILE"
sed -i "s|api_key: \"\${OPENROUTER_API_KEY}\"|api_key: \"$OPENROUTER_KEY\"|" "$INTEGRATIONS_FILE"

# Update deploy/.env
if [[ -f "$ENV_FILE" ]]; then
    sed -i "s|OPENROUTER_API_KEY=.*|OPENROUTER_API_KEY=$OPENROUTER_KEY|" "$ENV_FILE"
else
    echo "OPENROUTER_API_KEY=$OPENROUTER_KEY" >> "$ENV_FILE"
fi

echo "✅ OpenRouter configured with Nemotron access"
echo "Available models:"
echo "  - nvidia/nemotron-3-ultra-550b-a55b:free"
echo "  - anthropic/claude-3.5-sonnet"
echo "  - openai/gpt-4o"
echo "  - google/gemini-pro-1.5"
echo "  - x-ai/grok-2"

# Test the API
echo "Testing API connection..."
curl -s -H "Authorization: Bearer $OPENROUTER_KEY" \
     -H "Content-Type: application/json" \
     "https://openrouter.ai/api/v1/models" | \
     python3 -c "import sys,json; [print(f\"  - {m['id']}\") for m in json.load(sys.stdin)['data'] if 'nemotron' in m['id'].lower()]" 2>/dev/null || echo "  (API test skipped)"

echo "════════════════════════════════════════════════"
