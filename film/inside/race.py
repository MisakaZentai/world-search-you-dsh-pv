"""G2 / G4: the rank race, v10 (inside_lab/v10_fine.py) at the pace of the song (ARRANGE_20261003 §2, §4).

The merged one is about to end its turn. Its candidates race through the layers: the logit lens at each layer
ranks them, a line per candidate, layer by layer. Her phrase (the perfect line's template, blue: it is hers) is in
the race for the first time and leads in the middle layers; on the perfect line's stressed syllable <eos> (its own,
ink) overtakes it, and at L64 <eos> wins. The layer cursor moves one step per sung syllable; her phrase's tokens go
grey one per syllable as it loses (the first cut's slab did the same, R5).

  orient "h"  G2: layers left to right, ranks top down (the v10 picture)
  orient "v"  G4: layers bottom up, ranks left to right (the second failure drawn as threads rising, v11's sense)
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import numpy as np
from .plate import PH, PW, W_FINE, W_MAIN, W_SEC, Plate, lerp, out_cubic, prog, smooth, text_w
MONO = 'mono'
CJK = 'sans:460'
KEY_L = [1, 12, 24, 36, 48, 64]

class RacePlate:
    """cands: [(text, kind, ranks at KEY_L, p at L64)], kind 'her' | 'eos' | 'other'.
    syll: the sung syllables the cursor steps on; cross: the syllable index where <eos> overtakes;
    her_dim: times her phrase's tokens go grey; tokens: her phrase split into tokens."""

    def __init__(self, cands, syll, t_in, eos_at, orient='h', status='', her_tokens=(), her_dim=()):
        self.cands, self.syll, self.t_in, self.eos_at = (cands, list(syll), t_in, eos_at)
        self.orient, self.status = (orient, status)
        self.her_tokens, self.her_dim = (list(her_tokens), list(her_dim))
        n = len(self.syll)
        self.lay_at = [(self.syll[k], 1 + 63 * (k + 1) / n) for k in range(n)]
        if orient == 'h':
            self.x0, self.x1 = (130.0, 670.0)
            self.y0, self.dy = (74.0, 46.0)
        else:
            self.yb, self.yt = (476.0, 70.0)
            self.xr0, self.dx = (200.0, 78.0)

    def cursor(self, t):
        L = 1.0
        prev_t, prev_L = (self.t_in + 0.35, 1.0)
        for at, lay in self.lay_at:
            if t < at - 0.14:
                break
            u = out_cubic(prog(t, at - 0.14, at + 0.06))
            L = lerp(prev_L, lay, u)
            prev_t, prev_L = (at, lay)
        return L

    @staticmethod
    def rank(c, L):
        ks = c[2]
        if L <= KEY_L[0]:
            return float(ks[0])
        for i in range(len(KEY_L) - 1):
            a, b = (KEY_L[i], KEY_L[i + 1])
            if L <= b:
                u = (L - a) / (b - a)
                u = u * u * u * (u * (6 * u - 15) + 10)
                return ks[i] + (ks[i + 1] - ks[i]) * u
        return float(ks[-1])

    def xy(self, L, r):
        if self.orient == 'h':
            return (self.x0 + (L - 1) / 63 * (self.x1 - self.x0), self.y0 + (r - 1) * self.dy)
        return (self.xr0 + (r - 1) * self.dx, self.yb - (L - 1) / 63 * (self.yb - self.yt))

    def render(self, t):
        P = Plate()
        a = prog(t, self.t_in, self.t_in + 0.3)
        L = self.cursor(t)
        if self.status:
            P.text(0, 14, f'{self.status} · L{int(round(L)):02d}', 12, MONO, 0.7 * a, 'ash')
        self._axis(P, t, a, L)
        order = sorted(range(len(self.cands)), key=lambda i: {'other': 0, 'eos': 1, 'her': 2}[self.cands[i][1]])
        for i in order:
            self._line(P, t, a, L, self.cands[i])
        self._panel(P, t, a, L)
        return P.compose()

    def _axis(self, P, t, a, L):
        if self.orient == 'h':
            y = self.y0 + 7.5 * self.dy + 6
            P.line([(self.x0, y), (self.x1, y)], W_FINE, 0.7 * a)
            for lay in (1, 12, 24, 36, 48, 64):
                x, _ = self.xy(lay, 1)
                P.line([(x, y), (x, y + 5)], W_FINE, 0.7 * a)
                P.text(x, y + 18, f'L{lay}', 11, MONO, 0.7 * a, 'ash', 'ms')
                P.line([(x, self.y0 - 14), (x, y)], W_FINE, 0.12 * a)
            cx, _ = self.xy(L, 1)
            P.line([(cx, self.y0 - 18), (cx, y)], W_SEC, 0.85 * a)
        else:
            x = self.xr0 - 46
            P.line([(x, self.yb), (x, self.yt)], W_FINE, 0.7 * a)
            for lay in (1, 12, 24, 36, 48, 64):
                _, y = self.xy(lay, 1)
                P.line([(x - 5, y), (x, y)], W_FINE, 0.7 * a)
                P.text(x - 9, y + 4, f'L{lay}', 11, MONO, 0.7 * a, 'ash', 'rs')
                P.line([(x, y), (self.xr0 + 7.4 * self.dx, y)], W_FINE, 0.12 * a)
            _, cy = self.xy(L, 1)
            P.line([(x, cy), (self.xr0 + 7.4 * self.dx, cy)], W_SEC, 0.85 * a)

    def _line(self, P, t, a, L, c):
        text, kind, ranks, p_end = c
        ls = np.arange(1.0, max(1.01, L) + 1e-06, 0.25)
        pts = np.array([self.xy(l_, self.rank(c, l_)) for l_ in ls])
        lead = self.rank(c, L) < 1.5
        if kind == 'her':
            wd, layer, val = (W_MAIN, 'blue', 1.0)
        elif kind == 'eos':
            wd, layer, val = (W_MAIN if lead else W_SEC + 0.4, 'ink', 1.0)
        else:
            wd, layer, val = (W_FINE + 0.2, 'ash', 0.75)
        P.line(pts, wd, val * a, layer)
        hx, hy = pts[-1]
        P.circle(hx, hy, 2.6 if kind != 'other' else 1.6, val * a, layer)
        size = 17 if kind != 'other' else 13
        if self.orient == 'h':
            lx, ly, anc = (hx + 12, hy + size * 0.36, 'ls')
        else:
            lx, ly, anc = (hx, hy - (34 if kind == 'her' else 12), 'ms')
        if kind == 'her' and self.her_tokens:
            self._her_label(P, t, a, lx, ly, size, anc)
        else:
            P.mixed(lx, ly, text, size, a * (val if kind != 'eos' else 1.0), layer if kind != 'other' else 'ash', anchor=anc)

    def _her_label(self, P, t, a, x, y, size, anc):
        """Her phrase, token by token: each goes grey on its syllable (her_dim) as it loses."""
        toks = self.her_tokens
        ws = [text_w(tk, size, CJK) for tk in toks]
        tot = sum(ws)
        if anc[0] == 'm':
            x -= tot / 2
        for k, (tk, w_) in enumerate(zip(toks, ws)):
            g = prog(t, self.her_dim[k], self.her_dim[k] + 0.1) if k < len(self.her_dim) else 0.0
            P.text(x, y, tk, size, CJK, a * (1 - g), 'blue')
            P.text(x, y, tk, size, CJK, a * g * 0.8, 'ash')
            x += w_

    def _panel(self, P, t, a, L):
        """Right: the top three at the cursor's layer with p; when <eos> lands, it large."""
        x0 = 880 if self.orient == 'h' else 860
        P.text(x0, 70, f'p( next | ctx ) · L{int(round(L)):02d}', 12, MONO, 0.85 * a, 'ink')
        P.line([(x0, 78), (PW - 4, 78)], W_SEC, 0.8 * a)
        u = (L - 1) / 63
        order = sorted(self.cands, key=lambda c: self.rank(c, L))
        sharp = 0.5 + 2.6 * u
        wts = [np.exp(-sharp * (self.rank(c, L) - 1)) for c in order]
        tot = sum(wts)
        ranked = order[:3]
        for k, c in enumerate(ranked):
            text, kind, ranks, p_end = c
            p = p_end if u >= 0.999 else max(0.004, wts[k] / tot)
            y = 108 + k * 34
            layer = 'blue' if kind == 'her' else 'ink' if k == 0 else 'ash'
            txt = text
            while text_w(txt, 15, CJK) > 180 and len(txt) > 2:
                txt = txt[:-2] + '…'
            P.mixed(x0, y, txt, 15, a, layer)
            P.rect(x0, y + 6, x0 + 150 * min(1.0, p), y + 9, a * (0.9 if k == 0 else 0.5), 'blue' if kind == 'her' else 'ink')
            P.text(PW - 4, y, f'{p:.2f}', 11, MONO, a, 'ink' if k == 0 else 'ash', 'rs')
        if t >= self.eos_at:
            e = prog(t, self.eos_at, self.eos_at + 0.08)
            drop = (1 - out_cubic(prog(t, self.eos_at, self.eos_at + 0.16))) * -10
            P.text(x0, 300 + drop, '<eos>', 54, 'monob', e, 'ink')
            P.text(x0, 330, 'turn ends · mem_refs 0', 12, MONO, 0.7 * e, 'ash')
