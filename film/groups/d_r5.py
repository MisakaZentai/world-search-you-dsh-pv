"""r5 batch 3 (REVISE_R4_20261004.md §3.5-3.6, DECISIONS D34): the forgotten word as a coy message, and the
dual of film 1's love.tex. Switch: DSH_D=r5. Started as a copy of groups/d_lead.py (r4); everything before
151.55 (SCROLL_AT, frame 3637 and earlier) is r4's code path, unchanged (137.0-151.54 checked lossless, 349 frames
identical to DSH_D=lead). Samples: sample_r5/d/. From 151.55:

  stage     the dsh window is the stage: you type to her. 151.55 it grows to the left over the terminal
            (STAGE_X0) and its page is seen at 2x (browser zoom: shot at deviceScaleFactor 2, ui/pane_d_r5/);
            171.90 (bar 99) it goes back to its place and steps back. Your text in its composer: one character
            a sung syllable, a drop with a squash on landing; the IME's candidate window (笨蛋 / 傻瓜 / 小猪), its
            highlighted block hopping; a backspace burst on 16ths; the caret blinking on the beat where you are
            stuck (157.38, 171.72); in the staccato (166.71-171.90) the text squashes on every kick and snare.
            Page: ui/pages/d_r5.py, timing below (the page reads it, the two sides never disagree).
  left      the machine helping badly, a narrow column (input: your keys as it reads them, deleted ones struck;
            trace; generate: its guess board p(next | stdin) per key, then dope picked and stretched an o per
            sung onset (beatmap vocal), each o hopping, struck by you on your next key and shaking; forward).
  love.tex  171.90 the left becomes film 1's love.tex (sec_outro.shot_algebra: 22 px Segoe UI Symbol, 60 px
            between lines, typed at 45 characters a second, the conclusion at 34 px), its dual: from the word
            you could not say to love; the prefix tree is the search, its pruned branches get −∞ (the same −∞
            as line 3). = love grows an o a sung onset into the big word; ∴ you = love on the third onset.
            177.48 the terminal fills the frame (r4); 179.26-179.64 the shade lifts (r4).

r4's notes follow (batch 3).

Batch 3 (sample_batch3/README.md): group D, one pane leads a beat over the whole group (137.31-179.64).
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
             and a ghost after 大); "如果你能 / 一直这样子…… / 我就能……"; it offers 喜欢 · 好感 · 依赖 on the hum.
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
                d.line([(x - 2, ym), (x - 2 + (w + 4) * k, ym)], fill=lv(INK, 0.8), width=1)
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
            d.line([(x - 4, y + TREE_PX + 5), (x - 4 + (w + 8) * u, y + TREE_PX + 5)], fill=hud.her(GD.lit(t, sel, LOVE_AT)), width=1)

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

def _body_r4(c, img, d):
    """r4's shot body (d_lead), used unchanged before R5_AT."""
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
import random
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
import beatmap as BM
from tuikit.uipane import PaneFrames
FPS = P.FPS
R5_AT = SCROLL_AT
N_R5 = math.ceil(R5_AT * FPS - 1e-09)
LAYOUT_E = LOVE_AT + 0.4
N_E = int(round(LAYOUT_E * FPS))
_T1 = [at for _c, at in GD.TYPE1]
IME1_OPEN, IME1_HL, IME1_PICK = (_T1[5], _T1[6], _T1[7])
AH_AT = BM.events('beat', IME1_PICK + 0.3, IME1_PICK + 0.9)[0]
TILDE_AT = BM.events('eighth', AH_AT + 0.05, AH_AT + 0.5)[0]
DEL_BURST = BM.events('sixteenth', GD.DEL_AT[0] - 0.03, GD.DEL_AT[0] + 0.7)[:6]
STUCK1 = GD.STALL
RETYPE = GD.IME_AT[:2]
IME2 = GD.IME_AT[2:]
IME_FOLD = GD.IME_FOLD
DOPE_OS = BM.events('vocal', DOPE_AT - 0.05, GD.DOPE_END - 0.1)
STRIKE_AT = GD.TYPE2[0][1]
ELLIPSIS2 = BM.events('snare', GD.TYPE2[8][1] + 0.05, GD.TYPE2[8][1] + 0.4)[0]
STAC = (QUIET_AT, SHRINK)
KICKS = BM.events('kick', *STAC)
SNARES = BM.events('snare', *STAC)
LOVE_OS = BM.events('vocal', LOVE_AT - 0.05, LOVE_AT + 1.3)[:3]
TEX_AT = [GD.TREE_AT[0], GD.TREE_AT[2], GD.TREE_AT[5], LOVE_OS[0], LOVE_OS[2]]
PRUNE1, PRUNE2 = (GD.TREE_AT[5], GD.TREE_AT[8])
IME_WORDS = ['笨蛋', '傻瓜', '小猪']

def _script():
    """Your keys in dsh's composer: (t, op, text); op type | del | nl (a new line, Shift+Enter)."""
    ops = [(at, 'type', ch) for ch, at in zip('你就是个大', _T1[:5])]
    ops += [(IME1_PICK, 'type', '笨蛋'), (AH_AT, 'type', '啊'), (TILDE_AT, 'type', '～')]
    ops += [(at, 'del', '') for at in DEL_BURST]
    ops += [(RETYPE[0], 'type', '个'), (RETYPE[1], 'type', '大')]
    ops += [(STRIKE_AT, 'nl', '')] + [(at, 'type', ch) for ch, at in GD.TYPE2[:9]] + [(ELLIPSIS2, 'type', '……')]
    ops += [(GD.TYPE3[0][1], 'nl', '')] + [(at, 'type', ch) for ch, at in GD.TYPE3[:3]] + [(HUM, 'type', '……')]
    return ops
SCRIPT = _script()

