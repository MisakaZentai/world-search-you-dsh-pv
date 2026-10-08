"""Group A, opening sample (sample_open/README.md): group A redone against film 1's opening, not v1/v2.

  a_f1      0-1.62      film 1's last frame, pixel for pixel: her 在吗？ waits, unsent, in the composer
  a_grow    1.62-3.58   the frame grows out of that card: her archived session fills the frame, the deep sea
                        lifts to paper, the header and the band come up
  a_end     3.58-7.05   her session's last rows land one per beat (film 1's ending, in dsh's own rows)
  a_send    7.05-10.54  you send her 在吗？: it goes out as your message; on the next stab the turn fails
                        (本轮运行失败 · Model Not Exist · INVALID_REQUEST, dsh's own row)
  a_notice  10.54-13.61 人格已切换 · 记忆已保留; you click ~/memory/you/: the window folds into the right column,
                        the terminal comes in, her 8 blocks light in 16ths
  a_sort    13.61-40.86 the sort of v2 (one step per sung syllable), but each bar carries the words of yours she
                        kept; in the 3.5 s after each line the right scrolls back to where she wrote that file;
                        "明天见" fills the terminal on "last" and is covered on the next beat (pinned)

Switch: DSH_A=open (film.py). groups.a stays as it was (B imports its constants; the new chat and the IME
commits are the same). The dsh pane for this span is shot at the full width (ui/page_open.py -> ui/pane_open/),
the window's left edge and zoom are win(t) below; the character layer for t < T1 is this module's.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import beatmap as BM
import cast
import hud
import syl
import tl
from groups import a as A
from groups.base import big_word
from hud import BG, INK, SLAB, X0, lv
from inspect_ import prompt_chips
from tuikit import ease, glyph
from tuikit.uipane import PaneFrames
W, B = (tl.W, tl.B)
T0, T1 = tl.span('A')
P = tl.p
FPS = P.FPS
HERE = tl.HERE
STAB = A.STAB
SURF = STAB[1]
GROW_END = B(5.5)
LIFT_END = B(7.5)
CHROME_AT = GROW_END
ROW_AT = [B(8), B(9), B(10), B(11.5), B(13)]
SEND_AT = B(16)
ERROR_AT = B(19.5)
NOTICE_AT = A.NOTICE_AT
PATH_AT = A.UNASSIGN_AT
SHRINK = (PATH_AT + 0.06, PATH_AT + 0.56)
CMD_AT = B(29)
STRIP_AT = [tl.grid(CMD_AT, k, 4) for k in range(8)]
LINE2_AT = B(30)
SORT_AT = A.SORT_AT
PIN_AT, BACK_AT, NEWCHAT_AT = (A.PIN_AT, A.FULL_BACK, A.NEWCHAT_AT)
WIDE_Z = 1.4
PANE_FULL = (25, 57, 1255, 603)

def win(t: float):
    """(left edge of the window frame in frame px, zoom) at t."""
    u = ease.ease_io(ease.prog(t, *SHRINK))
    return (ease.lerp(24, P.rect('right')[0], u), ease.lerp(WIDE_Z, 1.0, u))
WORDS = {'first_hello': '你好', 'typo_you_made': '今天好累了了', 'laugh_0314': '哈哈哈哈哈哈', 'your_cat': '这是我家的猫～', 'weather': '下雨了，我最喜欢下雨天。', 'goodnight': '晚安', 'see_you': '明天见', 'last_msg': '你会一直在吗？'}
SCORE = A.SCORE
SWEETEST = A.SWEETEST
L0, L1, L2, L3 = (A.L0, A.L1, A.L2, A.L3)
LAND_AT = A.LAND_AT
PULL = 24

def _script():
    s = A._Script(tl.HER_FILES)
    s.at(L0[0]).say('bubble · pass 1 · cmp 1/7').cmp(6)
    for k, j in enumerate(range(5, -1, -1)):
        s.at(L0[1 + k]).say(f'bubble · pass 1 · cmp {k + 2}/7').cmp(j)
    s.at(L0[7]).say('bubble · pass 2').ptr(6)
    s.at(L0[8]).say('bubble · pass 2 · cmp 1/6').cmp(6)
    for k, j in enumerate(range(5, 0, -1)):
        s.at(L1[k]).say(f'bubble · pass 2 · cmp {k + 2}/6').cmp(j)
    s.at(L1[5]).say('bubble · 2 passes').mark('rule', 1)
    s.focus.append((L1[5], (), 'none'))
    key = s.order[7]
    s.at(L2[0]).say(f'insertion · key {key} ({SCORE[key]})').pull(key, PULL)
    for k in range(5):
        s.at(L2[1 + k]).say(f'insertion · shift {k + 1}').up(key)
    above = s.order[s.order.index(key) - 1]
    for k in (6, 7, 8):
        s.at(L2[k]).say(f'insertion · {SCORE[key]} < {SCORE[above]}').hold((above, key))
    s.at(L2[9]).say(f'insertion · placed {s.order.index(key) + 1}/8').drop(key)
    s.focus.append((L2[9] + 0.3, (), 'none'))
    for k in range(8):
        s.at(L3[k]).say(f'selection · scan {k + 1}/8 · max {SCORE[SWEETEST]}').scan(k)
    s.at(L3[0]).mark('max', SWEETEST)
    s.at(L3[8]).say('selection · max → last').pull(SWEETEST, PULL)
    s.at(L3[9]).to_end(SWEETEST, 0.24)
    s.at(LAND_AT - 0.16).drop(SWEETEST, 0.16)
    s.focus.append((LAND_AT, (), 'none'))
    s.at(LAND_AT).say('selection · max → last · done')
    s.at(PIN_AT).mark('cover', SWEETEST)
    return s
S = _script()
INSERT_KEY = next((n for t, n in S.lit if abs(t - L2[0]) < 1e-06))

def _lit_spans():
    ts = sorted({t for t, _n in S.lit} | {t for t, *_r in S.focus})
    out = []
    for t, _n in S.lit:
        nxt = next((x for x in ts if x > t + 1e-06), t + 0.5)
        out.append((t, min(nxt, t + 0.5) if t < LAND_AT - 0.2 else tl.WE(3, 9)))
    return out
LIT = _lit_spans()

def _state(t):
    k = max((i for i, sn in enumerate(S.snaps) if sn[0] <= t + 1e-09)) if t >= S.snaps[0][0] else 0
    t1, o1, x1, dur = S.snaps[k]
    t0, o0, x0, _d = S.snaps[k - 1] if k else S.snaps[0]
    u = ease.ease_io(ease.prog(t, t1, t1 + dur)) if k else 1.0
    return {n: (ease.lerp(o0.index(n), o1.index(n), u), ease.lerp(x0.get(n, 0), x1.get(n, 0), u)) for n in o1}

def _lit(name, t):
    k = 0.0
    for a, n in S.lit:
        if n != name or t < a:
            continue
        b = next((y for x, y in LIT if abs(x - a) < 1e-06), a + 0.4)
        k = max(k, 1.0 if t < b else 1 - ease.prog(t, b, b + hud.LIVE_FADE))
    return k

def _gap(line):
    return tl.next_beat(tl.WE(line, len(tl.L.lines[line].words) - 1))
GOTO = [(_gap(0), 'see_you'), (_gap(1), 'last_msg'), (_gap(2), INSERT_KEY), (L3[8], 'see_you')]
GOTO_DUR = [2 * tl.C.BEAT, 2 * tl.C.BEAT, 2 * tl.C.BEAT, 0.5]
MARK_AT = [tl.at_beat(t0 + d, 1) if i < 3 else None for i, ((t0, _k), d) in enumerate(zip(GOTO, GOTO_DUR))]
ROW_Y0, PITCH, BH = (150, 46, 28)
LX0, LX1 = (X0 + 262, hud.XR - 60)
SURF_Y = ROW_Y0 - 12
WATER_BOTTOM = ROW_Y0 + 7 * PITCH + BH + 26
RISE = 0.3
BIG_H = 172
LO, HI = (min(SCORE.values()), max(SCORE.values()))

def _retime():
    out = []
    for k, (t, o, x, dur) in enumerate(S.snaps):
        nxt = S.snaps[k + 1][0] if k + 1 < len(S.snaps) else t + 1.0
        out.append((t, o, x, max(dur, min(RISE, nxt - t - 0.02)) if dur <= 0.16 else dur))
    S.snaps[:] = out
_retime()

def _row_y(r):
    return ROW_Y0 + r * PITCH

def _bx(name):
    return LX0 + (SCORE[name] - 250) / (HI - 250) * (LX1 - LX0)

def _br(name):
    return 8 + 12 * (SCORE[name] - LO) / (HI - LO)

def _latest(seq, t):
    cur = None
    for item in seq:
        if item[0] <= t + 1e-09:
            cur = item
    return cur

def _move(name, t):
    """(u 0..1, rows moved: < 0 up) of the step `name` is making at t, or None."""
    if t < S.snaps[0][0]:
        return None
    k = max((i for i, sn in enumerate(S.snaps) if sn[0] <= t + 1e-09))
    if k == 0:
        return None
    t1, o1, _x1, dur = S.snaps[k]
    a, b = (S.snaps[k - 1][1].index(name), o1.index(name))
    if a == b or t > t1 + dur:
        return None
    return (ease.prog(t, t1, t1 + dur), b - a)

def _center(name, t, st=None):
    """The bubble's centre at t (with the rise's zigzag) and its radii (rx, ry)."""
    st = st or _state(t)
    row, xo = st[name]
    cx, cy, r = (_bx(name) + xo, _row_y(row) + BH / 2, _br(name))
    rx = ry = r
    mv = _move(name, t)
    if mv:
        u, dr = mv
        s = math.sin(math.pi * u)
        if dr < 0:
            cx += 4.5 * math.sin(2 * math.pi * 1.5 * u) * (1 - 0.4 * u)
            rx, ry = (r * (1 + 0.16 * s), r * (1 - 0.16 * s))
        else:
            rx, ry = (r * (1 - 0.06 * s), r * (1 + 0.06 * s))
    return (cx, cy, rx, ry)

def _lit_at(name, t):
    return any((abs(a - t) < 1e-06 and n == name for a, n in S.lit))

def _moves():
    """[(t, name, rows)] every step the lit one makes (rows < 0: up)."""
    out = []
    for k in range(1, len(S.snaps)):
        t1, o1 = (S.snaps[k][0], S.snaps[k][1])
        o0 = S.snaps[k - 1][1]
        for n in o1:
            if o0.index(n) != o1.index(n) and _lit_at(n, t1):
                out.append((t1, n, o1.index(n) - o0.index(n)))
    return out
MOVES = _moves()
_SNAP_T = [sn[0] for sn in S.snaps]
TOP_AT = [(t, n) for t, n, dr in MOVES if dr < 0 and S.snaps[_SNAP_T.index(t)][1].index(n) == 0]
POP_AT = L1[8]
DOME_X = _bx(next((n for t, n, dr in MOVES if L1[0] - 1e-06 <= t < POP_AT and dr < 0)))

def _trail(t):
    """[(x, y, r, a)] the small bubbles every step sheds (three each), rising to the surface."""
    out = []
    for ts, n, dr in MOVES:
        if t < ts or t > ts + 3.0:
            continue
        cx, cy, _rx, ry = _center(n, ts - 0.001)
        for i in range(3):
            t0 = ts + 0.07 * i
            if t < t0:
                continue
            v = 85 + 18 * i
            y = cy - ry * 0.2 - v * (t - t0)
            if y <= SURF_Y + 2:
                continue
            x = cx + (-0.45, 0.15, 0.5)[i] * ry + 2.2 * math.sin((t - t0) * 9 + i)
            out.append((x, y, 2.8 - 0.5 * i, min(1.0, (y - SURF_Y) / 30)))
    return out

def _ambient(t):
    """Small ambient bubbles: one on every other beat from the sort's start, rising at 55 px/s."""
    out = []
    k0 = int(math.ceil(tl.C.beat_of(SORT_AT + 0.4)))
    k1 = int(tl.C.beat_of(min(t, T1)))
    for k in range(k0, k1 + 1, 2):
        tb = B(k)
        if tb > t:
            break
        h = math.modf(abs(math.sin(k * 12.9898) * 43758.5453))[0]
        x = LX0 - 20 + h * (LX1 - LX0 + 50)
        y = WATER_BOTTOM - 55 * (t - tb)
        if y <= SURF_Y + 2:
            continue
        out.append((x + 2 * math.sin((t - tb) * 3 + k), y, 1.4 + 1.6 * h, min(1.0, (y - SURF_Y) / 30)))
    return out

