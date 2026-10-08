"""Helpers every group uses to add shots with the terminal skeleton."""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from functools import lru_cache
from PIL import ImageDraw
import hud
import tl

def add(film, name, t0, t1, body, title='you@surface · dsh inspect'):
    """A terminal shot: paper background, the terminal frame with `title` (str or fn(t) -> str), then
    body(c, img, d) draws the rest (content, hud.strip, hud.layers, hud.fine_print)."""

    def fn(c):
        img = film.background(c.t)
        d = ImageDraw.Draw(img)
        hud.frame(d, hud.left_rect(c.t), title(c.t) if callable(title) else title)
        body(c, img, d)
        c.img.paste(img)
    return film.add(name, t0, t1, fn, chapter=tl.chapter(t0))

def skeleton(d, t, hits=None, mode='closed', segs=(), tokens=None, right=None, level=1.0, merged=None):
    """Strip + forward layers + fine print in one call."""
    hud.strip(d, t, hits, merged=merged)
    hud.layers(d, t, segs, mode, right, level)
    hud.fine_print(d, t, tokens, level=level)

def placeholder(film, g, cmd, mode='idle'):
    """A group not built yet: the skeleton and the command, so the whole film plays at speed (BATCHES.md)."""
    t0, t1 = tl.span(g)

    def body(c, img, d):
        hud.cmdline(d, c.t, cmd)
        hud.tx(d, (hud.X0, 260), f'[ {g} ]', 40, hud.lv(hud.INK, 0.25), True)
        skeleton(d, c.t, mode=mode)
    add(film, f'{g.lower()}_todo', t0, t1, body)

def full_frame(t_out, t_back, slide_out=0.3, slide_back=0.4):
    """D2 (break the layout): from t_out the dsh window slides off to the right in slide_out s and the
    terminal frame widens to the whole width; from t_back both return in slide_back s. Put t_out on a stop
    or a phrase and t_back on a downbeat (R8, R9). Inside the span draw with hud.xr(t) as the right edge."""
    hud.FULL.append((float(t_out), float(t_back), float(slide_out), float(slide_back)))

@lru_cache(maxsize=64)
def _size_for(text, height, bold):
    """Font size whose ink for `text` is at least `height` px tall (measured, not guessed)."""
    size = height
    for _ in range(6):
        f = hud.font(size, text, bold)
        x0, y0, x1, y1 = f.getbbox(text)
        h = y1 - y0
        if h >= height:
            break
        size = int(size * height / max(1, h)) + 1
    return size

def big_word(d, text, xy, height=200, fill=hud.INK, anchor='ra', bold=True, bump=1.0, halo=0):
    """D3 (a word that fills the frame): `text` with ink at least `height` px tall (>= 180 at 720 p,
    10_aesthetics §13.3), its ink box anchored at xy ("ra": right/top, "la": left/top; "rd"/"ld": the bottom,
    so a landing overshoot grows up and away from what is under the word, r5c R02). Returns the ink box.
    It lands on its syllable and stays; bump > 1 for the landing overshoot. halo (px): a paper outline drawn
    first, so what the word lands on keeps that much paper between it and the ink (R-C, r5b)."""
    size = int(_size_for(text, height, bold) * bump)
    f = hud.font(size, text, bold)
    x0, y0, x1, y1 = f.getbbox(text)
    x, y = xy
    ox = x - x1 if anchor[0] == 'r' else x - x0
    oy = y - y1 if anchor[1] == 'd' else y - y0
    if halo > 0:
        d.text((ox, oy), text, font=f, fill=hud.BG, stroke_width=int(halo), stroke_fill=hud.BG)
    d.text((ox, oy), text, font=f, fill=fill)
    return (ox + x0, oy + y0, ox + x1, oy + y1)
