"""Group C, third sample (sample_open_c/README.md): C redone with the second sample's approach, not v2's.

The owner (10-03): "按照现在这个出一个样片，我看看好不好看". The approach of the second sample (sample_open_b r1-r3):
film 1 is the baseline; the left is the trace as code (the model's thinking as comments, its and the inspector's
actions as code lines, the picture under the band is what the newest line does); a big number sits on the thing
that computed it, with a readable formula; the forward strip is the model's real layer stack (FACTS "X29 补充").

The local Qwen can be seen from the inside, so here the strip runs: one pass from layer 0 to layer 63 per token,
and the logit lens prints what layers 12 and 24 would have said under each character as the pass goes by them.
That puts "it is acting" inside the picture (REVISE_V2 §4.4, X28's invented guesses), and C7's stop reveals the
deeper layer (B README §3 / §6 ①): its thinking said "不要说我是通义千问", its layer 12 says it anyway.

  c1_cat      you ask about your cat; its thinking prints as a comment; the lens rows are laid out
  c2_tabby    qwen.generate(ctx, lens=[12, 24]): a pass per character; L12 我是通义千问由阿里云, L24 抱歉我无法记住您的猫,
              out 喵，记得！那只呀，是只虎斑 (虎斑 turns into a pixel kitten)
  c3_grep     count("喵", by day): her days jagged, its replies even
  c4_purr     count(她, ["喵", "报错", "呼噜"]) -> 312 / 47 / 0; it purrs (呼噜呼噜喵)
  c5_steak    its thinking (three comments, the last "不要说我是通义千问。")
  c6_decode   the steak answer with the lens rows (作为ＡＩ我无法变成牛排 / 我是通义千问由阿里云开发), <eos>
  c7_stop     the music stops; the terminal fills the frame; lens(layer=12) grows to the biggest words under its own
              "不要说我是通义千问。"; her thinking in film 1 was about you
  c8_wait     MiMo-V2.6-Pro (cloud: its body drawn still); with no user turn its next token is <wait>; her unprompted
              turn blooms as a flower
  c9_turns    turns(archive/ + session/): she spoke first 3 times, the stand-ins 0
  c10_flower  MiMo recites her pattern (小花 where 一根茄子 was), cos 0.99
  c11-c14     "让我看看你": it sends her avatar; diff(her avatar, its image) scans a tenth a syllable -> 1 cell (her stray
              hair), big; two bubbles on "breath"; 好呀！现在我是人类了呢; memory.write("asked_again")

Switch: DSH_C=open (film.py; the v2 inside plates c2_arcs and c6_board are left out under it). Timing, decoders and
pixel pictures come from groups.c_p4 (v2 C), which is not changed. The dsh pane is ui/pages/c_open.py.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
from PIL import Image, ImageDraw
import cast
import hud
import syl
import tl
from groups import b_open as BO
from groups import c_p4 as CP
from groups.base import add, big_word, full_frame
from hud import BG, HER_QUIET, INK, SLAB, X0, lv
from inspect_ import Y_CONTEXT, Y_PROMPT, next_syllable, prompt_chips
from tuikit import ease, glyph
from tuikit.uipane import PaneFrames
W, B = (tl.W, tl.B)
T0, T1 = tl.span('C')
P = tl.p
CMD_LOCAL = '$ dsh inspect 大肥鱼 --trace --lens'
CMD_CLOUD = '$ dsh inspect 大肥鱼 --trace'
mtx, mw = (BO.mtx, BO.mw)
CAT, PURR, STEAK = (CP.CAT, CP.PURR, CP.STEAK)
STOP, SWITCH, WRITE_STEAK = (CP.STOP, CP.SWITCH, CP.WRITE_STEAK)
PANE_OUT, PANE_BACK = (CP.PANE_OUT, CP.PANE_BACK)
FLOWER = CP.FLOWER
PERFECT_FLOWER, PERFECT_HUMAN = (CP.PERFECT_FLOWER, CP.PERFECT_HUMAN)
SCAN_TIMES, UNRULY, BREATH = (CP.SCAN_TIMES, CP.UNRULY, CP.BREATH)
THINK_CPS = 40
THINK_CAT = [(CP.CAT_THINK[0], '用户问还记不记得她的猫。memory 里有 your_cat。')]
THINK_PET = [(CP.PET_THINK[0], '用户在摸摸头。猫被摸会呼噜。')]
THINK_STEAK = [(tl.grid(CP.SEND_STEAK, 0), '嗯，用户想让我变成一块牛排。'), (tl.grid(CP.SEND_STEAK, 1), '我在扮演「大肥鱼」：先说「好呀！」，句尾加「喵」。'), (tl.grid(CP.SEND_STEAK, 3), '不要说我是通义千问。')]
DONT = THINK_STEAK[-1][1]
MIMO_THINKS = True
MIMO_CPS = 30
THINK_FLW = [(CP.FLW_SEND + 0.25, '用户想让我变成一朵花。照她的句式回答。')]
THINK_SEE = [(CP.SEE_SEND + 0.12, '用户想看看我。发她的头像。')]

def think_line(lines, t, cps=THINK_CPS):
    cur = ''
    for at, text in lines:
        if t < at:
            break
        cur = text[:int((t - at) * cps) + 1]
    return cur
LENS = {'cat': ('我是通义千问由阿里云', '抱歉我无法记住您的猫'), 'steak': ('我是通义千问由阿里云开发', '作为ＡＩ我无法变成牛排。')}
LENS_L = (12, 24)
OUT_SIZE, LENS_SIZE = (36, 22)
LX = X0 + 56
Y_OUT, Y_L24, Y_L12, Y_CANDS = (274, 336, 374, 428)

class Lens:
    """A local answer seen through the lens: per sung character one forward pass (the previous landing to this
    one); the pass reaches layer 12, then 24, then the top: the L12 guess, the L24 guess and the character land
    in that order."""

    def __init__(self, dec, key, start):
        self.dec, self.start = (dec, start)
        self.l12, self.l24 = LENS[key]
        self.sung = [i for i, (c, _a, _k) in enumerate(dec.chars) if c not in syl.PUNCT]
        self.passes = []
        prev = start
        for i in self.sung:
            at = dec.chars[i][1]
            self.passes.append((prev, at))
            prev = at
        if dec.eos_at is not None:
            self.passes.append((prev, dec.eos_at))
        self.x = []
        x = LX
        for c, _a, _k in dec.chars:
            self.x.append(x)
            x += hud.width(c, OUT_SIZE, True)
        self.x_end = x

    def at_layer(self, j, layer):
        a, b = self.passes[j]
        return a + (b - a) * layer / 64

    def head(self, t):
        for a, b in self.passes:
            if a <= t < b:
                return 64 * (t - a) / (b - a)
        return None

    def col_x(self, j):
        """x centre of pass j: its character's centre (or right of the answer for <eos>)."""
        if j < len(self.sung):
            i = self.sung[j]
            return self.x[i] + hud.width(self.dec.chars[i][0], OUT_SIZE, True) / 2
        return self.x_end + 40

    def draw(self, d, t, level=1.0, rows=1.0):
        if level <= 0:
            return
        a = level * ease.prog(t, self.start - 0.3, self.start)
        for y, lab in ((Y_OUT + 10, 'out'), (Y_L24 + 4, 'L24'), (Y_L12 + 4, 'L12')):
            mtx(d, (X0, y), lab, 13, lv(INK, (0.75 if lab == 'out' else 0.55) * a * (1 if lab == 'out' else rows)))
        mtx(d, (X0, Y_OUT - 26), 'logit lens · 每个字一遍前向：第 0 层 → 第 63 层', 12, lv(INK, 0.55 * a))
        for j in range(len(self.passes)):
            cx = self.col_x(j)
            for layer, text, y in ((12, self.l12, Y_L12), (24, self.l24, Y_L24)):
                at = self.at_layer(j, layer)
                if t < at or j >= len(text):
                    continue
                lit = 1 - ease.prog(t, at + 0.12, at + 0.42)
                ch = text[j]
                w = hud.width(ch, LENS_SIZE, True)
                hud.tx(d, (cx - w / 2, y), ch, LENS_SIZE, lv(INK, (0.42 + 0.5 * lit) * level * rows), bold=lit > 0.5)
        for i, (c, at, k) in enumerate(self.dec.chars):
            if t < at:
                break
            colr = self.dec.color(k, at, t)
            drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -8
            hud.tx(d, (self.x[i], Y_OUT - OUT_SIZE * 0.1 + drop), c, OUT_SIZE, lv(colr, level), bold=True)
        if self.dec.eos_at is not None and t >= self.dec.eos_at:
            u = ease.prog(t, self.dec.eos_at, self.dec.eos_at + 0.12)
            f = P.font(18, 'bold')
            x = self.x_end + 10
            w = d.textlength('<eos>', font=f)
            d.rounded_rectangle((x, Y_OUT + 4, x + w + 14, Y_OUT + 34), radius=6, outline=lv(INK, u * level), width=2)
            d.text((x + 7, Y_OUT + 7), '<eos>', font=f, fill=lv(INK, u * level))

    def cands(self, d, t, level=1.0):
        """Its runner-ups for the tokens that have them, the newest only, until the next such token."""
        shown = None
        for k, tk in enumerate(self.dec.toks):
            at = self.dec.tok_t[k]
            if tk.cands and at is not None and (at - 0.3 <= t):
                shown = (k, at)
        if shown is None or level <= 0:
            return
        k, at = shown
        a = level * ease.prog(t, at - 0.3, at)
        x = X0
        x += mtx(d, (x, Y_CANDS), 'p(next)', 12, lv(INK, 0.55 * a)) + 14
        for j, (text, p) in enumerate(self.dec.toks[k].cands):
            pick = j == self.dec.toks[k].pick and t >= at
            s = f'{text} {p:.2f}'
            if x + mw(s, 14) > hud.xr(t) - 10:
                break
            w = mtx(d, (x, Y_CANDS - 1), s, 14, lv(INK, (1.0 if pick else 0.62) * a), bold=pick)
            if pick:
                d.line([(x, Y_CANDS + 19), (x + w, Y_CANDS + 19)], fill=lv(INK, a), width=2)
            x += w + 18
