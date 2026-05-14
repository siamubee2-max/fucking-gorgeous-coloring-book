#!/usr/bin/env python3
"""
F*cking Gorgeous - Image Generation Core
Priority: Higgsfield API > DALL-E 3
"""
import os, time, requests
from pathlib import Path
from PIL import Image
from io import BytesIO

OUTPUT_DIR = Path("./images")
OUTPUT_DIR.mkdir(exist_ok=True)


def process_to_lineart(img):
    """Convert image to clean black & white line art."""
    from PIL import ImageOps
    gray = img.convert("L")
    gray = ImageOps.autocontrast(gray, cutoff=10)
    threshold = 128
    bw = gray.point(lambda x: 255 if x > threshold else 0, "1")
    return bw.convert("RGB")


# ===== BACKEND 1: HIGGSFIELD API =====
def generate_higgsfield(prompt, filename):
    """Generate image using Higgsfield API."""
    api_key = os.environ.get("HIGGSFIELD_API_KEY", "")
    if not api_key:
        raise ValueError("HIGGSFIELD_API_KEY not set")
    
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # Censor for moderation
    safe = prompt
    for word, sw in [("FUCK","F*CK"),("fuck","f*ck"),("Fuck","F*ck"),
                     ("SHIT","SH*T"),("shit","sh*t"),("BITCH","B*TCH"),
                     ("bitch","b*tch"),("BULLSHIT","BULLSH*T"),("bullshit","bullsh*t"),
                     ("DAMN","D*MN"),("damn","d*mn"),("BASTARD","B*STARD"),
                     ("bastard","b*stard"),("DOUCHE","D*UCHE"),("douche","d*uche"),
                     ("ASS","A**"),("ass","a**")]:
        safe = safe.replace(word, sw)
    
    data = {"prompt": safe, "aspect_ratio": "9:16", "resolution": "1080p"}
    
    print(f"  Submitting to Higgsfield...")
    resp = requests.post("https://platform.higgsfield.ai/higgsfield-ai/soul/standard",
                          headers=headers, json=data, timeout=30)
    
    if resp.status_code not in (200, 201, 202):
        raise Exception(f"Higgsfield error: {resp.status_code} {resp.text[:200]}")
    
    result = resp.json()
    request_id = result.get("request_id")
    status_url = result.get("status_url", f"https://platform.higgsfield.ai/requests/{request_id}/status")
    
    print(f"  Request: {request_id}")
    for attempt in range(60):
        time.sleep(5)
        sr = requests.get(status_url, headers=headers, timeout=30)
        sd = sr.json()
        status = sd.get("status", "unknown")
        print(f"  Status: {status} ({attempt*5}s)")
        
        if status == "completed":
            images = sd.get("images", [])
            if images:
                ir = requests.get(images[0]["url"], timeout=60)
                ir.raise_for_status()
                img = Image.open(BytesIO(ir.content))
                img = img.resize((2550, 3300), Image.LANCZOS)
                img = process_to_lineart(img)
                out = OUTPUT_DIR / f"{filename}.png"
                img.save(str(out), "PNG", dpi=(300, 300))
                print(f"  Saved: {out}")
                return out
            raise Exception("No images in response")
        elif status in ("failed", "nsfw"):
            raise Exception(f"Generation {status}: {sd}")
        elif status in ("queued", "in_progress"):
            continue
    
    raise Exception("Timeout after 5 minutes")


# ===== BACKEND 2: DALL-E 3 =====
def generate_openai(prompt, filename):
    """Generate image using DALL-E 3."""
    from openai import OpenAI
    client = OpenAI()
    print(f"  Generating with DALL-E 3...")
    response = client.images.generate(model="dall-e-3", prompt=prompt,
                                       size="1024x1792", quality="hd", n=1)
    url = response.data[0].url
    ir = requests.get(url, timeout=60)
    ir.raise_for_status()
    img = Image.open(BytesIO(ir.content))
    img = img.resize((2550, 3300), Image.LANCZOS)
    img = process_to_lineart(img)
    out = OUTPUT_DIR / f"{filename}.png"
    img.save(str(out), "PNG", dpi=(300, 300))
    print(f"  Saved: {out}")
    return out


# ===== AUTO-DETECT =====
def generate(prompt, filename):
    """Auto-detect and use the best available backend."""
    if os.environ.get("HIGGSFIELD_API_KEY"):
        print(f"  Backend: Higgsfield")
        return generate_higgsfield(prompt, filename)
    elif os.environ.get("OPENAI_API_KEY"):
        print(f"  Backend: DALL-E 3")
        return generate_openai(prompt, filename)
    else:
        raise ValueError("Set HIGGSFIELD_API_KEY or OPENAI_API_KEY")
