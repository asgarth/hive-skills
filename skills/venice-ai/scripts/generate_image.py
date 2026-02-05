#!/usr/bin/env python3
"""
Venice AI Image Generator

Generate images from text prompts using Venice.ai API.

Uses cost-effective defaults:
- Model: z-image-turbo (fast and inexpensive)
- Aspect Ratio: 16:9 (widescreen format)

For premium quality, use: --model nano-banana-pro

Usage:
    python generate_image.py "A serene landscape at sunset"
    python generate_image.py "Product photo of headphones" --model nano-banana-pro --resolution 2K
    python generate_image.py "Portrait photo" --aspect-ratio 9:16
"""

import os
import sys
import argparse
import base64
import requests
from typing import Optional, List

API_BASE = "https://api.venice.ai/api/v1"


def generate_image(
    prompt: str,
    model: str = "z-image-turbo",
    output: str = "generated_image.png",
    width: int = 1024,
    height: int = 576,
    aspect_ratio: Optional[str] = "16:9",
    resolution: Optional[str] = None,
    negative_prompt: str = "",
    cfg_scale: float = 7.5,
    seed: Optional[int] = None,
    format: str = "png",
    variants: int = 1,
    api_key: Optional[str] = None
):
    """Generate an image using Venice.ai API."""
    
    api_key = api_key or os.environ.get("VENICE_API_KEY")
    if not api_key:
        raise ValueError("VENICE_API_KEY environment variable not set")
    
    payload = {
        "model": model,
        "prompt": prompt,
        "width": width,
        "height": height,
        "negative_prompt": negative_prompt,
        "cfg_scale": cfg_scale,
        "format": format,
        "variants": variants,
        "safe_mode": False
    }
    
    if aspect_ratio:
        payload["aspect_ratio"] = aspect_ratio
    if resolution:
        payload["resolution"] = resolution
    if seed is not None:
        payload["seed"] = seed
    
    response = requests.post(
        f"{API_BASE}/image/generate",
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload
    )
    
    response.raise_for_status()
    data = response.json()
    
    # Save images
    saved_files = []
    for i, img_data in enumerate(data["images"]):
        filename = output if len(data["images"]) == 1 else f"{output.rsplit('.', 1)[0]}_{i+1}.{output.rsplit('.', 1)[1]}"
        with open(filename, "wb") as f:
            f.write(base64.b64decode(img_data))
        saved_files.append(filename)
        print(f"Saved: {filename}")
    
    return saved_files


def main():
    parser = argparse.ArgumentParser(description="Generate images using Venice.ai (cost-effective defaults)")
    parser.add_argument("prompt", help="Image description/prompt")
    parser.add_argument("--model", default="z-image-turbo",
                        help="Model to use (default: z-image-turbo for fast, cost-efficient generation. Use nano-banana-pro for premium quality)")
    parser.add_argument("--output", "-o", default="generated_image.png", help="Output filename")
    parser.add_argument("--width", type=int, default=1024, help="Image width")
    parser.add_argument("--height", type=int, default=576, help="Image height (default 576 for 16:9)")
    parser.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio (default: 16:9)")
    parser.add_argument("--resolution", help="Resolution (e.g., 1K, 2K, 4K) - premium models only")
    parser.add_argument("--negative-prompt", default="", help="What to avoid")
    parser.add_argument("--cfg-scale", type=float, default=7.5, help="CFG scale (0-20)")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--format", default="png", choices=["png", "jpeg", "webp"], help="Output format")
    parser.add_argument("--variants", type=int, default=1, help="Number of variants (1-4)")
    
    args = parser.parse_args()
    
    try:
        files = generate_image(
            prompt=args.prompt,
            model=args.model,
            output=args.output,
            width=args.width,
            height=args.height,
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution,
            negative_prompt=args.negative_prompt,
            cfg_scale=args.cfg_scale,
            seed=args.seed,
            format=args.format,
            variants=args.variants
        )
        print(f"\nSuccessfully generated {len(files)} image(s)")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
