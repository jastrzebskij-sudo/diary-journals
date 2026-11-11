"""c_tts_commas_ep01.py - add pacing commas to the Episode-1 page-1 NARRATION copy (originals untouched). Workstream C, 2026-11-11.
Usage: python c_tts_commas_ep01.py IN.txt OUT.txt
Every replacement is hand-written and must match exactly once (assert), like tts_prep_pl.py. Only commas are inserted; the
diary's own spellings (bendąc, ewakułując, sprzęd, Bataljon) are kept. Writes OUT.txt and OUT.txt.manifest.txt."""
import datetime, sys
from pathlib import Path
R = [
 ("Onego historycznego dnia bendąc na Forcie Wola po prowiant byłem", "Onego historycznego dnia, bendąc na Forcie Wola po prowiant, byłem"),
 ("Po nalocie który miał miejsce około godziny piętnastej jeszcze dużo ludzi nie wierzyło że to wojna.", "Po nalocie, który miał miejsce około godziny piętnastej, jeszcze dużo ludzi nie wierzyło, że to wojna."),
 ("opuszczam Warszawę ewakułując", "opuszczam Warszawę, ewakułując"),
 ("Jedziemy bez świateł na szczęście", "Jedziemy bez świateł, na szczęście"),
 ("w zupełnym porządku jadąc wałem Wisły lecz gdy wydostała się na szosę Warszawa Lublin na której panował ogromny tłok kolumna się rozleciała.",
  "w zupełnym porządku, jadąc wałem Wisły, lecz gdy wydostała się na szosę Warszawa Lublin, na której panował ogromny tłok, kolumna się rozleciała."),
 ("z naszej kolumny lecz nie było", "z naszej kolumny, lecz nie było"),
]
t = Path(sys.argv[1]).read_text(encoding="utf-8")
for o, n in R:
    assert t.count(o) == 1, f"must match exactly once: {o!r} ({t.count(o)})"
    t = t.replace(o, n)
Path(sys.argv[2]).write_text(t, encoding="utf-8", newline="\n")
Path(sys.argv[2] + ".manifest.txt").write_text(f"c_tts_commas_ep01.py {datetime.datetime.now().isoformat(timespec='seconds')} in={sys.argv[1]} replacements={len(R)}\n")
print("ok,", len(R), "replacements")
