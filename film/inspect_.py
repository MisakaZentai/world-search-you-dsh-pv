"""`dsh inspect --logits`: the decoding device from the approved style sample (sample_p3d, G2/D16).

  Decoder     a stand-in's answer, one Chinese character per sung syllable (local model) or one chunk per
              sung word (cloud model, R11). Draws it typed into big lines with a caret, shrinks it into a
              context line, and pops a p(next | ctx) slab before each token that has candidates: the
              runners-up are the vendor's own voice (R10), the pick is hers (blue) or its own (paper).
  slab(...)   one candidate slab (also used on its own: <wait>, the IME bar, completions)
  think_bars  the hidden thinking as redaction bars, grown on 16ths, folded while it answers
  prompt_chips your message as token chips, appearing word by word as the IME commits (R7)

p5 (GEN_PLAN_20261002.md §2, D19/D22; sample_p5/stills_design/README.md "做动态要补的接口"): the inside of the
local model. persona_row() prints the system prompt (context token 0, the attention sink) and the rows under it
move down (the P_* layout); Tok.lens / Decoder.lens_cols() fill the logit-lens grid one cell per layer on the
16ths of each forward pass; Tok.attn / Lookback draw the lookback lines on the V1 bus (round2/README.md).

(The module is called inspect_ so it never shadows Python's own inspect.)
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from dataclasses import dataclass, field
from PIL import Image, ImageChops, ImageDraw
import hud
import syl
import tl
from hud import BG, HER, INK, SLAB, X0, XR, lv
from tuikit import ease, glyph
Y_PROMPT, Y_FOLD, PANEL_TOP = (92, 146, 168)
L1, L2, BIG = (346, 436, 78)
Y_CONTEXT = 488
RH, HEAD, PW = (26, 24, 400)
Y_PERSONA = 86
P_PROMPT, P_FOLD, P_PANEL = (112, 168, 188)
P_PW, P_BAR_X, P_BAR_W = (368, 262, 54)
LENS_GROW = 0.12
LENS_MIN_STEP = 0.09
_SYLS: list = []

def next_syllable(t: float) -> float:
    """D1: the first sung syllable after t (any line); t + 0.6 past the last one."""
    if not _SYLS:
        _SYLS.extend(sorted((x for Lx in tl.L.lines for x in syl.times(Lx.id))))
    for x in _SYLS:
        if x > t + 0.02:
            return x
    return t + 0.6

@dataclass
class Tok:
    text: str
    src: str = 'archive'
    cands: list | None = None
    pick: int = 0
    ln: int = 0
    syl: int | None = None
    lens: list | None = None
    attn: list | None = None

@dataclass
class Decoder:
    toks: list
    chars: list = field(default_factory=list)
    tok_t: list = field(default_factory=list)
    eos_at: float | None = None
    start: float = 0.0
    hold: float | None = None
    title: str = 'p( next | ctx )'
    big: int = BIG
    lines: tuple = (L1, L2)
    x0: float = X0

    @classmethod
    def on(cls, toks, lid=None, wi0=0, counts=None, at=None, chunk=False, eos_at=None, **kw):
        """Lay toks on the sung syllables of line lid from word wi0 (or on explicit times `at`).
        chunk=True: a cloud model, every character of a token arrives on the token's first syllable."""
        ts = list(at) if at is not None else syl.times(lid, counts, wi0)
        chars, tok_t, j = ([], [], 0)
        for k, tk in enumerate(toks):
            if tk.text == '<eos>':
                tok_t.append(eos_at)
                continue
            body = [c for c in tk.text if c not in syl.PUNCT]
            n = tk.syl if tk.syl is not None else len(body)
            mine = ts[j:j + n]
            if len(mine) < n:
                raise ValueError(f'token {tk.text!r}: {n} syllables, {len(mine)} left')
            j += n
            tok_t.append(mine[0])
            i = 0
            for c in tk.text:
                if c in syl.PUNCT and chars:
                    chars.append((c, chars[-1][1], k))
                else:
                    chars.append((c, mine[0] if chunk else mine[min(i, n - 1)], k))
                    i += 1
        d = cls(toks, chars, tok_t, eos_at, **kw)
        d._layout()
        return d

    def falls(self) -> list:
        """D1: [(t0, t1)] one per landing (a character, a chunk, <eos>), lit until the next landing."""
        if getattr(self, '_falls', None) is None:
            ts = sorted(set((at for _c, at, _k in self.chars)))
            if self.eos_at is not None:
                ts.append(self.eos_at)
            self._falls = [(a, ts[i + 1] if i + 1 < len(ts) else next_syllable(a)) for i, a in enumerate(ts)]
        return self._falls

    def lit(self, at: float, t: float) -> float:
        """D1: 1 while the thing that landed at `at` is the newest, then settling to 0 over hud.LIVE_FADE."""
        for a, b in self.falls():
            if abs(a - at) < 1e-06:
                return 1.0 if t < b else 1 - ease.prog(t, b, b + hud.LIVE_FADE)
        return 0.0

    def until(self, at: float) -> float:
        for a, b in self.falls():
            if abs(a - at) < 1e-06:
                return b
        return at + 0.5

    def color(self, k: int, at: float, t: float):
        """D1: ink for the stand-in's own habit; her blue, lit only while it is landing."""
        return INK if self.toks[k].src == 'self' else hud.her(self.lit(at, t))

    @property
    def done(self) -> float:
        return self.chars[-1][1]

    def text_at(self, t: float) -> str:
        return ''.join((c for c, at, _k in self.chars if at <= t))

    def n_tok(self, t: float) -> int:
        return sum((1 for x in self.tok_t if x is not None and x <= t))

    def segs(self):
        """Forward passes for the layer strip: one per sung syllable after start."""
        out, prev = ([], self.start)
        for _c, at, _k in self.chars:
            if at > prev + 0.001:
                out.append((prev, at))
                prev = at
        if self.eos_at:
            out.append((prev, self.eos_at))
        return out

    def sung(self) -> list:
        """p5: indices into chars of the sung characters (punctuation rides the one before): one lens column,
        one forward pass, one set of lookback lines each."""
        if getattr(self, '_sung', None) is None:
            self._sung = [i for i, (c, _a, _k) in enumerate(self.chars) if c not in syl.PUNCT]
        return self._sung

    def landed(self, t: float) -> list:
        """p5: the sung characters that have landed by t (chars indices)."""
        return [i for i in self.sung() if self.chars[i][1] <= t]

    def newest(self, t: float):
        """p5: the newest landed sung character (chars index), or None."""
        got = self.landed(t)
        return got[-1] if got else None

    def char_box(self, i: int, t: float | None=None):
        """p5: ink box of big character i where typed() draws it (with its landing drop at t)."""
        c, at, _k = self.chars[i]
        x, y = self.pos[i]
        bx0, by0, bx1, by1 = hud.font(self.big, c, True).getbbox(c)
        drop = 0.0 if t is None else (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -10
        return (x + bx0, y - 8 + drop + by0, x + bx1, y - 8 + drop + by1)

    def eos_box(self):
        """p5: the <eos> chip's box (typed() draws it right of the last line once the answer is done)."""
        if self.eos_at is None:
            return None
        ln = self.toks[self.chars[-1][2]].ln
        cx, y, h = (self.line_end[ln], self.lines[ln], self.big)
        w = _MEAS.textlength('<eos>', font=tl.p.font(22, 'bold'))
        return (cx + 12, y + 44 * h / 78, cx + 28 + w, y + 78 * h / 78)

    def tok_of(self, i: int):
        """p5: (token, index of character i among its token's sung characters)."""
        k = self.chars[i][2]
        n = sum((1 for j in self.sung() if j < i and self.chars[j][2] == k))
        return (self.toks[k], n)

    def passes(self) -> list:
        """p5: [(i, a, b)] one forward pass per sung character i: from the landing before it (or start) to its
        own landing (a local model only; R11)."""
        out, prev = ([], self.start)
        for i in self.sung():
            at = self.chars[i][1]
            out.append((i, prev, at))
            prev = at
        return out

    def lens_steps(self, a: float, b: float) -> list:
        """p5 (短前向, R6): [(time, cells lit)] for the four lower lens cells (layers 12, 24, 36, 48) of a pass from
        a to b; the top one lands with the character at b. The climb starts as the character before lands (a)
        and its steps sit on the 16ths, each >= LENS_MIN_STEP before b; up to four steps, spread evenly over
        the pass; when fewer fit (0.23 s between two syllables holds two), cells share a step, bottom first."""
        pts, k = ([], 0)
        g0 = tl.grid(a - 0.02, 0)
        while True:
            g = tl.grid(g0, k)
            if g > b - LENS_MIN_STEP + 1e-06:
                break
            pts.append(max(g, a))
            k += 1
        if not pts:
            return [(b, 4)]
        if len(pts) > 4:
            pts = [pts[round(j * (len(pts) - 1) / 3)] for j in range(4)]
        m = len(pts)
        return [(pts[s], max((c + 1 for c in range(4) if c * m // 4 == s))) for s in range(m)]

    def lens_cols(self, t: float):
        """p5 (§2.2): (cols, computing) for hud.lens_grid at t: a full column per landed character (top to bottom:
        64 = the character, 48, 36, 24, 12 from Tok.lens), then the column being computed filled from the bottom
        up to the step the pass has reached; old columns stay (R4)."""
        cols, comp = ([], None)
        for j, (i, a, b) in enumerate(self.passes()):
            if t < a:
                break
            tok, n = self.tok_of(i)
            if not tok.lens:
                break
            low = list(tok.lens[n])
            if t >= b:
                top = (self.chars[i][0], tok.src != 'self')
                cols.append([top] + low[::-1])
                continue
            lit = 0
            for at, cells in self.lens_steps(a, b):
                if t >= at:
                    lit = cells
            cols.append([None] + [low[r] if r < lit else None for r in (3, 2, 1, 0)])
            comp = j
            break
        return (cols, comp)

    def lens_head(self, t: float):
        """p5 (forward 标尺): the layer the running pass has reached (0..64) or None, following the lens steps (the
        head reaches a lens tick when its cell lights); and the 0..1 'sampled' flash after each landing."""
        done = 0.0
        for i, a, b in self.passes() + ([(None, self.chars[-1][1], self.eos_at)] if self.eos_at else []):
            if b <= t < b + 0.25:
                done = max(done, 1 - (t - b) / 0.25)
        for i, a, b in self.passes():
            if a <= t < b:
                knots = [(a, 0.0)] + [(at, hud.LENS_ROWS[::-1][n - 1]) for at, n in self.lens_steps(a, b)] + [(b, 64.0)]
                head = 0.0
                for (t0, h0), (t1, h1) in zip(knots, knots[1:]):
                    if t >= t1:
                        head = h1
                    elif t >= t0:
                        head = h0 + (h1 - h0) * ((t - t0) / (t1 - t0) if t1 > t0 else 1.0)
                        break
                return (head, done)
        if self.eos_at and self.chars[-1][1] <= t < self.eos_at:
            a, b = (self.chars[-1][1], self.eos_at)
            return (64 * (t - a) / (b - a), done)
        return (None, done)

    def progress(self, t: float):
        """p5 (第一轮 README): (column being computed, 0..1 of its pass) or None."""
        for j, (i, a, b) in enumerate(self.passes()):
            if a <= t < b:
                return (j, (t - a) / max(1e-06, b - a))
        return None

    def attn_of(self, i: int) -> list:
        """p5: the lookback targets of sung character i (Tok.attn; one list per sung character, or one list for all)."""
        tok, n = self.tok_of(i)
        if not tok.attn:
            return []
        a = tok.attn
        return list(a[n] if isinstance(a[0], list) else a)

    def eos_attn(self) -> list:
        tk = next((tk for tk in self.toks if tk.text == '<eos>'), None)
        if tk is None or not tk.attn:
            return []
        return list(tk.attn[0]) if isinstance(tk.attn[0], list) else list(tk.attn)

    def knock(self, md, t: float, r: int=3):
        """p5 (线从字后面过): the big characters' knockout on a mask (Lookback.composite)."""
        for i, (c, at, _k) in enumerate(self.chars):
            if at > t:
                break
            x, y = self.pos[i]
            drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -10
            hud.halo(md, (x, y - 8 + drop), c, self.big, True, r=r, fill=255)

    def _layout(self):
        n_lines = max((tk.ln for tk in self.toks)) + 1
        widths = [0.0] * n_lines
        for c, _at, k in self.chars:
            widths[self.toks[k].ln] += hud.width(c, self.big, True)
        room = XR - self.x0 - 70
        if max(widths) > room:
            self.big = int(self.big * room / max(widths))
        self.pos, x = ([], [self.x0] * n_lines)
        for c, at, k in self.chars:
            ln = self.toks[k].ln
            self.pos.append((x[ln], self.lines[ln]))
            x[ln] += hud.width(c, self.big, True)
        self.line_end = x
        self.small, xs = ([], self.x0)
        for c, *_r in self.chars:
            self.small.append(xs)
            xs += hud.width(c, 20)

    def typed(self, d, t, shrink=0.0, level=1.0, caret=True, y_small=Y_CONTEXT):
        """The answer, one character per sung syllable; shrink 0..1 morphs it down into the context line."""
        last = None
        for i, (c, at, k) in enumerate(self.chars):
            if at > t:
                break
            colr = self.color(k, at, t)
            drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -10
            size = max(20, int(round(ease.lerp(self.big, 20, shrink))))
            x, y = self.pos[i]
            xx = ease.lerp(x, self.small[i], shrink)
            yy = ease.lerp(y + drop, y_small, shrink)
            hud.tx(d, (xx, yy - 8 * (1 - shrink)), c, size, lv(colr, level), bold=shrink < 0.5)
            last = (i, c, at, k)
        if last is None or shrink > 0 or (not caret):
            return
        i, c, at, k = last
        ln = self.toks[k].ln
        x, y = self.pos[i]
        cx = self.line_end[ln] if t >= self.done else x + hud.width(c, self.big, True)
        h = self.big * 78 / 78
        if self.eos_at is None or t < self.eos_at:
            ph = tl.C.beat_of(t) % 1.0
            if ph < 0.5 or t - at < 0.3:
                d.rectangle((cx + 6, y + 14 * h / 78, cx + 12, y + 92 * h / 78), fill=lv(INK, level))
        else:
            u = ease.prog(t, self.eos_at, self.eos_at + 0.12)
            f = tl.p.font(22, 'bold')
            w = d.textlength('<eos>', font=f)
            ce = hud.her(self.lit(self.eos_at, t))
            d.rounded_rectangle((cx + 12, y + 44 * h / 78, cx + 28 + w, y + 78 * h / 78), radius=6, outline=lv(ce, u * level), width=2)
            d.text((cx + 20, y + 48 * h / 78), '<eos>', font=f, fill=lv(ce, u * level))

    def _prev_time(self, k):
        first = self.tok_t[k]
        before = [at for _c, at, _k in self.chars if at < first - 1e-06]
        return before[-1] if before else self.start

    def _appear(self, k):
        prev_panel = k > 0 and self.toks[k - 1].cands is not None
        return max(self._prev_time(k) + (0.24 if prev_panel else 0.0), self.tok_t[k] - 0.7)

    def span(self, k):
        if self.toks[k].cands is None:
            return None
        at = self.tok_t[k]
        if k == len(self.toks) - 1:
            return (self._appear(k), self.hold if self.hold is not None else at + 0.9)
        end = self.tok_t[k + 1]
        if self.toks[k + 1].cands is not None:
            end = min(end, self._appear(k + 1) - 0.04)
        return (self._appear(k), max(at + 0.2, end))

    def panels(self, d, t, level=1.0, y=PANEL_TOP, x0=None, pw=PW, bar_x=280, bar_w=64):
        for k, tk in enumerate(self.toks):
            sp = self.span(k)
            if sp and sp[0] <= t < sp[1] + 0.12:
                slab(d, t, tk.cands, tk.pick, self.tok_t[k], sp[0], sp[1], self.title, tk.src, x0=self.x0 if x0 is None else x0, y_top=y, level=level, pw=pw, bar_x=bar_x, bar_w=bar_w)

def slab(d, t, cands, pick, at, a0, a1, title, src='self', x0=X0, y_top=PANEL_TOP, pw=PW, level=1.0, right=None, dim_rows=None, lit_until=None, bar_x=280, bar_w=64, min_h=0):
    """pdoom's p(next | ctx) popup on paper: a solid ink slab that unfolds while the pass computes; the pick
    lights on the sung syllable (her blue if it came from her, paper if it is the model's own) and the
    slab folds at a1. dim_rows: {row: 0..1} rows that fade out (G2/G4: her phrase losing).
    lit_until (D1): her pick is lit until then and settles to the quiet blue; default: always quiet.
    bar_x, bar_w (p5): the bar column and its longest bar (a slab narrowed beside the lens grid).
    min_h (p6, round3 "塔头"): the slab folds no lower than this (HEAD: a 24 px cap that stays on the tower)."""
    built = ease.prog(t, a0, at)
    picked = t >= at
    collapse = ease.ease_in(ease.prog(t, a1, a1 + 0.12))
    collapse = max(collapse, 1 - ease.ease_out(ease.prog(t, a0, a0 + 0.12)))
    if collapse >= 1 and min_h <= 0:
        return
    sl = lv(SLAB, level)
    full = HEAD + len(cands) * RH + 8
    h = max(int(min_h), int(full * (1 - collapse)))
    y1 = y_top + full
    y0 = y1 - h
    d.rectangle((x0, y0, x0 + pw, y1), fill=sl)
    if h < HEAD:
        return
    on_slab = lambda a: glyph.level(BG, a, sl)
    d.text((x0 + 12, y0 + 7), title, font=tl.p.font(12), fill=on_slab(0.75))
    rtxt = right if right is not None else 'sampled' if picked else 'computing…'
    d.text((x0 + pw - 12, y0 + 7), rtxt, font=tl.p.font(12), fill=on_slab(0.75), anchor='ra')
    pmax = max((pp for _, pp in cands)) or 1.0
    for i, (text, pr) in enumerate(cands):
        ry = y0 + HEAD + i * RH
        if ry + RH > y1 + 1:
            break
        on = picked and i == pick
        fade = 1.0 - 0.75 * (dim_rows or {}).get(i, 0.0)
        if on:
            k_lit = 0.0 if lit_until is None else 1.0 if t < lit_until else 1 - ease.prog(t, lit_until, lit_until + hud.LIVE_FADE)
            fill = hud.her(k_lit, level) if src != 'self' else lv(BG, level)
            d.rectangle((x0 + 2, ry + 1, x0 + pw - 2, ry + RH - 2), fill=fill)
            fg = BG if src != 'self' else sl
        else:
            fg = on_slab((0.82 if picked else 0.6) * fade)
        hud.tx(d, (x0 + 26, ry + 5), text, 16, fg, bold=on)
        if on:
            d.polygon([(x0 + 10, ry + 8), (x0 + 18, ry + 14), (x0 + 10, ry + 20)], fill=fg)
        grow = 1.0 if picked else ease.ease_out(built)
        bw = max(2, bar_w * pr / pmax * grow) if pr > 0 else 1
        d.rectangle((x0 + bar_x, ry + 10, x0 + bar_x + bw, ry + 18), fill=fg if on else on_slab(0.45 * fade))
        d.text((x0 + pw - 12, ry + 7), f'{pr:.2f}', font=tl.p.font(13), fill=fg, anchor='ra')
BAR_W = [300, 214, 336, 252, 176, 318, 236, 196]

def think_bars(d, t, t0, n=8, unfold=0.0, stop=None, level=1.0, top=PANEL_TOP, folded=False, y=None):
    """The hidden thinking: n redaction bars grown on the 16ths from t0; they fold into a thin row after the
    last one (Y_FOLD, or y: p5's persona layout uses P_FOLD) and unfold into the content area while unfold > 0
    (after `stop`)."""
    a = tl.grid(t0, 0)
    if t < a:
        return
    yf = Y_FOLD if y is None else y
    d.text((X0, yf - 2), '<think>', font=tl.p.font(11), fill=lv(INK, 0.75 * level))
    last = tl.grid(t0, n - 1)
    fold = ease.ease_io(ease.prog(t, last + 0.06, last + 0.2))
    for k in range(n):
        w = BAR_W[k % len(BAR_W)]
        g = tl.grid(t0, k)
        grow = ease.ease_out(ease.prog(t, g, g + 0.07))
        if grow <= 0:
            break
        big = 1 - fold if stop is None or t < stop else unfold
        if folded:
            big = 0.0
        fx0, fy0 = (X0 + 60 + k * 30, yf + 1)
        bx0, by0 = (X0, top + 8 + k * 32)
        x0 = ease.lerp(fx0, bx0, big)
        y0 = ease.lerp(fy0, by0, big)
        ww = ease.lerp(24, w, big) * grow
        hh = ease.lerp(6, 18, big)
        y0 += (1 - big) * 1.5
        d.rectangle((x0, y0, x0 + ww, y0 + hh), fill=lv(SLAB, level))

def prompt_chips(d, t, commits, sent_at, y=Y_PROMPT, level=1.0, split=None):
    """Your message as token chips with their ids, word by word as the IME commits. commits = [(t, word)];
    split(word) -> tokens (default: the word itself). Returns the x where the row ends (p5: chip_boxes() gives
    each chip's box, the same arithmetic)."""
    d.text((X0, y + 6), 'user', font=tl.p.font(12), fill=lv(INK, 0.7 * level))
    x = X0 + 50
    sent = t >= sent_at
    for at, w in commits:
        if at > t:
            break
        for tok in split(w) if split else [w]:
            tw = hud.width(tok, 22, True)
            drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.12))) * -6
            hud.tx(d, (x, y + drop), tok, 22, lv(INK, level), True)
            by = y + 32
            bl = lv(INK, (0.85 if sent else 0.5) * level)
            d.line([(x, by), (x + tw, by)], fill=bl)
            d.line([(x, by - 4), (x, by)], fill=bl)
            d.line([(x + tw, by - 4), (x + tw, by)], fill=bl)
            d.text((x, by + 3), str(glyph.token_id(tok)), font=tl.p.font(10), fill=lv(INK, 0.55 * level))
            x += max(tw, d.textlength('00000', font=tl.p.font(10))) + 12
    return x
_MEAS = ImageDraw.Draw(Image.new('RGB', (1, 1)))
BAR_SPANS = [(X0 + 60 + k * 30, X0 + 84 + k * 30) for k in range(8)]

def chip_boxes(commits, t, y=Y_PROMPT, split=None):
    """p5 (第一轮 README: prompt_chips 返回每个小块的框): [(token, (x0, y0, x1, y1))] of the chips prompt_chips()
    draws at t; y1 is the bracket's line (the lines land just under it)."""
    out, x = ([], X0 + 50)
    fid = tl.p.font(10)
    for at, w in commits:
        if at > t:
            break
        for tok in split(w) if split else [w]:
            tw = hud.width(tok, 22, True)
            out.append((tok, (x, y, x + tw, y + 32)))
            x += max(tw, _MEAS.textlength('00000', font=fid)) + 12
    return out

def persona_row(d, t, y=Y_PERSONA, level=1.0, text='你是大肥鱼'):
    """p5 (§2.1, R1): `persona: 你是大肥鱼`, the system prompt the process prints: context token 0, where every
    token's sink line lands. A bracket under it like the chips'. Returns the bracket (x0, x1, y)."""
    x = X0
    x += hud.tx(d, (x, y), 'persona:', 16, lv(INK, 0.6 * level))
    x += 8
    w = hud.tx(d, (x, y - 2), text, 16, lv(INK, 0.9 * level))
    by = y + 20
    bl = lv(INK, 0.5 * level)
    d.line([(x, by), (x + w, by)], fill=bl)
    d.line([(x, by - 3), (x, by)], fill=bl)
    d.line([(x + w, by - 3), (x + w, by)], fill=bl)
    return (x, x + w, by)

def persona_geom(y=Y_PERSONA, text='你是大肥鱼'):
    x = X0 + hud.width('persona:', 16) + 8
    return (x, x + hud.width(text, 16), y + 20)

def knock_context(md, t, commits, sent_at, y_prompt=P_PROMPT, y_fold=P_FOLD, y_persona=Y_PERSONA, split=None):
    """p5 (线从字后面过): the knockout of the context rows the lines cross: the persona row, the user label, the
    chips and their ids, the <think> label (drawn on a mask, see Lookback.composite)."""
    hud.halo(md, (X0, y_persona), 'persona:', 16, fill=255)
    hud.halo(md, (X0 + hud.width('persona:', 16) + 8, y_persona - 2), '你是大肥鱼', 16, fill=255)
    md.text((X0, y_prompt + 6), 'user', font=tl.p.font(12), fill=255, stroke_width=3, stroke_fill=255)
    for w, (x0, y0, _x1, _y1) in chip_boxes(commits, t, y_prompt, split):
        hud.halo(md, (x0, y0), w, 22, True, fill=255)
        md.text((x0, y0 + 35), str(glyph.token_id(w)), font=tl.p.font(10), fill=255, stroke_width=3, stroke_fill=255)
    md.text((X0, y_fold - 2), '<think>', font=tl.p.font(11), fill=255, stroke_width=3, stroke_fill=255)

class Lookback:
    """p5 (GEN_PLAN §2.1; D22; round2 V1): attention as one-pixel elbow lines. When a token lands on its syllable
    it sends 1-3 lines (Tok.attn) to the context: the persona row (the sink), your message's chips, her files.
    Routes (V1 bus): a short riser from the character up to a bus over the first big line, one lane per kind of
    target; a riser up to the persona row or a chip; along the lane to the trunk beside the memory strip and
    down (or up) to her block. Lines to the same kind of target share the lane and the trunk. A second-line
    character goes up into the free row between the big lines and up a gutter of the first line.
    Thinning (主代理的瘦身规则, GEN_PLAN §2.1): while a token is the newest landing (until the next one, then
    over hud.LIVE_FADE, as its character's D1 light) all its lines show, the line into her file lit (HER_LIVE),
    the others ink; after that it keeps only the line into her file, at INK 0.25 (dotted: V3); the sink and
    chip lines only for the newest. Each line grows over LENS_GROW from the token to its target."""
    LANES = {'chip': -21, 'persona': -18, 'file': -15}

    def __init__(self, dec, trunk_x=110, dotted=False, clear=6):
        self.dec, self.trunk_x, self.dotted, self.clear = (dec, trunk_x, dotted, clear)
        self._ink = {}
        boxes0 = [dec.char_box(i) for i in dec.sung() if dec.toks[dec.chars[i][2]].ln == 0]
        boxes1 = [dec.char_box(i) for i in dec.sung() if dec.toks[dec.chars[i][2]].ln == 1]
        top0 = round(min((b[1] for b in boxes0)))
        self.bus = {k: top0 + v for k, v in self.LANES.items()}
        self.gap_y = round((max((b[3] for b in boxes0)) + min((b[1] for b in boxes1))) / 2) if boxes0 and boxes1 else None

    def landings(self, t):
        """[(key, at, targets)] for every landing so far: sung characters (key = chars index), then <eos>."""
        out = [(i, self.dec.chars[i][1], self.dec.attn_of(i)) for i in self.dec.landed(t)]
        e = self.dec.eos_at
        if e is not None and t >= e and self.dec.eos_attn():
            out.append(('eos', e, self.dec.eos_attn()))
        return out

    def hits(self, t, grow=LENS_GROW):
        """[(strip key, time)] the read pulses: her block is hit as a line reaches it (hud.Pulse, as before)."""
        out = []
        for _key, at, targets in self.landings(t):
            for sp in targets:
                if sp[0] == 'file':
                    out.append((tl.HER_FILES.index(sp[1]), at + grow))
                elif sp[0] == 'archive':
                    out.append(('archive', at + grow))
        return out

    def _ink1(self, t):
        """bool[x]: columns with ink in the first big line (the gutters a second-line riser goes up)."""
        key = tuple((i for i in self.dec.landed(t) if self.dec.toks[self.dec.chars[i][2]].ln == 0))
        if key not in self._ink:
            img = Image.new('L', (tl.p.W, tl.p.H), 0)
            md = ImageDraw.Draw(img)
            for i in key:
                c = self.dec.chars[i][0]
                x, y = self.dec.pos[i]
                md.text((x, y - 8), c, font=hud.font(self.dec.big, c, True), fill=255)
            import numpy as np
            self._ink[key] = (np.asarray(img) > 40).any(axis=0)
        return self._ink[key]

    def _gutter(self, cx, ink):
        """x where a second-line riser goes up through the first line: cx itself if that column is clear of ink,
        else the clear column nearest cx among the gaps between the first line's tokens (word boundaries: a line
        never slices a word), clear of the ink by `clear` px."""
        c = self.clear
        clear = lambda x: not ink[max(0, x - c):x + c + 1].any()
        if clear(cx):
            return cx
        dec, bounds = (self.dec, [])
        for k, tk in enumerate(dec.toks):
            first = next((i for i, (_c, _a, kk) in enumerate(dec.chars) if kk == k), None)
            if tk.ln == 0 and first is not None and (dec.pos[first][0] > dec.x0 + 1):
                bounds.append(dec.pos[first][0])
        bounds.append(dec.line_end[0])
        best = None
        for b in bounds:
            xs = [x for x in range(int(b) - 24, int(b) + 25) if clear(x)]
            if xs:
                x = min(xs, key=lambda v: abs(v - b))
                if best is None or abs(x - cx) < abs(best - cx):
                    best = x
        return cx if best is None else best

    def origin(self, key, t):
        if key == 'eos':
            x0, y0, x1, _y1 = self.dec.eos_box()
            return (round((x0 + x1) / 2), round(y0) - 4, 1)
        x0, y0, x1, _y1 = self.dec.char_box(key, t)
        return (round((x0 + x1) / 2), round(y0) - 4, self.dec.toks[self.dec.chars[key][2]].ln)

    def target(self, sp, ctx):
        if sp == 'persona':
            return ctx['sink']
        if sp[0] == 'chip':
            w, (x0, _y0, x1, y1) = ctx['chips'][sp[1]]
            idw = _MEAS.textlength(str(glyph.token_id(w)), font=tl.p.font(10))
            xs = [x for x in range(int(x0 + idw + 4), int(x1 - 1)) if all((not a - 2 <= x <= b + 2 for a, b in BAR_SPANS))]
            c = (x0 + x1) / 2
            return (min(xs, key=lambda x: abs(x - c)) if xs else round(c), int(y1) + 1)
        if sp[0] == 'file':
            return hud.strip_point(tl.HER_FILES.index(sp[1]), ctx['t'], ctx['hits'])
        return hud.archive_point(ctx['t'], ctx['hits'])

    def path(self, key, sp, t, ctx):
        """The route of one line: [points] from the token to the target, and the junction on the bus."""
        kind = 'persona' if sp == 'persona' else 'file' if sp[0] in ('file', 'archive') else 'chip'
        lane = self.bus[kind]
        cx, top, ln = self.origin(key, t)
        if ln == 0:
            pts = [(cx, top), (cx, lane)]
        else:
            gx = self._gutter(cx, self._ink1(t))
            pts = [(cx, top), (cx, lane)] if gx == cx else [(cx, top), (cx, self.gap_y), (gx, self.gap_y), (gx, lane)]
        junction = pts[-1]
        tx_, ty = self.target(sp, ctx)
        if kind == 'file':
            pts += [(self.trunk_x, lane), (self.trunk_x, ty), (tx_, ty)]
        else:
            pts += [(tx_, lane), (tx_, ty)]
        return (kind, pts, junction)

    def draw(self, ld, t, ctx):
        """Draw on the line layer ld (RGBA). Returns the ticks to draw over the knockout: [(xy, colour, r)]."""
        dec, old_lines, live = (self.dec, [], [])
        for key, at, targets in self.landings(t):
            k = dec.lit(at, t)
            u = ease.ease_out(ease.prog(t, at, at + LENS_GROW))
            for sp in targets:
                kind, pts, j = self.path(key, sp, t, ctx)
                if k > 0:
                    live.append((k, u, kind, pts, j, key))
                elif kind == 'file':
                    old_lines.append((pts, j))
        ticks = []
        old_c = lv(INK, 0.45) if self.dotted else lv(INK, 0.25)
        for pts, j in old_lines:
            hud.trace(ld, pts, old_c, dotted=self.dotted, under=False)
        for pts, j in old_lines:
            ticks.append((j, lv(INK, 0.4 if self.dotted else 0.3), 1))
        order = {'persona': 0, 'chip': 1, 'file': 2}
        live.sort(key=lambda x: (x[0], order[x[2]]))
        for k, u, kind, pts, j, key in live:
            if kind == 'file':
                col = glyph.mix(old_c, hud.HER_LIVE, k)
            elif kind == 'persona':
                col = lv(INK, 0.55 * k)
            else:
                col = lv(INK, 0.9 * k)
            hud.casing(ld, pts[:-1], u)
            hud.trace(ld, pts, col, u)
            if u >= 1:
                ticks.append((pts[-1], col, 2))
                ticks.append((j, col, 1))
            if k >= 1:
                ticks.append((pts[0], lv(INK, 0.9), 1))
        return ticks

    def composite(self, img, t, ctx, knock, alpha=1.0):
        """Draw the lines on their own layer, cut them where the knockout mask is (knock(md) draws halos on it),
        paste them on img (alpha: the whole layer fades, e.g. at the stop) and put the ticks on top. The page's
        texts are drawn after this, so the lines pass under them."""
        if alpha <= 0.003:
            return
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ticks = self.draw(ImageDraw.Draw(layer), t, ctx)
        mask = Image.new('L', img.size, 0)
        knock(ImageDraw.Draw(mask))
        a = ImageChops.subtract(layer.getchannel('A'), mask)
        if alpha < 1:
            a = a.point(lambda v: int(v * alpha))
        img.paste(layer.convert('RGB'), (0, 0), a)
        d = ImageDraw.Draw(img)
        for xy, col, r in ticks:
            hud.tick(d, xy, glyph.mix(BG, col, alpha) if alpha < 1 else col, r)

class Inside:
    """p5 (GEN_PLAN §2.3): what a model whose weights are at hand shows of its inside on one page of
    `dsh inspect --logits --attn --lens`: the persona row (drawn by the caller), the lookback lines (lines()), the
    logit-lens grid (lens()) and the forward ruler (ruler()). dec carries the script (Tok.lens, Tok.attn);
    commits / sent_at are your message (the chips the lines land on); the thinking's passes run on the 16ths
    from sent_at (as the groups' think_segs). Cloud models never get one (R11, §2.3: weights: closed)."""

    def __init__(self, dec, commits, sent_at, n_think=8, lens_y=hud.LENS_Y0, dotted=False, split=None, y_prompt=P_PROMPT, y_fold=P_FOLD):
        self.dec, self.commits, self.sent_at, self.split = (dec, commits, sent_at, split)
        self.lens_y, self.y_prompt, self.y_fold = (lens_y, y_prompt, y_fold)
        self.look = Lookback(dec, dotted=dotted) if any((tk.attn for tk in dec.toks)) else None
        self.think, prev = ([], sent_at)
        for k in range(n_think):
            g = tl.grid(sent_at, k)
            self.think.append((prev, g))
            prev = g

    def chips(self, t):
        return chip_boxes(self.commits, t, self.y_prompt, self.split)

    def sink(self, t):
        """Where the sink lines land: under the persona bracket, in the gap between your first two chips."""
        bx0, bx1, by = persona_geom()
        ch = self.chips(t)
        gaps = [(a[1][2] + b[1][0]) / 2 for a, b in zip(ch, ch[1:])]
        xs = [g for g in gaps if bx0 + 4 <= g <= bx1 - 4]
        return (round(xs[0]) if xs else round(bx0 + 8), by + 1)

    def hits(self, P):
        """Her blocks pulse as the lines reach them (hud.Pulse, as the token reads did)."""
        if self.look is not None:
            for key, at in self.look.hits(P.t):
                P.hit(key, at, 0.35)
        return P

    def lines(self, img, t, hits, alpha=1.0):
        if self.look is None or t < self.dec.start or alpha <= 0.003:
            return
        ctx = {'t': t, 'hits': hits or {}, 'chips': self.chips(t), 'sink': self.sink(t)}

        def knock(md):
            knock_context(md, t, self.commits, self.sent_at, self.y_prompt, self.y_fold, split=self.split)
            self.dec.knock(md, t)
        self.look.composite(img, t, ctx, knock, alpha)

    def lens(self, d, t, level=1.0, dx=0.0):
        """dx: shift right (the grid rides the frame's right edge while the terminal fills the frame, D2)."""
        if level <= 0.003:
            return
        cols, comp = self.dec.lens_cols(t)
        hud.lens_grid(d, cols, x0=hud.LENS_X0 + dx, label_x=hud.LENS_X_LABEL + dx, y0=self.lens_y, computing=comp, level=level)

    def ruler(self, d, t, level=1.0, right=None):
        head, done = self.dec.lens_head(t)
        if head is None:
            for a0, b0 in self.think:
                if a0 <= t < b0:
                    head = 64 * (t - a0) / max(0.001, b0 - a0)
                elif b0 <= t < b0 + 0.25:
                    done = max(done, 1 - (t - b0) / 0.25)
        hud.layers(d, t, (), 'ruler', right, level, head=head, done=done)
