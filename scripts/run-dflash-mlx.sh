#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DFLASH_DIR="${DFLASH_DIR:-"${ROOT_DIR}/../dflash"}"
DFLASH_REPO="${DFLASH_REPO:-https://github.com/z-lab/dflash.git}"
DFLASH_MODEL="${DFLASH_MODEL:-Qwen/Qwen3.5-4B}"
DFLASH_DRAFT_MODEL="${DFLASH_DRAFT_MODEL:-z-lab/Qwen3.5-4B-DFlash}"
DFLASH_DATASET="${DFLASH_DATASET:-gsm8k}"
DFLASH_MAX_SAMPLES="${DFLASH_MAX_SAMPLES:-8}"
DFLASH_MAX_NEW_TOKENS="${DFLASH_MAX_NEW_TOKENS:-128}"
DFLASH_TEMPERATURE="${DFLASH_TEMPERATURE:-0.0}"
DFLASH_ENABLE_THINKING="${DFLASH_ENABLE_THINKING:-0}"
DFLASH_PYTHON="${DFLASH_PYTHON:-3.11}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it first: https://docs.astral.sh/uv/" >&2
  exit 1
fi

if [[ ! -d "${DFLASH_DIR}/.git" ]]; then
  git clone "${DFLASH_REPO}" "${DFLASH_DIR}"
fi

cd "${DFLASH_DIR}"

if [[ ! -x .venv/bin/python ]]; then
  uv venv --python "${DFLASH_PYTHON}" .venv
fi

uv pip install -e '.[mlx]'

mkdir -p "${ROOT_DIR}/results/dflash"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_PATH="${ROOT_DIR}/results/dflash/${STAMP}-mlx.log"

args=(
  -m dflash.benchmark
  --backend mlx
  --model "${DFLASH_MODEL}"
  --draft-model "${DFLASH_DRAFT_MODEL}"
  --dataset "${DFLASH_DATASET}"
  --max-samples "${DFLASH_MAX_SAMPLES}"
  --max-new-tokens "${DFLASH_MAX_NEW_TOKENS}"
  --temperature "${DFLASH_TEMPERATURE}"
)

if [[ "${DFLASH_ENABLE_THINKING}" == "1" || "${DFLASH_ENABLE_THINKING}" == "true" ]]; then
  args+=(--enable-thinking)
fi

echo "DFlash repo: ${DFLASH_DIR}"
echo "Target:      ${DFLASH_MODEL}"
echo "Draft:       ${DFLASH_DRAFT_MODEL}"
echo "Dataset:     ${DFLASH_DATASET}, samples=${DFLASH_MAX_SAMPLES}, max_new_tokens=${DFLASH_MAX_NEW_TOKENS}"
echo "Log:         ${LOG_PATH}"

.venv/bin/python "${args[@]}" "$@" 2>&1 | tee "${LOG_PATH}"
