"""p6 (D23; sample_p5/stills_design/round3/): the model drawn as one standing tower, three placements of it.

D23: the owner on p5 "still messy, and the picture does not say it clearly"; keep the mechanism (lookback lines +
logit lens), redesign the left, put the model's inside at the far left. Round 3 drew it as one path per token:
the context goes in, the token climbs a tower layer by layer (lens slots at layers 12/24/36/48/64: the stand-in's
own habit low, her phrasing high), the p(next | ctx) slab is the tower's head, the picked character lands in the
big lines; attention is a short comb from the column being computed to the context blocks that sit against the
tower. One engine, three placements (the switch):

  A  tower at the far left, the context column against its right side, the big text right of that
  B  the memory strip stays at x 24-92 (persona and your message on top of it), the tower against it (default)
  C  a vertical pipeline: the big text on top, the head row, the tower, the context along the bottom

  DSH_LAYOUT=A|B|C  (environment), or PROJECT.yaml style.layout; unset: B.

Moved here from sample_p5/design_r3.py (Pen, Tower, the head slab / head row, the context column, the comb lines,
the tallies) and made to move. The p6 rules (sample_p6/README.md, the main agent's brief):
  - a comb line leaves the column at the floor of the layer whose step reads its target, and stays put: the persona
    (the sink) at layer 12, your message at 24, her file at the layer where her character first shows (36 or 48);
    so the lines appear one by one as the column climbs; they grow over GROW from the column; when the column
    lands they leave over FADE (the landing is the one event, R5). C: from the column's foot, down.
  - the head folds to a 24 px cap, never to nothing; it unfolds only for tokens with scripted candidates.
  - your chips carry no token id: a tally dot per read instead (persona and her files add up over the turns, R4).
  - the context moves into its place over MORPH when the local model's first page opens (C1, 82.955) and back when
    the cloud model's `--turns` page scrolls in (C9, 113.225): groups/c.py, morph().
groups/c.py keeps the script and the times (Tok.lens / Tok.attn, X28); this module draws.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import copy
import os
from PIL import Image, ImageChops, ImageDraw
import cast
import hud
import tl
from hud import BG, INK, SLAB, lv
from inspect_ import HEAD, RH, slab
from tuikit import ease, glyph
P = tl.p
HQ = hud.HER_QUIET
ROWS = hud.LENS_ROWS
GROW = 0.12
FADE = 0.3
MORPH = 0.35
LABEL = f'logit lens · {cast.LOCAL['quant']} · 本地权重 · 64 layers'

def _key() -> str:
    k = str(os.environ.get('DSH_LAYOUT') or P.setting('layout', 'B')).strip().upper()
    if k not in ('A', 'B', 'C'):
        raise ValueError(f'DSH_LAYOUT / style.layout must be A, B or C, not {k!r}')
    return k
KEY = _key()

class Pen:
    """Draws on the page, or (mask=True) only the knockout of every text on a mask: the lines are pasted through
    that mask before the page is drawn, so they pass under the texts (p5's 线从字后面过, without painting paper over
    the dot field). level fades everything it draws toward the paper."""

    def __init__(self, d, mask=False, level=1.0):
        self.d, self.mask, self.level = (d, mask, level)

    def c(self, col):
        return col if self.level >= 0.999 or col is None else lv(col, self.level)

    def text(self, xy, s, size, fill, bold=False, anchor='la', font=None, r=3):
        f = font or hud.font(size, s, bold)
        if self.mask:
            if self.level > 0.25:
                self.d.text(xy, s, font=f, fill=255, anchor=anchor, stroke_width=r, stroke_fill=255)
        else:
            self.d.text(xy, s, font=f, fill=self.c(fill), anchor=anchor)
        return self.d.textlength(s, font=f)

    def rect(self, box, fill=None, outline=None, width=1):
        if not self.mask:
            self.d.rectangle(box, fill=self.c(fill), outline=self.c(outline), width=width)

    def line(self, pts, fill, width=1):
        if not self.mask:
            self.d.line(pts, fill=self.c(fill), width=width)

    def point(self, xy, fill):
        if not self.mask:
            self.d.point(xy, fill=self.c(fill))

def bracket(pen, x0, x1, y, color):
    pen.line([(x0, y), (x1, y)], color)
    pen.line([(x0, y - 3), (x0, y)], color)
    pen.line([(x1, y - 3), (x1, y)], color)

def dots(pen, x, y, n, color, per=99, step=4, leftward=False):
    """A tally: n 2 x 2 dots, one per read, `per` to a row (R4: the reads add up; the lines themselves go)."""
    for k in range(n):
        r, c = divmod(k, per)
        xx = x - c * step - 2 if leftward else x + c * step
        pen.rect((xx, y + r * 4, xx + 1, y + r * 4 + 1), fill=color)

def trunc(s, maxw, size=16):
    if hud.width(s, size) <= maxw:
        return s
    while s and hud.width(s + '…', size) > maxw:
        s = s[:-1]
    return s + '…'

def lerp_box(a, b, u):
    return tuple((ease.lerp(x, y, u) for x, y in zip(a, b)))

class Turn:
    """One answer of the local model on its page: the decoder (times, Tok.lens / Tok.attn, X28), your message
    (IME commits, sent_at), the thinking passes on the 16ths from sent_at, and the answer laid out again for the
    layout's big text (bt: same times, other lines / size / x)."""

    def __init__(self, dec, commits, sent_at, breaks, n_think=8, big=None, lines=None, x0=None):
        self.dec, self.commits, self.sent_at = (dec, commits, sent_at)
        self.think, prev = ([], sent_at)
        for k in range(n_think):
            g = tl.grid(sent_at, k)
            self.think.append((prev, g))
            prev = g
        b = LAY.big
        self.bt = relay(dec, b['x0'] if x0 is None else x0, b['lines'] if lines is None else lines, b['size'] if big is None else big, b['right'], breaks)

    def computing(self, t):
        d = self.dec
        if d.progress(t) is not None:
            return True
        if d.eos_at is not None and d.done <= t < d.eos_at:
            return True
        return any((a <= t < b for a, b in self.think))

    def head(self, t):
        """(layer the pass has reached or None) on the ruler: the decoder's climb, or one sweep per thinking pass."""
        head, _done = self.dec.lens_head(t)
        if head is None:
            for a0, b0 in self.think:
                if a0 <= t < b0:
                    return 64 * (t - a0) / max(0.001, b0 - a0)
        return head

    def slab_spec(self, t):
        """The scripted candidates showing at t: (cands, pick, at, a0, a1, src), or None."""
        d = self.dec
        for k, tk in enumerate(d.toks):
            sp = d.span(k)
            if sp and sp[0] <= t < sp[1] + 0.12:
                return (tk.cands, tk.pick, d.tok_t[k], sp[0], sp[1], tk.src)
        return None

