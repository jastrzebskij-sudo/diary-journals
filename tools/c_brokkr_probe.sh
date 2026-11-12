#!/bin/bash
echo ok; hostname
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader
ls -la ~/c-workstream ~/.local/bin
~/work/tts/.venv/bin/python -c 'import transformers,torch;print(transformers.__version__,torch.__version__)' 2>&1 | tail -1
df -h ~ | tail -1
ls /srv/tts-out
