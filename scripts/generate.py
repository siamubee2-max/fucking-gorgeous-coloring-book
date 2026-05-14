#!/usr/bin/env python3
"""
F*cking Gorgeous - Batch Image Generator
Uses OpenAI DALL-E API to generate all 55 coloring pages.

PREREQUISITES:
  pip install openai Pillow
  export OPENAI_API_KEY="sk-..."

USAGE:
  python3 generate.py --start 1 --end 55
  python3 generate.py --cover
"""

import os
import sys
import time
import argparse
from pathlib import Path
from openai import OpenAI
from PIL import Image

client = OpenAI()
OUTPUT_DIR = Path("./images")
OUTPUT_DIR.mkdir(exist_ok=True)

# All 55 prompts (from 02-image-prompts.md)
PROMPTS = {
    1: 'Coloring page: The word "FUCK" in large bold brush script lettering, surrounded by an intricate mandala of roses, thorny vines, and leaves. Clean black line art on white background, no shading, no grayscale. Detailed petal patterns within mandala rings. 2550x3300 pixels portrait.',
    2: 'Coloring page: The word "SHIT" in large bold brush script lettering, surrounded by an intricate mandala of sunflowers, seeds, and leaves. Clean black line art on white background, no shading, no grayscale. 2550x3300 pixels portrait.',
    3: 'Coloring page: The word "DAMN" in large bold brush script lettering, surrounded by an intricate mandala of lavender stems, bees, and small flowers. Clean black line art on white background, no shading. 2550x3300 pixels portrait.',
    4: 'Coloring page: The word "BITCH" in large bold brush script lettering, surrounded by an intricate mandala of roses, daggers, and thorny vines. Clean black line art on white background, no shading. 2550x3300 pixels portrait.',
    5: 'Coloring page: The word "HELL" in large bold brush script lettering, surrounded by an intricate mandala of lilies, flame shapes, and leaves. Clean black line art on white background, no shading. 2550x3300 pixels portrait.',
    6: 'Coloring page: The word "ASS" in large bold brush script lettering, surrounded by an intricate mandala of chrysanthemums and leaves. Clean black line art on white background, no shading. 2550x3300 pixels portrait.',
    7: 'Coloring page: The word "BASTARD" in large bold brush script lettering, surrounded by an intricate mandala of orchids, hanging vines, and leaves. Clean black line art on white background, no shading. 2550x3300 pixels portrait.',
    8: 'Coloring page: The word "CRAP" in large bold brush script lettering, surrounded by an intricate mandala of daisies, butterflies, and leaves. Clean black line art on white background, no shading. 2550x3300 pixels portrait.',
    9: 'Coloring page: The word "DOUCHE" in large bold brush script lettering, surrounded by an intricate mandala of lotus flowers, water ripples, and lily pads. Clean black line art on white background, no shading. 2550x3300 pixels portrait.',
    10: 'Coloring page: The word "WTF" in large bold brush script lettering, surrounded by an intricate mandala of cherry blossoms, branches, and petals. Clean black line art on white background, no shading. 2550x3300 pixels portrait.',
    11: 'Coloring page: The word "OMFG" in large bold brush script lettering, surrounded by an intricate mandala of morning glory vines, flowers, and leaves. Clean black line art on white background, no shading. 2550x3300 pixels portrait.',
    12: 'Coloring page: The phrase "HELL NO" in large bold brush script lettering, surrounded by an intricate mandala of tropical hibiscus, plumeria, and palm leaves. Clean black line art on white background, no shading. 2550x3300 pixels portrait.',
    13: 'Coloring page: The word "GODDAMN" in large bold brush script lettering, surrounded by an intricate mandala of iris flowers, feathers, and flowing ribbons. Clean black line art on white background, no shading. 2550x3300 pixels portrait.',
    14: 'Coloring page: The word "BULLSHIT" in large bold brush script lettering, surrounded by an intricate mandala of peonies, dragonflies, and leaves. Clean black line art on white background, no shading. 2550x3300 pixels portrait.',
    15: 'Coloring page: The phrase "PISS OFF" in large bold brush script lettering, surrounded by an intricate mandala of wildflowers, daisies, and grass. Clean black line art on white background, no shading. 2550x3300 pixels portrait.',
    16: 'Coloring page: The phrase "Fuck off, I\'m coloring" in a mix of bold script and clean sans-serif lettering, surrounded by a eucalyptus botanical wreath. Clean black line art on white background, no shading. 2550x3300 pixels portrait.',
    17: 'Coloring page: The phrase "Not today, Satan" in a mix of bold script and clean sans-serif, surrounded by a gothic rose wreath with thorns. Clean black line art, no shading. 2550x3300 pixels portrait.',
    18: 'Coloring page: The phrase "Sorry, I can\'t. I have plans" in modern script, surrounded by a lavender bunch botanical wreath. Clean black line art, no shading. 2550x3300 pixels portrait.',
    19: 'Coloring page: The phrase "Zero fucks given" in bold script, surrounded by dandelion seeds and dandelion wreath. Clean black line art, no shading. 2550x3300 pixels portrait.',
    20: 'Coloring page: The phrase "I\'m not arguing, I\'m explaining" in modern script and sans-serif, surrounded by ferns and ivy border. Clean black line art, no shading. 2550x3300 pixels portrait.',
    21: 'Coloring page: The phrase "Resting bitch face" in bold script, surrounded by a poppy wreath. Clean black line art, no shading. 2550x3300 pixels portrait.',
    22: 'Coloring page: The phrase "Please leave" in elegant script, surrounded by monstera leaves border. Clean black line art, no shading. 2550x3300 pixels portrait.',
    23: 'Coloring page: The phrase "I need a drink" in bold script, surrounded by hibiscus and cocktail glass elements. Clean black line art, no shading. 2550x3300 pixels portrait.',
    24: 'Coloring page: The phrase "Nope. Not happening." in bold block lettering, surrounded by cactus and succulent wreath. Clean black line art, no shading. 2550x3300 pixels portrait.',
    25: 'Coloring page: The phrase "Boss bitch energy" in bold script, surrounded by roses and crown shapes wreath. Clean black line art, no shading. 2550x3300 pixels portrait.',
    26: 'Coloring page: The phrase "Too glam to give a damn" in elegant script, surrounded by peonies and pearl elements. Clean black line art, no shading. 2550x3300 pixels portrait.',
    27: 'Coloring page: The phrase "I do what I want" in bold script, surrounded by tropical leaf border. Clean black line art, no shading. 2550x3300 pixels portrait.',
    28: 'Coloring page: The phrase "You had one job" in sans-serif and script, surrounded by olive branches wreath. Clean black line art, no shading. 2550x3300 pixels portrait.',
    29: 'Coloring page: The phrase "Adulting is hard" in casual script, surrounded by coffee cup and flowers border. Clean black line art, no shading. 2550x3300 pixels portrait.',
    30: 'Coloring page: The phrase "That\'s the tea" in modern script, surrounded by tea roses and teacup wreath. Clean black line art, no shading. 2550x3300 pixels portrait.',
    31: 'Coloring page: The quote "Self-care is telling people to fuck off" in modern sans-serif, framed by a rose archway with vines. Clean black line art, no shading. 2550x3300 pixels portrait.',
    32: 'Coloring page: The quote "Color your stress the f*ck away" in flowing script, surrounded by wildflower garland. Clean black line art, no shading. 2550x3300 pixels portrait.',
    33: 'Coloring page: The quote "Inhale calm, exhale bullshit" in elegant script, enclosed in a lotus mandala border. Clean black line art. 2550x3300 pixels portrait.',
    34: 'Coloring page: The quote "Namaste the f*ck away from me" in modern script, surrounded by zen garden with cacti and stones. Clean black line art. 2550x3300 pixels portrait.',
    35: 'Coloring page: The quote "I meditate so I don\'t punch people" in casual script, surrounded by cherry blossom circle. Clean black line art. 2550x3300 pixels portrait.',
    36: 'Coloring page: The quote "Healing looks a lot like saying no" in elegant script, surrounded by dried flower wreath. Clean black line art. 2550x3300 pixels portrait.',
    37: 'Coloring page: The quote "Boundaries are sexy" in bold script, framed by thorned rose border. Clean black line art. 2550x3300 pixels portrait.',
    38: 'Coloring page: The quote "Protect your peace" in flowing script with smaller "(and tell them to f*ck off)" enclosed in peace lily mandala. Clean black line art. 2550x3300 pixels portrait.',
    39: 'Coloring page: The quote "Glow up or f*ck off" in bold script, surrounded by sunflower burst. Clean black line art. 2550x3300 pixels portrait.',
    40: 'Coloring page: The quote "Self-love means no bullshit" in elegant script, enclosed in dahlia circle. Clean black line art. 2550x3300 pixels portrait.',
    41: 'Coloring page: The quote "You\'re a badass, now color" in bold mixed lettering, surrounded by tiger lilies and stars frame. Clean black line art. 2550x3300 pixels portrait.',
    42: 'Coloring page: The quote "Keep f*cking going" in bold script, surrounded by morning glory spiral. Clean black line art. 2550x3300 pixels portrait.',
    43: 'Coloring page: The quote "Strong as f*ck" in bold block lettering, surrounded by protea and shield leaf patterns. Clean black line art. 2550x3300 pixels portrait.',
    44: 'Coloring page: The quote "She believed she could, so she f*cking did" in elegant flowing script, surrounded by bougainvillea. Clean black line art. 2550x3300 pixels portrait.',
    45: 'Coloring page: The quote "Dream big, work hard, give zero f*cks" in bold script, surrounded by sunflowers and stars. Clean black line art. 2550x3300 pixels portrait.',
    46: 'Coloring page: The word "UNFUCKWITHABLE" in bold geometric lettering, surrounded by intricate orchid mandala. Clean black line art. 2550x3300 pixels portrait.',
    47: 'Coloring page: The quote "Make it happen, bitches" in bold script, surrounded by peony pattern. Clean black line art. 2550x3300 pixels portrait.',
    48: 'Coloring page: The quote "Warrior, not worrier" in bold script, surrounded by lavender and swords. Clean black line art. 2550x3300 pixels portrait.',
    49: 'Coloring page: The quote "You got this, you gorgeous f*cker" in bold script, surrounded by rose crown wreath. Clean black line art. 2550x3300 pixels portrait.',
    50: 'Coloring page: The quote "F*cking sparkle" in bold script, surrounded by diamond and flower shapes. Clean black line art. 2550x3300 pixels portrait.',
    51: 'Coloring page: Full-page artistic quote "Color your stress the f*ck away" in large decorative script, surrounded by mixed wildflowers, roses, sunflowers radiating outward. Clean black line art. 2550x3300 pixels portrait.',
    52: 'Coloring page: Full-page quote "Life is short. Color more. Swear more." in clean sans-serif, surrounded by minimalist botanical line art. Clean black line art. 2550x3300 pixels portrait.',
    53: 'Coloring page: Full-page quote "Behind every successful woman is a whole lot of f*cks given" in elegant script, enclosed in wreath mandala with roses and ribbons. Clean black line art. 2550x3300 pixels portrait.',
    54: 'Coloring page: Full-page quote "Art is how we decorate our freedom" with smaller "(and tell stress to f*ck off)" in art nouveau style, framed by ornate floral border. Clean black line art. 2550x3300 pixels portrait.',
    55: 'Coloring page: Full-page quote "F*ck perfect. Color outside the lines." in bold rebellious lettering, surrounded by wild organic floral chaos. Clean black line art. 2550x3300 pixels portrait.',
}

