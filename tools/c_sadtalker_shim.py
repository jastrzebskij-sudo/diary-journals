"""c_sadtalker_shim.py - run SadTalker's inference.py with a compatibility shim.
basicsr (a SadTalker dependency) imports torchvision.transforms.functional_tensor, which new torchvision removed.
This wrapper registers a stand-in module in memory (no third-party file is edited), plus the removed numpy aliases (np.float etc.), then runs inference.py.
Usage: python c_sadtalker_shim.py <SadTalker dir> [inference.py args...]   Workstream C, 2026-11-11."""
import os, runpy, sys, types
import torchvision.transforms.functional as F
m = types.ModuleType("torchvision.transforms.functional_tensor")
m.rgb_to_grayscale = F.rgb_to_grayscale
sys.modules[m.__name__] = m
import numpy as np
for _n, _t in (("float", float), ("int", int), ("bool", bool), ("object", object), ("complex", complex)):
    if not hasattr(np, _n):
        setattr(np, _n, _t)  # removed numpy aliases still used by SadTalker
d = sys.argv[1]; os.chdir(d); sys.path.insert(0, d)
sys.argv = [os.path.join(d, "inference.py")] + sys.argv[2:]
runpy.run_path(sys.argv[0], run_name="__main__")
