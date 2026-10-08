"""The terminal's skeleton, on screen the whole film (PLAN_FULL.md §3), and the drawing helpers every group
shares. Everything here is a pure function of song time t.

Skeleton:
  frame(...)         the terminal pane: firm ink outline, a title chip naming the running process
  cmdline(...)       `$ command` at the top, the persona's model as an inverse chip on the right
  strip(d, t, hits)  the ownership strip of ~/memory/you/ at the far left (her files blue, stand-ins'
                     files hatched); `hits` = {block index | "archive": 0..1} from Pulse
  layers(d, t, ...)  the forward-pass strip: crawls only while a local model computes (R11)
  fine_print(...)    sim(her) · speed · where · tokens

Layout (1280 x 720 design pixels, PROJECT.yaml): the terminal text column starts at X0 and ends at XR;
content goes between Y_TOP and Y_BOTTOM; the strip owns the column x 24..92.
Colour (R2): ink for the stand-ins and for you, her blue the one signal colour, solid slab for weight.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import re
from PIL import Image, ImageDraw
import cast
import tl
from tuikit import ease, glyph
p = tl.p
BG, INK, SLAB, DIM, HER = (p.color(k) for k in ('bg', 'ink', 'slab', 'dim', 'her'))
ERR = p.color('error')
LEFT, TERM, COLR, RIGHT = (p.rect('left'), p.rect('term'), p.rect('column'), p.rect('right'))
COLR = (COLR[0] + 7, COLR[1], COLR[2] + 7, COLR[3])
X0 = TERM[0] + 24
XR = TERM[2] - 16
Y_CMD, Y_TOP, Y_BOTTOM, Y_LAYERS, Y_FINE = (64, 92, 528, 548, 570)
CJK = re.compile('[⺀-鿿\u3000-〿\uff00-\uffef]')
DEEP: list = []
HER_LIVE = HER
HER_QUIET = glyph.mix(HER, (115, 115, 115), 0.55)
LIVE: list = []
LIVE_FADE = 0.3
FULL: list = []
FULL_RECT = (p.rect('left')[0], p.rect('left')[1], p.rect('right')[2], p.rect('left')[3])

def lv(c, a, bg=BG):
    return glyph.level(c, a, bg)

def live_k(t: float) -> float:
    """D1: 1 while something of hers is landing, settling to 0 over LIVE_FADE after it."""
    k = 0.0
    for a, b in LIVE:
        if a <= t < b:
            return 1.0
        if b <= t < b + LIVE_FADE:
            k = max(k, 1 - ease.prog(t, b, b + LIVE_FADE))
    return k

def her(u: float=0.0, level: float=1.0):
    """D1: her colour, u = 1 lit (landing now) .. 0 quiet."""
    return lv(glyph.mix(HER_QUIET, HER_LIVE, ease.clamp(u)), level)

def full_u(t: float, min_out: float=0.0) -> float:
    """D2: 0 = the usual split, 1 = the terminal fills the frame (slide out ease-out, back ease-in-out).
    min_out: stretch the way out to at least this long (the LEAD brightening keeps R8's 0.5 s)."""
    u = 0.0
    for a, b, d_out, d_back in FULL:
        d_out = max(d_out, min_out)
        if a <= t < b + d_back:
            u = max(u, ease.ease_out(ease.prog(t, a, a + d_out)) * (1 - ease.ease_io(ease.prog(t, b, b + d_back))))
    return u

def left_rect(t: float):
    """D2: the terminal frame at t (LEFT, widened toward FULL_RECT)."""
    u = full_u(t)
    return LEFT if u <= 0 else tuple((int(round(ease.lerp(a, b, u))) for a, b in zip(LEFT, FULL_RECT)))

def xr(t: float) -> float:
    """D2: right edge of the terminal's text column at t (XR, or 1240 when the terminal fills the frame)."""
    return ease.lerp(XR, FULL_RECT[2] - 16, full_u(t))

def pane_dx(t: float) -> int:
    """D2: how far the dsh window is pushed right (off screen at full_u = 1)."""
    return int(round(full_u(t) * (p.W - RIGHT[0] + 16)))

def font(size: int, s: str='', bold: bool=False):
    if CJK.search(s):
        return p.font(size, 'font_cjk_bold' if bold else 'cjk')
    return p.font(size, 'bold' if bold else 'mono')

def tx(d, xy, s, size, fill, bold=False, anchor='la'):
    """Text in the right face for its script (mono for ASCII, YaHei for CJK); returns its width."""
    f = font(size, s, bold)
    d.text(xy, s, font=f, fill=fill, anchor=anchor)
    return d.textlength(s, font=f)

def tlen(d, s, size, bold=False):
    return d.textlength(s, font=font(size, s, bold))
_MEASURE = ImageDraw.Draw(Image.new('RGB', (1, 1)))

def width(s, size, bold=False):
    return _MEASURE.textlength(s, font=font(size, s, bold))

def pix(d, pattern, x, y, cell, colors):
    """A low-precision pixel picture: pattern rows of characters, colors = {char: rgb}."""
    for j, row in enumerate(pattern):
        for i, ch in enumerate(row):
            if ch in colors:
                d.rectangle((x + i * cell, y + j * cell, x + (i + 1) * cell - 1, y + (j + 1) * cell - 1), fill=colors[ch])

def hatch(d, rect, color, step=5, width=1):
    x0, y0, x1, y1 = (int(v) for v in rect)
    for k in range(x0 - (y1 - y0), x1, step):
        a = (max(k, x0), y0 + max(0, x0 - k))
        b = (min(k + (y1 - y0), x1), y0 + min(y1 - y0, x1 - k))
        if a[0] <= b[0]:
            d.line([a, b], fill=color, width=width)

def frame(d, rect, title=None, size=13, level=1.0, ink=INK, bg=BG):
    """A paper-side pane: a firm ink outline, corner ticks and a title chip."""
    x0, y0, x1, y1 = rect
    d.rectangle(rect, outline=glyph.level(ink, 0.62 * level, bg))
    for cx, cy, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(cx, cy), (cx + 8 * sx, cy)], fill=glyph.level(ink, level, bg), width=2)
        d.line([(cx, cy), (cx, cy + 8 * sy)], fill=glyph.level(ink, level, bg), width=2)
    if title:
        f = font(size, title)
        tw = d.textlength(title, font=f)
        d.rectangle((x0 + 12, y0 - 7, x0 + 22 + tw, y0 + 7), fill=bg)
        d.text((x0 + 17, y0 - 8 if CJK.search(title) else y0 - 7), title, font=f, fill=glyph.level(ink, level, bg))

