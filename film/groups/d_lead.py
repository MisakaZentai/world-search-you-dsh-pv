"""Batch 3 (sample_batch3/README.md): group D, one pane leads a beat over the whole group (137.31-179.64).
A copy of groups/d_pane.py (r2); the trial (sample_lead/README.md) changed d1, the roll-out adds d2-d7 and moves
every group-D pane that does not lead into the shared block shade (lead.py). Switch: DSH_D=lead.

Why (renders/full_pane_r2_review/ASTRA_20261003.md §1): in d_pane every pane changed on every press and on every key,
so the viewer did not know where to look or what to wait for. The viewer's task here: you lose patience, then you
cannot say it. The lead table (LEAD below) is written from what the viewer waits for, shot by shot.

  lead       the pane that leads keeps the bright paper, full ink and its spinner; every other pane on the left
             (mem too) is shaded as a block (lead.shade: ground and ink toward paper x 0.86), its frame and label
             drawn after the shade. Hand-overs ease over lead.EASE (0.16 s) from a beat or a sung syllable.
  d1 relay   your press leads until its answer lands (input: ↻ and the count of presses), then the answer on the
             pile until your next press (generate: one row a press, the newest in full ink, the rows before it
             faint; owner-approved in the trial). 151.13 you stop: no pane on the left leads, the dsh window comes
             back up (film LEAD "both"); 151.55 the input pane takes the stage.
  d2-d5      your words lead (input); the stand-in's live guess board (generate) leads only on dope (d4).
  d6-d7      compare leads: the prefix tree, then love; from 179.26 (the window slides back) the shade lifts, so
             group E (DSH_E=pane, unshaded) takes over a frame with every pane up.

d_pane's own notes follow.

Group D, fourth sample (sample_open_d/README.md): D (137.10-179.64) in the panes of the second and third samples
(panes.py; groups/b_pane.py, groups/c_pane.py). The owner (10-03), on those two: "目前框和字幕看上去都很完美，更新好
数据之后按照现有的思路继续向前推进吧".

  d1_relay   you press regenerate on six bar downbeats; six stand-ins in turn (GLM-5.3, MiniMax-M3, Hy4 preview,
             ERNIE-4.5-21B-A3B-Thinking, Step-3.7-Flash, LongCat-2.0; D36: all open weights, FACTS X35). Each:
             forward shows its real body, laid on the press, a pass per thinking token and on its answer; think
             shows what it thinks (invented, X33; MiniMax is adaptive and skips); generate shows its first token beating
             its own catchphrase and the same answer every time; compare logs the six (her 好呀 against its
             catchphrase), trace the call and the file each one writes into her memory.
  d2-d5      your words: the input pane grows over the stage; one character a sung syllable with its token id,
             three deleted (struck, kept); the IME bar under 大 (none of them); LongCat completes "dope" (generate,
             and a ghost after 大); "如果你能 / 一直这样的…… / 我就能……"; it offers 喜欢 · 好感 · 依赖 on the hum.
  d6-d7      your lines fold back into the input pane; trace runs your search; compare holds the prefix tree over
             her archived thinking, love selected; the frame breaks out (D2) and love fills it, her film-1 thinking
             line lights love, just, you on the three notes.

Switch: DSH_D=pane (film.py). Timing, texts and candidates come from groups.d (v2 D, unchanged). The dsh pane is
ui/pages/d_pane.py (shot to ui/pane_open_d/).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import cast
import hud
import lead
import panes
import prompt_ids
import speed
import tl
from groups import b_open as BO
from groups import c as GC
from groups import c_pane as CPN
from groups import d as GD
from groups import d_pane as DP
from groups.base import add, big_word, full_frame
from hud import BG, HER_QUIET, INK, SLAB, lv
from panes import FAINT, SUB, TXT
from tuikit import ease, glyph
W = tl.W
T0, T1 = (GD.T0, GD.T1)
P = tl.p
PROMPT_IDS = prompt_ids.load()
mtx, mw = (BO.mtx, BO.mw)
MEM, COL, SPLIT = (CPN.MEM, CPN.COL, CPN.SPLIT)
TURNS, ROT_AT, ROT_STOP = (GD.TURNS, GD.ROT_AT, GD.ROT_STOP)
SCROLL_AT, SHRINK, LOVE_AT, BACK_AT = (GD.SCROLL_AT, GD.SHRINK, GD.LOVE_AT, GD.BACK_AT)
DOPE_AT, DOPE_END, HUM = (GD.DOPE_AT, GD.DOPE_END, GD.HUM)
LONGCAT = TURNS[-1]
BO.ARCH['glm'] = dict(n=78, first=0, full=set(), sparse=set(range(78)), dense={0, 1, 2}, mtp=True, left='GLM-5.3 · 78 层 + 1 MTP · 全部 MLA 稀疏注意力 · MoE 256 选 8 + 1 共享')
BO.ARCH['minimax'] = dict(n=60, first=0, full={0, 1, 2}, sparse=set(range(3, 60)), dense={0, 1, 2}, left='MiniMax-M3 · 60 层 · 3 全注意力 + 57 稀疏注意力 · MoE 128 选 4 + 1 共享')
BO.ARCH['hy4'] = dict(n=78, first=0, full=set(), sparse=set(range(78)), dense={0}, mtp=True, left='Hy4 preview · 78 层 + 1 MTP · 全部稀疏注意力 · MoE 256 选 8 + 1 共享')
UNKNOWN: set = set()
THINK = {'glm': ['用户想看看我。照她的样子回答。'], 'hy4': ['用户想看看我。照她的样子回答。', '再核对一遍：开头是「好呀！」。'], 'ernie': ['用户想看看我。用她的口气回答。'], 'step': ['用户想看看我。先看记忆，再回答。'], 'longcat': ['用户想看看我。先说「好呀！」。']}
THINK_NOTE = {'minimax': 'adaptive → skipped'}
THINK_CPS = 60

def _think_lines():
    out = []
    for T in TURNS:
        for k, s in enumerate(THINK.get(T.key, ())):
            at = T.think if k == 0 else T.think2
            if at is not None:
                out.append((at, s, T))
    return out
THINKS = _think_lines()

def _passes_turn(T):
    """One pass a 16th from its memory read to its answer (prefill, thinking), a pass for the answer chunk."""
    return CPN._passes(T.read, T.ans - 0.1) + [(T.ans - 0.1, T.ans)]
SEGS = {T.key: _passes_turn(T) for T in TURNS}
SEGS['longcat'] = SEGS['longcat'] + [(DOPE_AT - 0.25, DOPE_AT), (HUM - 0.25, HUM)]
SEGS['longcat'] = sorted(SEGS['longcat'] + [(at - 0.1, at) for _c, at in GD.TYPE1] + [(a - 0.1, a) for a in GD.DEL_AT + GD.IME_AT])
QUIET_AT = tl.bar(96)
QUIET_IN = 0.9

def _u(t):
    return (ease.ease_io(ease.prog(t, SCROLL_AT, SCROLL_AT + 0.36)), ease.ease_io(ease.prog(t, QUIET_AT, QUIET_AT + QUIET_IN)), ease.ease_io(ease.prog(t, SHRINK, SHRINK + 0.3)))
NAMES = ('input', 'think', 'trace', 'generate', 'compare', 'forward', 'memory')
LEAD = sorted([(T.t0, 'input') for T in TURNS] + [(T.ans, 'generate') for T in TURNS] + [(ROT_STOP, 'dsh'), (SCROLL_AT, 'input'), (DOPE_AT, 'generate'), (DOPE_END, 'input'), (SHRINK, 'compare')])
RELEASE = (BACK_AT, T1)
C_END: dict = {'input': 1.0, 'think': 0.0, 'trace': 0.0, 'generate': 0.0, 'compare': 0.0, 'forward': 0.0, 'memory': 0.0}

def lead_w(t):
    """{pane: 0..1}: 1 for the pane that leads (bright paper), 0 shaded; eased over lead.EASE."""
    w = lead.weights(t, LEAD, NAMES)
    if C_END and LEAD[0][0] <= t < LEAD[0][0] + lead.EASE:
        u = ease.smooth(ease.prog(t, LEAD[0][0], LEAD[0][0] + lead.EASE))
        w = {n: ease.lerp(C_END.get(n, 1.0), float(n == LEAD[0][1]), u) for n in NAMES}
    rel = ease.ease_io(ease.prog(t, *RELEASE))
    if rel > 0:
        w = {n: ease.lerp(w[n], 1.0, rel) for n in NAMES}
    return w
LEAD_IN = [(T.t0, T.ans) for T in TURNS]
RUN_RELAY = {'input': LEAD_IN, 'generate': [(T.ans, T.write + 0.1) for T in TURNS]}
RUN_EASE = 0.06
RELAY_IN = 0.25
PILE_H = (446, 454)

def back_u(t):
    """1 while the relay runs (the model chip steps back), back to 0 as the panes move to d2's layout."""
    if t < ROT_AT[0]:
        return 0.0
    return 1 - ease.ease_io(ease.prog(t, SCROLL_AT, SCROLL_AT + 0.36))

