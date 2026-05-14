#!/bin/bash
# F*cking Gorgeous - KDP Interior Assembly
# PREREQUISITES: ImageMagick, Poppler
set -e

echo "=== KDP Interior Assembly ==="

W=2550
H=3300
DPI=300
IMG_DIR="./images"
OUT_DIR="./output"
TMP_DIR="./tmp"
mkdir -p "$OUT_DIR" "$TMP_DIR"

IMG_COUNT=$(ls -1 "$IMG_DIR"/*.png 2>/dev/null | wc -l)
echo "Found $IMG_COUNT images"

echo "[1/5] Normalizing images..."
for img in "$IMG_DIR"/*.png; do
  name=$(basename "$img" .png)
  convert "$img" -resize ${W}x${H}! -units PixelsPerInch -density ${DPI} "$TMP_DIR/${name}_norm.png"
done

echo "[2/5] Creating blank pages..."
convert -size ${W}x${H} xc:white -units PixelsPerInch -density ${DPI} \
  -font Helvetica -pointsize 24 -fill "#cccccc" \
  -annotate +0+3200 "This page intentionally left blank" \
  "$TMP_DIR/blank_page.png"

echo "[3/5] Creating front matter..."
convert -size ${W}x${H} xc:white -units PixelsPerInch -density ${DPI} \
  -font Georgia -pointsize 96 -fill black \
  -annotate +0+1200 "F*CKING\nGORGEOUS" \
  -font Helvetica -pointsize 36 -fill "#666666" \
  -annotate +0+1600 "A Swear Word & Floral Coloring Book" \
  -font Helvetica -pointsize 20 -fill "#999999" \
  -annotate +0+2900 "MechaVault Publishing" \
  "$TMP_DIR/title_page.png"

convert -size ${W}x${H} xc:white -units PixelsPerInch -density ${DPI} \
  -font Helvetica -pointsize 22 -fill "#666666" \
  -annotate +150+800 "Copyright 2026 MechaVault Publishing. All rights reserved." \
  -font Helvetica -pointsize 16 -fill "#999999" \
  -annotate +150+900 "ISBN: KDP-assigned. First Edition. Printed in USA." \
  "$TMP_DIR/copyright_page.png"

convert -size ${W}x${H} xc:white -units PixelsPerInch -density ${DPI} \
  -font Georgia -pointsize 36 -fill "#666666" -gravity Center \
  -annotate +0+0 "For everyone who needs\nto tell stress to f*ck off." \
  "$TMP_DIR/dedication_page.png"

echo "[4/5] Assembling PDF..."
PAGES="$TMP_DIR/blank_page.png $TMP_DIR/title_page.png $TMP_DIR/copyright_page.png $TMP_DIR/dedication_page.png"
for i in $(ls "$TMP_DIR"/*_norm.png | sort -V); do
  PAGES="$PAGES $TMP_DIR/blank_page.png $i"
done

convert $PAGES -density ${DPI} -page ${W}x${H} "$OUT_DIR/interior_draft.pdf"

echo "[5/5] Verifying..."
PAGE_COUNT=$(pdfinfo "$OUT_DIR/interior_draft.pdf" | grep "Pages:" | awk "{print \$2}")
echo "Pages: $PAGE_COUNT"
echo "Output: $OUT_DIR/interior_draft.pdf"
echo "=== Done ==="