#!/bin/bash
# EN voice candidates, round 2 (mid/higher pitch, per Jim's 'archival audio is tinny' idea). Waits for round 1 to finish, same recipe.
W=~/c-workstream; R=/srv/tts-out/render/c-en-voice
until grep -q ALL-VOICES-DONE $W/en_voices.out 2>/dev/null; do [ -e $R/STOP ] && exit 3; sleep 20; done
run() { tag=$1; lat=$2; shift 2
  env GAP_S=0.5 GAP_P=1.0 "$@" bash $W/c_brokkr_episode.sh en /srv/tts-out/c-input/ep01-en-p1a.txt $R/$tag en_$tag "$lat" --takes 4 --seed 5000 --names /srv/tts-out/c-input/ep01-en-page1.names.txt
  rc=$?; cp $R/$tag/final/en_$tag.mp3 $R/finals/ 2>/dev/null; return $rc; }
run Luis_Moray "Luis Moray" DEEPEN_ST=0 DEEPEN_BASS=0 || exit $?
run Ludvig_Milivoj "Ludvig Milivoj" DEEPEN_ST=0 DEEPEN_BASS=0 || exit $?
run Marcos_Rudaski "Marcos Rudaski" DEEPEN_ST=0 DEEPEN_BASS=0 || exit $?
run Viktor_Menelaos "Viktor Menelaos" DEEPEN_ST=0 DEEPEN_BASS=0 || exit $?
echo ROUND2-DONE
