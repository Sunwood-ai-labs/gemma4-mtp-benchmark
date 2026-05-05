#!/usr/bin/env bash
set -euo pipefail

gemma4-mtp-bench run \
  --model e4b \
  --backend gpu \
  --prompt-set coding \
  --rounds 2 \
  --output results/e4b-gpu-coding.json
