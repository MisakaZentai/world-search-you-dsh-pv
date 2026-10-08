"""C6 / G3: the attention board, v9 (inside_lab/v9_fine.py) at the pace of the song (ARRANGE_20261003 §2, §4).

Rows are what it can look back at, grouped as in v9 (sys, persona, memory/you/, history, you, its answer); her eight
files get a row each, tall enough to name them (the memory strip, opened out). Columns are query positions: the
prompt's own columns are the cached prefill (the faint causal triangle, already there when the plate opens), and
the answer adds one column per sung syllable. While a column is being computed its cells fill in; the cell of the
file of hers it reads lights blue, your words are ink (R2); then its character lands in the column head. Cells
stay (R4): a finished answer leaves a fingerprint. After <eos> her rows are tallied (one count per eighth note).
Right: p( next | ctx ) of the newest column (runner-ups invented, X15) and its logit-lens column.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import numpy as np
from .plate import PH, PW, W_FINE, W_SEC, Plate, clamp, lerp, out_cubic, prog, smooth, text_w
MONO = 'mono'
CJK = 'sans:460'
LBL_X1 = 168
PF_X0, PF_X1 = (178, 470)
AN_X0 = 486
AN_W = 30
PANEL_X = 905
TOP = 70
HEAD_Y = 52

def _h(*k):
    v = 2166136261
    for x in k:
        v = (v ^ int(x) & 4294967295) * 16777619 & 4294967295
    return v / 4294967296.0

class Row:

    def __init__(self, group, label, h, key=None, hers=False, kind='thin'):
        self.group, self.label, self.h, self.key, self.hers, self.kind = (group, label, h, key, hers, kind)
        self.y0 = 0.0

    @property
    def y1(self):
        return self.y0 + self.h

    @property
    def cy(self):
        return self.y0 + self.h / 2

class BoardPlate:
    """turn: content.Turn; spec: [(group, tag, [Row...])] for the prompt (top to bottom); history: label lines."""

    def __init__(self, turn, spec, t_in, t_stop, status='', tally=True, history=(), geo=None, labels=True, panel=True, title=None, ink_heads=False):
        self.turn, self.t_in, self.t_stop, self.status = (turn, t_in, t_stop, status)
        self.history = list(history)
        self.tally = tally
        g = dict(lbl_x1=LBL_X1, pf_x0=PF_X0, pf_x1=PF_X1, an_x0=AN_X0, an_w=AN_W, panel_x=PANEL_X)
        g.update(geo or {})
        self.LBL_X1, self.PF_X0, self.PF_X1 = (g['lbl_x1'], g['pf_x0'], g['pf_x1'])
        self.AN_X0, self.AN_W, self.PANEL_X = (g['an_x0'], g['an_w'], g['panel_x'])
        self.labels, self.panel, self.title, self.ink_heads = (labels, panel, title, ink_heads)
        self.sung = [i for i, c in enumerate(turn.chars) if c.sung]
        self.cols = list(self.sung) + (['eos'] if turn.eos_at is not None else [])
        y = TOP
        self.rows, self.groups = ([], [])
        for gi, (group, tag, rows) in enumerate(spec):
            g0 = y
            for r in rows:
                r.y0 = y
                y += r.h
                self.rows.append(r)
            self.groups.append((group, tag, g0, y, rows))
            y += 5
        g0 = y
        self.ans_rows = []
        for k, i in enumerate(self.sung):
            r = Row('asst', turn.chars[i].ch, 3.6, f'ans{k}', turn.chars[i].hers, 'ans')
            r.y0 = y
            y += r.h
            self.rows.append(r)
            self.ans_rows.append(r)
        self.groups.append(('asst', 'its answer', g0, y, self.ans_rows))
        self.bottom = y
        self.n_ctx = sum((1 for r in self.rows if r.kind != 'ans'))
        self.pf_w = (self.PF_X1 - self.PF_X0) / max(1, self.n_ctx)
        self._schedule()

    def _schedule(self):
        tc = self.turn
        self.a0, self.land = ({}, {})
        prev = max(tc.start, self.t_in + 0.4)
        for col in self.cols:
            t = tc.eos_at if col == 'eos' else tc.chars[col].t
            d = min(0.45, max(0.16, 0.7 * (t - prev)))
            self.a0[col], self.land[col] = (t - d, t)
            prev = t
        self.reads = {}
        for k, col in enumerate(self.cols):
            rd = tc.eos_reads if col == 'eos' else tc.chars[col].reads
            m = {}
            for key, w in rd:
                m[key] = max(m.get(key, 0.0), w)
            if k > 0:
                m[f'ans{k - 1}'] = 0.35
            self.reads[col] = m
        her = [r for r in self.rows if r.hers and r.kind == 'file']
        t_end = self.land[self.cols[-1]]
        self.tally_at = {r.key: t_end + 0.35 + 0.216 * k for k, r in enumerate(her)}

    def col_x(self, k):
        return self.AN_X0 + k * self.AN_W

    def cell(self, row, col, k):
        """Attention of answer column k (col) to row: (value, hers, main)."""
        m = self.reads[col]
        if row.key in m and row.key != 'persona':
            w = m[row.key]
            return (0.88 if w >= 1 else 0.42, row.hers, w >= 1)
        if row.group == 'persona':
            base = 0.2 if 'persona' in m else 0.04
            return (base * (0.5 + 0.9 * _h(k, row.y0, 7) ** 2), False, False)
        if row.kind == 'file':
            return (0.025 + 0.05 * _h(k, int(row.y0 * 10), 3) ** 3, False, False)
        if row.kind == 'ans':
            kk = int(row.key[3:])
            if kk >= k:
                return (0.0, False, False)
        if row.group == 'sys' and row.label == '<|im_start|>':
            return (0.55, False, False)
        return (0.035 + 0.1 * _h(k, int(row.y0 * 10), 3) ** 4, False, False)

    def render(self, t):
        P = Plate()
        self.draw(P, t)
        return P.compose()

    def draw(self, P, t, a_scale=1.0):
        a_in = prog(t, self.t_in, self.t_in + 0.3) * a_scale
        if self.status:
            done = sum((1 for c in self.cols if self.land[c] <= t))
            P.text(0, 14, f'{self.status} · step {done}', 12, MONO, 0.7 * a_in, 'ash')
        if self.title:
            P.mixed(self.PF_X0, 14, self.title, 12, 0.8 * a_in, 'ink')
        if self.labels:
            self._labels(P, t, a_in)
        self._prefill(P, t, a_in)
        self._answer_cols(P, t)
        if self.panel:
            self._panel(P, t)
        if self.tally:
            self._tally(P, t)

    def _labels(self, P, t, a):
        for group, tag, g0, g1, rows in self.groups:
            if group == 'asst':
                if not any((self.land[c] <= t for c in self.cols)):
                    continue
            P.text(0, g0 + 9, tag, 11, MONO, 0.8 * a, 'ash')
            P.line([(self.LBL_X1 + 3, g0 + 1), (self.LBL_X1 + 3, g1 - 1)], W_FINE, 0.6 * a)
            for r in rows:
                if r.kind == 'file':
                    lit = self._lit(r, t)
                    P.text(self.LBL_X1 - 4, r.cy + 4, r.label, 11.5, MONO, a * (1 - lit), 'quiet', 'rs')
                    P.text(self.LBL_X1 - 4, r.cy + 4, r.label, 11.5, MONO, a * lit, 'blue', 'rs')
                elif r.kind == 'chip':
                    P.mixed(self.LBL_X1 - 4, r.cy + 4.5, r.label, 12, a * (0.7 + 0.3 * self._lit(r, t)), 'ink', anchor='rs')
        for group, tag, g0, g1, rows in self.groups:
            if group == 'history':
                for k, line in enumerate(self.history):
                    P.mixed(self.LBL_X1 - 4, g0 + 22 + k * 13.5, line, 10.5, 0.6 * a, 'ink', anchor='rs')
            if group == 'persona':
                P.mixed(self.LBL_X1 - 4, g0 + 24, '你是大肥鱼，', 10.5, 0.7 * a, 'ink', anchor='rs')
                P.mixed(self.LBL_X1 - 4, g0 + 38, '一只住在终端里的猫，', 10.5, 0.7 * a, 'ink', anchor='rs')
                P.mixed(self.LBL_X1 - 4, g0 + 52, '说话结尾带喵。', 10.5, 0.7 * a, 'ink', anchor='rs')

    def _lit(self, row, t):
        u = 0.0
        for col in self.cols:
            if row.key in self.reads[col] and self.reads[col][row.key] >= 1:
                a0, ld = (self.a0[col], self.land[col])
                mid = a0 + 0.62 * (ld - a0)
                u = max(u, prog(t, mid - 0.03, mid + 0.05) * (1 - prog(t, ld + 0.1, ld + 0.4)))
        return u

    def _prefill(self, P, t, a):
        """The prompt's own columns: computed in the prefill, cached. A faint causal triangle (plus the sink
        column and a previous-token diagonal), swept in left to right as the plate opens."""
        ctx = [r for r in self.rows if r.kind != 'ans']
        sweep = self.PF_X0 + (self.PF_X1 - self.PF_X0) * out_cubic(prog(t, self.t_in, self.t_in + 0.6))
        w = self.pf_w
        for q in range(len(ctx)):
            x = self.PF_X0 + q * w
            if x > sweep:
                break
            for kidx in range(q + 1):
                r = ctx[kidx]
                if kidx == 0:
                    v = 0.5
                elif kidx == q - 1 or kidx == q:
                    v = 0.32
                else:
                    v = 0.05 + 0.16 * _h(q, kidx, 5) ** 4
                if r.hers and r.kind == 'file':
                    layer = 'quiet'
                    v *= 1.2
                else:
                    layer = 'ink'
                P.rect(x + 0.3, r.y0 + 0.4, x + w - 0.3, r.y1 - 0.4, v * a, layer)
        P.text(self.PF_X0, HEAD_Y + 4, 'prefill · cached', 11, MONO, 0.65 * a, 'ash')
        P.text(self.PF_X1, HEAD_Y + 4, f'{len(ctx)} tok', 11, MONO, 0.55 * a, 'ash', 'rs')
        P.line([(self.PF_X1 + 7, TOP - 4), (self.PF_X1 + 7, self.bottom + 2)], W_FINE, 0.5 * a)

    def _answer_cols(self, P, t):
        tc = self.turn
        cur = None
        for k, col in enumerate(self.cols):
            a0, ld = (self.a0[col], self.land[col])
            if t < a0:
                break
            cur = k
            x = self.col_x(k)
            fill = smooth(prog(t, a0, a0 + 0.62 * (ld - a0)))
            for r in self.rows:
                v, hers, main = self.cell(r, col, k)
                if v <= 0.004:
                    continue
                ry = (r.cy - TOP) / max(1.0, self.bottom - TOP)
                u = clamp((fill - 0.7 * ry) / 0.3)
                if u <= 0:
                    continue
                if hers and main:
                    mid = a0 + 0.62 * (ld - a0)
                    lit = prog(t, mid - 0.03, mid + 0.05) * (1 - prog(t, ld + 0.1, ld + 0.4))
                    P.rect(x + 1.5, r.y0 + 0.8, x + self.AN_W - 1.5, r.y1 - 0.8, u * v * (1 - lit), 'quiet')
                    P.rect(x + 1.5, r.y0 + 0.8, x + self.AN_W - 1.5, r.y1 - 0.8, u * v * lit, 'blue')
                else:
                    P.rect(x + 1.5, r.y0 + 0.5, x + self.AN_W - 1.5, r.y1 - 0.5, u * v, 'ink')
            if t >= ld:
                a = prog(t, ld, ld + 0.05)
                drop = (1 - out_cubic(prog(t, ld, ld + 0.14))) * -8
                hs = min(24.0, self.AN_W * 0.82)
                if col == 'eos':
                    P.text(x + self.AN_W / 2, HEAD_Y + drop, '<eos>', 10, 'monob', a, 'ink', 'ms')
                else:
                    c = tc.chars[col]
                    nxt = next((self.land[cc] for cc in self.cols if self.land[cc] > ld), ld + 0.5)
                    live = 1 - prog(t, nxt, nxt + 0.3)
                    if c.hers and (not self.ink_heads):
                        P.text(x + self.AN_W / 2, HEAD_Y + drop, c.ch, hs, CJK, a * (1 - live), 'quiet', 'ms')
                        P.text(x + self.AN_W / 2, HEAD_Y + drop, c.ch, hs, CJK, a * live, 'blue', 'ms')
                    else:
                        P.text(x + self.AN_W / 2, HEAD_Y + drop, c.ch, hs, CJK, a, 'ink', 'ms')
        if cur is not None:
            col = self.cols[cur]
            if t < self.land[col] + 0.25:
                a = 1 - prog(t, self.land[col] + 0.05, self.land[col] + 0.25)
                x = self.col_x(cur)
                P.rect(x, TOP - 3, x + self.AN_W, self.bottom + 2, 0.9 * a, 'ink', W_SEC)
        nk = cur + 1 if cur is not None else 0
        if nk < len(self.cols) and t >= self.t_in + 0.4:
            x = self.col_x(nk)
            a = prog(t, self.t_in + 0.4, self.t_in + 0.6) * 0.45
            P.line([(x, TOP - 3), (x, self.bottom + 2)], W_FINE, a)
            P.line([(x + self.AN_W, TOP - 3), (x + self.AN_W, self.bottom + 2)], W_FINE, a)

    def _panel(self, P, t):
        """p( next | ctx ) of the newest column: its runner-ups when the script has them, and its lens column."""
        tc = self.turn
        cur = None
        for col in self.cols:
            if t >= self.a0[col]:
                cur = col
        if cur is None:
            return
        a = prog(t, self.a0[self.cols[0]], self.a0[self.cols[0]] + 0.2)
        P.text(self.PANEL_X, HEAD_Y + 4, 'p( next | ctx )', 12, MONO, 0.85 * a, 'ink')
        P.line([(self.PANEL_X, TOP - 2), (PW - 4, TOP - 2)], W_SEC, 0.8 * a)
        if cur == 'eos':
            tok = len(tc.tokens) - 1
            ch_hers = False
        else:
            tok = tc.chars[cur].tok
            ch_hers = tc.chars[cur].hers
        landed = t >= self.land[cur]
        win = prog(t, self.land[cur], self.land[cur] + 0.1)
        cands = tc.cands.get(tok)
        if cands is None:
            txt = '<eos>' if cur == 'eos' else tc.tokens[tok]
            p = 0.62 + 0.3 * _h(tok, 11)
            cands = [(txt, p)]
        for r_, (txt, pr) in enumerate(cands[:4]):
            y = TOP + 24 + r_ * 34
            top = r_ == 0
            val = a * (lerp(0.8, 1.0, win) if top else lerp(0.8, 0.5, win))
            layer = 'blue' if top and ch_hers and landed else 'ink' if top else 'ash'
            txt_ = txt
            while text_w(txt_, 15, CJK) > 190 and len(txt_) > 2:
                txt_ = txt_[:-2] + '…'
            P.mixed(self.PANEL_X, y, txt_, 15, val, layer)
            bw = 150 * pr / cands[0][1]
            P.rect(self.PANEL_X, y + 6, self.PANEL_X + bw, y + 9, val * (0.9 if top else 0.5), 'ink')
            P.text(PW - 4, y, f'{pr:.2f}', 11, MONO, val, 'ink' if top else 'ash', 'rs')
        if cur != 'eos':
            c = tc.chars[cur]
            y0 = TOP + 160
            P.text(self.PANEL_X, y0, 'lens', 11, MONO, 0.7 * a, 'ash')
            for r_, (lay, (txt, hers)) in enumerate(zip((12, 24, 36, 48), c.lens)):
                x = self.PANEL_X + 18 + r_ * 50
                P.text(x, y0 + 22, f'L{lay}', 10, MONO, 0.6 * a, 'ash', 'ms')
                P.text(x, y0 + 52, txt, 22, CJK, a * (0.85 if hers else 0.7), 'quiet' if hers else 'ink', 'ms')
            x = self.PANEL_X + 18 + 4 * 50
            P.text(x, y0 + 22, 'L64', 10, MONO, 0.6 * a, 'ash', 'ms')
            if landed:
                P.text(x, y0 + 52, c.ch, 22, 'sans:600', a, 'quiet' if c.hers else 'ink', 'ms')
            P.line([(self.PANEL_X, y0 + 62), (PW - 4, y0 + 62)], W_FINE, 0.5 * a)

    def _tally(self, P, t):
        """After <eos>: her rows counted, one per eighth note; the total under them."""
        her = [r for r in self.rows if r.hers and r.kind == 'file']
        x = self.col_x(len(self.cols)) + 10
        total = 0
        last = None
        for r in her:
            at = self.tally_at[r.key]
            n = sum((1 for col in self.cols if self.reads[col].get(r.key, 0) >= 1))
            if t < at:
                continue
            last = at
            total += n
            a = prog(t, at, at + 0.06)
            pop = 1 - prog(t, at, at + 0.2)
            P.text(x, r.cy + 4, str(n), 12 + 3 * pop, 'monob', a * (1.0 if n else 0.45), 'quiet' if n else 'ash')
        if last is not None and t >= last + 0.216:
            a = prog(t, last + 0.216, last + 0.3)
            g = next((g for g in self.groups if g[0] == 'memory'))
            P.line([(x - 2, g[3] + 1), (x + 26, g[3] + 1)], W_SEC, a)
            P.text(x, g[3] + 20, f'{total}', 18, 'monob', a, 'blue')

class PairPlate:
    """G3: two fingerprints side by side on the same rows. The left one is finished (frozen at t_left: the local
    Qwen's steak answer, her rows lit); the right one fills in on the song's syllables (the merged one's message:
    its reads go to your old words, her rows stay empty)."""

    def __init__(self, left, right, t_left, t_in):
        self.left, self.right, self.t_left, self.t_in = (left, right, t_left, t_in)

    def render(self, t):
        P = Plate()
        self.left.draw(P, self.t_left, a_scale=prog(t, self.t_in, self.t_in + 0.3))
        self.right.draw(P, t)
        x = (self.left.col_x(len(self.left.cols)) + self.right.PF_X0) / 2 + 6
        P.line([(x, TOP - 30), (x, self.left.bottom + 6)], W_FINE, 0.6 * prog(t, self.t_in, self.t_in + 0.3))
        return P.compose()
