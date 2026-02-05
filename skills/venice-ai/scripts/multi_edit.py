#!/usr/bin/env python3
"""
Venice AI Multi-Editor

Apply multiple edits to an image sequentially.

Usage:
    python multi_edit.py input.png "Change sky to sunset" "Add birds" "Enhance shadows"
    python multi_edit.py photo.jpg "Remove person" "Change background to beach" --save-steps
"""

import os
import sys
import argparse
import requests
from typing import Optional, List

API_BASE = "https://api.venice.ai/api/v1"


def apply_edit(
    image_path: str,
    prompt: str,
    model: str = "qwen-edit",
    aspect_ratio: Optional[str] = None,
    api_key: Optional[str] = None
) -> bytes:
    """Apply a single edit to an image. Returns image bytes."""
    
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
    return response.content


def multi_edit(
    image_path: str,
    edits: List[str],
    output: str = "final_edit.png",
    model: str = "qwen-edit",
    save_steps: bool = False,
    aspect_ratio: Optional[str] = None,
    api_key: Optional[str] = None
) -> str:
    """Apply multiple edits sequentially to an image."""
    
    current_path = image_path
    step_files = []
    
    for i, edit_prompt in enumerate(edits):
        step_num = i + 1
        print(f"[{step_num}/{len(edits)}] Applying: {edit_prompt}")
        
        # Apply edit
        image_bytes = apply_edit(
            image_path=current_path,
            prompt=edit_prompt,
            model=model,
            aspect_ratio=aspect_ratio,
            api_key=api_key
        )
        
        # Determine output path for this step
        if save_steps:
            base_name = os.path.splitext(output)[0]
            step_path = f"{base_name}_step{step_num}.png"
            step_files.append(step_path)
        else:
            step_path = f".temp_step_{step_num}.png"
        
        # Save result
        with open(step_path, "wb") as f:
            f.write(image_bytes)
        
        # Update current path for next iteration
        if not save_steps and step_num > 1:
            # Clean up previous temp file
            try:
                os.remove(current_path)
            except:
                pass
        
        current_path = step_path
        print(f"  -> Saved: {step_path}")
    
    # Rename final result to output name
    if current_path != output:
        os.rename(current_path, output)
        print(f"\nFinal result: {output}")
    
    # Clean up temp files if not saving steps
    if not save_steps:
        for step_file in step_files:
            try:
                if os.path.exists(step_file):
                    os.remove(step_file)
            except:
                pass
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Apply multiple edits to an image sequentially",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python multi_edit.py photo.png "Change sky to sunset"
  python multi_edit.py input.png "Remove background person" "Change to beach scene" "Add sunset"
  python multi_edit.py product.png "Change color to red" "Add gold accents" --save-steps
        """
    )
    parser.add_argument("image", help="Input image path")
    parser.add_argument("edits", nargs="+", help="Edit prompts to apply in order")
    parser.add_argument("--output", "-o", default="final_edit.png", help="Final output filename")
    parser.add_argument("--model", default="qwen-edit",
                        choices=["qwen-edit", "flux-2-max-edit", "nano-banana-pro-edit",
                                "seedream-v4-edit", "grok-imagine-edit", "gpt-image-1-5-edit"],
                        help="Edit model to use")
    parser.add_argument("--save-steps", action="store_true",
                        help="Save intermediate steps as separate files")
    parser.add_argument("--aspect-ratio", help="Output aspect ratio (e.g., 16:9)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}", file=sys.stderr)
        sys.exit(1)
    
    if not args.edits:
        print("Error: At least one edit prompt is required", file=sys.stderr)
        sys.exit(1)
    
    try:
        print(f"Applying {len(args.edits)} edit(s) to {args.image}\n")
        
        final_file = multi_edit(
            image_path=args.image,
            edits=args.edits,
            output=args.output,
            model=args.model,
            save_steps=args.save_steps,
            aspect_ratio=args.aspect_ratio
        )
        
        print(f"\nSuccessfully applied all edits!")
        print(f"Final output: {final_file}")
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