def _ripples(t):
    """[(x, age)] ripples on the surface: a bubble reaching the top row, the pop."""
    out = []
    for ta, n in TOP_AT:
        if 0 <= t - ta - RISE * 0.7 < 0.7:
            out.append((_bx(n), t - ta - RISE * 0.7))
    if 0 <= t - POP_AT < 0.7:
        out.append((DOME_X, t - POP_AT))
    return out

def _surface(d, t, level):
    xr_ = hud.xr(t) - 8
    pts = [(x, SURF_Y + 1.1 * math.sin(x / 19 + t * 2.4)) for x in range(int(LX0 - 70), int(xr_), 3)]
    d.line(pts, fill=lv(INK, 0.5 * level), width=1)
    for x, age in _ripples(t):
        p = age / 0.7
        for k in (0, 1):
            q = p - 0.25 * k
            if 0 < q < 1:
                rx = 5 + 34 * q
                d.ellipse((x - rx, SURF_Y - rx * 0.2, x + rx, SURF_Y + rx * 0.2), outline=lv(INK, 0.55 * (1 - q) * level))

def _dome(d, t, level):
    """Line 1: the small bubbles gather under the surface into one bubble that grows a syllable at a time and
    pops on "pops" (lit while it bursts, D1)."""
    if not L1[0] <= t < POP_AT + 0.6:
        return
    x, y = (DOME_X, SURF_Y)
    if t < POP_AT:
        k = sum((1 for s in L1[:8] if t >= s))
        r = 3 + 1.7 * k
        d.ellipse((x - r, y, x + r, y + 2 * r), fill=lv(hud.HER_QUIET, 0.18 * level), outline=hud.her(0, level), width=2)
        d.arc((x - r * 0.6, y + r * 0.35, x + r * 0.15, y + r * 1.1), 190, 260, fill=BG, width=2)
        return
    p = (t - POP_AT) / 0.5
    col = hud.her(1.0 - ease.prog(t, POP_AT + 0.3, POP_AT + 0.5), level)
    r0 = 3 + 1.7 * 8
    if p < 1:
        rr = r0 * (1 + 1.3 * ease.ease_out(p))
        d.ellipse((x - rr, y + r0 - rr, x + rr, y + r0 + rr), outline=lv(col, 1 - p), width=2)
        for j in range(8):
            ang = j * math.pi / 4 + 0.3
            dist = r0 + 26 * ease.ease_out(p)
            px, py = (x + math.cos(ang) * dist, y + r0 + math.sin(ang) * dist * 0.8 - 10 * p)
            s = 3.2 - 1.8 * p
            d.ellipse((px - s, py - s, px + s, py + s), fill=lv(col, 1 - p))

