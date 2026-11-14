B=/srv/tts-out/render/ep01_pl
echo "== 2-2 run.log tail"; tail -12 $B/2-2/run.log
echo "== flags"; tail -5 $B/flags.txt
echo "== pages dir"; ls ~/c-workstream/ep01_pl/pages | tr '\n' ' '; echo
echo "== p2-5 PL tail"; tail -c 600 ~/c-workstream/ep01_pl/pages/p2-5.txt; echo
echo "== p2-5 EN tail"; tail -c 500 ~/c-workstream/ep01_en/pages/p2-5.txt; echo
echo "== c_prep_ep_pages?"; ls ~/c-workstream | grep -i prep; ls ~/work/tts | head
