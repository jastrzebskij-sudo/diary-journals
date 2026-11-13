#!/bin/bash
cd ~/c-workstream
CUDA_VISIBLE_DEVICES=0 venv-asr/bin/python c_brokkr_asr_exp.py 2>&1 | grep --line-buffered -E "same-as|Error|Traceback"
echo EXP-DONE
