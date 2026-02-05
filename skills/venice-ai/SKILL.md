---
name: venice-ai
description: Generate and manipulate images and videos using Venice.ai's privacy-first, uncensored AI API. Use when the user needs to create images from text prompts, edit/inpaint existing images, upscale/enhance image quality, remove backgrounds, or generate videos from text or images. Triggers on requests like "generate an image of...", "upscale this photo", "remove background", "create a video from this image", etc.
---

# Venice AI

Generate and manipulate images and videos using Venice.ai's privacy-first API.

## Overview

Venice.ai provides uncensored, private AI image and video generation with no data retention. The API is OpenAI-compatible with additional Venice-specific features for advanced image editing and video generation.

**Base URL:** `https://api.venice.ai/api/v1`

**Authentication:** Bearer token via `Authorization: Bearer VENICE_API_KEY` header

## Quick Start

```python
import os
import requests

# Generate an image (using cost-effective default model)
response = requests.post(
    "https://api.venice.ai/api/v1/image/generate",
    headers={"Authorization": f"Bearer {os.environ['VENICE_API_KEY']}"},
    json={
        "model": "z-image-turbo",  # Fast, cost-effective default
        "prompt": "A serene canal in Venice at sunset, golden hour lighting",
        "aspect_ratio": "16:9",  # Default aspect ratio
        "width": 1024,
        "height": 576,
        "hide_watermark": True  # No watermark on paid generations
    }
)

# Save the generated image
image_data = response.json()["images"][0]
with open("generated_image.png", "wb") as f:
    f.write(base64.b64decode(image_data))
```

## Core Capabilities

### 1. Image Generation

Generate images from text prompts using various models.

**Endpoint:** `POST /image/generate`

**Cost-Effective Models (Recommended for most use cases):**
- `z-image-turbo` - Fast and inexpensive (default)
- `flux-2-dev` - Good quality, cost-effective
- `fluently-xl` - Budget-friendly for artistic outputs

**Premium Models (Higher quality, higher cost):**
- `nano-banana-pro` - Best photorealism, supports 2K/4K
- `flux-2-max` - High quality, versatile
- `grok-imagine` - Uncensored generation

**Default Model:** `z-image-turbo` (fast and cost-effective)
**Default Aspect Ratio:** `16:9`

Check current pricing: https://docs.venice.ai/models/image

**Key Parameters:**
- `prompt` (required) - Text description (max 7500 chars, model-specific)
- `model` (required) - Model ID
- `width/height` - Output dimensions (max 1280, model-specific divisors apply)
- `negative_prompt` - What to avoid
- `cfg_scale` - 0-20, higher = more prompt adherence
- `seed` - For reproducible results
- `format` - `webp` (default), `png`, `jpeg`
- `variants` - 1-4 images per request
- `resolution` - For supported models: `1K`, `2K`, `4K`
- `aspect_ratio` - e.g., `1:1`, `16:9`, `9:16`
- `style_preset` - Apply predefined styles
- `hide_watermark` - Set to `True` to hide Venice watermark (recommended)

**Example (Cost-Effective - Default):**
```python
response = requests.post(
    "https://api.venice.ai/api/v1/image/generate",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": "z-image-turbo",  # Fast, cost-effective default
        "prompt": "Professional product photography of a sleek wireless headphone",
        "aspect_ratio": "16:9",  # Default widescreen format
        "negative_prompt": "blurry, low quality, distorted",
        "cfg_scale": 7.5,
        "format": "png",
        "hide_watermark": True  # No watermark
    }
)
```

**Example (High Quality - Higher Cost):**
```python
response = requests.post(
    "https://api.venice.ai/api/v1/image/generate",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": "nano-banana-pro",
        "prompt": "Professional product photography of a sleek wireless headphone",
        "aspect_ratio": "1:1",
        "resolution": "2K",
        "negative_prompt": "blurry, low quality, distorted",
        "cfg_scale": 7.5,
        "format": "png",
        "hide_watermark": True  # No watermark
    }
)
```

### 2. Image Editing (Inpainting)

Modify existing images using AI inpainting.

**Endpoint:** `POST /image/edit`

**Models:**
- `qwen-edit` (default) - $0.04/edit
- `flux-2-max-edit`
- `nano-banana-pro-edit`
- `seedream-v4-edit`

**Parameters:**
- `image` (required) - File upload, base64 string, or URL
- `prompt` (required) - Edit instructions (be specific and short)
- `modelId` - Model to use
- `aspect_ratio` - Output aspect ratio

