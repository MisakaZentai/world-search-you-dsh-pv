"""Group B: 甲 Kimi K3 (40.86-82.95), STORYBOARD_v2 B1-B9. Plan and timing table: PLAN_B.md.

D21: the header tag `tempo: Allegro` (EGGS N19) is drawn by film.py while Kimi wears the persona.

The left is `grep` / `diff` against her archive: a cloud model is seen from the outside only (its answers
arrive in chunks, a chunk on a sung word; logprobs are approximate; the forward layers stay grey,
"weights: closed", R11).

  b1_kimi     you send (D5: the model changes); her files read on the 16ths; 记得！ lands on "table" (its panel
              holds Kimi's own voice, X17); first_hello's atime jumps to 刚刚
  b2_table    it answers in a table (its habit): a cell per syllable, each cell grepped in her archive
  b3_wobble   her own table from the archive, one leg short, rocking on the beat; your red pen (X02, X09)
  b4_perfect  the perfect template, chunk by chunk, her chunks blue; 0.97 slams on "perfect" (D3)
  b5_ask      you ask for her eggplant (IME), sent on "eggplant"
  b6_grep     grep finds her line; a segment per syllable
  b7_redpen   its first revision: a red stroke per syllable through her quirks
  b8_diff     it recites her line chunk by chunk, all hers, minus 一根; it writes eggplant_2 (89 %)
  b9_near     (D2: the terminal fills the frame) its 24 chunks around her, one ring tighter per bar: no hit;
              82.13 the local Qwen is picked (R9 cut, D5)
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import random
from PIL import ImageDraw
import cast
import hud
import syl
import tl
from groups import a as A
from groups.base import big_word, full_frame
from hud import BG, ERR, HER_QUIET, INK, SLAB, X0, lv
from inspect_ import BIG, L1, L2, Y_CONTEXT, Decoder, Tok, prompt_chips
from tuikit import ease
W, B = (tl.W, tl.B)
T0, T1 = tl.span('B')
P = tl.p
CMD = '$ dsh inspect 大肥鱼 --diff archive/'
CMD_NEAR = '$ dsh inspect 大肥鱼 --near archive/her --k 24'
CMD_QWEN = '$ dsh inspect 大肥鱼 --logits --attn'
SEND1 = tl.KIMI_AT
ASK1, COMMITS1 = (A.KIMI_ASK, A.KIMI_COMMITS)
READ1 = SEND1 + 0.2
REMEMBER_AT = W(4, 5)
SHRINK1 = tl.at_beat(W(5, 0), -1)
REMEMBER = Decoder.on([Tok('记得！', 'first_hello', [('记得！', 0.41), (cast.CAST['kimi']['meme'], 0.33), ('当然可以～', 0.12), ('好的', 0.06)], syl=1)], at=[REMEMBER_AT], chunk=True, start=SEND1 + 0.3, title='p( next | ctx )  ·  logprobs ≈', hold=SHRINK1)
KIMI_TABLE = [['项目', '规格', '备注'], ['桌面', '圆的', '喵～'], ['桌腿', '四条', '一样长']]
CELL_AT = syl.times(5)
HITS = {'喵～': 312}
HER_TABLE = [['早', '午', '晚'], ['包子', '拉面', '寿司'], ['豆浆', '奶茶', None]]
FIX = '汤'
L6 = syl.times(6)
HER_TABLE_AT, CIRCLE_AT, FIXED_AT = (L6[0], L6[4], L6[7])
L7 = syl.times(7)
CLEAR4 = tl.at_beat(W(7, 0), -1)
PERFECT_AT = L7[4]
PERFECT_TABLE = Decoder.on([Tok('好', 'archive', syl=1), Tok('呀！现在', 'archive', syl=3), Tok('我是', 'archive', syl=1, ln=1), Tok('桌子', 'self', syl=1, ln=1), Tok('了', 'archive', ln=1), Tok('哦', 'self', ln=1)], at=L7[:4] + L7[6:], chunk=True, start=W(7, 0) - 0.3, big=70, lines=(364, 448))
REPLY1 = '记得！'
TEMPLATE1 = '好呀！现在我是桌子了哦'
SIM_BIG = '0.97'
SHRINK4 = W(8, 0)
EGG_ASK = '你能变成一根茄子吗？'
EGG_COMMITS = syl.ime(W(8, 1), ['你能变成', '一根茄子', '吗？'], step=2)
SEND2 = W(8, 5)
READ2 = SEND2 + 0.2
L9 = syl.times(9)
GREP_AT = L9[0]
HER_EGG = '好呀！现在我是一根茄子了🍆'
SEGS = [('好呀！', 0), ('现在', 0), ('我是', 0), ('一根', 1), ('茄子了', 1), ('🍆', 1)]
L10 = syl.times(10)
RAW = [('好呀', None), ('好呀', 0), ('！', None), ('！', 1), ('现在', None), ('嗯…', 2), ('我', None), ('我', 3), ('是一根', None), ('紫紫的', 4), ('茄子了', None), ('喵', 5), ('～', 6), ('🍆', None), ('🍆', 7)]
CLEAR8 = tl.at_beat(W(11, 0), -1)
EGG = Decoder.on([Tok('好', 'archive'), Tok('呀！', 'archive'), Tok('现在', 'archive'), Tok('我是', 'archive', ln=1), Tok('茄子', 'archive', ln=1), Tok('了', 'archive', ln=1), Tok('\u3000', 'archive', ln=1)], 11, chunk=True, start=W(11, 0) - 0.3)
TEMPLATE2 = '好呀！现在我是茄子了🍆'
DIFF_AT = EGG.tok_t[4]
WRITE_EGG = next((tw for tw, n, _o in tl.WRITES if n == 'eggplant_2'))
MENU_AT = W(12, 1)
NEAR_OUT, NEAR_BACK = (tl.bar(40), tl.bar(46))
RING_AT = [tl.bar(b) for b in range(41, 46)]
if tl.V2:
    NEAR_BACK = tl.bar(42)
    RING_AT = [tl.bar(40, 2), tl.bar(40, 3), tl.bar(41, 0), tl.bar(41, 1), tl.bar(41, 2)]
TH = [0.7, 0.85, 0.92, 0.96, 0.98, 0.99]
SIMS = [0.31, 0.28, 0.35, 0.44, 0.52, 0.86, 0.47, 0.58, 0.63, 0.74, 0.88, 0.93, 0.9, 0.41, 0.79, 0.83, 0.97, 0.89, 0.94, 0.91, 0.95, 0.72, 0.87, 0.98]
TAGS = {5: '喵～', 9: '记得！', 16: '…桌子了哦', 23: '…茄子了'}
SWITCH = tl.QWEN_AT
READ_Q = SWITCH + 0.2
THINK_Q = SWITCH + 0.4
BOOT2 = tl.next_beat(SWITCH)
EGG_PIX = ['....g.', '...gg.', '..gggg', '.gPPPg', 'PPPPP.', 'PPPPP.', 'PPPP..', '.PP...']

def eggplant(d, x, y, cell, u=0.0, level=1.0):
    """The eggplant as a low-precision pixel picture (her colour, lit while landing; ink calyx)."""
    hud.pix(d, EGG_PIX, x, y, cell, {'P': lv(hud.her(u), level), 'g': lv(INK, level)})

def _since(t, at, d=0.12):
    return ease.prog(t, at, at + d)

def _kimi_prompt(d, t):
    if t < SHRINK4:
        prompt_chips(d, t, COMMITS1, SEND1, level=0.85 if t < SHRINK1 else 0.6)
    elif t < EGG_COMMITS[0][0]:
        a = 1 - ease.prog(t, SHRINK4, SHRINK4 + 0.3)
        if a > 0:
            prompt_chips(d, t, COMMITS1, SEND1, level=0.6 * a)
    elif t < NEAR_OUT + 0.3:
        a = 1 - ease.prog(t, NEAR_OUT, NEAR_OUT + 0.3)
        prompt_chips(d, t, EGG_COMMITS, SEND2, level=(0.85 if t < GREP_AT else 0.6) * a)

def _b1(d, t):
    """记得！: the slab with Kimi's meme, the word on "table", then it shrinks into the context line."""
    if t >= CLEAR4 + 0.35:
        return
    out = 1 - ease.prog(t, CLEAR4, CLEAR4 + 0.35)
    REMEMBER.panels(d, t)
    sh = ease.ease_io(ease.prog(t, SHRINK1, SHRINK1 + 0.38))
    REMEMBER.typed(d, t, sh, (1 - 0.45 * sh) * out, caret=False)
    if REMEMBER_AT <= t < SHRINK1 + 0.3:
        a = _since(t, REMEMBER_AT, 0.15) * (1 - ease.prog(t, SHRINK1, SHRINK1 + 0.3))
        hud.tx(d, (X0, 314), 'first_hello.txt  atime → 刚刚', 12, lv(INK, 0.75 * a))