def relay(dec, x0, lines, size, right, breaks):
    """The answer laid out again (inspect_.Decoder._layout with the room up to `right` and other line breaks):
    same characters, same times, same D1 light (falls() is computed from the same chars)."""
    bt = copy.copy(dec)
    bt.toks = copy.deepcopy(dec.toks)
    for tk, ln in zip(bt.toks, breaks):
        tk.ln = ln
    bt.big, bt.lines, bt.x0 = (size, tuple(lines), x0)
    n_lines = max((tk.ln for tk in bt.toks)) + 1
    widths = [0.0] * n_lines
    for c, _at, k in bt.chars:
        widths[bt.toks[k].ln] += hud.width(c, bt.big, True)
    room = right - x0
    if max(widths) > room:
        bt.big = int(bt.big * room / max(widths))
    bt.pos, x = ([], [x0] * n_lines)
    for c, _at, k in bt.chars:
        ln = bt.toks[k].ln
        bt.pos.append((x[ln], bt.lines[ln]))
        x[ln] += hud.width(c, bt.big, True)
    bt.line_end = x
    bt.small, xs = ([], x0)
    for c, *_r in bt.chars:
        bt.small.append(xs)
        xs += hud.width(c, 20)
    return bt

class Tower:
    """The model, standing: the ruler wall (64 ticks facing the context, the lens layers longer, a head marker
    where the pass is), one column per sung character, five lens slots on dotted floors at layers 12..64, the base
    line at layer 0. The column being computed fills with its layer lines up to the head (the old 48 cells' crawl,
    now inside the column); old columns keep their five characters (R4).
    Parts: the shell (the walls, the base, its label) and the inside (ticks, floors, layer numbers, columns)."""

    def __init__(self, wall_x, col0, pitch, ncols, base_y, top_y, label_x=None, font=18, ruler='left', base_label='under'):
        self.wall_x, self.col0, self.pitch, self.ncols = (wall_x, col0, pitch, ncols)
        self.base_y, self.top_y = (base_y, top_y)
        self.lp = (base_y - top_y) / 64.0
        self.font, self.base_label = (font, base_label)
        self.right_x = col0 + ncols * pitch + 4
        self.ruler_x, self.plain_x = (wall_x, self.right_x) if ruler == 'left' else (self.right_x, wall_x)
        self.ticks = 1 if ruler == 'left' else -1
        self.label_x = label_x
        self.side = ruler

    def ly(self, layer):
        return self.base_y - layer * self.lp

    def floor(self, layer):
        """The dotted floor under a lens slot (a comb line leaves the column along it)."""
        return round(self.ly(layer) + self.font / 2 + 4)

    def colx(self, j):
        return self.col0 + j * self.pitch

    def cx(self, j):
        return self.col0 + j * self.pitch + self.pitch / 2

    @property
    def top(self):
        return self.ly(64) - self.font / 2 - 6

    def box(self, dx=0):
        """Everything the tower draws (labels included), for the scroll's crossfade."""
        lab_r = self.right_x + 30 if self.label_x is None else self.right_x
        if self.base_label != 'under':
            lab_r = self.right_x + 8 + 150
        lab_l = self.wall_x if self.label_x is None else self.label_x - 24
        bottom = round(self.base_y) + (16 if self.base_label == 'under' else 3)
        return (lab_l + dx - 3, round(self.top) - 3, lab_r + dx + 3, bottom)

    def draw(self, pen, t, turn=None, inside=1.0, cols=1.0, dx=0.0, label=LABEL, label_level=1.0):
        """inside: the ticks, floors and layer numbers (0 = the empty shell); cols: the columns' level (they leave
        with the answer); dx: slide right (D2)."""
        top, base = (round(self.top), round(self.base_y))
        wall, right = (round(self.wall_x + dx), round(self.right_x + dx))
        rx = round(self.ruler_x + dx)
        px = round(self.plain_x + dx)
        pen.line([(rx, top), (rx, base)], lv(INK, ease.lerp(0.32, 0.5, inside)))
        pen.line([(px, top), (px, base)], lv(INK, 0.22))
        pen.line([(wall, base), (right, base)], lv(INK, 0.75))
        if label:
            if self.base_label == 'under':
                pen.text((wall, base + 4), label, 10, lv(INK, 0.55 * label_level))
            else:
                pen.text((right + 8, base - 13), label, 10, lv(INK, 0.55 * label_level))
        if inside > 0.003:
            for L in range(1, 65):
                y = round(self.ly(L))
                n = 8 if L in ROWS else 4
                pen.line([(rx + self.ticks, y), (rx + self.ticks * n, y)], lv(INK, (0.62 if L in ROWS else 0.32) * inside))
            for L in ROWS:
                y = self.floor(L)
                for x in range(int(self.col0 + dx), int(right), 3):
                    pen.point((x, y), lv(INK, 0.3 * inside))
                if self.label_x is None:
                    pen.text((right + 6, self.ly(L)), str(L), 16, lv(INK, 0.55 * inside), anchor='lm')
                else:
                    pen.text((self.label_x + dx, self.ly(L)), str(L), 16, lv(INK, 0.55 * inside), anchor='rm')
        if turn is None:
            return (None, None)
        dec = turn.dec
        k_cols = cols * inside
        cols_, comp = dec.lens_cols(t) if any((tk.lens for tk in dec.toks)) else ([], None)
        head = turn.head(t)
        if k_cols > 0.003:
            if comp is not None and head is not None:
                x0, x1 = (self.colx(comp) + dx + 3, self.colx(comp) + dx + self.pitch - 3)
                for L in range(1, int(head) + 1):
                    y = round(self.ly(L))
                    pen.line([(x0, y), (x1, y)], lv(INK, 0.28 * k_cols))
            for j, col in enumerate(cols_):
                for r, L in enumerate(ROWS):
                    cell = col[r]
                    x, y = (self.cx(j) + dx, self.ly(L))
                    if cell is None:
                        pen.text((x, y), '·', 16, lv(INK, 0.45 * k_cols), anchor='mm', font=P.font(16))
                        continue
                    text, hers = cell
                    f = hud.font(self.font if not text.isascii() else 16, text, r == 0)
                    if j == comp and (not pen.mask):
                        pen.d.text((x, y), text, font=f, fill=BG, anchor='mm', stroke_width=2, stroke_fill=BG)
                    pen.text((x, y), text, self.font, lv(HQ if hers else INK, k_cols), anchor='mm', font=f)
            if comp is not None and head is not None:
                y = round(self.ly(head))
                pen.rect((self.colx(comp) + dx + 1, y - 1, self.colx(comp) + dx + self.pitch - 1, y), fill=lv(INK, k_cols))
        if head is not None and inside > 0.003 and (cols > 0.003):
            y = round(self.ly(head))
            pen.rect((rx - 2, y - 2, rx + 2, y + 2), fill=lv(INK, inside * cols))
        return (comp, head)