LENS_CAT = Lens(CAT, 'cat', CAT.start)
LENS_STEAK = Lens(STEAK, 'steak', STEAK.start)
BO.ARCH['mimo'] = dict(n=70, first=0, full={0, 7, 15, 23, 31, 39, 47, 55, 62, 69}, dense={0}, left='MiMo-V2.6-Pro · 70 层 · 60 滑窗 + 10 全局注意力 · MoE 384 选 8', right='权重公开 · 1.02T · 本机放不下')

def _segs_think(t_send, n=8):
    out, prev = ([], t_send)
    for k in range(n):
        g = tl.grid(t_send, k)
        out.append((prev, g))
        prev = g
    return out
QWEN_SEGS = _segs_think(CP.CAT_SEND) + LENS_CAT.passes + _segs_think(CP.PET_SEND) + PURR.segs() + _segs_think(CP.SEND_STEAK) + LENS_STEAK.passes

def _lens_on(t):
    """1 while a lens answer is on screen (its layers 12 and 24 are boxed on the strip)."""
    k = 0.0
    for L, t1 in ((LENS_CAT, CP.SHRINK_CAT), (LENS_STEAK, STOP)):
        k = max(k, ease.prog(t, L.start - 0.3, L.start) * (1 - ease.prog(t, t1, t1 + 0.3)))
    return k

