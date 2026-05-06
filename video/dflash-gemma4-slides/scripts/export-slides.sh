#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "${PROJECT_DIR}/../.." && pwd)"
OUT_DIR="${OUT_DIR:-"${ROOT_DIR}/docs/assets/dflash-gemma4-slides"}"

mkdir -p "${OUT_DIR}"

for slide in $(seq 1 11); do
  id="$(printf "%02d" "${slide}")"
  url="file://${PROJECT_DIR}/index.html?slide=${slide}"
  out="${OUT_DIR}/slide-${id}.png"
  echo "Exporting slide ${id} -> ${out}"
  npx --yes playwright@1.59.1 screenshot \
    --browser chromium \
    --viewport-size=1920,1080 \
    --wait-for-selector "#slide-${id}.snapshot-active" \
    --wait-for-timeout 250 \
    "${url}" \
    "${out}"
done
