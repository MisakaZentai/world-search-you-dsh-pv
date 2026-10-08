"""Group E, fifth sample (sample_open_e/README.md): the chorus (179.64-207.015) in the panes. The same terminal as
B-D (panes.py); in E one pane at a time takes the stage (tmux's zoom), because each beat is one view:

  e1 / e3   the 3D city (inside/, e1_city and e3_city, unchanged): hundreds of identical towers, one per session
            running her persona; it is the forward pane zoomed (its chrome goes over the plate in a finish hook)
  e2        the mem pane zoomed: her files stay in their column, and the nine files the stand-ins wrote land in a
            3 x 3 grid beside it, one a syllable (`dsh memory ~/memory/you/ --watch --grid`)
  e4        nine searches of her archive after she was retired: the query you type fills the input pane; trace runs
            each search; compare keeps the record, "0 hits after retire" (R4); the whole frame freezes on the
            ah-ah (D4)
  e5        ls -la ~/memory/you/: the trace pane fills the wide frame (D2); one syllable lights one of her eight
            rows, "left" lights the line where she was retired

Switch: DSH_E=pane (film.py). Timing, texts and pictures come from groups.e (v2 E, unchanged). The dsh pane is
ui/pages/e_pane.py (shot to ui/pane_open_e/).

r2 (sample_open_e/README.md §6, the review in renders/e_pane_review_20261003/): the command line names what each
view runs (the city is `dsh ps --persona 大肥鱼 --watch`); the city plates are inside/city_epane.py (the roofs
flash on every beat, a tower lights in her blue on its syllable, the reel lands on her and slips three times,
e_reel.py); the cells fill the zoomed pane; the query scrolls up when ls prints; the caret keeps blinking through
the ah-ah; the owner column of ls carries the shot (her eight `me` big, one a syllable; on "left" the line where
she was retired and the stand-ins' names under it); the window stays out into F (F holds it). r1's source is in
sample_open_e/src_r1/.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from PIL import ImageDraw
import cast
import hud
import panes
import syl
import tl
from groups import b_open as BO
from groups import c_pane as CPN
from groups import d_pane as DP
from groups import e as GE
from groups.base import big_word, full_frame
from hud import BG, HER_QUIET, INK, SLAB, lv
from panes import FAINT, SUB, TXT
from tuikit import ease, glyph
from inside import city_epane
city_epane.patch_shots()
W = tl.W
T0, T1 = (GE.T0, GE.T1)
P = tl.p
mtx, mw = (BO.mtx, BO.mw)
MEM, COL = (CPN.MEM, CPN.COL)
CELLS_AT, SEARCH_AT, LS_AT, LS_OUT, LS_BACK = (GE.CELLS_AT, GE.SEARCH_AT, GE.LS_AT, GE.LS_OUT, GE.LS_BACK)
M_AT = CELLS_AT[0] - 0.3
CITY = ('e1_city_p', 'e3_city_p')
CITY2_IN = syl.times(46)[0] - 0.24
CITY2_FULL = GE.SESS2[0]
CMD_CITY = '$ dsh ps --persona 大肥鱼 --watch'

def layout(t):
    """e2 zooms the mem pane; from the moment the e2'/e3 city is opaque the search panes are laid out under it,
    so the city fades out onto them (r1 showed the cells again for 0.17 s there); ls fills the frame."""
    r = CPN.right(t)
    s = 1.0 if t >= CITY2_FULL else 0.0
    l_ = ease.ease_out(ease.prog(t, LS_AT, LS_AT + 0.14))
    zero = (COL, 598, r, 598)
    M = {'mem': (MEM[0], 88, r, 598), 'input': zero, 'trace': zero, 'compare': zero}
    S = {'mem': MEM, 'input': (COL, 88, r, 330), 'trace': (COL, 338, r, 392), 'compare': (COL, 400, r, 598)}
    L = {'mem': MEM, 'input': (COL, 88, r, 88), 'trace': (COL, 88, r, 598), 'compare': (COL, 598, r, 598)}
    VM, VS, VL = ({'mem': 1, 'input': 0, 'trace': 0, 'compare': 0}, {k: 1 for k in S}, {'mem': 1, 'input': 0, 'trace': 1, 'compare': 0})
    w = (1 - s, s * (1 - l_), l_)
    out, lev = ({}, {})
    for k in M:
        out[k] = tuple((w[0] * a + w[1] * b + w[2] * c for a, b, c in zip(M[k], S[k], L[k])))
        lev[k] = w[0] * VM[k] + w[1] * VS[k] + w[2] * VL[k]
    return (out, lev)

def _command(t):
    """(command, when it was typed): every view names what it runs (r1 kept D's command under the e1 city, and
    `--watch --grid` under the e3 city)."""
    for t0, cmd in ((LS_AT, GE.CMD_LS), (SEARCH_AT, GE.CMD_SEARCH), (CITY2_IN, CMD_CITY), (M_AT, GE.CMD_WATCH), (T0, CMD_CITY)):
        if t >= t0:
            return (cmd, t0)
    return (CMD_CITY, T0)

def _chip(d, t, r):
    chip = cast.term(tl.model(t))
    f = P.font(13, 'bold')
    w = d.textlength(chip, font=f)
    d.rectangle((r - w - 12, hud.Y_CMD - 3, r, hud.Y_CMD + 17), fill=SLAB)
    d.text((r - w - 6, hud.Y_CMD), chip, font=f, fill=BG)
    return r - w - 12

def _cmdline(d, t, r, clear=False):
    """The top row: the command, typed in at BO.CODE_CPS when it changes; the model chip on the right."""
    x_chip = _chip(d, t, r)
    if clear:
        d.rectangle((30, hud.Y_CMD - 3, x_chip - 4, hud.Y_CMD + 17), fill=BG)
    cmd, t0 = _command(t)
    n = cmd.index('$ ') + 2 + int((t - t0) * BO.CODE_CPS) + 1
    hud.tx(d, (36, hud.Y_CMD), cmd[:n], 13, lv(INK, 0.86))
CELL, GAP = (150, 14)
CS = CELL / 120

def _cell_rect(k, t):
    r, c = divmod(k, 3)
    gw = 3 * CELL + 2 * GAP
    x = COL + max(20, (CPN.right(t) - COL - gw) // 2) + c * (CELL + GAP)
    y = 88 + (598 - 88 - gw) // 2 + r * (CELL + GAP)
    return (x, y, x + CELL, y + CELL)

def _draw_cell(d, t, k, level=1.0):
    """GE.draw_cell at the zoomed size: empty and dim until its syllable, then the picture lands (ink, one touch of
    her blue, lit while it lands), the file name and who wrote it."""
    x0, y0, x1, y1 = _cell_rect(k, t)
    at = CELLS_AT[k]
    on = t >= at
    d.rectangle((x0, y0, x1, y1), outline=lv(INK, (0.85 if on else 0.22) * level), width=2 if on else 1)
    if not on:
        return
    name = GE.E2_FILES[k]
    tw, who = GE.E2_WRITES[name]
    u = GE.lit(t, at, CELLS_AT[k + 1] if k + 1 < len(CELLS_AT) else at + 0.5)
    blue = lv(hud.her(u), level)
    g = ease.ease_back(ease.prog(t, at, at + 0.22))
    cx, cy = ((x0 + x1) / 2, y0 + 46 * CS + 4)
    if name in ('dope', 'love'):
        f = tl.p.font(max(8, int(30 * CS * g)), 'bold')
        d.text((cx, cy + GE.drop(t, at, -8, 0.14)), name, font=f, fill=blue if name == 'love' else lv(INK, level), anchor='mm')
        if name == 'dope':
            d.rectangle((cx - 36, cy + 24, cx + 36, cy + 26), fill=blue)
    else:
        if name == 'cat_2':
            pat, cmap = (GE.GC.CAT_PIX, {'I': lv(INK, level), 'B': blue})
        elif name == 'flower_2':
            pat, cmap = (GE.GC.FLOWER_PIX, {'#': lv(INK, level), 'o': blue})
        else:
            pat, cmap = (GE.PIX[name], {'#': lv(INK, level), 'b': blue})
        cell = int(round((6 if len(pat[0]) <= 12 else 5) * CS))
        cc = max(1, int(round(cell * g)))
        w, h = (len(pat[0]) * cc, len(pat) * cc)
        hud.pix(d, pat, int(cx - w / 2), int(cy - h / 2), cc, cmap)
    a = ease.prog(t, at, at + 0.16)
    hud.tx(d, (x0 + 8, y1 - 36), name + '.txt', 13, lv(INK, 0.8 * a * level))
    hud.tx(d, (x0 + 8, y1 - 19), GE.OWNER[who], 11, lv(INK, 0.55 * a * level))

def _grid(d, t, level):
    for k in range(9):
        _draw_cell(d, t, k, level)

def _cur_search(t):
    cur = None
    for q, a, b, f in GE.SEARCHES:
        if t >= a:
            cur = (q, a, b, f)
    return cur

def _query(d, t, r, real=None):
    """The query box: what you are typing, the word that fills the pane (D3), its caret. When ls prints the pane
    folds up and its content scrolls up with it (r1 clipped the word in half). The caret blinks on real time,
    so it goes on blinking with the beat through the ah-ah while everything else is frozen (D4)."""
    if t < CITY2_FULL:
        return
    real = t if real is None else real
    dy = r[3] - 330
    mtx(d, (r[0] + 14, r[1] + 14 + dy), 'query ›', 12, lv(INK, SUB))
    cur = _cur_search(t)
    x, top = (r[0] + 96, r[1] + 22 + dy)
    blink = tl.C.beat_of(real) % 1.0 < 0.5
    if cur is not None:
        q, a, b, f = cur
        shown = q[0] if t < b else q
        last = a if t < b else b
        bump = 1.0 + 0.1 * (1 - ease.prog(t, last, last + 0.1))
        box = big_word(d, shown, (x, top + 6), 176, INK, 'la', bump=bump)
        cx = box[2] + 14
        ids = '·'.join((str(i) for i in DP.PROMPT_IDS.get(shown, ()))) if shown in DP.PROMPT_IDS else str(glyph.token_id(shown))
        mtx(d, (x, top + 196), ids, 11, lv(INK, SUB))
        if blink or real - last < 0.3:
            d.rectangle((cx, top + 4, cx + 6, top + 186), fill=INK)
    elif blink:
        d.rectangle((x, top + 4, x + 6, top + 186), fill=INK)

def _record(d, t, c):
    """Every 'for' prints a line: 0 hits after retire (R4: it accumulates); the 0 lands a size up and settles."""
    for i, (q, a, b, f) in enumerate(GE.SEARCHES):
        if t < f:
            break
        y = c[1] + 14 + i * 20 + DP.GD.drop(t, f, -6, 0.12)
        mtx(d, (c[0] + 14, y), q, 15, lv(INK, TXT), bold=True)
        k = 1 - ease.ease_out(ease.prog(t, f, f + 0.16))
        sz = int(round(14 * (1 + 0.7 * k)))
        mtx(d, (c[0] + 74 - sz * 0.3, y + 1 - (sz - 14) * 0.6), '0', sz, lv(INK, TXT), bold=True)
        mtx(d, (c[0] + 90, y + 2), 'hits after retire', 12, lv(INK, SUB))
CODE = [(a, f'search("{q}", author=她, after="retire")', (f, '0')) for q, a, b, f in GE.SEARCHES]
CODE.append((LS_AT - 0.2, 'ls -la ~/memory/you/', None))

def _trace(d, t, r):
    if t >= LS_AT:
        return
    shown = [(at, s, ret) for at, s, ret in CODE if at <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    bottom = r[3] - 21
    for pos, (at, s, ret) in enumerate(reversed(shown[-3:])):
        y = bottom - pos * 19 + (1 - sc) * 19
        a = {0: TXT, 1: SUB}.get(pos, SUB * (1 - sc))
        n = int((t - at) * BO.CODE_CPS) + 1
        w = mtx(d, (r[0] + 10, y), s[:n], 14, lv(INK, 0.92 * a), bold=pos == 0)
        if ret and t >= ret[0]:
            mtx(d, (r[0] + 10 + w + 12, y), '→ ' + ret[1], 14, lv(INK, 0.7 * a * ease.prog(t, ret[0], ret[0] + 0.1)), bold=True)
HER_PITCH, OTHER_PITCH = (28, 12.5)
ME_PX, HER_PX, OTHER_PX = (28, 14, 11)
DIM = 0.3

def _ls(d, t, r):
    if t < LS_AT:
        return
    off = 14 * (1 - ease.ease_out(ease.prog(t, LS_AT, LS_AT + 0.14)))
    x0, xr = (r[0] + 14, r[2] - 14)
    x_own, x_grp = (x0 + 96, x0 + 96 + 168)
    x_size_r, x_name = (x_grp + 86, x_grp + 102)
    y = r[1] + 14 + off
    rows = GE.LS
    left_at = GE.LS_ROWS[8]
    f_h, f_o = (P.font(HER_PX), P.font(OTHER_PX))
    k_her = 0
    for k, (perm, own, grp, size, name, hers) in enumerate(rows):
        if hers:
            base = y + 21
            at = GE.LS_ROWS[k_her]
            on = t >= at
            u = GE.lit(t, at, GE.LS_ROWS[k_her + 1]) if on else 0.0
            c = lv(hud.her(u), 1.0) if on else lv(INK, DIM)
            d.text((x0, base), perm, font=f_h, fill=c, anchor='ls')
            bump = 1.0 + 0.3 * (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) if on else 1.0
            d.text((x_own, base + 2), own, font=P.font(int(round(ME_PX * bump)), 'bold'), fill=c, anchor='ls')
            d.text((x_grp, base), grp, font=f_h, fill=c, anchor='ls')
            d.text((x_size_r, base), str(size), font=f_h, fill=c, anchor='rs')
            d.text((x_name, base), name, font=P.font(HER_PX, 'bold') if on else f_h, fill=c, anchor='ls')
            y += HER_PITCH
            k_her += 1
            if k_her == 8:
                y += 10
                _retired(d, t, x0, xr, y, left_at)
                y += 12
        else:
            base = y + 10
            j = k - 8
            c = lv(INK, DIM)
            d.text((x0, base), perm, font=f_o, fill=c, anchor='ls')
            ow_at = left_at + 0.06 + 0.022 * j
            g = ease.prog(t, ow_at, ow_at + 0.08)
            d.text((x_own, base), own, font=P.font(OTHER_PX, 'bold') if g > 0.5 else f_o, fill=lv(INK, DIM + (0.92 - DIM) * g), anchor='ls')
            d.text((x_grp, base), grp, font=f_o, fill=c, anchor='ls')
            d.text((x_size_r, base), str(size), font=f_o, fill=c, anchor='rs')
            d.text((x_name, base), name, font=f_o, fill=c, anchor='ls')
            y += OTHER_PITCH
    total = sum((rw[3] for rw in rows))
    d.text((x0, y + 16), f'total {total // 1024}K   {len(rows)} files   owner: me + {len(cast.STANDINS)} others   about: you', font=P.font(12), fill=lv(INK, 0.5), anchor='ls')

def _retired(d, t, x0, xr, y, at):
    """The line where she was retired: dashed and faint until "left", then drawn across the frame in her blue
    with her date and name landing on it."""
    if t < at:
        for x in range(int(x0), int(xr), 8):
            d.line([(x, y), (x + 3, y)], fill=lv(INK, 0.25))
        return
    u = GE.lit(t, at, at + 0.6)
    k = ease.ease_out(ease.prog(t, at, at + 0.18))
    col = lv(hud.her(u), 1.0)
    d.line([(x0, y), (x0 + (xr - x0) * k, y)], fill=col, width=2)
    bump = 1.0 + 0.35 * (1 - ease.ease_out(ease.prog(t, at, at + 0.14)))
    f = P.font(int(round(18 * bump)), 'bold')
    d.text((xr, y - 6), f'retired {GE.RETIRED} · {cast.name('her')}', font=f, fill=col, anchor='rs')
RUN = {'mem': [(at - 0.1, at + 0.15) for at in CELLS_AT], 'input': [(a, a + 0.25) for q, a, b, f in GE.SEARCHES] + [(b, b + 0.25) for q, a, b, f in GE.SEARCHES], 'trace': [(a, f) for q, a, b, f in GE.SEARCHES] + [(LS_AT - 0.2, LS_AT + 0.1)], 'compare': [(f - 0.1, f + 0.15) for q, a, b, f in GE.SEARCHES]}

def _reads(t):
    her_k = {k: i for i, k in enumerate(tl.HER_FILES)}
    Pl = hud.Pulse(t)
    for at in CELLS_AT:
        Pl.hit('archive', at, 0.12)
    for q, a, b, f in GE.SEARCHES:
        Pl.hit('archive', f, 0.16)
    for k, at in enumerate(GE.LS_ROWS[:8]):
        Pl.hit(her_k[GE.LS_STRIP[k]], at, 0.3)
    return Pl.out

def _body_fn(c, img, d, t):
    if t < M_AT:
        DP._body_fn(_At(c, t), img, d)
        _cmdline(d, t, CPN.right(t), clear=True)
        return
    L, lev = layout(t)
    r = CPN.right(t)
    _cmdline(d, t, r)
    hits = _reads(t)
    for name in ('input', 'trace', 'compare'):
        rect = L[name]
        level = lev[name]
        if level <= 0.01 or rect[3] - rect[1] < 4:
            continue
        d.rectangle(rect, fill=BG)
        with panes.Clip(img, rect) as dd:
            if name == 'input':
                _query(dd, t, rect, real=c.t)
            elif name == 'trace':
                _trace(dd, t, rect)
                _ls(dd, t, rect)
            else:
                _record(dd, t, rect)
        status = {'compare': 'author: 她 · after retire'}.get(name, '')
        panes.box(d, rect, name, t, panes.run_k(t, RUN[name]), level, status)
    m = L['mem']
    zoom = m[2] - m[0] > MEM[2] - MEM[0] + 4
    if zoom:
        d.rectangle(m, fill=BG)
        with panes.Clip(img, m) as dd:
            _grid(dd, t, lev['mem'])
    CPN._memory(d, t, MEM, hits)
    run = max(min(1.0, 3 * max(hits.values(), default=0.0)), panes.run_k(t, RUN['mem']) if zoom else 0.0)
    panes.box(d, m, 'mem', t, run, 1.0, '~/memory/you/ · watch' if m[2] - m[0] > 320 else '')

class _At:
    """The shot context at a frozen / given time (DP._body_fn reads c.t)."""

    def __init__(self, c, t):
        self.c, self.t = (c, t)

    def __getattr__(self, k):
        return getattr(self.c, k)

def _city_chrome(film):
    """The e1 / e3 city plates fill the stage: they are the forward pane zoomed (a batch of sessions running her
    persona), so the pane's chrome goes over the plate (install() paints the plate after the shot body)."""

    def fn(img, t):
        if not T0 <= t < T1:
            return None
        a = 0.0
        for sp in getattr(film, 'inside_spans', ()):
            if sp.name in CITY and sp.active(t):
                a = max(a, sp.alpha(t))
        if a <= 0.01:
            return None
        d = ImageDraw.Draw(img)
        panes.box(d, (COL, 88, CPN.right(t), 598), 'forward', t, 1.0, a, 'batch · 云端')
        panes.box(d, MEM, 'mem', t, 0.0, 1.0)
        return img
    return fn