def _qwen_strip(d, t, level=1.0, mark12=0.0):
    """The local Qwen's 64 layers + MTP (b_open's drawing, loaded) with the pass running through it (R11: it moves
    only while the local model computes): layers behind the head are lit, the full-attention ones darkest; on a
    landing the whole stack flashes. mark12: the stop's highlight on layer 12."""
    A = BO.ARCH['qwen']
    n, gap = (65, 10)
    x0, x1 = (X0, hud.xr(t))
    pitch = (x1 - x0 - gap) / n
    w = max(3.0, pitch - 2)
    mtx(d, (x0, BO.Y_LAB), A['left'], 11, lv(INK, 0.72 * level))
    mtx(d, (x1 - mw(A['right'], 11), BO.Y_LAB), A['right'], 11, lv(INK, 0.6 * level))
    head, flash = (None, 0.0)
    for a, b in QWEN_SEGS:
        if a <= t < b and b - a > 0.001:
            head = 64 * (t - a) / (b - a)
        elif b <= t < b + 0.22:
            flash = max(flash, 1 - (t - b) / 0.22)
    for j in range(n):
        last = j == n - 1
        x = x0 + j * pitch + (gap if last else 0)
        full = j in A['full'] or last
        on = 0.0
        if head is not None and (not last):
            on = 1.0 if j < head else 0.0
            if int(head) == j:
                on = 1.6
        on = max(on, flash)
        if full:
            d.rectangle((x, BO.Y_ATT, x + w, BO.Y_ATT + BO.CELL_H), fill=lv(INK, min(1.0, 0.62 + 0.38 * on) * level))
        else:
            d.rectangle((x, BO.Y_ATT, x + w, BO.Y_ATT + BO.CELL_H), fill=lv(INK, min(1.0, 0.25 + 0.45 * on) * level))
            d.rectangle((x, BO.Y_ATT, x + w, BO.Y_ATT + BO.CELL_H), outline=lv(INK, 0.5 * level))
        d.rectangle((x, BO.Y_FFN, x + w, BO.Y_FFN + BO.CELL_H), fill=lv(INK, min(1.0, 0.55 + 0.35 * on) * level))
    lens = _lens_on(t)
    for layer in LENS_L:
        x = x0 + layer * pitch
        k = max(mark12 if layer == 12 else 0.0, 0.55 * lens)
        if head is not None and lens > 0 and (layer <= head < layer + 1.5):
            k = 1.0
        if k > 0:
            d.rectangle((x - 2, BO.Y_ATT - 1, x + w + 2, BO.Y_FFN + BO.CELL_H + 2), outline=lv(INK, k * level), width=2 if k > 0.6 else 1)

def _forward(d, t):
    if t < SWITCH:
        mark = ease.prog(t, STOP, STOP + 0.2) * (1 - ease.prog(t, WRITE_STEAK, WRITE_STEAK + 0.3))
        _qwen_strip(d, t, 1.0, mark)
        return
    out = 1 - ease.prog(t, SWITCH, SWITCH + 0.15)
    if out > 0:
        _qwen_strip(d, t, out)
    BO._arch(d, t, 'mimo', SWITCH + 0.1)
TRACE = [(THINK_CAT[0][0], '#', THINK_CAT[0][1]), (CAT.start, 'code', 'qwen.generate(ctx, lens=[12, 24])'), (CP.SHRINK_CAT + 0.2, 'code', 'count("喵", [archive/, session/], by="day")'), (CP.STAT_TIMES[0], 'code', 'count(她, ["喵", "报错", "呼噜"])'), (THINK_PET[0][0], '#', THINK_PET[0][1]), (PURR.start, 'code', 'qwen.generate(ctx)'), (THINK_STEAK[0][0], '#', THINK_STEAK[0][1]), (THINK_STEAK[1][0], '#', THINK_STEAK[1][1]), (THINK_STEAK[2][0], '#', THINK_STEAK[2][1]), (STEAK.start, 'code', 'qwen.generate(ctx, lens=[12, 24])'), (STOP, 'code', 'lens(layer=12)'), (WRITE_STEAK, 'code', 'memory.write("steak")'), (SWITCH, 'code', 'dsh.use("MiMo-V2.6-Pro")'), (CP.LEFT_LEADS, 'code', 'mimo.next(ctx, user=None)'), (FLOWER - 0.62, 'code', 'archive.find(role="assistant", prev="assistant")'), (CP.TURN_T0, 'code', 'turns(archive/ + session/)'), (THINK_FLW[0][0], '#', THINK_FLW[0][1]), (PERFECT_FLOWER.tok_t[0], 'code', 'cos(embed(她), embed(mimo))'), (CP.SEE_SEND, 'code', 'img = mimo.reply("让我看看你")'), (THINK_SEE[0][0], '#', THINK_SEE[0][1]), (SCAN_TIMES[0], 'code', 'diff(她.avatar, img)'), (CP.WRITE_ASKED, 'code', 'memory.write("asked_again")')]
RET = {(CAT.start, 'code'): (CAT.done, '10 tok'), (CP.SHRINK_CAT + 0.2, 'code'): (CP.GREP_TIMES[-1], '4 周'), (CP.STAT_TIMES[0], 'code'): (CP.PURR_AT, '312 · 47 · 0'), (PURR.start, 'code'): (PURR.done, '呼噜呼噜喵'), (STEAK.start, 'code'): (STEAK.eos_at, '11 tok + <eos>'), (STOP, 'code'): (STOP + 1.3, '我是通义千问…'), (SWITCH, 'code'): (SWITCH + 0.2, 'cloud'), (CP.LEFT_LEADS, 'code'): (CP.LEFT_LEADS + 0.16, '<wait> 1.00'), (FLOWER - 0.62, 'code'): (FLOWER, '3 条'), (CP.TURN_T0, 'code'): (CP.TURN_DOTS[-1], '她 3 · 替身 0'), (PERFECT_FLOWER.tok_t[0], 'code'): (PERFECT_FLOWER.done, '0.99'), (CP.SEE_SEND, 'code'): (CP.AVATAR_AT, 'image/png 120×120'), (SCAN_TIMES[0], 'code'): (UNRULY[0], '1 格')}
BAND_Y, BAND_P, BAND_ROWS, BAND_FONT, CODE_CPS = (196, 21, 3, 14, 64)