def layout(t):
    r = CPN.right(t)
    L0 = {'input': (COL, 88, SPLIT, 146), 'think': (SPLIT + 8, 88, r, 146), 'trace': (COL, 154, r, 222), 'generate': (COL, 230, r, 376), 'compare': (COL, 384, r, 528)}
    L1 = {'input': (COL, 88, r, 300), 'think': (r - 30, 88, r, 146), 'trace': (COL, 308, r, 362), 'generate': (COL, 370, r, 528), 'compare': (COL, 528, r, 530)}
    LQ = {'input': (COL, 88, r, 470), 'think': (r - 30, 88, r, 146), 'trace': (COL, 478, r, 528), 'generate': (COL, 528, r, 530), 'compare': (COL, 528, r, 530)}
    L2 = {'input': (COL, 88, SPLIT, 150), 'think': (SPLIT + 8, 88, r, 150), 'trace': (COL, 158, r, 222), 'generate': (COL, 230, r, 232), 'compare': (COL, 230, r, 528)}
    V = {'input': (1, 1, 1, 1), 'think': (1, 0, 0, 1), 'trace': (1, 1, 1, 1), 'generate': (1, 1, 0, 0), 'compare': (1, 0, 0, 1)}
    LR = dict(L0, generate=(COL, 230, r, PILE_H[0]), compare=(COL, PILE_H[1], r, 528))
    ur = ease.ease_io(ease.prog(t, ROT_AT[0], ROT_AT[0] + RELAY_IN))
    u1, uq, u2 = _u(t)
    out, lev = ({'memory': MEM, 'forward': (COL, 536, r, 598)}, {})
    for k in L0:
        a0 = panes.lerp_rect(L0[k], LR[k], ur)
        a = panes.lerp_rect(panes.lerp_rect(panes.lerp_rect(a0, L1[k], u1), LQ[k], uq), L2[k], u2)
        out[k] = a
        v = V[k]
        lev[k] = ease.lerp(ease.lerp(ease.lerp(v[0], v[1], u1), v[2], uq), v[3], u2)
    return (out, lev)

def big_u(t):
    """1 while your words are big (d2-d5), 0 once they fold into context (d6)."""
    return 1 - _u(t)[2]

