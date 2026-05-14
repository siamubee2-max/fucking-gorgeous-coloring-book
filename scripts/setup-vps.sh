#!/bin/bash
# ================================================
# F*cking Gorgeous - VPS Setup Script
# Run this on your VPS to set everything up
# ================================================
set -e

echo "=== F*cking Gorgeous: VPS Setup ==="
echo ""

# 1. Install dependencies
echo "[1/6] Installing system dependencies..."
apt update && apt install -y git python3-pip python3-venv imagemagick poppler-utils

# 2. Create project directory
echo "[2/6] Cloning project..."
cd /root
if [ -d "fucking-gorgeous-coloring-book" ]; then
  cd fucking-gorgeous-coloring-book && git pull
else
  git clone https://github.com/siamubee2-max/fucking-gorgeous-coloring-book.git
  cd fucking-gorgeous-coloring-book
fi

# 3. Create virtual environment
echo "[3/6] Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install requests Pillow

# 4. Create directories
echo "[4/6] Creating directories..."
mkdir -p images output tmp

# 5. Download prompts as separate files for easy access
echo "[5/6] Project ready!"

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Set your API key:"
echo "   # For Higgsfield:"
echo "   export HIGGSFIELD_API_KEY=\"your_key:your_secret\""
echo "   # OR for DALL-E:"
echo "   export OPENAI_API_KEY=\"sk-...\""
echo ""
echo "2. Generate images:"
echo "   source venv/bin/activate"
echo "   python3 scripts/generate.py --start 1 --end 55 --delay 3"
echo "   python3 scripts/generate.py --cover"
echo ""
echo "3. Assemble PDF:"
echo "   bash scripts/assemble.sh"
echo ""
echo "4. Check output:"
echo "   ls -la output/"
echo ""
echo "Done! Happy coloring book creation."