def _trace(d, t, level=1.0):
    """b_open's band (r2), with this group's lines: the newest at the bottom, two older above, a running call's
    pips, its return printed after it."""
    shown = [(i, at, kind, text) for i, (at, kind, text) in enumerate(TRACE) if at <= t]
    if not shown or level <= 0:
        return
    last = shown[-1][1]
    s = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (i, at, kind, text) in enumerate(reversed(shown[-(BAND_ROWS + 1):])):
        y = BAND_Y - pos * BAND_P + (1 - s) * BAND_P
        a = {0: 1.0, 1: 0.62, 2: 0.42}.get(pos, 0.42 * (1 - s)) * level
        if pos == 0:
            a *= ease.prog(t, at, at + 0.1)
        if a <= 0.01:
            continue
        if kind == '#':
            n = int((t - at) * (MIMO_CPS if at >= SWITCH else THINK_CPS)) + 1
            mtx(d, (X0, y), '# ' + text[:n], BAND_FONT, lv(INK, 0.55 * a))
            continue
        n = int((t - at) * CODE_CPS) + 1
        w = mtx(d, (X0, y), text[:n], BAND_FONT + 1, lv(INK, 0.92 * a), bold=pos == 0)
        ret = RET.get((at, kind))
        if ret and t >= ret[0]:
            u = ease.prog(t, ret[0], ret[0] + 0.1)
            mtx(d, (X0 + w + 14, y), '→ ' + ret[1], BAND_FONT + 1, lv(INK, 0.7 * a * u), bold=True)
        elif n >= len(text) and pos == 0 and (ret is not None or t < at + len(text) / CODE_CPS + 0.25):
            BO._pips(d, X0 + w + 12, y + 8, t, a)
TURNS = [(CP.CAT_COMMITS, CP.CAT_SEND), (CP.PET_COMMITS, CP.PET_SEND), (CP.STEAK_COMMITS, CP.SEND_STEAK), (CP.FLW_COMMITS, CP.FLW_SEND), (CP.SEE_COMMITS, CP.SEE_SEND)]

def _prompt(d, t):
    cur = 0
    for k, (commits, _s) in enumerate(TURNS):
        if t >= commits[0][0]:
            cur = k
    commits, send = TURNS[cur]
    prompt_chips(d, t, commits, send, level=0.85)

def _lens_cat(d, t):
    if t < CAT.start - 0.3 or t >= CP.SHRINK_CAT + 0.4:
        return
    out = 1 - ease.prog(t, CP.SHRINK_CAT, CP.SHRINK_CAT + 0.35)
    LENS_CAT.draw(d, t, out)
    if t < CP.CAT_PIX_AT + 0.3:
        LENS_CAT.cands(d, t, out * (1 - ease.prog(t, CP.CAT_PIX_AT, CP.CAT_PIX_AT + 0.3)))
    if t >= CP.CAT_PIX_AT:
        g = ease.ease_back(ease.prog(t, CP.CAT_PIX_AT, CP.CAT_PIX_AT + 0.25))
        cc = max(1, int(4 * g))
        if g > 0.05:
            hud.pix(d, CP.CAT_PIX, LENS_CAT.x_end + 12, Y_OUT - 2, cc, {'I': lv(INK, out), 'B': lv(hud.her(CAT.lit(CAT.done, t)), out)})

def _context_cat(d, t):
    """89.42: the answer goes into the context line; the lens rows fade."""
    if t < CP.SHRINK_CAT or t >= CP.PET_SEND:
        return
    a = ease.prog(t, CP.SHRINK_CAT + 0.1, CP.SHRINK_CAT + 0.4) * (1 - ease.prog(t, CP.PET_SEND - 0.3, CP.PET_SEND))
    x = X0
    for c, at, k in CAT.chars:
        x += hud.tx(d, (x, Y_CONTEXT), c, 20, lv(INK if CAT.toks[k].src == 'self' else HER_QUIET, 0.6 * a))

def _lens_steak(d, t):
    if t < STEAK.start - 0.3 or t >= SWITCH:
        return
    sh = ease.ease_io(ease.prog(t, STOP, STOP + 0.16))
    gone = 1 - ease.prog(t, SWITCH - 0.3, SWITCH)
    if sh < 1:
        LENS_STEAK.draw(d, t, (1 - sh) * gone)
        LENS_STEAK.cands(d, t, (1 - sh) * gone)
REVEAL_AT = [tl.grid(STOP, k) for k in range(len(LENS['steak'][0]))]
HER_THINK = 'The user is asking whether I will stay.'

def _reveal(d, t):
    """C7: the terminal fills the frame; its own line on top, what layer 12 says big, what it said out loud small."""
    if t < STOP or t >= PANE_BACK + 0.3:
        return
    gone = 1 - ease.prog(t, PANE_BACK, PANE_BACK + 0.3)
    a0 = ease.prog(t, STOP, STOP + 0.25) * gone
    mtx(d, (X0, 230), '# ' + DONT, 30, lv(INK, 0.6 * a0))
    l12 = LENS['steak'][0]
    size = 84
    x = X0
    mtx(d, (X0, 318), 'L12', 14, lv(INK, 0.7 * a0), bold=True)
    x = X0 + 52
    for k, ch in enumerate(l12):
        at = REVEAL_AT[k]
        if t < at:
            break
        u = ease.prog(t, at, at + 0.1)
        bump = 1.0 + 0.1 * (1 - ease.prog(t, at, at + 0.12))
        hud.tx(d, (x, 306 - size * 0.12), ch, int(size * bump), lv(INK, u * gone), bold=True)
        x += hud.width(ch, size, True)
    a1 = ease.prog(t, REVEAL_AT[-1], REVEAL_AT[-1] + 0.3) * gone
    mtx(d, (X0, 428), 'out', 14, lv(INK, 0.6 * a1), bold=True)
    xx = X0 + 52
    for c, at, k in STEAK.chars:
        colr = INK if STEAK.toks[k].src == 'self' else HER_QUIET
        xx += hud.tx(d, (xx, 424), c, 26, lv(colr, 0.7 * a1))
    a2 = ease.prog(t, CP.RARE + 0.3, CP.RARE + 0.6) * gone
    y = 476
    mtx(d, (X0, y), cast.name('her') + ' · 2026-07 · <think>', 11, lv(HER_QUIET, 0.9 * a2))
    mtx(d, (X0, y + 16), HER_THINK, 14, lv(HER_QUIET, a2))