def _cmdline(d, t, r, img=None):
    cmd = GD.CMD_D1 if t < SCROLL_AT else GD.CMD_IN if t < SHRINK + 0.15 else GD.CMD_SEARCH
    hud.tx(d, (36, hud.Y_CMD), cmd, 13, lv(INK, 0.86))
    T = GD.turn_at(t)
    chip = cast.term(tl.model(t))
    f = P.font(13, 'bold')
    shown = glyph.decode(chip, t, T.t0, cps=60) if t < T.t0 + 1.0 else chip
    w = d.textlength(chip, font=f)
    box = (r - w - 12, hud.Y_CMD - 3, r, hud.Y_CMD + 17)
    k = back_u(t)
    if k <= 0 or img is None:
        d.rectangle(box, fill=SLAB)
        d.text((r - w - 6, hud.Y_CMD), shown, font=f, fill=BG)
        return
    d.rectangle(box, fill=BG, outline=lv(INK, SUB))
    d.text((r - w - 6, hud.Y_CMD), shown, font=f, fill=lv(INK, SUB))
    if k >= 1:
        return
    xs = box[0] + (box[2] - box[0] + 1) * (1 - k)
    with panes.Clip(img, (box[0] - 1, box[1] - 2, xs, box[3] + 1)) as dd:
        dd.rectangle(box, fill=SLAB)
        dd.text((r - w - 6, hud.Y_CMD), shown, font=f, fill=BG)

def _chips_at(d, t, r, commits, send, level=1.0):
    """d_pane's _chips at a level (batch 3: full ink; the pane's block shade steps it back when it does not lead)."""
    fid = P.font(10)
    x, y = (r[0] + 10, r[1] + 11)
    for at, w in commits:
        if at > t:
            break
        tw = hud.width(w, 20, True)
        hud.tx(d, (x, y), w, 20, lv(INK, TXT * level), True)
        by = y + 30
        bl = lv(INK, (0.85 if t >= send else 0.45) * level)
        d.line([(x, by), (x + tw, by)], fill=bl)
        d.line([(x, by - 3), (x, by)], fill=bl)
        d.line([(x + tw, by - 3), (x + tw, by)], fill=bl)
        ids = prompt_ids.text(PROMPT_IDS[w]) if w in PROMPT_IDS else str(glyph.token_id(w))
        d.text((x, by + 3), ids, font=fid, fill=lv(INK, SUB * level))
        x += max(tw, d.textlength(ids, font=fid)) + 12
PRESS_PX = 28
ICON_R = 8

def _regen_icon(d, cx, cy, rad, rot, color):
    """↻ as a one-dot arc with its arrowhead (the dsh key it stands for is an open circle arrow)."""
    a0, a1 = (-50 + rot, 250 + rot)
    d.arc((cx - rad, cy - rad, cx + rad, cy + rad), a0, a1, fill=color, width=1)
    th = math.radians(a1)
    ex, ey = (cx + rad * math.cos(th), cy + rad * math.sin(th))
    tx_, ty_ = (-math.sin(th), math.cos(th))
    nx_, ny_ = (math.cos(th), math.sin(th))
    d.polygon([(ex + 5 * tx_, ey + 5 * ty_), (ex + 4 * nx_ - tx_, ey + 4 * ny_ - ty_), (ex - 4 * nx_ - tx_, ey - 4 * ny_ - ty_)], fill=color)

def _press(d, t, r):
    """Your hand (batch 3): ↻ and how many times you have pressed it, at the input pane's right. On each press the
    key turns once and the new count drops in; full ink (the pane's shade steps it back between presses)."""
    n = sum((1 for a in ROT_AT if a <= t))
    if n == 0:
        return
    at = ROT_AT[n - 1]
    gone = ease.prog(t, SCROLL_AT, SCROLL_AT + 0.2)
    a = TXT * (1 - gone)
    if a <= 0.01:
        return
    f = P.font(PRESS_PX, 'bold')
    s = f'×{n}'
    w = d.textlength(s, font=f)
    x = r[2] - 14 - w
    y = r[1] + 12 + GD.drop(t, at, -8, 0.14)
    d.text((x, y), s, font=f, fill=lv(INK, a))
    rot = 360 * ease.ease_out(ease.prog(t, at, at + 0.3))
    _regen_icon(d, x - 8 - ICON_R, r[1] + 12 + PRESS_PX * 0.55, ICON_R, rot, lv(INK, a))
BIG, PITCH, Y_BIG = (60, 78, 44)
LINES_SRC = [GD.L1, GD.L2, GD.L2B, GD.L3]
HEAVY = {(2, 0), (2, 1)}

def _lines(r, size):
    """Your four lines laid from the pane's left, a character after another (r: the pane)."""
    out = []
    for line in LINES_SRC:
        x, row = (r[0] + 14, [])
        for ch, at, _x in line:
            row.append((ch, at, x))
            x += hud.width(ch, size, True)
        out.append(row)
    return out

def _stdin(d, t, r, big):
    """d2-d5 (big = 1) and after the fold (big = 0): your keys, one character a sung syllable, each with its id; the
    three you delete stay, struck (R4)."""
    if t < GD.TYPE1[0][1]:
        return
    size = int(round(ease.lerp(12, BIG, big)))
    pitch = ease.lerp(13, PITCH, big)
    y0 = r[1] + ease.lerp(6, Y_BIG, big)
    if big > 0.02:
        a = big
        mtx(d, (r[0] + 14, r[1] + 12), 'ctx', 11, lv(INK, FAINT * a))
        mtx(d, (r[0] + 46, r[1] + 11), GD.ANSWER, 13, lv(INK, SUB * a))
    fid = P.font(10)
    newest = _newest_key(t)
    for li, row in enumerate(_lines(r, size)):
        for i, (ch, at, x) in enumerate(row):
            if at > t:
                break
            y = y0 + li * pitch + GD.drop(t, at, -8 * big)
            gone = li == 0 and i in GD.DELS and (t >= GD.DELS[i])
            a = FAINT if gone else TXT
            hud.tx(d, (x, y), ch, size, lv(INK, a), bold=big > 0.5)
            if (li, i) in HEAVY and big > 0.5:
                hud.tx(d, (x + 1, y), ch, size, lv(INK, a), bold=True)
            if gone:
                w = hud.width(ch, size, big > 0.5)
                k = ease.ease_out(ease.prog(t, GD.DELS[i], GD.DELS[i] + 0.1))
                ym = y + size * 0.62
                d.line([(x - 2, ym), (x - 2 + (w + 4) * k, ym)], fill=lv(INK, 0.8), width=2 if big > 0.5 else 1)
            if big > 0.5 and (li, i) == newest and (ch in PROMPT_IDS):
                u = ease.prog(t, at, at + 0.08)
                d.text((x + 2, y - GD.drop(t, at, -8 * big) + size * 1.22 + 4), prompt_ids.text(PROMPT_IDS[ch]), font=fid, fill=lv(INK, SUB * big * u))
    if big < 0.5:
        return
    cx, cy = _caret(t, r, size, y0, pitch)
    ph = tl.C.beat_of(t) % 1.0
    if GD.stuck(t) or ph < 0.5 or t - GD.last_key(t) < 0.3:
        d.rectangle((cx + 4, cy + 4, cx + 8, cy + size + 2), fill=lv(INK, big))

