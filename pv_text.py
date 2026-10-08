"""Optional local subtitle text. Copyrighted lyrics are not part of the source distribution."""
import json
from functools import lru_cache
from pv_paths import ROOT

@lru_cache(None)
def chinese_input():
    p = ROOT / 'input/zh_subtitles.json'
    return json.loads(p.read_text('utf8')) if p.exists() else {'base': {}, 'display': {}}

def load_chinese():
    return {int(k): v for k, v in chinese_input()['base'].items()}

def load_alignment():
    source = chinese_input()
    spec = json.loads((ROOT / 'data/zh_alignment.json').read_text('utf8'))
    result = {}
    for key, chunks in spec.items():
        if key not in source.get('display', {}):
            continue
        text = ''.join(c for c in source['display'][key] if c not in '，、')
        if len(text) != sum(n for n, _ in chunks):
            raise ValueError(f'Chinese line {key}: chunk lengths do not match; see input/README.md')
        pos, rows = 0, []
        for length, words in chunks:
            rows.append((text[pos:pos+length], words))
            pos += length
        result[int(key)] = rows
    return result

@lru_cache(None)
def lyric_lines():
    data = json.loads((ROOT / 'film/timing/words.json').read_text('utf8'))
    return {line['id']: line['text'] for line in data['lines']}

def lyric_fragment(line_id, start, end):
    return lyric_lines()[line_id][start:end]
