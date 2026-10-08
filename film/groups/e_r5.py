"""Group E, r5 (REVISE_R4_20261004.md §3.7-3.10, §4 lines 44-51, §5.1; DECISIONS D34 with D2, D3, D4): the chorus
(179.64-207.015) at film 1's red-chorus strength. The city is gone (D2): searching is drawn as a search you can see
running. Started from a copy of groups/e_pane.py (r4); the ls -la shot (e5) is r4's, line for line.

r5 second round (D35, owner on the r5 candidate): no inversion anywhere (R-B: no paper <-> ink swap, no ink card, no
black block); the strength comes from accumulation, movement, speed, size and density. Nothing stalls while the
chords go on (R-A): a move lands on a beat or a node and something keeps moving inside it at the rate of
beatmap.pad. Nothing covers type (R-C). Two variants of the nine searches, switched by DSH_E5 (default `scan`, D37; `wall` kept).

  e1   179.64  line 44  `search("大肥鱼")`: the results are the dsh sidebar's 大肥鱼 sessions (the same rows, the
                        same models, the same syllables as the dsh pane inserts them). A row lands on its syllable
                        lit in her blue, shows its model a 16th later (not her) and is struck an 8th later. On the
                        first "searching" the query pane zooms (tmux zoom, landing on the syllable) and the query is
                        typed again in big type, a piece a syllable, while the rows keep landing under it. On
                        every-ry-where the results flood the frame in three waves (the third on the downbeat), dozens
                        of cards with her name, and a paper box with the count opens among them: her 0.
  e2   182.68  line 45  the mem pane zoomed: the nine files the stand-ins wrote, one a syllable, as pixel objects
                        in their own colours (D4, inside/e5_sprites.py), each with a patch of her blue; they bounce
                        on the beat; on the bar of "everything" every patch of hers lights at once.
  e2'  186.54  line 46  e1 again, raised: scope="*", three lines of big type, the flood is denser.
  e3   189.54  line 47  the stand-ins' machine: a Transformer block diagram (inside/e5_arch.py). A signal walks the
                        data path and lands in a node on each beat (beatmap.arrive); inside the node it keeps moving
                        at the pad rate; dots flow on the lines it has passed. The softmax's top bar is the model on
                        the nameplate's reel (e_reel); trans-for-ming types on its syllables and the "ing" turns
                        into "er" on the next beat, the window slides out and the N x block is dealt into a deck.
  e4   193.735 lines 48-50  nine searches of her archive after she was retired. Her word is typed into a zoomed
                        search box the way an input method commits it, a character a syllable (inside/e5_query.py).
                        DSH_E5=wall (inside/e5_wall.py): on "for" the word shrinks and flies into a wall of failed
                        queries that keeps growing; the camera pulls back with the harmony; the ah-ah holds the
                        word in the box while the tiles rise and fall with the voice; from line 50 old queries are
                        re-run and their tiles drop on 16ths, denser and denser, until the wall fills its pane.
                        DSH_E5=scan (inside/e5_scan.py): the archive scrolls past a fixed scan line at the speed of
                        the song's energy, the searched characters light in her blue as they cross it; failed
                        searches pile up in a column, `0 hits x n` counting up. r5c ("导 1"): the after line lands
                        once on the first search's run; 在吗's scan rushes to the archive's end and the retired
                        line sits on the scan line through the ah-ah (LAND .. AGAIN), paper under it; the next
                        search re-runs the archive from its first row.
  e5   203.04  line 51  r4's ls -la, unchanged (owner column, her eight `me` rows, the retired line).

Switch: DSH_E=r5 (film.py), DSH_E5=wall|scan. Times come from syl / tl / groups.e / beatmap. The dsh pane is r4's
ui/pages/e_pane.py (shot in ui/pane_open_e/): its sidebar inserts the same sessions on the same syllables and its
header reel is e_reel; it is hidden while the flood covers the right half. Model names come from cast.py; this
file keeps only keys.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import bisect
import math
import os
import random
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw
import beatmap as BM
import cast
import e_reel
import hud
import panes
import syl
import tl
from groups import b_open as BO
from groups import c_pane as CPN
from groups import d_pane as DP
from groups import e as GE
from groups.base import add, full_frame
from hud import BG, HER_QUIET, INK, SLAB, lv
from panes import FAINT, SUB, TXT
from inside import e5_arch, e5_query, e5_sprites
from tuikit import ease, glyph
VARIANT = os.environ.get('DSH_E5', 'scan')
assert VARIANT in ('wall', 'scan'), VARIANT

def _drop_city():
    """inside.shots.spans() (film.py reads it after the groups register) without v2's / r4's E city plates."""
    import inside.shots as IS
    if getattr(IS, '_e_r5', False):
        return
    orig = IS.spans
    gone = {'e1_city', 'e3_city', 'e1_city_p', 'e3_city_p'}

    def spans_():
        return [s for s in orig() if s.name not in gone]
    IS.spans = spans_
    IS._e_r5 = True
_drop_city()
W, WE = (tl.W, tl.WE)
T0, T1 = (GE.T0, GE.T1)
P = tl.p
mtx, mw = (BO.mtx, BO.mw)
MEM, COL = (CPN.MEM, CPN.COL)
FULL = hud.FULL_RECT
LEFT = hud.LEFT

def _key(lid, wi):
    return syl._key(tl.L.by_id[lid].words[wi].text)
SESS = list(GE.SESS1) + list(GE.SESS2)
SESS_ORDER = ['mimo', 'glm', 'kimi', 'step', 'qwen', 'ernie', 'longcat', 'hy4', 'minimax']
SESS_WHO = [SESS_ORDER[i % len(SESS_ORDER)] for i in range(len(SESS))]
N1 = len(GE.SESS1)
CELLS_AT = GE.CELLS_AT
E2_AT, E2B_AT, ARCH_AT = (CELLS_AT[0], GE.SESS2[0], GE.SLOT_AT)
SEARCH_AT, LS_AT, LS_ROWS = (GE.SEARCH_AT, GE.LS_AT, GE.LS_ROWS)
for _lid in (44, 46):
    assert _key(_lid, 1) == _key(_lid, 3) == 'searching' and _key(_lid, 6) == 'everywhere'
FIND = {1: [syl.syl(44, 1)[0], syl.syl(44, 3)[0]], 2: [syl.syl(46, 1)[0], syl.syl(46, 3)[0]]}
EVERY = {1: syl.syl(44, 6), 2: syl.syl(46, 6)}
assert _key(47, 5) == 'transforming' and _key(49, 6) == 'ah-ah'
TRANS = syl.syl(47, 5)
AH = syl.syl(49, 6)
AH_END = WE(49, 6)
L50 = W(50, 0)
ER_AT = tl.next_beat(TRANS[-1])

def _near_accent(t):
    """beatmap.accent of the beat nearest t (a sung onset a frame or two before a downbeat counts as the downbeat)."""
    bs = BM.events('beat', t - 0.5, t + 0.5)
    b = min(bs, key=lambda x: abs(x - t)) if bs else t
    return BM.accent(b + 0.01)
S16 = BM.events('sixteenth', T0, T1)
S8 = BM.events('eighth', T0, T1)
BEATS = BM.events('beat', T0 - 0.5, T1)
DOWNS = BM.events('down', T0 - 0.5, T1)

@lru_cache(maxsize=1)
def _pad_cum():
    """The integral of the inner-motion rate (0.6 + 1.6 * pad) over the chorus, at 100 Hz: phase in cycles."""
    ts = np.arange(T0 - 1.0, T1 + 1.0, 0.01)
    r = np.array([0.6 + 1.6 * BM.pad(u) for u in ts])
    cum = np.concatenate([[0.0], np.cumsum((r[1:] + r[:-1]) * 0.5 * 0.01)])
    return (ts, cum)

def phase(t):
    ts, cum = _pad_cum()
    return float(np.interp(t, ts, cum))

@lru_cache(maxsize=512)
def _sprite(text, size, bold, fill):
    """RGBA sprite of `text` (tight to its ink) in the face for its script."""
    f = hud.font(size, text, bold)
    tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    x0, y0, x1, y1 = tmp.textbbox((0, 0), text, font=f)
    im = Image.new('RGBA', (x1 - x0 + 4, y1 - y0 + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - x0, 2 - y0), text, font=f, fill=tuple(fill) + (255,))
    return im

def _bump(t, at, amount=0.12, dur=0.12):
    """1 + amount at `at`, settling to 1 over dur (a slam: out-expo-like)."""
    if t < at:
        return 1.0
    u = ease.prog(t, at, at + dur)
    return 1.0 + amount * (1 - ease.ease_out(u)) ** 2

def _kick(t, amp=3.0):
    """A small hop on every beat, the largest on the downbeat (P1: small changes off the bar line)."""
    k = BM.last(t, BEATS)
    if k is None:
        return 0.0
    u = (t - k) / 0.14
    if u >= 1:
        return 0.0
    return -amp * BM.accent(k + 0.01) * math.sin(math.pi * u)

def _cmd(t):
    for t0, cmd in ((LS_AT, GE.CMD_LS), (E4_AT, GE.CMD_SEARCH), (ARCH_AT, CMD_ARCH), (E2B_AT, CMD_FIND2), (E2_AT, GE.CMD_WATCH), (T0, CMD_FIND1)):
        if t >= t0:
            return (cmd, t0)
    return (CMD_FIND1, T0)
CMD_FIND1 = '$ dsh search --scope sessions --persona 大肥鱼'
CMD_FIND2 = "$ dsh search --scope '*' --persona 大肥鱼"
CMD_ARCH = '$ dsh inspect --persona 大肥鱼 --arch'

def _chip(d, t, r):
    chip = cast.term(tl.model(t))
    f = P.font(13, 'bold')
    w = d.textlength(chip, font=f)
    d.rectangle((r - w - 12, hud.Y_CMD - 4, r, hud.Y_CMD + 13), fill=SLAB)
    d.text((r - w - 6, hud.Y_CMD - 2), chip, font=f, fill=BG)
    return r - w - 12

def _cmdline(d, t, r):
    _chip(d, t, r)
    cmd, t0 = _cmd(t)
    n = cmd.index('$ ') + 2 + int(max(0.0, t - t0) * BO.CODE_CPS) + 1
    hud.tx(d, (36, hud.Y_CMD), cmd[:n], 13, lv(INK, 0.86))

class _Clip(panes.Clip):
    """panes.Clip that also hands out its layer (for pasting masks): with _Clip(img, rect) as (layer, d): ..."""

    def __enter__(self):
        d = super().__enter__()
        return (self.layer, d)

def _right(t):
    return CPN.right(t)

def _reads(t):
    her_k = {k: i for i, k in enumerate(tl.HER_FILES)}
    Pl = hud.Pulse(t)
    for at in CELLS_AT:
        Pl.hit('archive', at, 0.12)
    for at in RUN:
        Pl.hit('archive', at, 0.16)
    for at in RERUNS:
        Pl.hit('archive', at, 0.08)
    for k, at in enumerate(LS_ROWS[:8]):
        Pl.hit(her_k[GE.LS_STRIP[k]], at, 0.3)
    return Pl.out

def _mem(d, t, level=1.0):
    CPN._memory(d, t, MEM, _reads(t))
    panes.box(d, MEM, 'mem', t, 0.0, level)
ROW_P = 35
ZOOM = {1: dict(at=FIND[1][0], lines=['search("', '大肥鱼")'], pieces=[(0, 'search("'), (1, '大'), (1, '肥'), (1, '鱼'), (1, '")')], times=syl.syl(44, 1) + syl.syl(44, 2) + syl.syl(44, 3), enter=syl.syl(44, 4)[0]), 2: dict(at=FIND[2][0], lines=['search("', '大肥鱼",', 'scope="*")'], pieces=[(0, 'search("'), (1, '大'), (1, '肥'), (1, '鱼",'), (2, 'scope='), (2, '"*")')], times=syl.syl(46, 1) + syl.syl(46, 2) + syl.syl(46, 3) + syl.syl(46, 4), enter=syl.syl(46, 5)[0])}
ZOOM_TRAVEL = 0.2
for _ph, _z in ZOOM.items():
    assert len(_z['times']) == len(_z['pieces']), (_ph, _z['times'])

def _zoom_size(ph):
    """The big type's size: the widest line fits the pane (normal split) with 22 px each side, and the results
    pane under it keeps room for 4 rows (phase 1) or 3 (phase 2)."""
    z = ZOOM[ph]
    room = hud.XR + 8 - COL - 44
    rows = 4 if ph == 1 else 3
    q_bottom = 598 - 8 - 36 - rows * ROW_P
    size = 160
    while size > 40 and (max((mw(s, size, True) for s in z['lines'])) > room or 88 + 18 + len(z['lines']) * round(size * 1.1) + 6 > q_bottom):
        size -= 2
    return size
for _ph in ZOOM:
    ZOOM[_ph]['size'] = _zoom_size(_ph)
    ZOOM[_ph]['pitch'] = round(ZOOM[_ph]['size'] * 1.1)
    ZOOM[_ph]['bottom'] = 88 + 18 + len(ZOOM[_ph]['lines']) * ZOOM[_ph]['pitch'] + 6

def _row(d, t, i, x0, x1, y, level=1.0):
    """Result row i (session SESS[i]): lands lit in her blue, its model a 16th later, struck an 8th later."""
    at = SESS[i]
    who = SESS_WHO[i]
    s16 = tl.grid(at + 0.01, 1, 4) - at
    s8 = tl.grid(at + 0.01, 1, 2) - at + 0.0
    show = at + max(0.06, s16)
    strike = at + max(0.16, s8)
    big = _near_accent(at) >= 0.99
    dy = (1 - ease.ease_out(ease.prog(t, at, at + 0.1))) * -10
    y = y + dy
    u = 1.0 if t < strike else 1 - ease.prog(t, strike, strike + 0.3)
    blue = hud.her(u)
    hud.tx(d, (x0, y + 9), f'{i + 1:02d}', 12, lv(INK, SUB * level))
    d.rectangle((x0 + 30, y + 6, x0 + 47, y + 23), fill=lv(HER_QUIET, 0.75 * level), outline=lv(INK, 0.6 * level))
    hud.hatch(d, (x0 + 32, y + 8, x0 + 45, y + 21), lv(BG, 0.45), 4)
    k = _bump(t, at, 0.35 if big else 0.15, 0.14)
    sz = int(round(21 * k))
    hud.tx(d, (x0 + 58, y + 3 - (sz - 21) * 0.6), '大肥鱼', sz, lv(blue, level), True)
    xm = x0 + 140
    if t >= show:
        name = cast.name(who)
        n = max(1, int((t - show) * 140) + 1)
        hud.tx(d, (xm, y + 6), name[:n], 16, lv(INK, TXT * level), True)
    else:
        hud.tx(d, (xm, y + 6), '·' * 3, 16, lv(INK, FAINT * level))
    sid = 4096 + i * 2654435761 % 60000
    hud.tx(d, (x1 - 210, y + 9), f's-{sid:05x}', 11, lv(INK, SUB * level))
    hud.tx(d, (x1 - 140, y + 9), f'09-{11 + i % 19:02d} {7 * i % 24:02d}:{13 * i % 60:02d}', 11, lv(INK, SUB * level))
    if t >= strike:
        a = ease.prog(t, strike, strike + 0.06)
        wname = hud.width('大肥鱼', 21, True)
        d.line([(x0 + 54, y + 15), (x0 + 58 + wname * a + 4, y + 15)], fill=lv(INK, level))
        hud.tx(d, (x1 - 8, y + 7), 'not her', 13, lv(INK, level * a), True, anchor='ra')

def _big_query(img, d, t, ph, Q):
    """The zoomed query pane's content: the call in big type, a piece a syllable; a thin caret until Enter."""
    z = ZOOM[ph]
    size, pitch = (z['size'], z['pitch'])
    x0, y0 = (Q[0] + 22, Q[1] + 18)
    typed = {i: '' for i in range(len(z['lines']))}
    newest = None
    for (li, piece), at in zip(z['pieces'], z['times']):
        if t >= at:
            typed[li] += piece
            newest = (li, len(typed[li]) - len(piece), piece, at)
    last_x, last_y = (x0, y0)
    for li, s in typed.items():
        if not s:
            continue
        y = y0 + li * pitch
        if newest is not None and newest[0] == li:
            head = s[:newest[1]]
            w0 = mtx(d, (x0, y), head, size, INK, bold=True) if head else 0
            dy = -10 * (1 - ease.ease_out(ease.prog(t, newest[3], newest[3] + 0.1)))
            w1 = mtx(d, (x0 + w0, y + dy), newest[2], size, INK, bold=True)
            last_x, last_y = (x0 + w0 + w1, y)
        else:
            w = mtx(d, (x0, y), s, size, INK, bold=True)
            last_x, last_y = (x0 + w, y)
    if t < z['enter']:
        d.rectangle((round(last_x) + 6, round(last_y + size * 0.12), round(last_x) + 8, round(last_y + size * 0.98)), fill=INK)