def leader(d, x_from, y_from, target, color, u=1.0, lane=110, width=2):
    """Elbow leader from a point in the terminal to a strip block (diagram style, not a curve)."""
    bx0, by0, bx1, by1 = target
    ty = (by0 + by1) / 2
    pts = [(x_from, y_from), (lane, y_from), (lane, ty), (bx1 + 2, ty)]
    polyline(d, pts, color, u, width)
    if u >= 1:
        d.rectangle((bx1 - 1, ty - 3, bx1 + 5, ty + 3), fill=color)

def polyline(d, pts, color, u=1.0, width=2):
    """Draw the first u (0..1, eased out) of a polyline's length."""
    segs = list(zip(pts, pts[1:]))
    lens = [abs(a[0] - b[0]) + abs(a[1] - b[1]) for a, b in segs]
    left = sum(lens) * ease.ease_out(ease.clamp(u))
    for (a, b), ln in zip(segs, lens):
        if left <= 0:
            break
        k = min(1.0, left / ln) if ln else 1.0
        d.line([a, (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)], fill=color, width=width)
        left -= ln

class Pulse:
    """Collects read pulses for the strip: hit(key, at, half) -> {key: 0..1}."""

    def __init__(self, t):
        self.t, self.out = (t, {})

    def hit(self, key, at, half=0.14):
        if self.t >= at:
            v = math.exp(-(self.t - at) / half)
            if v > 0.01:
                self.out[key] = max(self.out.get(key, 0.0), v)
        return self