def head_slab(pen, t, x0, x1, cap_bottom, spec=None, status='computing…', title='p( next | ctx )', level=1.0, right=None):
    """A, B: the tower's head. The p(next | ctx) slab unfolds upward from a 24 px cap that always tops the tower
    (a token without scripted candidates keeps the cap). spec: Turn.slab_spec(t) or an explicit one."""
    if pen.mask or level <= 0.003:
        return
    pw = x1 - x0
    if spec:
        cands, pick, at, a0, a1, src = spec
        bar_x, bar_w = (pw - 84, 30)
        cands = [(trunc(s, bar_x - 36), p_) for s, p_ in cands]
        full = HEAD + len(cands) * RH + 8
        slab(pen.d, t, cands, pick, at, a0, a1, title, src, x0=x0, y_top=cap_bottom - full, pw=pw, bar_x=bar_x, bar_w=bar_w, min_h=HEAD, level=level, right=right)
        return
    sl = lv(SLAB, level)
    pen.d.rectangle((x0, cap_bottom - HEAD, x1, cap_bottom), fill=sl)
    on = lambda a_: glyph.level(BG, a_, sl)
    pen.d.text((x0 + 12, cap_bottom - HEAD + 7), title, font=P.font(12), fill=on(0.75))
    pen.d.text((x1 - 12, cap_bottom - HEAD + 7), status, font=P.font(12), fill=on(0.75), anchor='ra')

def head_row(pen, t, x0, x1, y0, spec=None, status='computing…', title='p( next | ctx )', level=1.0, h=30):
    """C: the head as one row across the top of the tower (the unembedding is wider than the tower): the
    candidates side by side, each with its p and a thin bar under it; they fade in and out with the slab's
    unfold / fold (0.12 s, as slab())."""
    if pen.mask or level <= 0.003:
        return
    d = pen.d
    sl = lv(SLAB, level)
    on = lambda a_: glyph.level(BG, a_, sl)
    d.rectangle((x0, y0, x1, y0 + h), fill=sl)
    d.text((x0 + 10, y0 + 9), title, font=P.font(12), fill=on(0.75))
    if spec:
        cands, pick, at, a0, a1, src = spec
        picked = t >= at
        status = 'sampled' if picked else 'computing…'
    d.text((x1 - 10, y0 + 9), status, font=P.font(12), fill=on(0.75), anchor='ra')
    if not spec:
        return
    vis = min(ease.ease_out(ease.prog(t, a0, a0 + 0.12)), 1 - ease.ease_in(ease.prog(t, a1, a1 + 0.12)))
    if vis <= 0.01:
        return
    built = ease.ease_out(ease.prog(t, a0, at)) if not picked else 1.0
    pmax = max((p_ for _, p_ in cands)) or 1.0
    x = x0 + 22 + d.textlength(title, font=P.font(12))
    for i, (s, p_) in enumerate(cands):
        s = trunc(s, 150)
        is_on = picked and i == pick
        sw = hud.width(s, 16, is_on)
        pw_ = d.textlength(f'{p_:.2f}', font=P.font(13))
        w = sw + 8 + pw_
        if x + w + 14 > x1 - 96:
            break
        if is_on:
            d.rectangle((x - 6, y0 + 2, x + w + 6, y0 + h - 2), fill=glyph.mix(sl, hud.her(0.0, level) if src != 'self' else lv(BG, level), vis))
            fg = glyph.mix(sl, BG if src != 'self' else sl, vis)
        else:
            fg = on((0.82 if picked else 0.6) * vis)
        hud.tx(d, (x, y0 + 4), s, 16, fg, bold=is_on)
        d.text((x + sw + 8, y0 + 7), f'{p_:.2f}', font=P.font(13), fill=fg)
        bw = max(2, w * p_ / pmax * built)
        d.rectangle((x, y0 + h - 5, x + bw, y0 + h - 4), fill=fg if is_on else on(0.45 * vis))
        x += w + 22

def draw_big(pen, t, bt, eos_xy=None, shrink=0.0, small_xy=None, level=1.0, caret=True, skip=None, halo=False):
    """The answer in the layout's big lines (inspect_.Decoder.typed with the <eos> chip where the layout has room);
    shrink 0..1 morphs it into one 20 px context line at small_xy. skip(k) -> True leaves token k out (the kitten).
    halo: a 2 px paper edge while it moves (C7: it flies over the thinking bars as they open)."""
    last = None
    sx, sy = small_xy if small_xy else (bt.x0, 488)
    xs = sx
    for i, (c, at, k) in enumerate(bt.chars):
        if at > t:
            break
        small_x = xs
        xs += hud.width(c, 20)
        if skip is not None and skip(k):
            last = (i, c, at, k)
            continue
        drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -10
        x, y = bt.pos[i]
        size = max(20, int(round(ease.lerp(bt.big, 20, shrink))))
        xx = ease.lerp(x, small_x, shrink)
        yy = ease.lerp(y + drop, sy, shrink)
        if halo and 0 < shrink < 1 and (not pen.mask):
            pen.d.text((xx, yy - 8 * (1 - shrink)), c, font=hud.font(size, c, shrink < 0.5), fill=lv(bt.color(k, at, t), level), stroke_width=2, stroke_fill=BG)
        else:
            pen.text((xx, yy - 8 * (1 - shrink)), c, size, lv(bt.color(k, at, t), level), bold=shrink < 0.5)
        last = (i, c, at, k)
    if last is None or pen.mask or shrink > 0 or (not caret):
        return
    d = pen.d
    i, c, at, k = last
    ln = bt.toks[k].ln
    x, y = bt.pos[i]
    h = bt.big
    if bt.eos_at is None or t < bt.eos_at:
        cx = bt.line_end[ln] if t >= bt.done else x + hud.width(c, bt.big, True)
        if tl.C.beat_of(t) % 1.0 < 0.5 or t - at < 0.3:
            d.rectangle((cx + 6, y + 14 * h / 78, cx + 12, y + 92 * h / 78), fill=lv(INK, level))
        return
    u = ease.prog(t, bt.eos_at, bt.eos_at + 0.12)
    f = P.font(22, 'bold')
    w = d.textlength('<eos>', font=f)
    ce = hud.her(bt.lit(bt.eos_at, t))
    ex, ey = eos_xy if eos_xy else (bt.line_end[ln] + 12, y + 44 * h / 78)
    d.rounded_rectangle((ex, ey, ex + 16 + w, ey + 34), radius=6, outline=lv(ce, u * level), width=2)
    d.text((ex + 8, ey + 4), '<eos>', font=f, fill=lv(ce, u * level))

