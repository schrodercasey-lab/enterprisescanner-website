# Video Assets Folder

## Overview
This folder contains video assets for the Enterprise Scanner website video player component.

## Required Videos

### 1. Overview Video
- **Filename**: `overview.mp4`
- **Poster**: `overview-poster.jpg`
- **Thumbnail**: `overview-thumb.jpg`
- **Duration**: ~2:30
- **Content**: Platform overview and key features
- **Resolution**: 1920x1080 (Full HD)
- **Format**: MP4 (H.264)

### 2. Dashboard Demo
- **Filename**: `dashboard.mp4`
- **Poster**: `dashboard-poster.jpg`
- **Thumbnail**: `dashboard-thumb.jpg`
- **Duration**: ~3:15
- **Content**: Dashboard features walkthrough
- **Resolution**: 1920x1080 (Full HD)
- **Format**: MP4 (H.264)

### 3. Security Scanning
- **Filename**: `scanning.mp4`
- **Poster**: `scanning-poster.jpg`
- **Thumbnail**: `scanning-thumb.jpg`
- **Duration**: ~2:45
- **Content**: Vulnerability scanning demonstration
- **Resolution**: 1920x1080 (Full HD)
- **Format**: MP4 (H.264)

## Video Specifications

### Encoding Settings
- **Codec**: H.264
- **Container**: MP4
- **Frame Rate**: 30 fps
- **Bitrate**: 5-8 Mbps
- **Audio**: AAC, 192 kbps, stereo

### Image Specifications
- **Posters**: 1920x1080 JPG (high quality)
- **Thumbnails**: 160x90 JPG (optimized)

## Creating Placeholder Videos

For development/testing, you can create placeholder videos:

### Using FFmpeg:
```bash
# Create a 30-second test video with timer
ffmpeg -f lavfi -i testsrc=duration=30:size=1920x1080:rate=30 \
       -f lavfi -i sine=frequency=1000:duration=30 \
       -pix_fmt yuv420p overview.mp4

# Create poster image from first frame
ffmpeg -i overview.mp4 -vframes 1 -f image2 overview-poster.jpg

# Create thumbnail (scaled down)
ffmpeg -i overview-poster.jpg -vf scale=160:90 overview-thumb.jpg
```

### Using Screen Recording:
1. Record a 2-3 minute walkthrough of your dashboard
2. Export as MP4 (H.264, 30fps)
3. Take screenshot for poster
4. Resize poster for thumbnail

## Production Videos

For production deployment, create professional videos:

### Content Guidelines
1. **Clear Narration**: Professional voiceover explaining features
2. **Screen Recordings**: High-quality captures of actual platform
3. **On-Screen Text**: Highlight key points and features
4. **Branding**: Include Enterprise Scanner logo and branding
5. **Call-to-Action**: End with CTA (demo request, trial signup)

### Tools Recommended
- **Recording**: OBS Studio, Camtasia, ScreenFlow
- **Editing**: Adobe Premiere, Final Cut Pro, DaVinci Resolve
- **Compression**: HandBrake, FFmpeg

## File Size Optimization

Target sizes:
- **Overview**: < 25 MB
- **Dashboard**: < 30 MB
- **Scanning**: < 28 MB
- **Total**: < 100 MB for all videos

### Optimization Tips:
1. Use H.264 with CRF 23-28
2. Optimize audio at 128-192 kbps
3. Remove unnecessary frames
4. Use adaptive streaming for larger files

## CDN Hosting (Production)

For production, host videos on CDN:
- **AWS S3 + CloudFront**
- **Azure Blob Storage + CDN**
- **Cloudflare Stream**
- **Vimeo Pro** (embed)
- **YouTube** (unlisted, embed)

Update video URLs in `video-player.js`:
```javascript
playlist: [
    {
        title: 'Enterprise Scanner Overview',
        url: 'https://cdn.enterprisescanner.com/videos/overview.mp4',
        // ...
    }
]
```

## Current Status

⚠️ **Placeholder videos needed for development**

To test the video player component:
1. Add actual video files to this folder
2. Or update URLs to point to existing videos
3. Or use a test video service (Big Buck Bunny, etc.)

## Next Steps

1. Record or acquire professional product demo videos
2. Create poster images and thumbnails
3. Optimize and compress for web delivery
4. Upload to CDN for production
5. Update URLs in video player configuration
