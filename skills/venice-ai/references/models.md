# Venice AI Models Reference

Detailed information about Venice.ai image and video generation models.

## Quick Reference: Model Selection

### Cost-Effective Models (Start Here)

| Model | Type | Best For | Relative Cost |
|-------|------|----------|---------------|
| `z-image-turbo` | Image Gen | Fast, inexpensive (DEFAULT) | $ |
| `flux-2-dev` | Image Gen | Good quality, budget-friendly | $ |
| `fluently-xl` | Image Gen | Artistic outputs, budget | $ |
| `qwen-edit` | Image Edit | Inpainting at $0.04/edit | $ |

### Premium Models (Higher Quality)

| Model | Type | Best For | Relative Cost |
|-------|------|----------|---------------|
| `nano-banana-pro` | Image Gen | Photorealism, 2K/4K | $$ |
| `flux-2-max` | Image Gen | High quality, versatile | $$ |
| `grok-imagine` | Image Gen | Uncensored generation | $$-$$$ |

**Default Recommendation:** Use `z-image-turbo` for image generation (fast and cost-effective) and `qwen-edit` for editing.

**Pricing Source:** https://docs.venice.ai/models/image and https://docs.venice.ai/models/video

---

## Image Generation Models

### z-image-turbo (RECOMMENDED - Fast & Cost-Effective Default)

**Type:** Image Generation
**Best For:** Fast generation, quick iterations, low cost (DEFAULT)

**Capabilities:**
- Fast text-to-image generation
- Good quality for speed
- Standard resolutions
- Most cost-effective option

**Parameters:**
- Max prompt length: 7500 characters
- Standard width/height: up to 1024x1024
- Supports `aspect_ratio`: `1:1`, `16:9`, `9:16`, etc.

**Example:**
```python
{
  "model": "z-image-turbo",
  "prompt": "A serene landscape at sunset",
  "aspect_ratio": "16:9"
}
```

### flux-2-dev

**Type:** Image Generation
**Best For:** Good quality at budget-friendly pricing

**Capabilities:**
- Text-to-image generation
- Good quality for cost
- Standard resolutions
- Fast generation

**Parameters:**
- Max prompt length: 7500 characters
- Standard width/height: up to 1024x1024
- Supports `aspect_ratio`: `1:1`, `16:9`, `9:16`, etc.

**Example:**
```python
{
  "model": "flux-2-dev",
  "prompt": "A serene landscape at sunset",
  "aspect_ratio": "16:9"
}
```

### fluently-xl

**Type:** Image Generation
**Best For:** Artistic and creative outputs at low cost

**Capabilities:**
- Budget-friendly artistic generation
- Good for creative projects

### nano-banana-pro

**Type:** Image Generation
**Best For:** Photorealism, product photography, high resolution

**Capabilities:**
- Text-to-image generation
- Image editing (via nano-banana-pro-edit)
- High resolution support (up to 2K/4K)
- Multiple aspect ratios

**Parameters:**
- Max prompt length: 7500 characters
- Supports `aspect_ratio`: `1:1`, `16:9`, `9:16`, `4:3`, `3:2`, etc.
- Supports `resolution`: `1K`, `2K`, `4K`
- Width/Height divisor: Check model constraints endpoint

**Example:**
```python
{
  "model": "nano-banana-pro",
  "prompt": "Professional product photo of headphones",
  "resolution": "2K",
  "aspect_ratio": "1:1"
}
```

### flux-2-max

**Type:** Image Generation
**Best For:** High quality, versatile outputs

**Capabilities:**
- High-quality image generation
- Image editing (via flux-2-max-edit)
- Excellent prompt adherence

### seedream-v4

**Type:** Image Generation
**Best For:** Detailed compositions

**Capabilities:**
- Image editing (via seedream-v4-edit)

### grok-imagine

**Type:** Image Generation
**Best For:** Uncensored generation

**Capabilities:**
- Image editing (via grok-imagine-edit)
- More permissive content policies

### gpt-image-1-5

**Type:** Image Generation
**Best For:** Natural, coherent images

**Capabilities:**
- Image editing (via gpt-image-1-5-edit)

## Image Editing Models

### qwen-edit (Default - Cost-Effective)

**Type:** Image Editing/Inpainting
**Price:** $0.04 per edit

**Capabilities:**
- AI-powered inpainting
- Object removal/addition
- Style modifications
- Background changes

**Content Policy:**
- Blocks explicit sexual imagery
- Blocks sexualization of minors
- Blocks real-world violence depiction

**Parameters:**
- Max prompt length: Model-specific (check constraints)
- Supports aspect ratio adjustments
- Accepts file upload, base64, or URL

### flux-2-max-edit

**Type:** Image Editing
**Best For:** High-quality edits with flux base model

### nano-banana-pro-edit

**Type:** Image Editing
**Best For:** Editing with nano-banana base quality

### seedream-v4-edit

**Type:** Image Editing
**Best For:** Detailed editing tasks