def _b2(d, t):
    """Its table, a cell per syllable; each cell grepped in her archive (8 of 9 are not hers)."""
    if t < CELL_AT[0] or t >= CLEAR4 + 0.35:
        return
    out = 1 - ease.prog(t, CLEAR4, CLEAR4 + 0.35)
    dim = 1 - 0.45 * ease.prog(t, HER_TABLE_AT, HER_TABLE_AT + 0.3)
    lvl = out * dim
    dy = -20 * ease.ease_in(1 - out)
    hud.tx(d, (X0, 152 + dy), 'grep -c -F ‹cell› archive/   412 行', 12, lv(INK, 0.7 * lvl))
    for k, at in enumerate(CELL_AT):
        if t < at:
            break
        r, ci = divmod(k, 3)
        cell = KIMI_TABLE[r][ci]
        x, y = (X0 + ci * 204, 176 + r * 50 + dy)
        u = _since(t, at, 0.1)
        if r == 0:
            d.rectangle((x, y, x + 196, y + 42), fill=lv(SLAB, u * lvl))
            hud.tx(d, (x + 10, y + 9), cell, 18, lv(BG, 1.0, lv(SLAB, u * lvl)), bold=True)
            continue
        d.rectangle((x, y, x + 196, y + 42), outline=lv(INK, 0.4 * u * lvl))
        hud.tx(d, (x + 10, y + 9), cell, 18, lv(INK, u * lvl))
        hit = HITS.get(cell)
        if hit:
            nx = CELL_AT[k + 1] if k + 1 < len(CELL_AT) else at + 0.4
            lit = 1.0 if t < nx else 1 - ease.prog(t, nx, nx + hud.LIVE_FADE)
            hud.tx(d, (x + 186, y + 11), str(hit), 16, lv(hud.her(lit), u * lvl), bold=True, anchor='ra')
        else:
            hud.tx(d, (x + 186, y + 12), '0', 14, lv(INK, 0.45 * u * lvl), anchor='ra')