STRIP_TOP = COLR[1] + 40
STRIP_ROOM = 380

def strip_files(t):
    """[(name, owner, born)] in ~/memory/you/ at t (born = -1 for her 8)."""
    return [(n, 'her', -1.0) for n in tl.HER_FILES] + [(n, o, tw) for tw, n, o in tl.WRITES if t >= tw]

def _pitch(t):
    n = 8.0 + sum((ease.ease_io(ease.prog(t, tw, tw + 0.3)) for tw, _n, _o in tl.WRITES))
    return min(30.0, STRIP_ROOM / n)

def block_rect(k, t=None):
    """Block k of the strip at t (pitch shrinks as files are added, eased over 0.3 s)."""
    x0, _y0, x1, _ = COLR
    pitch = 30.0 if t is None else _pitch(t)
    h = max(3.0, pitch - 4)
    y = STRIP_TOP + k * pitch
    return (x0, y, x1, y + h)

def archive_rect(t):
    x0, _y0, x1, _ = COLR
    n = len(strip_files(t))
    y = STRIP_TOP + n * _pitch(t) + 10
    return (x0, y, x1, y + 44)

def chip(d, name, width, font=None):
    """A file block's label: name[:9], cut further so it keeps 4 px left and at least 3 px right of a block
    `width` px wide (R-C, sample_r5/README.md: the narrow pane column put 'first_hel' 1 px from the edge)."""
    font = font or p.font(11)
    s = name[:9]
    while s and d.textlength(s, font=font) > width - 7:
        s = s[:-1]
    return s

