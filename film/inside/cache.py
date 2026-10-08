"""Render the inside plates ahead of the film (BUILD_V2_20261003.md §4): cache/inside/<shot>/<frame>.png.

  python -m inside.cache                 every span, missing frames only
  python -m inside.cache c2_arcs b9_tower --force --workers 14
  python -m inside.cache --list

The three-dimensional plates take seconds a frame, so they are rendered here in parallel, never inside tuikit's
chunked film render (one slow chunk would hold the whole render up). Each worker builds the span it renders
(the 3D modules are patched to one plate size per process).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import argparse
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(PV_ROOT / 'runtime')):
    if p not in sys.path:
        sys.path.insert(0, p)
_SPAN = None

def _init(name):
    global _SPAN
    from inside import shots
    _SPAN = next((s for s in shots.spans() if s.name == name))
    _SPAN.renderer()

def _one(n):
    from PIL import Image
    f = _SPAN.path(n)
    arr = _SPAN.renderer().render(n / 24)
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix('.tmp.png')
    Image.fromarray(arr).save(tmp)
    os.replace(tmp, f)
    return n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names', nargs='*')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--workers', type=int, default=14)
    ap.add_argument('--list', action='store_true')
    a = ap.parse_args()
    from inside import shots
    spans = shots.spans()
    if a.list:
        for s in spans:
            fr = s.frames()
            have = sum((1 for n in fr if s.path(n).exists()))
            print(f'{s.name:10s} {s.t_in:8.3f}-{s.end:8.3f}  {len(fr):4d} frames  cached {have}')
        return
    todo = [s for s in spans if not a.names or s.name in a.names]
    for s in todo:
        frames = [n for n in s.frames() if a.force or not s.path(n).exists()]
        if not frames:
            print(f'{s.name}: cached')
            continue
        t0 = time.time()
        with Pool(min(a.workers, len(frames)), initializer=_init, initargs=(s.name,)) as pool:
            for _ in pool.imap_unordered(_one, frames, chunksize=2):
                pass
        print(f'{s.name}: {len(frames)} frames in {time.time() - t0:.1f} s', flush=True)
if __name__ == '__main__':
    main()