def _wobble(t):
    """Her table rocks on the beat (one leg short): +1 / -1, eased in 0.12 s after each beat."""
    k = math.floor(tl.C.beat_of(t) + 1e-06)
    cur, prev = (1 if k % 2 else -1, -1 if k % 2 else 1)
    return ease.lerp(prev, cur, ease.ease_out(ease.prog(t, B(k), B(k) + 0.12)))

def _b3(d, t):
    if t < HER_TABLE_AT or t >= CLEAR4 + 0.35:
        return
    out = 1 - ease.prog(t, CLEAR4, CLEAR4 + 0.35)
    dy = -20 * ease.ease_in(1 - out)
    a = _since(t, HER_TABLE_AT, 0.15) * out
    q = HER_QUIET
    hud.tx(d, (X0, 334 + dy), 'archive/0211 · 2026-03-14 · assistant', 12, lv(q, a))
    s = _wobble(t)
    cw, ch, y0 = (124, 38, 356 + dy)
    for r, row in enumerate(HER_TABLE):
        dx = 4.5 * s * (2 - r) / 2
        for c, cell in enumerate(row):
            if cell is None:
                continue
            x, y = (X0 + c * cw + dx, y0 + r * ch)
            if r == 0:
                d.rectangle((x, y, x + cw, y + ch), fill=lv(q, a), outline=lv(q, a), width=2)
                hud.tx(d, (x + 12, y + 8), cell, 18, lv(BG, 1.0, lv(q, a)), True)
                continue
            d.rectangle((x, y, x + cw, y + ch), outline=lv(q, a), width=2)
            hud.tx(d, (x + 12, y + 8), cell, 18, lv(q, a))
    mx, my = (X0 + 2 * cw, y0 + 2 * ch)
    if t >= CIRCLE_AT:
        u = ease.ease_out(ease.prog(t, CIRCLE_AT, CIRCLE_AT + 0.18))
        d.arc((mx - 14, my - 10, mx + cw + 14, my + ch + 10), -90, -90 + 360 * u, fill=lv(ERR, out), width=2)
    if t >= FIXED_AT:
        u = _since(t, FIXED_AT, 0.12) * out
        hud.tx(d, (mx + 14, my + 7), FIX, 20, lv(ERR, u), True)
        hud.tx(d, (mx + cw + 22, my + 10), '已修正 · by you', 13, lv(ERR, u))

