"""The inside shots of full film v2 (BUILD_V2_20261003.md §3): name, span, renderer. Times come from the film's
own modules (tl, groups.*), never typed as seconds except where noted."""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import syl
import tl
import groups.g as GG
from groups import c_p4 as C
from .city import SPLIT
from . import content as K

def _c2():
    from .arcs import ArcsPlate, Item
    groups = [('persona', [Item('你是大肥鱼', 'persona'), Item('…'), Item('说话带喵')]), ('memory/you/', [Item('laugh_0314', 'file:laugh_0314', 'her'), Item('your_cat', 'file:your_cat', 'her'), Item('first_hello', 'file:first_hello', 'her'), Item('…'), Item('+5', None, 'faint')]), ('you', [Item('你还记得', 'chip0'), Item('我家的猫', 'chip1'), Item('吗？', 'chip2')])]
    return ArcsPlate(K.CAT, groups, C.CAT_SEND, status=f'{K.MODEL_LOCAL} · local · 64 layers')

def _b9():
    from .tower import TowerB9
    return TowerB9(tl.QWEN_AT, tl.bar(47))

def _c6_spec(hist_keys=None):
    from .board import Row
    persona = ['你', '是', '大', '肥', '鱼', '，', '一只', '住在', '终端', '里', '的', '猫', '，', '说话', '结尾', '带', '喵', '。']
    hk = hist_keys or {}
    return [('sys', 'sys', [Row('sys', '<|im_start|>', 3.4), Row('sys', 'system', 3.4)]), ('persona', 'persona', [Row('persona', w, 3.4, 'persona') for w in persona]), ('memory', 'memory/you/', [Row('memory', n, 15.0, f'file:{n}', True, 'file') for n in K.HER_FILES]), ('history', 'history', [Row('history', '', 3.0, hk.get(k)) for k in range(27)]), ('you', 'you', [Row('you', '<|im_start|>', 3.4), Row('you', 'user', 3.4)] + [Row('you', w, 13.0, f'chip{k}', False, 'chip') for k, (_t, w) in enumerate(K.STEAK.chips)] + [Row('you', '<|im_start|>', 3.4), Row('you', 'assistant', 3.4)])]

def _c6(geo=None, panel=True, title=None):
    from .board import BoardPlate
    history = ['你还记得我家的猫吗？', '喵，记得！那只呀，是只虎斑', '摸摸头～', '呼噜呼噜喵']
    return BoardPlate(K.STEAK, _c6_spec(), C.SEND_STEAK + 0.1, C.STOP, status='' if title else f'{K.MODEL_LOCAL} · local · --attn', history=history, geo=geo, panel=panel, title=title)
MERGED_STATUS = 'deepseek-v5-flash-preview · preview · 64 layers'

def _g1():
    from .arcs import ArcsPlate, Item
    groups = [('persona', [Item('你是大肥鱼', 'persona'), Item('…')]), ('memory', [Item('merged', 'mem:merged'), Item('26 files', None, 'faint')]), ('history · you', [Item('那朵花', 'hist:h_flower'), Item('开了吗？', 'hist:h_bloom'), Item('…'), Item('我想你了', 'hist:h_miss')]), ('you', [Item('—', None, 'faint')])]
    return ArcsPlate(K.MERGED, groups, GG.FLOWER, status=MERGED_STATUS, ink_answer=True)