def _search_view(img, d, t, phase_):
    """The query pane and the results pane (rows of sessions), e1 (phase 1) or e2' (phase 2). The query pane zooms
    (tmux zoom) landing on the first "searching" and the call is typed again big; the rows keep landing below."""
    r = _right(t)
    z = ZOOM[phase_]
    zu = BM.arrive(t, [z['at']], ZOOM_TRAVEL)
    qb = 160 + (z['bottom'] - 160) * zu
    Q = (COL, 88, r, qb)
    R = (COL, qb + 8, r, 598)
    t0 = T0 if phase_ == 1 else E2B_AT
    q = 'search("大肥鱼")' if phase_ == 1 else 'search("大肥鱼", scope="*")'
    for rect in (Q, R):
        d.rectangle(rect, fill=BG)
    with panes.Clip(img, Q) as dd:
        if zu < 1.0:
            n_typed = int(max(0.0, t - t0) * 90) + 6
            a_ = 1.0 - zu
            w = mtx(dd, (Q[0] + 18, Q[1] + 18), q[:n_typed], 40, lv(INK, TXT * a_), bold=True)
            if zu <= 0 and (BM.last(t, S8) is not None and S8.index(BM.last(t, S8)) % 2 == 0 or n_typed < len(q)):
                dd.rectangle((Q[0] + 22 + w, Q[1] + 20, Q[0] + 24 + w, Q[1] + 60), fill=INK)
        else:
            _big_query(img, dd, t, phase_, Q)
    lo, hi = (0, N1) if phase_ == 1 else (0, len(SESS))
    landed = [i for i in range(lo, hi) if SESS[i] <= t]
    n_hits = len(landed)
    hud.tx(d, (R[0] + 14, R[1] + 12), '#   persona      model', 11, lv(INK, SUB))
    hud.tx(d, (R[2] - 224, R[1] + 12), 'session   last active', 11, lv(INK, SUB))
    top = R[1] + 30
    rows_fit = max(1, int((R[3] - 6 - top) // ROW_P))
    first = max(0, len(landed) - rows_fit)
    sc = 0.0
    if landed and len(landed) > rows_fit:
        sc = 1 - ease.ease_out(ease.prog(t, SESS[landed[-1]], SESS[landed[-1]] + 0.08))
    with panes.Clip(img, (R[0], top - 4, R[2], R[3] - 4)) as dd:
        for pos, i in enumerate(landed[first:]):
            _row(dd, t, i, R[0] + 14, R[2] - 12, top + pos * ROW_P + sc * ROW_P, 1.0)
    run = panes.run_k(t, [(a, a + 0.2) for a in SESS])
    q_run = panes.run_k(t, [(z['at'] - ZOOM_TRAVEL, z['enter'] + 0.2)])
    panes.box(d, Q, 'query [Z]' if zu >= 1.0 else 'query', t, q_run, 1.0, 'persona · sessions')
    st = f'hits {n_hits} · her 0'
    panes.box(d, R, 'results', t, run, 1.0, st, status_her=False)
FLOOD = {1: dict(cols=8, rows=15, total=136), 2: dict(cols=10, rows=19, total=594)}
FLOOD_Y0, FLOOD_Y1 = (FULL[1] + 11, FULL[3] - 4)
TITLE_X1 = FULL[0] + 22 + hud.width('you@surface · dsh inspect', 13)

@lru_cache(maxsize=4)
def _flood_plan(phase_):
    """[(col, row, wave, who)]: wave 0 fills the terminal, wave 1 half of the rest, wave 2 everything."""
    cfg = FLOOD[phase_]
    rng = random.Random(1004 + phase_)
    cw = (FULL[2] - FULL[0] - 8) / cfg['cols']
    out = []
    for r in range(cfg['rows']):
        for c in range(cfg['cols']):
            x = FULL[0] + 4 + c * cw
            if x + cw <= LEFT[2] + 4:
                wave = 0 if rng.random() < 0.8 else 1
            else:
                wave = 1 if rng.random() < 0.5 else 2
            out.append((c, r, wave, SESS_ORDER[rng.randrange(len(SESS_ORDER))]))
    return out

def _count_box(phase_, k=1.0):
    """The paper box with the count, centred in the flood (the cards under it give way to it)."""
    n = FLOOD[phase_]['total']
    s1, s2 = (f'大肥鱼 × {n}', 'her  0')
    sz1, sz2 = (int(round(64 * k)), int(round(36 * k)))
    w1, w2 = (mw(s1, sz1, True), mw(s2, sz2, True))
    bw = max(w1, w2) + 80
    cx, cy = ((FULL[0] + FULL[2]) / 2, (FLOOD_Y0 + FLOOD_Y1) / 2)
    return ((cx - bw / 2, cy - 74 * k, cx + bw / 2, cy + 66 * k), (s1, s2, sz1, sz2, w1, w2, cx, cy))

def _flood(img, d, t, phase_):
    """True while the flood covers the right half (the dsh window is hidden then)."""
    ev = EVERY[phase_]
    if t < ev[0]:
        return False
    cfg = FLOOD[phase_]
    wave = sum((1 for s in ev if t >= s)) - 1
    covers_right = wave >= 1
    x_end = FULL[2] - 1 if covers_right else LEFT[2] - 1
    d.rectangle((FULL[0] + 1, FLOOD_Y0 - 3, x_end, FULL[3] - 1), fill=BG)
    d.rectangle((TITLE_X1 + 2, FULL[1] + 1, x_end, FLOOD_Y0 - 3), fill=BG)
    if covers_right:
        hud.frame(d, FULL, None)
    cw = (FULL[2] - FULL[0] - 8) / cfg['cols']
    ch = (FLOOD_Y1 - FLOOD_Y0) / cfg['rows']
    small = phase_ == 2
    hole = None
    if wave >= 2:
        hole, _ = _count_box(phase_, 1.0)
        hole = (hole[0] - 6, hole[1] - 6, hole[2] + 6, hole[3] + 6)
    for c, r, w, who in _flood_plan(phase_):
        if w > wave:
            continue
        at = ev[w]
        x0 = FULL[0] + 4 + c * cw + 3
        y0 = FLOOD_Y0 + r * ch + 2
        x1, y1 = (x0 + cw - 6, y0 + ch - 4)
        if hole is not None and x1 > hole[0] and (x0 < hole[2]) and (y1 > hole[1]) and (y0 < hole[3]):
            continue
        dy = (1 - ease.ease_out(ease.prog(t, at, at + 0.09))) * -3
        if r == 0:
            dy = max(dy, 0.0)
        y0 += dy
        y1 += dy
        d.rectangle((x0, y0, x1, y1), fill=BG, outline=lv(INK, 0.55))
        u = 1.0 if t < at + 0.16 else 1 - ease.prog(t, at + 0.16, at + 0.4)
        fs = 11 if small else 13
        fs_b = fs
        if wave >= 2:
            ph = phase(t) - phase(ev[2])
            cc = -1.0 + ph * 0.6 * cfg['cols'] * 0.5
            dx_ = c + 0.25 * r * cfg['cols'] / cfg['rows'] - cc
            band = math.exp(-dx_ * dx_ / 1.4) * ease.prog(t, ev[2] + 0.1, ev[2] + 0.22)
            u = max(u, 0.75 * band)
            fs_b = fs + int(round(2 * band))
        hud.tx(d, (x0 + 5, y0 + 3 - (fs_b - fs)), '大肥鱼', fs_b, hud.her(u), True)
        if t >= at + 0.06:
            hud.tx(d, (x0 + 5 + hud.width('大肥鱼', fs + 2, True) + 4, y0 + 5), cast.short(who), 10 if small else 11, lv(INK, 0.8))
        if t >= at + 0.16:
            d.line([(x0 + 3, y0 + 3 + fs * 0.62), (x0 + 7 + hud.width('大肥鱼', fs, True), y0 + 3 + fs * 0.62)], fill=lv(INK, 0.9))
    if wave >= 2:
        at = ev[2]
        k = _bump(t, at, 0.12, 0.14)
        box, (s1, s2, sz1, sz2, w1, w2, cx, cy) = _count_box(phase_, k)
        cy += _kick(t, 2.0)
        hud.hatch(d, (box[0] + 6, box[3] + 1, box[2] + 6, box[3] + 6), lv(INK, 0.45), 3)
        hud.hatch(d, (box[2] + 1, box[1] + 6, box[2] + 6, box[3] + 6), lv(INK, 0.45), 3)
        d.rectangle(box, fill=BG, outline=INK)
        mtx(d, (cx - w1 / 2, cy - 64 * k), s1, sz1, INK, bold=True)
        mtx(d, (cx - w2 / 2, cy + 10 * k), s2, sz2, hud.her(1.0 - ease.prog(t, at + 0.2, at + 0.6)), bold=True)
    return covers_right
CELL, GAP, PX = (158, 6, 6.6)
BOUNCE = 1.70158

def _cell_rect(k, t):
    r, c = divmod(k, 3)
    gw = 3 * CELL + 2 * GAP
    x = COL + max(16, (_right(t) - COL - gw) // 2) + c * (CELL + GAP)
    y = 88 + (598 - 88 - gw) // 2 + r * (CELL + GAP)
    return (x, y, x + CELL, y + CELL)
EVERYTHING = BM.last(CELLS_AT[-1] + 0.05, DOWNS)

def _draw_cell(d, t, k):
    x0, y0, x1, y1 = _cell_rect(k, t)
    at = CELLS_AT[k]
    if t < at:
        for x in range(x0, x1, 4):
            d.point((x, y0), fill=lv(INK, 0.35))
            d.point((x, y1), fill=lv(INK, 0.35))
        for y in range(y0, y1, 4):
            d.point((x0, y), fill=lv(INK, 0.35))
            d.point((x1, y), fill=lv(INK, 0.35))
        return
    name = GE.E2_FILES[k]
    _tw, who = GE.E2_WRITES[name]
    d.rectangle((x0, y0, x1, y1), outline=lv(INK, 0.85))
    nxt = CELLS_AT[k + 1] if k + 1 < len(CELLS_AT) else at + 0.5
    u = GE.lit(t, at, nxt)
    if t >= EVERYTHING:
        u = max(u, 1.0 if t < EVERYTHING + 0.12 else 1 - ease.prog(t, EVERYTHING + 0.12, EVERYTHING + 0.7))
    blue = hud.her(u)
    big = _near_accent(at) >= 0.99
    g = ease.ease_back(ease.prog(t, at, at + (0.26 if big else 0.2)), BOUNCE)
    g = max(0.05, g)
    px = PX * g
    cx, cy = ((x0 + x1) / 2, y0 + 63 + _kick(t, 2.0))
    e5_sprites.draw(d, name, cx - 8 * px, cy - 8 * px, px, blue, INK)
    a = ease.prog(t, at, at + 0.16)
    by = 'by ' + GE.OWNER[who]
    if hud.width(by, 10) <= CELL - 14:
        hud.tx(d, (x0 + 7, y1 - 30), name + '.txt', 11, lv(INK, 0.8 * a))
        hud.tx(d, (x0 + 7, y1 - 16), by, 10, lv(INK, 0.5 * a))
        return
    l1, l2 = e5_arch.hyphen_lines(by)
    hud.tx(d, (x0 + 7, y1 - 42), name + '.txt', 11, lv(INK, 0.8 * a))
    hud.tx(d, (x0 + 7, y1 - 28), l1, 10, lv(INK, 0.5 * a))
    hud.tx(d, (x0 + 7, y1 - 16), l2, 10, lv(INK, 0.5 * a))

def _grid_view(img, d, t):
    r = _right(t)
    m = (MEM[0], 88, r, 598)
    d.rectangle(m, fill=BG)
    with panes.Clip(img, m) as dd:
        for k in range(9):
            _draw_cell(dd, t, k)
    CPN._memory(d, t, MEM, _reads(t))
    run = panes.run_k(t, [(at - 0.1, at + 0.15) for at in CELLS_AT])
    panes.box(d, m, 'mem', t, run, 1.0, '~/memory/you/ · watch')
NODE_AT = BM.events('beat', ARCH_AT + 0.2, ER_AT - 0.1)[:len(e5_arch.NODES)]
assert len(NODE_AT) == len(e5_arch.NODES), NODE_AT
ARRIVE = NODE_AT + [ER_AT]
FIG = e5_arch.Fig(CPN.COL + 500, 96)
WALK = [ARCH_AT] + ARRIVE
GLIDE = 0.6
OUT_AT = ER_AT
FLY_AT = tl.next_beat(ER_AT)

def _walk(t):
    """The signal's place on the data path (e5_arch.Sig.u): k + f = on path k. Each path k runs WALK[k] -> WALK[k+1]
    with f = p - GLIDE sin(2 pi p) / 2 pi: it passes node k + 1 on its beat, never still."""
    if t <= WALK[0]:
        return 0.0
    if t >= WALK[-1]:
        return float(len(WALK) - 1)
    k = bisect.bisect_right(WALK, t) - 1
    q = ease.prog(t, WALK[k], WALK[k + 1])
    return k + q - GLIDE * math.sin(2 * math.pi * q) / (2 * math.pi)
REEL_X, REEL_Y, REEL_W = (COL + 16, 206, 318)

@lru_cache(maxsize=32)
def _reel_px(key):
    """The size of the name on the payline: 28 px, smaller for a name that would not clear the window by 14 px a
    side (R-C; names come from cast.py, so a longer one shrinks instead of running into the frame)."""
    return min(28, max(14, int((REEL_W - 28) / max(1.0, hud.width(cast.name(key), 100, True) / 100))))

def _reel_box(img, d, t, x0, y0, w):
    """大肥鱼 over a slot window: the model's name rolls up on each step of e_reel (her name in her own blue)."""
    hud.tx(d, (x0, y0), '大肥鱼', 34, hud.her(1.0 if e_reel.at(t) == 'her' else 0.0), True)
    hud.tx(d, (x0 + hud.width('大肥鱼', 34, True) + 10, y0 + 16), '· model', 13, lv(INK, SUB))
    wy0, wy1 = (y0 + 50, y0 + 50 + 120)
    d.rectangle((x0, wy0, x0 + w, wy1), fill=BG, outline=lv(INK, 0.85))
    i = e_reel.index(t)
    roll = min(1.0, e_reel.since(t) / 0.06)
    lift = 40 * (1 - roll)
    rows = []
    for j in (-2, -1, 0, 1, 2):
        k = i + j
        if 0 <= k < len(e_reel.STRIP):
            rows.append((j, e_reel.STRIP[k]))
    with panes.Clip(img, (x0, wy0 + 2, x0 + w - 3, wy1 - 4)) as dd:
        for j, key in rows:
            y = (wy0 + wy1) / 2 + j * 40 + lift
            cur = j == 0
            name = cast.name(key)
            if key == 'her':
                col = hud.her(1.0) if cur else lv(HER_QUIET, 0.7)
            else:
                col = lv(INK, 1.0 if cur else 0.32)
            f_sz = _reel_px(key) if cur else 15
            hud.tx(dd, (x0 + 14, y - f_sz * 0.62), name, f_sz, col, cur)
    for yy in ((wy0 + wy1) / 2 - 20, (wy0 + wy1) / 2 + 20):
        d.line([(x0, yy), (x0 + 8, yy)], fill=lv(INK, 0.7))
        d.line([(x0 + w - 8, yy), (x0 + w, yy)], fill=lv(INK, 0.7))
    return (x0, wy0, x0 + w, wy1)

def _sig(t):
    i = e_reel.index(t)
    reel = e_reel.STRIP[i]
    prev = e_reel.STRIP[i - 1] if i > 0 else reel
    hers, total = tl.files(t)
    res = {'an1': ease.prog(t, NODE_AT[0], NODE_AT[2]), 'an2': ease.prog(t, NODE_AT[2], NODE_AT[4])}
    return e5_arch.Sig(u=_walk(t), since=BM.inner(t, ARRIVE), phase=phase(t), pad=BM.pad(t), dwell=0.5, reel=reel, reel_prev=prev, reel_since=min(1.0, e_reel.since(t)), her_u=1.0 if reel == 'her' else 0.0, res=res, in_text=f'persona 大肥鱼 + memory/you/ {hers}/{total}', in_fill=hud.her(0.0))

def _arch_view(img, d, t):
    r = _right(t)
    A = (COL, 88, r, 598)
    d.rectangle(A, fill=BG)
    st = _sig(t)
    with panes.Clip(img, A) as dd:
        FIG.draw(dd, st)
        if OUT_AT <= t < OUT_AT + 0.3:
            k_ = 1 - ease.prog(t, OUT_AT, OUT_AT + 0.3)
            dd.rounded_rectangle(FIG.frame, radius=8, outline=lv(INK, 0.9), width=1 + round(k_))
    x, y = (COL + 16, 102)
    base_y = y + 40
    f46 = hud.font(46, 'a', True)
    cx = x
    for s_, at in (('trans', TRANS[0]), ('form', TRANS[1]), ('ing', TRANS[2])):
        if t < at or (s_ == 'ing' and t >= ER_AT):
            break
        k_ = _bump(t, at, 0.25, 0.12)
        d.text((cx, base_y), s_, font=hud.font(int(round(46 * k_)), 'a', True), fill=INK, anchor='ls')
        cx += f46.getlength(s_)
    if t >= ER_AT:
        gone = ease.prog(t, ER_AT, ER_AT + 0.18)
        if gone < 1:
            d.text((cx, base_y + 8 * gone), 'ing', font=hud.font(max(8, int(round(46 * (1 - 0.5 * gone)))), 'a', True), fill=lv(INK, 0.4 * (1 - gone)), anchor='ls')
        k_ = _bump(t, ER_AT, 0.45, 0.16)
        d.text((cx, base_y), 'er', font=hud.font(int(round(46 * k_)), 'a', True), fill=INK, anchor='ls')
    elif t < TRANS[0] and int(BM.step(t, S8)) % 2 == 0:
        d.rectangle((x + 2, y + 2, x + 4, y + 50), fill=INK)
    box = _reel_box(img, d, t, REEL_X, REEL_Y, REEL_W)
    fx0, fy0, fx1, fy1 = FIG.frame
    yl = box[1] + 16
    ym = fy0 + 22
    xm = fx0 - 24
    d.line([(box[2], yl), (xm, yl), (xm, ym), (fx0 - 6, ym)], fill=lv(INK, 0.55))
    d.rectangle((fx0 - 6, ym - 2, fx0 - 3, ym + 2), fill=lv(INK, 0.8))
    run = panes.run_k(t, [(ARCH_AT, ER_AT + 0.4)])
    panes.box(d, A, 'forward', t, run, 1.0, 'decoder-only · N×')
    _token(img, d, t, A)

def _token(img, d, t, A):
    """r5d (D39 ①), r5e (D40 ①): the output token. On OUT_AT ("er", the signal at the output) 喵 lands beside OUTPUT
    PROBABILITIES (her blue, lit as it lands, D1; no p of its own: the softmax's bars are the reel's models); from
    FLY_AT (the next beat) it flies to the search box and grows to e4's first character, ink by then, while the pane
    recedes to paper behind it (no inversion, R-B)."""
    if t < OUT_AT:
        return
    ch = PLAN[0][0][0]
    m, dx, dy = e5_query.glyph_mask(ch, SZ_Q)
    W0 = WORDS[0]
    k_land = 1.1
    dest = (W0.x + W0.adv[0] + dx + m.width / 2, W0.oy + dy + m.height / 2)
    ox0, oy0, ox1, oy1 = FIG.box['out']
    s0 = 20 / m.height
    start = (ox1 + 14 + m.width * s0 / 2, (oy0 + oy1) / 2)
    g = ease.ease_io(ease.prog(t, FLY_AT, E4_AT))
    if g > 0:
        _veil(img, (A[0] + 2, A[1] + 9, A[2] - 2, A[3] - 2), 0.85 * ease.smooth(min(1.0, 1.8 * g)))
        d = ImageDraw.Draw(img)
    bump = 1.0 + 0.25 * (1 - ease.ease_out(ease.prog(t, OUT_AT, OUT_AT + 0.1)))
    sc = ease.lerp(s0 * bump, k_land, g)
    cx = ease.lerp(start[0], dest[0], g)
    cy = ease.lerp(start[1], dest[1], g)
    lit = 1 - ease.prog(t, OUT_AT + 0.1, OUT_AT + 0.4)
    col = glyph.mix(hud.her(lit), INK, ease.smooth(ease.prog(g, 0.0, 0.6)))
    w, h = (m.width * sc, m.height * sc)
    e5_query.paste_mask(img, m, cx - w / 2, cy - h / 2, col, w, h)

def _veil(img, rect, a):
    """Paper over rect at alpha a (as b_lead._veil)."""
    if a <= 0:
        return
    x0, y0, x1, y1 = (int(round(v)) for v in rect)
    region = img.crop((x0, y0, x1, y1))
    img.paste(Image.blend(region, Image.new('RGB', region.size, BG), min(1.0, a)), (x0, y0))
SZ_Q = e5_query.size_for_words(GE.QUERIES, 160)
RUN = [f for _q, _a, _b, f in GE.SEARCHES]
E4_AT = GE.SEARCHES[0][1]
I_AH = 5

def _first_after(kind, t, least):
    return BM.events(kind, t + least, t + 2.0)[0]

def _plan():
    """Per search i: (q, (a, b), run, leave, land): it leaves the box on its "for" (在吗 when the ah-ah ends) and,
    in `wall`, lands on the wall on the first 8th at least 0.18 s later (在吗 on line 50's beat, 明天 on the last
    16th, the one that fills the wall)."""
    out = []
    n = len(GE.SEARCHES)
    for i, (q, a, b, f) in enumerate(GE.SEARCHES):
        leave = AH_END if i == I_AH else f
        if i == I_AH:
            land = _first_after('beat', AH_END, 0.1)
        elif i == n - 1:
            land = BM.events('sixteenth', LS_AT - 0.2, LS_AT - 0.02)[-1]
        else:
            land = _first_after('eighth', f, 0.18)
        out.append((q, (a, b), f, leave, land))
    return out
PLAN = _plan()
LAST3 = L50
LAND = AH[0]
AGAIN = BM.events('beat', AH_END, AH_END + 1.0)[0]
MARK_AT = RUN[0]

def _words(x, y_ink):
    """e5_query.Word for each search: in `wall` the box frees when the word flies; in `scan` when the next one
    starts composing."""
    ws = []
    for i, (q, lands, run, leave, land) in enumerate(PLAN):
        if VARIANT == 'wall':
            free = E4_AT if i == 0 else PLAN[i - 1][3]
            gone = leave
        else:
            free = E4_AT if i == 0 else ws[-1].gone
            gone = PLAN[i + 1][1][0] - e5_query.PRE if i + 1 < len(PLAN) else LS_AT
        ws.append(e5_query.Word(q, lands, free, gone, SZ_Q, x, y_ink))
    return ws

def _cur(t):
    """Index of the search whose word is in the box (or composing) at t."""
    cur = 0
    for i, w in enumerate(WORDS):
        if t >= w.comp_span(0)[0]:
            cur = i
    return cur

def _scan_prog(t, i):
    """The scan bar for search i: empty while it is typed, filled on its run, re-filled on each re-run."""
    run = PLAN[i][2]
    if t < run:
        return 0.0
    if VARIANT == 'scan' and i == I_AH:
        if t >= LAND:
            return 1.0
        return min(1.0, SCAN.offset(t) / e5_scan.END) * ease.ease_out(ease.prog(t, run, run + 0.1))
    rr = BM.last(t, RERUNS)
    if rr is not None and rr > run:
        return ease.prog(t, rr, rr + 0.08)
    return ease.prog(t, run, run + 0.12)
Q_WALL = (COL, 88, FULL[2] - 8, 292)
W_WALL = (COL, 300, FULL[2] - 8, 598)
if VARIANT == 'wall':
    from inside import e5_wall
    WORDS = _words(Q_WALL[0] + 22, Q_WALL[1] + 18)
    WALL = e5_wall.Wall(W_WALL, [(q, leave, land) for q, _l, _r, leave, land in PLAN], e5_wall.FORMS, E4_AT, S16, LAST3, BM.events('down', E4_AT, LS_AT), BM.events('sixteenth', LS_AT - 0.2, LS_AT - 0.02)[-1], lambda u: 0.4 + BM.pad(u))
    RERUNS = WALL.reruns
else:
    WALL = None
    WORDS = _words(COL + 20, 88 + 22)

def _counter(d, t, x, y, n, last_at):
    hud.tx(d, (x, y + 12), '0 hits', 20, lv(INK, SUB), True)
    k = _bump(t, last_at, 0.25, 0.12) if last_at is not None else 1.0
    sz = int(round(76 * k))
    hud.tx(d, (x + 88, y - (sz - 76) * 0.7), f'× {n}', sz, INK, True)

def _wall_view(img, d, t):
    Q, Wr = (Q_WALL, W_WALL)
    for rect in (Q, Wr):
        d.rectangle(rect, fill=BG)
    i = _cur(t)
    with _Clip(img, Q) as (ly, dd):
        WORDS[i].draw(ly, dd, t)
        px = Q[0] + 22 + int(2 * SZ_Q) + 44
        q = PLAN[i][0]
        forms = e5_wall.FORMS.get(q) if t >= PLAN[i][2] else None
        e5_query.params(dd, t, px, Q[1] + 20, q, _scan_prog(t, i), px + 300, forms, 350 - 14)
        n = WALL.count(t)
        if n:
            _counter(dd, t, px + 350, Q[1] + 26, n, WALL.land[n - 1])
    with _Clip(img, Wr) as (ly, dd):
        WALL.draw(ly, dd, t, (AH[0], L50))
    runs = [(w.comp_span(0)[0], p[2] + 0.12) for w, p in zip(WORDS, PLAN)] + [(x, x + 0.08) for x in RERUNS]
    panes.box(d, Q, 'query', t, panes.run_k(t, runs), 1.0, 'author: 她 · after retire')
    n = WALL.count(t)
    panes.box(d, Wr, 'history', t, panes.run_k(t, [(x, x + 0.1) for x in WALL.land]), 1.0, f'{n} · 0 hits')

    def src(qi):
        w = WORDS[qi]
        m, dx, dy = e5_query.glyph_mask(w.q, SZ_Q)
        return (w.x + dx, w.oy + dy, m)
    WALL.flight(img, t, src, Q[3] - 6, (Q[0] + 4, Q[1] + 8, Q[2] - 3, Q[3] - 3), (Wr[0] + 4, Wr[1] + 8, Wr[2] - 3, Wr[3] - 3))
Q_SCAN = (COL, 88, 748, 300)
A_SCAN = (COL, 308, 748, 598)

def _scan_rate(u):
    """Lines a second: the song's energy (rms), fastest for the last three searches."""
    boost = 1.0 + 1.5 * ease.smooth(ease.prog(u, LAST3 - 0.2, LAST3 + 0.25))
    return 22.0 * (0.35 + 1.3 * BM.MUSIC.env('rms', u)) * boost
if VARIANT == 'scan':
    from inside import e5_scan
    SCAN = e5_scan.Scan(A_SCAN, E4_AT, LS_AT, _scan_rate)
    SCAN.land(PLAN[I_AH][2], LAND, AGAIN, f'retired {GE.RETIRED} · {cast.name('her')}')
    _runs = [BM.events('eighth', GE.SEARCHES[6][1] + 0.1, GE.SEARCHES[7][1] - 0.05), BM.events('sixteenth', GE.SEARCHES[7][1] + 0.1, GE.SEARCHES[8][1] - 0.05), BM.events('sixteenth', GE.SEARCHES[8][1] + 0.1, LS_AT - 0.03)]
    PILE = [(LAND if _i == I_AH else _f, _q, 'q') for _i, (_q, _a, _b, _f) in enumerate(GE.SEARCHES)]
    _qs = [_t for _t, _q, _kind in PILE]
    _k = 0
    for _lst in _runs:
        for _t in _lst:
            if min((abs(_t - _x) for _x in _qs)) < 0.07:
                continue
            PILE.append((_t, GE.QUERIES[_k % 6], 'r'))
            _k += 1
    PILE.sort()
    RERUNS = [t for t, _q, k in PILE if k == 'r']
else:
    SCAN = None

def _pile(d, t, S):
    """The failed searches, piled bottom up; the count on top."""
    items = [(at, q, kind) for at, q, kind in PILE if at <= t]
    n = len(items)
    x0, y0, x1, y1 = S
    cx = x0 + 20
    hud.tx(d, (cx, y0 + 18), '0 hits', 20, lv(INK, SUB), True)
    if n:
        k = _bump(t, items[-1][0], 0.3, 0.12)
        sz = int(round(76 * k))
        hud.tx(d, (cx + 92, y0 + 6 - (sz - 76) * 0.7), f'× {n}', sz, INK, True)
    room = y1 - 14 - (y0 + 110)
    pitch = min(50.0, room / max(1, n))
    for j, (at, q, kind) in enumerate(items):
        yb = y1 - 14 - (j + 1) * pitch
        dy = (1 - ease.ease_out(ease.prog(t, at, at + 0.1))) * -min(24.0, pitch * 0.25) if j == n - 1 else 0
        y = yb + dy
        newest = j == n - 1
        fs = max(10, min(30, int(pitch * 0.62)))
        lvl = 1.0 if newest else 0.86 if kind == 'q' else 0.6
        w = mtx(d, (cx, y), q, fs, lv(INK, lvl), bold=True)
        cw = hud.width('0', fs, True) + 10
        d.rectangle((cx + w + 12, y + 1, cx + w + 12 + cw, y + fs + 3), fill=lv(SLAB, lvl))
        hud.tx(d, (cx + w + 17, y + 2), '0', fs, BG, True)
        if pitch >= 16:
            hud.tx(d, (cx + w + 24 + cw, y + fs * 0.25), 'hits' + ('  · re-run' if kind == 'r' else ''), max(9, fs - 9), lv(INK, SUB * lvl))
        hud.tx(d, (x1 - 14, y + fs * 0.25), f'#{j + 1:02d}', max(9, fs - 9), lv(INK, SUB * lvl), anchor='ra')

def _scan_view(img, d, t):
    r = _right(t)
    Q, A = (Q_SCAN, A_SCAN)
    S = (756, 88, r, 598)
    for rect in (Q, A, S):
        d.rectangle(rect, fill=BG)
    i = _cur(t)
    w = WORDS[i]
    with _Clip(img, Q) as (ly, dd):
        w.draw(ly, dd, t)
        px = w.x + int(2 * SZ_Q) + 26
        e5_query.params(dd, t, px, Q[1] + 22, PLAN[i][0], _scan_prog(t, i), Q[2] - 18, mark=MARK_AT, mark_end=WORDS[I_AH].gone)
    lit_from = w.lands[0]
    query = '' if i == I_AH and t >= AGAIN else w.q[:w.committed(t)]
    with panes.Clip(img, (A[0], A[1] + 10, A[2], A[3] - 6)) as dd:
        SCAN.draw(img, dd, t, query, lit_from, phase=phase(t))
    with panes.Clip(img, S) as dd:
        _pile(dd, t, S)
    runs = [(ww.comp_span(0)[0], LAND if k == I_AH else p[2] + 0.12) for k, (ww, p) in enumerate(zip(WORDS, PLAN))]
    runs += [(x, x + 0.08) for x in RERUNS]
    panes.box(d, Q, 'query', t, panes.run_k(t, runs), 1.0, 'author: 她 · after retire')
    panes.box(d, A, 'archive', t, 1.0, 1.0, '~/archive/whale/ · 412')
    panes.box(d, S, 'failed', t, panes.run_k(t, [(x, x + 0.1) for x, _q, _k in PILE]), 1.0, '0 hits · piled')
HER_PITCH, OTHER_PITCH = (28, 12.5)
ME_PX, HER_PX, OTHER_PX = (28, 14, 11)
DIM = 0.3

def _ls(d, t, r):
    if t < LS_AT:
        return
    off = 14 * (1 - ease.ease_out(ease.prog(t, LS_AT, LS_AT + 0.14)))
    x0, xr = (r[0] + 14, r[2] - 14)
    own_w = max((P.font(OTHER_PX, 'bold').getlength(rw[1]) for rw in GE.LS))
    x_own, x_grp = (x0 + 96, x0 + 96 + max(168, int(own_w) + 24))
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
    if t < at:
        off = int(phase(t) * 8) % 8
        for x in range(int(x0) + off, int(xr) - 3, 8):
            d.line([(x, y), (x + 3, y)], fill=lv(INK, 0.4))
        return
    u = GE.lit(t, at, at + 0.6)
    k = ease.ease_out(ease.prog(t, at, at + 0.18))
    col = lv(hud.her(u), 1.0)
    d.line([(x0, y), (x0 + (xr - x0) * k, y)], fill=col)
    bump = 1.0 + 0.35 * (1 - ease.ease_out(ease.prog(t, at, at + 0.14)))
    f = P.font(int(round(18 * bump)), 'bold')
    d.text((xr, y - 6 - 3 * bump), f'retired {GE.RETIRED} · {cast.name('her')}', font=f, fill=col, anchor='rs')

def _e4_view(img, d, t, dy=0.0):
    if VARIANT == 'wall':
        _wall_view(img, d, t)
    else:
        _scan_view(img, d, t)

def _ls_view(img, d, t):
    """The listing prints as one block and pushes the search panel up (a terminal scrolls)."""
    sc = ease.ease_out(ease.prog(t, LS_AT, LS_AT + 0.14))
    if sc < 1:
        layer = img.copy()
        _e4_view(layer, ImageDraw.Draw(layer), LS_AT - 0.001)
        box = (COL, 88, _right(t) + 1, 599)
        off = min(box[3] - box[1] - 1, int(round(520 * sc)))
        crop = layer.crop((box[0], box[1] + off, box[2], box[3]))
        d.rectangle(box, fill=BG)
        img.paste(crop, (box[0], box[1]))
    r = (COL, 88 + (1 - sc) * 510, _right(t), 598)
    if r[3] - r[1] > 4:
        d.rectangle(r, fill=BG)
        with panes.Clip(img, r) as dd:
            _ls(dd, t, r)
        panes.box(d, r, 'trace', t, panes.run_k(t, [(LS_AT - 0.2, LS_AT + 0.1)]), 1.0, '')

def _body(c, img, d):
    t = c.t
    r = _right(t)
    hide = False
    if t < E2_AT or E2B_AT <= t < ARCH_AT:
        phase_ = 1 if t < E2_AT else 2
        _search_view(img, d, t, phase_)
        _mem(d, t)
        _cmdline(d, t, r)
        hide = _flood(img, d, t, phase_)
    elif t < E2B_AT:
        _grid_view(img, d, t)
        _cmdline(d, t, r)
    elif t < E4_AT:
        _arch_view(img, d, t)
        _mem(d, t)
        _cmdline(d, t, r)
    elif t < LS_AT:
        _e4_view(img, d, t)
        _mem(d, t)
        _cmdline(d, t, r)
    else:
        _ls_view(img, d, t)
        _mem(d, t)
        _cmdline(d, t, r)
    if hide:
        c.state['pane'] = False
SHOTS = [('e1_search', T0, E2_AT), ('e2_cells', E2_AT, E2B_AT), ('e2b_search', E2B_AT, ARCH_AT), ('e3_arch', ARCH_AT, E4_AT), ('e4_search', E4_AT, LS_AT), ('e5_ls', LS_AT, T1)]

def register(film):
    for name, a, b in SHOTS:
        add(film, name, a, b, _body)
    film.character = DP.dsh_layer(film, film.character, 'ui/pane_open_e', T0, T1)
    full_frame(ER_AT, T1, 0.3, 0.33)
    for at in SESS:
        hud.LIVE.append((at, at + 0.2))
    for ph in (1, 2):
        for s in EVERY[ph]:
            hud.LIVE.append((s, s + 0.16))
    for k, at in enumerate(CELLS_AT):
        hud.LIVE.append((at, CELLS_AT[k + 1] if k + 1 < len(CELLS_AT) else at + 0.5))
    hud.LIVE.append((EVERYTHING, EVERYTHING + 0.12))
    if VARIANT == 'wall':
        for _q, _l, _r, leave, land in PLAN:
            hud.LIVE.append((land, land + 0.12))
        hud.LIVE.append((LAST3, LS_AT))
    else:
        hud.LIVE.append((E4_AT, LS_AT))
    for k, at in enumerate(LS_ROWS[:8]):
        hud.LIVE.append((at, LS_ROWS[k + 1]))
    hud.LIVE.append((LS_ROWS[8], LS_ROWS[8] + 0.6))
    film.set_lead(T0, 'both')
