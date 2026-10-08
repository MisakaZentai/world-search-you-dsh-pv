"""Who wears the persona (PLAN_FULL.md §2, FACTS X14, X17, X29, X35). Names as they appear on screen.

D20/D21 (2026-10-02): the stand-ins are the newest domestic models, `CAST_20261002.md`; Doubao is gone (no API).
Only model names as text: no logos, no imitation of anyone's interface (the interface is always dsh).
The memes in the candidate panels are invented parody (X17). Release dates, sizes and thinking modes are
registered, with their sources, in FACTS X29.

key: name (dsh header and menu), term (terminal chip), color (PROJECT.yaml key; only the dsh model dot
uses it, the terminal draws every stand-in in ink, R2), kind (offline | cloud | local | merged),
memes (the runner-up and the third candidate in its first candidate panel, R10), meme (= memes[0]),
theme (dsh theme class), thinking (see THINKING below), owner (the lowercase name in `ls -la`'s owner
column, X24), short (the bucket label in group F).

Key "doubao": tl.py (frozen while the groups run) still says "doubao" for model 丙; 丙 is now MiMo-V2.6-Pro,
canonical key "mimo". CAST["doubao"] is the same dict as CAST["mimo"], so either key works everywhere;
canon() maps a key to the canonical one. Ask the main agent to rename it in tl.py someday.

D36 (2026-10-04, FACTS X35): every model on screen has open weights. ERNIE 5.1 -> ERNIE-4.5-21B-A3B-Thinking (key
"ernie"), Spark-X2.5 -> Step-3.7-Flash (new canonical key "step"; "spark" is an alias, as "doubao" is for "mimo"),
LongCat-2.5-Preview -> LongCat-2.0 (key "longcat"). Step's memes are invented parody (X17); the second one is the
sense of its model card's system prompt ("you can see, think, and act").
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
CAST = {'her': dict(name='DeepSeek-V4.1-Flash', term='DeepSeek-V4.1-Flash', color='her', kind='offline', owner='me', short='me', thinking='none'), 'kimi': dict(name='Kimi K3', term='Kimi K3', color='kimi', kind='cloud', memes=('（已读完你们全部 412 行聊天记录）',), owner='kimi-k3', short='Kimi', thinking='always'), 'qwen': dict(name='Qwen3.8-27B（本地）', term='Qwen3.8-27B · local', color='qwen', kind='local', memes=('我是通义千问，由阿里云',), theme='kuro', owner='qwen3.8-27b', short='Qwen3.8', thinking='local'), 'mimo': dict(name='MiMo-V2.6-Pro', term='MiMo-V2.6-Pro', color='mimo', kind='cloud', memes=('你好，我是 MiMo', '我能跟你唠东北嗑'), owner='mimo-v2.6-pro', short='MiMo', thinking='switch'), 'glm': dict(name='GLM-5.3', term='GLM-5.3', color='glm', kind='cloud', memes=('我是智谱清言',), owner='glm-5.3', short='GLM', thinking='always'), 'minimax': dict(name='MiniMax-M3', term='MiniMax-M3', color='minimax', kind='cloud', memes=('Your model version is MiniMax-M3',), owner='minimax-m3', short='MiniMax', thinking='adaptive'), 'hy4': dict(name='Hy4 preview', term='Hy4 preview', color='hy4', kind='cloud', memes=('让我再核对一遍',), owner='hy4-preview', short='Hy4', thinking='effort'), 'ernie': dict(name='ERNIE-4.5-21B-A3B-Thinking', term='ERNIE-4.5-21B-A3B-Thinking', color='ernie', kind='cloud', memes=('我是文心一言', '我还没学会如何回答这个问题'), owner='ernie-4.5-21b-a3b-thinking', short='ERNIE', thinking='default_on'), 'step': dict(name='Step-3.7-Flash', term='Step-3.7-Flash', color='step', kind='cloud', memes=('我是阶跃星辰的 AI 助手', '我能看、能想、还能动手'), owner='step-3.7-flash', short='Step', thinking='levels'), 'longcat': dict(name='LongCat-2.0', term='LongCat-2.0', color='longcat', kind='cloud', memes=('领 50 元买菜券', '美团，让思念比月光先到'), owner='longcat-2.0', short='LongCat', thinking='switch'), 'merged': dict(name='deepseek-v5-flash-preview', term='deepseek-v5-flash-preview', color='merged', kind='merged', owner='deepseek-v5-flash-preview', short='merged', thinking='none')}
for _k, _v in CAST.items():
    _v['meme'] = _v['memes'][0] if _v.get('memes') else None
CAST['doubao'] = CAST['mimo']
CAST['spark'] = CAST['step']
ALIAS = {'doubao': 'mimo', 'spark': 'step'}
import os as _os
if _os.environ.get('DSH_END') == 'story':
    CAST['merged'].update(name='大肥鱼', term='大肥鱼')
ROTATION = ['glm', 'minimax', 'hy4', 'ernie', 'step', 'longcat']
STANDINS = ['kimi', 'qwen', 'mimo'] + ROTATION
LOCAL = {'alias': 'blackcat-qwen3.8-27b-q4', 'quant': 'Q4_K_M', 'where': 'llama.cpp · CPU（3090 在出图）', 'tok_s': 1.4}
THINK_ROWS = {'always': ['<think> · hidden by provider'], 'default_on': ['构思回答'], 'switch': ['构思回答'], 'effort': ['构思回答', '再核对一遍'], 'levels': ['构思回答']}
PANEL_NOTE = {'adaptive': 'thinking: adaptive → skipped'}

def canon(key: str) -> str:
    return ALIAS.get(key, key)

def name(key: str) -> str:
    return CAST[key]['name']

def term(key: str) -> str:
    return CAST[key]['term']

def kind(key: str) -> str:
    return CAST[key]['kind']

def owner(key: str) -> str:
    return CAST[key]['owner']

def short(key: str) -> str:
    return CAST[key]['short']

def thinking(key: str) -> str:
    return CAST[key]['thinking']

def think_rows(key: str) -> list[str]:
    """Summaries of the thinking rows dsh shows for this model (none: no row)."""
    return list(THINK_ROWS.get(CAST[key]['thinking'], []))

def panel_note(key: str) -> str | None:
    """Text for the top right of its candidate panel instead of 'sampled' (None: the usual one)."""
    return PANEL_NOTE.get(CAST[key]['thinking'])