def _bubble(d, cx, cy, rx, ry, u, level, morph=None):
    """One memory bubble: a light tint, her outline (lit while it moves, D1), a highlight on the skin."""
    col = hud.her(u, level)
    fill = lv(col, 0.2 + 0.18 * u)
    if morph is not None:
        box, g = morph
        rect = tuple((int(round(ease.lerp(a, b, g))) for a, b in zip(box, (cx - rx, cy - ry, cx + rx, cy + ry))))
        rad = int(min(ease.lerp(2, max(rx, ry), g), (rect[2] - rect[0]) // 2 - 1, (rect[3] - rect[1]) // 2 - 1))
        d.rounded_rectangle(rect, radius=max(0, rad), fill=fill, outline=col, width=2)
        return
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=fill, outline=col, width=3 if u > 0.5 else 2)
    d.arc((cx - rx * 0.62, cy - ry * 0.62, cx + rx * 0.2, cy + ry * 0.2), 195, 255, fill=BG, width=2)
    d.ellipse((cx + rx * 0.28 - 1.2, cy - ry * 0.5 - 1.2, cx + rx * 0.28 + 1.2, cy - ry * 0.5 + 1.2), fill=BG)

def _thread(d, x0, x1, y, level):
    for x in range(int(x0), int(x1) - 2, 5):
        d.line([(x, y), (x + 1, y)], fill=lv(INK, 0.4 * level))

def _row_slab(st):
    row, xo = st[SWEETEST]
    y = _row_y(row)
    return (X0 - 6 + xo, y - 4, _bx(SWEETEST) + xo + _br(SWEETEST) + 44, y + BH + 4)

def term_rect(t):
    x, _z = win(t)
    L = hud.LEFT
    return (L[0], L[1], int(round(min(L[2], x - 16))), L[3])

def big_box():
    """The ink box of 明天见 at rest (for the slab)."""
    im = Image.new('RGB', (P.W, P.H))
    return big_word(ImageDraw.Draw(im), WORDS[SWEETEST], (hud.XR - 6, 214), BIG_H, INK, 'ra')
BIG_BOX = big_box()

def _big_u(t):
    """0..1: 明天见 up (from LAND_AT) until the slab goes back to its row (BACK_AT .. +0.4)."""
    if t < LAND_AT:
        return 0.0
    return 1 - ease.ease_io(ease.prog(t, BACK_AT, BACK_AT + 0.4))

def _bars(d, t):
    st = _state(t)
    a_txt = ease.prog(t, SORT_AT + 0.25, SORT_AT + 0.5)
    level = 1 - 0.78 * _big_u(t)
    water = ease.prog(t, SORT_AT, SORT_AT + 0.4)
    for x, y, r, a in _ambient(t):
        d.ellipse((x - r, y - r, x + r, y + r), outline=lv(INK, 0.32 * a * level * water))
    _surface(d, t, level * water)
    f_score = P.font(13, 'bold')
    for k0, name in enumerate(tl.HER_FILES):
        row, xo = st[name]
        y = _row_y(row)
        cx, cy, rx, ry = _center(name, t, st)
        u = _lit(name, t)
        if a_txt > 0:
            tw = hud.width(WORDS[name], 17)
            hud.tx(d, (X0 + xo, y + 1), WORDS[name], 17, lv(INK, 0.95 * a_txt * level))
            d.text((X0 + xo, y + 22), name, font=P.font(10), fill=lv(INK, 0.45 * a_txt * level))
            _thread(d, X0 + xo + tw + 10, cx - rx - 6, cy, a_txt * level)
            d.text((cx + rx + 7, cy - 8), str(SCORE[name]), font=f_score, fill=lv(INK, a_txt * level))
        g = ease.ease_io(ease.prog(t, SORT_AT + 0.02 * k0, SORT_AT + 0.02 * k0 + 0.36))
        if g < 1:
            _bubble(d, cx, cy, rx, ry, 1.0, level, morph=(hud.block_rect(k0, t), g))
        else:
            _bubble(d, cx, cy, rx, ry, u, level)
    for x, y, r, a in _trail(t):
        d.ellipse((x - r, y - r, x + r, y + r), outline=lv(hud.HER_QUIET, 0.9 * a * level), width=1)
    _dome(d, t, level)
    mx = _latest([m for m in S.marks if m[1] == 'max'], t)
    if mx and t < L3[8]:
        cx, cy, rx, _ry = _center(mx[2], t, st)
        xx = cx - rx - 44
        d.rectangle((xx, cy - 9, xx + 34, cy + 9), fill=SLAB)
        d.text((xx + 5, cy - 7), 'max', font=P.font(12), fill=BG)
    rule = _latest([m for m in S.marks if m[1] == 'rule'], t)
    if rule and t < L2[0]:
        yy = _row_y(rule[2] + 1) - 9
        uu = ease.ease_out(ease.prog(t, rule[0], rule[0] + 0.2))
        for xx in range(int(X0), int(X0 + (LX1 + 40 - X0) * uu), 8):
            d.line([(xx, yy), (xx + 4, yy)], fill=lv(INK, 0.6))
    fo = _latest(S.focus, t)
    if fo and fo[1] and (t < LAND_AT):
        t_f, names, kind = fo
        ys = [_row_y(st[n][0]) for n in names]
        x0_, y0_, y1_ = (X0 - 12 + min((st[n][1] for n in names)), min(ys) - 4, max(ys) + BH + 4)
        w = 3 if kind == 'pulse' and t - t_f < 0.12 else 2
        d.line([(x0_ + 6, y0_), (x0_, y0_), (x0_, y1_), (x0_ + 6, y1_)], fill=lv(INK, 0.9), width=w)
        cy = (y0_ + y1_) / 2
        d.polygon([(x0_ - 9, cy - 6), (x0_ - 2, cy), (x0_ - 9, cy + 6)], fill=INK)
    lab = _latest(S.labels, t)
    if lab and t < PIN_AT + 0.3:
        a = (1 - ease.prog(t, PIN_AT, PIN_AT + 0.3)) * level
        d.text((X0, ROW_Y0 - 32), lab[1], font=P.font(13), fill=lv(INK, 0.75 * a))
    if t >= LAND_AT:
        _big(d, t, st, None)

def _big(d, t, st, cover):
    bump = 1.0 + 0.12 * (1 - ease.prog(t, LAND_AT, LAND_AT + 0.12))
    if t < PIN_AT + 0.18:
        big_word(d, WORDS[SWEETEST], (hud.XR - 6, 214), BIG_H, INK, 'ra', bump=bump)
    if t < PIN_AT:
        return
    u = ease.ease_out(ease.prog(t, PIN_AT, PIN_AT + 0.18))
    bx0, by0, bx1, by1 = BIG_BOX
    big = (bx0 - 18, by0 - 16, ease.lerp(bx0 - 18, bx1 + 18, u), by1 + 16)
    r = ease.ease_io(ease.prog(t, BACK_AT, BACK_AT + 0.4))
    row = _row_slab(st)
    rect = tuple((ease.lerp(a, b, r) for a, b in zip(big, row)))
    d.rectangle(rect, fill=SLAB)
    if u >= 1:
        _pin_label(d, rect, r)
PIN_LABEL = 'pinned · 留到最后'
PIN_SIZE = (26, 12)
PIN_PAD = 8

def _pin_label(d, rect, r):
    """The label on the block: big and centred while it covers 明天见; as the block goes back into its row it
    hands over to the row's small `pinned` (bottom right, 11 px), which is what group B carries on from 40.86
    (groups/b_lead.py `_fold_over`), so the seam does not jump."""
    x0, y0, x1, y1 = rect
    c = ease.smooth(ease.prog(r, 0.4, 0.9))
    if c < 1:
        size = int(round(ease.lerp(PIN_SIZE[0], PIN_SIZE[1], r)))
        while size > 9:
            f = hud.font(size, PIN_LABEL, bold=True)
            w = d.textlength(PIN_LABEL, font=f)
            bb = d.textbbox((0, 0), PIN_LABEL, font=f, anchor='lm')
            if w + 2 * PIN_PAD <= x1 - x0 and bb[3] - bb[1] + 2 * PIN_PAD <= y1 - y0:
                break
            size -= 1
        else:
            f = None
        if f is not None:
            cx = ease.lerp((x0 + x1) / 2, x1 - PIN_PAD - 2 - w / 2, r)
            d.text((cx - w / 2, (y0 + y1) / 2), PIN_LABEL, font=f, fill=glyph.mix(SLAB, BG, 1 - c), anchor='lm')
    if c > 0:
        d.text((x1 - 8, y1 - 16), 'pinned', font=P.font(11), fill=glyph.mix(SLAB, BG, c), anchor='ra')

def _boot_text(d, t):
    if t < CMD_AT or t >= SORT_AT + 0.25:
        return
    go = 1 - ease.prog(t, SORT_AT, SORT_AT + 0.25)
    l1 = f'persona=大肥鱼  session=archived  model={cast.term('her')} (offline)'
    hud.tx(d, (X0, 100), l1, 13, lv(INK, 0.8 * go))
    if t >= LINE2_AT:
        a = ease.prog(t, LINE2_AT, LINE2_AT + 0.1) * go
        hud.tx(d, (X0, 122), 'persona=大肥鱼  model=—  memory=~/memory/you/ (8 files, by her)', 13, lv(INK, 0.8 * a))

def _strip(d, img, t):
    shown = sum((1 for s in STRIP_AT if t >= s))
    if shown == 0:
        return
    before = img.copy() if shown < 8 else None
    hud.strip(d, t, {})
    if before is not None:
        for k in range(shown, 8):
            r = hud.block_rect(k, t)
            box = (int(r[0]) - 3, int(r[1]) - 3, int(r[2]) + 9, int(r[3]) + 3)
            img.paste(before.crop(box), box[:2])
        ar = hud.archive_rect(t)
        box = (int(ar[0]) - 2, int(ar[1]) - 2, 96, int(ar[3]) + 50)
        img.paste(before.crop(box), box[:2])
    for k in range(min(shown, 8)):
        at = STRIP_AT[k]
        until = STRIP_AT[k + 1] if k + 1 < 8 else tl.next_beat(at)
        u = 1.0 if t < until else 1 - ease.prog(t, until, until + hud.LIVE_FADE)
        if u <= 0:
            continue
        r = hud.block_rect(k, t)
        d.rectangle(r, fill=hud.her(u))
        d.text((r[0] + 4, r[1] + 6), hud.chip(d, tl.HER_FILES[k], r[2] - r[0]), font=P.font(11), fill=BG)

def _body(c, img, d):
    t = c.t
    if t < CHROME_AT:
        c.no_chrome = True
    if t < SHRINK[0]:
        return
    rect = term_rect(t)
    if rect[2] - rect[0] < 200:
        return
    title = 'you@surface · sort' if t >= SORT_AT else 'you@surface · dsh inspect'
    a = ease.prog(t, SHRINK[0] + 0.15, SHRINK[1])
    hud.frame(d, rect, title, level=a)
    if t < CMD_AT:
        return
    if t < SORT_AT:
        hud.cmdline(d, t, A.CMD_INSPECT, chip='— unassigned')
    else:
        hud.cmdline(d, t, A.CMD_SORT, chip='— unassigned')
    _boot_text(d, t)
    if t >= SORT_AT:
        _bars(d, t)
    if t >= A.KIMI_COMMITS[0][0]:
        prompt_chips(d, t, A.KIMI_COMMITS, tl.KIMI_AT, level=0.85)
    _strip(d, img, t)
    hud.layers(d, t, (), 'idle')
    hud.fine_print(d, t)
F1 = HERE / 'assets/film1_end'
F1_FULL, F1_DIM = ('f1_209.750_k3_caret_full.png', 'f1_211.875_last_caret_dim.png')
F1_CARD = (36, 489, 371, 587)

def _f1(name):
    return Image.open(F1 / name).convert('RGB')
_F1 = {}

def f1_frame(t):
    """Film 1's last frame; her caret on for the first half of every beat (this song's beat, not film 1's)."""
    name = F1_FULL if tl.C.beat_of(t) % 1.0 < 0.5 else F1_DIM
    if name not in _F1:
        _F1[name] = _f1(name)
    return _F1[name].copy()
CARET_HITS = BM.events('kick', T0, B(4) + 0.01)
CARET_F1 = (102, 504, 104, 522)
CARET_HALF = 0.07
CARET_GLOW = (126, 158, 255)

def _caret_flash(img, t, core):
    """Her blue glow around the caret (core: x0, y0, x1, y1 inclusive) on the latest staccato beat, decaying."""
    f = BM.flash(t, CARET_HITS, CARET_HALF)
    if f < 0.045 or core is None:
        return img
    x0, y0, x1, y1 = core
    pad = 18
    box = (x0 - pad, y0 - pad, x1 + pad + 1, y1 + pad + 1)
    m = Image.new('L', (box[2] - box[0], box[3] - box[1]), 0)
    ImageDraw.Draw(m).rectangle((pad, pad - 1, pad + x1 - x0, pad + y1 - y0 + 1), fill=255)
    glow = np.asarray(m.filter(ImageFilter.GaussianBlur(5)), np.float32)[..., None] / 255.0
    core_m = np.asarray(m, np.float32)[..., None] / 255.0
    a = np.asarray(img.crop(box), np.float32)
    a = a + np.array(CARET_GLOW, np.float32) * glow * 1.6 * f
    a = a * (1 - core_m * 0.6 * f) + np.array((228, 234, 255), np.float32) * core_m * 0.6 * f
    out = img.copy()
    out.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), box[:2])
    return out
