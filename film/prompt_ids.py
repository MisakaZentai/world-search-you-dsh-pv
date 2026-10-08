"""Token ids for your messages in the input pane (groups/c_pane.py, groups/b_pane.py), from the local Qwen model's
own vocabulary (subs_tok.py, the subtitle band's tokenizer; FACTS X32). Each IME commit is encoded on its own, so a
commit that the model would split differently inside the whole message may differ (known, small).

  python prompt_ids.py      -> prompt_ids.json  {commit text: [ids]}; rendering reads only the json
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
OUT = HERE / 'prompt_ids.json'

def load() -> dict:
    try:
        return json.loads(OUT.read_text(encoding='utf-8'))['ids']
    except (OSError, KeyError, ValueError):
        return {}

def text(ids) -> str:
    return '·'.join((str(i) for i in ids))