def _units():
    """Every character you type: dict(line, ch, t_in, t_out); t_out is when a backspace takes it (inf if never).
    An IME commit (笨蛋) is two characters landing together; a backspace takes one character."""
    lines, out = ([[]], [])
    for at, op, s in SCRIPT:
        if op == 'nl':
            lines.append([])
        elif op == 'type':
            chars = [s] if s == '……' else list(s)
            for ch in chars:
                u = dict(line=len(lines) - 1, ch=ch, t_in=at, t_out=math.inf)
                lines[-1].append(u)
                out.append(u)
        else:
            lines[-1].pop()['t_out'] = at
    return out
UNITS = _units()
KEY_TIMES = sorted({at for at, op, _s in SCRIPT})

def ime_state(t):
    """The IME's candidate window at t: None, or (highlight index, time it moved there, picked)."""
    if IME1_OPEN <= t < IME1_PICK + 0.12:
        if t < IME1_HL:
            return (0, IME1_OPEN, False)
        if t < IME1_PICK:
            return (1, IME1_HL, False)
        return (0, IME1_PICK, True)
    if IME2[0] <= t < IME_FOLD:
        k = max((i for i, at in enumerate(IME2) if at <= t))
        return (k % 3, IME2[k], False)
    return None

def dope_word(t):
    """(the stretched word, number of o's, the onset of the newest o) on the guess board from DOPE_AT."""
    n = max(1, sum((1 for a in DOPE_OS if a <= t)))
    return ('d' + 'o' * n + 'pe', n, DOPE_OS[n - 1])

def stuck(t):
    """Where the caret stops and blinks on the beat: 嗯 (157.38 until you type again), the long vowel, the hum."""
    return STUCK1 <= t < RETYPE[0] or DOPE_AT <= t < STRIKE_AT or t >= HUM

def last_key(t):
    ts = [a for a in KEY_TIMES if a <= t]
    return ts[-1] if ts else -1.0

def caret_on(t):
    """Solid for 0.3 s after a key; otherwise on for the first half of each beat (it blinks on the beat)."""
    if t - last_key(t) < 0.3 and (not stuck(t)):
        return True
    return tl.C.beat_of(t) % 1.0 < 0.5

def bounce(u):
    """A character landing u s ago: (dy px, sx, sy) in its own size units of 16 px; it drops 9 px, squashes
    on impact and springs back (0.3 s). None before it lands."""
    if u < 0:
        return None
    if u < 0.05:
        return (-9 * (1 - u / 0.05) ** 2, 1.0, 1.0)
    v = u - 0.05
    if v > 0.3:
        return (0.0, 1.0, 1.0)
    sq = 0.24 * math.exp(-v / 0.055) * math.cos(2 * math.pi * v / 0.17)
    dy = -2.2 * math.exp(-v / 0.07) * max(0.0, math.sin(2 * math.pi * v / 0.2))
    return (dy, 1 + 0.55 * sq, 1 - sq)

def drum_squash(t):
    """In the staccato (166.71-171.90) the text squashes on every kick and harder on the snare: (sx, sy)."""
    if not STAC[0] <= t < STAC[1] + 0.3:
        return (1.0, 1.0)
    k = BM.flash(t, KICKS, 0.05) if t >= KICKS[0] else 0.0
    s = BM.flash(t, SNARES, 0.07) if SNARES and t >= SNARES[0] else 0.0
    q = 0.07 * k + 0.13 * s
    return (1 + 0.6 * q, 1 - q)

def hop(u, dur=0.2):
    """0..1..0 over dur after an event (a hop up and back down)."""
    if u < 0 or u > dur:
        return 0.0
    return math.sin(math.pi * u / dur)
R_WIN = P.rect('right')
R_PANE = P.rect('pane')
PAGE_W, PAGE_H = (R_PANE[2] - R_PANE[0], R_PANE[3] - R_PANE[1])
STAGE_X0 = 442
STAGE_IN = 0.36
SHOT_SCALE = 2
R5_DIR = 'ui/pane_d_r5'

def stage_s(t):
    """0 = the window in its place, 1 = the stage (grown to STAGE_X0, its page at 2x)."""
    return ease.ease_io(ease.prog(t, R5_AT, R5_AT + STAGE_IN)) * (1 - ease.ease_io(ease.prog(t, SHRINK, SHRINK + STAGE_IN)))

def win_rect(t):
    s = stage_s(t)
    return (ease.lerp(R_WIN[0], STAGE_X0, s), R_WIN[1], R_WIN[2], R_WIN[3])

def page_crop(t):
    """(the window's inner rect, the page region in css px it shows). One zoom for both axes: the page is held at
    its bottom right (the composer) and seen at z = 1..2."""
    s = stage_s(t)
    x0 = win_rect(t)[0] + 1
    inner = (x0, R_PANE[1], R_PANE[2], R_PANE[3])
    z = ease.lerp(1.0, float(SHOT_SCALE), s)
    w, h = ((inner[2] - inner[0]) / z, PAGE_H / z)
    return (inner, (PAGE_W - w, PAGE_H - h, PAGE_W, PAGE_H))

def pane_r(t):
    """Right edge of the left panes: the terminal's (r4), or short of the grown window."""
    return ease.lerp(CPN.right(t), STAGE_X0 - 10, stage_s(t))
NAMES_R5 = ('input', 'think', 'trace', 'generate', 'compare', 'forward', 'love', 'memory', 'dsh')
LEAD_R5 = sorted([e for e in LEAD if e[0] < R5_AT] + [(DOPE_AT, 'generate'), (QUIET_AT, 'dsh'), (SHRINK, 'love')])
WIN_UP = LOVE_AT - GD.LEAD_EARLY

def lead_r5(t):
    w = lead.weights(t, LEAD_R5, NAMES_R5)
    rel = ease.ease_io(ease.prog(t, *RELEASE))
    if rel > 0:
        w = {n: ease.lerp(w[n], 1.0, rel) for n in NAMES_R5}
    return w