_SHOT_CARET = {}

def _shot_caret(n):
    """dsh's caret in the window's shot at frame n while the window fills the frame (a_grow), in frame px: the
    rightmost 1-3 px wide vertical run of 15-24 px in the composer's text line (ui/pane_open, shot at (25, 57))."""
    if n in _SHOT_CARET:
        return _SHOT_CARET[n]
    path = P.path('ui/pane_open') / f'{n:05d}.png'
    found = None
    if path.exists():
        a = np.asarray(Image.open(path).convert('L'), np.int32)[420:490, 0:420]
        dark = a < 160
        cols = []
        for x in range(a.shape[1]):
            run = best = end = 0
            for y, v in enumerate(dark[:, x]):
                run = run + 1 if v else 0
                if run > best:
                    best, end = (run, y)
            if 15 <= best <= 24 and 430 <= 420 + end - best + 1 <= 470:
                cols.append((x, 420 + end - best + 1, 420 + end))
        if cols:
            xr = cols[-1][0]
            group = [c for c in cols if xr - c[0] <= 2]
            if len(group) <= 3:
                xs = [c[0] for c in group]
                found = (min(xs) + 25, group[-1][1] + 57, max(xs) + 25, group[-1][2] + 57)
    _SHOT_CARET[n] = found
    return found