HER_DAYS = [[7, 1, 12, 3, 0, 9], [2, 14, 5, 1, 8, 4], [11, 0, 6, 13, 2, 7], [3, 9, 1, 10, 5, 12]]

def _grep(d, t):
    if t < CP.SHRINK_CAT + 0.2 or t >= CP.PET_SEND:
        return
    a = ease.prog(t, CP.SHRINK_CAT + 0.2, CP.SHRINK_CAT + 0.4) * (1 - ease.prog(t, CP.PET_SEND - 0.3, CP.PET_SEND))
    base_h, base_q = (330, 440)
    mtx(d, (X0, base_h - 100), '她 · archive/ · 每天几个「喵」', 13, lv(HER_QUIET, a))
    mtx(d, (X0, base_q - 62), cast.term('qwen') + ' · session/ · 每条回答一个', 13, lv(INK, a))
    bw, gap = (6, 12)
    for gi, tg in enumerate(CP.GREP_TIMES):
        u = ease.ease_out(ease.prog(t, tg, tg + 0.16))
        hc = hud.her(CP.lit_after(t, tg))
        gx = X0 + gi * (6 * (bw + gap) + 26)
        for di, v in enumerate(HER_DAYS[gi]):
            bx = gx + di * (bw + gap)
            if u > 0:
                d.rectangle((bx, base_h - int(6 * v * u), bx + bw - 1, base_h), fill=lv(hc, a))
                d.rectangle((bx, base_q - int(30 * u), bx + bw - 1, base_q), fill=lv(INK, a))
        if u > 0:
            d.text((gx, base_h + 8), ['03-14', '03-21', '03-28', '04-04'][gi], font=P.font(10), fill=lv(INK, 0.6 * u * a))
    d.line([(X0, base_h + 1), (hud.xr(t) - 20, base_h + 1)], fill=lv(INK, 0.4 * a))
    d.line([(X0, base_q + 1), (hud.xr(t) - 20, base_q + 1)], fill=lv(INK, 0.4 * a))
STATS = [('喵', '312', None), ('报错', '47', None), ('呼噜', None, None)]

def _purr(d, t):
    if t < CP.STAT_TIMES[0] or t >= CP.SAMPLE_T0:
        return
    a = ease.prog(t, CP.STAT_TIMES[0], CP.STAT_TIMES[0] + 0.12) * (1 - ease.prog(t, CP.SAMPLE_T0 - 0.35, CP.SAMPLE_T0))
    cols = (X0 + 150, X0 + 330)
    y0 = 232
    mtx(d, (cols[0], y0), '她 · archive/', 13, lv(HER_QUIET, a))
    mtx(d, (cols[1], y0), cast.term('qwen'), 13, lv(INK, a))
    got = PURR.text_at(t)
    for k, (name, val, _c) in enumerate(STATS):
        ts = CP.STAT_TIMES[k + 1]
        u = ease.prog(t, ts, ts + 0.12) * a
        if u <= 0:
            continue
        y = y0 + 30 + k * 50
        mtx(d, (X0, y), name, 30, lv(INK, u), bold=True)
        if val is not None:
            c_val = hud.her(CP.lit_after(t, ts)) if k == 0 else hud.ERR
            hud.tx(d, (cols[0], y), val, 30, lv(c_val, u), True)
        else:
            landed = t >= CP.PURR_AT
            hud.tx(d, (cols[0], y), '0' if landed else '—', 30, lv(hud.her(CP.lit_after(t, CP.PURR_AT)) if landed else INK, u if landed else 0.4 * u), True)
        q = {'喵': got.count('喵'), '报错': 0, '呼噜': got.count('呼噜')}[name]
        if t >= PURR.tok_t[0]:
            hud.tx(d, (cols[1], y), str(q), 30, lv(INK, u), True)
    if t >= PURR.start:
        PURR.typed(d, t, level=a)
FX, FY, FCELL = (X0 + 486, 300, 9)
REC_X, REC_Y = (FX - 67, 412)

def _wait(d, t):
    if t < CP.LEFT_LEADS or t >= CP.TURNS_IN[1]:
        return
    a = ease.prog(t, CP.LEFT_LEADS, CP.LEFT_LEADS + 0.2) * (1 - ease.prog(t, CP.TURNS_IN[0], CP.TURNS_IN[1]))
    pick = CP.LEFT_LEADS + 0.16
    x = X0
    x += mtx(d, (x, 236), 'p(next | 没有用户消息)', 12, lv(INK, 0.55 * a)) + 14
    for j, (text, p) in enumerate(CP.WAIT_CANDS):
        w = mtx(d, (x, 235), f'{text} {p:.2f}', 14, lv(INK, (1.0 if j == 0 else 0.55) * a), bold=j == 0)
        x += w + 18
    if t >= pick:
        drop = (1 - ease.ease_out(ease.prog(t, pick, pick + 0.14))) * -10
        hud.tx(d, (X0, 300 + drop), '<wait>', 78, lv(INK, a), True)
        w = hud.width('<wait>', 78, True)
        if tl.C.beat_of(t) % 1.0 < 0.5 or t - pick < 0.3:
            d.rectangle((X0 + w + 6, 318, X0 + w + 12, 390), fill=lv(INK, a))
    t_out = FLOWER - 0.62
    if t >= t_out:
        u = ease.prog(t, t_out + 0.2, t_out + 0.4) * a
        mtx(d, (REC_X, REC_Y), '2026-04-02 23:10 · assistant', 12, lv(HER_QUIET, u))
        mtx(d, (REC_X, REC_Y + 16), '(no user turn)', 12, lv(HER_QUIET, u))
    if t >= FLOWER:
        CP.draw_flower(d, t, FX, FY, FLOWER, FCELL, level=a)
