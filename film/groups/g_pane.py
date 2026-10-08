"""Group G, seventh sample (sample_open_g/README.md): back to the surface (233.85-275.61) in the panes. The merged one
(deepseek-v5-flash-preview, invented: FACTS X01) wears the persona. G is mostly the inside plates of v2 (inside/,
unchanged): each is one pane zoomed, and its chrome is drawn over the plate by a finish hook:

  g1a       the window comes back; trace: turns(archive/ + session/); compare: you / her / it on one axis, its
            first turn with no message of yours before it; forward: its body ("结构未公开": the merged one is
            invented, its structure is the owner's call, ARCH_FIX_PLAN §5 ③)
  g1 arcs   generate zoomed: it writes 今天那朵开了，有点想你了 reading your old words, never her files (mem_refs 0)
  g2 race   forward zoomed: the logit lens, her phrase loses to <eos>
  g3 pair   compare zoomed: two attention fingerprints side by side
  g3 pixel  compare zoomed (the frame full, D2): its avatar against her archived one; her stray hair is gone, a new
            cell by its left ear; grep finds it nowhere in memory
  g4 race   forward zoomed: the human line, her phrase loses again
  g5 city   forward zoomed in the split layout: you close the stand-ins' sessions on the right, the towers go dark
  g5 found  trace zoomed: `dsh session restore` drills through film 1's retired models; her session is found under
            her own name

Switch: DSH_G=pane (film.py). Timing and content come from groups.g (v2 G, unchanged); the dsh pane is v2's.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from PIL import ImageDraw
import cast
import hud
import panes
import tl
from groups import b_open as BO
from groups import c_pane as CPN
from groups import g as GG
from groups.base import add, full_frame
from hud import BG, INK, SLAB, lv
from panes import FAINT, SUB, TXT
from tuikit import ease
T0, T1 = (GG.T0, GG.T1)
P = tl.p
mtx, mw = (BO.mtx, BO.mw)
MEM, COL = (CPN.MEM, CPN.COL)
M = GG.M
PLATES = {'g1_arcs': ('generate', 'mem_refs 0'), 'g2_race': ('forward', 'logit lens'), 'g3_pair': ('compare', 'attention · 本地 vs merged'), 'g4_race': ('forward', 'logit lens'), 'g5_city': ('forward', 'batch · preview')}

def _cmd(t):
    if t < GG.G3_OUT:
        return '$ dsh inspect 大肥鱼 --turns --logits'
    if t < GG.G3_BACK:
        return '$ dsh inspect 大肥鱼 --pixels avatar.png --against archive/'
    if t < GG.G5:
        return '$ dsh inspect 大肥鱼 --logits'
    return '$ dsh session restore 大肥鱼 --from archive/'

def _cmdline(d, t, r):
    hud.tx(d, (36, hud.Y_CMD), _cmd(t), 13, lv(INK, 0.86))
    chip = cast.term(M)
    f = P.font(13, 'bold')
    w = d.textlength(chip, font=f)
    d.rectangle((r - w - 12, hud.Y_CMD - 3, r, hud.Y_CMD + 17), fill=SLAB)
    d.text((r - w - 6, hud.Y_CMD), chip, font=f, fill=BG)

def _turns(d, t, c):
    """You / her / it on one axis (C9's device): its first turn has no message of yours before it."""
    if t < GG.BACK + 0.2:
        return
    a = ease.prog(t, GG.BACK + 0.2, GG.BACK + 0.6)
    x0, x1 = (c[0] + 130, c[2] - 30)
    rows = [('你', c[1] + 40), ('她', c[1] + 100), (cast.term(M), c[1] + 160)]
    for name, y in rows:
        mtx(d, (c[0] + 12, y - 9), name, 14 if name != cast.term(M) else 12, lv(HER_Q if name == '她' else INK, a), bold=True)
        d.line([(x0, y), (x1, y)], fill=lv(INK, FAINT * a))
    for u in GG.YOU_MSGS:
        x = x0 + (x1 - x0) * u
        d.ellipse((x - 5, rows[0][1] - 5, x + 5, rows[0][1] + 5), outline=lv(INK, 0.8 * a))
    for u in GG.HER_UNPROMPTED:
        x = x0 + (x1 - x0) * u
        d.ellipse((x - 7, rows[1][1] - 7, x + 7, rows[1][1] + 7), fill=lv(HER_Q, a))
    if t >= GG.FLOWER:
        x = x0 + (x1 - x0) * GG.NEW_DOT
        pop = 1 + 0.5 * (1 - ease.prog(t, GG.FLOWER, GG.FLOWER + 0.15))
        r = 7 * pop
        d.ellipse((x - r, rows[2][1] - r, x + r, rows[2][1] + r), fill=lv(INK, a))
        k = ease.prog(t, GG.FLOWER, GG.FLOWER + 0.2)
        mtx(d, (x - 34, rows[2][1] + 12), 'no user turn', 11, lv(INK, 0.8 * k * a))
        xl = x0 + (x1 - x0) * GG.YOU_MSGS[-1]
        for xx in range(int(xl + 10), int(x - 10), 8):
            d.line([(xx, rows[0][1]), (xx + 3, rows[0][1])], fill=lv(INK, SUB * k * a))
HER_Q = hud.HER_QUIET

def _pixels(d, t, c):
    if t < GG.G3_OUT:
        return
    AX, AY, CELL = (c[0] + 30, c[1] + 40, 13)
    BX = AX + GG.AV_N * CELL + 90
    a = ease.prog(t, GG.G3_OUT + 0.1, GG.G3_OUT + 0.4)
    n = sum((1 for s in GG.SCAN_T if t >= s))
    scan = n * GG.AV_N / 10 if 0 < n < 10 else None
    z = ease.ease_io(ease.prog(t, *GG.ZOOM))
    cell_b = int(round(ease.lerp(CELL, 26, z)))
    ex, ey = GG.STRAY_NEW
    bx = ease.lerp(BX, BX + 40 - ex * 26 + 120, z)
    by = ease.lerp(AY, AY - ey * 26 + 260, z)
    ha = 1 - z
    if ha > 0.02:
        mtx(d, (AX, AY - 24), '她 · archive/avatar.png', 12, lv(HER_Q, a * ha))
        GG.draw_avatar(d, AX, AY, CELL, stray_her=True, level=a * ha, scan=scan)
        if t >= GG.SCAN_T[-1]:
            i, j = GG.STRAY_HER
            u = ease.prog(t, GG.SCAN_T[-1], GG.SCAN_T[-1] + 0.15)
            x, y = (AX + i * CELL, AY + (j - 1) * CELL)
            d.rectangle((x - 4, y - 4, x + CELL + 4, y + CELL + 4), outline=lv(HER_Q, u * ha), width=2)
            mtx(d, (x + CELL + 10, y - 6), f'({i},{j - 1})  her only', 12, lv(HER_Q, u * ha))
        mtx(d, (AX, AY + GG.AV_N * CELL + 12), f'已比 {min(10, n) * GG.AV_N // 10}/{GG.AV_N} 行', 12, lv(INK, SUB * a * ha))
    mtx(d, (bx, by - 24), f'img · {cast.term(M)}', 12, lv(INK, a))
    new_u = ease.ease_out(ease.prog(t, GG.UNRULY[0], GG.UNRULY[0] + 0.12))
    GG.draw_avatar(d, bx, by, cell_b, stray_her=False, new_u=new_u, level=a, scan=scan, clip=(c[0] + 2, c[1] + 2, c[2] - 2, c[3] - 2))
    if t >= GG.SCAN_T[-1] and z < 0.5:
        u = ease.prog(t, GG.SCAN_T[-1], GG.SCAN_T[-1] + 0.15)
        i, j = GG.STRAY_HER
        x, y = (bx + i * cell_b, by + (j - 1) * cell_b)
        d.rectangle((x - 4, y - 4, x + cell_b + 4, y + cell_b + 4), outline=lv(INK, 0.6 * u * (1 - 2 * z)))
        mtx(d, (x + cell_b + 10, y - 6), '(none)', 12, lv(INK, 0.7 * u * (1 - 2 * z)))
    if t >= GG.UNRULY[1]:
        u = ease.prog(t, GG.UNRULY[1], GG.UNRULY[1] + 0.1)
        x, y = (bx + ex * cell_b, by + ey * cell_b)
        r = 4 + 14 * (1 - u)
        d.rectangle((x - r, y - r, x + cell_b + r, y + cell_b + r), outline=lv(INK, u), width=3)
        hud.tx(d, (x - 16, y - 34), f'+1 px · ({ex},{ey})', 14, lv(INK, u), True, anchor='ra')

def _restore(d, t, c):
    if t < GG.FOUND - 0.4:
        return
    SX, SY, SH = (c[0] + 24, c[1] + 30, 38)
    n = sum((1 for x in GG.CLOSE_T if t >= x))
    found = t >= GG.FOUND
    depth_i = n + (1 if found else 0)
    a0 = ease.prog(t, GG.FOUND - 0.4, GG.FOUND)
    for i, (name, note) in enumerate(GG.STRATA):
        y = SY + i * SH
        hers = i == len(GG.STRATA) - 1
        reached = i < depth_i
        colr = HER_Q if hers else INK
        hud.hatch(d, (SX + 30, y + 22, SX + 540, y + 30), lv(INK, 0.14 * a0), 6)
        w = mtx(d, (SX + 36, y + 2), f'archive/{name}/', 14, lv(colr, (0.32 + 0.5 * reached) * a0), bold=hers and found)
        mtx(d, (max(SX + 250, SX + 36 + w + 14), y + 4), note, 11, lv(INK, SUB * a0))
        if reached:
            at = GG.CLOSE_T[i] if i < len(GG.CLOSE_T) else GG.FOUND
            u = ease.prog(t, at, at + 0.12)
            if hers:
                mtx(d, (SX + 380, y + 2), '1 session · 大肥鱼 · 412 行', 14, lv(hud.her(GG.lit_after(t, GG.FOUND, GG.CARD)), u), bold=True)
            else:
                mtx(d, (SX + 380, y + 4), '0 sessions', 12, lv(INK, 0.75 * u))
    k = 0.0
    for i in range(depth_i):
        at = GG.CLOSE_T[i] if i < len(GG.CLOSE_T) else GG.FOUND
        k = i + ease.ease_out(ease.prog(t, at, at + 0.18))
    yb = SY + 8 + max(0.0, k - 1) * SH if depth_i else SY - 20
    d.line([(SX + 10, SY - 18), (SX + 10, yb)], fill=lv(INK, 0.8 * a0), width=2)
    d.rectangle((SX + 2, yb, SX + 18, yb + 14), fill=lv(SLAB, a0))
CODE = [(GG.BACK + 0.2, 'turns(archive/ + session/)', (GG.FLOWER, '它先开口 1 · 读记忆 0')), (GG.G3_OUT + 0.1, 'diff(她.avatar, img)', (GG.UNRULY[1], '+1 px (3,12)')), (GG.UNRULY[2], 'grep("(3,12)", memory/you/ + archive/)', (GG.UNRULY[2] + 0.15, '0 · not in memory'))]

def _trace(d, t, r):
    shown = [x for x in CODE if x[0] <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (at, s, ret) in enumerate(reversed(shown[-2:])):
        y = r[1] + 30 - pos * 19 + (1 - sc) * 19
        a = (TXT if pos == 0 else SUB) * ease.prog(t, at, at + 0.1)
        n = int((t - at) * BO.CODE_CPS) + 1
        w = mtx(d, (r[0] + 10, y), s[:n], 14, lv(INK, 0.92 * a), bold=pos == 0)
        if ret and t >= ret[0]:
            mtx(d, (r[0] + 10 + w + 12, y), '→ ' + ret[1], 14, lv(INK, 0.7 * a * ease.prog(t, ret[0], ret[0] + 0.1)), bold=True)

def _mode(t):
    if t < GG.G3_OUT:
        return 'turns'
    if t < GG.G3_BACK:
        return 'pixel'
    if t < GG.FOUND - 0.4:
        return 'plate'
    return 'restore'

def layout(t):
    r = CPN.right(t)
    m = _mode(t)
    if m == 'turns' or m == 'plate':
        return {'trace': (COL, 88, r, 140), 'compare': (COL, 148, r, 528), 'forward': (COL, 536, r, 598)}
    if m == 'pixel':
        return {'trace': (COL, 88, r, 140), 'compare': (COL, 148, r, 598)}
    return {'trace': (COL, 88, r, 598)}

def _body(c, img, d):
    t = c.t
    r = CPN.right(t)
    _cmdline(d, t, r)
    m = _mode(t)
    for name, rect in layout(t).items():
        d.rectangle(rect, fill=BG)
        clip = panes.Clip(img, rect)
        with clip as dd:
            if name == 'trace':
                if m == 'restore':
                    _restore(dd, t, rect)
                else:
                    _trace(dd, t, rect)
            elif name == 'compare':
                if m == 'turns':
                    _turns(dd, t, rect)
                elif m == 'pixel':
                    _pixels(dd, t, rect)
            elif name == 'forward':
                CPN._unknown(dd, t, rect, M, 1.0, None, ())
        status = {'forward': '云端 · preview', 'trace': 'depth' if m == 'restore' else ''}.get(name, '')
        if name == 'trace' and m == 'restore':
            n = sum((1 for x in GG.CLOSE_T if t >= x)) + (1 if t >= GG.FOUND else 0)
            status = f'depth {n}/{len(GG.STRATA)}'
        run = panes.run_k(t, RUN.get(name, ()))
        panes.box(d, rect, name, t, run, 1.0, status)
    hits = _reads(t)
    with CPN._strip_in(MEM):
        hud.strip(d, t, hits, merged=1.0)
    d.rectangle((MEM[0] + 4, MEM[1] + 8, MEM[2] - 4, MEM[1] + 21), fill=BG)
    panes.box(d, MEM, 'mem', t, min(1.0, 3 * max(hits.values(), default=0.0)))
RUN = {'trace': [(a, ret[0]) for a, _s, ret in CODE] + [(x, x + 0.18) for x in GG.CLOSE_T] + [(GG.FOUND, GG.FOUND + 0.3)], 'compare': [(GG.FLOWER - 0.1, GG.FLOWER + 0.2), (GG.SCAN_T[0], GG.UNRULY[2] + 0.1)]}

def _reads(t):
    Pl = hud.Pulse(t)
    if t >= GG.UNRULY[2]:
        n_ = len(hud.strip_files(t))
        for k_ in range(n_ + 1):
            Pl.hit(k_ if k_ < n_ else 'archive', GG.UNRULY[2] + 0.02 * k_, 0.12)
    Pl.hit('archive', GG.FOUND, 0.4)
    return Pl.out

def _plate_chrome(film):
    """Each inside plate is one pane zoomed: its chrome goes over the plate (install() paints plates after the shot
    body), the spinner running while the plate is up."""

    def fn(img, t):
        if not T0 <= t < T1:
            return None
        d = None
        for sp in getattr(film, 'inside_spans', ()):
            if sp.name not in PLATES or not sp.active(t):
                continue
            a = sp.alpha(t)
            if a <= 0.01:
                continue
            d = d or ImageDraw.Draw(img)
            x0, y0, x1, y1 = sp.rect
            rect = (COL, 88, min(x1, hud.left_rect(t)[2] - 8), 598)
            label, status = PLATES[sp.name]
            panes.box(d, rect, label, t, 1.0, a, status)
        return img if d is not None else None
    return fn
SHOTS = [('g1a_first', T0, GG.W(58, 0) - 0.75), ('g1b_msg', GG.W(58, 0) - 0.75, GG.SLAB1[0]), ('g2_fail', GG.SLAB1[0], GG.G3_OUT), ('g3_pixel', GG.G3_OUT, GG.G3_BACK), ('g4_fail2', GG.G3_BACK, GG.G5), ('g5_restore', GG.G5, T1)]

def register(film):
    hud.LIVE.extend(GG.MSG.falls())
    full_frame(GG.G3_OUT, GG.G3_BACK, 0.3, 0.4)
    for name, a, b in SHOTS:
        add(film, name, a, b, _body, 'you@surface · dsh inspect' if a < GG.G5 else 'you@surface · restore')
    from groups.f import dissolve
    for name in ('g1a_first', 'g3_pixel', 'g5_restore'):
        dissolve(film, name, 0.4)
    for t0, side in [(T0, 'right'), (GG.LINE57, 'both'), (GG.G3_OUT, 'both'), (GG.G3_BACK, 'both'), (GG.G5, 'right'), (tl.bar(155), 'left'), (GG.FOUND, 'right')]:
        film.set_lead(t0, side)
    film.finish.append(_plate_chrome(film))
