"""Batch 3 (sample_lead/README.md, sample_batch3/README.md): one pane leads a beat, the others step back.
r5 round 2, D11 (REVISE_R4_20261004.md §5.1 first row, §6 D11; sample_r5/README.md §4 2-X): stepping back lowers
the contrast of a pane's content only; its ground stays paper.

r4 shaded a pane that does not lead as a block: ground and content both went toward one darker paper tone
(paper x 0.86, film.py support_sink), and the dsh window as the support side was greyed and darkened by film.py's
dim_paper. The frame turned grey and the dsh window's white was gone (bright-white share of the right column,
r3 -> r4: B 42 % -> 11 %, D 51 % -> 2 %). D11: a pane that steps back keeps its paper; its ink and lines go toward
the paper, full ink landing between SUB and FAINT (MIX). The pane that leads keeps full ink, its frame running
(panes.box) and its label bold, so the one dark place on the left is the leader (owner D13: light text on paper is
pale with no focal point; pv-not-ppt: on paper, weight comes from solid ink).

  shade(img, rect, k, inset)   k = 0 (leads) .. 1 (steps back); the pane's frame and label are drawn after it
  weights(t, table, names, ease_s)   {name: 0..1 lead weight} from a [(t0, name), ...] lead table
  support(img, rect, k)        the dsh window as the support side, D11: her blue greyed as film.dim_paper did
                               (D1: one lit place), its content toward its own white; the white stays white
  install(film)                film.py's support dimming, D11, for the frames whose panes go through shade():
                               the window by support(), and the left is not dimmed a second time over shade()
                               (sample_batch3/README.md §5 item 3). Other frames keep film.py's dim_paper as is.

TONE and MIX keep their meaning for the overlays drawn over a shaded pane (groups/b_lead.py `_shaded`:
glyph.mix(colour, TONE, MIX * k)). Constants are shared by every group that steps panes back (B, C, D, G): change
them here, not in a group.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import numpy as np
from PIL import Image, ImageOps
from hud import BG, INK
from tuikit import ease
SINK = 0.86
TONE = BG
MIX = 0.45
EASE = 0.16
GAIN = 0.32
GAIN_TOP = 8
SUPPORT_GREY = 0.55
SUPPORT_LIFT = 0.4
WHITE = (255, 255, 255)
_SEEN: list = []
_FR = {'img': None, 'panes': []}
_BG = np.array(BG, np.float32)
_INK = np.array(INK, np.float32)

def _deepen(img, box, g):
    """The pane that leads gets heavier (D11): its ink and lines away from the paper by g (>= 1), never past INK;
    her blue and the other saturated colours stay as they are."""
    region = img.crop(box)
    a = np.asarray(region, np.float32)
    sat = (a.max(axis=2) - a.min(axis=2))[..., None] / 255.0
    keep = np.clip((sat - 0.12) * 5.0, 0.0, 1.0)
    deep = np.clip(_BG + (a - _BG) * g, _INK, 255.0)
    out = deep * (1 - keep) + a * keep
    img.paste(Image.fromarray(np.clip(np.rint(out), 0, 255).astype(np.uint8)), box[:2])

def _lead_gain(img, rect, k):
    """Record the pane; every pane shaded so far on this image gets ink x (1 + GAIN * (1 - its k) * the largest k
    of the others): the leader is heavier exactly as much as the others step back (all lit: no change, so the
    seams with unshaded groups do not move). A pane shaded before a later one stepped back is deepened then."""
    if _FR['img'] is not img:
        _FR['img'], _FR['panes'] = (img, [])
    x0, y0, x1, y1 = (int(round(v)) for v in rect)
    box = (x0 + 1, y0 + GAIN_TOP, x1, y1)
    panes_ = _FR['panes']
    panes_.append([box, min(1.0, max(0.0, k)), 1.0])
    for i, p in enumerate(panes_):
        others = max((q[1] for j, q in enumerate(panes_) if j != i), default=0.0)
        g = 1.0 + GAIN * (1.0 - p[1]) * others
        if g > p[2] + 0.01 and p[0][2] > p[0][0] and (p[0][3] > p[0][1]):
            _deepen(img, p[0], g / p[2])
            p[2] = g

def shade(img: Image.Image, rect, k: float, inset=(1, 2, 1, 1)) -> None:
    """Step the inside of rect back by k (0..1): its content mixed toward the paper (TONE) by MIX * k; the paper
    ground stays as it is. The pane that leads (k ~ 0) is deepened by _lead_gain as the others step back."""
    _SEEN.append(k)
    if k > 0.003:
        x0, y0, x1, y1 = (int(round(v)) for v in rect)
        box = (x0 + inset[0], y0 + inset[1], x1 - inset[2] + 1, y1 - inset[3] + 1)
        if box[2] > box[0] and box[3] > box[1]:
            region = img.crop(box)
            img.paste(Image.blend(region, Image.new('RGB', region.size, TONE), MIX * min(1.0, k)), box[:2])
    _lead_gain(img, rect, k)

def support_rgb(region: Image.Image, k: float) -> Image.Image:
    """D11 on an RGB image of the dsh window: greyer (film.dim_paper's blend), its content toward white."""
    k = min(1.0, max(0.0, k))
    if k <= 0.003:
        return region
    grey = ImageOps.grayscale(region).convert('RGB')
    region = Image.blend(region, grey, SUPPORT_GREY * k)
    return Image.blend(region, Image.new('RGB', region.size, WHITE), SUPPORT_LIFT * k)

def support(img: Image.Image, rect, k: float) -> None:
    """The dsh window in rect as the support side (D11), in place."""
    if k <= 0.003:
        return
    box = tuple((int(round(v)) for v in rect))
    img.paste(support_rgb(img.crop(box), k), box[:2])

def install(film):
    """D11 for film.py's support dimming (film._dim). In a frame whose panes went through shade() the left is
    not dimmed again (its panes already stepped back) and the dsh window is dimmed by support(); every other frame
    (A, E, F, H) keeps film.py's dim_paper. Call once in film.build, after film._dim is set."""
    base_dim, base_frame = (film._dim, film.frame)
    s_lv = film.p.setting('support_level', 0.42)

    def frame(n, *a, **kw):
        _SEEN.clear()
        return base_frame(n, *a, **kw)

    def dim(img, levels):
        if not _SEEN:
            return base_dim(img, levels)
        _SEEN.clear()
        for region, level in levels.items():
            rect = film.lead_regions.get(region)
            if rect is None or level >= 0.999 or region != 'right':
                continue
            support(img, rect, min(1.0, (1 - level) / (1 - s_lv)))
        return img
    film._dim, film.frame = (dim, frame)
    return film

def weights(t: float, table, names, ease_s: float=EASE) -> dict:
    """{name: 0..1}: 1 for the pane that leads at t by `table` ([(t0, name), ...], sorted), eased over ease_s
    from the previous leader. Before the first entry every pane is 1 (nothing is shaded)."""
    if not table or t < table[0][0]:
        return {n: 1.0 for n in names}
    k = max((i for i, (t0, _n) in enumerate(table) if t >= t0))
    t0, cur = table[k]
    u = ease.smooth(ease.prog(t, t0, t0 + ease_s))
    if k == 0:
        return {n: 1.0 if cur == n else 1 - u for n in names}
    prev = table[k - 1][1]
    return {n: (cur == n) * u + (prev == n) * (1 - u) for n in names}
