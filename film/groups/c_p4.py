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
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
from PIL import Image, ImageChops, ImageDraw
import cast
import hud
import syl
import tl
from groups.base import add, big_word, full_frame
from hud import BG, HER, HER_QUIET, INK, SLAB, X0, XR, lv
from inspect_ import BAR_W, BIG, L1, Decoder, Tok, next_syllable, prompt_chips, slab, think_bars, PANEL_TOP, Y_PROMPT, Y_FOLD
from tuikit import ease, glyph
W, B = (tl.W, tl.B)
T0, T1 = tl.span('C')
INSPECT = '$ dsh inspect 大肥鱼 --logits --attn'
LOGITS = '$ dsh inspect 大肥鱼 --logits'

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

def register(film):
    sources = {k: i for i, k in enumerate(tl.HER_FILES)}

    def her_hits(P, toks_dec):
        for k, tk in enumerate(toks_dec.toks):
            if tk.src not in ('self',) and toks_dec.tok_t[k] is not None:
                P.hit(sources.get(tk.src, 'archive'), toks_dec.tok_t[k], 0.35)

    def think_hits(P, t_send):
        for k in range(8):
            P.hit(k, tl.grid(t_send, k), 0.1)

    def think_segs(t_send):
        segs, prev = ([], t_send)
        for k in range(8):
            g = tl.grid(t_send, k)
            segs.append((prev, g))
            prev = g
        return segs

    def local_skel(d, t, P, segs, tokens=None):
        hud.strip(d, t, P.out)
        hud.layers(d, t, segs, 'local')
        hud.fine_print(d, t, tokens)
    CAT_SEGS = think_segs(CAT_SEND) + CAT.segs()

    def cat_body(c, img, d):
        t = c.t
        hud.cmdline(d, t, INSPECT)
        prompt_chips(d, t, CAT_COMMITS, CAT_SEND)
        think_bars(d, t, CAT_SEND, folded=True)
        P = hud.Pulse(t)
        think_hits(P, CAT_SEND)
        her_hits(P, CAT)
        if t >= CAT.start:
            CAT.panels(d, t)
            if t < CAT_PIX_AT:
                CAT.typed(d, t)
            else:
                cat_typed_with_kitten(d, t)
        local_skel(d, t, P, CAT_SEGS, (CAT.n_tok(t), len(CAT.toks)))

    def cat_typed_with_kitten(d, t, shrink=0.0, level=1.0):
        u = ease.prog(t, CAT_PIX_AT, CAT_PIX_AT + 0.25)
        k_tabby = len(CAT.toks) - 1
        for i, (ch, ch_at, k) in enumerate(CAT.chars):
            x, y = CAT.pos[i]
            colr = CAT.color(k, ch_at, t)
            if k == k_tabby:
                if u < 1 and shrink == 0:
                    hud.tx(d, (x, y - 8), ch, CAT.big, lv(colr, (1 - u) * level), True)
                continue
            size = max(20, int(round(ease.lerp(CAT.big, 20, shrink))))
            xx = ease.lerp(x, CAT.small[i], shrink)
            yy = ease.lerp(y, 488, shrink)
            hud.tx(d, (xx, yy - 8 * (1 - shrink)), ch, size, lv(colr, level), bold=shrink < 0.5)
        i0 = next((i for i, (_c, _a, k) in enumerate(CAT.chars) if k == k_tabby))
        x, y = CAT.pos[i0]
        cell = max(2, int(ease.lerp(9, 3, shrink)))
        xx = ease.lerp(x + 6, CAT.small[i0] + 4, shrink)
        yy = ease.lerp(y - 2, 482, shrink)
        g = ease.ease_back(u)
        if g > 0.05:
            cc = max(1, int(cell * g))
            hud.pix(d, CAT_PIX, xx, yy, cc, {'I': lv(INK, level), 'B': lv(hud.her(CAT.lit(CAT.done, t)), level)})
    add(film, 'c1_cat', T0, CAT.start + 0.01, cat_body)
    add(film, 'c2_tabby', CAT.start + 0.01, SHRINK_CAT, cat_body)
    HER_DAYS = [[7, 1, 12, 3, 0, 9], [2, 14, 5, 1, 8, 4], [11, 0, 6, 13, 2, 7], [3, 9, 1, 10, 5, 12]]

    def grep_body(c, img, d):
        t = c.t
        hud.cmdline(d, t, INSPECT)
        prompt_chips(d, t, CAT_COMMITS, CAT_SEND, level=0.6)
        think_bars(d, t, CAT_SEND, level=0.6, folded=True)
        sh = ease.ease_io(ease.prog(t, SHRINK_CAT, SHRINK_CAT + 0.38))
        cat_typed_with_kitten(d, t, sh, 1 - 0.55 * sh)
        y0 = PANEL_TOP + 4
        a = ease.prog(t, SHRINK_CAT + 0.2, SHRINK_CAT + 0.4)
        hud.tx(d, (X0, y0), '$ grep -c 喵 archive/ session/ --by-day', 13, lv(INK, 0.8 * a))
        base_h, base_q = (y0 + 150, y0 + 270)
        hud.tx(d, (X0, base_h - 112), 'her · archive/', 12, lv(HER_QUIET, a))
        hud.tx(d, (X0, base_q - 74), f'{cast.term('qwen')} · session/', 12, lv(INK, a))
        bw, gap, x = (4, 12, X0)
        for gi, tg in enumerate(GREP_TIMES):
            u = ease.ease_out(ease.prog(t, tg, tg + 0.16))
            hc = hud.her(lit_after(t, tg))
            gx = x + gi * (6 * (bw + gap) + 22)
            for di, v in enumerate(HER_DAYS[gi]):
                bx = gx + di * (bw + gap)
                if u > 0:
                    h = int(6 * v * u)
                    d.rectangle((bx, base_h - h, bx + bw - 1, base_h), fill=hc)
                    hq = int(36 * u)
                    d.rectangle((bx, base_q - hq, bx + bw - 1, base_q), fill=INK)
            if u > 0:
                d.text((gx, base_h + 8), ['03-14', '03-21', '03-28', '04-04'][gi], font=tl.p.font(10), fill=lv(INK, 0.6 * u))
        d.line([(X0, base_h + 1), (XR - 20, base_h + 1)], fill=lv(INK, 0.4 * a))
        d.line([(X0, base_q + 1), (XR - 20, base_q + 1)], fill=lv(INK, 0.4 * a))
        P = hud.Pulse(t)
        P.hit('archive', SHRINK_CAT + 0.3, 0.4)
        for tg in GREP_TIMES:
            P.hit('archive', tg, 0.12)
        hud.strip(d, t, P.out)
        hud.layers(d, t, [], 'local', 'idle · waiting for input')
        hud.fine_print(d, t)
    add(film, 'c3_grep', SHRINK_CAT, SCROLL_PET, grep_body)
    STATS = [('喵', '312', HER_QUIET), ('报错', '47', hud.ERR), ('呼噜', None, HER_QUIET)]
    PURR_SEGS = think_segs(PET_SEND) + PURR.segs()

    def purr_body(c, img, d):
        t = c.t
        hud.cmdline(d, t, INSPECT)
        prompt_chips(d, t, PET_COMMITS, PET_SEND)
        think_bars(d, t, PET_SEND, folded=True)
        y0 = PANEL_TOP + 4
        cols = (X0 + 150, X0 + 330)
        a = ease.prog(t, STAT_TIMES[0], STAT_TIMES[0] + 0.12)
        hud.tx(d, (cols[0], y0), 'her · archive/', 12, lv(HER_QUIET, a))
        hud.tx(d, (cols[1], y0), f'{cast.term('qwen')}', 12, lv(INK, a))
        for k, (name, val, colr) in enumerate(STATS):
            ts = STAT_TIMES[k + 1]
            u = ease.prog(t, ts, ts + 0.12)
            if u <= 0:
                continue
            y = y0 + 34 + k * 54
            hud.tx(d, (X0, y), name, 30, lv(INK, u), True)
            if val is not None:
                c_val = hud.her(lit_after(t, ts)) if k == 0 else colr
                hud.tx(d, (cols[0], y), val, 30, lv(c_val, u), True)
            else:
                landed = t >= PURR_AT
                hud.tx(d, (cols[0], y), '0' if landed else '—', 30, lv(hud.her(lit_after(t, PURR_AT)) if landed else INK, u if landed else 0.4 * u), True)
            got = PURR.text_at(t)
            q = {'喵': got.count('喵'), '报错': 0, '呼噜': got.count('呼噜')}[name]
            if t >= PURR.tok_t[0]:
                hud.tx(d, (cols[1], y), str(q), 30, lv(INK, u), True)
        if t >= PURR.start:
            PURR.typed(d, t)
        P = hud.Pulse(t)
        think_hits(P, PET_SEND)
        for ts in STAT_TIMES:
            P.hit('archive', ts, 0.12)
        P.hit(sources['your_cat'], PURR.tok_t[3], 0.35)
        local_skel(d, t, P, PURR_SEGS, (PURR.n_tok(t), len(PURR.toks)))
    add(film, 'c4_purr', SCROLL_PET, SCROLL_STEAK, scrolled(film, grep_body, purr_body, SCROLL_PET, PET_SEND, top=BAND_TOP_TURN))
    for dec in (CAT, PURR, STEAK, PERFECT_FLOWER, PERFECT_HUMAN):
        hud.LIVE.extend(dec.falls())
    hud.LIVE.append((FLOWER, tl.WE(22, 5)))
    for at in [PURR_AT, STAT_TIMES[1], BREATH] + list(GREP_TIMES) + [a for a, w in zip(TURN_DOTS, TURN_WHO) if w == 'her']:
        hud.LIVE.append((at, next_syllable(at)))
    full_frame(PANE_OUT, PANE_BACK, 0.3, 0.4)
    terminal = _register_sample(film, sources)
    add(film, 'c4_scroll', SCROLL_STEAK, SAMPLE_T0, scrolled(film, purr_body, lambda c, img, d: terminal(c, img, d, 'prompt'), SCROLL_STEAK, SAMPLE_T0, top=BAND_TOP_TURN))
    _register_doubao(film, sources, terminal)