def eos_xy(bt):
    """Where the <eos> chip goes: after the last line, or under it when it does not fit (A, B)."""
    w = hud.width('<eos>', 22, True) + 16
    ln = max((tk.ln for tk in bt.toks))
    if bt.line_end[ln] + 12 + w <= LAY.big['right']:
        return None
    return (bt.x0, bt.lines[-1] + bt.big + 22)

def eos_box(bt):
    xy = eos_xy(bt)
    ln = max((tk.ln for tk in bt.toks))
    h = bt.big
    if xy is None:
        xy = (bt.line_end[ln] + 12, bt.lines[ln] + 44 * h / 78)
    w = hud.width('<eos>', 22, True)
    return (xy[0], xy[1], xy[0] + 16 + w, xy[1] + 34)

def files(t):
    return hud.strip_files(t)

def _n_eased(t):
    return 8.0 + sum((ease.ease_io(ease.prog(t, tw, tw + 0.3)) for tw, _n, _o in tl.WRITES))

def her_block(pen, box, name, r, n_reads, chars=9, size=11, dxk=4, strip=False, dots_level=1.0):
    """Her file: a quiet-blue block, the name in paper, a read pulse r (shift + outline), tally dots inside.
    strip=True: drawn exactly as hud.strip draws it (the name top-left), for the morph's strip end."""
    x0, y0, x1, y1 = box
    dx = dxk * r
    pen.rect((x0 + dx, y0, x1 + dx, y1), fill=HQ)
    if r > 0.05:
        pen.rect((x0 + dx - 2, y0 - 2, x1 + dx + 2, y1 + 2), outline=lv(INK, r), width=2)
    if not pen.mask and y1 - y0 > (14 if strip else 9):
        if strip:
            pen.d.text((x0 + 4 + dx, y0 + 6), name[:9], font=P.font(11), fill=BG)
        else:
            pen.d.text((x0 + 4 + dx, (y0 + y1) / 2), name[:chars], font=P.font(size), fill=BG, anchor='lm')
    if y1 - y0 > 6 and dots_level > 0.003:
        dots(pen, x1 + dx - 3, round((y0 + y1) / 2) - 1, n_reads, glyph.mix(HQ, BG, dots_level), leftward=True)

def own_block(pen, box, name, r=0.0, chars=9, size=11, dxk=4, strip=False):
    x0, y0, x1, y1 = box
    dx = dxk * r
    x0, x1 = (x0 + dx, x1 + dx)
    pen.rect((x0, y0, x1, y1), fill=BG, outline=INK, width=2 if strip else 1)
    if not pen.mask:
        hud.hatch(pen.d, (x0 + 2, y0 + 2, x1 - 2, y1 - 2), pen.c(lv(INK, 0.45)), 4)
    if r > 0.05:
        pen.rect((x0 - 2, y0 - 2, x1 + 2, y1 + 2), outline=lv(INK, r), width=2)
    if pen.mask:
        return
    if strip and y1 - y0 > 14:
        tw = pen.d.textlength(name[:9], font=P.font(11))
        pen.d.rectangle((x0 + 3, y0 + 6, x0 + 5 + tw, y0 + 19), fill=BG)
        pen.d.text((x0 + 4, y0 + 6), name[:9], font=P.font(11), fill=pen.c(INK))
    elif not strip and y1 - y0 > 12:
        tw = pen.d.textlength(name[:chars], font=P.font(size))
        pen.d.rectangle((x0 + 3, (y0 + y1) / 2 - 6, x0 + 5 + tw, (y0 + y1) / 2 + 6), fill=BG)
        pen.d.text((x0 + 4, (y0 + y1) / 2), name[:chars], font=P.font(size), fill=pen.c(INK), anchor='lm')

def archive_block(pen, box, r=0.0, size=11, strip=False):
    """strip=True: hud.strip's archive (44 px, '412 行' under the name, 2 px outline); else the layout's short one."""
    x0, y0, x1, y1 = box
    q = HQ
    pen.rect((x0, y0, x1, y1), fill=lv(q, 0.16 + 0.5 * r), outline=q, width=2 if strip else 1)
    if pen.mask:
        return
    d = pen.d
    hud.hatch(d, (x0 + 2, y0 + 2, x1 - 2, y1 - 2), pen.c(lv(q, 0.55 + 0.45 * r)), 5)
    if strip:
        d.rectangle((x0 + 3, y0 + 5, x0 + 52, y0 + 18), fill=BG)
        d.text((x0 + 4, y0 + 5), 'archive', font=P.font(11), fill=pen.c(q))
        d.rectangle((x0 + 3, y0 + 23, x0 + 46, y0 + 36), fill=BG)
        d.text((x0 + 4, y0 + 23), '412 行', font=P.font(11, 'cjk'), fill=pen.c(q))
        return
    s = 'archive'
    tw = hud.width(s, size)
    ty = (y0 + y1) / 2
    d.rectangle((x0 + 3, ty - 7, x0 + 6 + tw, ty + 6), fill=BG)
    hud.tx(d, (x0 + 4, ty), s, size, pen.c(q), anchor='lm')

def think_chips(pen, x, y, t, sent_at, w=8, gap=2, n=8, gone=(), level=1.0):
    """The hidden thinking, folded: chip k grows on the k-th 16th after sent_at (as think_bars(folded=True));
    gone[k]: chip k has left (it opens as a bar, C7)."""
    for k in range(n):
        g = tl.grid(sent_at, k)
        grow = ease.ease_out(ease.prog(t, g, g + 0.07))
        if grow <= 0:
            break
        if k < len(gone) and gone[k]:
            continue
        bx = x + k * (w + gap)
        pen.rect((bx, y, bx + max(1, w * grow), y + 4), fill=lv(SLAB, level))