COVER_PROMPT = 'Professional coloring book cover design: The words "FUCKING GORGEOUS" in large bold ornate script lettering, each letter formed from intertwined roses, lilies, and foliage. Surrounding floral mandala border extending to edges. Subtitle "A Swear Word & Floral Coloring Book for Stressed-Out Adults" below. Clean black line art on white background. Coloring book cover style. 2550x3300 pixels portrait.'

def generate_image(prompt, filename, size="1024x1024"):
    """Generate a single image using DALL-E 3."""
    print(f"Generating: {filename}")
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="hd",
        n=1,
    )
    image_url = response.data[0].url
    
    # Download image
    import requests
    img_response = requests.get(image_url)
    img_response.raise_for_status()
    
    # Save and resize to KDP specs
    from PIL import Image
    from io import BytesIO
    img = Image.open(BytesIO(img_response.content))
    img = img.resize((2550, 3300), Image.LANCZOS)
    img = img.convert("RGB")
    
    output_path = OUTPUT_DIR / f"{filename}.png"
    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"  Saved: {output_path}")
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Generate coloring book images")
    parser.add_argument("--start", type=int, default=1, help="Start design number")
    parser.add_argument("--end", type=int, default=55, help="End design number")
    parser.add_argument("--cover", action="store_true", help="Generate cover image")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between API calls (seconds)")
    args = parser.parse_args()
    
    if args.cover:
        generate_image(COVER_PROMPT, "cover-front")
        return
    
    for i in range(args.start, args.end + 1):
        if i not in PROMPTS:
            print(f"  Skipping {i}: no prompt defined")
            continue
        try:
            generate_image(PROMPTS[i], f"design_{i:02d}")
        except Exception as e:
            print(f"  Error on design {i}: {e}")
            print(f"  Retrying in 10 seconds...")
            time.sleep(10)
            try:
                generate_image(PROMPTS[i], f"design_{i:02d}")
            except Exception as e2:
                print(f"  Failed again on design {i}: {e2}")
        time.sleep(args.delay)
    
    print(f"\nDone! Generated {args.end - args.start + 1} designs.")

if __name__ == "__main__":
    main()
