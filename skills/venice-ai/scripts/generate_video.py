#!/usr/bin/env python3
"""
Venice AI Video Generator

Generate videos from images using Venice.ai API.

⚠️ IMPORTANT: Video generation can be expensive! 
This script ALWAYS asks for model selection and shows cost before proceeding.

Usage:
    python generate_video.py input.png "Gentle waves at sunset" --output video.mp4
    python generate_video.py image.png "Camera slowly zooms in" --model wan-2.5-preview-image-to-video

Video Models Reference: https://docs.venice.ai/models/video
"""

import os
import sys
import argparse
import time
import base64
import requests
from typing import Optional, List

API_BASE = "https://api.venice.ai/api/v1"

# Common video models - check https://docs.venice.ai/models/video for current list
AVAILABLE_MODELS = {
    "1": ("wan-2.5-preview-image-to-video", "Image to Video (Recommended for most use cases)"),
    "2": ("wan-2.5-preview-text-to-video", "Text to Video"),
}


def get_video_quote(
    model: str,
    duration: str,
    resolution: str = "720p",
    aspect_ratio: Optional[str] = None,
    audio: bool = True,
    api_key: Optional[str] = None
) -> float:
    """Get price quote for video generation."""
    
    api_key = api_key or os.environ.get("VENICE_API_KEY")
    if not api_key:
        raise ValueError("VENICE_API_KEY environment variable not set")
    
    payload = {
        "model": model,
        "duration": duration,
        "resolution": resolution,
        "audio": audio
    }
    if aspect_ratio:
        payload["aspect_ratio"] = aspect_ratio
    
    response = requests.post(
        f"{API_BASE}/video/quote",
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload
    )
    
    response.raise_for_status()
    return response.json()["quote"]


def queue_video(
    image_path: str,
    prompt: str,
    duration: str = "5s",
    resolution: str = "720p",
    aspect_ratio: Optional[str] = None,
    negative_prompt: str = "",
    audio: bool = True,
    model: str = "wan-2.5-preview-image-to-video",
    reference_images: Optional[List[str]] = None,
    api_key: Optional[str] = None
) -> str:
    """Queue a video generation request. Returns queue_id."""
    
    api_key = api_key or os.environ.get("VENICE_API_KEY")
    if not api_key:
        raise ValueError("VENICE_API_KEY environment variable not set")
    
    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    payload = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "image_url": f"data:image/png;base64,{image_data}",
        "audio": audio
    }
    
    if aspect_ratio:
        payload["aspect_ratio"] = aspect_ratio
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt
    if reference_images:
        ref_encoded = []
        for ref_path in reference_images:
            with open(ref_path, "rb") as f:
                ref_data = base64.b64encode(f.read()).decode("utf-8")
            ref_encoded.append(f"data:image/png;base64,{ref_data}")
        payload["reference_image_urls"] = ref_encoded
    
    response = requests.post(
        f"{API_BASE}/video/queue",
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload
    )
    
    response.raise_for_status()
    return response.json()["queue_id"]


def retrieve_video(
    model: str,
    queue_id: str,
    output: str = "generated_video.mp4",
    poll_interval: int = 5,
    delete_on_completion: bool = False,
    api_key: Optional[str] = None
) -> str:
    """Poll for video completion and download when ready."""
    
    api_key = api_key or os.environ.get("VENICE_API_KEY")
    if not api_key:
        raise ValueError("VENICE_API_KEY environment variable not set")
    
    print(f"Polling for video completion (queue_id: {queue_id})...")
    
    while True:
        response = requests.post(
            f"{API_BASE}/video/retrieve",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "queue_id": queue_id,
                "delete_media_on_completion": delete_on_completion
            }
        )
        
        response.raise_for_status()
        
        content_type = response.headers.get("content-type", "")
        
        if "video/mp4" in content_type:
            # Video is ready
            with open(output, "wb") as f:
                f.write(response.content)
            print(f"\nVideo saved: {output}")
            return output
        else:
            # Still processing
            data = response.json()
            status = data.get("status", "UNKNOWN")
            
            if status == "PROCESSING":
                exec_time = data.get("execution_duration", 0)
                avg_time = data.get("average_execution_time", 0)
                print(f"Processing... {exec_time/1000:.1f}s / {avg_time/1000:.1f}s estimated", end="\r")
                time.sleep(poll_interval)
            else:
                print(f"\nUnexpected status: {status}")
                raise RuntimeError(f"Unexpected status: {status}")


