"""Panes on the left (owner 10-03 on the third sample: "还是乱"): the terminal is split into named panes, each a
thin box with a small English label at its top-left and, while what it holds is running, a braille spinner at its
top-right. One look for everything on the left, so the picture stops reading as a pile:

  - a pane's border is one dot wide; idle it is faint ink, running it is firm ink and its label is bold;
  - the spinner steps on 16th notes (a small event is locked to the grid, pv-change-rate-follows-lyric);
  - colours: ink at three levels (TXT, SUB, FAINT) and her blue for what is hers; nothing else;
  - type: mono for ASCII, YaHei for CJK (hud.tx / b_open.mtx), sizes from SIZE only.

  box(d, rect, label, t, run, ...)   the pane chrome; run = 0..1 (eased in and out by the caller or run_k)
  run_k(t, spans)                    0..1: 1 inside any (t0, t1) of spans, eased over RUN_EASE at both ends
  spinner(d, x, y, t, color)         the braille spinner (drawn as dots, the mono font has no braille)
  Layout                             named rects for a group's panes (lerp between two layouts for a zoom)
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from PIL import ImageDraw
import hud
import tl
from hud import BG, INK, lv
from tuikit import ease
P = tl.p
TXT, SUB, FAINT = (1.0, 0.62, 0.38)
SIZE = dict(label=12, id=10, body=14, word=20, out=30, big=96)
LINE_IDLE, LINE_RUN = (0.3, 0.85)
RUN_EASE = 0.12
SPIN = [(1, 2, 4), (1, 4, 5), (1, 4, 5, 6), (4, 5, 6), (3, 4, 5, 6), (3, 5, 6), (2, 3, 6), (1, 2, 3, 6), (1, 2, 3), (1, 2, 3, 4)]
_DOT = {1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (1, 0), 5: (1, 1), 6: (1, 2)}

def spinner(d, x, y, t, color, pitch=4, r=1):
    """Braille spinner with its top-left dot at (x, y); one frame per 16th note."""
    k = int(tl.C.beat_of(t) * 4) % len(SPIN)
    for n in SPIN[k]:
        cx, cy = _DOT[n]
        px, py = (x + cx * pitch, y + cy * pitch)
        d.rectangle((px, py, px + r, py + r), fill=color)

def run_k(t, spans, ease_s=RUN_EASE):
    k = 0.0
    for a, b in spans:
        if a - ease_s <= t < b + ease_s:
            k = max(k, ease.prog(t, a - ease_s, a) * (1 - ease.prog(t, b, b + ease_s)))
    return k

def box(d, rect, label, t, run=0.0, level=1.0, status='', status_her=False):
    """The pane chrome: border, label (top-left, on the border), spinner and status (top-right, on the border)."""
    if level <= 0.01:
        return
    x0, y0, x1, y1 = (round(v) for v in rect)
    line = lv(INK, (LINE_IDLE + (LINE_RUN - LINE_IDLE) * run) * level)
    d.rectangle((x0, y0, x1, y1), outline=line)
    f = P.font(SIZE['label'], 'bold' if run > 0.5 else 'mono')
    tw = d.textlength(label, font=f)
    d.rectangle((x0 + 7, y0 - 1, x0 + 15 + tw, y0 + 1), fill=BG)
    d.text((x0 + 11, y0 - 7), label, font=f, fill=lv(INK, (0.55 + 0.45 * run) * level))
    right = x1 - 8
    if run > 0.01:
        d.rectangle((right - 12, y0 - 1, right + 3, y0 + 1), fill=BG)
        spinner(d, right - 9, y0 - 4, t, lv(INK, run * level))
        right -= 16
    if status:
        sw = hud.width(status, 11)
        d.rectangle((right - sw - 5, y0 - 1, right + 1, y0 + 1), fill=BG)
        hud.tx(d, (right - sw - 2, y0 - 7), status, 11, lv(hud.HER_QUIET if status_her else INK, SUB * level))

def lerp_rect(a, b, u):
    return tuple((ease.lerp(p, q, u) for p, q in zip(a, b)))

def inner(rect, pad=10, top=12):
    """Content area of a pane: inside the border, below the label."""
    x0, y0, x1, y1 = rect
    return (x0 + pad, y0 + top, x1 - pad, y1 - 6)

class Clip:
    """Draw a pane's content on its own layer and paste it back cropped to the pane (nothing spills over a
    neighbour). Usage: with Clip(img, rect) as d: ...  (d draws in full-frame coordinates)."""

    def __init__(self, img, rect):
        self.img, self.rect = (img, tuple((int(round(v)) for v in rect)))

    def __enter__(self):
        self.layer = self.img.copy()
        return ImageDraw.Draw(self.layer)

    def __exit__(self, *exc):
        x0, y0, x1, y1 = self.rect
        box = (x0 + 1, y0 + 2, x1, y1)
        self.img.paste(self.layer.crop(box), box[:2])
        return False
