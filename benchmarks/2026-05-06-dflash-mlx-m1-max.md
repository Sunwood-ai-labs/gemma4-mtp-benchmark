# DFlash MLX comparison on M1 Max

Date: 2026-05-06  
Machine: Apple M1 Max, 64 GiB memory, macOS 26.4.1, arm64  
DFlash checkout: `z-lab/dflash` commit `6d6229e`  
DFlash install: `uv venv --python 3.11 .venv` then `uv pip install -e '.[mlx]'`

## Why this is a separate lane

[DFlash](https://github.com/z-lab/dflash) is not LiteRT-LM MTP. It is a block diffusion draft model for speculative decoding, with MLX support for Apple Silicon. The upstream README lists DFlash drafts for Qwen3.5-4B and Gemma 4 31B/26B-class models, and says the MLX implementation was tested on Apple Silicon with Qwen3, Qwen3.5, and Gemma-4 models.

That means this repository now has two useful but different experiences:

| Lane | Runtime | Default local model | What it shows |
| --- | --- | --- | --- |
| LiteRT-LM MTP | LiteRT-LM GPU | Gemma 4 E2B/E4B | Google's Gemma 4 LiteRT-LM MTP path |
| DFlash MLX | MLX | Qwen3.5-4B + DFlash draft | DFlash speculative decoding on Apple Silicon |

The numbers below are not model-to-model apples-to-apples. They are a same-machine check that both speculative paths can produce visible decode speedups on predictable tasks.

## DFlash Qwen3.5-4B smoke

Command:

```bash
cd /Users/admin/Prj/dflash
.venv/bin/python -m dflash.benchmark \
  --backend mlx \
  --model Qwen/Qwen3.5-4B \
  --draft-model z-lab/Qwen3.5-4B-DFlash \
  --dataset gsm8k \
  --max-samples 8 \
  --max-new-tokens 128 \
  --temperature 0.0
```

Result:

| Metric | Value |
| --- | ---: |
| Baseline throughput | 28.31 tok/s |
| DFlash throughput | 44.28 tok/s |
| Decoding speedup | 1.56x |
| Average acceptance length | 5.34 |

A smaller first smoke with `--max-samples 2` produced `27.06 tok/s` baseline, `38.01 tok/s` DFlash, and `1.40x` speedup.

## LiteRT-LM E4B comparison snapshot

Command:

```bash
uv run gemma4-mtp-bench run \
  --model e4b \
  --backend gpu \
  --prompt-set json \
  --rounds 3 \
  --warmups 1 \
  --preview-chars 0 \
  --output results/e4b-gpu-json-dflash-comparison-local.json
```

Result:

| MTP | runs | mean seconds | mean chars/sec | est tokens/sec |
| --- | ---: | ---: | ---: | ---: |
| off | 3 | 2.31 | 80.7 | 21.5 |
| on | 3 | 1.39 | 133.5 | 35.6 |

Estimated MTP speed ratio: `1.65x`

## Model download sizes checked

Hugging Face model metadata on 2026-05-06:

| Model | Approx repository bytes |
| --- | ---: |
| `Qwen/Qwen3.5-4B` | 8.70 GiB |
| `z-lab/Qwen3.5-4B-DFlash` | 1.00 GiB |
| `mlx-community/gemma-4-31b-it-4bit` | 17.18 GiB |
| `z-lab/gemma-4-31B-it-DFlash` | 2.86 GiB |

Use the Qwen3.5-4B lane for a practical first run. The Gemma 4 31B lane downloads roughly 20 GiB of additional model files and takes noticeably longer to load.

## Gemma 4 31B DFlash smoke

Command:

```bash
DFLASH_MODEL=mlx-community/gemma-4-31b-it-4bit \
DFLASH_DRAFT_MODEL=z-lab/gemma-4-31B-it-DFlash \
DFLASH_ENABLE_THINKING=1 \
DFLASH_MAX_SAMPLES=4 \
DFLASH_MAX_NEW_TOKENS=128 \
scripts/run-dflash-mlx.sh
```

Result:

| Metric | Value |
| --- | ---: |
| Baseline throughput | 12.10 tok/s |
| DFlash throughput | 11.38 tok/s |
| Decoding speedup | 0.94x |
| Average acceptance length | 7.03 |

A smaller first smoke with `--max-samples 1 --max-new-tokens 64` produced `11.51 tok/s` baseline, `8.91 tok/s` DFlash, and `0.77x` speedup.

This confirms the Gemma 4 31B DFlash path runs on this M1 Max, but this short local setup did not show a speedup. The upstream DFlash README's MLX benchmark example uses more samples, and the README says their MLX testing covered Apple M5 Pro hardware. Treat this M1 Max 31B result as a runnable smoke result, not a final performance claim.

## Reproduce from this repository

Default DFlash smoke:

```bash
scripts/run-dflash-mlx.sh
```

Heavy Gemma 4 31B MLX lane:

```bash
DFLASH_MODEL=mlx-community/gemma-4-31b-it-4bit \
DFLASH_DRAFT_MODEL=z-lab/gemma-4-31B-it-DFlash \
DFLASH_ENABLE_THINKING=1 \
DFLASH_MAX_SAMPLES=4 \
DFLASH_MAX_NEW_TOKENS=128 \
scripts/run-dflash-mlx.sh
```

## Notes

- DFlash reports exact token throughput from the MLX generation stream.
- The LiteRT-LM helper in this repository reports estimated tokens/sec from output length, so compare LiteRT runs against LiteRT runs using the same prompt set.
- DFlash's default Qwen3.5-4B lane is the easiest way to feel the technique locally, but it is not a replacement for the Gemma 4 E2B/E4B LiteRT-LM MTP path.