def strip_geo(t, k=None):
    """The strip's own geometry (hud.strip) for the morph: block k, archive, count, label."""
    if k is None:
        return hud.archive_rect(t)
    return hud.block_rect(k, t)

class Context:
    """The context the comb lines reach: the persona row (context token 0, the sink), your message as chips, the
    folded thinking, her files, the archive and the count. A, B: one column beside the tower; C: two rows under
    it. u (morph): 0 = the strip as every other group draws it (hud.strip), 1 = the layout's place."""

    def __init__(self, lay):
        self.L = lay

    def turn_rows(self, pen, t, turn, geo, tal, u=1.0, chips_level=1.0, think_gone=(), think_level=1.0):
        L = self.L
        if L.key == 'C':
            return self._rows_C(pen, t, turn, geo, tal, u, chips_level, think_gone, think_level)
        S, (x0, w, y0) = (L.S, L.ctx)
        bx0 = ease.lerp(hud.COLR[0], x0, u)
        x = bx0 + S.get('inset', 0)
        lvl = u
        side = L.side
        ax = (lambda: round(bx0) - 5) if side == 'left' else lambda: round(bx0 + w) + 5
        y = L.y['persona']
        pen.text((x, y), 'persona', S['lab'], lv(INK, 0.6 * lvl), font=P.font(S['lab']))
        y += S['lab'] + S['pad']
        tw = pen.text((x, y), '你是大肥鱼', S['persona'], lv(INK, 0.9 * lvl))
        by = y + S['persona'] + 6
        bracket(pen, x, x + tw, by, lv(INK, 0.5 * lvl))
        geo['persona'] = (ax(), round(y + S['persona'] / 2 + 3))
        dots(pen, x + 1, by + 3, tal.get('persona', 0), lv(INK, 0.6 * lvl), per=int(w // 4) - 1)
        y = L.y['user']
        pen.text((x, y), 'user', S['lab'], lv(INK, 0.7 * lvl), font=P.font(S['lab']))
        y += S['lab'] + S['pad']
        sent = turn is not None and t >= turn.sent_at
        for k, (at, word) in enumerate(turn.commits if turn is not None else []):
            if at > t:
                break
            drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.12))) * -6
            cy = y + k * L.chip_pitch
            tw = pen.text((x, cy + drop), word, S['chip'], lv(INK, chips_level * lvl), True)
            by = cy + S['chip'] + 6
            bracket(pen, x, x + tw, by, lv(INK, (0.85 if sent else 0.5) * chips_level * lvl))
            geo['chip', k] = (ax(), round(cy + S['chip'] / 2 + 3))
            geo['chipbox', k] = (round(x), round(cy), round(x + tw), round(by))
            dots(pen, x + 1, by + 3, tal.get(('chip', k), 0), lv(INK, 0.75 * chips_level * lvl))
        y = L.y['think']
        pen.text((x, y), '<think>', S['lab'], lv(INK, 0.75 * lvl * think_level), font=P.font(S['lab']))
        if turn is not None:
            if S['think_dx']:
                think_chips(pen, x + S['think_dx'], y + 4, t, turn.sent_at, w=S['think_w'], gone=think_gone, level=lvl * think_level)
            else:
                think_chips(pen, x, y + S['lab'] + 4, t, turn.sent_at, w=S['think_w'], gone=think_gone, level=lvl * think_level)

    def _rows_C(self, pen, t, turn, geo, tal, u, chips_level, think_gone, think_level):
        """C: persona, your message, <think> in one row under the tower; lines come down into their top edges."""
        y = self.L.conv_y
        lvl = u
        x = self.L.conv_x
        pen.text((x, y + 3), 'persona', 11, lv(INK, 0.6 * lvl), font=P.font(11))
        x += hud.width('persona', 11) + 8
        tw = pen.text((x, y), '你是大肥鱼', 16, lv(INK, 0.9 * lvl))
        bracket(pen, x, x + tw, y + 22, lv(INK, 0.5 * lvl))
        geo['persona'] = (round(x + tw / 2), y - 3)
        dots(pen, x + 1, y + 25, tal.get('persona', 0), lv(INK, 0.6 * lvl), per=int(tw // 4))
        x += tw + 26
        pen.text((x, y + 3), 'user', 11, lv(INK, 0.7 * lvl), font=P.font(11))
        x += hud.width('user', 11) + 8
        sent = turn is not None and t >= turn.sent_at
        xc = x
        for k, (at, word) in enumerate(turn.commits if turn is not None else []):
            if at > t:
                break
            drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.12))) * -6
            w = pen.text((xc, y - 2 + drop), word, 18, lv(INK, chips_level * lvl), True)
            bracket(pen, xc, xc + w, y + 22, lv(INK, (0.85 if sent else 0.5) * chips_level * lvl))
            geo['chip', k] = (round(xc + w / 2), y - 3)
            geo['chipbox', k] = (round(xc), y - 2, round(xc + w), y + 22)
            dots(pen, xc + 1, y + 25, tal.get(('chip', k), 0), lv(INK, 0.75 * chips_level * lvl))
            xc += w + 12
        x = max(xc, x + self.L.conv_user_w) + 10
        pen.text((x, y + 3), '<think>', 11, lv(INK, 0.75 * lvl * think_level), font=P.font(11))
        if turn is not None:
            think_chips(pen, x + 52, y + 7, t, turn.sent_at, w=8, gone=think_gone, level=lvl * think_level)

    def memory(self, pen, t, geo, tal, hits, u=1.0):
        L = self.L
        fl = files(t)
        n = _n_eased(t)
        lay = L.file_boxes(t, n, len(fl))
        hits = hits or {}
        S = L.S
        if u < 0.999:
            pen.text((hud.COLR[0], hud.COLR[1] + 6), 'memory/', 11, lv(INK, 0.8 * (1 - u)), font=P.font(11))
            pen.text((hud.COLR[0], hud.COLR[1] + 19), 'you/', 11, lv(INK, 0.8 * (1 - u)), font=P.font(11))
        if u > 0.001 and L.key != 'C':
            lx, ly_ = L.mem_label
            lx, ly_ = (ease.lerp(hud.COLR[0], lx, u), ease.lerp(hud.COLR[1] + 6, ly_, u))
            pen.text((lx, ly_), 'memory/you/', S['lab'], lv(INK, 0.8 * u), font=P.font(S['lab']))
        strip = u < 0.5
        for k, (name, owner, born) in enumerate(fl):
            a = strip_geo(t, k)
            b = lay[k]
            x0, y0, x1, y1 = lerp_box(a, b, u)
            g = ease.ease_back(ease.prog(t, born, born + 0.25)) if born > 0 else 1.0
            if L.key == 'C' and (not strip):
                x1 = x0 + max(1, (x1 - x0) * g)
            else:
                y1 = y0 + max(1, (y1 - y0) * g)
            box = (round(x0), round(y0), round(x1), round(y1))
            r = hits.get(k, 0.0)
            dxk = 5 if strip else 4
            if owner == 'her':
                her_block(pen, box, name, r, tal.get(('file', name), 0), S['fchars'], S['fsize'], dxk, strip, dots_level=u)
                if L.key == 'C':
                    geo['file', name] = (round((box[0] + box[2]) / 2), box[1] - 3)
                elif L.side == 'left':
                    geo['file', name] = (box[0] - 5, round((box[1] + box[3]) / 2))
                else:
                    geo['file', name] = (box[2] + 5, round((box[1] + box[3]) / 2))
            else:
                own_block(pen, box, name, r, S['fchars'], S['fsize'], dxk, strip)
            geo['box', k] = box
        a = hud.archive_rect(t)
        b = L.archive_box(t, n, len(fl))
        box = tuple((round(v) for v in lerp_box(a, b, u)))
        archive_block(pen, box, hits.get('archive', 0.0), S['fsize'], strip)
        if L.key == 'C':
            geo['archive',] = (round((box[0] + box[2]) / 2), box[1] - 3)
        elif L.side == 'left':
            geo['archive',] = (box[0] - 5, round((box[1] + box[3]) / 2))
        else:
            geo['archive',] = (box[2] + 5, round((box[1] + box[3]) / 2))
        geo['archive_box'] = box
        hers, total = tl.files(t)
        s = f'{hers}/{total}'
        cx0, cy0 = (hud.COLR[0], a[3] + 12)
        cx1, cy1 = L.count_xy(box)
        cx, cy = (ease.lerp(cx0, cx1, u), ease.lerp(cy0, cy1, u))
        tw = pen.text((cx, cy), s, 16, HQ, True, font=P.font(16, 'bold'))
        by_lv = 1 - u if L.key == 'C' else 1.0
        if S.get('byher') == 'below':
            bx_, byy = (ease.lerp(cx0, cx1, u), ease.lerp(cy0 + 20, cy1 + 18, u))
        else:
            bx_, byy = (ease.lerp(cx0, cx1 + tw + 6, u), ease.lerp(cy0 + 20, cy1 + 4, u))
        if by_lv > 0.003:
            pen.text((bx_, byy), 'by her', 11, lv(HQ, 0.85 * by_lv), font=P.font(11))

