#!/bin/bash
# Fucking Gorgeous - Quickstart with Leonardo.ai
set -e

echo "=== Fucking Gorgeous Coloring Book - VPS Setup ==="

# Install deps
apt-get update -qq
apt-get install -y -qq git python3 python3-pip python3-venv poppler-utils fonts-dejavu fonts-liberation 2>/dev/null

# Clone repo
cd /root
if [ -d "fucking-gorgeous-coloring-book" ]; then
  cd fucking-gorgeous-coloring-book && git pull
else
  git clone https://github.com/siamubee2-max/fucking-gorgeous-coloring-book.git
  cd fucking-gorgeous-coloring-book
fi

# Setup venv
python3 -m venv venv
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Set API key
export LEONARDO_API_KEY="da844abf-24a9-46cf-956d-4239de3ebda0"

# Create images dir
mkdir -p images output

echo ""
echo "=== Generating 55 designs with Leonardo.ai ==="
python3 scripts/generate.py

echo ""
echo "=== Assembling PDF ==="
python3 scripts/assemble.py

echo ""
echo "=== Generating cover wrap ==="
python3 scripts/cover_wrap.py

echo ""
echo "=== DONE! ==="
echo "  Interior: output/interior_draft.pdf"
echo "  Cover:    output/cover_wrap.pdf"
echo "  Upload to: https://kdp.amazon.com"
