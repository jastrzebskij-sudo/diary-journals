#!/bin/bash
ps aux | grep -E '[e]pisode_pick|[f]astcheck' | cut -c1-100
for p in $(ps aux | grep -E '[e]pisode_pick|[f]astcheck' | awk '{print $2}'); do kill $p; done
sleep 1; rm -rf /srv/tts-out/render/c-pipe-val1fast; ls /srv/tts-out/render | grep -c fast