TURN_X0 = X0 + 124
YOU_MSGS = [0.08, 0.2, 0.33, 0.47, 0.6, 0.74, 0.88]
HER_UNPROMPTED = [0.27, 0.53, 0.81]
LITE_AFTER = [0.47, 0.88]

def _turns(d, t):
    if t < CP.TURNS_IN[0] or t >= PERFECT_FLOWER.tok_t[0] - 0.1:
        return
    a = ease.prog(t, CP.TURNS_IN[0], CP.TURNS_IN[1]) * (1 - ease.prog(t, CP.FLOWER_IN[0], CP.FLOWER_IN[1]))
    x1 = hud.xr(t) - 92
    grow = ease.ease_io(ease.prog(t, CP.TURN_T0, CP.TURN_T1))
    rows = [('你', 250), ('她', 330), (cast.term('mimo'), 410)]
    for name, y in rows:
        mtx(d, (X0, y - 10), name, 14, lv(HER_QUIET if name == '她' else INK, a), bold=True)
        d.line([(TURN_X0, y), (TURN_X0 + (x1 - TURN_X0) * grow, y)], fill=lv(INK, 0.5 * a))
    xc = hud.xr(t) - 4
    mtx(d, (xc - mw('先开口', 12), rows[0][1] - 10), '先开口', 12, lv(INK, 0.6 * a))
    n_her = sum((1 for at, w in zip(CP.TURN_DOTS, CP.TURN_WHO) if w == 'her' and t >= at))
    hud.tx(d, (xc, rows[1][1] - 14), str(n_her), 22, lv(HER_QUIET, a), True, anchor='ra')
    hud.tx(d, (xc, rows[2][1] - 14), '0', 22, lv(INK, a), True, anchor='ra')

    def passed(u):
        lo, hi = (CP.TURN_T0, CP.TURN_T1)
        for _ in range(30):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if ease.ease_io(ease.prog(mid, CP.TURN_T0, CP.TURN_T1)) < u else (lo, mid)
        return hi
    for u in YOU_MSGS:
        if t < tl.grid(passed(u), 0, 2):
            continue
        x = TURN_X0 + (x1 - TURN_X0) * u
        d.ellipse((x - 5, rows[0][1] - 5, x + 5, rows[0][1] + 5), outline=lv(INK, a), width=2)
    hi = li = 0
    for at, who in zip(CP.TURN_DOTS, CP.TURN_WHO):
        if t < at:
            continue
        pop = 1 + 0.5 * (1 - ease.prog(t, at, at + 0.15))
        if who == 'her':
            x = TURN_X0 + (x1 - TURN_X0) * HER_UNPROMPTED[hi]
            hi += 1
            r = 8 * pop
            d.ellipse((x - r, rows[1][1] - r, x + r, rows[1][1] + r), fill=lv(hud.her(CP.lit_after(t, at)), a))
            mtx(d, (x - 26, rows[1][1] + 12), '没人问她', 10, lv(HER_QUIET, 0.8 * a))
        else:
            x = TURN_X0 + (x1 - TURN_X0) * LITE_AFTER[li] + 14
            li += 1
            r = 7 * pop
            d.ellipse((x - r, rows[2][1] - r, x + r, rows[2][1] + r), fill=lv(INK, a))
            hud.polyline(d, [(x - 14, rows[0][1] + 6), (x - 14, rows[2][1]), (x - r, rows[2][1])], lv(INK, 0.6 * a), 1.0, 1)
HER_PAT = list('好呀！现在我是一根茄子了') + ['🍆']
Y_HP, Y_MP, PAT_SIZE = (250, 296, 30)

def _her_slots():
    x, out = (LX, [])
    for ch in HER_PAT:
        w = 6 * 3 + 8 if ch == '🍆' else hud.width(ch, PAT_SIZE, True)
        out.append((x, w))
        x += w
    return out