**Example:**
```python
# Using multipart/form-data for file upload
with open("image.png", "rb") as f:
    response = requests.post(
        "https://api.venice.ai/api/v1/image/edit",
        headers={"Authorization": f"Bearer {api_key}"},
        files={"image": f},
        data={"prompt": "Change the sky to sunset colors", "modelId": "qwen-edit"}
    )
```

**Best Practices for Editing:**
- Use short, descriptive prompts: "remove the tree", "change shirt color to red"
- Be specific about what to change, not what to keep
- Model has content filters (blocks explicit/violent content)

### 3. Image Upscaling and Enhancement

Upscale images 1x-4x with optional AI enhancement.

**Endpoint:** `POST /image/upscale`

**Parameters:**
- `image` (required) - File upload or base64
- `scale` - 1 to 4 (scale factor)
- `enhance` - Apply AI enhancement (must be true if scale=1)
- `enhanceCreativity` - 0-1, higher = more changes
- `enhancePrompt` - Style guidance (e.g., "gold", "marble", "crisp details")
- `replication` - 0-1, preserve original lines/noise (higher = noisier but less AI artifacts)

**Example - Pure Upscale:**
```python
response = requests.post(
    "https://api.venice.ai/api/v1/image/upscale",
    headers={"Authorization": f"Bearer {api_key}"},
    files={"image": open("low_res.png", "rb")},
    data={"scale": 2, "enhance": False}
)
```

**Example - Enhancement Only:**
```python
response = requests.post(
    "https://api.venice.ai/api/v1/image/upscale",
    headers={"Authorization": f"Bearer {api_key}"},
    files={"image": open("photo.jpg", "rb")},
    data={
        "scale": 1,
        "enhance": True,
        "enhanceCreativity": 0.6,
        "enhancePrompt": "professional photography, sharp details"
    }
)
```

### 4. Background Removal

Remove backgrounds from images.

**Endpoint:** `POST /image/remove-background`

**Parameters:**
- `image` (required) - File upload, base64 string, or URL

**Example:**
```python
response = requests.post(
    "https://api.venice.ai/api/v1/image/remove-background",
    headers={"Authorization": f"Bearer {api_key}"},
    files={"image": open("product.png", "rb")}
)
```

### 5. Video Generation

Generate videos from text prompts or animate images.

**⚠️ IMPORTANT: Always get user confirmation before generating video - it can be expensive!**

**Video Workflow:**
1. **Ask user to select model** (if not provided) - See available models at https://docs.venice.ai/models/video
2. **Get price quote** via `/video/quote`
3. **Show cost to user and confirm** before proceeding
4. **Queue generation** via `/video/queue`
5. **Poll** `/video/retrieve` until complete

**Step 1: Get Quote (ALWAYS do this first)**

**Endpoint:** `POST /video/quote`

**Parameters:**
- `model` (required) - e.g., `wan-2.5-preview-image-to-video`
- `duration` (required) - `5s` or `10s`
- `resolution` - `480p`, `720p` (default), `1080p`
- `aspect_ratio` - e.g., `16:9` (default), `9:16`
- `audio` - Include audio generation

**Step 2: Ask User for Model Selection and Confirm Cost**

```python
# Get available models (check documentation for current list)
models = [
    "wan-2.5-preview-image-to-video",
    "wan-2.5-preview-text-to-video"
]

# Ask user which model to use
print("Available video models:")
for i, model in enumerate(models):
    print(f"  {i+1}. {model}")

# Get quote for user's selected configuration
quote_response = requests.post(
    "https://api.venice.ai/api/v1/video/quote",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": selected_model,
        "duration": "5s",
        "resolution": "720p",
        "aspect_ratio": "16:9"
    }
)
price = quote_response.json()["quote"]  # Price in USD

# Show cost and get confirmation
print(f"\nVideo generation will cost: ${price:.4f} USD")
confirm = input("Proceed with video generation? (yes/no): ")

if confirm.lower() not in ["yes", "y"]:
    print("Video generation cancelled.")
    return
```

**Step 3: Queue Generation**

**Endpoint:** `POST /video/queue`

**Parameters:**
- `model` (required)
- `prompt` (required) - Text description (max 2500 chars)
- `duration` (required) - `5s` or `10s`
- `image_url` (required for image-to-video) - URL or data URL
- `negative_prompt` - What to avoid
- `resolution` - Video resolution
- `aspect_ratio` - Video aspect ratio (default: `16:9`)
- `audio` - Generate audio
- `end_image_url` - For models supporting end frames
- `reference_image_urls` - Up to 4 reference images for consistency

**Step 4: Retrieve Result**

