#!/usr/bin/env python3
"""
Venice AI Background Remover

Remove backgrounds from images using Venice.ai API.

Usage:
    python remove_background.py input.png --output no_bg.png
    python remove_background.py product.jpg --output product_clean.png
"""

import os
import sys
import argparse
import requests
from typing import Optional

API_BASE = "https://api.venice.ai/api/v1"


def remove_background(
    image_path: str,
    output: str = "no_background.png",
    api_key: Optional[str] = None
):
    """Remove background from an image using Venice.ai API."""
    
    api_key = api_key or os.environ.get("VENICE_API_KEY")
    if not api_key:
        raise ValueError("VENICE_API_KEY environment variable not set")
    
    with open(image_path, "rb") as f:
        files = {"image": f}
        
        response = requests.post(
            f"{API_BASE}/image/remove-background",
            headers={"Authorization": f"Bearer {api_key}"},
            files=files
        )
    
    response.raise_for_status()
    
    # Save image with transparent background
    with open(output, "wb") as f:
        f.write(response.content)
    
    return output


def main():
    parser = argparse.ArgumentParser(description="Remove backgrounds using Venice.ai")
    parser.add_argument("image", help="Input image path")
    parser.add_argument("--output", "-o", default="no_background.png", help="Output filename")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}", file=sys.stderr)
        sys.exit(1)
    
    try:
        output_file = remove_background(
            image_path=args.image,
            output=args.output
        )
        print(f"Saved image without background: {output_file}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
