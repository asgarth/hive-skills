#!/usr/bin/env python3
"""
Venice AI Image Editor

Edit images using AI inpainting.

Usage:
    python edit_image.py input.png "Change the sky to sunset" --output edited.png
    python edit_image.py photo.jpg "Remove the person in the background" --model qwen-edit
"""

import os
import sys
import argparse
import requests
from typing import Optional

API_BASE = "https://api.venice.ai/api/v1"


def edit_image(
    image_path: str,
    prompt: str,
    output: str = "edited_image.png",
    model: str = "qwen-edit",
    aspect_ratio: Optional[str] = None,
    api_key: Optional[str] = None
):
    """Edit an image using Venice.ai API."""
    
    api_key = api_key or os.environ.get("VENICE_API_KEY")
    if not api_key:
        raise ValueError("VENICE_API_KEY environment variable not set")
    
    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {
            "prompt": prompt,
            "modelId": model
        }
        if aspect_ratio:
            data["aspect_ratio"] = aspect_ratio
        
        response = requests.post(
            f"{API_BASE}/image/edit",
            headers={"Authorization": f"Bearer {api_key}"},
            files=files,
            data=data
        )
    
    response.raise_for_status()
    
    # Save edited image
    with open(output, "wb") as f:
        f.write(response.content)
    
    return output


def main():
    parser = argparse.ArgumentParser(description="Edit images using Venice.ai")
    parser.add_argument("image", help="Input image path")
    parser.add_argument("prompt", help="Edit instructions (e.g., 'change sky to sunset')")
    parser.add_argument("--output", "-o", default="edited_image.png", help="Output filename")
    parser.add_argument("--model", default="qwen-edit", 
                        choices=["qwen-edit", "flux-2-max-edit", "nano-banana-pro-edit", 
                                "seedream-v4-edit", "grok-imagine-edit", "gpt-image-1-5-edit"],
                        help="Edit model to use")
    parser.add_argument("--aspect-ratio", help="Output aspect ratio (e.g., 16:9)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}", file=sys.stderr)
        sys.exit(1)
    
    try:
        output_file = edit_image(
            image_path=args.image,
            prompt=args.prompt,
            output=args.output,
            model=args.model,
            aspect_ratio=args.aspect_ratio
        )
        print(f"Saved edited image: {output_file}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