**Endpoint:** `POST /video/retrieve`

**Parameters:**
- `model` (required) - Same model used for queue
- `queue_id` (required) - ID from queue response
- `delete_media_on_completion` - Auto-delete after download

**Complete Example (with user confirmation):**
```python
import time

# Step 1 & 2: Get quote and ask for model selection
def get_user_video_config(api_key):
    """Get video configuration with user confirmation."""
    
    print("Video Generation Setup")
    print("=" * 50)
    
    # Ask for model (check https://docs.venice.ai/models/video for current list)
    print("\nCommon video models:")
    print("  1. wan-2.5-preview-image-to-video (Image to Video)")
    print("  2. wan-2.5-preview-text-to-video (Text to Video)")
    model_choice = input("Enter model name (or number 1-2): ").strip()
    
    if model_choice == "1":
        model = "wan-2.5-preview-image-to-video"
    elif model_choice == "2":
        model = "wan-2.5-preview-text-to-video"
    else:
        model = model_choice
    
    # Get configuration
    duration = input("Duration (5s/10s) [5s]: ").strip() or "5s"
    resolution = input("Resolution (480p/720p/1080p) [720p]: ").strip() or "720p"
    aspect_ratio = input("Aspect ratio (16:9/9:16/1:1) [16:9]: ").strip() or "16:9"
    audio = input("Generate audio? (y/n) [y]: ").strip().lower() != "n"
    
    # Get quote
    quote_response = requests.post(
        "https://api.venice.ai/api/v1/video/quote",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "audio": audio
        }
    )
    price = quote_response.json()["quote"]
    
    # Show cost and confirm
    print(f"\n" + "=" * 50)
    print(f"VIDEO GENERATION COST: ${price:.4f} USD")
    print(f"Configuration:")
    print(f"  Model: {model}")
    print(f"  Duration: {duration}")
    print(f"  Resolution: {resolution}")
    print(f"  Aspect Ratio: {aspect_ratio}")
    print(f"  Audio: {audio}")
    print("=" * 50)
    
    confirm = input("\nProceed with video generation? (yes/no): ").strip().lower()
    
    if confirm not in ["yes", "y"]:
        print("Video generation cancelled.")
        return None
    
    return {
        "model": model,
        "duration": duration,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "audio": audio,
        "price": price
    }

# Usage
config = get_user_video_config(api_key)
if not config:
    return

# Step 3: Queue generation
queue_response = requests.post(
    "https://api.venice.ai/api/v1/video/queue",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": config["model"],
        "prompt": "Gentle waves lapping against the shore at sunset",
        "duration": config["duration"],
        "resolution": config["resolution"],
        "aspect_ratio": config["aspect_ratio"],
        "audio": config["audio"],
        "image_url": "data:image/png;base64,iVBORw0K...",  # Starting image
        "negative_prompt": "blurry, distorted, low quality"
    }
)
queue_id = queue_response.json()["queue_id"]

# Step 4: Poll for completion
while True:
    retrieve_response = requests.post(
        "https://api.venice.ai/api/v1/video/retrieve",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": config["model"], "queue_id": queue_id}
    )
    
    if retrieve_response.headers.get("content-type") == "video/mp4":
        # Video is ready
        with open("generated_video.mp4", "wb") as f:
            f.write(retrieve_response.content)
        print(f"Video saved! Total cost: ${config['price']:.4f} USD")
        break
    else:
        status = retrieve_response.json()
        if status["status"] == "PROCESSING":
            print(f"Processing... {status['execution_duration']}ms / {status['average_execution_time']}ms")
            time.sleep(5)
```

## Multi-Edit Workflow

For complex image modifications requiring multiple changes:

```python
def multi_edit_image(image_path, edits, api_key):
    """
    Apply multiple edits sequentially to an image.
    
    Args:
        image_path: Path to original image
        edits: List of edit prompts to apply in order
        api_key: Venice API key
    """
    current_image = image_path
    
    for i, edit_prompt in enumerate(edits):
        with open(current_image, "rb") as f:
            response = requests.post(
                "https://api.venice.ai/api/v1/image/edit",
                headers={"Authorization": f"Bearer {api_key}"},
                files={"image": f},
                data={
                    "prompt": edit_prompt,
                    "modelId": "qwen-edit"
                }
            )
        
        # Save intermediate result
        current_image = f"edit_step_{i+1}.png"
        with open(current_image, "wb") as f:
            f.write(response.content)
        
        print(f"Applied edit {i+1}/{len(edits)}: {edit_prompt}")
    
    return current_image

# Example usage
edits = [
    "Change the sky to golden sunset",
    "Add a flock of birds in the distance",
    "Enhance the foreground shadows"
]
final_image = multi_edit_image("original.jpg", edits, api_key)
```

