# DFlash and Gemma 4 Experiment Slides

Japanese HyperFrames slide deck summarizing the local LiteRT-LM Gemma 4 MTP and DFlash MLX experiments.

## Check

```bash
npm run check
```

## Export Slide Images

```bash
npm run export:slides
```

Images are written to:

```text
../../docs/assets/dflash-gemma4-slides/
```

## Render Video

```bash
npm run render
```

The default render lands in `renders/`. Copy the finished MP4 to
`../../docs/assets/dflash-gemma4-slides/dflash-gemma4-slides.mp4` when updating
the published docs artifact.

If FFmpeg is missing on macOS, install it separately or put an `ffmpeg` binary on
`PATH` before running HyperFrames render.