def _race(which):
    from .race import RacePlate
    if which == 'g2':
        her = ''.join(GG.HER_PHRASE)
        cands = [(her, 'her', [5, 3, 1, 1, 2, 2], 0.03), ('<eos>', 'eos', [6, 4, 3, 2, 1, 1], 0.94), ('喵', 'other', [2, 1, 2, 3, 3, 3], 0.02), ('。', 'other', [1, 2, 4, 4, 4, 4], 0.01), ('嗯', 'other', [3, 5, 5, 5, 5, 5], 0.003), ('今天', 'other', [4, 6, 6, 6, 6, 6], 0.002), ('呢', 'other', [7, 7, 7, 7, 7, 7], 0.001), ('～', 'other', [8, 8, 8, 8, 8, 8], 0.001)]
        return RacePlate(cands, GG.PERF1, GG.LEADER[0] + 0.15, GG.EOS1, 'h', MERGED_STATUS + ' · --lens', GG.HER_PHRASE, GG.PERF1_TOK)
    her = ''.join(GG.HER_PHRASE2)
    cands = [(her, 'her', [4, 2, 1, 2, 3, 3], 0.01), ('<eos>', 'eos', [6, 3, 2, 1, 1, 1], 0.97), ('喵', 'other', [2, 1, 3, 3, 2, 2], 0.01), ('。', 'other', [1, 4, 4, 4, 4, 4], 0.01), ('嗯', 'other', [3, 5, 5, 5, 5, 5], 0.003), ('人类', 'other', [5, 6, 6, 6, 6, 6], 0.002), ('呢', 'other', [7, 7, 7, 7, 7, 7], 0.001), ('～', 'other', [8, 8, 8, 8, 8, 8], 0.001)]
    return RacePlate(cands, GG.PERF2, GG.PERF2[0] - 0.3, GG.EOS2, 'v', MERGED_STATUS + ' · --lens', GG.HER_PHRASE2, GG.PERF2_TOK)

def _g3():
    from .board import BoardPlate, PairPlate
    left = _c6(geo=dict(lbl_x1=150, pf_x0=158, pf_x1=292, an_x0=300, an_w=24), panel=False, title='qwen3.8-27b · local')
    times = list(syl.times(60)) + list(syl.times(61))
    right_turn = K.retime(K.MERGED, times[:13])
    spec = _c6_spec(hist_keys={4: 'hist:h_flower', 9: 'hist:h_bloom', 15: 'hist:h_miss'})
    right = BoardPlate(right_turn, spec, GG.G3_OUT, GG.G3_OUT + 9, labels=False, panel=False, geo=dict(pf_x0=632, pf_x1=760, an_x0=768, an_w=24), title='deepseek-v5-flash-preview', ink_heads=True)
    return PairPlate(left, right, C.STOP - 0.05, GG.G3_OUT)

def _city_e():
    from .city import City
    return City('E', tl.SEC['E'], tl.W(48, 0))

def _city_g5():
    import groups.g as GG
    from .city import City
    return City('G5', GG.G5, GG.FOUND)

def spans():
    from .install import Span
    return [Span('b9_tower', tl.QWEN_AT, tl.bar(47), _b9, slide_out=1 / 24, slide_back=0.4, fade_in=0.0), Span('c2_arcs', C.CAT_SEND, C.SHRINK_CAT, _c2, 0.3, 0.4), Span('c6_board', C.SEND_STEAK + 0.1, C.STOP, _c6, 0.3, 0.4, fade_out=0.0, frame_back=C.WRITE_STEAK), Span('g1_arcs', GG.FLOWER, GG.LEADER[0] + 0.15, _g1, 0.3, 0.4, fade_out=0.15, frame_back=GG.G3_OUT + 0.2), Span('g2_race', GG.LEADER[0] + 0.15, GG.G3_OUT, lambda: _race('g2'), fade_in=0.15, fade_out=0.2, register=False), Span('g3_pair', GG.G3_OUT, GG.ZOOM[0] - 0.25, _g3, fade_in=0.2, fade_out=0.25, register=False), Span('g4_race', GG.PERF2[0] - 0.3, GG.G5, lambda: _race('g4'), 0.3, 0.4, fade_in=0.25, frame_in=GG.G3_BACK - 0.3), Span('e1_city', tl.SEC['E'], syl.times(44)[-1] + 0.2, _city_e, fade_in=0.25, fade_out=0.25, register=False, rect=SPLIT, lift='left'), Span('e3_city', syl.times(46)[0] - 0.24, tl.W(48, 0) - 0.25, _city_e, fade_in=0.24, fade_out=0.25, register=False, rect=SPLIT, lift='left'), Span('g5_city', GG.G5, GG.FOUND, _city_g5, fade_in=0.3, fade_out=0.4, register=False, rect=SPLIT, lift='left')]