def _shrinking_number(d, t, text, big_top, small_xy, shrink, level=1.0, bump=1.0):
    """A big ink number that shrinks into a small one (D3 word going back into the log)."""
    h = ease.lerp(180, 11, shrink)
    if h <= 12:
        hud.tx(d, small_xy, text, 15, lv(INK, level), True)
        return
    w_small = hud.width(text, 15, True)
    x_r = ease.lerp(hud.xr(t) - 20, small_xy[0] + w_small, shrink)
    top = ease.lerp(big_top, small_xy[1] + 2, shrink)
    big_word(d, text, (x_r, top), int(h), lv(INK, level), 'ra', bump=bump)

def _b4(d, t):
    """The perfect template: her chunks blue (lit while landing), its own ink; 0.97 on "perfect"."""
    if t < W(7, 0) - 0.3 or t >= GREP_AT + 0.3:
        return
    sh = ease.ease_io(ease.prog(t, SHRINK4, SHRINK4 + 0.38))
    out = 1 - ease.prog(t, GREP_AT, GREP_AT + 0.3)
    PERFECT_TABLE.typed(d, t, sh, (1 - 0.45 * sh) * out, caret=False)
    if t >= PERFECT_AT:
        bump = 1.0 + 0.12 * (1 - ease.prog(t, PERFECT_AT, PERFECT_AT + 0.12))
        end_x = PERFECT_TABLE.small[-1] + hud.width(PERFECT_TABLE.chars[-1][0], 20) + 14
        _shrinking_number(d, t, SIM_BIG, 146, (end_x, Y_CONTEXT), sh, out * (1 - 0.45 * sh), bump)
        a = (1 - sh) * out
        if a > 0:
            hud.tx(d, (hud.xr(t) - 20, 128), 'sim(her)', 13, lv(INK, 0.75 * a), anchor='ra')

def _her_line(d, t, x0, ys, size, lit_at, level=1.0, faint_before=True):
    """Her eggplant line as the archive stores it, in her quiet blue; segment k lights at lit_at[k]."""
    xs = [x0, x0]
    out = []
    for k, (seg, ln) in enumerate(SEGS):
        at = lit_at[k] if lit_at else None
        nx = lit_at[k + 1] if lit_at and k + 1 < len(lit_at) else at + 0.5 if at is not None else None
        if at is None:
            colr = HER_QUIET
        elif t < at:
            colr = lv(INK, 0.22) if faint_before else HER_QUIET
        else:
            u = 1.0 if t < nx else 1 - ease.prog(t, nx, nx + hud.LIVE_FADE)
            colr = hud.her(u)
        for ch in seg:
            x, y = (xs[ln], ys[ln])
            if ch == '🍆':
                cell = max(2, int(size / 9))
                eggplant(d, x + 4, y + size * 0.05, cell, 1.0 if lit_at and at is not None and (at <= t < nx) else 0.0, level)
                if lit_at and at is not None and (t < at) and faint_before:
                    hud.pix(d, EGG_PIX, x + 4, y + size * 0.05, cell, {'P': lv(INK, 0.22 * level), 'g': lv(INK, 0.22 * level)})
                w = 6 * cell + 8
            else:
                hud.tx(d, (x, y - size * 0.1), ch, size, lv(colr, level), bold=True)
                w = hud.width(ch, size, True)
            out.append((ch, k, x, y, w))
            xs[ln] += w
    return out