def win_shade(t):
    """0..1: the window as the support side (D11: lead.support_rgb, applied to the window layer itself: it
    overlaps the terminal on the stage, so the film's fixed LEAD regions cannot dim it)."""
    return (1 - lead_r5(t)['dsh']) * (1 - ease.smooth(ease.prog(t, WIN_UP, WIN_UP + lead.EASE)))

def layout_r5(t):
    """Rects and levels: r4's relay layout at 151.55 -> the narrow column (A) -> love.tex (B, from 171.90)."""
    r = pane_r(t)
    u_in = ease.ease_io(ease.prog(t, R5_AT, R5_AT + STAGE_IN))
    u_out = ease.ease_io(ease.prog(t, SHRINK, SHRINK + STAGE_IN))
    LR = {'input': (COL, 88, SPLIT, 146), 'think': (SPLIT + 8, 88, r, 146), 'trace': (COL, 154, r, 222), 'generate': (COL, 230, r, PILE_H[0]), 'compare': (COL, PILE_H[1], r, 528), 'forward': (COL, 536, r, 598), 'love': (COL, 598, r, 598)}
    A = {'input': (COL, 88, r, 160), 'think': (r, 88, r, 88), 'trace': (COL, 168, r, 232), 'generate': (COL, 240, r, 528), 'compare': (COL, 528, r, 528), 'forward': (COL, 536, r, 598), 'love': (COL, 598, r, 598)}
    B = {'input': (COL, 88, r, 88), 'think': (r, 88, r, 88), 'trace': (COL, 88, r, 88), 'generate': (COL, 88, r, 88), 'compare': (COL, 88, r, 88), 'forward': (COL, 598, r, 598), 'love': (COL, 88, r, 598)}
    V = {'input': (1, 1, 0), 'think': (1, 0, 0), 'trace': (1, 1, 0), 'generate': (1, 1, 0), 'compare': (1, 0, 0), 'forward': (1, 1, 0), 'love': (0, 0, 1)}
    out, lev = ({'memory': MEM}, {})
    for k in LR:
        out[k] = panes.lerp_rect(panes.lerp_rect(LR[k], A[k], u_in), B[k], u_out)
        v = V[k]
        lev[k] = ease.lerp(ease.lerp(v[0], v[1], u_in), v[2], u_out)
    return (out, lev)
KEY_PX, KEY_P = (15, 17)

def _keys(d, t, r):
    """Every key you typed, in the order it reads them (R4: what you delete stays, struck; nothing is replaced)."""
    shown = [u for u in UNITS if u['t_in'] <= t]
    if not shown:
        return
    x0, y = (r[0] + 12, r[1] + 11)
    for li in range(3):
        row = [u for u in shown if u['line'] == li]
        x = x0
        for u in row:
            gone = t >= u['t_out']
            w = hud.width(u['ch'], KEY_PX)
            yy = y + li * KEY_P + GD.drop(t, u['t_in'], -5, 0.1)
            hud.tx(d, (x, yy), u['ch'], KEY_PX, lv(INK, FAINT if gone else TXT))
            if gone:
                k = ease.ease_out(ease.prog(t, u['t_out'], u['t_out'] + 0.06))
                ym = yy + KEY_PX * 0.62
                d.line([(x - 1, ym), (x - 1 + (w + 2) * k, ym)], fill=lv(INK, 0.8))
            x += w

def _code_r5():
    out = [e for e in CODE if e[0] < R5_AT]
    out += [(GD.TYPE1[0][1], 'stdin.read()', None), (GD.TYPE1[1][1], 'stdin.on_key(complete)', None), (IME1_OPEN, 'ime.suggest("大")', (IME1_PICK, '笨蛋')), (DEL_BURST[0], 'stdin.backspace()', (DEL_BURST[-1], '×6')), (IME2[0], 'ime.suggest("大")', (IME_FOLD, '没有选')), (DOPE_AT - 0.25, 'complete(stdin)', (DOPE_AT, f'dope {GD.DOPE_CANDS[0][1]:.2f}')), (STRIKE_AT, 'complete.reject("dooooope")', (STRIKE_AT + 0.1, 'ok')), (HUM - 0.25, 'complete(stdin)', (HUM, ' · '.join(GD.COMPLETE)))]
    return sorted(out, key=lambda e: e[0])
CODE_R5 = _code_r5()

def _trace_r5(d, t, r):
    shown = [(at, s, ret) for at, s, ret in CODE_R5 if at <= t]
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
            mtx(d, (r[0] + 10 + w + 10, y), '→ ' + ret[1], 14, lv(INK, 0.7 * a * u), bold=True)