def color_of(k):
    if k == 'persona':
        return lv(INK, 0.5)
    if k[0] == 'chip':
        return lv(INK, 0.9)
    return HQ

def key(sp):
    return 'persona' if sp == 'persona' else tuple(sp)

def read_layer(dec, i, sp):
    """The lens layer whose step reads target sp in sung character i's pass (the main agent's rule): the persona
    (the sink) at the lowest slot, 12; your message at 24; her file (or the archive) where the landed character
    first shows in its column (36 or 48; 48 if it never does below the top)."""
    if sp == 'persona':
        return 12
    if sp[0] == 'chip':
        return 24
    tok, n = dec.tok_of(i)
    c = dec.chars[i][0]
    if tok.lens:
        for L, cell in zip((36, 48), tok.lens[n][2:]):
            if cell and cell[0] == c:
                return L
    return 48

def births(dec, i, a, b):
    """{target key: (birth time, layer)} for pass (i, a, b): a line is born on the lens step that lights its
    layer (12 = first cell, 24 = second, 36, 48); none when that step is the landing itself."""
    steps = dec.lens_steps(a, b)
    out = {}
    for sp in dec.attn_of(i):
        L = read_layer(dec, i, sp)
        need = {12: 1, 24: 2, 36: 3, 48: 4}[L]
        at = next((s for s, cells in steps if cells >= need), b)
        if at < b - 0.03:
            out[key(sp)] = (at, L)
    return out

def tallies(turns, t):
    """Reads per context key by the characters landed by t (and <eos>). The persona and her files add up over
    all the local turns so far (R4); your chips count only for the turn on the page (`turns[-1]`)."""
    n = {}
    for j, turn in enumerate(turns):
        dec = turn.dec
        if t < dec.start:
            continue
        reads = [dec.attn_of(i) for i in dec.landed(t)]
        if dec.eos_at is not None and t >= dec.eos_at:
            reads.append(dec.eos_attn())
        for targets in reads:
            for sp in targets:
                k = key(sp)
                if k[0] == 'chip' and j != len(turns) - 1:
                    continue
                n[k] = n.get(k, 0) + 1
    return n

def hits(turn, P_):
    """Her blocks pulse as a comb line reaches them (hud.Pulse, decay 0.35 s as in p5)."""
    dec = turn.dec
    for i, a, b in dec.passes():
        if a > P_.t:
            break
        for k, (at, _L) in births(dec, i, a, b).items():
            if k[0] == 'file':
                P_.hit(tl.HER_FILES.index(k[1]), at + GROW, 0.35)
            elif k[0] == 'archive':
                P_.hit('archive', at + GROW, 0.35)
    return P_

def comb(L, lay, tw, t, turn, geo, alpha=1.0, dx=0.0):
    """The lines of the column being computed (and of the one that just landed, leaving over FADE).
    A, B: from the column's edge along the floor of the line's layer to the spine beside the context, along the
    spine, one short stub into the target; C: from the column's foot down to the lane, along it, down into the
    target's top edge. Returns the ticks to draw over the knockout."""
    dec = turn.dec
    ticks = []
    trunk_c = lv(INK, 0.55)
    for j, (i, a, b) in enumerate(dec.passes()):
        if t < a or t >= b + FADE:
            continue
        k_out = 1 - ease.ease_out(ease.prog(t, b, b + FADE))
        k = k_out * alpha
        if k <= 0.003:
            continue
        for tk, (at, layer) in sorted(births(dec, i, a, b).items(), key=lambda x: x[1][0]):
            if t < at or tk not in geo:
                continue
            u = ease.ease_out(ease.prog(t, at, at + GROW))
            tx_, ty = geo[tk]
            col = color_of(tk)
            if lay.key == 'C':
                ox, oy = (round(tw.cx(j) + dx), round(tw.base_y) + 1)
                pts = [(ox, oy), (ox, lay.lane_y), (tx_, lay.lane_y), (tx_, ty)]
                junction = (tx_, lay.lane_y)
            else:
                fy = tw.floor(layer)
                ox = round(tw.colx(j) + dx + (tw.pitch - 1 if lay.side == 'left' else 1))
                sx = lay.spine_x
                pts = [(ox, fy), (sx, fy), (sx, ty), (tx_, ty)]
                junction = (sx, ty)
            pts = [p for n_, p in enumerate(pts) if n_ == 0 or p != pts[n_ - 1]]
            tc = lv(trunk_c, k)
            sc = lv(col, k)
            hud.casing(L, pts, u)
            hud.trace(L, pts, tc, u)
            seg_lens = [abs(p[0] - q[0]) + abs(p[1] - q[1]) for p, q in zip(pts, pts[1:])]
            total = sum(seg_lens) or 1
            head_len = total - seg_lens[-1]
            if u * total > head_len:
                us = (u * total - head_len) / max(1, seg_lens[-1])
                hud.trace(L, pts[-2:], sc, us)
            if u >= 1:
                ticks += [(pts[-1], sc, 2), (junction, tc, 1)]
            ticks.append((pts[0], lv(INK, 0.9 * k), 1))
    return ticks

