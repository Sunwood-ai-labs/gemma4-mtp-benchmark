<div align="center">

# Gemma 4 MTP Benchmark

Feel the difference between Gemma 4 LiteRT-LM generation with Multi-Token Prediction on and off.

[日本語](README.ja.md) | [Docs](https://sunwood-ai-labs.github.io/gemma4-mtp-benchmark/)

[![CI](https://github.com/Sunwood-ai-labs/gemma4-mtp-benchmark/actions/workflows/ci.yml/badge.svg)](https://github.com/Sunwood-ai-labs/gemma4-mtp-benchmark/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-3776ab.svg)](pyproject.toml)

</div>

## Why This Exists

Google's LiteRT-LM Gemma 4 page says LiteRT-LM currently supports Gemma 4 E2B and E4B, and recommends MTP on GPU backends. This repository turns that into a small, repeatable Apple Silicon benchmark you can run locally.

It measures:

- baseline generation with speculative decoding off
- MTP generation with speculative decoding on
- generation seconds, chars/sec, and estimated tokens/sec
- machine metadata so results from M1, M2, M3, and M4 Macs can be compared

The model files are downloaded at runtime and are never committed to the repository.

## Watch The Difference

The repository includes a 30-second HyperFrames video built from the local M1 Max task matrix:

[Watch the speed comparison video](https://sunwood-ai-labs.github.io/gemma4-mtp-benchmark/assets/mtp-speed-comparison.mp4)

It highlights the visible E4B coding win (`76.28s` off versus `40.79s` on) and the broader task pattern: coding, JSON formatting, and extraction benefit most; creative and very short prompts may be flat or slower.

## Quick Start

Apple Silicon Mac plus `uv` is the smoothest path:

```bash
git clone https://github.com/Sunwood-ai-labs/gemma4-mtp-benchmark.git
cd gemma4-mtp-benchmark
uv venv
uv pip install -e '.[bench]'
uv run gemma4-mtp-bench doctor
```

## Interactive Chat

To type your own prompts and feel LiteRT-LM MTP directly, use `chat`:

```bash
uv run gemma4-mtp-bench chat --model e4b --backend gpu --mode mtp
```

To compare the same prompt with MTP off and on in one session:

```bash
uv run gemma4-mtp-bench chat --model e4b --backend gpu --mode compare
```

Inside the chat, type `/bye`, `/exit`, `/quit`, or press `Ctrl-D` to stop.

Run a quick E2B GPU comparison:

```bash
uv run gemma4-mtp-bench run \
  --model e2b \
  --backend gpu \
  --prompt-set quick \
  --rounds 1 \
  --output results/e2b-gpu-quick.json
```

If your Mac has 16 GB or more, E4B is the more interesting comparison:

```bash
uv run gemma4-mtp-bench run \
  --model e4b \
  --backend gpu \
  --prompt-set coding \
  --rounds 2 \
  --output results/e4b-gpu-coding.json
```

In the repository creation smoke test on a MacBook Pro M1 Max with 64 GB memory, the E4B GPU coding prompt set measured about `1.87x` estimated tokens/sec with MTP enabled. The short E2B quick prompt was slower with MTP in that one run, so treat `quick` as a smoke test and use `coding` or `summarize` to feel the difference. See [the local benchmark note](benchmarks/2026-05-06-m1-max.md).

A broader one-round task matrix on the same M1 Max showed the clearest MTP wins on predictable tasks:

- E4B GPU `coding`: `1.87x`
- E4B GPU `json`: `1.65x`
- E4B GPU `extract`: `1.51x`
- E2B GPU `json`: `1.53x`
- E2B CPU `json`: `1.81x`

Open-ended `creative` and very short `quick` prompts were flat or slower. See [the task matrix note](benchmarks/2026-05-06-task-matrix-m1-max.md).

## DFlash Comparison Lane

[z-lab/dflash](https://github.com/z-lab/dflash) is a separate speculative decoding project with an MLX backend for Apple Silicon. It does not target the LiteRT-LM E2B/E4B files, so this repository treats it as a comparison lane rather than a direct replacement.

Run the practical DFlash smoke test:

```bash
scripts/run-dflash-mlx.sh
```

By default, that clones or reuses `../dflash`, installs DFlash with `.[mlx]`, and benchmarks `Qwen/Qwen3.5-4B` against `z-lab/Qwen3.5-4B-DFlash` on `gsm8k`.

On the same M1 Max used above, the cached 8-sample DFlash MLX smoke measured:

| Lane | Baseline | Speculative | Speed ratio |
| --- | ---: | ---: | ---: |
| LiteRT-LM E4B GPU `json` | 21.5 est tok/s | 35.6 est tok/s | 1.65x |
| DFlash MLX Qwen3.5-4B `gsm8k` | 28.31 tok/s | 44.28 tok/s | 1.56x |

To try the heavier Gemma 4 31B DFlash path:

```bash
DFLASH_MODEL=mlx-community/gemma-4-31b-it-4bit \
DFLASH_DRAFT_MODEL=z-lab/gemma-4-31B-it-DFlash \
DFLASH_ENABLE_THINKING=1 \
DFLASH_MAX_SAMPLES=4 \
DFLASH_MAX_NEW_TOKENS=128 \
scripts/run-dflash-mlx.sh
```

The Gemma 4 31B target plus DFlash draft is roughly 20 GiB of model downloads. See [the DFlash MLX comparison note](benchmarks/2026-05-06-dflash-mlx-m1-max.md).

Render a Markdown report:

```bash
uv run gemma4-mtp-bench report \
  results/e4b-gpu-coding.json \
  --output results/e4b-gpu-coding.md
```

## What To Try

| Mac | Suggested first run |
| --- | --- |
| M1/M2/M3/M4 with 8 GB | `--model e2b --backend gpu --prompt-set quick` |
| M1/M2/M3/M4 with 16 GB+ | `--model e4b --backend gpu --prompt-set coding` |
| M4 Pro/Max/Ultra | `--model e4b --backend gpu --prompt-set coding --rounds 3` |
| Intel Mac | CPU may run, but this benchmark is not aimed at the MTP experience there |

Prompt sets:

- `quick`: short Japanese explanation
- `coding`: Python code generation prompts, usually good for feeling MTP
- `summarize`: constrained summarization
- `rewrite`: README-style rewriting
- `extract`: structured extraction from logs
- `json`: strict JSON formatting
- `translation`: technical English-to-Japanese translation
- `creative`: short open-ended introduction

Run a broader task matrix:

```bash
scripts/run-gpu-task-matrix.sh e4b gpu 1 1
```

## Commands

```bash
gemma4-mtp-bench doctor
gemma4-mtp-bench download --model e2b
gemma4-mtp-bench run --model e2b --backend gpu --prompt-set quick
gemma4-mtp-bench run --model e4b --backend gpu --prompt-set coding --rounds 2
gemma4-mtp-bench report results/e4b-gpu-coding.json --output results/e4b-gpu-coding.md
```

For a no-download smoke test:

```bash
PYTHONPATH=src python3 -m gemma4_mtp_benchmark run --model e2b --backend gpu --dry-run
```

## Reading Results

The summary prints a table like this:

```text
| MTP | runs | mean seconds | mean chars/sec | est tokens/sec |
| --- | ---: | ---: | ---: | ---: |
| off | 2 | 18.42 | 49.1 | 18.0 |
| on  | 2 | 10.21 | 88.4 | 32.2 |

Estimated MTP speed ratio: 1.79x
```

`est tokens/sec` is an approximation from output text length. LiteRT-LM streaming chunks do not expose exact token counts through the simple API used here, so compare runs using the same prompt set.

## Troubleshooting

If GPU fails, confirm CPU first:

```bash
uv run gemma4-mtp-bench run --model e2b --backend cpu --prompt-set quick --rounds 1
```

LiteRT/WebGPU may print low-level adapter and kernel initialization logs before the benchmark summary. They are normal unless the command exits with an error.

If you downloaded LiteRT Gemma 4 models before 2026-05-05 and want speculative decoding, remove the old cached model and download again. The LiteRT Community model cards note that speculative decoding requires a fresh model from that date onward.

## References

- [Google AI Edge: Gemma 4 for LiteRT-LM](https://ai.google.dev/edge/litert-lm/models/gemma-4)
- [Google AI Edge: LiteRT-LM CLI](https://ai.google.dev/edge/litert-lm/cli)
- [Google AI Edge: LiteRT-LM Python API](https://ai.google.dev/edge/litert-lm/python)
- [Hugging Face: Gemma 4 E2B LiteRT-LM](https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm)
- [Hugging Face: Gemma 4 E4B LiteRT-LM](https://huggingface.co/litert-community/gemma-4-E4B-it-litert-lm)
- [z-lab/dflash](https://github.com/z-lab/dflash)
- [Hugging Face: Qwen3.5-4B DFlash](https://huggingface.co/z-lab/Qwen3.5-4B-DFlash)
- [Hugging Face: Gemma 4 31B DFlash](https://huggingface.co/z-lab/gemma-4-31B-it-DFlash)

## License

Repository code and docs are Apache-2.0. Gemma model weights are downloaded from Hugging Face and are governed by their own model terms.