_RANK_PREFIX = {'你': [('是', 0.34), ('好', 0.17), ('们', 0.08), ('呀', 0.05)], '你就': [('是', 0.71), ('会', 0.09), ('不', 0.05), ('要', 0.03)], '你就是': [('个', 0.29), ('我', 0.18), ('最', 0.11), ('她', 0.06)], '你就是个': [('大', 0.26), ('笨蛋', 0.19), ('好人', 0.12), ('小', 0.07)], '你就是个大': [('笨蛋', 0.43), ('坏蛋', 0.14), ('可爱', 0.09), ('傻瓜', 0.06)], '你就是个大笨': [('蛋', 0.93), ('拙', 0.02), ('鸟', 0.01), ('手', 0.01)], '你就是个大笨蛋': [('啊', 0.36), ('。', 0.22), ('！', 0.15), ('呢', 0.08)], '你就是个大笨蛋啊': [('～', 0.31), ('。', 0.27), ('！', 0.18), ('哈', 0.06)], '你就是个大笨蛋啊～': [('。', 0.38), ('！', 0.22), ('哈', 0.1), ('嘿', 0.05)], '如': [('果', 0.88), ('此', 0.05), ('今', 0.02), ('何', 0.01)], '如果': [('你', 0.41), ('我', 0.22), ('她', 0.09), ('能', 0.05)], '如果你': [('能', 0.32), ('愿意', 0.14), ('想', 0.09), ('也', 0.06)], '如果你能': [('一直', 0.27), ('陪', 0.18), ('记住', 0.11), ('回来', 0.07)], '如果你能一': [('直', 0.91), ('起', 0.03), ('样', 0.02), ('天', 0.01)], '如果你能一直': [('这样', 0.34), ('陪', 0.17), ('在', 0.14), ('记', 0.06)], '如果你能一直这': [('样', 0.95), ('么', 0.03), ('里', 0.01), ('个', 0.01)], '如果你能一直这样': [('的', 0.31), ('子', 0.24), ('下去', 0.17), ('就', 0.08)], '如果你能一直这样子': [('就', 0.36), ('……', 0.19), ('下去', 0.12), ('。', 0.07)], '如果你能一直这样子……': [('我', 0.44), ('就', 0.19), ('那', 0.11), ('。', 0.06)], '我': [('就', 0.38), ('会', 0.21), ('也', 0.12), ('想', 0.07)], '我就': [('能', 0.29), ('会', 0.23), ('不', 0.11), ('好', 0.08)], '我就能': [('……', 0.26), ('一直', 0.18), ('开心', 0.12), ('好', 0.07)], '我就能……': [(w, p_) for w, p_ in zip(GD.COMPLETE + ['在一起'], (0.23, 0.17, 0.12, 0.08))]}
_RANK_IME = [[('笨蛋', 0.41), ('傻瓜', 0.12), ('小猪', 0.07), ('dope', 0.06)], [('笨蛋', 0.37), ('傻瓜', 0.11), ('dope', 0.08), ('小猪', 0.06)], [('笨蛋', 0.33), ('dope', 0.12), ('傻瓜', 0.1), ('小猪', 0.05)], [('笨蛋', 0.27), ('dope', 0.18), ('傻瓜', 0.09), ('小猪', 0.05)], [('dope', 0.25), ('笨蛋', 0.24), ('傻瓜', 0.08), ('小猪', 0.04)], [('dope', 0.33), ('笨蛋', 0.21), ('傻瓜', 0.07), ('小猪', 0.04)], [('dope', 0.41), ('笨蛋', 0.19), ('傻瓜', 0.07), ('小猪', 0.03)]]
_RANK_DOPE = [('dope', GD.DOPE_CANDS[0][1]), ('笨蛋', 0.18), ('傻瓜', 0.07), ('小猪', 0.03)]
RANK_T = 'p( next | stdin )'

def _line_text(t, li):
    return ''.join((u['ch'] for u in UNITS if u['line'] == li and u['t_in'] <= t < u['t_out']))

def _rank_events_r5():
    ev = []
    for at in sorted({a for a, op, _s in SCRIPT if op in ('type', 'del')} | {u['t_out'] for u in UNITS if u['t_out'] < math.inf}):
        if IME2[0] <= at < STRIKE_AT or DEL_BURST[0] <= at < DEL_BURST[-1]:
            continue
        t_ = at + 0.0001
        li = max((u['line'] for u in UNITS if u['t_in'] <= t_))
        key = _line_text(t_, li)
        if key in _RANK_PREFIX:
            ev.append((at, RANK_T, _RANK_PREFIX[key]))
    for k, at in enumerate(IME2):
        ev.append((at, f'p( next | stdin, 没选 {k + 1} 个 )', _RANK_IME[k]))
    ev.append((DOPE_AT, f'p( next | stdin, 没选 {len(IME2)} 个 )', _RANK_DOPE))
    return sorted(ev, key=lambda e: e[0])
RANK_EV_R5 = _rank_events_r5()
RANK_AT_R5 = [e[0] for e in RANK_EV_R5]
BOARD_ROWS, BOARD_RP = (4, 26)
OUT_PX = 46

def _board(d, t, g):
    """The stand-in's guess board (an ink slab, r4's look), the width of the narrow column."""
    t0 = RANK_AT_R5[0]
    if t < t0:
        return None
    k = max((i for i, at in enumerate(RANK_AT_R5) if at <= t))
    at, title, cur = RANK_EV_R5[k]
    prev = RANK_EV_R5[k - 1][2] if k > 0 else []
    u = ease.ease_out(ease.prog(t, at, at + 0.12))
    picked = DOPE_AT <= t < STRIKE_AT
    x0, y0 = (g[0] + 10, g[1] + 14)
    pw = g[2] - g[0] - 20
    full = 24 + BOARD_ROWS * BOARD_RP + 8
    h = int(full * ease.ease_out(ease.prog(t, t0, t0 + 0.12)))
    if h <= 0:
        return None
    y1 = y0 + full
    ya = y1 - h
    d.rectangle((x0, ya, x0 + pw, y1), fill=SLAB)
    if h < 24:
        return y1
    on = lambda a: glyph.level(BG, a, SLAB)
    mtx(d, (x0 + 10, ya + 7), title, 12, on(0.75))
    bar_x, bar_w = (pw - 128, 70)
    words = [w for w, _p in prev] + [w for w, _p in cur if w not in dict(prev)]
    pc, pp = (dict(cur), dict(prev))
    ic = {w: i for i, (w, _p) in enumerate(cur)}
    ip = {w: i for i, (w, _p) in enumerate(prev)}
    for w in words:
        if w in ip and w in ic:
            row, vis = (ease.lerp(ip[w], ic[w], u), 1.0)
        elif w in ic:
            row, vis = (ic[w], u)
        else:
            row, vis = (ip[w], 1 - u)
        if vis <= 0.02:
            continue
        p_ = ease.lerp(pp.get(w, 0.0), pc.get(w, 0.0), u)
        ry = ya + 24 + row * BOARD_RP
        top = ic.get(w) == 0
        if picked and top:
            d.rectangle((x0 + 2, ry + 1, x0 + pw - 2, ry + BOARD_RP - 2), fill=BG)
            fg = SLAB
            d.polygon([(x0 + 8, ry + 8), (x0 + 15, ry + 13), (x0 + 8, ry + 18)], fill=fg)
        else:
            fg = on((0.9 if top else 0.6) * vis)
        hud.tx(d, (x0 + 22, ry + 4), w, 16, fg, bold=top)
        bw = max(2, bar_w * p_)
        d.rectangle((x0 + bar_x, ry + 9, x0 + bar_x + bw, ry + 17), fill=fg if picked and top else on((0.7 if top else 0.45) * vis))
        d.text((x0 + pw - 10, ry + 6), f'{p_:.2f}', font=P.font(13), fill=fg, anchor='ra')
    return y1

