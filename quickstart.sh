#!/bin/bash
# ====================================================
# F*CKING GORGEOUS - Quickstart
# Uses HIGGSFIELD API for image generation
# ====================================================
set -e

echo "=========================================="
echo "  Setting up F*cking Gorgeous on VPS..."
echo "=========================================="

# Install deps
apt update && apt install -y git python3-pip python3-venk imagemagick poppler-utils

# Clone (or update)
cd /root
if [ -d "fucking-gorgeous-coloring-book" ]; then
  cd fucking-gorgeous-coloring-book && git pull
else
  git clone https://github.com/siamubee2-max/fucking-gorgeous-coloring-book.git
  cd fucking-gorgeous-coloring-book
fi

# Python venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install reportlab
mkdir -p images output tmp

# Set HIGGSFIELD API key
export HIGGSFIELD_API_KEY="410e1c5d-fac8-40fa-853b-293b255624c1:651d51867a6cf841a97484f8b65a80bfa35e9162265e04b65a97b75934bac171"

echo ""
echo "=========================================="
echo "  SETUP DONE! Starting generation..."
echo "  Backend: Higgsfield API"
echo "=========================================="
echo ""

# Generate all 55 designs in batches
echo "[BATCH 1/4] Designs 1-15..."
python3 scripts/generate.py --start 1 --end 15 --delay 5

echo "[BATCH 2/4] Designs 16-30..."
python3 scripts/generate.py --start 16 --end 30 --delay 5

echo "[BATCH 3/4] Designs 31-40..."
python3 scripts/generate.py --start 31 --end 40 --delay 5

echo "[BATCH 4/4] Designs 41-55..."
python3 scripts/generate.py --start 41 --end 55 --delay 5

echo "[COVER] Generating cover..."
python3 scripts/generate.py --cover

# Assemble PDF (Python-based, no ImageMagick OOM)
echo ""
echo "[ASSEMBLE] Building interior PDF (Python)..."
python3 scripts/assemble.py

echo ""
echo "=========================================="
echo "  ALL DONE!"
echo "=========================================="
echo ""
IMG_COUNT=$(ls -1 images/*.png 2>/dev/null | wc -l)
echo "  $IMG_COUNT images in ./images/"
ls -la output/ 2>/dev/null
echo ""
echo "  Next: Upload to KDP at https://kdp.amazon.com"
echo "=========================================="
