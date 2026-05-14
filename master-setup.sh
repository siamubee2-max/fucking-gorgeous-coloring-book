#!/bin/bash
# =====================================================
# F*CKING GORGEOUS - Master Setup & Generate Script
# Run this on your VPS: bash master-setup.sh
# =====================================================
set -e

echo "=========================================="
echo "  F*CKING GORGEOUS - Master Setup"
echo "=========================================="
echo ""

# 1. System deps
echo "[1/4] Installing system dependencies..."
apt update && apt install -y git python3-pip python3-venv imagemagick poppler-utils wget curl

# 2. Clone repo
echo "[2/4] Cloning project..."
cd /root
if [ -d "fucking-gorgeous-coloring-book" ]; then
  cd fucking-gorgeous-coloring-book && git pull
else
  git clone https://github.com/siamubee2-max/fucking-gorgeous-coloring-book.git
  cd fucking-gorgeous-coloring-book
fi
mkdir -p images output tmp

# 3. Python venv
echo "[3/4] Setting up Python..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install requests Pillow

# 4. Check for API keys
echo "[4/4] Checking API keys..."
BACKEND=""
if [ -n "$HIGGSFIELD_API_KEY" ]; then
  BACKEND="HIGGSFIELD"
  echo "  Using: Higgsfield API"
elif [ -n "$OPENAI_API_KEY" ]; then
  BACKEND="OPENAI"
  echo "  Using: OpenAI DALL-E 3"
else
  echo ""
  echo "  *** NO API KEY SET ***"
  echo ""
  echo "  Set one before generating:"
  echo "    export HIGGSFIELD_API_KEY=\"your_key:your_secret\""
  echo "    # OR"
  echo "    export OPENAI_API_KEY=\"sk-...\""
  echo ""
  echo "  To get Higgsfield key (FREE credits):"
  echo "    1. Go to https://platform.higgsfield.ai"
  echo "    2. Sign up / Log in"
  echo "    3. Go to Dashboard > API Keys"
  echo "    4. Create a new key"
  echo "    5. Copy the key:secret format"
  echo ""
fi

echo ""
echo "=========================================="
echo "  SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "NEXT: Generate images with one of these commands:"
echo ""
echo "  # Option A: Using the Python script (Higgsfield or DALL-E)"
echo "  source venv/bin/activate"
echo "  export HIGGSFIELD_API_KEY=\"key:secret\""
echo "  python3 scripts/generate.py --start 1 --end 55 --delay 3"
echo "  python3 scripts/generate.py --cover"
echo ""
echo "  # Option B: Using the run-all script"
echo "  source venv/bin/activate"
echo "  export HIGGSFIELD_API_KEY=\"key:secret\""
echo "  bash run-all.sh"
echo ""
echo "  # Option C: Batch generation (safer for rate limits)"
echo "  source venv/bin/activate"
echo "  export HIGGSFIELD_API_KEY=\"key:secret\""
echo "  python3 scripts/generate.py --start 1 --end 15 --delay 5"
echo "  python3 scripts/generate.py --start 16 --end 30 --delay 5"
echo "  python3 scripts/generate.py --start 31 --end 55 --delay 5"
echo "  python3 scripts/generate.py --cover"
echo ""
echo "  # Assemble PDF after generation:"
echo "  bash scripts/assemble.sh"
echo ""
echo "Then upload to KDP!"
echo "=========================================="