def strip(d, t, hits=None, level=1.0, merged=None, bare=()):
    """The ownership strip. merged: 0..1 (F4), the blocks gather into one 'merged' block. bare: names whose block
    is drawn without its label (r5c R01: B's fold, while that file's bubble still carries the name in)."""
    hits = hits or {}
    x0, y0, x1, _y1 = COLR
    L = lambda c, a=1.0: glyph.level(c, a * level, BG)
    d.text((x0, y0 + 6), 'memory/', font=p.font(11), fill=L(INK, 0.8))
    d.text((x0, y0 + 19), 'you/', font=p.font(11), fill=L(INK, 0.8))
    files = strip_files(t)
    pitch = _pitch(t)
    m = ease.ease_io(ease.clamp(merged or 0.0))
    for k, (name, owner, born) in enumerate(files):
        bx0, by0, bx1, by1 = block_rect(k, t)
        if m > 0:
            by0 = ease.lerp(by0, STRIP_TOP, m)
            by1 = ease.lerp(by1, STRIP_TOP + 60, m)
        u = ease.ease_back(ease.prog(t, born, born + 0.25)) if born > 0 else 1.0
        by1 = by0 + max(1, (by1 - by0) * u)
        r = hits.get(k, 0.0)
        names = by1 - by0 > 14 and m < 0.3 and (name not in bare)
        if owner == 'her':
            dx = 5 * r
            d.rectangle((bx0 + dx, by0, bx1 + dx, by1), fill=L(HER_QUIET))
            if r > 0.05:
                d.rectangle((bx0 + dx - 2, by0 - 2, bx1 + dx + 2, by1 + 2), outline=L(INK, r), width=2)
            if names:
                d.text((bx0 + 4 + dx, by0 + 6), chip(d, name, bx1 - bx0), font=p.font(11), fill=BG)
        else:
            dx = 5 * r
            d.rectangle((bx0 + dx, by0, bx1 + dx, by1), fill=BG, outline=L(INK), width=2 if pitch > 12 else 1)
            hatch(d, (bx0 + dx + 2, by0 + 2, bx1 + dx - 2, by1 - 2), L(INK, 0.45), 4)
            if r > 0.05:
                d.rectangle((bx0 + dx - 2, by0 - 2, bx1 + dx + 2, by1 + 2), outline=L(INK, r), width=2)
            if names:
                lab = chip(d, name, bx1 - bx0)
                tw = d.textlength(lab, font=p.font(11))
                d.rectangle((bx0 + dx + 3, by0 + 6, bx0 + dx + 5 + tw, by0 + 19), fill=BG)
                d.text((bx0 + dx + 4, by0 + 6), lab, font=p.font(11), fill=L(INK))
    if m > 0.6:
        a = ease.prog(m, 0.6, 1.0)
        d.rectangle((x0, STRIP_TOP, x1, STRIP_TOP + 60), fill=L(HER_QUIET, a), outline=L(INK, a), width=2)
        hatch(d, (x0 + 2, STRIP_TOP + 2, x1 - 2, STRIP_TOP + 58), L(BG, 0.7 * a) if a else BG, 4, 2)
        tw = d.textlength('merged', font=p.font(11))
        d.rectangle((x0 + 3, STRIP_TOP + 6, x0 + 5 + tw, STRIP_TOP + 19), fill=BG)
        d.text((x0 + 4, STRIP_TOP + 6), 'merged', font=p.font(11), fill=L(INK, a))
    ax0, ay0, ax1, ay1 = archive_rect(t) if m <= 0 else (x0, STRIP_TOP + 74, x1, STRIP_TOP + 118)
    r = hits.get('archive', 0.0)
    q = HER_QUIET
    d.rectangle((ax0, ay0, ax1, ay1), fill=L(lv(q, 0.16 + 0.5 * r)), outline=L(q), width=2)
    hatch(d, (ax0 + 2, ay0 + 2, ax1 - 2, ay1 - 2), L(lv(q, 0.55 + 0.45 * r)), 5)
    d.rectangle((ax0 + 3, ay0 + 5, ax0 + 52, ay0 + 18), fill=BG)
    d.text((ax0 + 4, ay0 + 5), 'archive', font=p.font(11), fill=L(q))
    d.rectangle((ax0 + 3, ay0 + 23, ax0 + 46, ay0 + 36), fill=BG)
    d.text((ax0 + 4, ay0 + 23), '412 行', font=p.font(11, 'cjk'), fill=L(q))
    if t >= tl.QMARK_AT:
        big, small = ('?', '')
    elif t >= tl.MERGED_AT:
        big, small = ('merged', '')
    else:
        hers, total = tl.files(t)
        big, small = (f'{hers}/{total}', 'by her')
    d.text((x0, ay1 + 12), big, font=p.font(16 if len(big) < 6 else 12, 'bold'), fill=L(HER_QUIET))
    if small:
        d.text((x0, ay1 + 32), small, font=p.font(11), fill=L(HER_QUIET, 0.85))

def cmdline(d, t, cmd, chip=None, chip_t0=None, level=1.0, x=X0):
    """`$ cmd` in the top row; chip = the model name as an inverse chip on the right (None: the persona's
    current model; "" for none). chip_t0: when the chip last changed (it decodes in, R9 cut).
    x (p6): where the command starts (layouts A and C start it at 36, tower.py)."""
    tx(d, (x, Y_CMD), cmd, 13, lv(INK, 0.86 * level))
    if chip is None:
        chip = cast.term(tl.model(t))
    if not chip:
        return
    f = p.font(13, 'bold') if not CJK.search(chip) else font(13, chip, True)
    shown = glyph.decode(chip, t, chip_t0, cps=60) if chip_t0 is not None else chip
    w = d.textlength(chip, font=f)
    xr_ = xr(t)
    d.rectangle((xr_ - w - 12, Y_CMD - 3, xr_, Y_CMD + 17), fill=lv(SLAB, level))
    d.text((xr_ - w - 6, Y_CMD - (1 if CJK.search(chip) else 0)), shown, font=f, fill=BG)