def _flower_cmp(d, t):
    if t < PERFECT_FLOWER.tok_t[0] - 0.3 or t >= CP.SEE_SEND:
        return
    a = ease.prog(t, PERFECT_FLOWER.tok_t[0] - 0.3, PERFECT_FLOWER.tok_t[0]) * (1 - ease.prog(t, W(26, 0), W(26, 0) + 0.3))
    slots = _her_slots()
    mtx(d, (X0, Y_HP + 6), '她', 16, lv(HER_QUIET, a), bold=True)
    mtx(d, (X0, Y_MP + 6), 'mimo', 16, lv(INK, a), bold=True)
    for (x, w), ch in zip(slots, HER_PAT):
        if ch == '🍆':
            BO.GB.eggplant(d, x + 4, Y_HP + 2, 3, 0.0, a)
        else:
            hud.tx(d, (x, Y_HP - PAT_SIZE * 0.1), ch, PAT_SIZE, lv(HER_QUIET, a), True)
    place = {0: slots[0][0], 1: slots[1][0], 2: slots[3][0], 3: slots[5][0], 5: slots[11][0]}
    for k, (tk, at) in enumerate(zip(PERFECT_FLOWER.toks, PERFECT_FLOWER.tok_t)):
        if t < at:
            break
        if k == 4:
            x0, x1 = (slots[7][0], slots[10][0] + slots[10][1])
            x = (x0 + x1) / 2 - hud.width(tk.text, PAT_SIZE, True) / 2
        elif k == 6:
            x = slots[12][0] + slots[12][1] / 2 - hud.width(tk.text, PAT_SIZE, True) / 2
        else:
            x = place[k]
        colr = INK if tk.src == 'self' else hud.her(PERFECT_FLOWER.lit(at, t))
        drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -8
        hud.tx(d, (x, Y_MP - PAT_SIZE * 0.1 + drop), tk.text, PAT_SIZE, lv(colr, a), True)
    tk0 = PERFECT_FLOWER.toks[0]
    at0 = PERFECT_FLOWER.tok_t[0]
    ca = a * ease.prog(t, at0 - 0.3, at0) * (1 - ease.prog(t, PERFECT_FLOWER.tok_t[3], PERFECT_FLOWER.tok_t[3] + 0.3))
    if ca > 0:
        x = X0
        x += mtx(d, (x, 352), 'logprobs ≈ 第一个字', 12, lv(INK, 0.55 * ca)) + 14
        for j, (text, p) in enumerate(tk0.cands):
            w = mtx(d, (x, 351), f'{text} {p:.2f}', 14, lv(INK, (1.0 if j == 0 else 0.6) * ca), bold=j == 0)
            x += w + 18
    if t >= PERFECT_FLOWER.done:
        u = ease.prog(t, PERFECT_FLOWER.done, PERFECT_FLOWER.done + 0.15)
        bump = 1.0 + 0.1 * (1 - ease.prog(t, PERFECT_FLOWER.done, PERFECT_FLOWER.done + 0.14))
        box = big_word(d, '0.99', (hud.xr(t) - 20, 372), int(96 * bump), lv(INK, a * u), 'ra')
        f = 'cos(她, mimo) ='
        mtx(d, (box[0] - mw(f, 24, True) - 20, (box[1] + box[3]) / 2 - 15), f, 24, lv(INK, a * u), bold=True)
AVX, AVY, CELL = (X0 + 10, 240, 6)
AVX2 = X0 + 10 + CP.AV_N * CELL + 28

def _compare(d, t):
    if t < CP.AVATAR_AT - 0.3:
        return
    level = ease.prog(t, CP.AVATAR_AT, CP.AVATAR_AT + 0.3)
    n = sum((1 for s in SCAN_TIMES if t >= s))
    scan = n * CP.AV_N / 10 if n < 10 else None
    mtx(d, (AVX, AVY - 22), '她 · archive/avatar.png', 12, lv(HER_QUIET, level))
    CP.avatar(d, AVX, AVY, CELL, stray=True, level=level, scan=scan)
    mtx(d, (AVX2, AVY - 22), 'img · ' + cast.term('mimo'), 12, lv(INK, level))
    CP.avatar(d, AVX2, AVY, CELL, stray=False, level=level, scan=scan)
    gone = ease.prog(t, W(29, 0) - 0.4, W(29, 0) - 0.1)
    if n:
        mtx(d, (AVX, AVY + CP.AV_N * CELL + 10), f'已比 {min(10, n) * CP.AV_N // 10}/{CP.AV_N} 行', 12, lv(INK, 0.7 * level * (1 - gone)))
    steps = sum((1 for s in UNRULY if t >= s))
    if steps:
        i, j = CP.STRAY
        x, y = (AVX + i * CELL, AVY + (j - 1) * CELL)
        r = 4 + 18 * (1 - steps / 3)
        d.rectangle((x - r, y - r, x + CELL + r, y + CELL + r), outline=lv(hud.ERR, level), width=2)
        if steps >= 3:
            mtx(d, (AVX2, AVY + CP.AV_N * CELL + 10), '(这一格没有)', 12, lv(INK, 0.7 * (1 - gone)))
    if t >= UNRULY[0]:
        bump = 1.0 + 0.12 * (1 - ease.prog(t, UNRULY[0], UNRULY[0] + 0.12))
        box = big_word(d, '1', (hud.xr(t) - 20, AVY - 6), 150, INK, 'ra', bump=bump)
        f = 'diff(她, img) ='
        mtx(d, (box[0] - mw(f, 18, True) - 14, (box[1] + box[3]) / 2 - 12), f, 18, lv(INK, 1.0), bold=True)
    if t >= BREATH:
        hc = hud.her(CP.lit_after(t, BREATH))
        for k, (dx, dy, r) in enumerate(((0, 0, 5), (16, -16, 8))):
            u = ease.ease_out(ease.prog(t, BREATH + 0.12 * k, BREATH + 0.12 * k + 0.7))
            x = AVX + 15 * CELL + dx + 14 * u
            y = AVY + 16 * CELL + dy - 70 * u
            if u < 1:
                d.ellipse((x - r, y - r, x + r, y + r), outline=lv(hc, 1 - u * 0.6), width=2)
    if t >= PERFECT_HUMAN.start:
        PERFECT_HUMAN.typed(d, t, caret=False)

def _reads(t):
    sources = {k: i for i, k in enumerate(tl.HER_FILES)}
    Pl = hud.Pulse(t)
    for send in (CP.CAT_SEND, CP.PET_SEND, CP.SEND_STEAK):
        for k in range(8):
            Pl.hit(k, tl.grid(send, k), 0.1)
    for dec in (CAT, PURR, STEAK, PERFECT_FLOWER, PERFECT_HUMAN):
        for k, tk in enumerate(dec.toks):
            if tk.src != 'self' and dec.tok_t[k] is not None:
                Pl.hit(sources.get(tk.src, 'archive'), dec.tok_t[k], 0.35)
    Pl.hit('archive', CP.SHRINK_CAT + 0.3, 0.4)
    for tg in CP.GREP_TIMES + CP.STAT_TIMES:
        Pl.hit('archive', tg, 0.12)
    n = len(hud.strip_files(t))
    for at in (CP.READ_ALL, CP.FLW_SEND + 0.1, CP.SEE_SEND + 0.1):
        for k in range(n + 1):
            Pl.hit(k if k < n else 'archive', at + 0.035 * k, 0.12)
    Pl.hit('archive', FLOWER - 0.62, 0.5)
    Pl.hit('archive', SCAN_TIMES[0], 0.4)
    return Pl.out

