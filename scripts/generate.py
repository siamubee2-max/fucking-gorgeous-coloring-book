#!/usr/bin/env python3
"""
Fucking Gorgeous - Leonardo.ai Image Generation + Pillow Text Overlay
Generates 50 designs (art via Leonardo Phoenix, text via Pillow) + 1 cover.
"""

import os, sys, time, json, requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO

LEONARDO_API_KEY = os.environ.get("LEONARDO_API_KEY", "")
LEONARDO_BASE = "https://cloud.leonardo.ai/api/rest/v1"

# Phoenix 1.0 model ID (discovered via API)
PHOENIX_MODEL_ID = "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3"

def generate_with_leonardo(prompt, width=1024, height=1536):
    """Generate image with Leonardo.ai Phoenix API."""
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "modelId": PHOENIX_MODEL_ID,
        "num_images": 1,
        "width": width,
        "height": height,
        "guidance_scale": 7,
        "negative_prompt": "color, shading, gradient, grey tones, shadow, photograph, realistic, 3d render, blurry, low quality",
        "num_inference_steps": 30,
        "public": False,
        "scheduler": "LEONARDO"
    }
    
    # Submit generation
    resp = requests.post(
        f"{LEONARDO_BASE}/generations",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if resp.status_code != 200:
        print(f"  Leonardo API error {resp.status_code}: {resp.text[:300]}")
        return None
    
    data = resp.json()
    generation_id = data.get("sdGenerationJob", {}).get("generationId") or data.get("generationId")
    
    if not generation_id:
        # Try alternative response format
        if "generationId" in data:
            generation_id = data["generationId"]
        else:
            print(f"  No generation ID: {json.dumps(data)[:300]}")
            return None
    
    # Poll for completion (max 3 minutes)
    for attempt in range(36):
        time.sleep(5)
        try:
            status_resp = requests.get(
                f"{LEONARDO_BASE}/generations/{generation_id}",
                headers=headers,
                timeout=10
            )
            if status_resp.status_code != 200:
                continue
            
            status_data = status_resp.json()
            # Navigate various response formats
            generations = status_data.get("generations", [])
            if not generations and "sdGenerationJob" in status_data:
                generations = status_data["sdGenerationJob"].get("generations", [])
            if not generations and "generations_by_pk" in status_data:
                generations = [status_data["generations_by_pk"]]
            
            if generations and len(generations) > 0:
                gen = generations[0]
                status = gen.get("status", "")
                img_url = gen.get("url")
                
                if img_url and (status == "COMPLETE" or status == "completed"):
                    print(f"  Image ready, downloading...")
                    img_resp = requests.get(img_url, timeout=30)
                    if img_resp.status_code == 200:
                        return Image.open(BytesIO(img_resp.content))
                elif status == "FAILED":
                    print(f"  Generation failed")
                    return None
        except Exception as e:
            print(f"  Polling error: {e}")
        
        if attempt % 6 == 0:
            print(f"  Waiting... (attempt {attempt+1}/36)")
    
    print("  Timeout waiting for generation")
    return None

def add_text_overlay(img, word, font_size_ratio=0.15):
    """Add crisp vector text overlay using Pillow - zero typos guaranteed."""
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    # Load a bold font
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    
    font_size = int(h * font_size_ratio)
    font = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, font_size)
                print(f"  Using font: {fp}")
                break
            except:
                continue
    
    if font is None:
        font = ImageFont.load_default()
        print("  WARNING: Using default font (may look bad)")
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), word, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # Center the text (slightly above center for balance)
    x = (w - text_w) // 2
    y = (h - text_h) // 2 - int(h * 0.05)
    
    # Draw outline for readability
    outline_width = max(3, font_size // 15)
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            draw.text((x + dx, y + dy), word, fill="black", font=font)
    
    # Draw main text in white for contrast against line art
    draw.text((x, y), word, fill="white", font=font)
    
    # Add thin black border around white text
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), word, fill="black", font=font)
    draw.text((x, y), word, fill="white", font=font)
    
    return img

def process_to_lineart(img):
    """Convert to clean B&W line art for KDP printing."""
    img = img.convert("L")
    img = ImageOps.autocontrast(img, cutoff=5)
    img = img.point(lambda p: 255 if p > 128 else 0, '1')
    img = img.convert("RGB")
    return img

