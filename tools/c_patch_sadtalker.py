"""c_patch_sadtalker.py - one-line compatibility patch for SadTalker on current numpy (Assets copy only). Workstream C, 2026-11-12.
Usage: python c_patch_sadtalker.py [SadTalker dir]     (default D:\\Claude\\Assets\\Diary\\face\\SadTalker)
src/face3d/util/preprocess.py builds np.array([w0, h0, s, t[0], t[1]]) where t[0], t[1] are 1-element arrays; numpy >= 1.24
refuses that ragged array. The patch squeezes them to floats. A backup preprocess.py.orig is kept; the patch asserts the old
line matches exactly once and is a no-op if already applied. Jim approved this edit on 2026-11-12."""
import shutil, sys
from pathlib import Path
d = Path(sys.argv[1] if len(sys.argv) > 1 else r"D:\Claude\Assets\Diary\face\SadTalker")
p = d / "src" / "face3d" / "util" / "preprocess.py"
old = "trans_params = np.array([w0, h0, s, t[0], t[1]])"
new = "trans_params = np.array([w0, h0, float(np.squeeze(s)), float(np.squeeze(t[0])), float(np.squeeze(t[1]))])  # c-patch"
t = p.read_text(encoding="utf-8")
if "# c-patch" in t: print("already patched"); sys.exit(0)
assert t.count(old) == 1, f"expected exactly one match, got {t.count(old)}"
shutil.copy2(p, p.with_suffix(".py.orig")); p.write_text(t.replace(old, new), encoding="utf-8", newline="")
print("patched", p)
