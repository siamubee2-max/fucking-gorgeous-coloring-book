#!/bin/bash
# ================================================
# F*cking Gorgeous - ONE COMMAND TO RULE THEM ALL
# ================================================
# Usage: bash run-all.sh
# 
# Prerequisites: Set your API key before running
#   export HIGGSFIELD_API_KEY="key:secret"
#   # OR
#   export OPENAI_API_KEY="sk-..."

set -e

echo "========================================="
echo "  F*CKING GORGEOUS - Production Pipeline"
echo "========================================="
echo ""

# Check API keys
if [ -z "\$HIGGSFIELD_API_KEY" ] && [ -z "\$OPENAI_API_KEY" ]; then
  echo "ERROR: Set your API key first!"
  echo "  export HIGGSFIELD_API_KEY=\"your_key:your_secret\""
  echo "  # OR"
  echo "  export OPENAI_API_KEY=\"sk-...\""
  exit 1
fi

BACKEND="Higgsfield"
[ -z "\$HIGGSFIELD_API_KEY" ] && BACKEND="DALL-E 3"
echo "Backend: \$BACKEND"
echo ""

# Setup if needed
if [ ! -d "venv" ]; then
  echo "[SETUP] Installing dependencies..."
  bash scripts/setup-vps.sh
fi

source venv/bin/activate

# Generate images
echo ""
echo "[GENERATE] Starting image generation..."
echo "This will take a while (~55 images x ~30s each = ~30 min)"
echo ""

python3 scripts/generate.py --start 1 --end 55 --delay 3

echo ""
echo "[COVER] Generating cover image..."
python3 scripts/generate.py --cover

# Assemble PDF
echo ""
echo "[ASSEMBLE] Building interior PDF..."
bash scripts/assemble.sh

echo ""
echo "========================================="
echo "  PRODUCTION COMPLETE!"
echo "========================================="
echo ""
echo "Output files:"
ls -la output/ 2>/dev/null || echo "  (check output/ directory)"
echo ""
echo "NEXT: Upload to KDP!"
echo "  1. Go to https://kdp.amazon.com"
echo "  2. Create new paperback"
echo "  3. Use metadata from KDP.md"
echo "  4. Upload interior PDF + cover"
echo ""
