#!/usr/bin/env bash
# c_brokkr_setup_asr.sh - user-level Whisper ASR venv + static ffmpeg for claude-agent on brokkr (no sudo, no Docker).
# Usage (from loki): scp it to brokkr:~/c-workstream/, then
#   ssh brokkr-agent 'nohup bash ~/c-workstream/c_brokkr_setup_asr.sh > ~/c-workstream/setup-asr.log 2>&1 < /dev/null &'
# Creates ~/c-workstream/venv-asr (py3.12, torch 2.11.0+cu126 like the XTTS venv, transformers 5.21.0), downloads
# openai/whisper-medium into ~/c-workstream/hf, installs static ffmpeg (needs the rubberband filter) into ~/.local/bin.
# Inbound downloads only. Workstream C, 2026-11-12.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd ~/c-workstream
[ -x venv-asr/bin/python ] || uv venv --python 3.12 venv-asr
uv pip install --python venv-asr/bin/python --index-url https://download.pytorch.org/whl/cu126 \
  --extra-index-url https://pypi.org/simple --index-strategy unsafe-best-match \
  torch==2.11.0 transformers==5.21.0 soundfile numpy scipy accelerate huggingface_hub
if ! command -v ffmpeg >/dev/null || ! ffmpeg -hide_banner -filters 2>/dev/null | grep -q rubberband; then
  mkdir -p dl/ff && cd dl/ff
  curl -fsSL -O https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
  curl -fsSL -O https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz.md5
  md5sum -c ffmpeg-release-amd64-static.tar.xz.md5
  tar -xJf ffmpeg-release-amd64-static.tar.xz
  install -m 0755 ffmpeg-*-amd64-static/ffmpeg ffmpeg-*-amd64-static/ffprobe ~/.local/bin/
  cd ~/c-workstream
fi
ffmpeg -hide_banner -version | head -1
ffmpeg -hide_banner -filters 2>/dev/null | grep -c rubberband || echo "WARNING: no rubberband filter"
HF_HOME=~/c-workstream/hf venv-asr/bin/python -c "from huggingface_hub import snapshot_download as s; print(s('openai/whisper-medium', allow_patterns=['*.json','*.safetensors','*.txt']))"
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 venv-asr/bin/python -c "import torch;print('torch',torch.__version__,torch.cuda.is_available(),torch.cuda.get_device_name(0))"
{ echo "date=$(date -Is)"; ffmpeg -version | head -1; venv-asr/bin/python --version; } > ~/c-workstream/setup-asr-manifest.txt
echo SETUP-DONE
