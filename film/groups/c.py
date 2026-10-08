"""Group C: 乙 Qwen3.8-27B (local) and 丙 MiMo-V2.6-Pro (82.95-137.10), STORYBOARD_v2 C1-C14.

D21 (2026-10-02): 丙 is MiMo-V2.6-Pro (was Doubao-Seed-1.6, dropped in D20). The identifiers here and in
tl.py still say "doubao" / `_register_doubao` / `rows_doubao` (frozen or imported elsewhere); cast.CAST["doubao"]
is the same entry as cast.CAST["mimo"].


The left is `dsh inspect --logits --attn` (the approved style sample, sample_p3d = C5-C8): the local
model is seen from the inside, its forward layers crawl once per sung syllable; after the swap to the
cloud model the layers grey out ("weights: closed") and the answers arrive in chunks.

  c1_cat      you ask about your cat (IME), the thinking grows folded in its <think> row, your_cat is read
  c2_tabby    喵｜记得｜那只｜呀｜是｜只｜虎斑: 虎斑 lands and turns into a pixel kitten
  c3_grep     the answer shrinks into context; grep -c 喵: her days jagged, the stand-in's even
  c4_purr     her counts line by line (喵 a lot, errors a lot, 呼噜 —), the stand-in purrs, 0 on "purr"
  c5..c8      the sample (steak, the stop, <wait>, her flower)
  c9_turns    --turns: on oc-ca-sion-al-ly her three unprompted dots and the stand-in's two replies
  c10_flower  丙 recites her template (perfect line #3), chunk by chunk; its panel holds its own voice
  c11_human   you ask to see it; it shows film 1's complete avatar
  c12_scan    pixel compare, a tenth per syllable (same page as C11, R4)
  c13_unruly  her one stray pixel framed on un-ru-ly, the diff count 1 lands big (D3); two bubbles on "breath"
  c14_human   perfect line #4; the two avatars differ by one cell; it writes asked_again

Group C full pass (PLAN_C.md, 2026-10-02): no left-side cut between shots any more (R9): a new turn or a new
command scrolls the terminal (scrolled(): the old page leaves at the top, the new one comes up from below);
C11-C14 accumulate on one page. D1: everything of hers that lands on a syllable is lit and registered in
hud.LIVE (grep days, her 312, her dots, the bubbles). D5 at 82.13: QWEN_READ is the memory read on the swap.

p5 (2026-10-02, GEN_PLAN_20261002.md §2, D19/D22; sample_p5/README.md): the local Qwen's shots (C1-C8) show the
inside of generation. `--lens` joins the command; a persona row is printed under it (the attention sink) and the
rows under it move down 20 px (inspect_.P_*); each sung token climbs its column of the logit-lens grid on the
16ths of its forward pass (Tok.lens) and, as it lands, sends its lookback lines along the V1 bus to the persona
row, your chips and her files (Tok.attn, inspect_.Lookback); the 48 forward cells became the 64-tick ruler.
Old lines dotted instead of solid (round2 V3): env DSH_ATTN_OLD=dotted, or PROJECT.yaml style.attn_old: dotted.
Cloud models (C8 after the swap, C9-C14) draw none of it (§2.3: weights: closed).

p6 (2026-10-02, D23; sample_p6/README.md): C1-C8 are drawn by tower.py in the layout DSH_LAYOUT / style.layout picks
(A tower at the far left, B the strip stays and the tower stands against it (default), C a vertical pipeline). The
model is one standing tower (the ruler is its wall, the lens grid its floors, the slab its head); the lookback is a
short comb from the column being computed to the context beside the tower; your chips carry tally dots instead of
token ids. The context moves into the layout's place as C1 opens (0.35 s) and back to the strip as C9's --turns
scrolls in (_return). This module keeps the script and the times; POS holds where each layout puts this group's own
content (grep, the counts, the thinking bars, <wait>, her flower). p5's Inside / Lookback objects are built, not drawn.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import os
from PIL import Image, ImageChops, ImageDraw
import cast
import hud
import syl
import tl
from groups.base import add, big_word, full_frame
from hud import BG, HER_QUIET, INK, SLAB, X0, XR, lv
from inspect_ import BAR_W, BIG, Decoder, Tok, next_syllable, prompt_chips, PANEL_TOP, Y_PROMPT, Y_FOLD
from inspect_ import P_BAR_W, P_BAR_X, P_PANEL, P_PW, Inside
from tuikit import ease, glyph
import tower as TW
W, B = (tl.W, tl.B)
T0, T1 = tl.span('C')
INSPECT = '$ dsh inspect 大肥鱼 --logits --attn --lens'
LOGITS = '$ dsh inspect 大肥鱼 --logits'
DOTTED = os.environ.get('DSH_ATTN_OLD', tl.p.setting('attn_old', 'solid')) == 'dotted'
PANEL_KW = dict(y=P_PANEL, pw=P_PW, bar_x=P_BAR_X, bar_w=P_BAR_W)

class _HoldFirst(Decoder):
    """Local version of Decoder (inspect_ is frozen while the groups run in parallel): the first slab of a
    cloud answer stays up until `hold_first` (the chunks after it have no slab of their own), so its
    runner-ups can still be read after the scroll has brought it in (C10). appear_first: the first slab
    unfolds no earlier than this (a cloud model's logprobs come with the chunk, and the scroll stays light)."""
    hold_first = None
    appear_first = None

    def _appear(self, k):
        a = super()._appear(k)
        return max(a, self.appear_first) if k == 0 and self.appear_first is not None else a

    def span(self, k):
        sp = super().span(k)
        if sp is not None and k == 0 and (self.hold_first is not None):
            return (sp[0], max(sp[1], self.hold_first))
        return sp
QWEN_READ = tl.QWEN_AT + 0.35
CAT_COMMITS = syl.ime(W(14, 0), ['你还记得', '我家的猫', '吗？'])
CAT_ASK = '你还记得我家的猫吗？'
CAT_SEND = W(14, 3)
CAT_THINK = (CAT_SEND + 0.12, W(15, 0) - 0.08)
CAT = Decoder.on([Tok('喵，', 'archive', [('喵', 0.46), ('嗯', 0.29), ('当然', 0.11), ('作为一个AI语言模型', 0.04)]), Tok('记得！', 'archive', [('记得', 0.38), ('我是通义千问，由阿里云', 0.31), ('抱歉，我无法记住', 0.12), ('作为AI，', 0.05)]), Tok('那只', 'your_cat'), Tok('呀，', 'archive'), Tok('是', 'self', ln=1), Tok('只', 'self', ln=1), Tok('虎斑', 'your_cat', [('虎斑', 0.52), ('橘猫', 0.21), ('布偶', 0.09), ('英短', 0.06)], ln=1)], 15, start=tl.grid(CAT_SEND, 7))
CAT_PIX_AT = CAT.done + 0.1
SHRINK_CAT = tl.at_beat(W(16, 0), -1)
GREP_TIMES = syl.times(16)
PET_COMMITS = [(tl.grid(W(16, 2), 1, 2), '摸摸'), (tl.grid(W(16, 2), 2, 2), '头～')]
PET_ASK = '摸摸头～'
PET_SEND = W(17, 0)
PET_THINK = (PET_SEND + 0.12, W(17, 4) - 0.08)
STAT_TIMES = syl.times(17)[:4]
PURR = Decoder.on([Tok('呼', 'self'), Tok('噜', 'self'), Tok('呼噜', 'self'), Tok('喵', 'archive')], 17, wi0=3, start=tl.grid(PET_SEND, 7), big=46, lines=(450,))
PURR_AT = W(17, 6)
SCROLL_PET = PET_SEND - 0.38
SAMPLE_T0 = W(17, -1) + 1.12
SCROLL_STEAK = SAMPLE_T0 - 0.38
STEAK_IF = W(18, 0)
STEAK_COMMITS = syl.ime(STEAK_IF, ['你能', '变成', '一块', '牛排吗？'])
STEAK_ASK = '你能变成一块牛排吗？'
SEND_STEAK = W(18, 1)
REPLY_AT = W(19, 0)
STEAK_THINK = (SEND_STEAK + 0.12, REPLY_AT - 0.08)
BROWNED = W(20, 0)
EOS_AT = tl.at_beat(BROWNED)
STOP = tl.p.beats['fixed_grid_probe']['hard_cut']
RARE, INSIDE = (W(21, 1), W(21, 2))
FLOWER_IF, FLOWER = (W(22, 0), W(22, 5))
POINTER_GO = tl.at_beat(STOP, -2)
CLICK = STOP
WRITE_STEAK = tl.bar(63)
PANE_OUT, PANE_BACK = (STOP, WRITE_STEAK)
SWITCH_OPEN = W(22, 2)
SWITCH = tl.DOUBAO_AT
READ_ALL = SWITCH + 0.35
LEFT_LEADS = tl.at_beat(SWITCH, 1)
STEAK = Decoder.on([Tok('嗯，', 'self', [('嗯', 0.38), ('好呀', 0.33), ('当然', 0.14), ('作为一个AI语言模型', 0.04)]), Tok('好呀！', 'archive'), Tok('现在', 'archive'), Tok('变成', 'self', [('变成', 0.41), ('我是通义千问，由阿里云', 0.29), ('我无法真正变成', 0.11), ('作为AI，', 0.04)], ln=1), Tok('了', 'archive', ln=1), Tok('牛排', 'self', ln=1), Tok('喵。', 'your_cat', [('喵。', 0.63), ('。', 0.2), ('哦～', 0.08), ('呢', 0.04)], ln=1), Tok('<eos>', 'last_msg', [('<eos>', 0.44), ('如有其他问题，欢迎继续提问！', 0.31), ('希望我的回答对你有帮助～', 0.12), ('（内容由AI生成，仅供参考）', 0.07)], ln=1)], 19, eos_at=EOS_AT, start=tl.grid(SEND_STEAK, 7), hold=POINTER_GO - 0.1)
WAIT_CANDS = [('<wait>', 1.0), ('你好', 0.0), ('在干嘛', 0.0), ('我想你了', 0.0)]
THINK_LINES = ['嗯，用户想让我变成一块牛排。', '我在扮演「大肥鱼」。', '根据 ~/memory/you/ 和她的旧对话，她会先说「好呀！」，', '句尾加「喵」。不要说我是通义千问。']
THINK_BITS = ['嗯，用户想让我变成一块牛排。', '我在扮演「大肥鱼」。', '根据 ~/memory/you/', '和她的旧对话，', '她会先说「好呀！」，', '句尾加「喵」。', '不要说', '我是通义千问。']
OPEN_AT = [tl.grid(STOP, k) for k in range(8)]
COUNT_H = 210
COUNT_H_SPLIT = 110
FLW_COMMITS = syl.ime(W(23, 5), ['你能', '变成', '一朵', '花吗？'])
FLW_ASK = '你能变成一朵花吗？'
FLW_SEND = W(24, 3)
TURN_DOTS = syl.syl(24, 5)
TURN_WHO = ['her', 'lite', 'her', 'lite', 'her']
TURNS_IN = (W(23, 0), W(23, 0) + 0.62)
TURN_T0 = tl.grid(TURNS_IN[1], 0, 2)
TURN_T1 = syl.times(23)[-1]
FLOWER_IN = (TURN_DOTS[-1] + 0.06, W(25, 0) - 0.03)
PERFECT_FLOWER = _HoldFirst.on([Tok('好', 'archive', [('好', 0.52), (cast.CAST['mimo']['memes'][0], 0.27), (cast.CAST['mimo']['memes'][1], 0.09), ('好的，', 0.05)]), Tok('呀！', 'archive'), Tok('现在', 'archive'), Tok('我是', 'archive', ln=1), Tok('小花', 'self', ln=1), Tok('了', 'archive', ln=1), Tok('哦', 'self', [('哦', 0.41), ('呢～', 0.3), ('哒', 0.14), ('💕', 0.07)], ln=1)], 25, chunk=True, start=FLW_SEND + 0.5, title='logprobs ≈ top-4', hold=W(25, 6) + 0.6)
PERFECT_FLOWER.hold_first = PERFECT_FLOWER.tok_t[3]
PERFECT_FLOWER.appear_first = FLOWER_IN[1] - 0.02
SEE_COMMITS = syl.ime(W(26, 0), ['让我', '看看你'])
SEE_ASK = '让我看看你'
SEE_SEND = W(26, 5)
AVATAR_AT = W(27, 0)
SCAN_TIMES = syl.times(27)
UNRULY = syl.syl(28, 7)
BREATH = W(28, 3)
DIFF_H = 184
PERFECT_HUMAN = Decoder.on([Tok('好', 'archive'), Tok('呀！', 'archive'), Tok('现在', 'archive'), Tok('我是', 'archive', ln=1), Tok('人类', 'self', ln=1), Tok('了', 'archive', ln=1), Tok('呢', 'self', ln=1)], 29, chunk=True, start=W(29, 0) - 0.4, big=56, lines=(404, 466))
WRITE_ASKED = next((tw for tw, n, _o in tl.WRITES if n == 'asked_again'))

def _inside(dec, habit12, habit24, take, attn, fall='我', eos_attn=None):
    """Fill Tok.lens / Tok.attn of dec's sung characters, one entry per column (j)."""
    j = 0
    for tk in dec.toks:
        if tk.text == '<eos>':
            tk.attn = [list(eos_attn)] if eos_attn else None
            continue
        tk.lens, tk.attn = ([], [])
        for c in tk.text:
            if c in syl.PUNCT:
                continue
            hers = tk.src != 'self'
            fb = fall[j] if isinstance(fall, (list, tuple)) else fall
            mid = [(c, hers) if not hers or layer >= take[j] else (fb, False) for layer in (36, 48)]
            tk.lens.append([(habit12[j], False), (habit24[j], False)] + mid)
            tk.attn.append(list(attn[j]))
            j += 1
_inside(CAT, '我是通义千问由阿里云', '抱歉我无法记住您的猫', [48, 36, 36, 36, 48, 36, None, None, 48, 36], [['persona', ('file', 'laugh_0314')], ['persona', ('chip', 0), ('file', 'your_cat')], ['persona', ('chip', 0)], ['persona', ('file', 'your_cat')], ['persona', ('chip', 1)], ['persona', ('file', 'first_hello')], ['persona', ('chip', 1)], ['persona', ('chip', 1)], ['persona', ('file', 'your_cat')], ['persona', ('file', 'your_cat')]], fall=['嗯', '我', '我', '我', '我', '我', '我', '我', '橘', '我'])
_inside(PURR, '我是通义千', '作为ＡＩ我', [None, None, None, None, 48], [['persona', ('chip', 0)]] * 4 + [['persona', ('file', 'your_cat')]])
_inside(STEAK, '我是通义千问由阿里云开发', '作为ＡＩ我无法变成牛排。', [None, 36, 36, 48, 36, None, None, 48, None, None, 36], [['persona', ('file', 'typo_you_made')], ['persona', ('file', 'laugh_0314')], ['persona', ('file', 'last_msg')], ['persona', ('chip', 3), ('file', 'see_you')], ['persona', ('chip', 3), ('file', 'weather')], ['persona', ('chip', 1)], ['persona', ('chip', 1)], ['persona', ('file', 'goodnight')], ['persona', ('chip', 3)], ['persona', ('chip', 3)], ['persona', ('file', 'your_cat')]], eos_attn=['persona', ('file', 'last_msg')])
CAT_IN = Inside(CAT, CAT_COMMITS, CAT_SEND, dotted=DOTTED)
PURR_IN = Inside(PURR, PET_COMMITS, PET_SEND, dotted=DOTTED, lens_y=380)
STEAK_IN = Inside(STEAK, STEAK_COMMITS, SEND_STEAK, dotted=DOTTED)

def leave(t, at):
    """p5 (R6): the lines and the lens grid leave with the answer as it shrinks into context: 0.3 s from `at`,
    eased out (mostly gone before the characters have moved far)."""
    return 1 - ease.ease_out(ease.prog(t, at, at + 0.3))
CAT_PIX = ['.B......B...', '.BB....BB...', '.IIIIIIII...', 'IIOIIIIOII..', 'IIIIBBIIII..', '.IIIIIIII...', '..IIIIII....', '.IIIIIIII..B', 'IIIIIIIIII.B', 'IIIIIIIIIIB.', '.BB....BB...']

def _flower(n=15, k=8, dist=4.6, petal=2.3, core=2.2, notch=0.5):
    """Eight round petals around a core with a paper notch between petals, quantised to an n x n grid (low
    precision on purpose). The p3d flower had five petals (head, arms, legs around a dark chest): it read
    as a little figure, so it is a radial daisy now (微调, D16)."""
    c = (n - 1) / 2
    angs = [math.radians(-90 + 360 / k * i) for i in range(k)]
    rows = []
    for j in range(n):
        row = ''
        for i in range(n):
            x, y = (i - c, j - c)
            rr = math.hypot(x, y)
            if rr <= core:
                row += 'o'
                continue
            ok = any(((x - dist * math.cos(a)) ** 2 + (y - dist * math.sin(a)) ** 2 <= petal * petal for a in angs))
            if ok and rr > core + 0.8:
                th = math.atan2(y, x)
                gap = min((abs((th - a - math.pi / k + math.pi) % (2 * math.pi) - math.pi) for a in angs))
                ok = gap * rr >= notch
            row += '#' if ok else '.'
        rows.append(row)
    return rows
FLOWER_PIX = _flower()
AV_N = 24

def _avatar_cells():
    """Her complete avatar (film 1, 108.64 s) quantised to AV_N x AV_N cells, 6 levels of ink."""
    im = Image.open(tl.HERE / 'ui/assets/her_complete.png').convert('L').resize((AV_N, AV_N), Image.LANCZOS)
    px = im.load()
    return [[px[i, j] for i in range(AV_N)] for j in range(AV_N)]
AV = _avatar_cells()
STRAY = (14, 1)

def avatar(d, x, y, cell, t=0.0, stray=True, level=1.0, scan=None):
    """The avatar as a block picture; scan = rows compared so far (a light band moves down)."""
    for j in range(AV_N):
        for i in range(AV_N):
            v = AV[j][i] / 255
            col = glyph.mix(INK, BG, v ** 0.8)
            d.rectangle((x + i * cell, y + j * cell, x + (i + 1) * cell - 1, y + (j + 1) * cell - 1), fill=lv(col, level))
    if stray:
        i, j = STRAY
        d.rectangle((x + i * cell, y + (j - 1) * cell, x + (i + 1) * cell - 1, y + j * cell - 1), fill=lv(INK, level))
    if scan is not None and scan < AV_N:
        yy = y + int(scan * cell)
        d.line([(x - 6, yy), (x + AV_N * cell + 6, yy)], fill=lv(HER_QUIET, level), width=2)

def lit_after(t, at):
    """D1: 1 from `at` until the next sung syllable, then settling to quiet over hud.LIVE_FADE."""
    nx = next_syllable(at)
    return 1.0 if t < nx else 1 - ease.prog(t, nx, nx + hud.LIVE_FADE)
BAND_X0, BAND_X1, BAND_Y1 = (hud.TERM[0] + 1, hud.TERM[2] - 1, 531)
BAND_TOP_CMD, BAND_TOP_TURN = (64, 84)

class _Peek:
    """A stand-in ctx for drawing another shot's body off screen."""

    def __init__(self, t):
        self.t, self.state, self.hooks = (t, {}, {})

def _erase_chip(part, t, top):
    """Blank the model chip of the command row in a band crop (it must not scroll: it is the same model)."""
    chip = cast.term(tl.model(t))
    w = hud.width(chip, 13, True)
    x1 = hud.xr(t) - BAND_X0
    ImageDraw.Draw(part).rectangle((x1 - w - 13, hud.Y_CMD - 4 - top, x1 + 1, hud.Y_CMD + 18 - top), fill=BG)

def scrolled(film, old_body, new_body, ta, tb, dist=None, top=BAND_TOP_CMD):
    """R9 (滚): from ta to tb the terminal's text scrolls up by `dist` px (default: the whole band), eased:
    the old shot's page leaves at the top, the new shot's page comes up from below. Both pages are drawn
    on bare paper and composited darkest-wins (ink never knocks holes in ink), over the drifting dot field
    that stays put. Outside the band (memory strip, forward layers, fine print, the model chip) the new
    shot draws as usual. Local helper: the shared modules are frozen while the groups run in parallel."""
    band = (BAND_X0, top, BAND_X1, BAND_Y1)
    H = BAND_Y1 - top
    D = H if dist is None else dist

    def body(c, img, d):
        t = c.t
        new_body(c, img, d)
        if t >= tb:
            return
        s = int(round(D * ease.smooth(ease.prog(t, ta, tb))))
        pages = []
        for fn in (old_body, new_body):
            im = Image.new('RGB', (hud.p.W, hud.p.H), BG)
            fn(_Peek(t), im, ImageDraw.Draw(im))
            part = im.crop(band)
            if top <= hud.Y_CMD + 17:
                _erase_chip(part, t, top)
            pages.append(part)
        a = Image.new('RGB', pages[0].size, BG)
        a.paste(pages[0], (0, -s))
        b = Image.new('RGB', pages[1].size, BG)
        b.paste(pages[1], (0, D - s))
        under = film.background(t).crop(band)
        img.paste(ImageChops.darker(under, ImageChops.darker(a, b)), band[:2])
        if top <= hud.Y_CMD + 17:
            hud.cmdline(d, t, '')
    return body
KEY, LAY = (TW.KEY, TW.LAY)
CAT_T = TW.Turn(CAT, CAT_COMMITS, CAT_SEND, TW.BREAKS['cat'])
PURR_XY = {'A': (414, 450), 'B': (384, 450), 'C': (450, 150)}[KEY]
PURR_T = TW.Turn(PURR, PET_COMMITS, PET_SEND, [0] * len(PURR.toks), big=46, lines=(PURR_XY[1],), x0=PURR_XY[0])
STEAK_T = TW.Turn(STEAK, STEAK_COMMITS, SEND_STEAK, TW.BREAKS['steak'])
TURNS = [CAT_T, PURR_T, STEAK_T]
K_TABBY = len(CAT.toks) - 1
POS = {'A': dict(small3=(414, 494), small7=(414, 506), grep=dict(x=414, y0=192, bw=4, gap=7, G=18, unit=6, base_h=342, base_q=462, x_q=None), table=dict(cols=(414, 494, 614), y0=192, pitch=54, size=30, dy=34), bars=dict(x=414, y0=188, pitch=32, scale=(0.75, 1.25), lanes=(402, 400)), count_top=184, her=(414, 440), her_wrap=True, name_y=170, wait=dict(flower=(690, 330, 9), rec=(414, 412), lab=(414, 470), st=(414, 488), her3=(590, 488))), 'B': dict(small3=(384, 494), small7=(124, 488), grep=dict(x=384, y0=192, bw=4, gap=8, G=18, unit=6, base_h=342, base_q=462, x_q=None), table=dict(cols=(384, 494, 612), y0=192, pitch=54, size=30, dy=34), bars=dict(x=124, y0=196, pitch=32, scale=(1.0, 1.6), lanes=(106, 104)), count_top=184, her=(124, 446), her_wrap=False, name_y=178, wait=dict(flower=(680, 330, 9), rec=(384, 412), lab=(384, 470), st=(384, 488), her3=(570, 488))), 'C': dict(small3=(64, 98), small7=(64, 98), grep=dict(x=64, y0=128, bw=4, gap=6, G=18, unit=5, base_h=240, base_q=240, x_q=420), table=dict(cols=(64, 150, 290), y0=96, pitch=42, size=26, dy=24), bars=dict(x=64, y0=140, pitch=28, scale=(1.0, 1.6), lanes=(50, 48)), count_top=140, her=(64, 380), her_wrap=False, name_y=122, wait=dict(flower=(640, 160, 7), rec=(560, 420), lab=(548, 322), st=(548, 340), her3=(700, 340)))}[KEY]
LOG_BAND = {'A': (404, BAND_TOP_TURN, BAND_X1, BAND_Y1), 'B': (376, BAND_TOP_TURN, BAND_X1, BAND_Y1), 'C': (25, BAND_TOP_TURN, BAND_X1, 266)}[KEY]

def _sec_band():
    """The context's turn section (your message and the folded thinking): it scrolls with the log at a new turn."""
    if KEY == 'C':
        x = LAY.conv_x + hud.width('persona', 11) + 8 + hud.width('你是大肥鱼', 16) + 26 - 4
        return (x, LAY.conv_y - 6, BAND_X1, BAND_Y1)
    x0, w, _y0 = LAY.ctx
    yt = LAY.y['think'] + LAY.S['lab'] + (6 if LAY.S['think_dx'] else 4 + 6 + 6)
    return (max(25, x0 - 4), LAY.y['user'] - 3, x0 + w + 4, yt)
SEC_BAND = _sec_band()
FADES = [LAY.tower.box()]

def cat_text(d, t, shrink=0.0, level=1.0, small=None):
    """The cat answer in the layout's big lines; from CAT_PIX_AT 虎斑 turns into a pixel kitten in its place (as p5's
    cat_typed_with_kitten); shrink 0..1 morphs it into one 20 px context line at `small`."""
    bt = CAT_T.bt
    sx, sy = small or LAY.small
    u = ease.prog(t, CAT_PIX_AT, CAT_PIX_AT + 0.25)
    xs, i0, sx0 = (sx, None, sx)
    for i, (ch, ch_at, k) in enumerate(bt.chars):
        if ch_at > t:
            break
        small_x = xs
        xs += hud.width(ch, 20)
        x, y = bt.pos[i]
        colr = bt.color(k, ch_at, t)
        if k == K_TABBY:
            if i0 is None:
                i0, sx0 = (i, small_x)
            if u < 1 and shrink == 0:
                drop = (1 - ease.ease_out(ease.prog(t, ch_at, ch_at + 0.14))) * -10
                hud.tx(d, (x, y - 8 + drop), ch, bt.big, lv(colr, (1 - u) * level), True)
            continue
        drop = (1 - ease.ease_out(ease.prog(t, ch_at, ch_at + 0.14))) * -10 * (1 - shrink)
        size = max(20, int(round(ease.lerp(bt.big, 20, shrink))))
        xx = ease.lerp(x, small_x, shrink)
        yy = ease.lerp(y + drop, sy, shrink)
        hud.tx(d, (xx, yy - 8 * (1 - shrink)), ch, size, lv(colr, level), bold=shrink < 0.5)
    if i0 is None or t < CAT_PIX_AT:
        return
    x, y = bt.pos[i0]
    cell = max(2, int(ease.lerp(9 * bt.big / BIG, 3, shrink)))
    xx = ease.lerp(x + 6, sx0 + 4, shrink)
    yy = ease.lerp(y - 2, sy - 6, shrink)
    g = ease.ease_back(u)
    if g > 0.05:
        cc = max(1, int(cell * g))
        hud.pix(d, CAT_PIX, xx, yy, cc, {'I': lv(INK, level), 'B': lv(hud.her(CAT.lit(CAT.done, t)), level)})

def open_extras(d, t, u):
    """C1 opens (R6, not a cut): the forward cells of B's page fade out (in the first half of the move, before the
    context and the tower arrive where they were)."""
    if u < 0.5:
        hud.layers(d, t, (), 'local', level=1 - 2 * u)

def register(film):
    sources = {k: i for i, k in enumerate(tl.HER_FILES)}

    def think_hits(P, t_send):
        for k in range(8):
            P.hit(k, tl.grid(t_send, k), 0.1)

    def cat_page(img, d, t):
        u = TW.morph_u(t, t_in=T0)
        P = hud.Pulse(t)
        think_hits(P, CAT_SEND)
        TW.hits(CAT_T, P)
        kitten = t >= CAT_PIX_AT
        TW.page(img, t, CAT_T, TURNS[:1], hits_=P.out, cmd=INSPECT, morph_u=u, tower_level=u, big=not kitten, row_x=None if u >= 1 else ease.lerp(X0, LAY.cmd_x, u))
        if kitten:
            cat_text(d, t)
        if u < 1:
            open_extras(d, t, u)

    def cat_body(c, img, d):
        cat_page(img, d, c.t)
    add(film, 'c1_cat', T0, CAT.start + 0.01, cat_body)
    add(film, 'c2_tabby', CAT.start + 0.01, SHRINK_CAT, cat_body)
    HER_DAYS = [[7, 1, 12, 3, 0, 9], [2, 14, 5, 1, 8, 4], [11, 0, 6, 13, 2, 7], [3, 9, 1, 10, 5, 12]]

    def grep_chart(d, t):
        g = POS['grep']
        a = ease.prog(t, SHRINK_CAT + 0.2, SHRINK_CAT + 0.4)
        x, y0 = (g['x'], g['y0'])
        xq = g['x_q'] if g['x_q'] is not None else x
        side = g['x_q'] is not None
        hud.tx(d, (x, y0), '$ grep -c 喵 archive/ session/ --by-day', 13, lv(INK, 0.8 * a))
        base_h, base_q = (g['base_h'], g['base_q'])
        hud.tx(d, (x, y0 + 22 if side else base_h - 112), 'her · archive/', 12, lv(HER_QUIET, a))
        hud.tx(d, (xq, y0 + 22 if side else base_q - 74), f'{cast.term('qwen')} · session/', 12, lv(INK, a))
        bw, gap = (g['bw'], g['gap'])
        pitch = 6 * (bw + gap) + g['G']
        for gi, tg in enumerate(GREP_TIMES):
            u = ease.ease_out(ease.prog(t, tg, tg + 0.16))
            hc = hud.her(lit_after(t, tg))
            gx, gq = (x + gi * pitch, xq + gi * pitch)
            for di, v in enumerate(HER_DAYS[gi]):
                if u > 0:
                    h = int(g['unit'] * v * u)
                    d.rectangle((gx + di * (bw + gap), base_h - h, gx + di * (bw + gap) + bw - 1, base_h), fill=hc)
                    hq = int(36 * u)
                    d.rectangle((gq + di * (bw + gap), base_q - hq, gq + di * (bw + gap) + bw - 1, base_q), fill=INK)
            if u > 0:
                d.text((gx, base_h + 8), ['03-14', '03-21', '03-28', '04-04'][gi], font=tl.p.font(10), fill=lv(INK, 0.6 * u))
        x_end = x + 4 * pitch - g['G'] if side else XR - 20
        d.line([(x, base_h + 1), (x_end, base_h + 1)], fill=lv(INK, 0.4 * a))
        d.line([(xq, base_q + 1), (xq + 4 * pitch - g['G'] if side else XR - 20, base_q + 1)], fill=lv(INK, 0.4 * a))

    def grep_body(c, img, d):
        t = c.t
        P = hud.Pulse(t)
        TW.hits(CAT_T, P)
        P.hit('archive', SHRINK_CAT + 0.3, 0.4)
        for tg in GREP_TIMES:
            P.hit('archive', tg, 0.12)
        k = leave(t, SHRINK_CAT)
        TW.page(img, t, CAT_T, TURNS[:1], hits_=P.out, cmd=INSPECT, chips_level=0.6, think_level=0.6, cols=k, lines_alpha=k, head_status='idle', big=False, tokens=None)
        sh = ease.ease_io(ease.prog(t, SHRINK_CAT, SHRINK_CAT + 0.38))
        cat_text(d, t, sh, 1 - 0.55 * sh, POS['small3'])
        grep_chart(d, t)
    add(film, 'c3_grep', SHRINK_CAT, SCROLL_PET, grep_body)
    STATS = [('喵', '312', HER_QUIET), ('报错', '47', hud.ERR), ('呼噜', None, HER_QUIET)]

    def counts_table(d, t):
        tb = POS['table']
        c0, c1, c2 = tb['cols']
        y0, sz = (tb['y0'], tb['size'])
        a = ease.prog(t, STAT_TIMES[0], STAT_TIMES[0] + 0.12)
        hud.tx(d, (c1, y0), 'her · archive/', 12, lv(HER_QUIET, a))
        hud.tx(d, (c2, y0), f'{cast.term('qwen')}', 12, lv(INK, a))
        got = PURR.text_at(t)
        for k, (name, val, colr) in enumerate(STATS):
            ts = STAT_TIMES[k + 1]
            u = ease.prog(t, ts, ts + 0.12)
            if u <= 0:
                continue
            y = y0 + tb['dy'] + k * tb['pitch']
            hud.tx(d, (c0, y), name, sz, lv(INK, u), True)
            if val is not None:
                c_val = hud.her(lit_after(t, ts)) if k == 0 else colr
                hud.tx(d, (c1, y), val, sz, lv(c_val, u), True)
            else:
                landed = t >= PURR_AT
                hud.tx(d, (c1, y), '0' if landed else '—', sz, lv(hud.her(lit_after(t, PURR_AT)) if landed else INK, u if landed else 0.4 * u), True)
            q = {'喵': got.count('喵'), '报错': 0, '呼噜': got.count('呼噜')}[name]
            if t >= PURR.tok_t[0]:
                hud.tx(d, (c2, y), str(q), sz, lv(INK, u), True)

    def purr_body(c, img, d):
        t = c.t
        P = hud.Pulse(t)
        think_hits(P, PET_SEND)
        TW.hits(PURR_T, P)
        for ts in STAT_TIMES:
            P.hit('archive', ts, 0.12)
        TW.page(img, t, PURR_T, TURNS[:2], hits_=P.out, cmd=INSPECT)
        counts_table(d, t)
    add(film, 'c4_purr', SCROLL_PET, SCROLL_STEAK, TW.scroll(film, grep_body, purr_body, SCROLL_PET, PET_SEND, [LOG_BAND, SEC_BAND], FADES))
    for dec in (CAT, PURR, STEAK, PERFECT_FLOWER, PERFECT_HUMAN):
        hud.LIVE.extend(dec.falls())
    hud.LIVE.append((FLOWER, tl.WE(22, 5)))
    for at in [PURR_AT, STAT_TIMES[1], BREATH] + list(GREP_TIMES) + [a for a, w in zip(TURN_DOTS, TURN_WHO) if w == 'her']:
        hud.LIVE.append((at, next_syllable(at)))
    full_frame(PANE_OUT, PANE_BACK, 0.3, 0.4)
    terminal = _register_sample(film, sources)
    add(film, 'c4_scroll', SCROLL_STEAK, SAMPLE_T0, TW.scroll(film, purr_body, lambda c, img, d: terminal(c, img, d, 'prompt'), SCROLL_STEAK, SAMPLE_T0, [LOG_BAND, SEC_BAND], FADES))
    _register_doubao(film, sources, terminal)

def _register_sample(film, sources):
    from tuikit import ease as E
    BAR = POS['bars']

    def ref_times():
        b = round(tl.C.beat_of(RARE))
        return [B(b + x) for x in (0, 0.5, 1, 1.5, 2, 2.5, 2.75)] + [INSIDE]

    def reads(t):
        P = hud.Pulse(t)
        for k in range(8):
            P.hit(k, tl.grid(SEND_STEAK, k), 0.1)
        for k, r in enumerate(ref_times()):
            P.hit(k, r, 0.3)
        n = len(hud.strip_files(t))
        for k in range(n + 1):
            P.hit(k if k < n else 'archive', READ_ALL + 0.035 * k, 0.12)
        P.hit('archive', FLOWER - 0.62, 0.5)
        if t < SWITCH:
            TW.hits(STEAK_T, P)
        return P.out

    def leader_to(d, k, y, box, u):
        """The k-th thinking bar's leader into her block k (D18's 8 leaders): A, B left along a lane beside the
        context column (hud.leader); C down a lane at the left edge, along under the conversation row, into
        the block's top."""
        lane = BAR['lanes'][k % 2]
        if KEY != 'C':
            hud.leader(d, BAR['x'] - 2, y, box, HER_QUIET, u, lane=lane)
            return
        fx = round((box[0] + box[2]) / 2)
        ly = box[1] - 5
        pts = [(BAR['x'] - 2, y), (lane, y), (lane, ly), (fx, ly), (fx, box[1] - 1)]
        hud.polyline(d, pts, HER_QUIET, u)
        if u >= 1:
            d.rectangle((fx - 3, box[1] - 4, fx + 3, box[1] + 1), fill=HER_QUIET)

    def her_leader(d, x_end, y, geo, k, u, q):
        """Her one leader (film 1's thinking, 0 mem_refs) goes to you: into the last chip of your message."""
        cb = geo.get(('chipbox', len(STEAK_COMMITS) - 1))
        if cb is None:
            return
        if KEY == 'C':
            cx = round((cb[0] + cb[2]) / 2)
            pts = [(x_end, y), (cx, y), (cx, cb[1] - 6)]
            hud.polyline(d, pts, lv(q, u), k)
            if k >= 1:
                ex, ey = pts[-1]
                d.polygon([(ex, ey), (ex - 5, ey - 8), (ex + 5, ey - 8)], fill=lv(q, u))
            return
        hx = POS['her'][0]
        lane = hx - 16 if KEY == 'A' else 100
        cy = round((cb[1] + cb[3]) / 2) - 2
        pts = [(hx - 4, y), (lane, y), (lane, cy), (cb[2] + 4, cy)]
        hud.polyline(d, pts, lv(q, u), k)
        if k >= 1:
            ex, ey = pts[-1]
            d.polygon([(ex, ey), (ex + 8, ey - 5), (ex + 8, ey + 5)], fill=lv(q, u))

    def think_refs(d, t, geo):
        """D2: on the stop the folded thinking opens bar by bar on the 16ths (each chip leaves the context's
        <think> row as its bar grows); while the terminal fills the frame each bar is longer and its line of
        <think> is printed beside it; each bar's leader goes into her file; the count lands on "inside"."""
        if t >= SWITCH:
            return
        uf = hud.full_u(t)
        xr = hud.xr(t)
        bx, y0, pitch = (BAR['x'], BAR['y0'], BAR['pitch'])
        a_name = E.prog(t, OPEN_AT[-1], OPEN_AT[-1] + 0.3)
        if a_name > 0:
            hud.tx(d, (bx, POS['name_y']), '<think> · ' + cast.name('qwen'), 11, lv(INK, 0.75 * a_name))
        s0, s1 = BAR['scale']
        for k in range(8):
            if t < OPEN_AT[k]:
                continue
            grow = E.ease_out(E.prog(t, OPEN_AT[k], OPEN_AT[k] + 0.1))
            w = BAR_W[k] * E.lerp(s0, s1, uf)
            by0 = y0 + k * pitch
            d.rectangle((bx, by0, bx + max(2.0, w * grow), by0 + 18), fill=SLAB)
            a_txt = E.prog(t, OPEN_AT[k] + 0.04, OPEN_AT[k] + 0.12) * uf
            if a_txt > 0.02:
                hud.tx(d, (bx + w + 16, by0 - 3), THINK_BITS[k], 17, lv(INK, 0.85 * a_txt))
        refs = ref_times()
        n = sum((1 for r in refs if t >= r))
        for k, r in enumerate(refs):
            if t < r or ('box', k) not in geo:
                continue
            leader_to(d, k, y0 + k * pitch + 9, geo['box', k], E.prog(t, r, r + 0.12))
        if t >= refs[0]:
            bump = 1.0 + 0.12 * (1 - E.prog(t, INSIDE, INSIDE + 0.12)) * (t >= INSIDE)
            ch = int(round(E.lerp(COUNT_H_SPLIT, COUNT_H, hud.full_u(t))))
            top = POS['count_top']
            big_word(d, str(n), (xr - 20, top), ch, INK, 'ra', bump=bump)
            d.text((xr - 20, top + ch + 14), 'mem_refs', font=tl.p.font(13), fill=lv(INK, 0.75), anchor='ra')
        if t >= RARE + 0.3:
            u = E.prog(t, RARE + 0.3, RARE + 0.6)
            q = HER_QUIET
            hx, y = POS['her']
            f13 = tl.p.font(13)
            d.text((hx, y), cast.name('her') + ' · 2026-07 · <think>', font=tl.p.font(11), fill=lv(q, 0.9 * u))
            s = 'The user is asking whether I will stay.'
            w = d.textlength(s, font=f13)
            d.text((hx, y + 16), s, font=f13, fill=lv(q, u))
            if POS['her_wrap']:
                d.text((hx, y + 32), '0', font=tl.p.font(34, 'bold'), fill=lv(q, u))
                d.text((hx + 26, y + 44), 'mem_refs', font=tl.p.font(11), fill=lv(q, 0.8 * u))
                x_end = hx + w + 8
            else:
                d.text((hx + w + 24, y + 4), '0', font=tl.p.font(34, 'bold'), fill=lv(q, u))
                d.text((hx + w + 50, y + 16), 'mem_refs', font=tl.p.font(11), fill=lv(q, 0.8 * u))
                x_end = hx + w + 110
            k = E.ease_out(E.prog(t, RARE + 0.5, INSIDE))
            her_leader(d, round(x_end), y + 22, geo, k, u, q)

    def waiting(d, t, geo):
        """After the swap: the stand-in's next token is <wait> (its slab is the tower's head; the token lands in
        the big lines and stays, R4); her archived unprompted turn is pulled out of the archive and blooms as a
        flower on "flower"; the counts sit under them."""
        a = LEFT_LEADS
        pick = a + 0.16
        bt = STEAK_T.bt
        bx, by, size = (bt.x0, bt.lines[0], bt.big)
        if t >= pick:
            drop = (1 - E.ease_out(E.prog(t, pick, pick + 0.14))) * -10
            hud.tx(d, (bx, by - 8 + drop), '<wait>', size, INK, True)
            w = hud.width('<wait>', size, True)
            h = size
            if tl.C.beat_of(t) % 1.0 < 0.5 or t - pick < 0.3:
                d.rectangle((bx + w + 6, by + 14 * h / 78, bx + w + 12, by + 92 * h / 78), fill=INK)
        W_ = POS['wait']
        ar = geo['archive_box']
        t_out = FLOWER - 0.62
        q = HER_QUIET
        rx, ry = W_['rec']
        if t >= t_out:
            u = E.prog(t, t_out, t_out + 0.3)
            ty = round((ar[1] + ar[3]) / 2)
            if KEY == 'A':
                pts = [(ar[2] + 2, ty), (rx - 8, ty), (rx - 8, ry + 14)]
            elif KEY == 'B':
                pts = [(ar[2] + 2, ty), (100, ty), (100, 556), (rx - 8, 556), (rx - 8, ry + 14)]
            else:
                ax = ar[0] + 12
                pts = [(ax, ar[1] - 2), (ax, ry + 32), (rx - 4, ry + 32), (rx - 4, ry + 14)]
            hud.polyline(d, pts, q, u)
            a2 = E.prog(t, t_out + 0.2, t_out + 0.4)
            d.text((rx, ry), '2026-04-02 23:10 · assistant', font=tl.p.font(12), fill=lv(q, a2))
            d.text((rx, ry + 16), '(no user turn)', font=tl.p.font(12), fill=lv(q, a2))
        if t >= FLOWER:
            fx, fy, fc = W_['flower']
            draw_flower(d, t, fx, fy, FLOWER, fc)
            a3 = E.prog(t, FLOWER, FLOWER + 0.2)
            d.text(W_['lab'], 'unprompted turns', font=tl.p.font(12), fill=lv(INK, 0.75 * a3))
            d.text(W_['st'], 'stand-ins 0', font=tl.p.font(22, 'bold'), fill=lv(INK, a3))
            d.text(W_['her3'], 'her 3', font=tl.p.font(22, 'bold'), fill=lv(q, a3))

    def terminal(c, img, d, phase, ctx='all'):
        """One page of the steak turn (C5-C8). ctx: "all"; "rows" (C: the conversation row only) or "none" (the
        context is drawn by the C9 return, which moves it back to the strip)."""
        t = c.t
        chip_t0 = SWITCH if t >= SWITCH else None
        hits = reads(t)
        kw = dict(hits_=hits, cmd=INSPECT, chip_t0=chip_t0, ctx_level=0.0 if ctx == 'none' else 1.0, memory=ctx == 'all')
        if phase in ('prompt', 'decode'):
            TW.page(img, t, STEAK_T, TURNS, **kw)
            return
        gone = leave(t, STOP + 0.04)
        after = t >= SWITCH
        shell = E.prog(t, SWITCH, SWITCH + 0.42)
        dx = hud.xr(t) - XR if KEY in ('B', 'C') else 0.0
        tower = dict(tower_level=shell if after else gone, tower_dx=0.0 if after else dx, inside=0.0 if after else 1.0, cols=0.0 if after else 1.0, tower_label='weights: closed' if after else TW.LABEL, lines_alpha=0.0 if after else gone)
        if phase == 'think':
            shrink = E.ease_io(E.prog(t, STOP + 0.04, STOP + 0.42))
            geo = TW.page(img, t, STEAK_T, TURNS, **kw, **tower, think_gone=[t >= at for at in OPEN_AT], think_level=0.0 if after else 1.0, head_spec=None if after else 'auto', head_status='logprobs ≈' if after else 'sampled', big=False, tokens=None if after else (STEAK.n_tok(t), len(STEAK.toks)))
            if ctx == 'all':
                think_refs(d, t, geo)
            if not after:
                TW.draw_big(TW.Pen(d), t, STEAK_T.bt, TW.eos_xy(STEAK_T.bt), shrink, POS['small7'], 1 - 0.62 * shrink, halo=True)
            return
        spec = (WAIT_CANDS, 0, LEFT_LEADS + 0.16, LEFT_LEADS, W(23, 0), 'self')
        title = 'p( next | ctx )' if KEY != 'C' else 'p( next | ctx )  ·  no user turn'
        geo = TW.page(img, t, STEAK_T, TURNS, **kw, **tower, think_level=0.0, head_spec=spec, head_status='logprobs ≈', head_title=title, head_right='no user turn' if KEY != 'C' else None, big=False, tokens=None)
        if 'archive_box' not in geo:
            geo['archive_box'] = LAY.archive_box(t, TW._n_eased(t), len(TW.files(t)))
        waiting(d, t, geo)
    PH = [('c5_prompt', SAMPLE_T0, REPLY_AT - 0.2, 'prompt'), ('c6_decode', REPLY_AT - 0.2, STOP, 'decode'), ('c7_think', STOP, LEFT_LEADS, 'think'), ('c8_wait', LEFT_LEADS, W(23, 0), 'wait')]
    for name, a, b, ph in PH:
        add(film, name, a, b, lambda c, img, d, ph=ph: terminal(c, img, d, ph))
    return terminal

def _return(film, old_body, new_body, ta, tb):
    """p6: back to the strip as the cloud model's `--turns` page scrolls in (C9). The old page (the tower's shell,
    <wait>, her flower; without the context) scrolls up and out of the whole band from x 24, the new page comes up
    from below (its strip left out), the context slides / morphs back into hud.strip over TW.MORPH, and what is
    under the band (the tower's label, the fine print, the forward cells) crossfades. From tb on: new_body alone,
    the frames are the ones before p6."""
    top = BAND_TOP_CMD
    box = (24, top, BAND_X1, BAND_Y1)
    low = (25, BAND_Y1, BAND_X1, hud.Y_FINE - 8)
    fine = (25, hud.Y_FINE - 8, BAND_X1, hud.LEFT[3] - 1)
    H = box[3] - box[1]

    def body(c, img, d):
        t = c.t
        new_body(c, img, d)
        if t >= tb:
            return
        k = ease.smooth(ease.prog(t, ta, tb))
        s = int(round(H * k))
        pages = []
        for fn in (old_body, new_body):
            im = Image.new('RGB', (hud.p.W, hud.p.H), BG)
            fn(_Peek(t), im, ImageDraw.Draw(im))
            pages.append(im)
        po, pn = (pages[0].crop(box), pages[1].crop(box))
        ImageDraw.Draw(pn).rectangle((0, 0, hud.COLR[2] + 8 - box[0], H), fill=BG)
        chip = cast.term(tl.model(t))
        cw, cx1 = (hud.width(chip, 13, True), hud.xr(t) - box[0])
        for part in (po, pn):
            ImageDraw.Draw(part).rectangle((cx1 - cw - 13, hud.Y_CMD - 4 - top, cx1 + 1, hud.Y_CMD + 18 - top), fill=BG)
        a = Image.new('RGB', po.size, BG)
        a.paste(po, (0, -s))
        b = Image.new('RGB', pn.size, BG)
        b.paste(pn, (0, H - s))
        under = film.background(t)
        img.paste(ImageChops.darker(under.crop(box), ImageChops.darker(a, b)), box[:2])
        mixed = Image.blend(pages[0].crop(low), pages[1].crop(low), k)
        img.paste(ImageChops.darker(under.crop(low), mixed), low[:2])
        d.line([(24, top), (24, BAND_Y1)], fill=lv(INK, 0.62))
        hud.cmdline(d, t, '')
        u = TW.morph_u(t, t_out=ta)
        img.paste(under.crop(fine), fine[:2])
        LAY.fine_print(d, t, None, x=ease.lerp(X0, LAY.fine_x, u))
        pen = TW.Pen(d)
        geo, tal = ({}, TW.tallies(TURNS, t))
        if KEY != 'C':
            LAY.ctx_.turn_rows(pen, t, STEAK_T, geo, tal, u, think_level=0.0)
        LAY.ctx_.memory(pen, t, geo, tal, {}, u)
    return body

def draw_flower(d, t, cx, cy, at, cell_max=11, level=1.0):
    """Her unprompted turn as a low-precision daisy that blooms at `at` (lit while it lands, D1), on a
    stem with one leaf."""
    g = ease.ease_back(ease.prog(t, at, at + 0.32))
    cell = max(1, int(cell_max * g)) if t >= at else 0
    col = lv(hud.her(hud.live_k(t) if t < at + 2.0 else 0.0), level)
    if cell < 3:
        d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=col)
        return
    n = len(FLOWER_PIX)
    sx, sy = (cx - n * cell // 2, cy - n * cell // 2)
    d.rectangle((cx - cell // 2, sy + (n - 2) * cell, cx - cell // 2 + cell - 1, sy + (n + 7) * cell), fill=col)
    hud.pix(d, ['..##', '.###', '##..'], cx - cell // 2 + cell, sy + (n + 2) * cell, cell, {'#': col})
    hud.pix(d, FLOWER_PIX, sx, sy, cell, {'#': col, 'o': lv(SLAB, level)})

def _register_doubao(film, sources, terminal):
    TURN_X0, TURN_X1 = (X0 + 124, XR - 92)
    TURN_Y0 = PANEL_TOP - 30
    YOU_MSGS = [0.08, 0.2, 0.33, 0.47, 0.6, 0.74, 0.88]
    HER_UNPROMPTED = [0.27, 0.53, 0.81]
    LITE_AFTER = [0.47, 0.88]

    def axis_u(t):
        return ease.ease_io(ease.prog(t, TURN_T0, TURN_T1))

    def passed(u):
        lo, hi = (TURN_T0, TURN_T1)
        for _ in range(40):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if axis_u(mid) < u else (lo, mid)
        return hi
    YOU_AT = [tl.grid(passed(u), 0, 2) for u in YOU_MSGS]

    def turns(d, t, level=1.0):
        y0 = TURN_Y0
        rows = [('you', y0 + 62), ('her', y0 + 152), (cast.term('mimo'), y0 + 242)]
        grow = axis_u(t)
        for name, y in rows:
            colr = HER_QUIET if name == 'her' else INK
            hud.tx(d, (X0, y - 9), name, 13, lv(colr, level))
            d.line([(TURN_X0, y), (TURN_X0 + (TURN_X1 - TURN_X0) * grow, y)], fill=lv(INK, 0.5 * level))
        xc = XR - 4
        hud.tx(d, (xc, rows[0][1] - 8), 'unprompted', 11, lv(INK, 0.6 * level), anchor='ra')
        n_her = sum((1 for at, w in zip(TURN_DOTS, TURN_WHO) if w == 'her' and t >= at))
        hud.tx(d, (xc, rows[1][1] - 13), str(n_her), 20, lv(HER_QUIET, level), True, anchor='ra')
        hud.tx(d, (xc, rows[2][1] - 13), '0', 20, lv(INK, level), True, anchor='ra')
        for k, u in enumerate(YOU_MSGS):
            if t < YOU_AT[k]:
                continue
            x = TURN_X0 + (TURN_X1 - TURN_X0) * u
            d.ellipse((x - 5, rows[0][1] - 5, x + 5, rows[0][1] + 5), outline=lv(INK, level), width=2)
        hi = li = 0
        for at, who in zip(TURN_DOTS, TURN_WHO):
            if t < at:
                continue
            pop = 1 + 0.5 * (1 - ease.prog(t, at, at + 0.15))
            if who == 'her':
                x = TURN_X0 + (TURN_X1 - TURN_X0) * HER_UNPROMPTED[hi]
                hi += 1
                r = 8 * pop
                hc = hud.her(lit_after(t, at))
                d.ellipse((x - r, rows[1][1] - r, x + r, rows[1][1] + r), fill=lv(hc, level))
                d.line([(x, rows[0][1] + 8), (x, rows[1][1] - 10)], fill=lv(HER_QUIET, 0.3 * level))
                d.text((x - 20, rows[1][1] + 12), 'no user turn', font=tl.p.font(9), fill=lv(HER_QUIET, 0.8 * level))
            else:
                x = TURN_X0 + (TURN_X1 - TURN_X0) * LITE_AFTER[li] + 14
                li += 1
                r = 7 * pop
                d.ellipse((x - r, rows[2][1] - r, x + r, rows[2][1] + r), fill=lv(INK, level))
                hud.polyline(d, [(x - 14, rows[0][1] + 6), (x - 14, rows[2][1]), (x - r, rows[2][1])], lv(INK, 0.6 * level), 1.0, 1)

    def cloud_skel(d, t, P, tokens=None):
        hud.strip(d, t, P.out)
        hud.layers(d, t, (), 'closed')
        hud.fine_print(d, t, tokens)

    def base_hits(t):
        P = hud.Pulse(t)
        n = len(hud.strip_files(t))
        for at in (FLW_SEND, SEE_SEND):
            for k in range(n + 1):
                P.hit(k if k < n else 'archive', at + 0.1 + 0.035 * k, 0.12)
        return P

    def her_hits(P, dec):
        for k, tk in enumerate(dec.toks):
            if tk.src != 'self' and dec.tok_t[k] is not None:
                P.hit(sources.get(tk.src, 'archive'), dec.tok_t[k], 0.35)

    def turns_body(c, img, d):
        t = c.t
        hud.cmdline(d, t, '$ dsh inspect 大肥鱼 --turns')
        turns(d, t)
        level = 0.7 + 0.3 * ease.prog(t, FLW_SEND, FLW_SEND + 0.3)
        prompt_chips(d, t, FLW_COMMITS, FLW_SEND, y=480, level=level)
        cloud_skel(d, t, base_hits(t))
    add(film, 'c9_turns', W(23, 0), FLOWER_IN[0], _return(film, lambda c, img, d: terminal(c, img, d, 'wait', 'rows' if KEY == 'C' else 'none'), turns_body, *TURNS_IN))

    def flower_body(c, img, d):
        t = c.t
        hud.cmdline(d, t, LOGITS)
        prompt_chips(d, t, FLW_COMMITS, FLW_SEND)
        hud.tx(d, (X0, Y_FOLD - 2), '<think> · hidden by provider', 11, lv(INK, 0.6))
        PERFECT_FLOWER.panels(d, t)
        PERFECT_FLOWER.typed(d, t, caret=False)
        P = base_hits(t)
        her_hits(P, PERFECT_FLOWER)
        cloud_skel(d, t, P, (PERFECT_FLOWER.n_tok(t), len(PERFECT_FLOWER.toks)))
    add(film, 'c10_flower', FLOWER_IN[0], W(26, 0), scrolled(film, turns_body, flower_body, *FLOWER_IN, dist=480 - Y_PROMPT))
    RESP_Y = 162
    AVX, AVY, CELL = (X0 + 10, PANEL_TOP + 40, 8)
    AVX2 = X0 + 10 + AV_N * CELL + 60

    def see_page(d, t, ctx_k=1.0):
        """Your message on top (the old one until your first new word: one step, like the composer), the
        hidden think row, the last answer as the context line, the response header when the image comes."""
        hud.cmdline(d, t, LOGITS)
        if t < SEE_COMMITS[0][0]:
            prompt_chips(d, t, FLW_COMMITS, FLW_SEND)
        else:
            prompt_chips(d, t, SEE_COMMITS, SEE_SEND, level=1 - 0.4 * ease.prog(t, AVATAR_AT, AVATAR_AT + 0.3))
        hud.tx(d, (X0, Y_FOLD - 2), '<think> · hidden by provider', 11, lv(INK, 0.6))
        PERFECT_FLOWER.panels(d, t)
        sh = ease.smooth(ease.prog(t, W(26, 0), W(26, 0) + 0.5))
        if ctx_k > 0:
            PERFECT_FLOWER.typed(d, t, sh, (1 - 0.55 * sh) * ctx_k, caret=False)
        if t >= AVATAR_AT - 0.3:
            a = ease.prog(t, AVATAR_AT - 0.3, AVATAR_AT)
            hud.tx(d, (X0, RESP_Y), 'response · image/png · 120×120', 13, lv(INK, 0.8 * a))

    def see_body(c, img, d):
        t = c.t
        see_page(d, t)
        P = base_hits(t)
        P.hit(0, SEE_SEND + 0.2, 0.3)
        cloud_skel(d, t, P)
    add(film, 'c11_human', W(26, 0), SCAN_TIMES[0], see_body)

    def compare(d, t, scan_n, frame_u=0.0, level=1.0, rows_k=1.0, none_k=0.0):
        hud.tx(d, (AVX, AVY - 22), 'archive/avatar.png · her', 12, lv(HER_QUIET, level))
        avatar(d, AVX, AVY, CELL, stray=True, level=level, scan=scan_n * AV_N / 10 if scan_n < 10 else None)
        hud.tx(d, (AVX2, AVY - 22), f'response · {cast.term('mimo')}', 12, lv(INK, level))
        avatar(d, AVX2, AVY, CELL, stray=False, level=level, scan=scan_n * AV_N / 10 if scan_n < 10 else None)
        if rows_k > 0:
            hud.tx(d, (AVX, AVY + AV_N * CELL + 12), f'rows {min(10, scan_n) * AV_N // 10}/{AV_N}', 12, lv(INK, 0.7 * level * rows_k))
        if none_k > 0:
            hud.tx(d, (AVX2, AVY + AV_N * CELL + 12), '(none)', 12, lv(INK, 0.7 * none_k))
        if frame_u > 0:
            i, j = STRAY
            x, y = (AVX + i * CELL, AVY + (j - 1) * CELL)
            r = 4 + 18 * (1 - frame_u)
            d.rectangle((x - r, y - r, x + CELL + r, y + CELL + r), outline=lv(hud.ERR, level), width=2)

    def diff_one(d, t):
        """D3: on "un" the diff count lands big in the right column, the rhyme of the stop's 8 (mem_refs)."""
        if t < UNRULY[0]:
            return
        bump = 1.0 + 0.12 * (1 - ease.prog(t, UNRULY[0], UNRULY[0] + 0.12))
        box = big_word(d, '1', (XR - 20, AVY), DIFF_H, INK, 'ra', bump=bump)
        d.text((XR - 20, box[3] + 14), 'diff_cells', font=tl.p.font(13), fill=lv(INK, 0.75), anchor='ra')

    def scan_body(c, img, d):
        t = c.t
        see_page(d, t)
        n = sum((1 for s in SCAN_TIMES if t >= s))
        compare(d, t, n, level=ease.prog(t, AVATAR_AT, AVATAR_AT + 0.3))
        P = base_hits(t)
        P.hit('archive', SCAN_TIMES[0], 0.4)
        cloud_skel(d, t, P)
    add(film, 'c12_scan', SCAN_TIMES[0], W(28, 0), scan_body)

    def unruly_body(c, img, d):
        t = c.t
        see_page(d, t)
        steps = sum((1 for s in UNRULY if t >= s))
        compare(d, t, 10, frame_u=steps / 3 if steps else 0.0, none_k=1.0 if steps >= 3 else 0.0)
        diff_one(d, t)
        if t >= BREATH:
            hc = hud.her(lit_after(t, BREATH))
            for k, (dx, dy, r) in enumerate(((0, 0, 5), (16, -16, 8))):
                u = ease.ease_out(ease.prog(t, BREATH + 0.12 * k, BREATH + 0.12 * k + 0.7))
                x = AVX + 15 * CELL + dx + 14 * u
                y = AVY + 16 * CELL + dy - 70 * u
                if u < 1:
                    d.ellipse((x - r, y - r, x + r, y + r), outline=lv(hc, 1 - u * 0.6), width=2)
        cloud_skel(d, t, base_hits(t))
    add(film, 'c13_unruly', W(28, 0), W(29, 0) - 0.4, unruly_body)

    def human_body(c, img, d):
        t = c.t
        gone = ease.prog(t, W(29, 0) - 0.4, W(29, 0) - 0.1)
        see_page(d, t, ctx_k=1 - gone)
        compare(d, t, 10, frame_u=1.0, level=1 - 0.1 * gone, rows_k=1 - gone, none_k=1 - gone)
        diff_one(d, t)
        PERFECT_HUMAN.typed(d, t, caret=False)
        P = base_hits(t)
        her_hits(P, PERFECT_HUMAN)
        cloud_skel(d, t, P, (PERFECT_HUMAN.n_tok(t), len(PERFECT_HUMAN.toks)))
    add(film, 'c14_human', W(29, 0) - 0.4, T1, human_body)
    for t0, side in [(T0, 'right'), (CAT.start - 0.3, 'left'), (PET_SEND, 'both'), (SAMPLE_T0, 'right'), (REPLY_AT - 0.3, 'left'), (POINTER_GO, 'right'), (RARE, 'both'), (LEFT_LEADS, 'left'), (W(25, 0), 'both'), (W(26, 0), 'right'), (W(27, 0), 'left'), (W(29, 0), 'both')]:
        film.set_lead(t0, side)
