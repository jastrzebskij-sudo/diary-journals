#!/bin/bash
cat /srv/tts-out/c-input/f0-ranking.csv | head -40
echo ----; ls ~/work/tts/latents | head -30; sed -n 1,30p ~/work/tts/scripts/blend.py