class Layout:

    def __init__(self, key, **kw):
        self.key = key
        self.__dict__.update(kw)
        self.ctx_ = Context(self)
        if key != 'C':
            self._column_y()

    def _column_y(self):
        S, (x0, w, y0) = (self.S, self.ctx)
        y = y0
        self.y = {'persona': y}
        y += S['lab'] + S['pad'] + S['persona'] + 6 + 3 + 6 + S['gap']
        self.y['user'] = y
        self.chip_pitch = S['chip'] + 6 + 3 + 2 + S['chip_gap']
        y += S['lab'] + S['pad'] + 4 * self.chip_pitch + S['gap'] - S['chip_gap']
        self.y['think'] = y
        y += S['lab'] + 4 + S['gap'] if S['think_dx'] else S['lab'] + 4 + 6 + S['gap']
        self.mem_label = (x0 + S.get('inset', 0), y)
        self.files_top = y + S['lab'] + S['pad'] + 2

    def pitch(self, n):
        S = self.S
        if self.key == 'C':
            return min(S['fpitch'], S['room'] / n)
        return min(S['fpitch'], S['room'] / n)

    def file_boxes(self, t, n_eased, n):
        S = self.S
        pitch = self.pitch(n_eased)
        if self.key == 'C':
            w = pitch - S['fgap']
            return [(S['fx0'] + k * pitch, S['fy'], S['fx0'] + k * pitch + w, S['fy'] + S['fh']) for k in range(n)]
        x0, w, _ = self.ctx
        h = max(3.0, S['fh'] * pitch / S['fpitch'])
        return [(x0, self.files_top + k * pitch, x0 + w, self.files_top + k * pitch + h) for k in range(n)]

    def archive_box(self, t, n_eased, n):
        S = self.S
        pitch = self.pitch(n_eased)
        if self.key == 'C':
            x = S['fx0'] + n_eased * pitch
            return (x, S['fy'], x + S['aw'], S['fy'] + S['fh'])
        x0, w, _ = self.ctx
        y = self.files_top + n_eased * pitch + 2
        return (x0, y, x0 + w, y + S['ah'])

    def count_xy(self, abox):
        if self.key == 'C':
            return (abox[2] + 8, abox[1] + 2)
        return (self.ctx[0] + self.S.get('inset', 0), abox[3] + 6)

    def cmdline(self, d, t, cmd, chip_t0=None, x=None):
        hud.cmdline(d, t, cmd, chip_t0=chip_t0, x=self.cmd_x if x is None else x)

    def fine_print(self, d, t, tokens=None, level=1.0, x=None):
        hud.fine_print(d, t, tokens, level=level, x0=self.fine_x if x is None else x)

    def head(self, pen, t, spec, status, title='p( next | ctx )', level=1.0, dx=0.0, right=None):
        tw = self.tower
        if self.key == 'C':
            x0, x1, y0 = self.head_row
            head_row(pen, t, x0 + dx, x1 + dx, y0, spec, status, title, level)
        else:
            head_slab(pen, t, tw.wall_x + dx, tw.right_x + dx, self.cap_bottom, spec, status, title, level, right)

    @property
    def head_box(self):
        tw = self.tower
        if self.key == 'C':
            x0, x1, y0 = self.head_row
            return (x0, y0, x1, y0 + 30)
        return (tw.wall_x, self.cap_bottom - HEAD - 4 * RH - 8, tw.right_x, self.cap_bottom)
LAYOUTS = {'A': dict(tower=Tower(wall_x=62, col0=66, pitch=19, ncols=11, base_y=528, top_y=246, label_x=56, ruler='right'), cap_bottom=230, spine_x=288, ctx=(302, 88, 92), side='left', S=dict(lab=11, pad=3, persona=16, gap=8, chip=18, chip_gap=2, think_dx=50, think_w=4, fh=17, fpitch=20, fchars=12, fsize=11, ah=20, room=190), big=dict(x0=414, lines=(176, 268, 360), size=78, right=hud.XR), log=(414, 92, hud.XR, 530), small=(414, 488), cmd_x=36, fine_x=36), 'B': dict(tower=Tower(wall_x=108, col0=118, pitch=20, ncols=11, base_y=528, top_y=246, label_x=None), cap_bottom=230, spine_x=102, ctx=(24, 68, 66), side='right', S=dict(lab=10, pad=2, persona=13, gap=7, chip=16, chip_gap=2, think_dx=0, think_w=6, inset=3, fh=19, fpitch=23, fchars=9, fsize=11, ah=24, room=240, byher='below'), big=dict(x0=384, lines=(176, 268, 360), size=78, right=hud.XR), log=(384, 92, hud.XR, 530), small=(124, 488), cmd_x=hud.X0, fine_x=hud.X0), 'C': dict(tower=Tower(wall_x=268, col0=276, pitch=22, ncols=11, base_y=482, top_y=318, label_x=262, base_label='side'), head_row=(64, hud.XR, 272), lane_y=490, side='down', conv_y=498, conv_x=124, conv_user_w=300, S=dict(lab=11, fx0=36, fy=534, fh=22, fpitch=68, fgap=4, aw=62, fchars=9, fsize=10, room=616), big=dict(x0=64, lines=(94, 180), size=78, right=hud.XR), log=(36, 92, hud.XR, 262), small=(64, 236), cmd_x=36, fine_x=36)}
for _k, _cfg in LAYOUTS.items():
    LAYOUTS[_k] = Layout(_k, **_cfg)
