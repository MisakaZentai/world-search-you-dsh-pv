"""dsh pane, interlude 3 for r17 (D59, sample_r17/README.md): ui/pages/i5_g.py unchanged, shot again with the merged
one's name from cast.py (run with DSH_END=story: 大肥鱼, not deepseek-v5-flash-preview) and its composer stats reading
`cloud API` (as the cloud stand-ins' pages do, pages/b.py) instead of `preview API`. Nothing else differs.

  DSH_END=story PYTHONUTF8=1 python ui/pages/i5_g_r17.py   -> ui/frames_I5_g_r17.json (out_dir pane_i5_g_r17), then
  node <local-production-path> ui/frames_I5_g_r17.json
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import os
import sys
from pathlib import Path
if __name__ == '__main__':
    sys.path[:0] = [str(Path(__file__).resolve().parent.parent), str(Path(__file__).resolve().parents[2])]
from pages import i5_g as PI

def body(t: float) -> str:
    return PI.body(t).replace('preview API', 'cloud API')
if __name__ == '__main__':
    assert os.environ.get('DSH_END') == 'story', "run with DSH_END=story (the merged one's name)"
    import tl
    from inside import i5_times as I5
    from tuikit.uipane import write_frames
    sys.stdout.reconfigure(encoding='utf-8')
    x0, y0, x1, y1 = tl.p.rect('pane')
    ui = Path(__file__).resolve().parent.parent
    n = write_frames(ui / 'frames_I5_g_r17.json', I5.G5, I5.FOUND, tl.p.FPS, body, page='host.html', viewport=(x1 - x0, y1 - y0), out_dir='pane_i5_g_r17')
    print(f'I5 G (r17): {n} frames -> frames_I5_g_r17.json')
