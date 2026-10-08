"""The transforming egg of the chorus (REVISE_R4_20261004.md §3.9, DECISIONS D34; r5 second round D35): a Transformer
block diagram in the outline everybody in the field knows (Vaswani et al. 2017, fig. 1), drawn as the decoder-only
stack the stand-ins all are: input embedding, positional encoding, N x [masked multi-head attention, add & norm,
feed forward, add & norm], linear, softmax, output probabilities. Ink lines one pixel wide, hatched drop shadows,
monospace capitals; no colour but ink, paper and her blue (her bar in the softmax, her name in the input).

D35 (owner: a step that stops dead feels stuck, the chords keep going): a signal walks the data path and lands in a
node exactly on a beat (beatmap.arrive); inside the node it has reached, something keeps moving at the rate of the
harmony (beatmap.pad): token dots joined by arcs in the attention, a residual merging and a ruler's marks jumping in
add & norm, a row of neurons breathing in the feed forward, a scan in the linear, the probabilities redistributing in
the softmax (its top bar is the model the nameplate's reel is on). On the lines it has passed, dots keep flowing.

  Fig(cx, top)                        geometry: boxes keyed STAGES, the N x frame, the paths between nodes
  Fig.deck(d, k, dx_step, level)      k copies of the N x frame dealt out to the right (draw before draw())
  Fig.draw(d, st)                     the figure in state st (a Sig): skeleton, inner motion, signal, flows

Generic on purpose: it is the textbook figure, not any one model's real structure, so N is written as N.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import random
from dataclasses import dataclass, field
import cast
import e_reel
import hud
from hud import BG, INK, lv
STAGES = ['in', 'emb', 'attn', 'an1', 'ffn', 'an2', 'lin', 'soft', 'out']
NODES = ['emb', 'attn', 'an1', 'ffn', 'an2', 'lin', 'soft']
LABEL = {'emb': 'INPUT EMBEDDING', 'attn': 'MASKED MULTI-HEAD ATTENTION', 'an1': 'ADD & NORM', 'ffn': 'FEED FORWARD', 'an2': 'ADD & NORM', 'lin': 'LINEAR', 'soft': 'SOFTMAX'}
FONT = 11
HALF = 104
SOFT_HALF = (112, 128)
H = {'soft': 58, 'lin': 32, 'an2': 32, 'ffn': 50, 'an1': 32, 'attn': 56, 'emb': 36}
GAP = 12
DECK_DX = 16
ACT, PAST, AHEAD = (0.92, 0.5, 0.26)

def hyphen_lines(s: str) -> list[str]:
    """D36: a name too long for its line, broken after a hyphen into two lines: the first the longer one, the two as
    even as possible (ERNIE-4.5-21B- / A3B-Thinking; by ernie-4.5-21b- / a3b-thinking), as the dsh sidebar wraps it."""
    best = None
    for i, ch in enumerate(s[:-1]):
        if ch != '-':
            continue
        a, b = (s[:i + 1], s[i + 1:])
        if len(a) >= len(b) and (best is None or len(a) - len(b) < len(best[0]) - len(best[1])):
            best = (a, b)
    return list(best) if best else [s]

@dataclass
class Sig:
    """What the figure shows at one instant."""
    u: float = 0.0
    since: float = 0.0
    phase: float = 0.0
    pad: float = 0.5
    burst: float = 0.0
    reel: str = ''
    reel_since: float = 1.0
    reel_prev: str = ''
    res: dict = field(default_factory=dict)
    her_u: float = 0.0
    in_text: str = ''
    in_fill: tuple = field(default_factory=lambda: INK)
    level: float = 1.0
    shadow: bool = True
    dwell: float = 0.0

class Fig:

    def __init__(self, cx, top):
        self.cx = cx
        b = {}
        y = top
        b['out'] = (cx - 80, y, cx + 80, y + 14)
        y += 14 + GAP
        b['soft'] = (cx - SOFT_HALF[0], y, cx + SOFT_HALF[1], y + H['soft'])
        y += H['soft'] + GAP
        b['lin'] = (cx - HALF, y, cx + HALF, y + H['lin'])
        y += H['lin'] + GAP
        ft = y
        y += 10
        for k in ('an2', 'ffn', 'an1', 'attn'):
            b[k] = (cx - HALF, y, cx + HALF, y + H[k])
            y += H[k] + GAP
        y = y - GAP + 22
        self.fork_y = b['attn'][3] + 12
        self.frame = (cx - HALF - 12, ft, cx + HALF + 28, y)
        self.lane = cx + HALF + 14
        self.plus = (cx, y + 16)
        y += 16 + 8 + GAP
        b['emb'] = (cx - HALF, y, cx + HALF, y + H['emb'])
        y += H['emb'] + 14
        b['in'] = (cx - 130, y, cx + 130, y + 14)
        self.box = b
        self.bottom = y + 14
        self._paths()

    def _paths(self):
        """paths[k]: the polyline from node STAGES[k] to STAGES[k + 1] (exit point to entry point), up the trunk;
        res[k]: the residual polyline that merges into node k (an1, an2)."""
        b, cx = (self.box, self.cx)
        P = {}
        P[0] = [(cx, b['in'][1] - 2), (cx, b['emb'][3])]
        P[1] = [(cx, b['emb'][1]), (cx, self.plus[1] + 8), (cx, self.plus[1] - 8), (cx, b['attn'][3])]
        P[2] = [(cx, b['attn'][1]), (cx, b['an1'][3])]
        P[3] = [(cx, b['an1'][1]), (cx, b['ffn'][3])]
        P[4] = [(cx, b['ffn'][1]), (cx, b['an2'][3])]
        P[5] = [(cx, b['an2'][1]), (cx, b['lin'][3])]
        P[6] = [(cx, b['lin'][1]), (cx, b['soft'][3])]
        P[7] = [(cx, b['soft'][1]), (cx, b['out'][3] + 2)]
        self.paths = P
        y1 = self.frame[3] - 4
        self.res = {'an1': [(cx, y1), (self.lane, y1), (self.lane, (b['an1'][1] + b['an1'][3]) / 2), (b['an1'][2] + 7, (b['an1'][1] + b['an1'][3]) / 2)], 'an2': [(cx, b['an1'][1] - 6), (self.lane, b['an1'][1] - 6), (self.lane, (b['an2'][1] + b['an2'][3]) / 2), (b['an2'][2] + 7, (b['an2'][1] + b['an2'][3]) / 2)]}

    @staticmethod
    def _at(pts, f):
        """The point at fraction f (0..1) of a polyline's length."""
        segs = [(a, c, math.dist(a, c)) for a, c in zip(pts, pts[1:])]
        total = sum((s[2] for s in segs)) or 1.0
        rest = max(0.0, min(1.0, f)) * total
        for a, c, L in segs:
            if rest <= L or L == 0:
                k = rest / L if L else 0.0
                return (a[0] + (c[0] - a[0]) * k, a[1] + (c[1] - a[1]) * k)
            rest -= L
        return pts[-1]

    @staticmethod
    def _len(pts):
        return sum((math.dist(a, c) for a, c in zip(pts, pts[1:])))

    def _shadow(self, d, r, level):
        x0, y0, x1, y1 = r
        hud.hatch(d, (x0 + 4, y1 + 1, x1 + 4, y1 + 4), lv(INK, 0.45 * level), 3)
        hud.hatch(d, (x1 + 1, y0 + 4, x1 + 4, y1 + 4), lv(INK, 0.45 * level), 3)

    def _arrow(self, d, x, y0, y1, level, head=True):
        c = lv(INK, 0.8 * level)
        d.line([(x, y0), (x, y1)], fill=c)
        if head:
            d.polygon([(x - 3, y1 + 5), (x + 3, y1 + 5), (x, y1)], fill=c)

    def zone(self, k):
        """The inside of box k under its label: where its motion is drawn."""
        x0, y0, x1, y1 = self.box[k]
        return (x0 + 6, y0 + 17, x1 - 6, y1 - 4)

    def deck(self, d, k, dx_step, level=1.0):
        """k copies of the N x frame dealt out to the right, behind the figure (the stack unfolds), each one
        painted over the one behind it like cards; nothing of one copy is drawn across another's lines."""
        x0, y0, x1, y1 = self.frame
        for i in range(int(k), 0, -1):
            dx = round(dx_step * i)
            a = level * max(0.3, 1.0 - 0.06 * i)
            r = (x0 + dx, y0, x1 + dx, y1)
            d.rounded_rectangle(r, radius=8, fill=BG, outline=lv(INK, 0.7 * a))
            for kk in ('an2', 'ffn', 'an1', 'attn'):
                bx0, by0, bx1, by1 = self.box[kk]
                d.rounded_rectangle((bx0 + dx, by0, bx1 + dx, by1), radius=4, outline=lv(INK, 0.35 * a))

    def _inner(self, d, k, st, lvl):
        """The motion inside box k, at ink level lvl; st.phase advances at the pad rate (never at zero)."""
        zx0, zy0, zx1, zy1 = self.zone(k)
        ph = st.phase
        c = lv(INK, lvl)
        cf = lv(INK, lvl * 0.45)
        zw, zh = (zx1 - zx0, zy1 - zy0)
        if k == 'emb':
            n = 14
            for i in range(n):
                x = zx0 + 4 + i * (zw - 8) / (n - 1)
                v = 0.5 + 0.5 * math.sin(ph * 2 * math.pi * 0.7 + i * 1.7)
                h = 2 + (zh - 2) * v * (0.55 + 0.45 * st.pad)
                d.line([(round(x), zy1), (round(x), round(zy1 - h))], fill=c)
            return
        if k == 'attn':
            n = 9
            xs = [zx0 + 8 + i * (zw - 16) / (n - 1) for i in range(n)]
            yb = zy1 - 2
            q_f = ph * 1.6 % (n - 1) + 1
            q = int(q_f)
            grow = q_f - q
            rng = random.Random(q * 31 + 7)
            ws = [rng.random() ** 1.5 for _ in range(q)]
            mx = max(ws) if ws else 1.0
            for j in range(q):
                a_ = min(1.0, grow * 2.2 - (q - 1 - j) * 0.12)
                if a_ <= 0:
                    continue
                x_a, x_b = (xs[j], xs[q])
                hgt = min(zh - 5, 5 + 0.32 * (x_b - x_a))
                lvl_j = lvl * (0.3 + 0.7 * ws[j] / mx)
                d.arc((round(x_a), round(yb - hgt), round(x_b), round(yb + hgt)), 180, 180 + 180 * a_, fill=lv(INK, lvl_j))
            for i, x in enumerate(xs):
                r = 2 if i != q else 3
                col = c if i <= q else cf
                d.rectangle((round(x) - r + 1, yb - r + 1, round(x) + r - 1, yb + r - 1), fill=col)
            return
        if k in ('an1', 'an2'):
            yb = zy1 - 1
            mid = (zx0 + zx1) / 2
            d.line([(zx0 + 2, yb), (zx1 - 2, yb)], fill=cf)
            step = 8
            for i in range(-11, 12):
                x = round(mid + i * step)
                if zx0 + 2 <= x <= zx1 - 2:
                    d.line([(x, yb), (x, yb - (4 if i % 4 == 0 else 2))], fill=cf)
            cyc = ph * 1.2
            spread = 0.35 + 0.65 * (0.5 + 0.5 * math.cos(cyc * 2 * math.pi))
            tick = int(cyc * 8)
            rng = random.Random(tick * 13 + (1 if k == 'an1' else 2))
            for m in range(6):
                v = (rng.random() * 2 - 1) * 11 * spread
                x = round(mid + round(v) * step)
                if zx0 + 3 <= x <= zx1 - 3:
                    d.line([(x, yb - 2), (x, yb - zh + 2)], fill=c)
            return
        if k == 'ffn':
            n = 22
            bw = 3
            for i in range(n):
                x = zx0 + 4 + i * (zw - 8 - bw) / (n - 1)
                v = 0.5 + 0.5 * math.sin(ph * 2 * math.pi * 0.55 + i * 2.1)
                act = max(0.0, v - 0.28) / 0.72
                h = (zh - 1) * act * (0.45 + 0.55 * st.pad)
                if h < 1.5:
                    d.point((round(x + 1), zy1), fill=cf)
                    continue
                d.rectangle((round(x), round(zy1 - h), round(x) + bw - 1, zy1), fill=c)
            return
        if k == 'lin':
            n = 40
            sx = zx0 + 2 + ph * 0.9 % 1.0 * (zw - 4)
            for i in range(n):
                x = round(zx0 + 2 + i * (zw - 4) / (n - 1))
                rng = random.Random(i * 7 + int(ph * 0.9))
                h = 2 + (zh - 3) * rng.random() ** 2
                done = x <= sx
                d.line([(x, zy1), (x, round(zy1 - (h if done else 1)))], fill=c if done else cf)
            return
        if k == 'soft':
            self._soft(d, st, lvl)

    def _soft(self, d, st, lvl):
        """Probabilities redistributing over the reel's candidates; the top bar is the model on the reel."""
        zx0, zy0, zx1, zy1 = self.zone('soft')
        keys = SOFT_KEYS
        zh = zy1 - zy0

        def dist(top, seed):
            rng = random.Random(seed)
            w = {k_: 0.15 + 0.55 * rng.random() for k_ in keys}
            w[top] = 2.6
            s = sum(w.values())
            return {k_: v / s for k_, v in w.items()}
        wob = st.phase * 1.1
        a = dist(st.reel_prev, int(wob) * 3 + keys.index(st.reel_prev))
        b = dist(st.reel, int(wob) * 3 + keys.index(st.reel))
        u = min(1.0, st.reel_since / 0.05)
        u = u * u * (3 - 2 * u)
        f = wob % 1.0
        nxt = dist(st.reel, (int(wob) + 1) * 3 + keys.index(st.reel))
        p = {k_: (a[k_] * (1 - u) + b[k_] * u) * (1 - 0.35 * f) + nxt[k_] * 0.35 * f for k_ in keys}
        top = max(keys, key=lambda k_: p[k_])
        mx = p[top]
        bw, gap = (6, 3)
        for i, k_ in enumerate(keys):
            x = zx0 + 2 + i * (bw + gap)
            h = max(1, round((zh - 1) * p[k_] / mx))
            if k_ == 'her':
                col = hud.her(st.her_u, lvl)
            else:
                col = lv(INK, lvl * (1.0 if k_ == top else 0.55))
            d.rectangle((x, zy1 - h, x + bw - 1, zy1), fill=col)
        nx = zx0 + 2 + len(keys) * (bw + gap) + 8
        name = cast.name(top)
        ncol = hud.her(st.her_u, lvl) if top == 'her' else lv(INK, lvl)
        f11 = hud.font(11, name, True)
        lines = [name]
        if f11.getlength(name) > zx1 - 3 - nx:
            lines = hyphen_lines(name)
            if any((f11.getlength(s) > zx1 - 3 - nx for s in lines)):
                lines = [cast.short(top)]
                f11 = hud.font(11, lines[0], True)
        for i, s in enumerate(lines):
            d.text((nx, zy0 + 2 + 11 * i), s, font=f11, fill=ncol)
        py = zy0 + 17 if len(lines) == 1 else zy0 + 2 + 11 * (len(lines) - 1) + 14
        d.text((nx, py), 'p %.2f' % mx, font=hud.font(10, 'p'), fill=lv(INK, lvl * 0.62))

    def _box(self, d, k, lvl, lit, level):
        r = self.box[k]
        self._shadow(d, r, level)
        d.rounded_rectangle(r, radius=5, fill=BG, outline=lv(INK, (0.95 if lit else 0.62) * level))
        f = hud.font(FONT, 'A', bold=lit)
        d.text((r[0] + 6, r[1] + 3), LABEL[k], font=f, fill=lv(INK, (1.0 if lit else 0.72) * level))

    def _flow(self, d, pts, st, lvl, speed=34.0, pitch=13.0, size=1):
        """Dots streaming along a path the signal has passed (the data keeps flowing between hits)."""
        L = self._len(pts)
        if L < 6:
            return
        off = st.phase * speed % pitch
        s = off
        while s < L - 2:
            if s > 2:
                x, y = self._at(pts, s / L)
                d.rectangle((round(x) - size, round(y) - size, round(x) + size, round(y) + size), fill=lv(INK, lvl))
            s += pitch

    def draw(self, d, st: Sig):
        b, cx = (self.box, self.cx)
        level = st.level
        x0, y0, x1, y1 = self.frame
        k_at = int(math.floor(st.u + 1e-09))
        moving = st.u - k_at > 1e-06
        held = not moving or st.u - k_at < st.dwell
        if st.shadow:
            hud.hatch(d, (x1 + 1, y0 + 6, x1 + 6, y1 + 6), lv(INK, 0.3 * level), 3)
            hud.hatch(d, (x0 + 6, y1 + 1, x1 + 6, y1 + 6), lv(INK, 0.3 * level), 3)
        d.rounded_rectangle(self.frame, radius=8, fill=BG, outline=lv(INK, 0.9 * level))
        f = hud.font(22, 'N', True)
        d.text((x0 - 12, (y0 + y1) / 2), 'N×', font=f, fill=lv(INK, level), anchor='rm')
        self._arrow(d, cx, b['in'][1] - 3, b['emb'][3] + 1, level)
        self._arrow(d, cx, b['emb'][1] - 1, self.plus[1] + 9, level)
        self._arrow(d, cx, self.plus[1] - 9, self.fork_y, level, head=False)
        self._arrow(d, cx, self.fork_y, b['attn'][3] + 1, level)
        self._arrow(d, cx, b['attn'][1] - 1, b['an1'][3] + 1, level)
        self._arrow(d, cx, b['an1'][1] - 1, b['ffn'][3] + 1, level)
        self._arrow(d, cx, b['ffn'][1] - 1, b['an2'][3] + 1, level)
        self._arrow(d, cx, b['an2'][1] - 1, y0 + 1, level, head=False)
        self._arrow(d, cx, y0, b['lin'][3] + 1, level)
        self._arrow(d, cx, b['lin'][1] - 1, b['soft'][3] + 1, level)
        self._arrow(d, cx, b['soft'][1] - 1, b['out'][3] + 3, level)
        for dx in (-44, 44):
            d.line([(cx, self.fork_y), (cx + dx, self.fork_y), (cx + dx, b['attn'][3] + 6)], fill=lv(INK, 0.8 * level))
            d.polygon([(cx + dx - 3, b['attn'][3] + 6), (cx + dx + 3, b['attn'][3] + 6), (cx + dx, b['attn'][3] + 1)], fill=lv(INK, 0.8 * level))
        for k in ('an1', 'an2'):
            pts = self.res[k]
            d.line(pts, fill=lv(INK, 0.6 * level))
            tx, ty = pts[-1]
            d.polygon([(tx, ty), (tx + 5, ty - 3), (tx + 5, ty + 3)], fill=lv(INK, 0.6 * level))
        px, py = self.plus
        d.ellipse((px - 8, py - 8, px + 8, py + 8), fill=BG, outline=lv(INK, 0.9 * level))
        d.line([(px - 5, py), (px + 5, py)], fill=lv(INK, level))
        d.line([(px, py - 5), (px, py + 5)], fill=lv(INK, level))
        wx = cx - 52
        d.ellipse((wx - 24, py - 12, wx, py + 12), outline=lv(INK, 0.8 * level))
        wave = [(wx - 22 + i, py - 7 * math.sin(i / 20 * 6.283 + st.phase * 2.0)) for i in range(21)]
        d.line(wave, fill=lv(INK, 0.8 * level))
        d.line([(wx, py), (px - 9, py)], fill=lv(INK, 0.6 * level))
        ff = hud.font(10, 'P')
        d.text((wx - 32, py - 7), 'POSITIONAL', font=ff, fill=lv(INK, 0.6 * level), anchor='rs')
        d.text((wx - 32, py + 6), 'ENCODING', font=ff, fill=lv(INK, 0.6 * level), anchor='rs')
        for i, k in enumerate(NODES):
            si = STAGES.index(k)
            lit = si == k_at and held
            self._box(d, k, 1.0, lit, level)
            if si < k_at or (si == k_at and (not held)):
                lvl = PAST
            elif si == k_at:
                lvl = ACT
            else:
                lvl = AHEAD
            if k == 'soft' or si <= k_at:
                self._inner(d, k, st, lvl * level)
            else:
                self._idle(d, k, lvl * level)
        on = k_at >= STAGES.index('out')
        fo = hud.font(12, 'O', bold=on)
        d.text((cx, (b['out'][1] + b['out'][3]) / 2), 'OUTPUT PROBABILITIES', font=fo, fill=lv(INK, (1.0 if on else 0.7) * level), anchor='mm')
        if st.in_text:
            fi = hud.font(12, st.in_text)
            d.text((cx, (b['in'][1] + b['in'][3]) / 2), st.in_text, font=fi, fill=st.in_fill, anchor='mm')
        for k in range(min(k_at, len(self.paths))):
            self._flow(d, self.paths[k], st, 0.55 * level)
        for k in ('an1', 'an2'):
            si = STAGES.index(k)
            if k_at >= si:
                self._flow(d, self.res[k], st, 0.5 * level, speed=46.0, pitch=16.0)
            elif 0 < st.res.get(k, 0.0) < 1:
                self._dot(d, self._at(self.res[k], st.res[k]), 2, 0.9 * level)
        if moving and k_at < len(self.paths):
            pts = self.paths[k_at]
            fr = st.u - k_at
            for j, lag in enumerate((0.18, 0.12, 0.06)):
                if fr - lag > 0:
                    self._dot(d, self._at(pts, fr - lag), 1, (0.3 + 0.2 * j) * level)
            self._dot(d, self._at(pts, fr), 3, level, ring=True)
        elif k_at == 0:
            (xa, ya), (xb, yb) = self.paths[0]
            self._dot(d, (xa, (ya + yb) / 2), 2, level)

    def _idle(self, d, k, lvl):
        """A node not reached yet: its motion's frame, still and faint."""
        zx0, zy0, zx1, zy1 = self.zone(k)
        c = lv(INK, lvl)
        if k == 'attn':
            n = 9
            for i in range(n):
                x = round(zx0 + 8 + i * (zx1 - zx0 - 16) / (n - 1))
                d.rectangle((x - 1, zy1 - 3, x + 1, zy1 - 1), fill=c)
        elif k in ('an1', 'an2', 'lin', 'emb', 'ffn'):
            d.line([(zx0 + 2, zy1 - 1), (zx1 - 2, zy1 - 1)], fill=c)

    def _dot(self, d, xy, r, level, ring=False, pulse=None):
        x, y = (round(xy[0]), round(xy[1]))
        d.ellipse((x - r, y - r, x + r, y + r), fill=lv(INK, level))
        if ring:
            rr = r + 3 + (0 if pulse is None else round(2 * pulse))
            d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=lv(INK, 0.45 * level))
SOFT_KEYS = list(e_reel.SPIN)
