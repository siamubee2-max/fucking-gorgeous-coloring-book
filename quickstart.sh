#!/bin/bash
# ====================================================
# F*CKING GORGEOUS - Quickstart (copy-paste this)
# ====================================================
set -e

echo "=========================================="
echo "  Setting up F*cking Gorgeous on VPS..."
echo "=========================================="

# Install deps
apt update && apt install -y git python3-pip python3-venv imagemagick poppler-utils

# Clone
cd /root
rm -rf fucking-gorgeous-coloring-book 2>/dev/null || true
git clone https://github.com/siamubee2-max/fucking-gorgeous-coloring-book.git
cd fucking-gorgeous-coloring-book

# Python venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
mkdir -p images output tmp

# Set HF API key
export HF_API_KEY="410e1c5d-fac8-40fa-853b-293b255624c1"

echo ""
echo "=========================================="
echo "  SETUP DONE! Starting generation..."
echo "=========================================="
echo ""

# Generate all 55 designs in batches to avoid rate limits
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

# Assemble PDF
echo ""
echo "[ASSEMBLE] Building interior PDF..."
bash scripts/assemble.sh

echo ""
echo "=========================================="
echo "  ALL DONE!"
echo "=========================================="
echo ""
echo "Generated files:"
ls -la images/*.png 2>/dev/null | wc -l
echo " images in ./images/"
ls -la output/ 2>/dev/null
echo ""
echo "Next: Upload to KDP at https://kdp.amazon.com"
echo "=========================================="