### grok-imagine-edit

**Type:** Image Editing
**Best For:** Uncensored editing

### gpt-image-1-5-edit

**Type:** Image Editing
**Best For:** Natural-looking edits

## Video Generation Models

### wan-2.5-preview-image-to-video

**Type:** Image-to-Video
**Best For:** Animating static images

**Capabilities:**
- Convert images to short video clips
- Text-guided motion
- Configurable duration and resolution
- Optional audio generation
- End frame support
- Reference images for consistency

**Parameters:**
- Duration: `5s` or `10s`
- Resolution: `480p`, `720p`, `1080p`
- Aspect ratios: Model-specific
- Audio generation: Optional
- Reference images: Up to 4

**Input Requirements:**
- Starting image: Required (image_url)
- End image: Optional (end_image_url)
- Reference images: Up to 4 for character consistency
- Background audio: Optional WAV/MP3 (max 30s, 15MB)

**Workflow:**
1. Get quote via `/video/quote`
2. Queue via `/video/queue`
3. Poll `/video/retrieve` for completion

**Example:**
```python
{
  "model": "wan-2.5-preview-image-to-video",
  "prompt": "Gentle camera movement, waves lapping shore",
  "duration": "5s",
  "resolution": "720p",
  "aspect_ratio": "16:9",
  "image_url": "data:image/png;base64,...",
  "reference_image_urls": ["data:image/png;base64,..."]
}
```

### Additional Video Models

Check the `/models` endpoint with `type=video` filter for the complete list of available video models.

**Always check current pricing before generating video** - use the `/video/quote` endpoint.

## Model Selection Guide

### For Image Generation

**Choose z-image-turbo (DEFAULT) when:**
- Speed is priority
- Quick iterations needed
- Lowest cost acceptable
- Good quality for the price

**Choose flux-2-dev when:**
- Budget-conscious generation
- Good quality needed at low cost
- Standard resolutions acceptable
- Slightly higher quality than z-image-turbo

**Choose nano-banana-pro when:**
- Need photorealistic results
- Product photography
- High resolution required (2K/4K)
- Best overall quality (higher cost)

**Choose flux-2-max when:**
- Need high-quality artistic outputs
- Excellent prompt adherence required
- Versatile generation needs

**Choose grok-imagine when:**
- Uncensored generation needed
- More permissive content requirements

### For Image Editing

**Choose qwen-edit (DEFAULT) when:**
- General-purpose editing
- Cost-conscious ($0.04/edit)
- Standard content policies acceptable

**Choose flux-2-max-edit when:**
- Need highest quality edits
- Complex modifications required

**Choose grok-imagine-edit when:**
- Uncensored editing needed

### For Video Generation

**Choose wan-2.5-preview-image-to-video when:**
- Animating images
- Need character consistency
- Configurable duration/resolution

**Important:** Video generation can be expensive. Always:
1. Check available models at https://docs.venice.ai/models/video
2. Get quote via `/video/quote`
3. Confirm cost with user before generating

## Model Constraints

Common constraints to check per model via `/models` endpoint:

- `widthHeightDivisor` - Required divisor for width/height
- `promptCharacterLimit` - Maximum prompt length
- `negativePromptCharacterLimit` - Max negative prompt length
- `maxWidth`, `maxHeight` - Dimension limits
- `supportedResolutions` - Available resolution options
- `supportedAspectRatios` - Available aspect ratios

## Pricing Summary

**Image Generation:**
- Varies by model
- Budget models: flux-2-dev, z-image-turbo, fluently-xl
- Premium models: nano-banana-pro, flux-2-max, grok-imagine
- Check `/models` endpoint for current pricing

**Image Editing:**
- qwen-edit: $0.04 per edit (most cost-effective)
- Other models: Check `/models` endpoint

**Image Upscaling:**
- Included in image generation pricing

**Background Removal:**
- Included

**Video Generation:**
- Use `/video/quote` for exact pricing
- Depends on model, duration, resolution, audio options
- Can range from $0.10 to $1+ per video

## Getting Model Information

```python
import requests

# Get all models
response = requests.get(
    "https://api.venice.ai/api/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)

# Filter for image models
image_models = [m for m in response.json()["data"] if m.get("type") == "image"]

# Get specific model details
for model in image_models:
    print(f"Model: {model['id']}")
    print(f"Capabilities: {model.get('capabilities', {})}")
    print(f"Constraints: {model.get('constraints', {})}")
    print(f"Pricing: {model.get('pricing', {})}")
    print("---")
```

## Default Settings Summary

When using Venice AI skill without specific model requests:

- **Image Generation Model:** `z-image-turbo` (fast and cost-effective)
- **Image Editing Model:** `qwen-edit` ($0.04/edit)
- **Default Aspect Ratio:** `16:9`
- **Video Generation:** Always ask user for model and confirm cost

For premium results, explicitly request `nano-banana-pro` or other high-quality models.
