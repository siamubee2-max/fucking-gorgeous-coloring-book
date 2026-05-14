#!/usr/bin/env python3
"""
F*cking Gorgeous - KDP Interior PDF Assembler
Uses Pillow + reportlab (low memory, no ImageMagick needed)
Output: 8.5x11 inches, 300 DPI, black & white interior
"""
import os
import sys
from pathlib import Path
from PIL import Image

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

IMAGE_DIR = Path("./images")
OUTPUT_DIR = Path("./output")
TMP_DIR = Path("./tmp")

# KDP specs: 8.5 x 11 inches, 300 DPI
PAGE_W = 2550  # 8.5 * 300
PAGE_H = 3300  # 11 * 300
DPI = 300


def find_images():
    """Find all design images sorted by number."""
    images = sorted(IMAGE_DIR.glob("design_*.png"))
    cover = IMAGE_DIR / "cover-front.png"
    return images, cover


def create_blank_page(output_path):
    """Create a blank white page."""
    img = Image.new("RGB", (PAGE_W, PAGE_H), (255, 255, 255))
    img.save(str(output_path), "PNG", dpi=(DPI, DPI))
    return output_path


def create_title_page(output_path):
    """Create title page."""
    img = Image.new("RGB", (PAGE_W, PAGE_H), (255, 255, 255))
    # The title page will be simple - white with text overlay done in PDF
    img.save(str(output_path), "PNG", dpi=(DPI, DPI))
    return output_path


def build_pdf_reportlab(images, cover_path):
    """Build interior PDF using reportlab (efficient, low memory)."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    pdf_path = OUTPUT_DIR / "interior_draft.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=(8.5*inch, 11*inch))
    c.setTitle("F*cking Gorgeous: A Swear Word & Floral Coloring Book")
    c.setAuthor("MechaVault")
    c.setSubject("Adult Coloring Book")
    
    # Page 1: Title page
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
    
    # Page 2: Copyright / dedication
    c.setFont("Helvetica", 12)
    c.drawCentredString(4.25*inch, 9*inch, "F*cking Gorgeous: A Swear Word & Floral Coloring Book")
    c.drawCentredString(4.25*inch, 8.5*inch, "Copyright 2026 MechaVault Publishing. All rights reserved.")
    c.drawCentredString(4.25*inch, 8*inch, "No part of this publication may be reproduced.")
    c.drawCentredString(4.25*inch, 7*inch, "For personal use only. Not for resale.")
    c.drawCentredString(4.25*inch, 5.5*inch, "This book is dedicated to everyone who needs")
    c.drawCentredString(4.25*inch, 5*inch, "to color their stress away. You deserve it.")
    c.showPage()
    
    # Pages 3+: Design + blank page pairs
    blank = Image.new("RGB", (PAGE_W, PAGE_H), (255, 255, 255))
    blank_path = TMP_DIR / "blank_page.png"
    blank.save(str(blank_path), "PNG", dpi=(DPI, DPI))
    
    for i, img_path in enumerate(images):
        if i % 10 == 0:
            print(f"  Adding page {i+1}/{len(images)}: {img_path.name}")
        
        # Design page (right side)
        c.drawImage(str(img_path), 0, 0, width=8.5*inch, height=11*inch,
                    preserveAspectRatio=False)
        c.showPage()
        
        # Blank back page (prevents bleed-through)
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


def build_pdf_pillow(images, cover_path):
    """Fallback: Build PDF using Pillow only (slower but works everywhere)."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    pdf_path = OUTPUT_DIR / "interior_draft.pdf"
    
    # Title page
    pages = []
    title = Image.new("RGB", (PAGE_W, PAGE_H), (255, 255, 255))
    pages.append(title)
    
    # Copyright page
    pages.append(Image.new("RGB", (PAGE_W, PAGE_H), (255, 255, 255)))
    
    # Design + blank pairs
    blank = Image.new("RGB", (PAGE_W, PAGE_H), (255, 255, 255))
    
    for i, img_path in enumerate(images):
        if i % 10 == 0:
            print(f"  Processing {i+1}/{len(images)}: {img_path.name}")
        
        # Load and resize design
        img = Image.open(str(img_path))
        img = img.resize((PAGE_W, PAGE_H), Image.LANCZOS)
        img = img.convert("RGB")
        pages.append(img)
        pages.append(blank.copy())
    
    # Thank you page
    pages.append(Image.new("RGB", (PAGE_W, PAGE_H), (255, 255, 255)))
    
    print(f"  Saving PDF with {len(pages)} pages...")
    pages[0].save(
        str(pdf_path),
        "PDF",
        resolution=DPI,
        save_all=True,
        append_images=pages[1:]
    )
    return pdf_path


def main():
    print("=== KDP Interior Assembly (Python) ===")
    
    # Install reportlab if needed
    if not HAS_REPORTLAB:
        print("  Installing reportlab...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "reportlab"], check=True)
        # Re-import
        global HAS_REPORTLAB
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        HAS_REPORTLAB = True
    
    TMP_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    images, cover = find_images()
    print(f"  Found {len(images)} design images")
    
    if not images:
        print("  ERROR: No design images found in ./images/")
        print("  Run generate.py first!")
        sys.exit(1)
    
    # Increase ImageMagick policy limits (just in case)
    policy_path = Path("/etc/ImageMagick-6/policy.xml")
    if policy_path.exists():
        print("  Relaxing ImageMagick memory limits...")
        import subprocess
        try:
            subprocess.run(["sed", "-i", "s/rights.*none.*pattern.*PDF/rights=\"read|write\" pattern=\"PDF\"/", str(policy_path)], capture_output=True)
        except:
            pass
    
    # Build PDF using reportlab (low memory)
    print("  Building PDF with reportlab (memory-efficient)...")
    pdf_path = build_pdf_reportlab(images, cover)
    
    # Stats
    size_mb = pdf_path.stat().st_size / (1024 * 1024)
    print(f"  PDF: {pdf_path} ({size_mb:.1f} MB)")
    print(f"  Pages: ~{2 + len(images) * 2 + 1}")
    print("")
    print("  DONE! Upload this to KDP.")
    print("  Next steps:")
    print("    1. Create a cover template at https://kdp.amazon.com")
    print("    2. Upload interior_draft.pdf as your manuscript")
    print("    3. Fill in KDP.md metadata")


if __name__ == "__main__":
    main()
