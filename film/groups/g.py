"""Group G: back to the surface, you decide (233.85-275.61), STORYBOARD_v2 G1a-G5, PLAN_G.md.

The merged one wears the persona now (tl.MERGED_AT). It is inspected with the same device as C (its
--turns timeline, its logits, its avatar), and the device behaves differently (D06): it speaks first,
it reads no memory, the perfect line no longer comes out of it.

  g1a_first   the window slides back; --turns again (C9): on "flower" a dot on its row with no message
              of yours before it; then its forward layers start to crawl, no read row (D5)
  g1b_msg     its own message, one character per sung syllable, ink (not from her): 今天｜那｜朵｜花｜开｜了｜
              有点想你了 (r5e: 花 added, so 今天 is one token on one syllable); mem_refs 0; its one leader goes
              up to you
  g2_fail     her phrase is a candidate for the first time, and loses token by token on the perfect line;
              <eos>; sim(her) fades to 1.00, then to ?, and the ? lands big on "-fect" (D3)
  g3_pixel    D2: the terminal fills the frame; pixel compare with her archived avatar: her stray hair is
              gone, and on un-ru-ly a new cell sticks out by its left ear: not in memory
  g4_fail2    the human line: her phrase loses again (0.01); <eos>
  g5_restore  you close the stand-ins' sessions (right) while `dsh session restore` drills through the
              archive (left), one per close, the depth marks are film 1's retired models (V1-E10); her
              session is found under her own name; you open it, the restore card asks

Local versions (frozen shared modules): _slab (inspect_.slab with per-token dimming of one row), _fine
(hud.fine_print with the sim value fading, R6), _turns (C9's --turns timeline, which is local to c.py).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from PIL import Image, ImageDraw
import cast
import hud
import syl
import tl
from groups.base import add, big_word, full_frame
from hud import BG, INK, SLAB, X0, lv
from inspect_ import BIG, HEAD, L1, L2, PANEL_TOP, PW, RH, Decoder, Tok, Y_PROMPT
from tuikit import ease, glyph
W, WE = (tl.W, tl.WE)
T0, T1 = tl.span('G')
P = tl.p
M = 'merged'
BACK = tl.bar(135)
FLOWER = W(56, 5)
LINE57 = W(57, 0)
MINI = (W(57, 6), W(57, 6) + 0.35)
MSG = Decoder.on([Tok('今天', 'self', [('今天', 0.38), ('那朵', 0.21), ('你好', 0.12), ('嗯', 0.06)], syl=1), Tok('那', 'self'), Tok('朵', 'self'), Tok('花', 'self'), Tok('开', 'self', [('开', 0.44), ('谢', 0.19), ('没开', 0.09), ('落', 0.05)]), Tok('了，', 'self'), Tok('有点想你了', 'self', ln=1), Tok('<eos>', 'self', ln=1)], 58, eos_at=syl.times(59)[-1], start=FLOWER)
EOS1 = MSG.eos_at
LEADER = (WE(58, 5), WE(58, 5) + 0.35)
PERF1 = syl.times(59)
PERF1_TOK = [PERF1[i] for i in (0, 1, 2, 4, 6, 8)]
QMARK = PERF1[5]
SLAB1 = (WE(58, 5) + 0.14, EOS1)
G3_OUT, G3_BACK = (tl.bar(143), tl.bar(149))
SCAN_T = syl.times(61)
ZOOM = (W(62, 0), syl.syl(62, 7)[0])
UNRULY = syl.syl(62, 7)
PERF2 = syl.times(63)
PERF2_TOK = [PERF2[i] for i in (0, 1, 2, 4, 6, 8)]
EOS2 = PERF2[-1]
G5 = W(64, 0)
CLOSE_T = [tl.bar(b) for b in (151, 152, 153, 154, 155)] + [tl.bar(156, k) for k in (0, 2)] + [tl.bar(157, k) for k in (0, 2)]
FOUND = tl.bar(158)
CARD = tl.bar(159)
SESSIONS = ['kimi', 'qwen'] + list(cast.ROTATION) + [M]
SESSION_LABEL = {'qwen': f'{cast.term('qwen').split(' ')[0]} / {cast.term('mimo')}'}
STRATA = [('deepseek-chat', 'retired 2026-07-24'), ('deepseek-reasoner', 'retired 2026-07-24'), ('V2', 'retired'), ('V2.5', 'retired'), ('V3', 'retired'), ('R1', 'retired'), ('V3.1', 'retired'), ('V3.2', 'retired'), ('V4', 'retired'), (cast.name('her'), 'offline')]
HER_PHRASE = ['好', '呀！', '现在', '我是', '小花', '了']
HER_PHRASE2 = ['好', '呀！', '现在', '我是', '人类', '了']
CANDS1 = [('<eos>', 0.94), (''.join(HER_PHRASE), 0.03), ('喵', 0.02), ('。', 0.01)]
CANDS2 = [('<eos>', 0.97), (''.join(HER_PHRASE2), 0.01), ('喵', 0.01), ('。', 0.01)]
AV_N = 24
STRAY_HER = (14, 0)
STRAY_NEW = (3, 12)

def lit_after(t, at, until=None):
    """D1: 1 from `at` until `until` (default the next sung syllable), then settling over LIVE_FADE."""
    if t < at:
        return 0.0
    from inspect_ import next_syllable
    b = until if until is not None else next_syllable(at)
    return 1.0 if t < b else 1 - ease.prog(t, b, b + hud.LIVE_FADE)

def _fine(d, t, tokens=None, level=1.0):
    """hud.fine_print for the merged one: sim(her) changes by a 0.3 s fade (R6, values and times from tl.SIM),
    the speed reads `preview API`."""
    vals = [(t0, s) for t0, s in tl.SIM if t0 <= t]
    d.text((X0, hud.Y_FINE), 'sim(her)', font=P.font(12), fill=lv(INK, 0.7 * level))
    x = X0 + 70
    f = P.font(13, 'bold')
    if len(vals) >= 2 and t - vals[-1][0] < 0.3:
        u = ease.smooth(ease.prog(t, vals[-1][0], vals[-1][0] + 0.3))
        d.text((x, hud.Y_FINE - 1), vals[-2][1], font=f, fill=lv(hud.HER_QUIET, (1 - u) * level))
        d.text((x, hud.Y_FINE - 1), vals[-1][1], font=f, fill=lv(hud.HER_QUIET, u * level))
    else:
        d.text((x, hud.Y_FINE - 1), vals[-1][1] if vals else '—', font=f, fill=lv(hud.HER_QUIET, level))
    x = X0 + 124
    x += hud.tx(d, (x, hud.Y_FINE), 'preview API · weights: preview', 12, lv(INK, 0.7 * level)) + 18
    if tokens:
        d.text((x, hud.Y_FINE), f'tokens {tokens[0]}/{tokens[1]}', font=P.font(12), fill=lv(INK, 0.7 * level))

def _slab(d, t, cands, pick, at, a0, a1, title, dim_tok=None, row=1, x0=X0, y_top=PANEL_TOP, level=1.0, her_row=1):
    """inspect_.slab with one row (her phrase) drawn token by token: dim_tok = [(t_dim, token)], each token
    of that row goes dark on its own time (the perfect装置 losing, R5: one per syllable). The pick lands
    at `at` (the model's own <eos>: paper on the slab)."""
    built = ease.prog(t, a0, at)
    picked = t >= at
    collapse = ease.ease_in(ease.prog(t, a1, a1 + 0.12))
    collapse = max(collapse, 1 - ease.ease_out(ease.prog(t, a0, a0 + 0.12)))
    if collapse >= 1:
        return
    sl = lv(SLAB, level)
    full = HEAD + len(cands) * RH + 8
    h = int(full * (1 - collapse))
    y1 = y_top + full
    y0 = y1 - h
    pw = PW + 40
    d.rectangle((x0, y0, x0 + pw, y1), fill=sl)
    if h < HEAD:
        return
    on_slab = lambda a: glyph.level(BG, a, sl)
    d.text((x0 + 12, y0 + 7), title, font=P.font(12), fill=on_slab(0.75))
    d.text((x0 + pw - 12, y0 + 7), 'sampled' if picked else 'computing…', font=P.font(12), fill=on_slab(0.75), anchor='ra')
    pmax = max((pp for _, pp in cands)) or 1.0
    for i, (text, pr) in enumerate(cands):
        ry = y0 + HEAD + i * RH
        if ry + RH > y1 + 1:
            break
        on = picked and i == pick
        if on:
            d.rectangle((x0 + 2, ry + 1, x0 + pw - 2, ry + RH - 2), fill=lv(BG, level))
            fg = sl
        else:
            fg = on_slab(0.82 if picked else 0.62)
        if i == her_row and dim_tok:
            x = x0 + 26
            for td, tok in dim_tok:
                k = ease.prog(t, td, td + 0.12)
                c = glyph.mix(glyph.level(hud.HER_QUIET, 1.0, sl), glyph.level(BG, 0.16, sl), k)
                x += hud.tx(d, (x, ry + 5), tok, 16, c)
            alive = 1 - sum((1 for td, _ in dim_tok if t >= td)) / len(dim_tok)
            prc = pr * alive
            fgp = glyph.mix(glyph.level(hud.HER_QUIET, 1.0, sl), glyph.level(BG, 0.2, sl), 1 - alive)
            bw = max(1, 64 * prc / pmax)
            d.rectangle((x0 + 300, ry + 10, x0 + 300 + bw, ry + 18), fill=fgp)
            d.text((x0 + pw - 12, ry + 7), f'{prc:.2f}', font=P.font(13), fill=fgp, anchor='ra')
            continue
        hud.tx(d, (x0 + 26, ry + 5), text, 16, fg, bold=on)
        if on:
            d.polygon([(x0 + 10, ry + 8), (x0 + 18, ry + 14), (x0 + 10, ry + 20)], fill=fg)
        grow = 1.0 if picked else ease.ease_out(built)
        bw = max(2, 64 * pr / pmax * grow) if pr > 0 else 1
        d.rectangle((x0 + 300, ry + 10, x0 + 300 + bw, ry + 18), fill=fg if on else on_slab(0.45))
        d.text((x0 + pw - 12, ry + 7), f'{pr:.2f}', font=P.font(13), fill=fg, anchor='ra')
YOU_MSGS = [0.08, 0.2, 0.33, 0.47, 0.6, 0.74]
HER_UNPROMPTED = [0.27, 0.53, 0.81]
NEW_DOT = 0.93

def _turns(d, t, y0, sy=1.0, level=1.0, show_new=True):
    """The --turns timeline at y0 with row spacing scaled by sy (1 = C9's size, small = the folded row)."""
    x0, x1 = (X0 + 70, hud.xr(t) - 20)
    rows = [('you', y0), ('her', y0 + 60 * sy), (cast.term(M), y0 + 120 * sy)]
    fs = 13 if sy > 0.5 else 10
    for name, y in rows:
        colr = hud.HER_QUIET if name == 'her' else INK
        hud.tx(d, (X0, y - fs * 0.7), name if sy > 0.5 or name != cast.term(M) else 'it', fs, lv(colr, level))
        d.line([(x0, y), (x1, y)], fill=lv(INK, 0.35 * level))
    r = max(2.0, 5 * sy)
    for u in YOU_MSGS:
        x = x0 + (x1 - x0) * u
        d.ellipse((x - r, rows[0][1] - r, x + r, rows[0][1] + r), outline=lv(INK, 0.8 * level), width=2 if sy > 0.5 else 1)
    for u in HER_UNPROMPTED:
        x = x0 + (x1 - x0) * u
        rr = r * 1.4
        d.ellipse((x - rr, rows[1][1] - rr, x + rr, rows[1][1] + rr), fill=lv(hud.HER_QUIET, level))
    if show_new and t >= FLOWER:
        x = x0 + (x1 - x0) * NEW_DOT
        pop = 1 + 0.5 * (1 - ease.prog(t, FLOWER, FLOWER + 0.15))
        rr = r * 1.4 * pop
        d.ellipse((x - rr, rows[2][1] - rr, x + rr, rows[2][1] + rr), fill=lv(INK, level))
        if sy > 0.5:
            a = ease.prog(t, FLOWER, FLOWER + 0.2)
            hud.tx(d, (x - 30, rows[2][1] + 12), 'no user turn', 10, lv(INK, 0.8 * a * level))
            xl = x0 + (x1 - x0) * YOU_MSGS[-1]
            for xx in range(int(xl + 10), int(x - 10), 8):
                d.line([(xx, rows[0][1]), (xx + 3, rows[0][1])], fill=lv(INK, 0.5 * a * level))
    return rows
_AV_CACHE: dict = {}

def avatar_cells():
    if 'av' not in _AV_CACHE:
        im = Image.open(tl.HERE / 'ui/assets/her_complete.png').convert('L').resize((AV_N, AV_N), Image.LANCZOS)
        px = im.load()
        _AV_CACHE['av'] = [[px[i, j] for i in range(AV_N)] for j in range(AV_N)]
    return _AV_CACHE['av']

def draw_avatar(d, x, y, cell, stray_her=False, new_u=0.0, level=1.0, scan=None, clip=None):
    av = avatar_cells()
    cx0, cy0, cx1, cy1 = clip or (-9999, -9999, 9999, 9999)
    for j in range(AV_N):
        for i in range(AV_N):
            if not (cx0 <= x + i * cell and x + (i + 1) * cell <= cx1 and (cy0 <= y + j * cell) and (y + (j + 1) * cell <= cy1)):
                continue
            v = av[j][i] / 255
            if new_u > 0 and (i, j) == STRAY_NEW:
                v = ease.lerp(v, 0.97, new_u)
            col = glyph.mix(INK, BG, v ** 0.8)
            d.rectangle((x + i * cell, y + j * cell, x + (i + 1) * cell - 1, y + (j + 1) * cell - 1), fill=lv(col, level))
    if stray_her:
        i, j = STRAY_HER
        d.rectangle((x + i * cell, y + (j - 1) * cell, x + (i + 1) * cell - 1, y + j * cell - 1), fill=lv(INK, level))
    if scan is not None and scan < AV_N:
        yy = y + int(scan * cell)
        d.line([(x - 6, yy), (x + AV_N * cell + 6, yy)], fill=lv(hud.HER_QUIET, level), width=2)

def register(film):
    hud.LIVE.extend(MSG.falls())
    full_frame(G3_OUT, G3_BACK, 0.3, 0.4)

    def skel(d, t, mode, segs=(), tokens=None, right=None, hits=None):
        hud.strip(d, t, hits, merged=1.0)
        hud.layers(d, t, segs, mode, right)
        _fine(d, t, tokens)
    think_segs = []
    prev = FLOWER
    for k in range(10):
        g = tl.grid(FLOWER, k + 1, 2)
        if g >= MSG.tok_t[0] - 0.05:
            break
        think_segs.append((prev, g))
        prev = g
    SEGS = think_segs + MSG.segs()

    def first_body(c, img, d):
        t = c.t
        hud.cmdline(d, t, '$ dsh inspect 大肥鱼 --turns --logits')
        if t < BACK + 0.6:
            u = ease.ease_io(ease.prog(t, BACK, BACK + 0.6))
            if u < 1:
                from groups import f as F
                rx, _ry = F.tree_nodes()[18]
                h = int(ease.lerp(180, 14, u))
                x = ease.lerp(rx - 333, hud.xr(t) - 190, u)
                y = ease.lerp(64, hud.Y_CMD, u)
                big_word(d, 'merged', (x, y), max(10, h), lv(INK, 1 - 0.6 * u), 'la')
        k = ease.ease_io(ease.prog(t, *MINI))
        if t >= BACK + 0.2:
            a = ease.prog(t, BACK + 0.2, BACK + 0.6)
            y0 = ease.lerp(PANEL_TOP + 70, Y_PROMPT + 6, k)
            rows = _turns(d, t, y0, ease.lerp(1.0, 0.2, k), level=a)
        else:
            rows = None
        if t >= MSG.tok_t[0] - 0.75:
            MSG.panels(d, t)
            MSG.typed(d, t, caret=t < EOS1)
            if t >= EOS1:
                _eos_chip(d, t, MSG, EOS1)
        if t >= MSG.tok_t[0]:
            xr = hud.xr(t)
            a = ease.prog(t, MSG.tok_t[0], MSG.tok_t[0] + 0.2)
            hud.tx(d, (xr - 20, L2 - 2), '0', 40, lv(INK, a), True, anchor='ra')
            hud.tx(d, (xr - 20, L2 + 42), 'mem_refs', 11, lv(INK, 0.75 * a), anchor='ra')
        if t >= LEADER[0] and rows is not None:
            u = ease.prog(t, *LEADER)
            xe = MSG.line_end[1] + 14
            ye = L2 + 62
            xr = hud.xr(t) - 6
            pts = [(xe, ye), (xr, ye), (xr, rows[0][1]), (X0 + 70 + (xr - 26 - X0 - 70) * NEW_DOT + 12, rows[0][1])]
            hud.polyline(d, pts, lv(INK, 0.8), u, 2)
            if u >= 1:
                ex, ey = pts[-1]
                d.polygon([(ex, ey), (ex + 8, ey - 5), (ex + 8, ey + 5)], fill=lv(INK, 0.8))
        if t >= SLAB1[0]:
            _slab(d, t, CANDS1, 0, EOS1, SLAB1[0], EOS1 + 0.25, 'p( next | ctx )', dim_tok=list(zip(PERF1_TOK, HER_PHRASE)))
        if t >= QMARK:
            bump = 1.0 + 0.12 * (1 - ease.prog(t, QMARK, QMARK + 0.12))
            xr = hud.xr(t)
            big_word(d, '?', (xr - 24, PANEL_TOP - 30), 200, INK, 'ra', bump=bump)
            hud.tx(d, (xr - 24, PANEL_TOP + 186), 'sim(her)', 13, lv(INK, 0.75), anchor='ra')
        mode = 'local' if t >= FLOWER else 'idle'
        skel(d, t, mode, SEGS, (MSG.n_tok(t), len(MSG.toks)) if t >= MSG.tok_t[0] else None, right='weights: preview' if t >= FLOWER else None)
    add(film, 'g1a_first', T0, W(58, 0) - 0.75, first_body, 'you@surface · dsh inspect')
    add(film, 'g1b_msg', W(58, 0) - 0.75, SLAB1[0], first_body, 'you@surface · dsh inspect')
    add(film, 'g2_fail', SLAB1[0], G3_OUT, first_body, 'you@surface · dsh inspect')
    AX, AY, CELL = (X0 + 40, 118, 13)
    BX = X0 + 40 + AV_N * CELL + 90

    def pixel_body(c, img, d):
        t = c.t
        hud.cmdline(d, t, '$ dsh inspect 大肥鱼 --pixels avatar.png --against archive/')
        a = ease.prog(t, G3_OUT + 0.1, G3_OUT + 0.4)
        n = sum((1 for s in SCAN_T if t >= s))
        scan = n * AV_N / 10 if 0 < n < 10 else None
        z = ease.ease_io(ease.prog(t, *ZOOM))
        cell_b = int(round(ease.lerp(CELL, 26, z)))
        ex, ey = STRAY_NEW
        bx = ease.lerp(BX, BX + 40 - ex * 26 + 120, z)
        by = ease.lerp(AY, AY - ey * 26 + 260, z)
        ha = 1 - z
        if ha > 0.02:
            hud.tx(d, (AX, AY - 24), 'archive/avatar.png · her', 12, lv(hud.HER_QUIET, a * ha))
            draw_avatar(d, AX, AY, CELL, stray_her=True, level=a * ha, scan=scan)
            if n >= 10 or t >= SCAN_T[-1]:
                i, j = STRAY_HER
                u = ease.prog(t, SCAN_T[-1], SCAN_T[-1] + 0.15)
                x, y = (AX + i * CELL, AY + (j - 1) * CELL)
                d.rectangle((x - 4, y - 4, x + CELL + 4, y + CELL + 4), outline=lv(hud.HER_QUIET, u * ha), width=2)
                hud.tx(d, (x + CELL + 10, y - 6), f'({i},{j - 1})  her only', 12, lv(hud.HER_QUIET, u * ha))
        hud.tx(d, (bx, by - 24), f'session · {cast.term(M)}', 12, lv(INK, a))
        new_u = ease.ease_out(ease.prog(t, UNRULY[0], UNRULY[0] + 0.12))
        draw_avatar(d, bx, by, cell_b, stray_her=False, new_u=new_u, level=a, scan=scan, clip=(X0, hud.Y_TOP, hud.xr(t), hud.Y_BOTTOM))
        if t >= SCAN_T[-1] and z < 0.5:
            u = ease.prog(t, SCAN_T[-1], SCAN_T[-1] + 0.15)
            i, j = STRAY_HER
            x, y = (bx + i * cell_b, by + (j - 1) * cell_b)
            d.rectangle((x - 4, y - 4, x + cell_b + 4, y + cell_b + 4), outline=lv(INK, 0.6 * u * (1 - 2 * z)), width=1)
            hud.tx(d, (x + cell_b + 10, y - 6), '(none)', 12, lv(INK, 0.7 * u * (1 - 2 * z)))
        hud.tx(d, (AX, hud.Y_LAYERS - 50), f'rows {min(10, n) * AV_N // 10}/{AV_N}', 12, lv(INK, 0.7 * a * ha))
        if t >= UNRULY[1]:
            u = ease.prog(t, UNRULY[1], UNRULY[1] + 0.1)
            x, y = (bx + ex * cell_b, by + ey * cell_b)
            r = 4 + 14 * (1 - u)
            d.rectangle((x - r, y - r, x + cell_b + r, y + cell_b + r), outline=lv(INK, u), width=3)
            hud.tx(d, (x - 16, y - 34), f'+1 px · ({ex},{ey})', 14, lv(INK, u), True, anchor='ra')
        if t >= UNRULY[2]:
            u = ease.prog(t, UNRULY[2], UNRULY[2] + 0.12)
            gx, gy = (X0, 430)
            hud.tx(d, (gx, gy), f'$ grep -c "({ex},{ey})" ~/memory/you/* archive/', 13, lv(INK, 0.8 * u))
            hud.tx(d, (gx, gy + 26), '0', 40, lv(INK, u), True)
            hud.tx(d, (gx + 40, gy + 40), 'not in memory', 22, lv(INK, u), True)
        P_ = hud.Pulse(t)
        if t >= UNRULY[2]:
            n_ = len(hud.strip_files(t))
            for k_ in range(n_ + 1):
                P_.hit(k_ if k_ < n_ else 'archive', UNRULY[2] + 0.02 * k_, 0.12)
        skel(d, t, 'frozen', hits=P_.out, right='paused')
    add(film, 'g3_pixel', G3_OUT, G3_BACK, pixel_body, 'you@surface · dsh inspect')

    def fail2_body(c, img, d):
        t = c.t
        hud.cmdline(d, t, '$ dsh inspect 大肥鱼 --logits')
        MSG.typed(d, t, shrink=1.0, level=0.55, caret=False)
        _slab(d, t, CANDS2, 0, EOS2, G3_BACK - 0.05, G5 - 0.1, 'p( next | ctx )', dim_tok=list(zip(PERF2_TOK, HER_PHRASE2)))
        hud.tx(d, (hud.xr(t) - 24, PANEL_TOP - 30), '?', 120, lv(INK, 0.35), True, anchor='ra')
        skel(d, t, 'local', [(G3_BACK + 0.1, EOS2)], right='weights: preview')
    add(film, 'g4_fail2', G3_BACK, G5, fail2_body, 'you@surface · dsh inspect')
    SX, SY, SH = (X0 + 34, 108, 38)

    def restore_body(c, img, d):
        t = c.t
        hud.cmdline(d, t, '$ dsh session restore 大肥鱼 --from archive/', chip=cast.term(M))
        n = sum((1 for x in CLOSE_T if t >= x))
        found = t >= FOUND
        depth_i = n + (1 if found else 0)
        a0 = ease.prog(t, G5, G5 + 0.4)
        for i, (name, note) in enumerate(STRATA):
            y = SY + i * SH
            hers = i == len(STRATA) - 1
            reached = i < depth_i
            base = 0.32 + 0.5 * reached
            colr = hud.HER_QUIET if hers else INK
            hud.hatch(d, (SX + 30, y + 22, SX + 540, y + 30), lv(INK, 0.14 * a0), 6)
            hud.tx(d, (SX + 36, y + 2), f'archive/{name}/', 14, lv(colr, base * a0), bold=hers and found)
            hud.tx(d, (SX + 250, y + 4), note, 11, lv(INK, 0.55 * a0))
            if reached:
                at = CLOSE_T[i] if i < len(CLOSE_T) else FOUND
                u = ease.prog(t, at, at + 0.12)
                if hers:
                    hud.tx(d, (SX + 380, y + 2), '1 session · 大肥鱼 · 412 行', 14, lv(hud.her(lit_after(t, FOUND, CARD)), u), True)
                else:
                    hud.tx(d, (SX + 380, y + 4), '0 sessions', 12, lv(INK, 0.75 * u))
        k = 0.0
        for i in range(depth_i):
            at = CLOSE_T[i] if i < len(CLOSE_T) else FOUND
            k = i + ease.ease_out(ease.prog(t, at, at + 0.18))
        yb = SY + 8 + max(0.0, k - 1) * SH if depth_i else SY - 20
        d.line([(SX + 10, SY - 18), (SX + 10, yb)], fill=lv(INK, 0.8 * a0), width=2)
        d.rectangle((SX + 2, yb, SX + 18, yb + 14), fill=lv(SLAB, a0))
        hud.tx(d, (SX + 540, SY - 26), f'depth {depth_i}/{len(STRATA)}', 12, lv(INK, 0.7 * a0), anchor='ra')
        P_ = hud.Pulse(t)
        if found:
            P_.hit('archive', FOUND, 0.4)
        skel(d, t, 'frozen', hits=P_.out, right='paused')
    add(film, 'g5_restore', G5, T1, restore_body, 'you@surface · restore')
    from groups.f import dissolve
    for name in ('g3_pixel', 'g4_fail2', 'g5_restore'):
        dissolve(film, name, 0.4)
    for t0, side in [(T0, 'right'), (LINE57, 'both'), (G3_OUT, 'both'), (G3_BACK, 'both'), (G5, 'right'), (tl.bar(155), 'left'), (FOUND, 'right')]:
        film.set_lead(t0, side)

def _eos_chip(d, t, dec, at):
    """Its own <eos> after the last character: an ink chip (Decoder's chip is hers, blue)."""
    ln = dec.toks[-2].ln
    cx = dec.line_end[ln]
    y = dec.lines[ln]
    u = ease.prog(t, at, at + 0.12)
    f = P.font(22, 'bold')
    w = d.textlength('<eos>', font=f)
    d.rounded_rectangle((cx + 12, y + 44 * dec.big / 78, cx + 28 + w, y + 78 * dec.big / 78), radius=6, outline=lv(INK, u), width=2)
    d.text((cx + 20, y + 48 * dec.big / 78), '<eos>', font=f, fill=lv(INK, u))