SHOTS = [('e1_sessions', T0, CELLS_AT[0]), ('e2_cells', CELLS_AT[0], GE.SESS2[0]), ('e2b_sessions', GE.SESS2[0], GE.SLOT_AT), ('e3_slot', GE.SLOT_AT, SEARCH_AT), ('e4_search', SEARCH_AT, LS_AT), ('e5_ls', LS_AT, T1)]

def register(film):
    for name, a, b in SHOTS:
        GE.add_frozen(film, name, a, b, _body_fn)
    film.character = DP.dsh_layer(film, film.character, 'ui/pane_open_e', T0, T1)
    full_frame(LS_OUT, T1, 0.3, 0.33)
    GE._freeze_header(film)
    for k, at in enumerate(CELLS_AT):
        hud.LIVE.append((at, CELLS_AT[k + 1] if k + 1 < len(CELLS_AT) else at + 0.5))
    for k, at in enumerate(GE.LS_ROWS[:8]):
        hud.LIVE.append((at, GE.LS_ROWS[k + 1]))
    hud.LIVE.append((GE.LS_ROWS[8], GE.LS_ROWS[8] + 0.6))
    for t0, side in [(T0, 'right'), (CELLS_AT[0], 'left'), (GE.SESS2[0], 'right'), (SEARCH_AT, 'left'), (LS_OUT - DP.GD.LEAD_EARLY, 'both')]:
        film.set_lead(t0, side)
    film.finish.append(_city_chrome(film))