@lru_cache(maxsize=8)
def _mono_bold(px):
    return P.font(px, 'bold')

def _out_word(d, t, g, y_top):
    """dope, its own word, out under the board: an o more on every sung onset of the long vowel, each o hopping;
    your next key strikes it (165.98) and it shakes; it stays, struck (nothing is replaced)."""
    if t < DOPE_AT:
        return
    x0 = g[0] + 12
    mtx(d, (x0, y_top), 'out', 11, lv(INK, FAINT))
    word, n, _new = dope_word(t)
    f = _mono_bold(OUT_PX)
    adv = f.getlength('o')
    struck = t >= STRIKE_AT
    sv = t - STRIKE_AT - 0.08
    shake = 8 * math.exp(-sv / 0.13) * math.sin(2 * math.pi * 6.0 * sv) if sv > 0 else 0.0
    a = TXT if not struck else ease.lerp(TXT, SUB, ease.prog(t, STRIKE_AT + 0.08, STRIKE_AT + 0.4))
    col = lv(INK, a)
    y = y_top + 16 + GD.drop(t, DOPE_AT, -8, 0.14)
    x = x0 + shake
    xs = [('d', x, 0.0)]
    cx = x + f.getlength('d')
    for j in range(n):
        born = DOPE_OS[j]
        wgrow = 1.0 if j == 0 else ease.ease_out(ease.prog(t, born, born + 0.08))
        dy = -10.0 * hop(t - born, 0.2)
        for kk in range(j + 1, n):
            dy -= 4.0 * hop(t - DOPE_OS[kk] - 0.03 * j, 0.2)
        if wgrow > 0.6:
            xs.append(('o', cx - adv * (1 - wgrow) * 0.5, dy))
        cx += adv * wgrow
    xs += [('p', cx, 0.0), ('e', cx + f.getlength('p'), 0.0)]
    for ch, xx, dy in xs:
        d.text((xx, y + dy), ch, font=f, fill=col)
    x_end = cx + f.getlength('pe')
    if struck:
        k = ease.ease_out(ease.prog(t, STRIKE_AT, STRIKE_AT + 0.08))
        ym = y + OUT_PX * 0.55
        d.line([(x - 4, ym), (x - 4 + (x_end - x + 8) * k, ym)], fill=lv(INK, TXT), width=1)

def _gen_r5(d, t, g):
    if t < R5_AT + STAGE_IN + 0.05:
        _gen_pile(d, t, g)
    y1 = _board(d, t, g)
    if y1 is not None:
        _out_word(d, t, g, y1 + 18)

def _segs_r5():
    s = [(a - 0.1, a) for a in KEY_TIMES] + [(a - 0.1, a) for a in RANK_AT_R5]
    s += [(DOPE_AT - 0.25, DOPE_AT), (HUM - 0.25, HUM)]
    return sorted(set(SEGS['longcat'] + s))
SEGS_R5 = _segs_r5()
FWD_DY = 8

def split_label(s, maxw, size=11):
    """A ' · '-separated label as lines no wider than maxw (greedy: as much as fits on each line)."""
    lines, cur = ([], '')
    for part in s.split(' · '):
        cand = part if not cur else cur + ' · ' + part
        if cur and mw(cand, size) > maxw:
            lines.append(cur)
            cur = part
        else:
            cur = cand
    return lines + [cur]

def _forward_r5(d, t, f):
    """D36: LongCat-2.0's real body (it was the sealed box). The pane narrows to 322 px on the stage (151.55-151.91):
    its label (419 px at 11 px) reflows into two lines once it no longer fits, and the rows ease down 8 px as the
    pane narrows, arriving exactly when it reflows (back up as it widens at 171.90)."""
    left = BO.ARCH['longcat']['left']
    need = mw(left, 11) + 20
    wide = CPN.right(R5_AT) - COL
    fw = f[2] - f[0]
    lines = split_label(left, fw - 20) if fw < need else None
    k = ease.clamp((wide - fw) / max(1.0, wide - need))
    CPN._stack(d, t, f, 'longcat', 1.0, None, segs=SEGS_R5, label_lines=lines, row_dy=FWD_DY * k)
F_SYM = 'C:/Windows/Fonts/seguisym.ttf'
TEX_PX, TEX_CONC, TEX_PITCH, TEX_CPS, TEX_SETTLE = (22, 34, 60, 45, 0.12)
TEX_X, TEX_Y = (26, 34)
SCR = '!<>-_\\/[]{}=+*^?#%$&@01|~:;'
CTX_ZH = ''.join((ch for ch, _a in GD.TYPE2[:9])) + '……' + ''.join((ch for ch, _a in GD.TYPE3[:3]))
TEX = [[('word = argmax  P( w | ', 'ink'), (CTX_ZH, 'zh'), (' ___ )', 'ink')], [('= argmax  softmax( q_you · K_her^T / √d )', 'ink')], [('= argmax  softmax( [ −∞, −∞, …, −∞, s_', 'ink'), ('love', 'her'), (' ] )', 'ink')], [('= ', 'ink')], [('∴  you = ', 'ink'), ('love', 'her')]]
TEX_NOTE = 'K_her = archive/thinking'
NOTE_PX = 14