def _register_sample(film, sources):
    from tuikit import ease as E
    SEGS = []
    prev = SEND_STEAK
    for k in range(8):
        g = tl.grid(SEND_STEAK, k)
        SEGS.append((prev, g))
        prev = g
    SEGS += STEAK.segs()
    SEGS.append((READ_ALL, READ_ALL + tl.C.BEAT))
    PROMPT_END = [X0 + 400]

    def ref_times():
        b = round(tl.C.beat_of(RARE))
        return [B(b + x) for x in (0, 0.5, 1, 1.5, 2, 2.5, 2.75)] + [INSIDE]

    def reads(t):
        P = hud.Pulse(t)
        for k in range(8):
            P.hit(k, tl.grid(SEND_STEAK, k), 0.1)
        for k, tk in enumerate(STEAK.toks):
            if tk.src != 'self':
                P.hit(sources.get(tk.src, 'archive'), STEAK.tok_t[k], 0.35)
        for k, r in enumerate(ref_times()):
            P.hit(k, r, 0.3)
        n = len(hud.strip_files(t))
        for k in range(n + 1):
            P.hit(k if k < n else 'archive', READ_ALL + 0.035 * k, 0.12)
        P.hit('archive', FLOWER - 0.62, 0.5)
        return P.out

    def open_bars(d, t, gone):
        """D2: on the stop the folded thinking opens bar by bar on the 16ths; while the terminal fills the
        frame each bar is longer and its line of <think> is printed beside it (the process prints it)."""
        uf = hud.full_u(t)
        d.text((X0, Y_FOLD - 2), '<think>', font=tl.p.font(11), fill=lv(INK, 0.75 * (1 - gone)))
        a_name = E.prog(t, OPEN_AT[-1], OPEN_AT[-1] + 0.3) * (1 - gone)
        if a_name > 0:
            hud.tx(d, (X0 + 60, Y_FOLD - 3), cast.name('qwen'), 11, lv(INK, 0.75 * a_name))
        for k in range(8):
            if t < OPEN_AT[k]:
                fx = X0 + 60 + k * 30
                d.rectangle((fx, Y_FOLD + 2.5, fx + 24, Y_FOLD + 8.5), fill=lv(SLAB, 1 - gone))
                continue
            grow = E.ease_out(E.prog(t, OPEN_AT[k], OPEN_AT[k] + 0.1))
            w = BAR_W[k] * E.lerp(1.0, 1.6, uf)
            by0 = PANEL_TOP + 8 + k * 32
            d.rectangle((X0, by0, X0 + max(2.0, w * grow), by0 + 18), fill=lv(SLAB, 1 - gone))
            a_txt = E.prog(t, OPEN_AT[k] + 0.04, OPEN_AT[k] + 0.12) * uf * (1 - gone)
            if a_txt > 0.02:
                hud.tx(d, (X0 + w + 16, by0 - 3), THINK_BITS[k], 17, lv(INK, 0.85 * a_txt))

    def think_refs(d, t):
        gone = 1.0 if t >= SWITCH else 0.0
        if gone >= 1:
            return
        open_bars(d, t, gone)
        xr = hud.xr(t)
        refs = ref_times()
        n = sum((1 for r in refs if t >= r))
        for k, r in enumerate(refs):
            if t < r:
                continue
            u = E.prog(t, r, r + 0.12)
            y = PANEL_TOP + 8 + k * 32 + 9
            hud.leader(d, X0 - 2, y, hud.block_rect(k, t), HER_QUIET, u, lane=106 - k % 2 * 2)
        if t >= refs[0]:
            bump = 1.0 + 0.12 * (1 - E.prog(t, INSIDE, INSIDE + 0.12)) * (t >= INSIDE)
            ch = int(round(E.lerp(COUNT_H_SPLIT, COUNT_H, hud.full_u(t))))
            big_word(d, str(n), (xr - 20, PANEL_TOP - 4), ch, INK, 'ra', bump=bump)
            d.text((xr - 20, PANEL_TOP - 4 + ch + 14), 'mem_refs', font=tl.p.font(13), fill=lv(INK, 0.75), anchor='ra')
        if t >= RARE + 0.3:
            u = E.prog(t, RARE + 0.3, RARE + 0.6)
            q = HER_QUIET
            y = 488 - 52
            f13 = tl.p.font(13)
            d.text((X0, y), cast.name('her') + ' · 2026-07 · <think>', font=tl.p.font(11), fill=lv(q, 0.9 * u))
            w = d.textlength('The user is asking whether I will stay.', font=f13)
            d.text((X0, y + 16), 'The user is asking whether I will stay.', font=f13, fill=lv(q, u))
            d.text((X0 + w + 24, y + 4), '0', font=tl.p.font(34, 'bold'), fill=lv(q, u))
            d.text((X0 + w + 50, y + 16), 'mem_refs', font=tl.p.font(11), fill=lv(q, 0.8 * u))
            k = E.ease_out(E.prog(t, RARE + 0.5, INSIDE))
            pts = [(X0 + w + 120, y + 22), (xr + 6, y + 22), (xr + 6, Y_PROMPT + 14), (PROMPT_END[0] + 4, Y_PROMPT + 14)]
            hud.polyline(d, pts, lv(q, u), k)
            if k >= 1:
                ex, ey = pts[-1]
                d.polygon([(ex, ey), (ex + 8, ey - 5), (ex + 8, ey + 5)], fill=lv(q, u))
    FX, FY, FCELL = (X0 + 486, PANEL_TOP + 102, 9)
    REC_X, REC_Y = (FX - 67, 412)

    def waiting(d, t):
        """After the swap: the stand-in's next token is <wait> (left column; it stays, R4); her archived
        unprompted turn blooms as a flower in the right column on "flower"; the counts sit under each."""
        a = LEFT_LEADS
        pick = a + 0.16
        slab(d, t, WAIT_CANDS, 0, pick, a, W(23, 0), 'p( next | ctx )  ·  no user turn', 'self')
        if t >= pick:
            drop = (1 - E.ease_out(E.prog(t, pick, pick + 0.14))) * -10
            hud.tx(d, (X0, L1 - 8 + drop), '<wait>', BIG, INK, True)
            w = hud.width('<wait>', BIG, True)
            if tl.C.beat_of(t) % 1.0 < 0.5 or t - pick < 0.3:
                d.rectangle((X0 + w + 6, L1 + 14, X0 + w + 12, L1 + 92), fill=INK)
        ar = hud.archive_rect(t)
        t_out = FLOWER - 0.62
        q = HER_QUIET
        if t >= t_out:
            u = E.prog(t, t_out, t_out + 0.3)
            ty = (ar[1] + ar[3]) / 2
            pts = [(ar[2] + 2, ty), (112, ty), (112, 456), (REC_X - 8, 456), (REC_X - 8, REC_Y + 14)]
            hud.polyline(d, pts, q, u)
            a2 = E.prog(t, t_out + 0.2, t_out + 0.4)
            d.text((REC_X, REC_Y), '2026-04-02 23:10 · assistant', font=tl.p.font(12), fill=lv(q, a2))
            d.text((REC_X, REC_Y + 16), '(no user turn)', font=tl.p.font(12), fill=lv(q, a2))
        if t >= FLOWER:
            draw_flower(d, t, FX, FY, FLOWER, FCELL)
            a3 = E.prog(t, FLOWER, FLOWER + 0.2)
            d.text((X0, 470), 'unprompted turns', font=tl.p.font(12), fill=lv(INK, 0.75 * a3))
            d.text((X0, 488), 'stand-ins 0', font=tl.p.font(22, 'bold'), fill=lv(INK, a3))
            d.text((REC_X, 488), 'her 3', font=tl.p.font(22, 'bold'), fill=lv(q, a3))

    def terminal(c, img, d, phase):
        t = c.t
        chip_t0 = SWITCH if t >= SWITCH else None
        hud.cmdline(d, t, INSPECT, chip_t0=chip_t0)
        PROMPT_END[0] = prompt_chips(d, t, STEAK_COMMITS, SEND_STEAK)
        if phase in ('prompt', 'decode'):
            think_bars(d, t, SEND_STEAK, folded=True)
        if phase == 'decode':
            STEAK.panels(d, t)
            STEAK.typed(d, t)
        if phase == 'think':
            shrink = E.ease_io(E.prog(t, STOP + 0.04, STOP + 0.42))
            if t < SWITCH:
                STEAK.typed(d, t, shrink, 1 - 0.62 * shrink)
            think_refs(d, t)
        if phase == 'wait':
            waiting(d, t)
        who = tl.model(t)
        hud.strip(d, t, reads(t))
        hud.layers(d, t, SEGS, 'local' if cast.kind(who) == 'local' else 'closed')
        hud.fine_print(d, t, (STEAK.n_tok(t), len(STEAK.toks)) if t < SWITCH else None)
    PH = [('c5_prompt', SAMPLE_T0, REPLY_AT - 0.2, 'prompt'), ('c6_decode', REPLY_AT - 0.2, STOP, 'decode'), ('c7_think', STOP, LEFT_LEADS, 'think'), ('c8_wait', LEFT_LEADS, W(23, 0), 'wait')]
    for name, a, b, ph in PH:
        add(film, name, a, b, lambda c, img, d, ph=ph: terminal(c, img, d, ph))
    return terminal

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
    add(film, 'c9_turns', W(23, 0), FLOWER_IN[0], scrolled(film, lambda c, img, d: terminal(c, img, d, 'wait'), turns_body, *TURNS_IN))

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
