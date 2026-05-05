# MTP Speed Comparison Video

HyperFrames source for the 30-second speed comparison video embedded in the docs site.

## Check

```bash
npm run check
```

The current composition is intentionally single-file for easy review. HyperFrames reports a maintainability warning about file size, but lint, console validation, contrast, and layout inspection pass.

## Render

Install FFmpeg/FFprobe on your machine, then run:

```bash
npm run render -- --quality standard --fps 30 --workers 1 --output ../../docs/assets/mtp-speed-comparison.mp4
```

If FFmpeg is not globally available, a local fallback works:

```bash
npm install --no-save ffmpeg-static ffprobe-static
ln -sf ../ffmpeg-static/ffmpeg node_modules/.bin/ffmpeg
ln -sf ../ffprobe-static/bin/darwin/arm64/ffprobe node_modules/.bin/ffprobe
PATH="$PWD/node_modules/.bin:$PATH" npm run render -- --quality standard --fps 30 --workers 1 --output ../../docs/assets/mtp-speed-comparison.mp4
```