def layers(d, t, segs=(), mode='local', right=None, level=1.0, head=None, done=0.0, cells=1.0):
    """48 layer cells. mode: local (the head walks across while a token is computed, all flash when it is
    sampled; segs = [(start, sampled)]), closed (cloud: grey, 'weights: closed'), idle (no model),
    frozen (paused in an interlude). R11: they move only while a local model computes.
    mode="ruler" (p5, GEN_PLAN §2.2 / 第一轮 README "forward 标尺"): the 48 cells shrink to a 64-tick ruler with
    the five lens layers taller; head = the layer the pass has reached (0..64, None: idle), done = 0..1 the
    sampled flash (see ruler()). cells (p5): 0..1 the cells' own level (labels stay), so the closed cells can fade
    in over the ruler at a model swap (R6)."""
    if mode == 'ruler':
        ruler(d, t, head, done, right if right is not None else f'{cast.LOCAL['quant']} · 本地权重 · 64 layers', level)
        return
    d.text((X0, Y_LAYERS - 15), 'forward', font=p.font(10), fill=lv(INK, 0.6 * level))
    if right is None:
        right = {'local': f'{cast.LOCAL['quant']} · 本地权重', 'closed': 'weights: closed', 'idle': 'no model loaded', 'frozen': 'paused'}.get(mode, '')
    xr_ = xr(t)
    tx(d, (xr_, Y_LAYERS - 15), right, 10, lv(INK, 0.55 * level), anchor='ra')
    n, cw = (48, (xr_ - X0 - 47 * 2) / 48)
    lit, head, flash = (0, -1, 0.0)
    if mode == 'local':
        for a0, b0 in segs:
            if a0 <= t < b0:
                head = int(n * (t - a0) / max(0.001, b0 - a0))
                lit = head
            elif b0 <= t < b0 + 0.25:
                flash = max(flash, 1 - (t - b0) / 0.25)
    for i in range(n):
        x = X0 + i * (cw + 2)
        if mode in ('closed', 'idle'):
            fill, out = (lv(INK, 0.06 * level * cells), lv(INK, 0.22 * level * cells))
        else:
            v = 0.12 + 0.6 * (i < lit) + 0.88 * (i == head)
            v = max(v, 0.12 + 0.8 * flash)
            fill, out = (lv(INK, min(1.0, v) * level * cells), lv(INK, 0.35 * level * cells))
        d.rectangle((x, Y_LAYERS, x + cw, Y_LAYERS + 10), fill=fill, outline=out)

def fine_print(d, t, tokens=None, who=None, level=1.0, x0=X0):
    """sim(her) · speed · where · tokens n/m. who defaults to the persona's model at t.
    x0 (p6): where the row starts (layouts A and C start it at 36, tower.py)."""
    who = who or tl.model(t)
    s = tl.sim(t)
    d.text((x0, Y_FINE), 'sim(her)', font=p.font(12), fill=lv(INK, 0.7 * level))
    d.text((x0 + 70, Y_FINE - 1), s or '—', font=p.font(13, 'bold'), fill=lv(HER_QUIET if s else INK, level))
    x = x0 + 124
    k = cast.kind(who)
    if k == 'local':
        speed = f'{cast.LOCAL['tok_s']:.1f} tok/s'
        d.text((x, Y_FINE - 1), speed, font=p.font(13, 'bold'), fill=lv(INK, level))
        x += d.textlength(speed, font=p.font(13, 'bold')) + 18
        x += tx(d, (x, Y_FINE), cast.LOCAL['where'], 12, lv(INK, 0.7 * level)) + 18
    elif k == 'offline':
        x += tx(d, (x, Y_FINE), 'model offline', 12, lv(INK, 0.7 * level)) + 18
    else:
        x += tx(d, (x, Y_FINE), 'cloud API · logprobs ≈' if k == 'cloud' else 'preview API', 12, lv(INK, 0.7 * level)) + 18
    if tokens:
        d.text((x, Y_FINE), f'tokens {tokens[0]}/{tokens[1]}', font=p.font(12), fill=lv(INK, 0.7 * level))