def resize_for_kdp(img):
    """Resize to KDP spec: 2550x3300px at 300 DPI."""
    img = img.resize((2550, 3300), Image.LANCZOS)
    return img

# DESIGN PROMPTS - Art only, NO TEXT (text added via Pillow)
PROMPTS = {
    1: ("FUCK", "Intricate floral mandala with roses, peonies, and curling vines forming a circular frame, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    2: ("SHIT", "Ornamental floral wreath with daisies, sunflowers and intertwining leaves forming a decorative frame, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    3: ("DAMN", "Decorative floral scrollwork with lilies, tulips and sweeping decorative curves forming an ornate border, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    4: ("ASS", "Symmetrical floral pattern with chrysanthemums and geometric petal frames forming a mandala, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    5: ("BITCH", "Elegant floral border with roses, thorns and ribbon-like vines forming a frame, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    6: ("HELL", "Bold floral mandala with lotus flowers and radiating petal design, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    7: ("CRAP", "Whimsical floral arrangement with wildflowers and butterfly accents, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    8: ("HECK", "Dramatic floral composition with orchids and sweeping decorative stems forming a frame, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    9: ("F*CK", "Delicate floral circle with lavender sprigs and daisy chain forming a wreath, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    10: ("BADASS", "Bold tribal floral design with sunflowers and geometric borders, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),

    # Category 2: Empowering Words
    11: ("SLAY", "Fierce floral crown with roses and laurel leaves, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    12: ("BOLD", "Strong geometric floral pattern with sunbursts and hibiscus, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    13: ("FIERCE", "Dramatic floral arrangement with birds of paradise and palm leaves, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    14: ("WILD", "Wildflower meadow design with daisies, poppies and intertwining vines, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    15: ("FEARLESS", "Brave floral shield with roses and crossed leaf swords, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    16: ("QUEEN", "Royal floral crown with roses, jewels and ornate scrollwork, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    17: ("BOSS", "Powerful floral emblem with lotus and radiating sun rays, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    18: ("MIGHTY", "Majestic floral arrangement with irises and crown-like lily frames, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    19: ("STRONG", "Solid floral anchor design with nautical roses and rope borders, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    20: ("FEISTY", "Spiky floral pattern with thistles and bold leaf clusters, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),

    # Category 3: Stress Relief
    21: ("BREATHE", "Zen floral mandala with lotus and serene water ripple frame, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    22: ("CHILL", "Relaxed floral pattern with chamomile and gentle curve borders, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    23: ("ZEN", "Minimalist floral design with single orchid and minimalist line frame, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    24: ("CALM", "Peaceful floral wreath with jasmine and soft vine curves, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    25: ("RELAX", "Soothing floral circle with lavender and eucalyptus sprigs, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    26: ("PEACE", "Harmonious floral design with olive branches and dove silhouettes, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    27: ("SERENE", "Tranquil floral arrangement with water lilies and floating leaves, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    28: ("UNWIND", "Flowing floral pattern with wisteria and sweeping vine tendrils, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    29: ("FLOW", "Organic floral design with flowing vines and bell flowers, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    30: ("DREAM", "Ethereal floral dreamcatcher with roses and feather accents, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),

    # Category 4: Word Play & Sass
    31: ("OH SHIT", "Playful floral burst with exploding daisies and stars, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    32: ("NOPE", "Sassy floral X-frame with bold roses and crossed stems, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    33: ("OUCH", "Spiky floral starburst with thistles and radiating thorns, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    34: ("UGHH", "Dramatic floral explosion with tangled roses and chaos vines, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    35: ("WTF", "Confused floral tangle with twisted vines and question-mark leaves, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    36: ("OMG", "Excited floral burst with sunflowers and exclamation petals, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    37: ("LOL", "Joyful floral spiral with daisies and dancing butterflies, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    38: ("UGH", "Frustrated floral knot with tangled roses and thorny stems, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    39: ("SO DONE", "Weary floral wilt with drooping tulips and bowed stems, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    40: ("SERIOUSLY", "Skeptical floral frame with raised-eyebrow roses and questioning buds, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),

    # Category 5: Self-Love & Motivation
    41: ("LOVE YOURSELF", "Heart-shaped floral wreath with roses and thorns transformed to flowers, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    42: ("YOU GOT THIS", "Empowering floral banner frame with sunflowers and upward-reaching vines, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    43: ("BE KIND", "Gentle floral embrace with soft peonies and curved vine arms, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    44: ("STAY GOLD", "Radiant floral sun with golden-style sunflowers and ray petals, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    45: ("SHINE ON", "Luminous floral star with lilies and radiating light beams, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    46: ("BE BRAVE", "Courageous floral shield with thistles and protective leaf border, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    47: ("RISE UP", "Ascending floral spiral with morning glories climbing upward, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    48: ("F*CK IT", "Liberated floral explosion with wildflowers breaking free from chains of vines, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    49: ("OWN IT", "Confident floral crown with bold roses and standing-tall stems, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
    50: ("FREE SPIRIT", "Free-flowing floral design with dandelion seeds and floating poppies, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, centered composition, white background, print-ready quality"),
}

COVER_PROMPT = "Stunning floral mandala frame for a coloring book cover, elaborate roses, peonies and ornamental scrollwork forming an elegant decorative border with empty center space, decorative corner flourishes, thick bold outlines, black and white line art, no shading, no fill, no text, no letters, no words, clean detailed drawing, white background, print-ready quality"
COVER_WORD = "F*CKING\nGORGEOUS"

def generate_design(num, word, art_prompt, delay=3):
    """Generate one design: Leonardo art + Pillow text overlay."""
    outpath = f"images/design_{num:02d}.png"
    # FORCE regeneration - delete old file if exists
    if os.path.exists(outpath):
        os.remove(outpath)
    
    print(f"  [{num:02d}] Generating '{word}'...")
    
    img = generate_with_leonardo(art_prompt, width=1024, height=1536)
    
    if img is None:
        print(f"  [{num:02d}] FAILED!")
        return False
    
    img = process_to_lineart(img)
    img = resize_for_kdp(img)
    img = add_text_overlay(img, word)
    img.save(outpath, "PNG", dpi=(300, 300))
    print(f"  [{num:02d}] Saved {outpath} ({img.size[0]}x{img.size[1]})")
    return True

def generate_cover():
    """Generate cover design."""
    outpath = "images/cover-front.png"
    if os.path.exists(outpath):
        os.remove(outpath)
    
    print(f"  [COVER] Generating cover art...")
    img = generate_with_leonardo(COVER_PROMPT, width=1024, height=1536)
    if img is None:
        print("  [COVER] FAILED!")
        return False
    
    img = process_to_lineart(img)
    img = resize_for_kdp(img)
    # Add title text
    img = add_text_overlay(img, "F*CKING\nGORGEOUS", font_size_ratio=0.10)
    img.save(outpath, "PNG", dpi=(300, 300))
    print(f"  [COVER] Saved {outpath}")
    return True

def main():
    if not LEONARDO_API_KEY:
        print("ERROR: Set LEONARDO_API_KEY env var")
        print("  export LEONARDO_API_KEY=your-key-here")
        sys.exit(1)
    
    os.makedirs("images", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    # Test connection first
    print("\n=== Testing Leonardo.ai Connection ===")
    test_img = generate_with_leonardo("test: simple black and white flower outline", width=512, height=768)
    if test_img is None:
        print("\nTest FAILED! Check your Leonardo API key and credits.")
        print("Get your key at: https://app.leonardo.ai/app/settings/api")
        sys.exit(1)
    print("  Connection OK!")
    
    # Generate all designs
    designs = sorted(PROMPTS.keys())
    batch_size = 5
    
    for batch_start in range(0, len(designs), batch_size):
        batch = designs[batch_start:batch_start + batch_size]
        print(f"\n=== Batch {batch_start//batch_size + 1}/{(len(designs)-1)//batch_size + 1} ===")
        
        for num in batch:
            word, prompt = PROMPTS[num]
            generate_design(num, word, prompt)
            time.sleep(2)
        
        if batch_start + batch_size < len(designs):
            print(f"  Pausing 5s between batches...")
            time.sleep(5)
    
    # Generate cover
    print("\n=== Generating Cover ===")
    generate_cover()
    
    print("\n=== DONE! ===")
    print(f"  Check images/ directory for results")
    print(f"  Next: python3 scripts/assemble.py")

if __name__ == "__main__":
    main()