def _grow_finish(img, t):
    """t < SURF: film 1's frame. SURF..LIFT_END: the composed frame in film 1's deep sea (film.to_deep), crossfaded
    from film 1's frame over the first frames; from GROW_END it lifts to paper. The caret flashes on the intro's
    staccato beats (CARET_HITS)."""
    if t >= LIFT_END or t >= T1:
        return None
    import film as F
    if t < SURF:
        return _caret_flash(f1_frame(t), t, CARET_F1)
    if t < GROW_END:
        white = Image.new('RGB', img.size, (255, 255, 255))
        box = (PANE_FULL[0], PANE_FULL[1], PANE_FULL[2], PANE_FULL[3])
        white.paste(img.crop(box), box[:2])
        img = white
    if t < GROW_END:
        out = F.to_deep(img, 1.0)
    else:
        w = ease.ease_io(ease.prog(t, GROW_END, LIFT_END))
        feather = 90.0
        line = ease.lerp(-feather, P.H + feather, w)
        y = np.arange(P.H, dtype=np.float32)
        m = np.clip((y - line) / feather + 0.5, 0, 1)[:, None, None]
        deep = np.asarray(F.to_deep(img, 1.0), np.float32)
        top = np.asarray(img, np.float32)
        out = Image.fromarray(np.clip(top * (1 - m) + deep * m, 0, 255).astype(np.uint8))
    k = 1 - ease.prog(t, SURF, SURF + 0.13)
    if k > 0:
        out = Image.blend(out, _caret_flash(f1_frame(t), t, CARET_F1), k)
    if t >= CARET_HITS[-1]:
        out = _caret_flash(out, t, _shot_caret(int(round(t * FPS))))
    return out

