#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DFLASH_DIR="${DFLASH_DIR:-"${ROOT_DIR}/../dflash"}"
DFLASH_REPO="${DFLASH_REPO:-https://github.com/z-lab/dflash.git}"
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
LOG_PATH="${ROOT_DIR}/results/dflash/${STAMP}-coding-cases.log"

echo "DFlash repo: ${DFLASH_DIR}"
echo "Experiment:  ${ROOT_DIR}/scripts/dflash_coding_cases.py"
echo "Log:         ${LOG_PATH}"

.venv/bin/python "${ROOT_DIR}/scripts/dflash_coding_cases.py" "$@" 2>&1 | tee "${LOG_PATH}"
