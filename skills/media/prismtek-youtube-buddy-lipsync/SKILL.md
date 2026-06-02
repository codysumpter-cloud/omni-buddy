---
name: prismtek-youtube-buddy-lipsync
description: Produce a Prismtek/Buddy talking-host overlay for narrated videos using pixel-art visemes and FFmpeg audio RMS animation.
version: 1.1.0
author: Prismtek
license: MIT
platforms: [macos, linux]
metadata:
  tags: [youtube, video, ffmpeg, imagemagick, pixel-art, vtuber, buddy, prismtek]
  canonical_runtime: codysumpter-cloud/buddy-agent#18
---

# Prismtek YouTube Buddy Lip-Sync

This skill gives Omni Buddy a local-device reference for rendering a Buddy talking-host overlay from a clean Buddy avatar and narrated media.

The canonical runnable package lives in `buddy-agent`. This repo keeps the embodied/local-device integration reference so the Raspberry Pi / offline Buddy surface can use the same contract without inventing a separate workflow.

## Expected Local Tools

```bash
command -v magick
command -v ffmpeg
command -v ffprobe
python3 --version
```

## Flow

1. Generate Buddy mouth states from a clean Buddy avatar.
2. Analyze narration energy frame-by-frame.
3. Render a proof clip with a Buddy overlay.
4. Review visual quality before using the output.

## Generated Outputs

Keep generated media and receipts outside the repo, preferably under a local output folder.

## Related

- Canonical runtime PR: `codysumpter-cloud/buddy-agent#18`
- Operator reference PR: `codysumpter-cloud/buddy-brain#315`
- Upstream context: `NousResearch/hermes-agent#26463`