N_LAYERS = 64
LENS_ROWS = (64, 48, 36, 24, 12)
LENS_X_LABEL, LENS_X0, LENS_Y0 = (522, 530, 192)
LENS_PITCH, LENS_ROW, LENS_FONT = (19, 26, 18)

def ruler(d, t, head=None, done=0.0, right='', level=1.0, y=Y_LAYERS, labels=True):
    """p5 (第一轮 README "forward 标尺"): the forward strip as a ruler of 64 one-pixel ticks, the lens layers
    taller; head = the layer the pass has reached (0..64) or None; done = 0..1 the 'sampled' flash (every tick
    dark, settling back, as the 48 cells' flash did). It rides the frame's right edge (D2). labels=False: the
    ticks only (fading out under the closed cells at a model swap)."""
    if labels:
        d.text((X0, y - 15), 'forward', font=p.font(10), fill=lv(INK, 0.6 * level))
    xr_ = xr(t)
    if right and labels:
        tx(d, (xr_, y - 15), right, 10, lv(INK, 0.55 * level), anchor='ra')
    span_ = xr_ - X0
    for i in range(N_LAYERS):
        x = round(X0 + span_ * (i + 0.5) / N_LAYERS)
        tall = i + 1 in LENS_ROWS
        on = head is not None and i < head
        a = max(0.85 if on else 0.3, 0.3 + 0.55 * done)
        d.line([(x, y + (0 if tall else 5)), (x, y + 10)], fill=lv(INK, a * level))
    if head is not None:
        x = round(X0 + span_ * min(head, N_LAYERS - 0.5) / N_LAYERS)
        d.rectangle((x - 2, y - 2, x + 2, y + 12), fill=lv(INK, level))

def lens_grid(d, cols, x0=LENS_X0, y0=LENS_Y0, pitch=LENS_PITCH, row=LENS_ROW, size=LENS_FONT, level=1.0, computing=None, header='logit lens', label_x=LENS_X_LABEL, frame_level=1.0):
    """p5 (GEN_PLAN §2.2, 字栅): rows are the lens layers 64 .. 12 (top to bottom), one column per sung token.
    cols = [[(text, hers) | None] * 5 (top to bottom)]; None = not reached yet (a dot). computing = the index of
    the column whose pass is running: its filled cells get a hairline frame. Hers in the quiet blue (D1: the
    lens is never the lit place), the stand-in's own in ink; the top row (layer 64 = what lands) bold.
    level dims the whole grid (labels too). Returns the grid's box."""
    n = len(cols)
    x_end = x0 + n * pitch
    if header:
        tx(d, (label_x - 20, y0 - 25), header, 16, lv(INK, 0.6 * level))
    for r, layer in enumerate(LENS_ROWS):
        tx(d, (label_x, y0 + r * row + 2), f'{layer}', 16, lv(INK, 0.55 * level), anchor='ra')
    for r in range(len(LENS_ROWS) - 1):
        yl = y0 + (r + 1) * row - 3
        for x in range(int(x0), int(max(x_end, x0 + 6 * pitch)), 3):
            d.point((x, yl), fill=lv(INK, 0.3 * level))
    for k, col in enumerate(cols):
        cx = x0 + k * pitch + pitch / 2
        for r, cell in enumerate(col):
            cy = y0 + r * row + row / 2 - 2
            if cell is None:
                d.text((cx, cy), '·', font=p.font(16), fill=lv(INK, 0.4 * level), anchor='mm')
                continue
            text, hers = cell
            f = font(size if not text.isascii() else 16, text, r == 0)
            d.text((cx, cy), text, font=f, fill=lv(HER_QUIET if hers else INK, level), anchor='mm')
    if computing is not None and computing < n and (frame_level > 0):
        filled = [r for r, c in enumerate(cols[computing]) if c is not None]
        if filled:
            xa = x0 + computing * pitch
            top = y0 + min(filled) * row - 2
            d.rectangle((xa - 1, top, xa + pitch, y0 + len(LENS_ROWS) * row - 4), outline=lv(INK, 0.75 * level * frame_level))
    return (x0, y0, x_end, y0 + len(LENS_ROWS) * row)