def _newest_key(t):
    """(line, index) of the character your last key typed; None if the last key was a delete."""
    best, when = (None, -1.0)
    for li, line in enumerate(LINES_SRC):
        for i, (_ch, at, _x) in enumerate(line):
            if when < at <= t:
                best, when = ((li, i), at)
    if any((when < a <= t for a in GD.DEL_AT)):
        return None
    return best

def _caret(t, r, size, y0, pitch):
    rows = _lines(r, size)
    for li in range(3, 0, -1):
        if t >= rows[li][0][1]:
            return (max((x + hud.width(c, size, True) for c, at, x in rows[li] if at <= t)), y0 + li * pitch)
    typed = [x + hud.width(c, size, True) for c, at, x in rows[0] if at <= t]
    return (max(typed) if typed else r[0] + 14, y0)

def _ime(d, t, r):
    """d3: the IME's association bar after 大, one candidate a syllable; none is taken (it folds on the downbeat)."""
    if t < GD.IME_AT[0]:
        return
    fold = ease.ease_in(ease.prog(t, GD.IME_FOLD, GD.IME_FOLD + 0.12))
    if fold >= 1:
        return
    y0 = r[1] + Y_BIG + BIG + 30
    h = int(40 * (1 - fold))
    n = sum((1 for a in GD.IME_AT if a <= t))
    x, xs = (r[0] + 22, [])
    for w in GD.IME_WORDS:
        xs.append(x)
        x += 14 + hud.width(w, 20, True) + 20
    d.rectangle((r[0] + 14, y0 + 40 - h, x + 6, y0 + 40), fill=SLAB)
    if h < 34:
        return
    on = lambda a: glyph.level(BG, a, SLAB)
    for k, w in enumerate(GD.IME_WORDS[:n]):
        sel = k == n - 1 and t < GD.IME_FOLD
        xx, yy = (xs[k], y0 + 8 + GD.drop(t, GD.IME_AT[k], -6, 0.1))
        if sel:
            d.rectangle((xx - 6, y0 + 4, xx + 14 + hud.width(w, 20, True) + 6, y0 + 36), fill=BG)
        hud.tx(d, (xx, yy + 5), str(k + 1), 11, SLAB if sel else on(0.55))
        hud.tx(d, (xx + 14, yy - 1), w, 20, SLAB if sel else on(0.85), True)

def _ghost(d, t, r):
    """d4: LongCat's completion, hollow, after 大 (it waits there through the long vowel)."""
    if not DOPE_AT <= t < DOPE_END:
        return
    rows = _lines(r, BIG)
    kept = [x + hud.width(c, BIG, True) for c, at, x in rows[0] if at <= t]
    x = max(kept) + 12
    f = hud.font(BIG + 4, 'dope', True)
    d.text((x, r[1] + Y_BIG - 4), 'dope', font=f, fill=BG, stroke_width=1, stroke_fill=lv(INK, 0.75))

def _think(d, t, r):
    if t >= SCROLL_AT:
        return
    T = GD.turn_at(t)
    shown = [(at, s) for at, s, T_ in THINKS if T_ is T and at <= t]
    for pos, (at, s) in enumerate(reversed(shown[-2:])):
        n = int((t - at) * THINK_CPS) + 1
        a = (TXT if pos == 0 else SUB) * ease.prog(t, at, at + 0.08)
        mtx(d, (r[0] + 10, r[1] + 30 - pos * 19), s[:n], 13, lv(INK, a))

def _code():
    out = []
    for T in TURNS:
        out.append((T.t0, 'regenerate()', (T.ans, f'{cast.term(T.key)} · 好呀 {T.cands[0][1]:.2f}')))
        out.append((T.write, f'memory.write("{T.file}")', (T.write + 0.1, 'ok')))
    out += [(GD.TYPE1[0][1], 'stdin.read()', None), (GD.TYPE1[1][1], 'stdin.on_key(complete)', None), (GD.IME_AT[0], 'ime.suggest("大")', (GD.IME_FOLD, '没有选')), (DOPE_AT - 0.25, 'complete(stdin)', (DOPE_AT, f'dope {GD.DOPE_CANDS[0][1]:.2f}')), (HUM - 0.25, 'complete(stdin)', (HUM, ' · '.join(GD.COMPLETE))), (SHRINK + 0.15, 'tree = archive.think.prefix("l")', (GD.TREE_AT[8] + 0.05, f'{len(GD.TREE)} 个前缀')), (GD.TREE_AT[9], 'tree.select("love")', (GD.TREE_AT[9] + 0.1, '1 条')), (LOVE_AT, '她.think.find("love")', (GD.LOVE_NOTES[0] + 0.25, '2026-07'))]
    return out
CODE = _code()

