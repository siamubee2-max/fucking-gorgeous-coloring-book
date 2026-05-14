#!/usr/bin/env python3
"""
F*cking Gorgeous - Batch Image Generator
Uses Higgsfield API (primary) or DALL-E 3 (fallback).

USAGE:
  export HIGGSFIELD_API_KEY="key:secret"
  # OR: export OPENAI_API_KEY="sk-..."
  python3 scripts/generate.py --start 1 --end 55
  python3 scripts/generate.py --cover
  python3 scripts/generate.py --start 16 --end 30
"""

import os, sys, time, json, argparse, requests
from pathlib import Path
from PIL import Image
from io import BytesIO

OUTPUT_DIR = Path("./images")
OUTPUT_DIR.mkdir(exist_ok=True)

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
    
    # Censor prompt for Higgsfield moderation
    safe_prompt = prompt
    safe_prompt = safe_prompt.replace("FUCK", "F*CK").replace("fuck", "f*ck").replace("Fuck", "F*ck")
    safe_prompt = safe_prompt.replace("SHIT", "SH*T").replace("shit", "sh*t")
    safe_prompt = safe_prompt.replace("BITCH", "B*TCH").replace("bitch", "b*tch")
    safe_prompt = safe_prompt.replace("BULLSHIT", "BULLSH*T").replace("bullshit", "bullsh*t")
    safe_prompt = safe_prompt.replace("DAMN", "D*MN").replace("damn", "d*mn")
    safe_prompt = safe_prompt.replace("BASTARD", "B*STARD").replace("bastard", "b*stard")
    safe_prompt = safe_prompt.replace("DOUCHE", "D*UCHE").replace("douche", "d*uche")
    safe_prompt = safe_prompt.replace("ASS", "A**").replace("ass", "a**")
    
    data = {
        "prompt": safe_prompt,
        "aspect_ratio": "9:16",
        "resolution": "1080p",
    }
    
    print(f"  Submitting to Higgsfield...")
    resp = requests.post(
        "https://platform.higgsfield.ai/higgsfield-ai/soul/standard",
        headers=headers, json=data
    )
    
    if resp.status_code not in (200, 201, 202):
        raise Exception(f"Higgsfield error: {resp.status_code} {resp.text[:200]}")
    
    result = resp.json()
    request_id = result.get("request_id")
    status_url = result.get("status_url", f"https://platform.higgsfield.ai/requests/{request_id}/status")
    
    print(f"  Request: {request_id}")
    max_wait = 300
    waited = 0
    while waited < max_wait:
        time.sleep(5)
        waited += 5
        sr = requests.get(status_url, headers=headers)
        sd = sr.json()
        status = sd.get("status", "unknown")
        print(f"  Status: {status} ({waited}s)")
        
        if status == "completed":
            images = sd.get("images", [])
            if images:
                url = images[0].get("url")
                ir = requests.get(url)
                ir.raise_for_status()
                img = Image.open(BytesIO(ir.content))
                img = img.resize((2550, 3300), Image.LANCZOS)
                img = img.convert("RGB")
                out = OUTPUT_DIR / f"{filename}.png"
                img.save(str(out), "PNG", dpi=(300, 300))
                print(f"  Saved: {out}")
                return out
            raise Exception("No images in response")
        elif status == "failed":
            raise Exception(f"Generation failed: {sd}")
        elif status == "nsfw":
            raise Exception("NSFW flagged - try different prompt")
        elif status in ("queued", "in_progress"):
            continue
        else:
            raise Exception(f"Unknown status: {status}")
    raise Exception(f"Timeout after {max_wait}s")


def generate_openai(prompt, filename):
    """Generate image using DALL-E 3 (fallback)."""
    from openai import OpenAI
    client = OpenAI()
    print(f"  Generating with DALL-E 3...")
    response = client.images.generate(
        model="dall-e-3", prompt=prompt,
        size="1024x1792", quality="hd", n=1,
    )
    url = response.data[0].url
    ir = requests.get(url)
    ir.raise_for_status()
    img = Image.open(BytesIO(ir.content))
    img = img.resize((2550, 3300), Image.LANCZOS)
    img = img.convert("RGB")
    out = OUTPUT_DIR / f"{filename}.png"
    img.save(str(out), "PNG", dpi=(300, 300))
    print(f"  Saved: {out}")
    return out


def generate(prompt, filename):
    if os.environ.get("HIGGSFIELD_API_KEY"):
        return generate_higgsfield(prompt, filename)
    elif os.environ.get("OPENAI_API_KEY"):
        return generate_openai(prompt, filename)
    else:
        raise ValueError("Set HIGGSFIELD_API_KEY or OPENAI_API_KEY")
