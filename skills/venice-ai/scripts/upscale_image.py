#!/usr/bin/env python3
"""
Venice AI Image Upscaler

Upscale and enhance images using Venice.ai API.

Usage:
    python upscale_image.py input.png --scale 2 --output upscaled.png
    python upscale_image.py photo.jpg --scale 4 --enhance --enhance-prompt "professional photo"
"""

import os
import sys
import argparse
import requests
from typing import Optional

API_BASE = "https://api.venice.ai/api/v1"


def upscale_image(
    image_path: str,
    output: str = "upscaled_image.png",
    scale: int = 2,
    enhance: bool = False,
    enhance_creativity: float = 0.5,
    enhance_prompt: str = "",
    replication: float = 0.35,
    api_key: Optional[str] = None
):
    """Upscale/enhance an image using Venice.ai API."""
    
    api_key = api_key or os.environ.get("VENICE_API_KEY")
    if not api_key:
        raise ValueError("VENICE_API_KEY environment variable not set")
    
    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {
            "scale": scale,
            "enhance": str(enhance).lower(),
            "replication": replication
        }
        
        if enhance:
            data["enhanceCreativity"] = enhance_creativity
            if enhance_prompt:
                data["enhancePrompt"] = enhance_prompt
        
        response = requests.post(
            f"{API_BASE}/image/upscale",
            headers={"Authorization": f"Bearer {api_key}"},
            files=files,
            data=data
        )
    
    response.raise_for_status()
    
    # Save upscaled image
    with open(output, "wb") as f:
        f.write(response.content)
    
    return output


def main():
    parser = argparse.ArgumentParser(description="Upscale images using Venice.ai")
    parser.add_argument("image", help="Input image path")
    parser.add_argument("--output", "-o", default="upscaled_image.png", help="Output filename")
    parser.add_argument("--scale", type=int, default=2, choices=[1, 2, 3, 4],
                        help="Scale factor (1-4). Use 1 with --enhance for enhancement only")
    parser.add_argument("--enhance", action="store_true",
                        help="Apply AI enhancement (required if scale=1)")
    parser.add_argument("--enhance-creativity", type=float, default=0.5,
                        help="Enhancement creativity (0-1, higher = more changes)")
    parser.add_argument("--enhance-prompt", default="",
                        help="Enhancement style prompt (e.g., 'crisp details', 'gold')")
    parser.add_argument("--replication", type=float, default=0.35,
                        help="Replication strength (0-1, higher = preserve more original)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}", file=sys.stderr)
        sys.exit(1)
    
    if args.scale == 1 and not args.enhance:
        print("Error: --enhance is required when scale=1", file=sys.stderr)
        sys.exit(1)
    
    try:
        output_file = upscale_image(
            image_path=args.image,
            output=args.output,
            scale=args.scale,
            enhance=args.enhance,
            enhance_creativity=args.enhance_creativity,
            enhance_prompt=args.enhance_prompt,
            replication=args.replication
        )
        print(f"Saved upscaled image: {output_file}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