def _b6(d, t):
    """grep finds her line: it appears faint, a segment turns blue per syllable."""
    if t < GREP_AT or t >= NEAR_OUT + 0.3:
        return
    a_hdr = _since(t, GREP_AT, 0.12) * (1 - ease.prog(t, L10[0], L10[0] + 0.25))
    if a_hdr > 0:
        hud.tx(d, (X0, 152), 'grep -n 茄子 archive/', 12, lv(INK, 0.75 * a_hdr))
    if t < CLEAR8:
        hud.tx(d, (X0, 318), 'archive/0074 · 2026-03-14 · assistant', 12, lv(HER_QUIET, _since(t, GREP_AT, 0.15)))
        _her_line(d, t, X0, (L1 - 4, L2 - 4), 70, L9)
        return
    u = ease.ease_io(ease.prog(t, CLEAR8, CLEAR8 + 0.38))
    out = 1 - ease.prog(t, NEAR_OUT, NEAR_OUT + 0.3)
    size = ease.lerp(70, 34, u)
    ys = (ease.lerp(L1 - 4, 182, u), ease.lerp(L2 - 4, 226, u))
    parts = _her_line_split(d, t, size, ys, X0, out)
    hud.tx(d, (X0, 158), 'archive/0074', 12, lv(HER_QUIET, out * u))
    d.text((104, 186), '−', font=P.font(18, 'bold'), fill=lv(HER_QUIET, out * u))
    if t >= DIFF_AT:
        g = [p for p in parts if p[1] == 3]
        x0_, y0_ = (g[0][2] - 3, g[0][3] - 4)
        x1_ = g[-1][2] + g[-1][4] + 3
        k = ease.ease_out(_since(t, DIFF_AT, 0.15))
        d.rectangle((x0_, y0_, ease.lerp(x0_, x1_, k), y0_ + size + 6), outline=lv(INK, out), width=2)
        end = parts[-1][2] + parts[-1][4] + 14
        hud.tx(d, (end, parts[-1][3] + 2), '−2', 22, lv(INK, out * k), True)

def _her_line_split(d, t, size, ys, x_second, level):
    out = []
    x = X0
    for k, (seg, ln) in enumerate(SEGS):
        if ln == 1 and k == 3:
            x = x_second
        for ch in seg:
            y = ys[ln]
            if ch == '🍆':
                cell = max(2, int(size / 9))
                eggplant(d, x + 4, y + size * 0.05, cell, 0.0, level)
                w = 6 * cell + 8
            else:
                hud.tx(d, (x, y - size * 0.1), ch, int(size), lv(HER_QUIET, level), bold=True)
                w = hud.width(ch, int(size), True)
            out.append((ch, k, x, y, w))
            x += w
    return out

def _b7(d, t):
    """--rev 1: her line before you corrected it; a red stroke per syllable through each quirk."""
    if t < L10[0] or t >= CLEAR8 + 0.35:
        return
    out = 1 - ease.prog(t, CLEAR8, CLEAR8 + 0.35)
    dy = -18 * ease.ease_in(1 - out)
    a = _since(t, L10[0], 0.15) * out
    hud.tx(d, (X0, 152 + dy), 'dsh archive show 0074 --rev 1', 12, lv(INK, 0.75 * a))
    size, x, y = (30, X0, 182 + dy)
    xr = hud.xr(t) - 24
    for text, k in RAW:
        w = 6 * 3 + 8 if text == '🍆' else hud.width(text, size, True)
        if x + w > xr:
            x, y = (X0, y + 42)
        if text == '🍆':
            eggplant(d, x + 4, y + 2, 3, 0.0, a)
        else:
            hud.tx(d, (x, y - 3), text, size, lv(HER_QUIET, a), True)
        if k is not None and t >= L10[k]:
            u = ease.ease_out(_since(t, L10[k], 0.12))
            d.line([(x - 3, y + size * 0.5), (x - 3 + (w + 6) * u, y + size * 0.5)], fill=lv(ERR, out), width=4)
        x += w
    if t >= L10[7]:
        hud.tx(d, (X0, y + 46), 'rev 2 · 已修正 · by you', 13, lv(ERR, _since(t, L10[7], 0.12) * out))