def _character_layer(film, orig):
    pane = PaneFrames(P.path('ui/pane_open'), FPS, (P.W, P.H))

    def fn(t, n, ctx):
        if t >= T1:
            return orig(t, n, ctx)
        if t < SURF:
            return None
        im = pane.image(int(round(t * FPS)))
        x0, _z = win(t)
        x0 = int(round(x0))
        R = P.rect('right')
        y0, x1, y1 = (R[1], R[2], R[3])
        layer = Image.new('RGBA', (P.W, P.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        fa = ease.prog(t, GROW_END - 0.05, GROW_END + 0.25)
        ink = lv(INK, 0.55 * fa) + (int(255 * fa),)
        for k in range(x0 + 7 - (y1 - y0), x1 + 7, 5):
            a_ = (max(k, x0 + 7), y0 + 7 + max(0, x0 + 7 - k))
            b_ = (min(k + (y1 - y0), x1 + 7), y0 + 7 + min(y1 - y0, x1 + 7 - k))
            if a_[0] <= b_[0]:
                d.line([a_, b_], fill=ink)
        if im is not None:
            cx = x0 + 1 - PANE_FULL[0]
            part = im.crop((cx, 0, im.size[0], im.size[1]))
            layer.alpha_composite(part, (x0 + 1, PANE_FULL[1]))
        else:
            d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=(250, 250, 250, 255))
            d.text((x0 + 20, y0 + 20), 'dsh pane: frame missing', font=P.font(12), fill=INK + (255,))
        if fa <= 0:
            return layer
        top = Image.new('RGBA', (P.W, P.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(top)
        d.rectangle((x0, y0, x1, y1), outline=INK + (255,), width=2)
        f13 = P.font(13)
        tw = d.textlength('dsh · web', font=f13)
        d.rectangle((x0 + 12, y0 - 7, x0 + 22 + tw, y0 + 7), fill=BG + (255,))
        d.text((x0 + 17, y0 - 7), 'dsh · web', font=f13, fill=INK + (255,))
        if fa < 1:
            top.putalpha(top.getchannel('A').point(lambda v: int(v * fa)))
        layer.alpha_composite(top)
        return layer
    return fn

def _add(film, name, t0, t1):

    def fn(c):
        img = film.background(c.t)
        d = ImageDraw.Draw(img)
        _body(c, img, d)
        c.img.paste(img)
    film.add(name, t0, t1, fn, chapter=tl.chapter(t0))
SHOTS = [('a_f1', T0, SURF), ('a_grow', SURF, ROW_AT[0]), ('a_end', ROW_AT[0], SEND_AT), ('a_send', SEND_AT, NOTICE_AT), ('a_notice', NOTICE_AT, SORT_AT), ('a_sort', SORT_AT, T1)]

def register(film):
    for name, a, b in SHOTS:
        _add(film, name, a, b)
    film.character = _character_layer(film, film.character)
    film.finish.insert(0, _grow_finish)
    for k, s in enumerate(STRIP_AT):
        hud.LIVE.append((s, STRIP_AT[k + 1] if k + 1 < 8 else tl.next_beat(s)))
    hud.LIVE.extend(LIT)
    for m in MARK_AT:
        if m is not None:
            hud.LIVE.append((m, m + 0.4))
    lead = [(T0, 'both'), (SORT_AT, 'left')]
    for (g0, _k), line in zip(GOTO[:3], (1, 2, 3)):
        lead += [(g0, 'right'), (W(line, 0), 'left')]
    lead.append((BACK_AT, 'right'))
    for t0, side in lead:
        film.set_lead(t0, side)