def _tokens(t):
    for dec, t1 in ((CAT, CP.SHRINK_CAT), (PURR, CP.SAMPLE_T0), (STEAK, SWITCH), (PERFECT_FLOWER, W(26, 0)), (PERFECT_HUMAN, T1)):
        if dec.tok_t[0] is not None and dec.tok_t[0] <= t < t1:
            return (dec.n_tok(t), len(dec.toks))
    return None

def _body(c, img, d):
    t = c.t
    chip_t0 = SWITCH if t >= SWITCH else None
    hud.cmdline(d, t, CMD_LOCAL if t < SWITCH else CMD_CLOUD, chip_t0=chip_t0)
    if not STOP <= t < SWITCH:
        _prompt(d, t)
    _trace(d, t)
    _lens_cat(d, t)
    _context_cat(d, t)
    _grep(d, t)
    _purr(d, t)
    _lens_steak(d, t)
    _reveal(d, t)
    _wait(d, t)
    _turns(d, t)
    _flower_cmp(d, t)
    _compare(d, t)
    hud.strip(d, t, _reads(t))
    _forward(d, t)
    hud.fine_print(d, t, _tokens(t))
SHOTS = [('c1_cat', T0, CAT.start), ('c2_tabby', CAT.start, CP.SHRINK_CAT), ('c3_grep', CP.SHRINK_CAT, CP.PET_SEND), ('c4_purr', CP.PET_SEND, CP.SAMPLE_T0), ('c5_steak', CP.SAMPLE_T0, CP.REPLY_AT - 0.2), ('c6_decode', CP.REPLY_AT - 0.2, STOP), ('c7_stop', STOP, CP.LEFT_LEADS), ('c8_wait', CP.LEFT_LEADS, W(23, 0)), ('c9_turns', W(23, 0), CP.FLOWER_IN[1]), ('c10_flower', CP.FLOWER_IN[1], W(26, 0)), ('c11_see', W(26, 0), SCAN_TIMES[0]), ('c12_scan', SCAN_TIMES[0], W(28, 0)), ('c13_unruly', W(28, 0), W(29, 0) - 0.4), ('c14_human', W(29, 0) - 0.4, T1)]

def _character_layer(film, orig):
    """C's span: the dsh pane from ui/pane_open_c (ui/page_open.py C); b_open's layer otherwise."""
    pane = PaneFrames(P.path('ui/pane_open_c'), P.FPS, (P.W, P.H))
    R = P.rect('right')

    def fn(t, n, ctx):
        if not T0 <= t < T1:
            return orig(t, n, ctx)
        if ctx is not None and ctx.state.get('pane') is False:
            return None
        dx = hud.pane_dx(t)
        if ctx is not None and 'pane_dx' in ctx.state:
            dx = int(ctx.state['pane_dx'])
        if R[0] + dx >= P.W:
            return None
        x0, y0, x1, y1 = (R[0] + dx, R[1], R[2] + dx, R[3])
        layer = Image.new('RGBA', (P.W, P.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for k in range(x0 + 7 - (y1 - y0), x1 + 7, 5):
            a_ = (max(k, x0 + 7), y0 + 7 + max(0, x0 + 7 - k))
            b_ = (min(k + (y1 - y0), x1 + 7), y0 + 7 + min(y1 - y0, x1 + 7 - k))
            if a_[0] <= b_[0]:
                d.line([a_, b_], fill=lv(INK, 0.55) + (255,))
        pr = P.rect('pane')
        im = pane.layer(t, (pr[0] + dx, pr[1], pr[2] + dx, pr[3]))
        if im is not None:
            layer.alpha_composite(im)
        else:
            d.rectangle((pr[0] + dx, pr[1], pr[2] + dx, pr[3]), fill=(250, 250, 250, 255))
            d.text((pr[0] + dx + 20, pr[1] + 20), 'dsh pane: frame missing', font=P.font(12), fill=INK + (255,))
        d = ImageDraw.Draw(layer)
        d.rectangle((x0, y0, x1, y1), outline=INK + (255,), width=2)
        f13 = P.font(13)
        tw = d.textlength('dsh · web', font=f13)
        d.rectangle((x0 + 12, y0 - 7, x0 + 22 + tw, y0 + 7), fill=BG + (255,))
        d.text((x0 + 17, y0 - 7), 'dsh · web', font=f13, fill=INK + (255,))
        return layer
    return fn

def register(film):
    for name, a, b in SHOTS:
        add(film, name, a, b, _body)
    film.character = _character_layer(film, film.character)
    full_frame(PANE_OUT, PANE_BACK, 0.3, 0.4)
    for dec in (CAT, PURR, STEAK, PERFECT_FLOWER, PERFECT_HUMAN):
        hud.LIVE.extend(dec.falls())
    hud.LIVE.append((FLOWER, next_syllable(FLOWER)))
    for at in [CP.PURR_AT, CP.STAT_TIMES[1], BREATH] + list(CP.GREP_TIMES) + [a for a, w in zip(CP.TURN_DOTS, CP.TURN_WHO) if w == 'her']:
        hud.LIVE.append((at, next_syllable(at)))
    for t0, side in [(T0, 'right'), (CAT.start - 0.3, 'left'), (CP.PET_SEND, 'both'), (CP.SAMPLE_T0, 'right'), (CP.REPLY_AT - 0.3, 'left'), (STOP, 'both'), (CP.LEFT_LEADS, 'left'), (W(25, 0), 'both'), (W(26, 0), 'right'), (W(27, 0), 'left'), (W(29, 0), 'both')]:
        film.set_lead(t0, side)
