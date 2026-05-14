#!/usr/bin/env python3
"""
F*cking Gorgeous - KDP Interior PDF Assembler
Uses Pillow + reportlab (low memory, no ImageMagick)
"""
import os
import sys
from pathlib import Path
from PIL import Image

IMAGE_DIR = Path("./images")
OUTPUT_DIR = Path("./output")
TMP_DIR = Path("./tmp")

PAGE_W = 2550  # 8.5 * 300
PAGE_H = 3300  # 11 * 300
DPI = 300


def find_images():
    return sorted(IMAGE_DIR.glob("design_*.png")), IMAGE_DIR / "cover-front.png"


def build_pdf(images):
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    TMP_DIR.mkdir(exist_ok=True)
    pdf_path = OUTPUT_DIR / "interior_draft.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=(8.5*inch, 11*inch))
    c.setTitle("F*cking Gorgeous: A Swear Word & Floral Coloring Book")
    c.setAuthor("MechaVault")
    c.setSubject("Adult Coloring Book")
    
    # Page 1: Title
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(4.25*inch, 7*inch, "F*CKING GORGEOUS")
    c.setFont("Helvetica", 18)
    c.drawCentredString(4.25*inch, 6.2*inch, "A Swear Word & Floral Coloring Book")
    c.drawCentredString(4.25*inch, 5.7*inch, "for Stressed-Out Adults")
    c.setFont("Helvetica", 14)
    c.drawCentredString(4.25*inch, 4.5*inch, "50 Sassy Designs to Color Your Stress Away")
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(4.25*inch, 3.5*inch, "MechaVault Publishing")
    c.showPage()
    
    # Page 2: Copyright
    c.setFont("Helvetica", 12)
    c.drawCentredString(4.25*inch, 9*inch, "F*cking Gorgeous: A Swear Word & Floral Coloring Book")
    c.drawCentredString(4.25*inch, 8.5*inch, "Copyright 2026 MechaVault Publishing. All rights reserved.")
    c.drawCentredString(4.25*inch, 8*inch, "No part of this publication may be reproduced.")
    c.drawCentredString(4.25*inch, 7*inch, "For personal use only. Not for resale.")
    c.drawCentredString(4.25*inch, 5.5*inch, "This book is dedicated to everyone who needs")
    c.drawCentredString(4.25*inch, 5*inch, "to color their stress away. You deserve it.")
    c.showPage()
    
    # Blank page for reference
    blank_path = TMP_DIR / "blank_page.png"
    blank = Image.new("RGB", (PAGE_W, PAGE_H), (255, 255, 255))
    blank.save(str(blank_path), "PNG", dpi=(DPI, DPI))
    
    # Design + blank pairs
    for i, img_path in enumerate(images):
        if i % 10 == 0:
            print(f"  Adding page {i+1}/{len(images)}: {img_path.name}")
        c.drawImage(str(img_path), 0, 0, width=8.5*inch, height=11*inch,
                    preserveAspectRatio=False)
        c.showPage()
        c.drawImage(str(blank_path), 0, 0, width=8.5*inch, height=11*inch,
                    preserveAspectRatio=False)
        c.showPage()
    
    # Final page
    c.setFont("Helvetica-Oblique", 14)
    c.drawCentredString(4.25*inch, 6*inch, "Thank you for coloring with us!")
    c.drawCentredString(4.25*inch, 5*inch, "More books at MechaVault Publishing")
    c.showPage()
    
    c.save()
    return pdf_path


def main():
    print("=== KDP Interior Assembly (Python) ===")
    
    images, cover = find_images()
    print(f"  Found {len(images)} design images")
    
    if not images:
        print("  ERROR: No design images found in ./images/")
        sys.exit(1)
    
    print("  Building PDF with reportlab (memory-efficient)...")
    pdf_path = build_pdf(images)
    
    size_mb = pdf_path.stat().st_size / (1024 * 1024)
    print(f"")
    print(f"  PDF: {pdf_path} ({size_mb:.1f} MB)")
    print(f"  Pages: ~{2 + len(images) * 2 + 1}")
    print("")
    print("  DONE! Upload to KDP.")
    print("  Next: https://kdp.amazon.com")


if __name__ == "__main__":
    main()
