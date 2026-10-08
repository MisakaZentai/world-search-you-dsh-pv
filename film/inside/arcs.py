"""C2 / G1b: the arcs plate, v12 (inside_lab/v12_fine.py) at the pace of the song (ARRANGE_20261003 §2, §4).

The context it reads is one line of type across the plate (group brackets and tags as in v12); the answer types
into a second, larger line under it, one character on each sung syllable, into an open box. Before a character
lands, its reads are drawn from the box up to the words it looks back at (cubic Beziers with vertical handles,
v12's grammar turned upright); a read of her file turns that file name lit blue and sends a blue wash back down
the arc, then the character drops into the box and a new box opens. Old arcs go pale and fine and stay (R4),
so a finished answer is a complete picture of what it read. The persona is read every time (the sink): a fine,
pale arc. Above the line on the right: the newest character large with its logit-lens column (its own habit at
L12/L24, hers or not at L36/L48, R2 colours) and, for tokens that have them, the runner-ups (invented, X15).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import numpy as np
from .plate import PH, PW, W_FINE, W_MAIN, W_SEC, Plate, bezier, clamp, ink_box, in_out_sine, is_cjk, lerp, out_cubic, partial, prog, smoother, text_w
FS, FM = (28, 21)
FA = 50
CTX_Y, ANS_Y = (268, 468)
TAG_Y = 222
CJK = 'sans:460'
CJK_A = 'sans:520'
MONO = 'mono'
FOOT = CTX_Y + 11
GX, GY, GS = (1040, 198, 148)
LX = 862
CX0, CX1 = (470, 800)
PALE_T = 0.3

class Item:

    def __init__(self, text, key=None, owner='ink', group=None):
        self.text, self.key, self.owner, self.group = (text, key, owner, group)
        self.elide = text == '…'
        if self.elide:
            self.w = FS * 0.62
            self.kind, self.size = (None, FS)
        else:
            self.kind = CJK if any((is_cjk(c) for c in text)) else MONO
            self.size = FS if self.kind == CJK else FM
            self.w = text_w(text, self.size, self.kind)
        self.x = 0.0
        self.n_in = 0

    @property
    def cx(self):
        return self.x + self.w / 2

class ArcsPlate:
    """groups: [(tag, [Item...])]; turn: content.Turn; t_in: the plate starts (the terminal begins to fill)."""

    def __init__(self, turn, groups, t_in, status='', ink_answer=False):
        self.turn, self.groups, self.t_in, self.status = (turn, groups, t_in, status)
        self.ink_answer = ink_answer
        self._layout_line()
        self._layout_answer()
        self._schedule()

    def _layout_line(self):
        inner, outer = (FS * 0.34, FS * 1.05)
        items = [it for _tag, its in self.groups for it in its]
        tot = sum((it.w for it in items))
        n_in = sum((len(its) - 1 for _t, its in self.groups))
        n_out = len(self.groups) - 1
        room = PW - 48 - tot
        k = room / (inner * n_in + outer * n_out) if n_in or n_out else 1.0
        k = min(k, 1.6)
        x = 24.0 + max(0.0, (room - k * (inner * n_in + outer * n_out)) / 2)
        self.items, self.brackets = ({}, [])
        for gi, (tag, its) in enumerate(self.groups):
            gx0 = x
            for j, it in enumerate(its):
                it.x = x
                x += it.w + (inner * k if j < len(its) - 1 else 0)
                if it.key:
                    self.items[it.key] = it
            self.brackets.append((tag, gx0, x, its))
            x += outer * k

    def _layout_answer(self):
        x = 24.0
        self.pos = []
        for c in self.turn.chars:
            self.pos.append(x)
            x += text_w(c.ch, FA, CJK_A) - (2 if c.sung else 8)
        self.ans_end = x

    def _schedule(self):
        sung = [i for i, c in enumerate(self.turn.chars) if c.sung]
        self.sung = sung
        self.a0, self.a1 = ({}, {})
        prev = max(self.turn.start, self.t_in + 0.45)
        self.slow = {}
        for i in sung:
            c = self.turn.chars[i]
            gap = c.t - prev
            if gap > 1.6:
                d = min(gap - 0.25, 4.4)
                self.slow[i] = d
            else:
                d = min(0.5, max(0.14, 0.75 * gap))
            self.a0[i], self.a1[i] = (c.t - d, c.t - 0.38 * min(d, 0.5))
            prev = c.t
        self.feet = {}
        count = {}
        for i in sung:
            for key, _w in self.turn.chars[i].reads:
                count[key] = count.get(key, 0) + 1
        seen = {}
        for i in sung:
            for key, _w in self.turn.chars[i].reads:
                it = self.items.get(key)
                if it is None:
                    continue
                n, k = (count[key], seen.get(key, 0))
                seen[key] = k + 1
                spread = min(7.0, max(2.5, it.w * 0.7 / max(1, n)))
                self.feet[i, key] = it.cx + (k - (n - 1) / 2) * spread

    def slot_box(self, x):
        return (x + 2, ANS_Y - FA * 0.9 - 4, x + FA * 0.94, ANS_Y + 9)

    def src_point(self, i, j, n):
        x = self.pos[i]
        cx = x + FA * 0.48 + (j - (n - 1) / 2) * 6.0
        return (cx, ANS_Y - FA * 0.9 - 6)

    def arc_pts(self, i, key, j, n):
        xs, ys = self.src_point(i, j, n)
        xa = self.feet.get((i, key))
        if xa is None:
            return None
        ya = FOOT
        k = 0.5 * (ys - ya)
        return bezier((xs, ys), (xs, ys - k), (xa, ya + k), (xa, ya), 140)

    def window(self, i, j, n):
        """(start, reached) of read j of character i: together, or one after another for a slow character."""
        if i not in self.slow:
            return (self.a0[i], self.a1[i])
        a0, end = (self.a0[i], self.turn.chars[i].t - 0.25)
        step = (end - a0) / max(1, n)
        return (a0 + j * step, a0 + j * step + 0.62 * step)

    def landed(self, t):
        return [i for i in self.sung if self.turn.chars[i].t <= t]

    def render(self, t):
        P = Plate()
        tc = self.turn
        done = self.landed(t)
        a_in = prog(t, self.t_in, self.t_in + 0.35)
        if self.status:
            P.text(24, 26, f'{self.status} · step {len(done)}', 12, MONO, 0.7 * a_in, 'ash')
        self._draw_line(P, t)
        self._draw_arcs(P, t)
        self._draw_answer(P, t)
        self._draw_top(P, t)
        return P.compose()

    def _reading(self, t):
        """{key: lit 0..1} words being read right now."""
        out = {}
        for i in self.sung:
            c = self.turn.chars[i]
            n = len(c.reads)
            for j, (key, w) in enumerate(c.reads):
                if key == 'persona':
                    continue
                s0, s1 = self.window(i, j, n)
                if s1 - 0.04 <= t < c.t + 0.3:
                    u = prog(t, s1 - 0.04, s1 + 0.06) * (1 - prog(t, c.t + 0.08, c.t + 0.3))
                    out[key] = max(out.get(key, 0.0), u)
        return out

    def _draw_line(self, P, t):
        lit = self._reading(t)
        for gi, (tag, x0, x1, its) in enumerate(self.brackets):
            a = out_cubic(prog(t, self.t_in + 0.06 + 0.12 * gi, self.t_in + 0.42 + 0.12 * gi))
            if a <= 0:
                continue
            dy = (1 - a) * -8
            P.line([(x0, TAG_Y + 9 + dy), (x1, TAG_Y + 9 + dy)], W_FINE, 0.8 * a)
            P.line([(x0, TAG_Y + 9 + dy), (x0, TAG_Y + 14 + dy)], W_FINE, 0.8 * a)
            P.line([(x1, TAG_Y + 9 + dy), (x1, TAG_Y + 14 + dy)], W_FINE, 0.8 * a)
            P.text(x0, TAG_Y + dy, tag, 12, MONO, 0.85 * a, 'ash')
            n_tok = sum((max(1, len(it.text) // (3 if it.kind == MONO else 1)) for it in its if not it.elide))
            if x1 - x0 > 90:
                P.text(x1, TAG_Y + dy, f'{n_tok} tok', 11, MONO, 0.6 * a, 'ash', 'rs')
            for it in its:
                if it.elide:
                    cy = CTX_Y - FS * 0.36 + dy
                    for k in range(3):
                        P.circle(it.x + FS * 0.08 + k * FS * 0.2, cy, FS * 0.045, 0.75 * a)
                    continue
                u = lit.get(it.key, 0.0) if it.key else 0.0
                y = CTX_Y + dy
                if it.owner == 'her':
                    P.text(it.x, y, it.text, it.size, it.kind, a * (1 - u), 'quiet')
                    P.text(it.x, y, it.text, it.size, it.kind, a * u, 'blue')
                elif it.owner == 'faint':
                    P.text(it.x, y, it.text, it.size, it.kind, 0.45 * a, 'ash')
                else:
                    P.text(it.x, y, it.text, it.size, it.kind, a, 'ink')
                    if u > 0:
                        P.line([(it.x, y + 6), (it.x + it.w * out_cubic(u), y + 6)], W_SEC, u)

    def _draw_arcs(self, P, t):
        nxt = {i: self.sung[k + 1] if k + 1 < len(self.sung) else None for k, i in enumerate(self.sung)}
        order = []
        for i in self.sung:
            if t < self.a0[i]:
                continue
            c = self.turn.chars[i]
            j2 = nxt[i]
            pale = smoother(prog(t, self.a0[j2], self.a0[j2] + PALE_T)) if j2 is not None else 0.0
            order.append((-pale, i, c, pale))
        order.sort(key=lambda o: (o[0], o[1]))
        for _o, i, c, pale in sorted(order, key=lambda o: -o[3]):
            n = len(c.reads)
            for j, (key, w) in enumerate(c.reads):
                pts = self.arc_pts(i, key, j, n)
                if pts is None:
                    continue
                s0, s1 = self.window(i, j, n)
                if t < s0:
                    continue
                phi = in_out_sine(prog(t, s0, s1))
                if key == 'persona':
                    wd, val = (W_FINE, lerp(0.55, 0.26, pale))
                else:
                    wd = lerp(W_SEC + (W_MAIN - W_SEC) * w, W_FINE, pale)
                    val = lerp(1.0, 0.36, pale)
                seg = partial(pts, phi) if phi < 1 else pts
                P.line(seg, wd, val, 'ink')
                if phi >= 1:
                    xa, ya = pts[-1]
                    P.circle(xa, ya, 1.6 if key != 'persona' else 1.0, val)
                if key.startswith('file:') or key == 'archive':
                    t0, t1 = (s1, c.t)
                    if t0 <= t < c.t + 0.35:
                        f = 1 - in_out_sine(prog(t, t0, t1 + 0.02))
                        fade = 1 - prog(t, c.t + 0.05, c.t + 0.35)
                        if f < 0.999:
                            P.line(partial(pts, 1.0, f) if f > 0 else pts, wd + 0.6, 0.95 * fade, 'blue')

    def _draw_answer(self, P, t):
        tc = self.turn
        if t < self.t_in + 0.45:
            return
        last = None
        for i, c in enumerate(tc.chars):
            if c.t > t:
                break
            last = i
            x = self.pos[i]
            drop = (1 - out_cubic(prog(t, c.t, c.t + 0.14))) * -12
            a = prog(t, c.t, c.t + 0.06)
            if c.hers and (not self.ink_answer):
                nxt_t = next((d.t for d in tc.chars[i + 1:] if d.sung and d.t > c.t), c.t + 0.5)
                live = 1 - prog(t, nxt_t, nxt_t + 0.3)
                P.text(x, ANS_Y + drop, c.ch, FA, CJK_A, a * (1 - live), 'quiet')
                P.text(x, ANS_Y + drop, c.ch, FA, CJK_A, a * live, 'blue')
            else:
                P.text(x, ANS_Y + drop, c.ch, FA, CJK_A, a, 'ink')
        nxt = last + 1 if last is not None else 0
        while nxt < len(tc.chars) and (not tc.chars[nxt].sung):
            nxt += 1
        if nxt < len(tc.chars):
            x = self.pos[nxt]
            a = prog(t, self.t_in + 0.45, self.t_in + 0.7)
            if last is not None:
                a *= prog(t, tc.chars[last].t + 0.04, tc.chars[last].t + 0.16)
            bx0, by0, bx1, by1 = self.slot_box(x)
            P.rect(bx0, by0, bx1, by1, 0.85 * a, 'ink', W_SEC)
        elif tc.eos_at is not None and t >= tc.eos_at:
            x = self.ans_end + 10
            a = prog(t, tc.eos_at, tc.eos_at + 0.12)
            P.text(x, ANS_Y - 8, '<eos>', 20, 'monob', a, 'ink')

    def _draw_top(self, P, t):
        tc = self.turn
        landed = self.landed(t)
        if not landed:
            return
        i = landed[-1]
        c = tc.chars[i]
        prev = landed[-2] if len(landed) > 1 else None
        u = 1.0
        nxt_t = next((tc.chars[j].t for j in self.sung if tc.chars[j].t > c.t), c.t + 0.6)
        live = 1 - prog(t, nxt_t, nxt_t + 0.3)
        t_top = getattr(self, 'top_in', None)
        t_top = tc.chars[landed[0]].t if t_top is None else t_top
        a_top = prog(t, t_top, t_top + 0.2)

        def glyph(cc, val):
            if val <= 0.003:
                return
            if cc.hers and (not self.ink_answer):
                P.text(GX, GY, cc.ch, GS, 'sans:540', val * (1 - live), 'quiet', 'ms')
                P.text(GX, GY, cc.ch, GS, 'sans:540', val * live, 'blue', 'ms')
            else:
                P.text(GX, GY, cc.ch, GS, 'sans:540', val, 'ink', 'ms')
        if prev is not None and u < 1:
            glyph(tc.chars[prev], 1 - u)
        glyph(c, u)
        p = None
        if c.tok in tc.cands:
            p = tc.cands[c.tok][0][1]
        else:
            p = 0.55 + 0.4 * (ord(c.ch) * 2654435761 % 97 / 97.0)
        P.text(GX - 74, 28, 'L64', 12, MONO, 0.8 * a_top, 'ash')
        P.line([(GX - 44, 24), (GX + 34, 24)], W_FINE, 0.6 * a_top)
        P.text(GX + 74, 28, f'p {p:.2f}', 12, MONO, 0.8 * a_top, 'ash', 'rs')
        for r, (lay, (txt, hers)) in enumerate(zip((48, 36, 24, 12), reversed(c.lens))):
            y = 70 + r * 34
            P.text(LX - 34, y, f'L{lay}', 11, MONO, 0.7 * a_top, 'ash', 'rs')
            for cc_, val in (((txt, hers), u),):
                layer = 'quiet' if hers and (not self.ink_answer) else 'ink'
                P.text(LX, y, txt, 24, CJK, (0.9 if layer == 'quiet' else 0.72) * val * a_top, layer, 'ms')
            if prev is not None and u < 1:
                ptxt, phers = list(reversed(tc.chars[prev].lens))[r]
                layer = 'quiet' if phers and (not self.ink_answer) else 'ink'
                P.text(LX, y, ptxt, 24, CJK, (0.9 if layer == 'quiet' else 0.72) * (1 - u) * a_top, layer, 'ms')
        P.line([(LX + 22, 60), (LX + 22, 176)], W_FINE, 0.5 * a_top)
        tok = None
        for j in self.sung:
            if t >= self.a0[j]:
                tok = tc.chars[j].tok
        if tok is None or tok not in tc.cands:
            return
        first = next((j for j in self.sung if tc.chars[j].tok == tok))
        a = prog(t, self.a0[first], self.a0[first] + 0.15)
        win = prog(t, tc.chars[first].t, tc.chars[first].t + 0.1)
        for r, (txt, pr) in enumerate(tc.cands[tok][:4]):
            y = 70 + r * 34
            top = r == 0
            val = a * (lerp(0.75, 1.0, win) if top else lerp(0.75, 0.5, win))
            layer = 'ink' if not top or not tc.chars[first].hers or self.ink_answer else 'blue'
            if top and layer == 'blue':
                P.mixed(CX0, y, txt, 20, val * (1 - win * 0), layer)
            else:
                P.mixed(CX0, y, txt, 20, val, 'ink' if top else 'ash')
            bw = 70 * pr / tc.cands[tok][0][1]
            P.rect(CX1 - 100, y - 8, CX1 - 100 + bw, y - 4, val * (0.9 if top else 0.5), 'ink')
            P.text(CX1, y, f'{pr:.2f}', 12, MONO, val, 'ink' if top else 'ash', 'rs')