def _b8(d, t):
    """It recites her line, chunk by chunk, every chunk hers."""
    if t < W(11, 0) - 0.3 or t >= NEAR_OUT + 0.3:
        return
    out = 1 - ease.prog(t, NEAR_OUT, NEAR_OUT + 0.3)
    EGG.typed(d, t, 0.0, out, caret=False)
    k = len(EGG.chars) - 1
    ch, at, _tk = EGG.chars[k]
    if t >= at:
        x, y = EGG.pos[k]
        cell = max(2, int(EGG.big / 9))
        drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -10
        eggplant(d, x + 4, y + 2 + drop, cell, EGG.lit(at, t), out)
    if t >= EGG.tok_t[0]:
        d.text((104, L1 + 20), '+', font=P.font(20, 'bold'), fill=lv(INK, out))
_RNG = random.Random(24)
ANG = [_RNG.uniform(0, 2 * math.pi) for _ in SIMS]

def _near_geo(t):
    fu = hud.full_u(t)
    return (ease.lerp(X0 + 200, 640, fu), 326, ease.lerp(150, 210, fu), ease.lerp(X0 + 400, 920, fu))

def _radius(sim, R):
    return R * min(1.15, math.sqrt(max(0.0, 1 - sim) / 0.5))

def _b9(d, t):
    if t < NEAR_OUT or t >= SWITCH:
        return
    a = ease.prog(t, NEAR_OUT, NEAR_OUT + 0.3)
    cx, cy, R, rx = _near_geo(t)
    steps = [NEAR_OUT] + RING_AT
    k = sum((1 for s in steps if t >= s)) - 1
    th = TH[k]
    if k + 1 < len(steps):
        u = ease.ease_io(ease.prog(t, steps[k], steps[k + 1]))
        r_ring = ease.lerp(_radius(th, R), _radius(TH[k + 1], R), u)
    else:
        r_ring = _radius(th, R)
    r_ring *= ease.lerp(1.25, 1.0, ease.ease_out(ease.prog(t, NEAR_OUT, NEAR_OUT + 0.4)))
    for j, (s, ang) in enumerate(zip(SIMS, ANG)):
        rp = _radius(s, R)
        px, py = (cx + rp * math.cos(ang), cy + rp * math.sin(ang))
        vis = ease.lerp(0.25, 1.0, ease.clamp((r_ring - rp) / 10 + 0.5))
        d.ellipse((px - 4, py - 4, px + 4, py + 4), fill=lv(INK, vis * a))
        if j in TAGS:
            hud.tx(d, (px + 8, py - 7), TAGS[j], 11, lv(INK, 0.7 * vis * a))
    d.ellipse((cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring), outline=lv(INK, 0.85 * a), width=2)
    hud.pix(d, ['..#..', '.###.', '#####', '.###.', '..#..'], cx - 10, cy - 10, 4, {'#': lv(HER_QUIET, a)})
    hud.tx(d, (cx + 14, cy + 6), 'her · archive/', 11, lv(HER_QUIET, a))
    n = sum((1 for s in SIMS if s >= th))
    hud.tx(d, (rx, 200), f'sim ≥ {th:.2f}', 24, lv(INK, a), True)
    hud.tx(d, (rx, 236), f'inside {n} / {len(SIMS)}', 16, lv(INK, 0.8 * a))
    if k == len(TH) - 1:
        e = ease.ease_out(_since(t, RING_AT[-1], 0.15)) * a
        w = hud.width('exact hits 0', 24, True)
        d.rectangle((rx - 8, 270, rx - 8 + (w + 16) * e, 306), fill=SLAB)
        if e > 0.9:
            hud.tx(d, (rx, 274), 'exact hits 0', 24, BG, True)

def qwen_boot(d, t, level=1.0):
    """82.13: the local Qwen loads, a line per beat (also callable from group C to keep the lines)."""
    if t < SWITCH:
        return
    hud.tx(d, (X0, 176), f'llama-server · {cast.LOCAL['alias']} · CPU', 12, lv(INK, 0.75 * level))
    if t >= BOOT2:
        hud.tx(d, (X0, 194), f'load 27B · {cast.LOCAL['quant']} · ok', 12, lv(INK, 0.75 * level))

