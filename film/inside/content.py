"""What the inside plates show, taken from the film's own script so the plates and the terminal never disagree:
answers and their sung times from groups.c_p4 (Decoder.chars), your messages from its IME commits, her files from
tl.HER_FILES. The per-character reads and lens columns are the p5/p6 tables (groups/c.py `_inside`, FACTS X28,
invented), copied here because groups/c_p4.py predates them.

A Turn is one answer: chars [Ch], the candidates per token, your chips and when it was sent.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from dataclasses import dataclass, field
import cast
import syl
import tl
from groups import c_p4 as C
MODEL_LOCAL = cast.LOCAL['alias'].replace('blackcat-', '').replace('-q4', '')

@dataclass
class Ch:
    ch: str
    t: float
    tok: int
    hers: bool
    reads: list = field(default_factory=list)
    lens: list = field(default_factory=list)
    sung: bool = True

@dataclass
class Turn:
    chars: list
    cands: dict
    chips: list
    send: float
    start: float
    eos_at: float | None = None
    eos_reads: list = field(default_factory=list)
    tokens: list = field(default_factory=list)

    @property
    def sung(self):
        return [c for c in self.chars if c.sung]

    @property
    def done(self):
        return self.chars[-1].t

def _key(a):
    if a == 'persona':
        return 'persona'
    if a[0] == 'chip':
        return f'chip{a[1]}'
    if a[0] in ('file', 'hist', 'mem'):
        return f'{a[0]}:{a[1]}'
    return 'archive'

def build_turn(dec, commits, send, attn, habit12, habit24, take, fall='我', eos_attn=None):
    chars, j = ([], 0)
    for c, at, k in dec.chars:
        tk = dec.toks[k]
        hers = tk.src != 'self'
        if c in syl.PUNCT:
            chars.append(Ch(c, at, k, hers, sung=False))
            continue
        fb = fall[j] if isinstance(fall, (list, tuple)) else fall
        mid = [(c, hers) if not hers or (take[j] is not None and layer >= take[j]) else (fb, False) for layer in (36, 48)]
        reads = [(_key(a), 0.45 if a == 'persona' else 1.0) for a in attn[j]]
        chars.append(Ch(c, at, k, hers, reads, [(habit12[j], False), (habit24[j], False)] + mid))
        j += 1
    cands = {k: list(tk.cands) for k, tk in enumerate(dec.toks) if tk.cands}
    eos_reads = [(_key(a), 0.45 if a == 'persona' else 1.0) for a in eos_attn] if eos_attn else []
    return Turn(chars, cands, list(commits), send, dec.start, dec.eos_at, eos_reads, [tk.text for tk in dec.toks])
CAT = build_turn(C.CAT, C.CAT_COMMITS, C.CAT_SEND, [['persona', ('file', 'laugh_0314')], ['persona', ('chip', 0), ('file', 'your_cat')], ['persona', ('chip', 0)], ['persona', ('file', 'your_cat')], ['persona', ('chip', 1)], ['persona', ('file', 'first_hello')], ['persona', ('chip', 1)], ['persona', ('chip', 1)], ['persona', ('file', 'your_cat')], ['persona', ('file', 'your_cat')]], '我是通义千问由阿里云', '抱歉我无法记住您的猫', [48, 36, 36, 36, 48, 36, None, None, 48, 36], fall=['嗯', '我', '我', '我', '我', '我', '我', '我', '橘', '我'])
STEAK = build_turn(C.STEAK, C.STEAK_COMMITS, C.SEND_STEAK, [['persona', ('file', 'typo_you_made')], ['persona', ('file', 'laugh_0314')], ['persona', ('file', 'last_msg')], ['persona', ('chip', 3), ('file', 'see_you')], ['persona', ('chip', 3), ('file', 'weather')], ['persona', ('chip', 1)], ['persona', ('chip', 1)], ['persona', ('file', 'goodnight')], ['persona', ('chip', 3)], ['persona', ('chip', 3)], ['persona', ('file', 'your_cat')]], '我是通义千问由阿里云开发', '作为ＡＩ我无法变成牛排。', [None, 36, 36, 48, 36, None, None, 48, None, None, 36], eos_attn=['persona', ('file', 'last_msg')])
HER_FILES = list(tl.HER_FILES)

def _merged():
    import groups.g as GG
    P = 'persona'
    fl, bl, mi = (('hist', 'h_flower'), ('hist', 'h_bloom'), ('hist', 'h_miss'))
    attn = [[P, fl, bl, mi], [P, bl], [P, fl], [P, fl], [P, fl], [P, bl], [P, bl], [P, ('mem', 'merged')], [P, mi], [P, mi], [P, mi], [P, mi]]
    n = len(attn)
    return build_turn(GG.MSG, [], GG.FLOWER, attn, '我是深度求索的助手很高兴', '你好请问有什么可以帮助你', [None] * n, eos_attn=[P, mi])
MERGED = _merged()

def retime(turn, times, start=None):
    """The same answer laid on other syllables (G3 replays the merged one's message column by column)."""
    import copy
    tc = copy.deepcopy(turn)
    k = 0
    for i, c in enumerate(tc.chars):
        if c.sung:
            c.t = times[k]
            k += 1
        elif i:
            c.t = tc.chars[i - 1].t
    if tc.eos_at is not None:
        tc.eos_at = times[k]
    tc.start = times[0] - 0.3 if start is None else start
    return tc