## Advanced Workflows

### Product Photography Pipeline

Complete workflow from generation to publication-ready:

```python
def create_product_shot(product_description, api_key):
    """Generate and prepare product photography."""
    
    # 1. Generate base image (using cost-effective model)
    gen_response = requests.post(
        "https://api.venice.ai/api/v1/image/generate",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "z-image-turbo",  # Fast, cost-effective option
            "prompt": f"Professional product photography, white background, studio lighting, {product_description}",
            "aspect_ratio": "16:9",  # Default widescreen format
            "cfg_scale": 7.5,
            "hide_watermark": True  # No watermark
        }
    )
    
    # Save base image
    base64_image = gen_response.json()["images"][0]
    base_image_path = "product_base.png"
    with open(base_image_path, "wb") as f:
        f.write(base64.b64decode(base64_image))
    
    # 2. Upscale for high resolution
    with open(base_image_path, "rb") as f:
        upscale_response = requests.post(
            "https://api.venice.ai/api/v1/image/upscale",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"image": f},
            data={"scale": 2, "enhance": True, "enhanceCreativity": 0.3}
        )
    
    final_path = "product_final.png"
    with open(final_path, "wb") as f:
        f.write(upscale_response.content)
    
    return final_path
```

### Image Variations Pipeline

Generate multiple variations with different styles:

```python
def generate_variations(base_prompt, styles, api_key):
    """Generate image variations with different style presets."""
    variations = []
    
    for style in styles:
        response = requests.post(
            "https://api.venice.ai/api/v1/image/generate",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "nano-banana-pro",
                "prompt": base_prompt,
                "style_preset": style,
                "variants": 1,
                "hide_watermark": True  # No watermark
            }
        )
        
        image_data = response.json()["images"][0]
        variations.append({
            "style": style,
            "image": image_data
        })
    
    return variations
```

## Error Handling

Common HTTP status codes:
- `400` - Invalid parameters
- `401` - Authentication failed
- `402` - Insufficient balance
- `413` - Payload too large (video)
- `422` - Content policy violation
- `429` - Rate limit exceeded
- `500` - Inference processing failed
- `503` - Model at capacity

**Headers to Monitor:**
- `x-venice-is-blurred` - Image was blurred (Safe Venice mode)
- `x-venice-is-content-violation` - Content flagged
- `x-ratelimit-remaining-requests` - Rate limit status
- `x-venice-balance-usd` - Account balance

## Response Headers Reference

All Venice API responses include useful headers:

| Header | Description |
|--------|-------------|
| `CF-RAY` | Request ID for troubleshooting |
| `x-venice-model-id` | Model used for request |
| `x-venice-model-name` | Friendly model name |
| `x-ratelimit-remaining-requests` | Requests remaining |
| `x-ratelimit-remaining-tokens` | Tokens remaining |
| `x-venice-balance-usd` | USD balance |
| `x-venice-balance-diem` | DIEM token balance |

## Pricing Notes

- **Image Generation:** Varies by model (check `/models` endpoint)
- **Image Editing:** $0.04 per edit (qwen-edit)
- **Image Upscaling:** Included in image generation pricing
- **Background Removal:** Included
- **Video Generation:** Use `/video/quote` for exact pricing

## Resources

### references/
- `api_reference.md` - Complete API endpoint documentation
- `models.md` - Detailed model specifications and capabilities

### scripts/
- Example scripts for common workflows

## Tips and Best Practices

1. **Prompt Engineering:**
   - Be specific and descriptive
   - Include style keywords ("photorealistic", "oil painting", "3D render")
   - Specify lighting and composition
   - Use negative prompts to avoid unwanted elements

2. **Image Editing:**
   - Keep edit prompts short and focused
   - Apply edits sequentially for complex changes
   - Save intermediate results for rollback

3. **Video Generation:**
   - Always get a quote first to confirm pricing
   - Use reference images for character consistency
   - Poll every 5-10 seconds (don't hammer the API)
   - Set `delete_media_on_completion=True` to save storage

4. **Performance:**
   - Use `webp` format for smaller file sizes
   - Use `return_binary=True` for direct image downloads
   - Batch operations when possible
   - Cache generated results to avoid regeneration

5. **Content Safety:**
   - Default models have content filters
   - Set `safe_mode: false` for uncensored generation on supported models
   - Check `x-venice-is-blurred` header for policy violations
