# Manual sentence splits in EN narration text (2026-11-14)
XTTS EN limit is 250 chars per sentence; these three sentences exceeded it. Punctuation-only splits (comma -> period, next word capitalised); source text and captions unchanged. Jim to confirm or re-split.
- Ep3 p2-33: "...took me along with him to a café. And since I was too embarrassed to admit..."
- Ep4 p2-48: "...headed to a concentration camp. And that our pay would be issued, only we should conduct ourselves in soldierly fashion."
- Ep4 p2-50: "...sitting on the sand. When suddenly a French NCO came up with a camera and, without saying anything to them, wanted to photograph them, ..."
Lesson: run the real splitter check (pipeline/check_split.py on brokkr) before queueing; lint LONG flags use a different splitter.
