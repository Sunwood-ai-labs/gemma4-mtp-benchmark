#!/usr/bin/env bash
set -euo pipefail

gemma4-mtp-bench run \
  --model e2b \
  --backend gpu \
  --prompt-set quick \
  --rounds 1 \
  --output results/e2b-gpu-quick.json