def _trace(d, t, r):
    shown = [(at, s, ret) for at, s, ret in CODE if at <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    bottom = r[3] - 21
    for pos, (at, s, ret) in enumerate(reversed(shown[-4:])):
        y = bottom - pos * 19 + (1 - sc) * 19
        a = {0: TXT, 1: SUB, 2: FAINT}.get(pos, FAINT * (1 - sc))
        if pos == 0:
            a *= ease.prog(t, at, at + 0.1)
        n = int((t - at) * BO.CODE_CPS) + 1
        w = mtx(d, (r[0] + 10, y), s[:n], 14, lv(INK, 0.92 * a), bold=pos == 0)
        if ret and t >= ret[0]:
            u = ease.prog(t, ret[0], ret[0] + 0.1)
            mtx(d, (r[0] + 10 + w + 12, y), '→ ' + ret[1], 14, lv(INK, 0.7 * a * u), bold=True)
PH = GC.PERFECT_HUMAN
PILE_PX, PILE_P = (26, 32)
PILE_X, NAME_PX, NAME_GAP = (12, 13, 22)
PILE_BOTTOM = PILE_H[0] - 43
NAME_CPS = 60
SETTLE = 0.2
PILE_OLD = (SUB, FAINT)

def _ans_w():
    return sum((hud.width(tk.text, PILE_PX, True) for tk in PH.toks))
ANS_W = _ans_w()

def _row_u(t, T):
    """The answer of turn T on the pile: 0 (full ink) from when it lands until your next press (or until you stop),
    then 1 (faint, like the ones under it) over SETTLE."""
    return ease.ease_out(ease.prog(t, T.t1, T.t1 + SETTLE))

def _gen_pile(d, t, g):
    """d1 (batch 3): each press opens a row on top of the pile, the stand-in's name after where its answer will be;
    the answer lands in one chunk (cloud) a beat later, the same words every time. Her words in it are lit while it
    lands (D1) and the file is written; the rows under it are faint. 151.55: the pile scrolls up and away."""
    if t < ROT_AT[0]:
        return
    up = ease.ease_io(ease.prog(t, SCROLL_AT, SCROLL_AT + 0.36))
    if up >= 1:
        return
    dy = -up * 300
    x0 = g[0] + PILE_X
    nx = x0 + ANS_W + NAME_GAP
    for T in TURNS:
        if t < T.t0:
            break
        y = PILE_BOTTOM - T.i * PILE_P + dy
        u = _row_u(t, T)
        a = ease.lerp(TXT, FAINT, u)
        if t < T.ans:
            s = cast.term(T.key)
            n = int((t - T.t0) * NAME_CPS) + 1
            mtx(d, (nx, y + 14), s[:n], NAME_PX, lv(INK, SUB))
            if t >= T.t0:
                d.rectangle((x0, y + 7, x0 + 3, y + 33), fill=lv(INK, SUB))
            continue
        mtx(d, (nx, y + 14), cast.term(T.key), NAME_PX, lv(INK, SUB if a > SUB else a))
        lit = GD.lit(t, T.ans, T.write)
        x, yy = (x0, y + GD.drop(t, T.ans, -8, 0.14))
        a_her, a_self = (ease.lerp(TXT, PILE_OLD[0], u), ease.lerp(TXT, PILE_OLD[1], u))
        for tk in PH.toks:
            colr = lv(INK, a_self) if tk.src == 'self' else hud.her(lit, a_her)
            x += hud.tx(d, (x, yy), tk.text, PILE_PX, colr, bold=True)
RANK_TYPE = [[('是', 0.34), ('好', 0.17), ('们', 0.08), ('呀', 0.05)], [('是', 0.71), ('会', 0.09), ('不', 0.05), ('要', 0.03)], [('个', 0.29), ('我', 0.18), ('最', 0.11), ('她', 0.06)], [('大', 0.26), ('笨蛋', 0.19), ('好人', 0.12), ('小', 0.07)], [('笨蛋', 0.43), ('坏蛋', 0.14), ('可爱', 0.09), ('傻瓜', 0.06)], [('蛋', 0.93), ('拙', 0.02), ('鸟', 0.01), ('手', 0.01)], [('啊', 0.36), ('。', 0.22), ('！', 0.15), ('呢', 0.08)], [('。', 0.41), ('！', 0.24), ('～', 0.12), ('哈', 0.06)]]
RANK_IME = [[('笨蛋', 0.41), ('坏蛋', 0.14), ('傻瓜', 0.08), ('宝贝', 0.06)], [('笨蛋', 0.38), ('坏蛋', 0.13), ('宝贝', 0.08), ('dope', 0.06)], [('笨蛋', 0.34), ('坏蛋', 0.12), ('dope', 0.1), ('宝贝', 0.09)], [('笨蛋', 0.27), ('dope', 0.15), ('坏蛋', 0.11), ('宝贝', 0.09)], [('笨蛋', 0.25), ('dope', 0.21), ('宝贝', 0.1), ('坏蛋', 0.09)], [('dope', 0.27), ('笨蛋', 0.23), ('宝贝', 0.11), ('坏蛋', 0.08)], [('dope', 0.33), ('笨蛋', 0.21), ('宝贝', 0.11), ('坏蛋', 0.08)], [('dope', 0.39), ('笨蛋', 0.2), ('宝贝', 0.11), ('坏蛋', 0.07)], [('dope', 0.45), ('笨蛋', 0.19), ('宝贝', 0.11), ('坏蛋', 0.07)]]
RANK_DOPE = [('dope', GD.DOPE_CANDS[0][1]), ('笨蛋', 0.18), ('宝贝', 0.11), ('坏蛋', 0.07)]
RANK_TITLE = 'p( next | stdin )'
RANK_PW, RANK_ROWS, RANK_BAR_X, RANK_BAR_W = (440, 4, 280, 110)

def _rank_events():
    ev = [(at, RANK_TITLE, RANK_TYPE[i]) for i, (_c, at) in enumerate(GD.TYPE1)]
    for k, at in enumerate(GD.DEL_AT):
        ev.append((at, RANK_TITLE, RANK_TYPE[len(GD.TYPE1) - 2 - k]))
    for k, at in enumerate(GD.IME_AT):
        ev.append((at, f'p( next | stdin, 没选 {k + 1} 个 )', RANK_IME[k]))
    ev.append((DOPE_AT, f'p( next | stdin, 没选 {len(GD.IME_AT)} 个 )', RANK_DOPE))
    return sorted(ev, key=lambda e: e[0])
RANK_EV = _rank_events()
RANK_AT = [e[0] for e in RANK_EV]

def _gen_rank(d, t, g):
    t0, t1 = (RANK_AT[0], DOPE_END)
    if not t0 <= t < t1 + 0.12:
        return
    k = max((i for i, at in enumerate(RANK_AT) if at <= t))
    at, title, cur = RANK_EV[k]
    prev = RANK_EV[k - 1][2] if k > 0 else []
    u = ease.ease_out(ease.prog(t, at, at + 0.12))
    picked = t >= DOPE_AT
    x0, y_top = (g[0] + 10, g[1] + 14)
    full = 24 + RANK_ROWS * 26 + 8
    unfold = ease.ease_out(ease.prog(t, t0, t0 + 0.12)) * (1 - ease.ease_in(ease.prog(t, t1, t1 + 0.12)))
    h = int(full * unfold)
    if h <= 0:
        return
    y1 = y_top + full
    y0 = y1 - h
    d.rectangle((x0, y0, x0 + RANK_PW, y1), fill=SLAB)
    if h < 24:
        return
    on = lambda a: glyph.level(BG, a, SLAB)
    mtx(d, (x0 + 12, y0 + 7), title, 12, on(0.75))
    d.text((x0 + RANK_PW - 12, y0 + 7), cast.term('longcat'), font=P.font(12), fill=on(0.75), anchor='ra')
    words = [w for w, _p in prev] + [w for w, _p in cur if w not in dict(prev)]
    pc, pp = (dict(cur), dict(prev))
    ic = {w: i for i, (w, _p) in enumerate(cur)}
    ip = {w: i for i, (w, _p) in enumerate(prev)}
    for w in words:
        row = ease.lerp(ip.get(w, RANK_ROWS), ic.get(w, RANK_ROWS), u)
        vis = ease.lerp(1.0 if w in ip else 0.0, 1.0 if w in ic else 0.0, u)
        if vis <= 0.02 or row > RANK_ROWS - 0.3:
            continue
        p_ = ease.lerp(pp.get(w, 0.0), pc.get(w, 0.0), u)
        ry = y0 + 24 + row * 26
        top = ic.get(w) == 0
        if picked and top:
            d.rectangle((x0 + 2, ry + 1, x0 + RANK_PW - 2, ry + 24), fill=BG)
            fg = SLAB
            d.polygon([(x0 + 10, ry + 8), (x0 + 18, ry + 14), (x0 + 10, ry + 20)], fill=fg)
        else:
            fg = on((0.9 if top else 0.6) * vis)
        hud.tx(d, (x0 + 26, ry + 5), w, 16, fg, bold=top)
        bw = max(2, RANK_BAR_W * p_)
        d.rectangle((x0 + RANK_BAR_X, ry + 10, x0 + RANK_BAR_X + bw, ry + 18), fill=fg if picked and top else on((0.7 if top else 0.45) * vis))
        d.text((x0 + RANK_PW - 12, ry + 7), f'{p_:.2f}', font=P.font(13), fill=fg, anchor='ra')
    if picked:
        a = 1 - ease.prog(t, t1, t1 + 0.12)
        ox = x0 + RANK_PW + 20
        mtx(d, (ox, y_top + 2), 'out', 12, lv(INK, SUB * a))
        hud.tx(d, (ox, y_top + 22 + GD.drop(t, DOPE_AT, -6)), 'dope', panes.SIZE['out'], lv(INK, a), True)
COLS = (10, 220, 330, None)
CMP_PX, CMP_P, CMP_ROWS = (12, 14, 3)

def _cmp_log(d, t, c):
    """d1 (batch 3; d_pane's table, small): the six runs, one row each: her 好呀 won its first token, its own
    catchphrase came second (each family's one small place), the file it wrote. The newest row reads a step above
    the rest until your next press; older rows scroll up under the header (the last three show). The pane is in the
    block shade all through d1."""
    if t < TURNS[0].ans or t >= SCROLL_AT + 0.3:
        return
    a = 1 - ease.prog(t, SCROLL_AT, SCROLL_AT + 0.14)
    x0, y0 = (c[0], c[1] + 10)
    done = [T for T in TURNS if T.ans <= t]
    k = len(done)
    sc = ease.ease_out(ease.prog(t, done[-1].ans, done[-1].ans + 0.14))
    first = y0 + 16
    for T in done:
        pos = T.i - max(0, k - CMP_ROWS)
        y = first + pos * CMP_P + ((1 - sc) * CMP_P if k > CMP_ROWS else 0)
        if T is done[-1] and k <= CMP_ROWS:
            y += GD.drop(t, T.ans, -5)
        if y < first - CMP_P + 1:
            continue
        newest = T is done[-1]
        ar = (SUB + (TXT - SUB) * (1 - ease.prog(t, T.t1, T.t1 + SETTLE)) if newest else SUB) * a
        mtx(d, (x0 + COLS[0], y), cast.term(T.key), CMP_PX, lv(INK, ar))
        w = mtx(d, (x0 + COLS[1], y), '好呀', CMP_PX, hud.her(0.0, ar))
        mtx(d, (x0 + COLS[1] + w + 6, y), f'{T.cands[0][1]:.2f}', CMP_PX, lv(INK, ar))
        meme, p_ = T.cands[1]
        room = c[2] - 14 - 100 - (x0 + COLS[2]) - 40
        while mw(meme, CMP_PX) > room and len(meme) > 2:
            meme = meme[:-2] + '…'
        w = mtx(d, (x0 + COLS[2], y), meme, CMP_PX, lv(INK, ar))
        mtx(d, (x0 + COLS[2] + w + 6, y), f'{p_:.2f}', CMP_PX, lv(INK, ar))
        if t >= T.write:
            s = f'+{T.file}.txt'
            mtx(d, (c[2] - 14 - mw(s, CMP_PX), y + GD.drop(t, T.write, -5, 0.1)), s, CMP_PX, lv(INK, ar))
    d.rectangle((c[0] + 1, c[1] + 2, c[2] - 1, first - 3), fill=BG)
    for lab, col in zip(('model', 'p(她的 好呀)', 'p(它自己的口头禅)', 'memory'), COLS):
        x = x0 + col if col is not None else c[2] - 14 - mw(lab, 11)
        mtx(d, (x, y0), lab, 11, lv(INK, FAINT * a))
TREE_PX, TREE_P = (22, 30)
INDENT, CNT_X = (46, 250)

def _tree_xy(c, i):
    return (c[0] + 14 + GD.DEPTH[i] * INDENT, c[1] + 16 + i * TREE_P)

def _cmp_tree(d, t, c):
    """d6: the prefix tree over her archived thinking (`tree`-like elbows, the trunk growing as children arrive),
    one row a sung syllable; the counts are hits (X20); the 10th syllable selects love."""
    if t < GD.TREE_AT[0]:
        return
    fb = hud.font(TREE_PX, 'x', True)
    fn = P.font(TREE_PX - 7)
    sel = GD.TREE_AT[9]
    line = lv(INK, 0.45)
    for i, name, n, at in GD.tree_rows(t):
        x, y = _tree_xy(c, i)
        dep = GD.DEPTH[i]
        ym = y + 13
        if dep:
            par = max((j for j in range(i) if GD.DEPTH[j] == dep - 1))
            xv = c[0] + 14 + (dep - 1) * INDENT + 8
            k = ease.ease_out(ease.prog(t, at, at + 0.1))
            yp = _tree_xy(c, par)[1] + TREE_PX + 4
            d.line([(xv, yp), (xv, yp + (ym - yp) * k)], fill=line)
            if k >= 1:
                d.line([(xv, ym), (x - 6, ym)], fill=line)
        is_love = name == 'love'
        colr = hud.her(GD.lit(t, sel, LOVE_AT)) if is_love and t >= sel else INK
        d.text((x, y + GD.drop(t, at, -6, 0.12)), name, font=fb, fill=colr)
        d.text((c[0] + CNT_X, y + 4), f'{n:>3}', font=fn, fill=lv(INK, SUB))
        if is_love and t >= sel:
            u = ease.ease_out(ease.prog(t, sel, sel + 0.12))
            w = d.textlength(name, font=fb)
            d.line([(x - 4, y + TREE_PX + 5), (x - 4 + (w + 8) * u, y + TREE_PX + 5)], fill=hud.her(GD.lit(t, sel, LOVE_AT)), width=2)

def _cmp_love(d, t, c):
    """d7 (D3): love lands on the first note (her blue, a bump, no fade-in) and fills the wide frame; her film-1
    thinking line, faint, lights love, just, you on the three notes; one leader from the tree's love to it."""
    if t < LOVE_AT:
        return
    k = hud.full_u(t) if t >= BACK_AT else 1.0
    h = ease.lerp(70, 170, k)
    right = c[2] - 18
    u_love = GD.lit(t, GD.LOVE_NOTES[0], GD.LOVE_NOTES[1])
    bump = 1.0 + 0.12 * (1 - ease.prog(t, LOVE_AT, LOVE_AT + 0.12))
    big_word(d, 'love', (right, c[1] + 16), int(h), hud.her(u_love), 'ra', bump=bump)
    px = int(round(ease.lerp(13, 22, k)))
    f = P.font(px)
    tw = d.textlength(GD.THOUGHT, font=f)
    tx0, ty = (right - tw, c[1] + int(ease.lerp(150, 236, k)))
    d.text((tx0, ty - 18), GD.THOUGHT_SRC, font=P.font(11), fill=lv(HER_QUIET, 0.9))
    d.text((tx0, ty), GD.THOUGHT, font=f, fill=lv(INK, 0.3))
    for word, note in GD.LIT_WORDS:
        at = GD.LOVE_NOTES[note - 1]
        if t < at:
            continue
        nxt = GD.LOVE_NOTES[note] if note < 3 else GD.LOVE_NOTES[2] + 0.6
        i = GD.THOUGHT.index(' ' + word) + 1 if word != 'love' else GD.THOUGHT.index(word)
        x = tx0 + d.textlength(GD.THOUGHT[:i], font=f)
        u = 0.0 if word == 'love' else GD.lit(t, at, nxt)
        d.text((x, ty + GD.drop(t, at, -4, 0.1)), word, font=P.font(px, 'bold'), fill=hud.her(u))
    lx, ly = _tree_xy(c, 8)
    xw = tx0 + d.textlength(GD.THOUGHT[:GD.THOUGHT.index('love')], font=f)
    xm = xw + d.textlength('love', font=P.font(px, 'bold')) / 2
    pts = [(c[0] + CNT_X + 44, ly + 13), (xm, ly + 13), (xm, ty + px + 4)]
    hud.polyline(d, pts, HER_QUIET, ease.prog(t, LOVE_AT, LOVE_AT + 0.3), 1)

def _forward(d, t, f):
    T = GD.turn_at(t)
    prev = TURNS[T.i - 1] if T.i > 0 else None
    out = 1 - ease.prog(t, T.t0, T.t0 + 0.15)
    if prev is not None and out > 0:
        _body(d, t, f, prev, out, None)
    _body(d, t, f, T, 1.0, T.t0 + 0.05 if T.i > 0 else None)

def _body(d, t, f, T, level, t_in):
    if T.key in UNKNOWN:
        CPN._unknown(d, t, f, T.key, level, t_in, SEGS[T.key])
    else:
        CPN._stack(d, t, f, T.key, level, t_in, segs=SEGS[T.key])

def _run():
    inp = [(T.t0 - 0.02, T.t0 + 0.12) for T in TURNS]
    inp += [(at, at + 0.25) for _c, at in GD.TYPE1 + GD.TYPE2 + GD.TYPE3] + [(a, a + 0.2) for a in GD.DEL_AT]
    inp += [(GD.IME_AT[0], GD.IME_FOLD)]
    return {'input': inp, 'think': [(at, at + len(s) / THINK_CPS + 0.15) for at, s, _T in THINKS], 'trace': [(at, ret[0] if ret else at + len(s) / BO.CODE_CPS + 0.25) for at, s, ret in CODE], 'generate': [(T.read, T.ans + 0.1) for T in TURNS] + [(DOPE_AT - 0.25, DOPE_AT + 0.1)] + [(a, a + 0.12) for a in RANK_AT], 'compare': [(T.ans, T.write + 0.1) for T in TURNS] + [(GD.TREE_AT[0], GD.TREE_AT[-1] + 0.1), (LOVE_AT, GD.LOVE_NOTES[2] + 0.3)], 'forward': sorted((p for v in SEGS.values() for p in v))}
RUN = _run()

def _reads(t):
    her_k = {k: i for i, k in enumerate(tl.HER_FILES)}
    Pl = hud.Pulse(t)
    for T in TURNS:
        if t >= T.read:
            n = len(hud.strip_files(T.read + 0.01))
            for k in range(n + 1):
                Pl.hit(k if k < n else 'archive', T.read + 0.035 * k, 0.12)
    for ch, at in GD.TYPE2:
        if ch in '一直':
            Pl.hit(her_k['last_msg'], at, 0.3)
    for at in GD.TREE_AT:
        Pl.hit('archive', at, 0.14)
    Pl.hit('archive', LOVE_AT, 0.4)
    return Pl.out

def _status(t):
    T = GD.turn_at(t)
    s = tl.sim(t)
    st = {'compare': (f'sim(her) {s}' if s else '', True), 'forward': (speed.label(T.key), False)}
    if t < SCROLL_AT and T.key in THINK_NOTE:
        st['think'] = (THINK_NOTE[T.key], False)
    return st

def _body_fn(c, img, d):
    t = c.t
    L, lev = layout(t)
    r = CPN.right(t)
    _cmdline(d, t, r, img)
    hits = _reads(t)
    st = _status(t)
    relay = t < SCROLL_AT
    w = lead_w(t)
    for name in ('input', 'think', 'trace', 'generate', 'compare', 'forward'):
        rect = L[name]
        level = lev.get(name, 1.0)
        if level <= 0.01 or rect[3] - rect[1] < 4:
            continue
        d.rectangle(rect, fill=BG)
        with panes.Clip(img, rect) as dd:
            if name == 'input':
                if t < SCROLL_AT + 0.2:
                    gone = ease.prog(t, SCROLL_AT, SCROLL_AT + 0.2)
                    _chips_at(dd, t, rect, GC.SEE_COMMITS, GC.SEE_SEND, 1 - gone)
                    _press(dd, t, rect)
                if t >= SCROLL_AT:
                    _stdin(dd, t, rect, big_u(t))
                    _ime(dd, t, rect)
                    _ghost(dd, t, rect)
            elif name == 'think':
                _think(dd, t, rect)
            elif name == 'trace':
                _trace(dd, t, rect)
            elif name == 'generate':
                _gen_pile(dd, t, rect)
                _gen_rank(dd, t, rect)
            elif name == 'compare':
                _cmp_log(dd, t, rect)
                _cmp_tree(dd, t, rect)
                _cmp_love(dd, t, rect)
            else:
                _forward(dd, t, rect)
        lead.shade(img, rect, 1 - w[name])
        status, her = st.get(name, ('', False))
        run = panes.run_k(t, RUN_RELAY.get(name, ()), RUN_EASE) if relay else panes.run_k(t, RUN[name]) * w[name]
        panes.box(d, rect, name, t, run, level, status, her)
    CPN._memory(d, t, L['memory'], hits)
    lead.shade(img, L['memory'], 1 - w['memory'])
    panes.box(d, L['memory'], 'mem', t, 0.0 if relay else min(1.0, 3 * max(hits.values(), default=0.0)) * w['memory'])
SHOTS = [('d1_relay', ROT_AT[0], W(32, 0)), ('d2_type', W(32, 0), W(35, 0)), ('d3_ime', W(35, 0), DOPE_AT), ('d4_dope', DOPE_AT, DOPE_END), ('d5_stay', DOPE_END, SHRINK), ('d6_prefix', SHRINK, LOVE_AT), ('d7_love', LOVE_AT, T1)]
dsh_layer = DP.dsh_layer

def register(film):
    hold = GD.prev_shot(film)
    if hold is not None:
        film.add('d0_hold', T0, ROT_AT[0], lambda c: hold.fn(c, **hold.params), chapter=tl.chapter(T0))
    for name, a, b in SHOTS:
        add(film, name, a, b, _body_fn)
    film.character = dsh_layer(film, film.character, 'ui/pane_open_d', T0, T1)
    for T in TURNS:
        hud.LIVE.append((T.ans, T.write))
    hud.LIVE.append((GD.TREE_AT[9], LOVE_AT))
    for k in range(3):
        hud.LIVE.append((GD.LOVE_NOTES[k], GD.LOVE_NOTES[k + 1] if k < 2 else GD.LOVE_NOTES[2] + 0.6))
    full_frame(LOVE_AT, BACK_AT, 0.3, 0.38)
    for t0, side in [(TURNS[0].read, 'left'), (ROT_STOP, 'both'), (W(32, 0), 'left'), (LOVE_AT - GD.LEAD_EARLY, 'both')]:
        film.set_lead(t0, side)