@lru_cache(maxsize=32)
def _sym(px):
    return ImageFont.truetype(F_SYM, px)

def _seg_font(kind, px):
    return hud.font(px, '中') if kind == 'zh' else _sym(px)

@lru_cache(maxsize=16)
def _tex_chars(i, px):
    """[(ch, dx, kind)] of line i: dx from the line's start (prefix widths, so kerning is kept)."""
    out, x = ([], 0.0)
    for text, kind in TEX[i]:
        f = _seg_font(kind, px)
        for j, ch in enumerate(text):
            out.append((ch, x + f.getlength(text[:j]), kind))
        x += f.getlength(text)
    return (tuple(out), x)

def _eq_dx():
    return _sym(TEX_PX).getlength('word ')

def _tex_line(d, t, i, x, y, px, t0, her_u=0.0, level=1.0):
    """Line i typed from t0 (45 a second, each character scrambling 0.12 s, film 1). Returns its end x."""
    chars, w = _tex_chars(i, px)
    if t < t0:
        return x
    for k, (ch, dx, kind) in enumerate(chars):
        ti = t0 + k / TEX_CPS
        if t < ti:
            break
        f = _seg_font(kind, px)
        shown = ch
        if ch != ' ' and kind != 'zh' and (t < ti + TEX_SETTLE):
            shown = random.Random(i * 7919 + k * 131 + ease.tick(t, 60)).choice(SCR)
        col = hud.her(her_u, level) if kind == 'her' and shown == ch else lv(INK, TXT * level)
        d.text((x + dx, y), shown, font=f, fill=col)
    return x + w

def _tex_typed(t, i, t0):
    chars, _w = _tex_chars(i, TEX_PX)
    return t >= t0 + (len(chars) - 1) / TEX_CPS + TEX_SETTLE
TR_PX, TR_P, TR_IND, TR_W = (22, 29, 34, 350)
TR_CNT, TR_INF = (214, 262)
TR_TOP = 206
PRUNED = {1: PRUNE1, 2: PRUNE1, 3: PRUNE1, 5: PRUNE2, 6: PRUNE2}

def _tree_xy(c, i):
    return (c[2] - TR_W + GD.DEPTH[i] * TR_IND, c[1] + TR_TOP + i * TR_P)

def _tree_r5(d, t, c, level=1.0):
    if t < GD.TREE_AT[0]:
        return
    x_cap, y_cap = (c[2] - TR_W, c[1] + TR_TOP - 18)
    mtx(d, (x_cap, y_cap), 'tree = archive.think.prefix("l")', 11, lv(INK, FAINT * level))
    fb = hud.font(TR_PX, 'x', True)
    fn = P.font(13)
    sel = GD.TREE_AT[9]
    line = lv(INK, 0.45 * level)
    for i, name, n, at in GD.tree_rows(t):
        x, y = _tree_xy(c, i)
        dep = GD.DEPTH[i]
        ym = y + 13
        if dep:
            par = max((j for j in range(i) if GD.DEPTH[j] == dep - 1))
            xv = c[2] - TR_W + (dep - 1) * TR_IND + 7
            k = ease.ease_out(ease.prog(t, at, at + 0.1))
            yp = _tree_xy(c, par)[1] + TR_PX + 3
            d.line([(xv, yp), (xv, yp + (ym - yp) * k)], fill=line)
            if k >= 1:
                d.line([(xv, ym), (x - 5, ym)], fill=line)
        cut = i in PRUNED and t >= PRUNED[i]
        is_love = name == 'love'
        if is_love and t >= sel:
            colr = hud.her(GD.lit(t, sel, LOVE_AT), level)
        else:
            a = ease.lerp(TXT, FAINT, ease.prog(t, PRUNED[i], PRUNED[i] + 0.1)) if cut else TXT
            colr = lv(INK, a * level)
        d.text((x, y + GD.drop(t, at, -6, 0.12)), name, font=fb, fill=colr)
        d.text((c[2] - TR_W + TR_CNT, y + 5), f'{n:>3}', font=fn, fill=lv(INK, FAINT * level))
        if cut:
            u = ease.ease_out(ease.prog(t, PRUNED[i], PRUNED[i] + 0.06))
            px = int(round(19 * ease.lerp(1.3, 1.0, u)))
            d.text((c[2] - TR_W + TR_INF, y + 13), '−∞', font=_sym(px), fill=lv(INK, SUB * level), anchor='lm')
        if is_love and t >= sel:
            u = ease.ease_out(ease.prog(t, sel, sel + 0.12))
            w = d.textlength(name, font=fb)
            d.line([(x - 3, y + TR_PX + 4), (x - 3 + (w + 6) * u, y + TR_PX + 4)], fill=hud.her(GD.lit(t, sel, LOVE_AT), level), width=1)
BIG_PX = (22, 110, 142, 172)
BIG_EASE = 0.16
F_BIG = 'C:/Windows/Fonts/segoeuib.ttf'

@lru_cache(maxsize=64)
def _big(px):
    return ImageFont.truetype(F_BIG, px)

def _big_size(t):
    s = BIG_PX[0]
    for k, at in enumerate(LOVE_OS):
        s = ease.lerp(s, BIG_PX[k + 1], ease.ease_out(ease.prog(t, at, at + BIG_EASE)))
    if t >= BACK_AT:
        s *= ease.lerp(0.3, 1.0, hud.full_u(t))
    return s

