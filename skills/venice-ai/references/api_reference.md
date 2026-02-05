# Venice AI API Reference

Complete reference for Venice.ai image and video generation endpoints.

## Base Information

**Base URL:** `https://api.venice.ai/api/v1`

**Authentication:** All endpoints require `Authorization: Bearer VENICE_API_KEY` header

## Image Endpoints

### POST /image/generate

Generate images from text prompts using Venice's native endpoint.

**Request Body:**
```json
{
  "model": "z-image-turbo",
  "prompt": "A serene landscape at sunset",
  "width": 1024,
  "height": 576,
  "negative_prompt": "blurry, distorted",
  "cfg_scale": 7.5,
  "seed": 12345,
  "format": "webp",
  "variants": 1,
  "safe_mode": false,
  "aspect_ratio": "16:9",
  "resolution": "1K",
  "style_preset": "Photographic",
  "hide_watermark": true,
  "embed_exif_metadata": false,
  "lora_strength": 50,
  "enable_web_search": false,
  "return_binary": false
}
```

**Response (JSON):**
```json
{
  "id": "generate-image-1234567890",
  "images": ["base64encodedstring..."],
  "request": {...},
  "timing": {
    "inferenceDuration": 2500,
    "inferencePreprocessingTime": 150,
    "inferenceQueueTime": 500,
    "total": 3150
  }
}
```

**Response (Binary when return_binary=true):**
- Content-Type: `image/jpeg`, `image/png`, or `image/webp`
- Raw image bytes

### POST /images/generations

OpenAI-compatible image generation endpoint.

**Request Body:**
```json
{
  "prompt": "A serene canal in Venice",
  "model": "nano-banana-pro",
  "n": 1,
  "size": "1024x1024",
  "quality": "auto",
  "style": "natural",
  "response_format": "b64_json",
  "output_format": "png",
  "moderation": "auto"
}
```

**Response:**
```json
{
  "created": 1713833628,
  "data": [
    {"b64_json": "iVBORw0KGgoAAAANSUhEUgAA..."}
  ]
}
```

### POST /image/edit

Edit/modify images using AI inpainting.

**Content-Type:** `multipart/form-data` or `application/json`

**Parameters (multipart):**
- `image` (file) - Image file to edit
- `prompt` (string) - Edit instructions
- `modelId` (string) - Model to use
- `aspect_ratio` (string) - Output aspect ratio

**Parameters (JSON):**
```json
{
  "image": "base64encodedstring...",
  "prompt": "Change the sky to sunset",
  "modelId": "qwen-edit",
  "aspect_ratio": "16:9"
}
```

**Response:**
- Content-Type: `image/png`
- Binary image data

**Available Edit Models:**
- `qwen-edit` (default) - $0.04/edit
- `flux-2-max-edit`
- `gpt-image-1-5-edit`
- `grok-imagine-edit`
- `nano-banana-pro-edit`
- `seedream-v4-edit`

### POST /image/upscale

Upscale and/or enhance images.

**Content-Type:** `multipart/form-data` or `application/json`

**Parameters:**
- `image` (required) - Image file or base64
- `scale` (number) - 1 to 4 (default: 2)
- `enhance` (boolean) - Apply AI enhancement (default: false)
- `enhanceCreativity` (number) - 0-1 (default: 0.5)
- `enhancePrompt` (string) - Style guidance
- `replication` (number) - 0-1, preserve original (default: 0.35)

**Constraints:**
- Image must be >= 65536 pixels
- Final dimensions after scaling must not exceed 16777216 pixels
- File size must be < 25MB

**Response:**
- Content-Type: `image/png`
- Binary image data

### POST /image/remove-background

Remove background from images.

**Content-Type:** `multipart/form-data` or `application/json`

**Parameters:**
- `image` (required) - Image file, base64, or URL

**Response:**
- Content-Type: `image/png` (with alpha channel)
- Binary image data

## Video Endpoints

### POST /video/quote

Get price estimate for video generation.

**Request Body:**
```json
{
  "model": "wan-2.5-preview-image-to-video",
  "duration": "5s",
  "resolution": "720p",
  "aspect_ratio": "16:9",
  "audio": true
}
```

**Response:**
```json
{
  "quote": 0.15
}
```

**Duration Options:** `5s`, `10s`
**Resolution Options:** `480p`, `720p`, `1080p`

### POST /video/queue

Queue a new video generation request.

**Request Body:**
```json
{
  "model": "wan-2.5-preview-image-to-video",
  "prompt": "Gentle waves at sunset",
  "duration": "5s",
  "image_url": "data:image/png;base64,...",
  "negative_prompt": "blurry, distorted",
  "resolution": "720p",
  "aspect_ratio": "16:9",
  "audio": true,
  "end_image_url": "data:image/png;base64,...",
  "reference_image_urls": ["data:image/png;base64,..."],
  "audio_url": "data:audio/mpeg;base64,...",
  "video_url": "data:video/mp4;base64,..."
}
```

**Required Fields:**
- `model`
- `prompt`
- `duration`
- `image_url` (for image-to-video models)

**Response:**
```json
{
  "model": "wan-2.5-preview-image-to-video",
  "queue_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### POST /video/retrieve

Retrieve video generation result.

**Request Body:**
```json
{
  "model": "wan-2.5-preview-image-to-video",
  "queue_id": "123e4567-e89b-12d3-a456-426614174000",
  "delete_media_on_completion": false
}
```

**Response (Processing):**
```json
{
  "status": "PROCESSING",
  "average_execution_time": 145000,
  "execution_duration": 53200
}
```

**Response (Complete):**
- Content-Type: `video/mp4`
- Binary video data

## Utility Endpoints

### GET /models

List all available models with capabilities and pricing.

**Query Parameters:**
- `type` - Filter by type: `text`, `image`, `audio`, `video`, `embedding`

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "nano-banana-pro",
      "object": "model",
      "created": 1700000000,
      "owned_by": "venice",
      "type": "image",
      "capabilities": {
        "generation": true,
        "upscale": false,
        "edit": true
      },
      "pricing": {...}
    }
  ]
}
```

## Error Responses

### Standard Error
```json
{
  "error": "Description of the error"
}
```

### Detailed Error (Validation)
```json
{
  "error": "Invalid request",
  "details": {
    "field": {
      "_errors": ["Field is required"]
    }
  }
}
```

## Content Safety Headers

Response headers indicating content filtering:

- `x-venice-is-blurred` - Image was blurred (true/false)
- `x-venice-is-content-violation` - Content violates ToS (true/false)
- `x-venice-is-adult-model-content-violation` - Adult content violation
- `x-venice-contains-minor` - Image contains minors

## Rate Limit Headers

- `x-ratelimit-limit-requests` - Request limit
- `x-ratelimit-remaining-requests` - Remaining requests
- `x-ratelimit-reset-requests` - Reset timestamp
- `x-ratelimit-limit-tokens` - Token limit
- `x-ratelimit-remaining-tokens` - Remaining tokens
- `x-ratelimit-reset-tokens` - Reset duration (seconds)

## Request Limits

### Image Endpoints
- Max prompt length: 7500 characters (model-specific)
- Max image size: 25MB
- Min image dimensions: 65536 pixels (width × height)
- Max image dimensions: 33177600 pixels (edit), 16777216 pixels (upscale output)
- Max width/height: 1280 pixels (generation)

### Video Endpoints
- Max prompt length: 2500 characters
- Max audio size: 15MB
- Max audio duration: 30 seconds
- Supported audio formats: WAV, MP3
- Supported video input formats: MP4, MOV, WebM
- Max reference images: 4
