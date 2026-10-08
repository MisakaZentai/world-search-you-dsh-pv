"""r17 (D59, sample_r17/README.md): r14's plate (inside/g_r14.py, on r13's interlude 3) with one change, in the pair's
plates of interlude 3: the big "=" between the two plates is gone. The two plates stay side by side, their structure
rows identical and on one line, so the viewer compares them; nothing is drawn between them (no "=", no "≠").

The merged one's name comes from cast.py: with DSH_END=story it is the persona's name, 大肥鱼, set in the CJK sans (the
mono face has no CJK glyphs); hers stays `DeepSeek-V4.1-Flash · offline`. Everything else is G13._plates as it was.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from .g_r13 import HRECT, MRECT, MW, PAIR_CX, W_CONN
from .g_r14 import G14
from .g_section import MONO, MONO_B, MX0, MY0, MY1, SANS_B
from .plate import is_cjk, prog

class G17(G14):

    def _plates(self, P, t):
        if t < self.NAMES_AT - 0.24:
            return
        fs = 0.05 * MW
        y1, y2, y3 = (MY1 + 0.075 * MW, MY1 + 0.13 * MW, MY1 + 0.185 * MW)
        spec = '40 = 20 enc + 20 dec · 384 → 6 + 1'

        def typed(s, a, b):
            return s[:int(round(len(s) * prog(t, a, b)))]
        a, b = (self.NAMES_AT - 0.24, self.NAMES_AT)
        m_arch = prog(t, self.closed_at['merged'], self.closed_at['merged'] + 0.15)
        m_face = SANS_B if any((is_cjk(ch) for ch in self.name_m)) else MONO_B
        P.text(MRECT[0], y1, typed(self.name_m, a, b), fs, m_face, 1.0 - 0.45 * m_arch)
        P.text(HRECT[0], y1, typed(self.name_h + ' · offline', a, b), fs, MONO_B, 0.95, 'quiet')
        a, b = (self.PLATES_AT - 0.22, self.PLATES_AT)
        P.text(MRECT[0], y2, typed(spec, a, b), 0.045 * MW, MONO, 0.9 - 0.4 * m_arch)
        P.text(HRECT[0], y2, typed(spec, a, b), 0.045 * MW, MONO, 0.9, 'quiet')
        if t >= self.PLATES_AT - 0.12:
            from .plate import out_cubic
            u = out_cubic(prog(t, self.PLATES_AT - 0.12, self.PLATES_AT + 0.05))
            for yy in (MY0 + 0.1 * MW + 0.085 * MW, MY0 + 0.1 * MW + 0.24 * MW):
                xa, xb = (MX0 + 0.94 * MW, HRECT[0] + 0.06 * MW)
                L = (xb - xa) / 2 * u
                P.line([(xa, yy), (xa + L, yy)], W_CONN, 0.7 * u)
                P.line([(xb - L, yy), (xb, yy)], W_CONN, 0.7 * u, 'ash')
        a0 = self.CLOSES[-1] + 0.15
        if t >= a0:
            from .plate import smooth
            u = smooth(prog(t, a0, self.FOUND))
            P.text(HRECT[0], y3, 'archive · 412 行'[:int(round(15 * prog(t, a0, a0 + 0.2)))], 0.045 * MW, MONO_B, 0.95 * u, 'quiet')
_ = PAIR_CX

def make():
    return G17()
