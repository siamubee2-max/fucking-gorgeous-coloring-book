#!/usr/bin/env python3
"""
F*cking Gorgeous - KDP Cover Wrap Generator
Creates full cover: Front + Spine + Back with bleed
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

IMAGE_DIR = Path("./images")
OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(exist_ok=True)

# KDP specs for 8.5x11 paperback
PAGE_W_INCHES = 8.5
PAGE_H_INCHES = 11.0
PAGE_COUNT = 113  # interior pages
PAPER_THICKNESS = 0.0025  # inches per page (white paper)
BLEED = 0.125  # inches

DPI = 300

# Calculations
SPINE_WIDTH = PAGE_COUNT * PAPER_THICKNESS  # ~0.28 inches
FULL_W = PAGE_W_INCHES + SPINE_WIDTH + PAGE_W_INCHES  # front + spine + back
FULL_H = PAGE_H_INCHES

# With bleed
TOTAL_W = FULL_W + 2 * BLEED
TOTAL_H = FULL_H + 2 * BLEED

# Pixel dimensions
PX_W = int(math.ceil(TOTAL_W * DPI))
PX_H = int(math.ceil(TOTAL_H * DPI))
PX_BLEED = int(BLEED * DPI)
PX_SPINE = int(math.ceil(SPINE_WIDTH * DPI))
PX_PAGE_W = int(PAGE_W_INCHES * DPI)
PX_PAGE_H = int(PAGE_H_INCHES * DPI)

print(f"=== KDP Cover Wrap Generator ===")
print(f"  Pages: {PAGE_COUNT}")
print(f"  Spine width: {SPINE_WIDTH:.3f} inches ({PX_SPINE}px)")
print(f"  Full cover: {TOTAL_W:.3f} x {TOTAL_H:.3f} inches ({PX_W} x {PX_H}px)")
print(f"  Bleed: {BLEED} inches ({PX_BLEED}px)")

# Create canvas
cover = Image.new("RGB", (PX_W, PX_H), (255, 255, 255))
draw = ImageDraw.Draw(cover)

# Load front cover image
front_path = IMAGE_DIR / "cover-front.png"
if front_path.exists():
    print(f"  Loading cover image: {front_path}")
    front_img = Image.open(str(front_path))
    # Resize to fit front cover area (with bleed)
    front_area_w = PX_PAGE_W + PX_BLEED  # front + right bleed
    front_area_h = PX_H  # full height including bleeds
    front_img = front_img.resize((front_area_w, front_area_h), Image.LANCZOS)
    
    # Paste front cover on the right side
    front_x = PX_BLEED + PX_PAGE_W + PX_SPINE  # back + spine + offset
    cover.paste(front_img, (front_x, 0))
    print(f"  Front cover pasted at x={front_x}")
else:
    print(f"  WARNING: No cover-front.png found, using plain white")

# Back cover - simple white with barcodes area
# (KDP will add barcode, we leave it blank)

# Spine - add title text vertically
try:
    # Try to load a font
    font_size = 28
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except:
    font = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Draw spine text (rotated)
spine_x = PX_BLEED + PX_PAGE_W
# Draw spine line
draw.rectangle([spine_x, PX_BLEED, spine_x + PX_SPINE, PX_H - PX_BLEED], fill=(0, 0, 0))

# Spine text - draw rotated manually by creating a separate image
spine_img = Image.new("RGB", (PX_SPINE, PX_H - 2 * PX_BLEED), (0, 0, 0))
spine_draw = ImageDraw.Draw(spine_img)
# Title on spine (bottom to top)
title = "F*CKING GORGEOUS"
author = "MECHAVAULT"

# Draw text on spine
bbox_t = spine_draw.textbbox((0, 0), title, font=font)
tw = bbox_t[2] - bbox_t[0]
th = bbox_t[3] - bbox_t[1]
spine_draw.text(((PX_SPINE - tw) // 2, PX_H // 3), title, fill=(255, 255, 255), font=font)

bbox_a = spine_draw.textbbox((0, 0), author, font=font_small)
aw = bbox_a[2] - bbox_a[0]
spine_draw.text(((PX_SPINE - aw) // 2, 2 * PX_H // 3), author, fill=(255, 255, 255), font=font_small)

# Rotate spine 90 degrees (text reads bottom to top per KDP convention)
spine_img = spine_img.rotate(90, expand=True)

# Paste spine
cover.paste(spine_img, (spine_x, PX_BLEED))

# Draw fold lines (guides) - remove these for final upload
# Left fold (back/spine junction)
# draw.line([(spine_x, 0), (spine_x, PX_H)], fill=(200,200,200), width=1)
# Right fold (spine/front junction) 
# draw.line([(spine_x + PX_SPINE, 0), (spine_x + PX_SPINE, PX_H)], fill=(200,200,200), width=1)

# Save
out_path = OUTPUT_DIR / "cover_wrap.png"
cover.save(str(out_path), "PNG", dpi=(DPI, DPI))
print(f"")
print(f"  Cover saved: {out_path}")
print(f"  Dimensions: {PX_W} x {PX_H} px ({TOTAL_W:.3f} x {TOTAL_H:.3f} inches)")
print(f"  Spine width: {SPINE_WIDTH:.3f} inches ({PX_SPINE} px)")

# Also create a PDF version for KDP upload
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as rl_canvas

pdf_path = OUTPUT_DIR / "cover_wrap.pdf"
c = rl_canvas.Canvas(str(pdf_path), pagesize=(TOTAL_W * inch, TOTAL_H * inch))
c.drawImage(str(out_path), 0, 0, width=TOTAL_W * inch, height=TOTAL_H * inch)
c.save()
print(f"  Cover PDF: {pdf_path}")
print(f"")
print(f"  DONE! Upload both files to KDP:")
print(f"    - Interior: output/interior_draft.pdf")
print(f"    - Cover: output/cover_wrap.pdf (or cover_wrap.png)")
