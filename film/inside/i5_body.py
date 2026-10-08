"""r5 batch 2 (REVISE_R4_20261004.md §3.4, §3.15; D34): a model's body, the forward pane zoomed (tmux zoom), flat.

The forward strip (groups/c_pane.py `_stack`) at a zoom: the layers left to right, per layer an attention cell on
top and an FFN cell under it, from the structures in BO.ARCH (FACTS "X29 补充", "X29 补充（续）"):

  attention   solid = full / global attention, stipple = sparse (DSA / MSA / MLA sparse), outline = linear / window
  FFN         solid = dense, comb = MoE (experts)
  MTP         its MTP cells after a gap (one: GLM-5.3, Hy4 preview, Qwen3.8-27B; three: Step-3.7-Flash, LongCat-2.0)
  enc / dec   her body (the merged one wears it): 20 encoder + 20 decoder layers, a gap between them

D36 (10-04): every model on screen has open weights (FACTS X35), so every body is its real structure; the sealed
dashed box ("结构未公开", FACTS X33) is no longer drawn (UNKNOWN is empty; its code is kept). Nothing is drawn that the
model does not have.

Her blue: the band of her nine sources (persona + eight files) comes in from the left and fills the layers a group
at a time: `fill` = layers filled, (`live0`, `live1`, `live_k`) = the group just reached (the node the picture stands
on) and how lit it still is; the rest settles to her quiet blue (D1). r5 round 2 (D35, R-A): the whole machine is
never lit any more (`flash` is kept for the call signature, callers pass 0); inner() keeps the node moving between
events: her blue runs along the band's lines through the node's layers, and the node's layers are read one after
another (an attention cell lit, the FFN cell of the layer before it after it), at the rate of the harmony.
Ink at three levels, her blue, one-dot lines.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
from PIL import ImageDraw
import hud
from groups import b_open as BO
from hud import BG, HER_LIVE, HER_QUIET, INK
from panes import FAINT, SUB, TXT
from tuikit import ease, glyph
UNKNOWN: set = set()
P = hud.p
N_BAND = 9

def _arch_ready():
    """The stand-ins' and the merged one's structures are set on BO.ARCH by their group modules (d_*, g_*); ERNIE,
    Step and LongCat (D36) are in groups/b_open.py's ARCH itself."""
    if 'glm' not in BO.ARCH:
        from groups import d_lead
    if 'merged' not in BO.ARCH:
        from groups import g_lead

