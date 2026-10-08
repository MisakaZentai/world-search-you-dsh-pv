"""r14 sample (sample_r14/README.md, D51; G_FOCUS_20261005.md): G with its camera locked, the change put inside.

The owner on r13: "g的放大不是很舒服，然后如果把放大去掉，页面的变化又太少". r12's camera (six punches, the dolly in line 57,
a constant drift) made most of the plate's frame change: 3.49 with it, 0.60 with it locked (g_focus/). Here the
camera stays on the whole plate (WIDE, no drift) and the change comes from inside the machine, three ways:

  focus       the machine rests at ~60%; the bay doing the work (context, attention, MoE, unembed, output) comes back
              to full ink inside a heavier frame, in a pass's real order; backwards through line 57's gradient
  values      what a head reads comes home along its arm as a chip: the character it weighted most, 好 from each of
              the 18 stand-in files (an empty chip from each one that only waited), the very pixels of her avatar
  callouts    one magnified card a line beside the part, the page still: <think> crossing <wait> (flower), the
              attribution (delicate), the six experts of 开 (bloom), <eos> crossing 好 (me), the prefill stopping at
              L20 (send), her avatar against its own and then the parts it copied (warmth .. hair), <eos> again (me)

Every number is r12's. Interlude 3 is r13's (inside/g_r13.py); its small drift comes in over the second after G5.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import numpy as np
from . import plate as PL
from .g_r12 import GCOLS, GP_, GRID_X0, GRID_Y0, HEAD_NAMES, N_ENC, P1, P4, P7, TEMPLATE, WIDE, CamPlate, experts, gx
from .g_r13 import G13, _compose, _mask
from .g_section import BAR_LEN, BAR_X0, BUS_Y, CANVAS, CX0, CX1, GY0, GY1, HEAD_YS, HH, HIS_LINES, HIS_X, HX0, HX1, MONO, MONO_B, MX0, MX1, NOW, OUT, SANS, SANS_B, STAND_TICKS, THUMB, TICK_Y0, TICK_Y1, W_BOX, W_CONN, chamfer, hatch, row_y, tick_x, tracked
from .plate import clamp, lerp, out_cubic, prog, smooth
REGIONS = {'ctx': ((CX0 - 5, 55, CX1 + 5, NOW[3] + 5), 0.85), 'att': ((MX0 + 10, 52, 428, BUS_Y - 16), 0.6), 'moe': ((436, 52, 660, BUS_Y - 16), 0.6), 'unb': ((668, 52, MX1 - 10, BUS_Y - 16), 0.6), 'out': ((OUT[0] - 5, OUT[1] - 5, OUT[2] + 5, OUT[3] + 5), 0.75)}
REST_ELSE = 0.8

def env(dt):
    """A focus hit at dt = t - hit: up over 0.06 s, held 0.06 s, down over 0.28 s (one bay at a time, not all)."""
    if dt < -0.06:
        return 0.0
    if dt < 0:
        return out_cubic((dt + 0.06) / 0.06)
    if dt < 0.06:
        return 1.0
    return max(0.0, 1 - smooth((dt - 0.06) / 0.28))

def p_of(stops, tok):
    return [next((p for x, p in row if x == tok), 0.0) for row in stops]

def top_chars(s, ws):
    i = int(np.argmax(ws))
    if i + 1 < len(ws) and ws[i] - ws[i + 1] <= 0.03:
        return s[i:i + 2]
    return s[i]

class G14(G13):

    def __init__(self):
        super().__init__()
        T, S = (self.T, self.S)
        self.copy_syl = self._copy_syllables()
        self.hits = self._hits()
        self.reg_mask = {r: _mask(WIDE, [rect]) for r, (rect, _lv) in REGIONS.items()}
        base = np.full_like(next(iter(self.reg_mask.values())), REST_ELSE)
        for r, (_rect, lv) in REGIONS.items():
            base = base + (lv - base) * self.reg_mask[r]
        self.base = base
        sw = [T['AVATAR_AT'], S[61][1], S[61][2], S[61][3]]
        self.bands = sw
        ru = T['UNRULY'][1]
        regions = [(at, reg, lab) for at, reg, lab in T['ZOOM'] if reg is not None and (not lab.startswith('('))]
        self.regions = regions
        S57 = S[57]
        self.calls = [('cross1', T['FLOWER'], S57[0], (914, 252, 1134, 404), (BAR_X0 + BAR_LEN, row_y(0)), 'UNEMBED · logit lens', '× 2.5', 0.2), ('attr', S57[5] - 0.15, self.msg_t[0], (222, 230, 398, 374), (HIS_X + 37, 332), 'BACKWARD · |∂Δz/∂x · x|', '× 2', 0.2), ('router', T['BLOOM'], S[59][0], (226, 92, 428, 330), (GRID_X0, GRID_Y0 + 6 * GP_), 'MoE · router', '× 2', 0.2), ('cross2', T['EOS1'], T['SEND'] - 0.12, (914, 262, 1134, 420), (BAR_X0 + BAR_LEN, row_y(0)), 'UNEMBED · logit lens', '× 2.5', 0.12), ('gauge', T['SEND'], T['DRAW_AT'] + 0.4, (446, 54, 704, 150), ((gx(N_ENC) + gx(N_ENC + 1)) / 2, GY1 + 2), 'DEPTH · prefill', '× 2', 0.2), ('copy', T['AVATAR_AT'], ru - 0.05, (446, 92, 664, 336), (THUMB[2] + 2, (THUMB[1] + THUMB[3]) / 2), 'H13 · copy', '× 3', 0.15), ('cross3', T['EOS2'], self.FILL[0] - 0.16, (446, 92, 664, 300), (684, 208), 'UNEMBED · logit lens', '× 2.5', 0.16)]

    def _cam(self, t):
        return WIDE

    def _wob(self, t):
        return smooth(prog(t, self.T['G5'], self.T['G5'] + 1.0))

    def _copy_syllables(self):
        """Lines 61-62: the sung syllables while a part of her face is being copied (warmth .. hair): one trip each."""
        T, S = (self.T, self.S)
        zs = [(at, reg) for at, reg, lab in T['ZOOM'] if reg is not None and (not lab.startswith('('))]
        out = []
        for k, (at, reg) in enumerate(zs):
            nxt = zs[k + 1][0] if k + 1 < len(zs) else T['UNRULY'][1]
            sy = [x for x in S[61] + S[62] if at - 0.01 <= x < nxt - 0.05]
            out += [(x, reg, i, len(sy)) for i, x in enumerate(sy)]
        return out

    def _hits(self):
        T, S = (self.T, self.S)
        H = []
        for t0, t1, stops, _c, name in self.passes:
            kind = name.split(':')[0]
            d = max(0.05, t1 - t0)
            if stops:
                seg = [t0] + [at for _l, at in stops]
                for a, b in zip(seg, seg[1:]):
                    dd = b - a
                    H += [(a + 0.15 * dd, 'att'), (a + 0.45 * dd, 'moe'), (a + 0.78 * dd, 'unb')]
                H.append((t1, 'out'))
            elif kind == 'prefill':
                H += [(t0, 'ctx'), (t0 + 0.5 * d, 'att')]
            elif kind == 'think':
                H += [(t0 + 0.3 * d, 'att'), (t0 + 0.6 * d, 'moe'), (t1, 'out')]
            else:
                H += [(t0 + 0.2 * d, 'att'), (t0 + 0.5 * d, 'moe'), (t0 + 0.8 * d, 'unb'), (t1, 'out')]
        S57 = S[57]
        H += [(S57[0], 'unb'), (S57[1], 'moe'), (S57[2], 'att'), (S57[3], 'ctx'), (S57[5], 'ctx'), (S57[6], 'ctx'), (S57[7], 'ctx'), (S57[8], 'ctx')]
        for t0, t1, kind, _tg in self.reads:
            H.append((t0, 'ctx'))
            x = t0 + 0.42
            while x < t1:
                H.append((x, 'ctx'))
                x += 0.42
        for at, _w in T['COMMITS']:
            H.append((at, 'ctx'))
        for x, _reg, _i, _n in self.copy_syl:
            H += [(x, 'ctx'), (x + 0.1, 'att'), (x + 0.22, 'out')]
        for at, _s in list(T['THINK']) + list(T['THINK_SEE']):
            H.append((at, 'out'))
        H.sort()
        return H

    def _focus(self, t):
        ks = {r: 0.0 for r in REGIONS}
        for at, r in self.hits:
            if at > t + 0.06:
                break
            if at < t - 0.4:
                continue
            ks[r] = max(ks[r], env(t - at))
        return ks

    def _static_w(self, ks, masks=None):
        masks = masks or self.reg_mask
        lit = sum((ks[r] * masks[r] for r in REGIONS))
        return self.base + (1 - self.base) * np.clip(lit, 0, 1)

    def _frames(self, F, ks, scale=1.0):
        for r, k in ks.items():
            if k < 0.02:
                continue
            x0, y0, x1, y1 = REGIONS[r][0]
            F.line(chamfer(x0 + 3, y0 + 3, x1 - 3, y1 - 3, 7), W_BOX * 1.3, 0.85 * k * scale)

    def render(self, t):
        T = self.T
        if t >= T['G5']:
            return self._render3(t)
        cam = WIDE
        S = CamPlate(*cam)
        self._draw_static(S, t)
        P = CamPlate(*cam)
        for f in (self._gauge, self._flow, self._now_card, self._memory, self._history, self._reads, self._moe, self._unembed, self._output, self._chips, self._backward, self._copy_bands):
            f(P, t)
        F = CamPlate(*cam)
        ks = self._focus(t)
        self._frames(F, ks)
        C = CamPlate(*cam)
        cm = self._callouts(C, t)
        a_in = out_cubic(prog(t, T['T0'], T['T0'] + 0.3))
        under = 1.0 if cm is None else 1 - 0.985 * cm
        W = self._static_w(ks)
        return _compose([(S, W * under * a_in), (P, under * a_in), (F, under * a_in), (C, a_in)])

    def _shut(self, cam, t):
        out = super()._shut(cam, t)
        k = smooth(prog(t, self.T['G5'], self.FILL[0]))
        if k < 1:
            masks = {r: _mask(cam, [rect]) for r, (rect, _lv) in REGIONS.items()}
            base = np.full((PL.PH, PL.PW), REST_ELSE, np.float32)
            for r, (_rect, lv) in REGIONS.items():
                base = base + (lv - base) * masks[r]
            lit = np.clip(sum((self._focus(t)[r] * masks[r] for r in REGIONS)), 0, 1)
            W = base + (1 - base) * lit
            S, w = out[0]
            out[0] = (S, w * (W + (1 - W) * k))
        return out

    def _overlay3(self, cam, t):
        if t >= self.FILL[0] + 0.05:
            return ([], None)
        F = CamPlate(*cam)
        self._frames(F, self._focus(t), 1 - smooth(prog(t, self.T['G5'], self.FILL[0])))
        C = CamPlate(*cam)
        cm = self._callouts(C, t, cam)
        return ([(F, 1.0), (C, 1.0)], None if cm is None else 1 - 0.985 * cm)

    def _chip_text(self, P, x, y, s, a, layer='ink', size=11.0):
        cjk = any((PL.is_cjk(c) for c in s))
        w = (PL.text_w(s, size, SANS_B) if cjk else PL.text_w(s, size * 0.86, MONO_B)) + 8
        P.rect(x - w / 2, y - 9, x + w / 2, y + 7, 0.12 * a, layer)
        P.rect(x - w / 2, y - 9, x + w / 2, y + 7, 0.9 * a, layer, width=1.0)
        P.mixed(x, y + 3, s, size, a, layer, anchor='ms', cjk=SANS_B, mono=MONO_B)

    def _chip_pixels(self, P, x, y, cells, a, layer, c=3.2):
        i0, j0, i1, j1 = cells
        w, h = ((i1 - i0) * c, (j1 - j0) * c)
        lx, ty = (x - w / 2, y - h / 2)
        P.rect(lx - 2, ty - 2, lx + w + 2, ty + h + 2, 0.9 * a, layer, width=1.0)
        for j in range(j0, j1):
            for i in range(i0, i1):
                v = 1 - self.av[j][i] / 255
                if v > 0.04:
                    P.rect(lx + (i - i0) * c, ty + (j - j0) * c, lx + (i - i0 + 1) * c, ty + (j - j0 + 1) * c, v * 0.95 * a, layer)

    def _cells_of(self, kind, target):
        n = self.n
        if kind == 'thumb':
            if target[0] == 'rows':
                nst = len(self.T['DRAW_STEPS'])
                j0, j1 = (int(n * target[1] / nst), max(int(n * target[1] / nst) + 1, int(n * (target[1] + 1) / nst)))
                return (0, j0, n, j1)
            if target[0] == 'band':
                k, nb = (target[1], target[2])
                return (0, int(n * k / nb), n, int(n * (k + 1) / nb))
            if target[0] == 'region':
                i0, j0, s = target[1]
                return (i0, j0, min(n, i0 + s), min(n, j0 + s))
        if kind == 'cell':
            i, j = target
            return (i, j, i + 1, j + 1)
        return None

    def _reads(self, P, t):
        heads_busy = {}
        back = self.in_backward(t)
        for (t0, t1, kind, target), inf in zip(self.reads, self.rinfo):
            hi = inf['head']
            if kind == 'fan':
                if not t0 - 0.15 <= t < t1 + 0.3:
                    continue
                k = out_cubic(prog(t, t0 - 0.15, t0)) * (1 - prog(t, t1, t1 + 0.3))
                hy = HEAD_YS[hi]
                n = target[0]
                ticks = STAND_TICKS if n >= 18 else STAND_TICKS[::6][:n]
                tmpl = target[2] == TEMPLATE
                for j in ticks:
                    x = tick_x(j)
                    pts = np.array([(HX0, hy), (MX0 + 18, hy), (MX0 - 4, TICK_Y0 - 14), (x, TICK_Y0 - 4)])
                    P.line(PL.partial(pts, k), 0.7 if n >= 18 else 1.2, 0.75 * k)
                    if t >= t0:
                        u = ((t - t0) / 0.55 + j * 0.13) % 1.0
                        bp = PL.partial(pts[::-1], u)[-1]
                        if bp[0] < CX1 + 6:
                            continue
                        if tmpl:
                            P.rect(bp[0] - 5, bp[1] - 7, bp[0] + 5, bp[1] + 5, 0.15 * k, 'quiet')
                            P.rect(bp[0] - 5, bp[1] - 7, bp[0] + 5, bp[1] + 5, 0.85 * k, 'quiet', width=0.8)
                            P.text(bp[0], bp[1] + 2.5, '好', 7.5, SANS_B, 0.95 * k, 'quiet', anchor='ms')
                        else:
                            P.rect(bp[0] - 4, bp[1] - 4, bp[0] + 4, bp[1] + 4, 0.75 * k, width=0.8)
                heads_busy[hi] = max(heads_busy.get(hi, 0), k)
                continue
            if back and kind == 'hist':
                continue
            if not t0 - 0.14 <= t < t1 + 0.25:
                continue
            hy = HEAD_YS[hi]
            pt, box = self._target(kind, target)
            if pt is None:
                continue
            reach = out_cubic(prog(t, t0 - 0.14, t0))
            gone = prog(t, t1, t1 + 0.25)
            k = reach * (1 - gone)
            pts = self._arm(hy, pt)
            P.line(PL.partial(pts, reach), 1.6, 0.95 * (1 - gone))
            lit = 1 - prog(t, t0, t0 + 0.3)
            her = kind in ('thumb', 'cell')
            if box is not None and her:
                bx0, by0, bx1, by1 = box
                P.rect(bx0 - 1, by0 - 1, bx1 + 1, by1 + 1, k * lit, 'blue', width=1.6)
                P.rect(bx0 - 1, by0 - 1, bx1 + 1, by1 + 1, k * (1 - lit), 'quiet', width=1.6)
            if kind == 'cell' and t >= t0:
                i, j = target
                hv = '0123456789abcdef'[int(round(clamp(self.her(i, j)) * 15))]
                u = out_cubic(prog(t, t0, t0 + 0.15)) * (1 - gone)
                P.text(THUMB[2] + 10, THUMB[1] + 58, f'her ({i},{j})', 9, MONO, 0.9 * u, 'quiet')
                P.text(THUMB[2] + 10, THUMB[1] + 72, f"= '{hv}'", 12, MONO_B, u, 'blue' if lit > 0.01 else 'quiet')
            if inf['alpha'] and kind != 'hist' and (t >= t0):
                P.text(MX0 - 8, pt[1] - 5 if kind != 'now' else pt[1] - 8, f'α .{int(round(inf['alpha'] * 100)):02d}', 8.5, MONO_B, 0.85 * k, anchor='rs')
            if t0 <= t < t1 + 0.1:
                u = clamp((t - t0) / 0.42 % 1.0) if t < t1 else 1.0
                if kind == 'thumb' and target[0] == 'region':
                    trips = [x for x, reg, _i, _n in self.copy_syl if reg == target[1] and x <= t]
                    if trips:
                        x = trips[-1]
                        u = smooth(prog(t, x, x + 0.34))
                bp = PL.partial(pts[::-1], max(0.002, u))[-1]
                a = (1 - gone) * (1 - smooth(prog(u, 0.85, 1.0)))
                if her:
                    cells = self._cells_of(kind, target)
                    if cells:
                        lay = 'blue' if lit > 0.5 else 'quiet'
                        if kind == 'cell':
                            self._chip_text(P, bp[0], bp[1], f"'{'0123456789abcdef'[int(round(clamp(self.her(*target)) * 15))]}'", a, lay, 10)
                        else:
                            c = 3.2 if cells[2] - cells[0] <= 12 else 2.2
                            self._chip_pixels(P, bp[0], bp[1], cells, a, lay, c)
                elif kind == 'hist':
                    ws = inf['chars'] or [0.1] * len(target)
                    self._chip_text(P, bp[0], bp[1], top_chars(target, ws), a)
                elif kind == 'now':
                    self._chip_text(P, bp[0], bp[1], '看你' if target == '让我看看你' else '想你', a)
            heads_busy[hi] = max(heads_busy.get(hi, 0), k)
        for hi, k in heads_busy.items():
            yh = HEAD_YS[hi]
            P.rect(HX0 + 2, yh - HH + 2, HX1 - 2, yh + HH - 2, 0.12 * k)
            for m in range(16):
                x = HX0 + 8 + m * 7.4
                h = 2 + 8 * (0.5 + 0.5 * math.sin(m * 1.7 + hi)) * k
                P.line([(x, yh + 7), (x, yh + 7 - h)], 2.0, 0.7 * k)
            P.text(HX1, yh - HH - 3, HEAD_NAMES[hi], 8.5, MONO_B, k, anchor='rs')

    def _copy_bands(self, P, t):
        """61-62: the band of the part copied on this syllable, on her face and on its drawing at once."""
        cur = [(x, reg, i, nn) for x, reg, i, nn in self.copy_syl if x - 0.04 <= t < x + 0.5]
        if not cur:
            return
        x, (i0, j0, s_), i, nn = cur[-1]
        kk = out_cubic(prog(t, x - 0.04, x + 0.06)) * (1 - prog(t, x + 0.25, x + 0.5))
        n = self.n
        i1, j1 = (min(n, i0 + s_), min(n, j0 + s_))
        rb0, rb1 = (j0 + (j1 - j0) * i / nn, j0 + (j1 - j0) * (i + 1) / nn)
        for (X0, Y0, X1, _Y1), lay in ((THUMB, 'quiet'), (CANVAS, 'ink')):
            c = (X1 - X0) / n
            P.rect(X0 + i0 * c - 1.5, Y0 + rb0 * c - 1.5, X0 + i1 * c + 1.5, Y0 + rb1 * c + 1.5, kk, lay, width=1.8)
            P.rect(X0 + i0 * c, Y0 + rb0 * c, X0 + i1 * c, Y0 + rb1 * c, 0.18 * kk, lay)

    def _callouts(self, C, t, cam=WIDE):
        rects = []
        for name, t_in, t_out, rect, src, title, tag, fold in self.calls:
            if not t_in - 0.14 <= t < t_out + fold:
                continue
            a = out_cubic(prog(t, t_in - 0.14, t_in)) * (1 - smooth(prog(t, t_out, t_out + fold)))
            if a <= 0.01:
                continue
            dy = (1 - out_cubic(prog(t, t_in - 0.14, t_in))) * 8
            x0, y0, x1, y1 = rect
            r = (x0, y0 + dy, x1, y1 + dy)
            self._callcard(C, r, a, title, tag)
            self._leader(C, r, src, a, prog(t, t_in - 0.14, t_in + 0.06))
            draw = self._c_cross if name.startswith('cross') else getattr(self, '_c_' + name)
            draw(C, r, a, t, t_in, name)
            rects.append(((x0 - 2, y0 + dy - 2, x1 + 9, y1 + dy + 9), a))
        if not rects:
            return None
        m = np.zeros((PL.PH, PL.PW), np.float32)
        for rr, a in rects:
            m = np.maximum(m, _mask(cam, [rr]) * a)
        return m

    def _callcard(self, C, r, a, title, tag):
        x0, y0, x1, y1 = r
        hatch(C, x1, y0 + 8, x1 + 7, y1 + 7, 5.0, 0.45 * a)
        hatch(C, x0 + 8, y1, x1, y1 + 7, 5.0, 0.45 * a)
        C.rect(x0, y0, x1, y1, a, width=W_BOX)
        tracked(C, x0 + 9, y0 + 15, title, 8.5, 0.85 * a, 1.2)
        C.text(x1 - 9, y0 + 15, tag, 9, MONO_B, 0.7 * a, anchor='rs')

    def _leader(self, C, r, src, a, grow):
        x0, y0, x1, y1 = r
        sx, sy = src
        ex = x0 if sx < x0 else x1 if sx > x1 else (x0 + x1) / 2
        ey = min(max(sy, y0 + 10), y1 - 10) if sx < x0 or sx > x1 else y0 if sy < y0 else y1
        pts = np.array([(sx, sy), (ex, ey)], np.float64)
        C.line(PL.partial(pts, clamp(grow)), W_CONN, 0.75 * a)
        C.circle(sx, sy, 2.6, 0.9 * a)

    def _c_cross(self, C, r, a, t, t_in, name):
        """Two candidates through the lens stops (L8 .. L40): the one that wins crosses the one that led."""
        if name == 'cross1':
            rows, (w, l), cap = (P1, ('<think>', '<wait>'), 'crosses between L24 and L32')
            lw = ('ink', 'ash')
        elif name == 'cross2':
            rows, (w, l), cap = (P4, ('<eos>', TEMPLATE), 'crosses between L16 and L24')
            lw = ('ink', 'quiet')
        else:
            rows, (w, l), cap = (P7, ('<eos>', TEMPLATE), '好 never leads · prefix no longer matches')
            lw = ('ink', 'quiet')
        x0, y0, x1, y1 = r
        cx0, cx1, cy0, cy1 = (x0 + 18, x1 - 64, y0 + 30, y1 - 34)
        grow = smooth(prog(t, t_in - 0.08, t_in + 0.4))
        for k in range(5):
            x = lerp(cx0, cx1, k / 4)
            C.line([(x, cy0), (x, cy1)], 0.6, 0.25 * a)
            C.text(x, cy1 + 13, f'L{8 * (k + 1)}', 8.5, MONO, 0.6 * a, anchor='ms')
        C.line([(cx0, cy1), (cx1, cy1)], 0.8, 0.5 * a)
        for tok, lay, wid in ((l, lw[1], 1.5), (w, lw[0], 2.4)):
            ps = p_of(rows, tok)
            pts = np.array([(lerp(cx0, cx1, k / 4), lerp(cy1, cy0, p)) for k, p in enumerate(ps)], np.float64)
            C.line(PL.partial(pts, max(0.01, grow)), wid, a, lay)
            nshow = int(math.floor(grow * 4 + 1e-06)) + 1
            for k in range(nshow):
                C.circle(pts[k][0], pts[k][1], 2.6 if tok == w else 2.0, a, lay)
            if grow >= 0.999:
                lab = f'{tok} {ps[-1]:.2f}'
                C.mixed(cx1 + 8, pts[-1][1] + 4, lab, 12 if tok == w else 10, a, lay, cjk=SANS_B if tok == w else SANS, mono=MONO_B if tok == w else MONO)
        C.mixed(x0 + 9, y1 - 9, cap, 9, 0.7 * a * smooth(prog(t, t_in + 0.3, t_in + 0.5)), msize=8.5)

    def _c_attr(self, C, r, a, t, t_in, name):
        S = self.S[57]
        x0, y0, x1, y1 = r
        rows = [('花', 0.26, S[5]), ('开', 0.12, S[6]), ('想', 0.09, S[7]), ('你', 0.09, S[7]), ('18 files', 0.0, S[8])]
        for k, (lab, v, at) in enumerate(rows):
            u = out_cubic(prog(t, at - 0.06, at + 0.1))
            yy = y0 + 46 + k * 23
            cjk = PL.is_cjk(lab[0])
            C.mixed(x0 + 14, yy, lab, 17 if cjk else 10, a * u, cjk=SANS_B, mono=MONO)
            C.rect(x0 + 62, yy - 11, x0 + 62 + 76 * v / 0.26 * u, yy - 1, 0.9 * a * u)
            C.text(x1 - 12, yy, '≈ 0' if v == 0 else f'.{int(round(v * 100)):02d}', 11, MONO_B, a * u, anchor='rs')

    def _c_router(self, C, r, a, t, t_in, name):
        ids, gates = experts('msg:开')
        x0, y0, x1, y1 = r
        pitch = (x1 - x0 - 28) / GCOLS
        gx0, gy0 = (x0 + 14, y0 + 30)
        for e in range(384):
            rr, cc = divmod(e, GCOLS)
            x, y = (gx0 + cc * pitch, gy0 + rr * pitch)
            C.rect(x, y, x + pitch * 0.72, y + pitch * 0.72, 0.28 * a, 'ash', width=0.6)
        order = sorted(range(6), key=lambda i: -gates[i])
        for n, i in enumerate(order):
            u = out_cubic(prog(t, t_in - 0.05 + 0.05 * n, t_in + 0.08 + 0.05 * n))
            if u <= 0:
                continue
            rr, cc = divmod(ids[i], GCOLS)
            x, y = (gx0 + cc * pitch, gy0 + rr * pitch)
            m = 1.6 * (1 - u)
            C.rect(x - m, y - m, x + pitch * 0.72 + m, y + pitch * 0.72 + m, a * u)
            C.circle(x + pitch * 0.36, y + pitch * 0.36, pitch * 0.9, 0.7 * a * u, width=0.8)
        yb = gy0 + 12 * pitch + 22
        C.mixed(x0 + 14, yb, '6 of 384 lit for 开', 11, a, cjk=SANS_B, mono=MONO_B)
        C.text(x0 + 14, yb + 16, 'gates ' + ' '.join((f'.{int(round(gates[i] * 100)):02d}' for i in order)), 9.5, MONO, 0.85 * a)
        C.text(x0 + 14, yb + 31, '#' + ' #'.join((str(ids[i]) for i in order)), 9, MONO, 0.7 * a)
        C.mixed(x1 - 12, yb + 26, '开', 26, a, anchor='rs', cjk=SANS_B)
        C.text(x1 - 12, yb + 42, 'p .88', 9.5, MONO_B, 0.85 * a, anchor='rs')

    def _c_gauge(self, C, r, a, t, t_in, name):
        T = self.T
        x0, y0, x1, y1 = r
        p, gap = (5.4, 10)
        sx = x0 + 14
        fill = N_ENC * smooth(prog(t, T['SEND'] - 0.02, T['SEND'] + 0.16))
        ya, yb = (y0 + 34, y0 + 52)
        xs = []
        for l in range(1, 41):
            x = sx + (l - 1) * p + (gap if l > N_ENC else 0)
            xs.append(x)
            if l <= fill:
                C.rect(x, ya, x + p - 1.4, yb, 0.9 * a)
            else:
                C.rect(x, ya, x + p - 1.4, yb, 0.55 * a, width=0.6)
        xg = xs[N_ENC - 1] + p + gap / 2 - 0.7
        C.line([(xg, ya - 8), (xg, yb + 8)], 1.4, a)
        C.text(sx, yb + 18, 'enc 1–20', 9, MONO, 0.75 * a)
        C.text(xs[-1] + p, yb + 18, 'dec 21–40', 9, MONO, 0.75 * a, anchor='rs')
        u = smooth(prog(t, T['SEND'] + 0.12, T['SEND'] + 0.3))
        C.mixed(sx, yb + 38, '让我看看你 · prefill stops at L20', 11, a * u, cjk=SANS_B, mono=MONO_B)
        C.text(sx, yb + 54, 'the decoder reads its K/V from L20', 9, MONO, 0.75 * a * u)

    def _c_copy(self, C, r, a, t, t_in, name):
        """Her avatar against its own: first whole (a band a syllable, I'd like all the), then the part named."""
        T = self.T
        x0, y0, x1, y1 = r
        n = self.n
        phase, cells, lab = ('whole', None, '')
        for at, reg, lb in self.regions:
            if t >= at - 0.06:
                phase, cells, lab = ('region', reg, lb)
        flip = max([out_cubic(prog(t, at - 0.06, at + 0.08)) for at, _r, _l in self.regions if t >= at - 0.06] + [1.0])
        lw, gapx = (84.0, x1 - x0 - 28 - 2 * 84.0)
        ax, bx, ty = (x0 + 14, x0 + 14 + lw + gapx, y0 + 34)
        if phase == 'whole':
            c = lw / n
            i0, j0, i1, j1 = (0, 0, n, n)
        else:
            i0, j0, s = cells
            i1, j1 = (min(n, i0 + s), min(n, j0 + s))
            c = lw / max(i1 - i0, j1 - j0)
        for j in range(j0, j1):
            for i in range(i0, i1):
                vh = 1 - self.av[j][i] / 255
                vi = 1 - self.its(i, j)
                if vh > 0.04:
                    C.rect(ax + (i - i0) * c, ty + (j - j0) * c, ax + (i - i0 + 1) * c - 0.4, ty + (j - j0 + 1) * c - 0.4, vh * 0.95 * a * flip, 'quiet')
                if vi > 0.04:
                    C.rect(bx + (i - i0) * c, ty + (j - j0) * c, bx + (i - i0 + 1) * c - 0.4, ty + (j - j0 + 1) * c - 0.4, vi * a * flip)
        hh = (j1 - j0) * c
        C.rect(ax - 1, ty - 1, ax + (i1 - i0) * c + 1, ty + hh + 1, 0.7 * a, 'quiet', width=0.8)
        C.rect(bx - 1, ty - 1, bx + (i1 - i0) * c + 1, ty + hh + 1, 0.7 * a, width=0.8)
        mx = (ax + lw + bx) / 2
        C.line([(mx - 10, ty + hh / 2), (mx + 8, ty + hh / 2)], 1.4, a)
        C.line([(mx + 3, ty + hh / 2 - 4), (mx + 8, ty + hh / 2), (mx + 3, ty + hh / 2 + 4)], 1.4, a)
        if phase == 'whole':
            for k, at in enumerate(self.bands):
                kk = out_cubic(prog(t, at - 0.05, at + 0.05)) * (1 - prog(t, at + 0.3, at + 0.5))
                if kk > 0.01:
                    jb0, jb1 = (n * k / len(self.bands), n * (k + 1) / len(self.bands))
                    for xx in (ax, bx):
                        C.rect(xx - 2, ty + jb0 * c - 1, xx + lw + 2, ty + jb1 * c + 1, kk * a, width=1.6)
            C.text(ax, ty + hh + 16, 'hers', 9.5, MONO_B, 0.9 * a, 'quiet')
            C.text(bx, ty + hh + 16, 'its own', 9.5, MONO_B, 0.9 * a)
        else:
            cur = [(x, i, nn) for x, reg, i, nn in self.copy_syl if reg == cells and x - 0.04 <= t]
            if cur:
                x, i, nn = cur[-1]
                kk = out_cubic(prog(t, x - 0.04, x + 0.06)) * (1 - 0.6 * prog(t, x + 0.25, x + 0.5))
                rows = j1 - j0
                rb0, rb1 = (j0 + rows * i / nn, j0 + rows * (i + 1) / nn)
                for xx in (ax, bx):
                    C.rect(xx - 2, ty + (rb0 - j0) * c - 1, xx + (i1 - i0) * c + 2, ty + (rb1 - j0) * c + 1, kk * a, width=1.8)
            C.text(ax, ty + hh + 16, f'her {lab}', 9.5, MONO_B, 0.9 * a * flip, 'quiet')
            C.text(bx, ty + hh + 16, f'its {lab}', 9.5, MONO_B, 0.9 * a * flip)

def make():
    return G14()
if __name__ == '__main__':
    import sys
    from pathlib import Path
    from PIL import Image
    out = Path(sys.argv[1] if len(sys.argv) > 1 else 'sample_r14/review/plate')
    out.mkdir(parents=True, exist_ok=True)
    g = G14()
    ts = [float(x) for x in sys.argv[2:]] or [234.9, 236.3, 238.2, 239.3, 241.7, 243.2, 245.5, 247.1, 248.6, 250.2, 251.3, 252.6, 255.5, 256.4, 257.5, 259.2, 260.75, 261.0, 261.4]
    for t in ts:
        Image.fromarray(g.render(t)).save(out / f'p_{t:07.2f}.png')
        print(t)
