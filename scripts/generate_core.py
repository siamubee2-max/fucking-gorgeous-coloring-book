#!/usr/bin/env python3
"""
F*cking Gorgeous - Image Generation Core
Supports: HuggingFace Inference API, Higgsfield API, DALL-E 3
"""
import os, time, requests
from pathlib import Path
from PIL import Image
from io import BytesIO

OUTPUT_DIR = Path("./images")
OUTPUT_DIR.mkdir(exist_ok=True)

# ===== BACKEND 1: HuggingFace Inference API =====
def generate_hf(prompt, filename):
    """Generate image using HuggingFace Inference API (FLUX Schnell - FREE)."""
    api_key = os.environ.get("HF_API_KEY", "")
    if not api_key:
        raise ValueError("HF_API_KEY not set")
    
    # FLUX Schnell - fast & free on HF
    models = [
        "black-forest-labs/FLUX.1-schnell",
        "stabilityai/stable-diffusion-xl-base-1.0",
        "runwayml/stable-diffusion-v1-5",
    ]
    
    # Add coloring book style enhancement to prompt
    enhanced = prompt + " Clean black and white line art coloring page, no colors, no shading, no grayscale, white background, high contrast outlines, 300 DPI print quality."
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    for model in models:
        print(f"  Trying HF model: {model.split('/')[-1]}...")
        try:
            # Try text-to-image API
            resp = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers,
                json={"inputs": enhanced},
                timeout=120,
            )
            
            if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
                img = Image.open(BytesIO(resp.content))
                # Resize to KDP specs: 8.5x11 inches at 300 DPI
                img = img.resize((2550, 3300), Image.LANCZOS)
                img = img.convert("RGB")
                # Convert to true black & white line art
                img = process_to_lineart(img)
                out = OUTPUT_DIR / f"{filename}.png"
                img.save(str(out), "PNG", dpi=(300, 300))
                print(f"  Saved: {out}")
                return out
            elif resp.status_code == 503:
                # Model loading, wait and retry
                print(f"  Model loading, waiting 30s...")
                time.sleep(30)
                resp = requests.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    headers=headers,
                    json={"inputs": enhanced},
                    timeout=120,
                )
                if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
                    img = Image.open(BytesIO(resp.content))
                    img = img.resize((2550, 3300), Image.LANCZOS)
                    img = img.convert("RGB")
                    img = process_to_lineart(img)
                    out = OUTPUT_DIR / f"{filename}.png"
                    img.save(str(out), "PNG", dpi=(300, 300))
                    print(f"  Saved: {out}")
                    return out
                else:
                    print(f"  Failed after retry: {resp.status_code}")
                    continue
            else:
                print(f"  Error {resp.status_code}: {resp.text[:100]}")
                continue
        except Exception as e:
            print(f"  Error with {model}: {e}")
            continue
    
    raise Exception("All HF models failed")


def process_to_lineart(img):
    """Convert a color image to clean black & white line art."""
    from PIL import ImageOps, ImageFilter
    # Convert to grayscale
    gray = img.convert("L")
    # Increase contrast heavily
    gray = ImageOps.autocontrast(gray, cutoff=10)
    # Apply threshold to get clean black/white
    threshold = 128
    bw = gray.point(lambda x: 255 if x > threshold else 0, "1")
    # Convert back to RGB for saving
    result = bw.convert("RGB")
    return result


# ===== BACKEND 2: Higgsfield API =====
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
    for word, safe_word in [("FUCK","F*CK"),("fuck","f*ck"),("Fuck","F*ck"),
                            ("SHIT","SH*T"),("shit","sh*t"),("BITCH","B*TCH"),
                            ("bitch","b*tch"),("BULLSHIT","BULLSH*T"),("bullshit","bullsh*t"),
                            ("DAMN","D*MN"),("damn","d*mn"),("BASTARD","B*STARD"),
                            ("bastard","b*stard"),("DOUCHE","D*UCHE"),("douche","d*uche"),
                            ("ASS","A**"),("ass","a**")]:
        safe = safe.replace(word, safe_word)
    
    data = {"prompt": safe, "aspect_ratio": "9:16", "resolution": "1080p"}
    
    print(f"  Submitting to Higgsfield...")
    resp = requests.post("https://platform.higgsfield.ai/higgsfield-ai/soul/standard",
                          headers=headers, json=data)
    
    if resp.status_code not in (200, 201, 202):
        raise Exception(f"Higgsfield error: {resp.status_code} {resp.text[:200]}")
    
    result = resp.json()
    request_id = result.get("request_id")
    status_url = result.get("status_url", f"https://platform.higgsfield.ai/requests/{request_id}/status")
    
    print(f"  Request: {request_id}")
    for _ in range(60):  # 5 min max
        time.sleep(5)
        sr = requests.get(status_url, headers=headers)
        sd = sr.json()
        status = sd.get("status", "unknown")
        print(f"  Status: {status}")
        
        if status == "completed":
            images = sd.get("images", [])
            if images:
                ir = requests.get(images[0]["url"])
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


# ===== BACKEND 3: DALL-E 3 =====
def generate_openai(prompt, filename):
    """Generate image using DALL-E 3."""
    from openai import OpenAI
    client = OpenAI()
    print(f"  Generating with DALL-E 3...")
    response = client.images.generate(model="dall-e-3", prompt=prompt,
                                       size="1024x1792", quality="hd", n=1)
    url = response.data[0].url
    ir = requests.get(url)
    ir.raise_for_status()
    img = Image.open(BytesIO(ir.content))
    img = img.resize((2550, 3300), Image.LANCZOS)
    img = process_to_lineart(img)
    out = OUTPUT_DIR / f"{filename}.png"
    img.save(str(out), "PNG", dpi=(300, 300))
    print(f"  Saved: {out}")
    return out


# ===== AUTO-DETECT BACKEND =====
def generate(prompt, filename):
    """Auto-detect and use the best available backend."""
    if os.environ.get("HF_API_KEY"):
        print(f"  Backend: HuggingFace")
        return generate_hf(prompt, filename)
    elif os.environ.get("HIGGSFIELD_API_KEY"):
        print(f"  Backend: Higgsfield")
        return generate_higgsfield(prompt, filename)
    elif os.environ.get("OPENAI_API_KEY"):
        print(f"  Backend: DALL-E 3")
        return generate_openai(prompt, filename)
    else:
        raise ValueError("Set HF_API_KEY, HIGGSFIELD_API_KEY, or OPENAI_API_KEY")