def halo(d, xy, s, size, bold=False, anchor='la', r=3, fill=BG):
    """p5 (第一轮 README "线从字后面过"): a text run's knockout, so lines drawn before it pass under it (drafting
    style). Draw it on a mask (fill=255) to cut a line layer, or on the page with the paper colour."""
    d.text(xy, s, font=font(size, s, bold), fill=fill, anchor=anchor, stroke_width=r, stroke_fill=fill)

def strip_point(k, t, hits=None):
    """p5 (§2.1): where a lookback line lands on her block k: 4 px right of its right edge (which moves with
    the read pulse), at its middle."""
    bx0, by0, bx1, by1 = block_rect(k, t)
    return (round(bx1 + 5 * (hits or {}).get(k, 0.0) + 4), round((by0 + by1) / 2))

def archive_point(t, hits=None):
    """p5 (§2.1): the same on the archive block."""
    ax0, ay0, ax1, ay1 = archive_rect(t)
    return (round(ax1 + 4), round((ay0 + ay1) / 2))

def seg(d, a, b, color, w=1):
    """p5: an axis-aligned segment, w px wide, on whole pixels (a hairline stays one pixel)."""
    (xa, ya), (xb, yb) = (a, b)
    xa, xb = sorted((round(xa), round(xb)))
    ya, yb = sorted((round(ya), round(yb)))
    h = (w - 1) // 2
    d.rectangle((xa - h, ya - h, xb + h, yb + h), fill=color)

def cut(pts, u):
    """p5: the first u (0..1) of an orthogonal polyline's length, as points."""
    if u >= 1:
        return list(pts)
    lens = [abs(a[0] - b[0]) + abs(a[1] - b[1]) for a, b in zip(pts, pts[1:])]
    left = sum(lens) * max(0.0, u)
    out = [pts[0]]
    for (a, b), ln in zip(zip(pts, pts[1:]), lens):
        if left <= 0:
            break
        k = min(1.0, left / ln) if ln else 1.0
        out.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
        left -= ln
    return out

def trace(d, pts, color, u=1.0, dotted=False, under=True, step=3):
    """p5 (D22, round2 V1/V3): a one-pixel orthogonal polyline grown to the first u of its length from pts[0];
    under: a 3 px band of the same colour at 0.25 below it, so a hairline holds on the paper; dotted: one-pixel
    dots on the absolute `step` px grid (shared runs dot alike, V3)."""
    pts = cut(pts, u)
    if len(pts) < 2:
        return
    if dotted:
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            xa, xb, ya, yb = (round(xa), round(xb), round(ya), round(yb))
            if ya == yb:
                for x in range(min(xa, xb), max(xa, xb) + 1):
                    if x % step == 0:
                        d.point((x, ya), fill=color)
            else:
                for y in range(min(ya, yb), max(ya, yb) + 1):
                    if y % step == 0:
                        d.point((xa, y), fill=color)
        return
    if under:
        for a, b in zip(pts, pts[1:]):
            seg(d, a, b, lv(color, 0.25), 3)
    for a, b in zip(pts, pts[1:]):
        seg(d, a, b, color, 1)

def casing(d, pts, u=1.0, w=3, fill=(0, 0, 0, 0)):
    """p5 (round2): clear a band under a line on the line layer, so it cuts the lines it crosses (a crossing
    reads as passing over, not as a join)."""
    pts = cut(pts, u)
    for a, b in zip(pts, pts[1:]):
        seg(d, a, b, fill, w)

def tick(d, xy, color, r=2):
    """p5: an end tick (5 x 5 at r = 2, as leader()'s) or a junction dot (r = 1)."""
    x, y = (round(xy[0]), round(xy[1]))
    d.rectangle((x - r, y - r, x + r, y + r), fill=color)

def terminal(img, title):
    """Paint the terminal pane (frame + title chip) on a fresh content canvas; returns a Draw."""
    d = ImageDraw.Draw(img)
    frame(d, LEFT, title)
    return d