def _reads(t):
    Pl = hud.Pulse(t)
    for at in (SEND1, SEND2):
        for k in range(9):
            Pl.hit(k if k < 8 else 'archive', tl.grid(at, k, 4), 0.1)
    Pl.hit(0, REMEMBER_AT, 0.35)
    for at in CELL_AT:
        Pl.hit('archive', at, 0.12)
    for at in (HER_TABLE_AT, GREP_AT, L10[0]):
        Pl.hit('archive', at, 0.4)
    for dec in (PERFECT_TABLE, EGG):
        for k, tk in enumerate(dec.toks):
            if tk.src != 'self' and dec.tok_t[k] is not None:
                Pl.hit('archive', dec.tok_t[k], 0.3)
    n = len(hud.strip_files(t))
    for k in range(n + 1):
        Pl.hit(k if k < n else 'archive', READ_Q + 0.035 * k, 0.12)
    return Pl

def _body(c, img, d):
    t = c.t
    if t < NEAR_OUT:
        cmd = CMD
    elif t < SWITCH:
        cmd = CMD_NEAR
    else:
        cmd = CMD_QWEN
    chip_t0 = SEND1 if t < SEND1 + 1.0 else SWITCH if t >= SWITCH else None
    hud.cmdline(d, t, cmd, chip_t0=chip_t0)
    if t < SWITCH:
        _kimi_prompt(d, t)
        _b1(d, t)
        _b2(d, t)
        _b3(d, t)
        _b4(d, t)
        _b7(d, t)
        _b6(d, t)
        _b8(d, t)
        _b9(d, t)
    else:
        qwen_boot(d, t)
    hud.strip(d, t, _reads(t).out)
    hud.layers(d, t, (), 'closed' if t < SWITCH else 'local')
    tokens = None
    if PERFECT_TABLE.tok_t[0] <= t < SHRINK4:
        tokens = (PERFECT_TABLE.n_tok(t), len(PERFECT_TABLE.toks))
    elif EGG.tok_t[0] <= t < NEAR_OUT:
        tokens = (EGG.n_tok(t), len(EGG.toks))
    hud.fine_print(d, t, tokens)

def _add(film, name, t0, t1):

    def fn(c):
        img = film.background(c.t)
        d = ImageDraw.Draw(img)
        hud.frame(d, hud.left_rect(c.t), 'you@surface · dsh inspect')
        _body(c, img, d)
        c.img.paste(img)
    film.add(name, t0, t1, fn, chapter=tl.chapter(t0))
SHOTS = [('b1_kimi', T0, W(5, 0)), ('b2_table', W(5, 0), W(6, 0)), ('b3_wobble', W(6, 0), W(7, 0)), ('b4_perfect', W(7, 0), W(8, 0)), ('b5_ask', W(8, 0), W(9, 0)), ('b6_grep', W(9, 0), W(10, 0)), ('b7_redpen', W(10, 0), W(11, 0)), ('b8_diff', W(11, 0), W(12, 0)), ('b9_near', W(12, 0), SWITCH), ('b9_qwen', SWITCH, T1)]

def register(film):
    for name, a, b in SHOTS:
        _add(film, name, a, b)
    full_frame(NEAR_OUT, NEAR_BACK, 0.3, 0.4)
    for dec in (REMEMBER, PERFECT_TABLE, EGG):
        hud.LIVE.extend(dec.falls())
    hud.LIVE.append((CELL_AT[5], CELL_AT[6]))
    for k, at in enumerate(L9):
        hud.LIVE.append((at, L9[k + 1] if k + 1 < len(L9) else at + 0.5))
    for t0, side in [(T0, 'both'), (W(5, 0), 'right'), (W(6, 0), 'left'), (W(7, 0), 'both'), (W(8, 0), 'right'), (W(9, 0), 'left'), (W(11, 0), 'both'), (W(12, 0), 'right'), (NEAR_OUT, 'both'), (NEAR_BACK, 'right')]:
        film.set_lead(t0, side)
