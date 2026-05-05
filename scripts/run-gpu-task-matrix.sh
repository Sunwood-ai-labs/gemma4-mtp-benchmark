#!/usr/bin/env bash
set -euo pipefail

model="${1:-e4b}"
backend="${2:-gpu}"
rounds="${3:-1}"
warmups="${4:-1}"

prompt_sets=(
  coding
  summarize
  rewrite
  extract
  json
  translation
  creative
)

mkdir -p results

for prompt_set in "${prompt_sets[@]}"; do
  echo "==> model=${model} backend=${backend} prompt_set=${prompt_set}"
  gemma4-mtp-bench run \
    --model "${model}" \
    --backend "${backend}" \
    --prompt-set "${prompt_set}" \
    --rounds "${rounds}" \
    --warmups "${warmups}" \
    --output "results/${model}-${backend}-${prompt_set}.json"
done