def select_model():
    """Interactive model selection."""
    print("\n" + "=" * 60)
    print("VIDEO MODEL SELECTION")
    print("=" * 60)
    print("\nAvailable video models:")
    print("(Check https://docs.venice.ai/models/video for latest models)")
    print()
    
    for key, (model_id, description) in AVAILABLE_MODELS.items():
        print(f"  {key}. {model_id}")
        print(f"     {description}")
        print()
    
    print("  Or enter any model ID manually")
    print()
    
    choice = input("Select model (number or ID) [1]: ").strip()
    
    if not choice:
        choice = "1"
    
    if choice in AVAILABLE_MODELS:
        return AVAILABLE_MODELS[choice][0]
    else:
        return choice


def confirm_generation(price: float, config: dict) -> bool:
    """Show cost and get user confirmation."""
    print("\n" + "=" * 60)
    print("VIDEO GENERATION COST CONFIRMATION")
    print("=" * 60)
    print(f"\n💰 Estimated Cost: ${price:.4f} USD")
    print(f"\nConfiguration:")
    print(f"  Model: {config['model']}")
    print(f"  Duration: {config['duration']}")
    print(f"  Resolution: {config['resolution']}")
    print(f"  Aspect Ratio: {config['aspect_ratio']}")
    print(f"  Audio: {'Yes' if config['audio'] else 'No'}")
    print("=" * 60)
    print("\n⚠️  Video generation will be charged to your account.")
    
    while True:
        confirm = input("\nDo you want to proceed? (yes/no): ").strip().lower()
        if confirm in ["yes", "y"]:
            return True
        elif confirm in ["no", "n"]:
            return False
        else:
            print("Please enter 'yes' or 'no'")


def main():
    parser = argparse.ArgumentParser(
        description="Generate videos using Venice.ai (requires cost confirmation)",
        epilog="""
Examples:
  python generate_video.py input.png "Gentle waves at sunset"
  python generate_video.py image.png "Camera zooms in slowly" --duration 10s
  python generate_video.py photo.png "Subtle motion" --model wan-2.5-preview-image-to-video
        """
    )
    parser.add_argument("image", help="Input image path")
    parser.add_argument("prompt", help="Video description/motion prompt")
    parser.add_argument("--output", "-o", default="generated_video.mp4", help="Output filename")
    parser.add_argument("--duration", default="5s", choices=["5s", "10s"], help="Video duration")
    parser.add_argument("--resolution", default="720p", choices=["480p", "720p", "1080p"],
                        help="Video resolution")
    parser.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio (default: 16:9)")
    parser.add_argument("--negative-prompt", default="", help="What to avoid")
    parser.add_argument("--no-audio", action="store_true", help="Disable audio generation")
    parser.add_argument("--model", help="Video generation model (if not provided, you'll be asked)")
    parser.add_argument("--reference-images", nargs="+", help="Reference images for consistency")
    parser.add_argument("--poll-interval", type=int, default=5,
                        help="Seconds between status checks")
    parser.add_argument("--delete-on-completion", action="store_true",
                        help="Delete from Venice servers after download")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Skip confirmation prompt (use with caution!)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Get model selection
        if args.model:
            model = args.model
            print(f"Using model: {model}")
        else:
            model = select_model()
            print(f"Selected model: {model}")
        
        # Get configuration
        config = {
            "model": model,
            "duration": args.duration,
            "resolution": args.resolution,
            "aspect_ratio": args.aspect_ratio,
            "audio": not args.no_audio
        }
        
        # Get price quote
        print("\nGetting price quote...")
        price = get_video_quote(
            model=config["model"],
            duration=config["duration"],
            resolution=config["resolution"],
            aspect_ratio=config["aspect_ratio"],
            audio=config["audio"]
        )
        config["price"] = price
        
        # Show cost and get confirmation
        if not args.yes:
            if not confirm_generation(price, config):
                print("\nVideo generation cancelled.")
                sys.exit(0)
        else:
            print(f"\n⚠️  Auto-confirming: ${price:.4f} USD")
        
        # Queue video generation
        print("\nQueueing video generation...")
        queue_id = queue_video(
            image_path=args.image,
            prompt=args.prompt,
            duration=config["duration"],
            resolution=config["resolution"],
            aspect_ratio=config["aspect_ratio"],
            negative_prompt=args.negative_prompt,
            audio=config["audio"],
            model=config["model"],
            reference_images=args.reference_images
        )
        
        print(f"Video queued (queue_id: {queue_id})")
        
        # Retrieve video
        output_file = retrieve_video(
            model=config["model"],
            queue_id=queue_id,
            output=args.output,
            poll_interval=args.poll_interval,
            delete_on_completion=args.delete_on_completion
        )
        
        print(f"\n✅ Successfully generated video: {output_file}")
        print(f"💰 Total cost: ${config['price']:.4f} USD")
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