LAY = LAYOUTS[KEY]
BREAKS = {'A': {'steak': [0, 0, 1, 1, 1, 2, 2, 2], 'cat': [0, 0, 1, 1, 2, 2, 2]}, 'B': {'steak': [0, 0, 1, 1, 1, 2, 2, 2], 'cat': [0, 0, 1, 1, 2, 2, 2]}, 'C': {'steak': [0, 0, 0, 1, 1, 1, 1, 1], 'cat': [0, 0, 0, 0, 1, 1, 1]}}[KEY]

def page(img, t, turn, turns, *, hits_=None, cmd=None, chip_t0=None, morph_u=1.0, chips_level=1.0, think_gone=(), think_level=1.0, tower_level=1.0, tower_dx=0.0, inside=1.0, cols=1.0, tower_label=LABEL, label_level=1.0, lines_alpha=1.0, head_spec='auto', head_status=None, head_title='p( next | ctx )', head_right=None, head_level=None, big=True, shrink=0.0, big_level=1.0, skip=None, tokens='auto', fine=True, ctx_level=1.0, small=None, memory=True, row_x=None):
    """Draw one page of `dsh inspect --logits --attn --lens` for a local turn on img (frame and background are
    already there): the command, the tower and its head, the context, the comb lines (under the texts), the big
    text, the fine print. Returns geo (the context's attach points and boxes) for the caller's own drawing."""
    lay = LAY
    tw = lay.tower
    geo = {}
    tal = tallies(turns, t)
    if head_spec == 'auto':
        head_spec = turn.slab_spec(t) if turn is not None else None
    if head_status is None:
        head_status = ('computing…' if turn.computing(t) else 'sampled' if turn.dec.landed(t) else 'idle') if turn is not None else 'idle'
    cmd_x, fine_x = (None, None) if row_x is None else (row_x, row_x)
    hl = tower_level if head_level is None else head_level

    def draw(pen, g):
        if cmd is not None and (not pen.mask):
            lay.cmdline(pen.d, t, cmd, chip_t0, cmd_x)
        if tower_level > 0.003:
            tpen = Pen(pen.d, pen.mask, tower_level)
            tw.draw(tpen, t, turn, inside=inside, cols=cols, dx=tower_dx, label=tower_label, label_level=label_level)
        if hl > 0.003:
            lay.head(Pen(pen.d, pen.mask, 1.0), t, head_spec, head_status, head_title, hl, tower_dx, head_right)
        if ctx_level > 0.003:
            cpen = Pen(pen.d, pen.mask, ctx_level)
            lay.ctx_.turn_rows(cpen, t, turn, g, tal, morph_u, chips_level, think_gone, think_level)
            if memory:
                lay.ctx_.memory(cpen, t, g, tal, hits_, morph_u)
        if big and turn is not None:
            draw_big(pen, t, turn.bt, eos_xy(turn.bt), shrink, small or lay.small, big_level, skip=skip)
        if fine and (not pen.mask):
            tok = (turn.dec.n_tok(t), len(turn.dec.toks)) if tokens == 'auto' and turn is not None else None if tokens == 'auto' else tokens
            lay.fine_print(pen.d, t, tok, x=fine_x)
    mask = Image.new('L', img.size, 0)
    draw(Pen(ImageDraw.Draw(mask), mask=True), geo)
    ticks = []
    if turn is not None and lines_alpha * tower_level > 0.003 and (t >= turn.dec.start):
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ticks = comb(ImageDraw.Draw(layer), lay, tw, t, turn, geo, lines_alpha * tower_level, tower_dx)
        a = ImageChops.subtract(layer.getchannel('A'), mask)
        img.paste(layer.convert('RGB'), (0, 0), a)
    out = {}
    draw(Pen(ImageDraw.Draw(img)), out)
    d = ImageDraw.Draw(img)
    for xy, col, r in ticks:
        hud.tick(d, xy, col, r)
    return out

def scroll(film, old_body, new_body, ta, tb, regions, fades=(), ground=None):
    """R9 (滚) for the new layouts: only the `regions` scroll (each (x0, y0, x1, y1), the old page up and out, the
    new one up from below, darkest-wins over the dot field as groups/c.py scrolled() does); the `fades` crossfade
    old -> new (the tower: its old columns leave while the new page's empty ones come); the rest is the new page.
    ground(t): the background to composite over (film.background)."""
    from groups.c import _Peek

    def body(c, img, d):
        t = c.t
        new_body(c, img, d)
        if t >= tb:
            return
        k = ease.smooth(ease.prog(t, ta, tb))
        pages = []
        for fn in (old_body, new_body):
            im = Image.new('RGB', (P.W, P.H), BG)
            fn(_Peek(t), im, ImageDraw.Draw(im))
            pages.append(im)
        under = film.background(t)
        for box in regions:
            box = tuple((int(v) for v in box))
            H = box[3] - box[1]
            s = int(round(H * k))
            parts = [pg.crop(box) for pg in pages]
            if box[1] <= hud.Y_CMD + 17 and box[2] > hud.XR - 160:
                chip = cast.term(tl.model(t))
                cw, cx1 = (hud.width(chip, 13, True), hud.xr(t) - box[0])
                for part in parts:
                    ImageDraw.Draw(part).rectangle((cx1 - cw - 13, hud.Y_CMD - 4 - box[1], cx1 + 1, hud.Y_CMD + 18 - box[1]), fill=BG)
            a = Image.new('RGB', parts[0].size, BG)
            a.paste(parts[0], (0, -s))
            b = Image.new('RGB', parts[1].size, BG)
            b.paste(parts[1], (0, H - s))
            img.paste(ImageChops.darker(under.crop(box), ImageChops.darker(a, b)), box[:2])
        for box in fades:
            box = tuple((int(v) for v in box))
            o, n = (pages[0].crop(box), pages[1].crop(box))
            mixed = Image.blend(o, n, k)
            img.paste(ImageChops.darker(under.crop(box), mixed), box[:2])
    return body

def morph_u(t, t_in=None, t_out=None):
    """The context's place: 0 (the strip) .. 1 (the layout's), eased in over MORPH from t_in and out from t_out."""
    u = 1.0
    if t_in is not None:
        u = min(u, ease.ease_io(ease.prog(t, t_in, t_in + MORPH)))
    if t_out is not None:
        u = min(u, 1 - ease.ease_io(ease.prog(t, t_out, t_out + MORPH)))
    return u
