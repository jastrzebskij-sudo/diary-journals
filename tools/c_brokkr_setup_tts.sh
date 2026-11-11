#!/usr/bin/env bash
# c_brokkr_setup_tts.sh - user-level XTTS-v2 venv for claude-agent on brokkr (no Docker, no sudo, no credentials).
# Usage (from loki PowerShell):  ssh brokkr-agent 'nohup bash ~/c-workstream/c_brokkr_setup_tts.sh > ~/c-workstream/setup.log 2>&1 < /dev/null &'
# Steps: (1) uv standalone binary from GitHub releases (sha256 verified) into ~/.local/bin if missing,
#        (2) ~/work/tts/.venv with Python 3.12 (fetched by uv), (3) pinned requirements.lock per the repo README
#        (torch 2.11.0+cu126: the newest build that still runs on Pascal), (4) CUDA check on GPU index 1.
# Weights are already cached in ~/work/tts/models. Writes ~/c-workstream/setup-manifest.txt. Workstream C, 2026-11-11.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd ~/work/tts
if ! command -v uv >/dev/null; then
  mkdir -p ~/.local/bin ~/c-workstream/dl && cd ~/c-workstream/dl
  base=https://github.com/astral-sh/uv/releases/latest/download
  curl -fsSL -O "$base/uv-x86_64-unknown-linux-gnu.tar.gz" -O "$base/uv-x86_64-unknown-linux-gnu.tar.gz.sha256"
  sha256sum -c uv-x86_64-unknown-linux-gnu.tar.gz.sha256
  tar -xzf uv-x86_64-unknown-linux-gnu.tar.gz
  install -m 0755 uv-x86_64-unknown-linux-gnu/uv uv-x86_64-unknown-linux-gnu/uvx ~/.local/bin/
  cd ~/work/tts
fi
uv --version
[ -x .venv/bin/python ] || uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python --index-url https://download.pytorch.org/whl/cu126 \
  --extra-index-url https://pypi.org/simple --index-strategy unsafe-best-match -r requirements.lock
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 .venv/bin/python -c \
  "import torch;print('torch',torch.__version__,'cuda',torch.cuda.is_available(),torch.cuda.get_device_name(0))"
{ echo "date=$(date -Is)"; uv --version; .venv/bin/python --version; git -C ~/work/tts rev-parse --short HEAD; } > ~/c-workstream/setup-manifest.txt
echo SETUP-DONE