def _big_love(d, t, x, y_top, level=1.0):
    """love on line 4: lands at 22 px on the first onset, an o more and bigger on each onset (each new o hops)."""
    if t < LOVE_OS[0]:
        return
    px = max(8, int(round(_big_size(t))))
    f = _sym(px) if px <= BIG_PX[0] else _big(px)
    n = sum((1 for a in LOVE_OS if a <= t))
    u_lit = 1.0 if t < LOVE_OS[2] else 1 - ease.prog(t, LOVE_OS[2], LOVE_OS[2] + hud.LIVE_FADE)
    col = hud.her(u_lit, level)
    y = y_top + _sym(TEX_PX).getbbox('l')[1] - f.getbbox('l')[1]
    adv = f.getlength('o')
    cx = x
    d.text((cx, y), 'l', font=f, fill=col)
    cx += f.getlength('l')
    for j in range(n):
        born = LOVE_OS[j]
        wgrow = 1.0 if j == 0 else ease.ease_out(ease.prog(t, born, born + 0.08))
        dy = -0.12 * px * hop(t - born, 0.22) if j > 0 else 0.0
        if wgrow > 0.6:
            d.text((cx - adv * (1 - wgrow) * 0.5, y + dy), 'o', font=f, fill=col)
        cx += adv * wgrow
    d.text((cx, y), 've', font=f, fill=col)

def _love_r5(d, t, c):
    """love.tex: the derivation (film 1's layout, its dual), the tree as its search step, love growing."""
    x, y0 = (c[0] + TEX_X, c[1] + TEX_Y)
    xe = x + _eq_dx()
    ys = [y0 + i * TEX_PITCH for i in range(4)]
    _tex_line(d, t, 0, x, ys[0], TEX_PX, TEX_AT[0])
    _tex_line(d, t, 1, xe, ys[1], TEX_PX, TEX_AT[1])
    if _tex_typed(t, 1, TEX_AT[1]):
        chars, _w = _tex_chars(1, TEX_PX)
        kx = next((dx for ch, dx, _k in chars if ch == 'K'))
        t0 = TEX_AT[1] + len(chars) / TEX_CPS + TEX_SETTLE
        n = int((t - t0) * TEX_CPS) + 1
        if n > 0:
            d.text((xe + kx, ys[1] + 30), TEX_NOTE[:n], font=_sym(NOTE_PX), fill=lv(INK, SUB))
    _tex_line(d, t, 2, xe, ys[2], TEX_PX, TEX_AT[2], her_u=0.0)
    _tree_r5(d, t, c)
    if t >= TEX_AT[3]:
        x4 = _tex_line(d, t, 3, xe, ys[3], TEX_PX, TEX_AT[3])
        _big_love(d, t, x4, ys[3])
    if t >= TEX_AT[4]:
        _tex_line(d, t, 4, x, c[1] + 382, TEX_CONC, TEX_AT[4], her_u=GD.lit(t, TEX_AT[4], BACK_AT))

def _reads_r5(t):
    out = _reads(t)
    Pl = hud.Pulse(t)
    Pl.hit('archive', TEX_AT[1], 0.4)
    for at in LOVE_OS:
        Pl.hit('archive', at, 0.3)
    for k, v in Pl.out.items():
        out[k] = max(out.get(k, 0.0), v)
    return out

def _run_r5():
    inp = [(a, a + 0.25) for a in KEY_TIMES]
    tex = [(TEX_AT[i], TEX_AT[i] + len(_tex_chars(i, TEX_PX)[0]) / TEX_CPS + 0.15) for i in range(3)]
    tex += [(GD.TREE_AT[0], GD.TREE_AT[-1] + 0.1), (LOVE_OS[0], LOVE_OS[2] + 0.5)]
    return {'input': inp, 'think': [], 'trace': [(at, ret[0] if ret else at + len(s) / BO.CODE_CPS + 0.25) for at, s, ret in CODE_R5], 'generate': [(a, a + 0.12) for a in RANK_AT_R5] + [(DOPE_AT - 0.25, STRIKE_AT + 0.5)], 'compare': [], 'forward': SEGS_R5, 'love': tex}
RUN_R5 = _run_r5()

def _body_r5(c, img, d):
    t = c.t
    LT = hud.left_rect(t)
    wx0 = win_rect(t)[0] + hud.pane_dx(t)
    if wx0 <= LT[2] + 1:
        d.rectangle((max(LT[2] - 9, int(wx0)), LT[1] - 1, LT[2] + 1, LT[1] - 1), fill=BG)
    L, lev = layout_r5(t)
    r = CPN.right(t)
    _cmdline(d, t, r, img)
    hits = _reads_r5(t)
    w = lead_r5(t)
    for name in ('input', 'think', 'trace', 'generate', 'compare', 'forward', 'love'):
        rect = L[name]
        level = lev.get(name, 1.0)
        if level <= 0.01 or rect[3] - rect[1] < 4 or rect[2] - rect[0] < 20:
            continue
        d.rectangle(rect, fill=BG)
        with panes.Clip(img, rect) as dd:
            if name == 'input':
                if t < R5_AT + 0.2:
                    gone = ease.prog(t, SCROLL_AT, SCROLL_AT + 0.2)
                    _chips_at(dd, t, rect, GC.SEE_COMMITS, GC.SEE_SEND, 1 - gone)
                    _press(dd, t, rect)
                _keys(dd, t, rect)
            elif name == 'trace':
                _trace_r5(dd, t, rect)
            elif name == 'generate':
                _gen_r5(dd, t, rect)
            elif name == 'compare':
                _cmp_log(dd, t, rect)
            elif name == 'forward':
                _forward_r5(dd, t, rect)
            elif name == 'love':
                _love_r5(dd, t, rect)
        lead.shade(img, rect, 1 - w[name])
        status = speed.label('longcat') if name == 'forward' else ''
        run = panes.run_k(t, RUN_R5.get(name, ())) * w[name]
        label = 'love.tex' if name == 'love' else name
        panes.box(d, rect, label, t, run, level, status, False)
    CPN._memory(d, t, L['memory'], hits)
    lead.shade(img, L['memory'], 1 - w['memory'])
    panes.box(d, L['memory'], 'mem', t, min(1.0, 3 * max(hits.values(), default=0.0)) * w['memory'])