class Body:

    def __init__(self, key, enc_dec=None):
        _arch_ready()
        self.key = key
        self.unknown = key in UNKNOWN
        self.A = None if self.unknown else BO.ARCH[key]
        self.enc_dec = enc_dec
        if self.A:
            self.n = self.A['n']
            self.mtp = BO.mtp_n(self.A)
        else:
            self.n, self.mtp = (10, 0)

    def columns(self, x0, x1):
        """[(x, w, layer index or 'mtp')] across x0..x1."""
        gaps = (12 if self.enc_dec else 0) + (12 if self.mtp else 0)
        n = self.n + self.mtp
        pitch = (x1 - x0 - gaps) / n
        w = max(2.0, pitch - (2 if pitch > 6 else 1))
        out, x = ([], x0)
        for j in range(self.n):
            if self.enc_dec and j == self.enc_dec[0]:
                x += 12
            out.append((x, w, j))
            x += pitch
        if self.mtp:
            x += 12
            for _k in range(self.mtp):
                out.append((x, w, 'mtp'))
                x += pitch
        return out

    def front_x(self, x0, x1, fill):
        """x of the band's front after `fill` layers."""
        cols = self.columns(x0, x1)
        if fill <= 0:
            return x0
        k = min(len(cols) - self.mtp - 1, int(math.floor(fill)))
        k = max(0, k)
        if fill >= self.n:
            x, w, _j = cols[self.n - 1]
            return x + w
        x, w, _j = cols[k]
        return x + (fill - k) * (w + 1)

    def draw(self, d, rect, t, fill=0.0, live0=0.0, live1=0.0, live_k=0.0, flash=0.0, level=1.0, band_in=1.0, labels=True, x_in=None):
        """rect = (x0, y0, x1, y1): the rows (labels to the left in the 40 px margin, ticks under)."""
        x0, y0, x1, y1 = rect
        lx0, lx1 = (x0 + 40, x1 - 40)
        gap = 10
        h = (y1 - y0 - gap) / 2
        ya0, ya1 = (y0, y0 + h)
        yf0, yf1 = (y0 + h + gap, y1)
        fk = ease.clamp(flash)

        def col(c, a):
            c = glyph.level(c, a * level, BG)
            return glyph.mix(c, HER_LIVE, 0.85 * fk) if fk > 0.003 else c

        def blue(c_, k_):
            return glyph.mix(c_, HER_LIVE if k_ > 1 else HER_QUIET, min(1.0, k_ if k_ <= 1 else 1.0))
        if self.unknown:
            self._sealed(d, (lx0, ya0, lx1, yf1), t, fill, live0, live1, live_k, col)
        else:
            self._layers(d, lx0, lx1, ya0, ya1, yf0, yf1, fill, live0, live1, live_k, col, blue, labels)
        hx0 = x1 - 30
        d.rectangle((hx0, ya0, x1, yf1), outline=col(INK, 0.55))
        if labels:
            ft = P.font(10)
            tw = d.textlength('HEAD', font=ft)
            d.text((hx0 + 15 - tw / 2, yf1 + 4), 'HEAD', font=ft, fill=col(INK, SUB))
        if band_in > 0 and fill > 0:
            xf = self.front_x(lx0, lx1, fill) if not self.unknown else lx0 + (lx1 - lx0) * min(1.0, fill / self.n)
            xs = x0 - 6 if x_in is None else x_in
            xe = xs + (xf - xs) * ease.clamp(band_in)
            xl = self.front_x(lx0, lx1, live0) if not self.unknown else lx0 + (lx1 - lx0) * min(1.0, live0 / self.n)
            for k in range(N_BAND):
                y = ya0 + 8 + (yf1 - ya0 - 16) * k / (N_BAND - 1)
                d.line([(xs, y), (min(xe, xl), y)], fill=col(HER_QUIET, 1.0))
                if xe > xl and live_k > 0.01:
                    d.line([(xl, y), (xe, y)], fill=glyph.mix(HER_QUIET, HER_LIVE, live_k))
                elif xe > xl:
                    d.line([(xl, y), (xe, y)], fill=col(HER_QUIET, 1.0))
            if live_k > 0.01 and xe >= xf - 1:
                d.line([(xf, ya0 - 3), (xf, yf1 + 3)], fill=glyph.mix(BG, HER_LIVE, live_k))
        if labels:
            self.row_labels(d, rect, col)

    def row_labels(self, d, rect, col=None):
        """The rows' names in the left margin, on a patch of paper over her lines (3 px clear on every side, R-C)."""
        x0, y0, x1, y1 = rect
        gap = 10
        h = (y1 - y0 - gap) / 2
        ya0, yf0 = (y0, y0 + h + gap)
        if col is None:
            col = lambda c, a: glyph.level(c, a, BG)
        f11 = P.font(11)
        for s_, yy in (('attn', ya0 + h / 2 - 7), ('ffn', yf0 + h / 2 - 7)):
            tw = d.textlength(s_, font=f11)
            d.rectangle((x0 - 3, yy - 2, x0 + tw + 4, yy + 16), fill=BG)
            d.text((x0, yy), s_, font=f11, fill=col(INK, SUB))

    def inner(self, d, rect, l0, l1, phi, labels=True):
        """The node the picture stands on, layers [l0, l1), between events. phi: the inner clock (i5_times.phase).
        Her blue runs along the band's nine lines through the node's layers (two pulses a line, 3.3 crossings per
        unit of phi); its layers are read one after another (12 a unit of phi): the attention cell of the layer
        being read lit her blue, the FFN cell of the layer before it after it. A sealed structure: its hatch, a
        stretch at a time. Nothing outside the node moves."""
        x0, y0, x1, y1 = rect
        lx0, lx1 = (x0 + 40, x1 - 40)
        gap = 10
        h = (y1 - y0 - gap) / 2
        ya0, ya1 = (y0, y0 + h)
        yf0, yf1 = (y0 + h + gap, y1)
        j0, j1 = (int(math.floor(l0 + 1e-06)), int(math.ceil(l1 - 1e-06)))
        j1 = min(j1, self.n)
        if j1 <= j0:
            return
        if self.unknown:
            xa = lx0 + (lx1 - lx0) * j0 / self.n
            xb = lx0 + (lx1 - lx0) * j1 / self.n
            self._sealed_inner(d, (xa, ya0, xb, yf1), phi, (lx0, lx1))
            return
        cols = self.columns(lx0, lx1)
        xa = cols[j0][0]
        xb = cols[j1 - 1][0] + cols[j1 - 1][1]
        span = j1 - j0
        step = phi * 12.0
        j = j0 + int(math.floor(step)) % span
        jp = j0 + (int(math.floor(step)) - 1) % span
        frac = step - math.floor(step)
        x, w, _j = cols[j]
        d.rectangle((x, ya0, x + w, ya1), fill=glyph.mix(HER_QUIET, HER_LIVE, 0.55 + 0.45 * (1 - frac)))
        if span > 1:
            xp, wp, _j = cols[jp]
            d.rectangle((xp, yf0, xp + wp, yf1), fill=glyph.mix(HER_QUIET, HER_LIVE, 0.35 + 0.4 * (1 - frac)))
        L = max(6.0, min(18.0, 0.3 * (xb - xa)))
        for k in range(N_BAND):
            y = ya0 + 8 + (yf1 - ya0 - 16) * k / (N_BAND - 1)
            for m in (0.0, 0.5):
                u = (phi * 3.3 + 0.29 * k + m) % 1.0
                xh = xa + u * (xb - xa + L)
                p0, p1 = (max(xa, xh - L), min(xb, xh))
                if p1 - p0 < 1:
                    continue
                pm = max(p0, p1 - L * 0.45)
                d.line([(p0, y), (pm, y)], fill=glyph.mix(HER_QUIET, HER_LIVE, 0.5))
                d.line([(pm, y), (p1, y)], fill=HER_LIVE)

    def _sealed_inner(self, d, box, phi, full):
        """A sealed structure's node: its hatch lines inside [xa, xb], a 14 px stretch lit, sweeping left to right."""
        xa, y0, xb, y1 = box
        fx0, fx1 = full
        u = phi * 3.3 % 1.0
        xw = xa + u * (xb - xa)
        for k in range(int(fx0) - int(y1 - y0), int(xb), 7):
            a_ = (max(k, fx0 + 1), y1 - 1 - max(0, fx0 + 1 - k))
            b_ = (min(k + (y1 - y0), xb), y1 - 1 - min(y1 - y0 - 2, xb - k))
            if a_[0] > b_[0]:
                continue
            mid = 0.5 * (a_[0] + b_[0])
            if not xa <= mid <= xb or abs(mid - xw) > 14:
                continue
            d.line([a_, b_], fill=HER_LIVE)
        if y1 - y0 < 40:
            return
        s = '结构未公开'
        sw = hud.width(s, 16, True)
        cx, cy = ((fx0 + fx1) / 2, (y0 + y1) / 2)
        d.rectangle((cx - sw / 2 - 10, cy - 15, cx + sw / 2 + 10, cy + 15), fill=BG)
        hud.tx(d, (cx - sw / 2, cy - 11), s, 16, glyph.level(INK, SUB, BG), True)

    def _layers(self, d, lx0, lx1, ya0, ya1, yf0, yf1, fill, live0, live1, live_k, col, blue, labels):
        A = self.A
        cols = self.columns(lx0, lx1)
        full, sparse, dense = (A['full'], A.get('sparse', set()), A['dense'])
        first = A.get('first', 0)
        for x, w, j in cols:
            mtp = j == 'mtp'
            jj = self.n if mtp else j
            filled = jj + 0.5 <= fill
            live = live_k if live0 <= jj < live1 and filled else 0.0
            kq = 0.5 if filled else 0.0
            i = self.n + first if mtp else j + first

            def c(c0, a, _kq=kq, _live=live):
                cc = col(c0, a)
                if _kq > 0:
                    cc = glyph.mix(cc, HER_QUIET, _kq)
                if _live > 0:
                    cc = glyph.mix(cc, HER_LIVE, 0.9 * _live)
                return cc
            if mtp or i in full:
                d.rectangle((x, ya0, x + w, ya1), fill=c(INK, 0.62))
            elif i in sparse:
                d.rectangle((x, ya0, x + w, ya1), fill=c(INK, 0.12))
                dot = c(INK, 0.55)
                for yy in range(int(ya0) + 2, int(ya1) - 1, 3):
                    for xx in range(int(x) + 1 + yy // 3 % 2, int(x + w), 2):
                        d.point((xx, yy), fill=dot)
                d.rectangle((x, ya0, x + w, ya1), outline=c(INK, 0.5))
            else:
                d.rectangle((x, ya0, x + w, ya1), fill=c(INK, 0.18))
                d.rectangle((x, ya0, x + w, ya1), outline=c(INK, 0.5))
            if mtp or i in dense:
                d.rectangle((x, yf0, x + w, yf1), fill=c(INK, 0.55))
            else:
                cc = c(INK, 0.42)
                d.rectangle((x, yf0, x + w, yf1), outline=cc)
                for xx in range(int(x) + 2, int(x + w) - 1, 2):
                    d.line([(xx, yf0 + 2), (xx, yf1 - 2)], fill=cc)
        if not labels:
            return
        ft = P.font(10)
        named = False
        for x, w, j in cols:
            if j == 'mtp':
                if not named:
                    d.text((x - 4, yf1 + 4), 'MTP', font=ft, fill=col(INK, SUB))
                    named = True
            elif j % 10 == 0 or j == self.n - 1:
                s = f'L{j}' if j == 0 else str(j)
                if j == self.n - 1 and j % 10 and (j % 10 < 4):
                    continue
                d.text((x, yf1 + 4), s, font=ft, fill=col(INK, FAINT if j else SUB))
        if self.enc_dec:
            ne = self.enc_dec[0]
            xa, _w, _j = cols[0]
            xb, wb, _j = cols[ne - 1]
            xc, _w, _j = cols[ne]
            xd, wd, _j = cols[self.n - 1]
            f12 = P.font(12)
            for a, b, s in ((xa, xb + wb, f'编码 · {ne} 层'), (xc, xd + wd, f'解码 · {self.n - ne} 层')):
                d.line([(a, ya0 - 6), (b, ya0 - 6)], fill=col(INK, SUB))
                d.line([(a, ya0 - 9), (a, ya0 - 6)], fill=col(INK, SUB))
                d.line([(b, ya0 - 9), (b, ya0 - 6)], fill=col(INK, SUB))
                hud.tx(d, (a, ya0 - 26), s, 12, col(INK, SUB))
            _ = f12

    def _sealed(self, d, box, t, fill, live0, live1, live_k, col):
        """A structure nobody published: a dashed frame, 结构未公开; her band fills it as a hatch, a group a beat."""
        x0, y0, x1, y1 = box
        c = col(INK, 0.5)
        for xx in range(int(x0), int(x1), 8):
            d.line([(xx, y0), (min(xx + 4, x1), y0)], fill=c)
            d.line([(xx, y1), (min(xx + 4, x1), y1)], fill=c)
        for yy in range(int(y0), int(y1), 6):
            d.line([(x0, yy), (x0, min(yy + 3, y1))], fill=c)
            d.line([(x1, yy), (x1, min(yy + 3, y1))], fill=c)
        u = min(1.0, fill / self.n)
        ul0, ul1 = (min(1.0, live0 / self.n), min(1.0, live1 / self.n))
        xf = x0 + (x1 - x0) * u
        if u > 0:
            for k in range(int(x0) - int(y1 - y0), int(xf), 7):
                a_ = (max(k, x0 + 1), y1 - 1 - max(0, x0 + 1 - k))
                b_ = (min(k + (y1 - y0), xf), y1 - 1 - min(y1 - y0 - 2, xf - k))
                if a_[0] <= b_[0]:
                    mid = 0.5 * (a_[0] + b_[0])
                    lit = live_k if x0 + (x1 - x0) * ul0 <= mid <= x0 + (x1 - x0) * ul1 else 0.0
                    d.line([a_, b_], fill=glyph.mix(col(HER_QUIET, 0.8), HER_LIVE, lit))
        if y1 - y0 < 40:
            return
        s = '结构未公开'
        sw = hud.width(s, 16, True)
        cx, cy = ((x0 + x1) / 2, (y0 + y1) / 2)
        d.rectangle((cx - sw / 2 - 10, cy - 15, cx + sw / 2 + 10, cy + 15), fill=BG)
        hud.tx(d, (cx - sw / 2, cy - 11), s, 16, col(INK, SUB), True)

def text_w(s, size, bold=False):
    return hud.width(s, size, bold)
_ = (ImageDraw, TXT)