def _body_fn(c, img, d):
    if c.t < R5_AT:
        return _body_r4(c, img, d)
    return _body_r5(c, img, d)
SHOTS = [('d1_relay', ROT_AT[0], R5_AT), ('d2_coy', R5_AT, DOPE_AT), ('d4_dope', DOPE_AT, QUIET_AT), ('d5_stay', QUIET_AT, SHRINK), ('d6_tex', SHRINK, LOVE_AT), ('d7_love', LOVE_AT, T1)]

def _dim(region, k):
    """The window as the support side, D11 (lead.support_rgb): her blue greyed, its content toward its own white;
    the page's white stays white (r5 round 1 used film.py's dim_paper here: greyer, toward paper, x 0.86 darker,
    and the window's white was gone, REVISE_R4 §5.1)."""
    return lead.support_rgb(region, k)
TOP_FADE, TOP_SOLID = (40, 14)

def _top_fade(part, k):
    """The page's top rows toward its white (a scroll fade, as a page clipped by its viewport): a line cut by the
    top of the window reads as scrolled away, not as the frame running through it."""
    import numpy as np
    a = np.asarray(part.convert('RGBA'), np.float32).copy()
    h = min(TOP_FADE, a.shape[0])
    y = np.arange(h, dtype=np.float32)
    ramp = np.clip((h - y) / (h - TOP_SOLID), 0.0, 1.0) * k
    a[:h, :, :3] = a[:h, :, :3] * (1 - ramp[:, None, None]) + 255.0 * ramp[:, None, None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')

def dsh_layer_r5(film, orig):
    """The dsh window from 151.55: r4's pane (ui/pane_open_d) before it and from LAYOUT_E on (the window is out,
    the page switches to E's layout, r4's seam into E); in between the r5 page (ui/pane_d_r5, shot at 2x), the
    window growing into the stage and back (win_rect, page_crop), shaded as the support side by win_shade."""
    r4 = DP.dsh_layer(film, orig, 'ui/pane_open_d', T0, T1)
    pd = P.path(R5_DIR)
    if not (pd.exists() and any(pd.iterdir())):
        return r4
    shots = PaneFrames(pd, FPS, (P.W, P.H))

    def fn(t, n, ctx):
        nn = int(round(t * FPS))
        if not N_R5 <= nn < N_E:
            return r4(t, n, ctx)
        if ctx is not None and ctx.state.get('pane') is False:
            return None
        dx = hud.pane_dx(t)
        wx0, wy0, wx1, wy1 = (int(round(v)) for v in win_rect(t))
        if wx0 + dx >= P.W:
            return None
        x0, y0, x1, y1 = (wx0 + dx, wy0, wx1 + dx, wy1)
        layer = Image.new('RGBA', (P.W, P.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for k in range(x0 + 7 - (y1 - y0), x1 + 7, 5):
            a_ = (max(k, x0 + 7), y0 + 7 + max(0, x0 + 7 - k))
            b_ = (min(k + (y1 - y0), x1 + 7), y0 + 7 + min(y1 - y0, x1 + 7 - k))
            if a_[0] <= b_[0]:
                d.line([a_, b_], fill=lv(INK, 0.55) + (255,))
        im = shots.image(nn) or shots.image(nn - 1)
        if im is not None:
            inner, (cx0, cy0, cx1, cy1) = page_crop(t)
            sc = im.size[0] / PAGE_W
            box = (cx0 * sc, cy0 * sc, cx1 * sc, cy1 * sc)
            ix0 = int(round(inner[0])) + dx
            size = (R_PANE[2] - int(round(inner[0])), inner[3] - inner[1])
            part = im.resize(size, Image.LANCZOS, box=box)
            fk = ease.clamp(cy0 * sc / (SHOT_SCALE * TOP_FADE))
            if fk > 0.003:
                part = _top_fade(part, fk)
            layer.alpha_composite(part, (ix0, inner[1]))
        d = ImageDraw.Draw(layer)
        d.rectangle((x0, y0, x1, y1), outline=INK + (255,), width=2)
        f13 = P.font(13)
        tw = d.textlength('dsh · web', font=f13)
        d.rectangle((x0 + 12, y0 - 7, x0 + 22 + tw, y0 + 7), fill=BG + (255,))
        d.text((x0 + 17, y0 - 7), 'dsh · web', font=f13, fill=INK + (255,))
        k = win_shade(t)
        if k > 0.003:
            bx = (max(0, x0), y0, min(P.W, x1 + 1), y1 + 1)
            reg = layer.crop(bx)
            rgb, alpha = (reg.convert('RGB'), reg.getchannel('A'))
            out = _dim(rgb, k).convert('RGBA')
            out.putalpha(alpha)
            layer.paste(out, bx[:2])
        return layer
    return fn

def register(film):
    hold = GD.prev_shot(film)
    if hold is not None:
        film.add('d0_hold', T0, ROT_AT[0], lambda c: hold.fn(c, **hold.params), chapter=tl.chapter(T0))
    for name, a, b in SHOTS:
        add(film, name, a, b, _body_fn)
    film.character = dsh_layer_r5(film, film.character)
    for T in TURNS:
        hud.LIVE.append((T.ans, T.write))
    hud.LIVE.append((GD.TREE_AT[9], LOVE_AT))
    hud.LIVE.append((LOVE_OS[0], LOVE_OS[2]))
    hud.LIVE.append((TEX_AT[4], BACK_AT))
    full_frame(LOVE_AT, BACK_AT, 0.3, 0.38)
    for t0, side in [(TURNS[0].read, 'left'), (ROT_STOP, 'both')]:
        film.set_lead(t0, side)
