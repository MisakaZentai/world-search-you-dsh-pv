"""Sung syllables as times (PLAN_FULL.md R3): one Chinese character lands on one sung syllable.

A word's first syllable is its aligned start (timing/words.json). Its other syllables are the vocal
note onsets measured inside the word (timing/audio.json, onsets.vocal); when fewer are measured than
the word has syllables, the rest are spread evenly over the word. How many syllables an English word
is sung as comes from COUNT (checked against the storyboard's counts), else a vowel-group guess.

  syl(lid, wi)          -> [t, ...]          the syllables of word wi of line lid
  line(lid)             -> [(t, wi, j), ...] every syllable of the line, in order
  place(text, lid, ...) -> [(ch, t), ...]    a Chinese line laid on the syllables, punctuation riding
                                             on the character before it
  ime(t0, words)        -> [(t, word), ...]  pinyin IME commits on the 8th notes after t0 (R7)

Lines are referred to by id and words by index; nothing here prints lyric text.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import json
import re
import tl
L = tl.L
_A = json.loads((tl.HERE / 'timing/audio.json').read_text(encoding='utf-8'))
VOCAL = [(float(t), float(s)) for t, s in _A['onsets']['vocal']]
PUNCT = '，。！？、～…：；,.!?~ '
COUNT = {'lovelier': 3, 'bubble': 2, 'memory': 3, 'insert': 2, 'sweetest': 2, 'table': 2, 'elbows': 2, 'stubby': 2, 'wobbly': 2, 'only': 2, 'perfect': 2, 'eggplant': 2, 'purple': 2, 'scratchy': 2, 'body': 2, 'searching': 2, 'little': 2, 'kitten': 2, 'blue-point': 2, 'meowing': 2, 'hissing': 2, 'never': 2, 'filet': 2, 'mignon': 2, 'covered': 2, 'mushroom': 2, 'browned': 1, 'outside': 2, 'medium': 3, 'inside': 2, 'flower': 2, 'delicate': 3, 'ever': 2, 'even': 2, 'occasionally': 5, 'human': 2, 'coming': 2, 'stinky': 2, 'unruly': 3, 'uhm': 1, 'uhmmm': 1, 'again': 2, 'do-o-o-o-ope': 1, 'lo-o-o-ove': 3, 'everywhere': 3, 'everything': 3, 'somehow': 2, 'transforming': 3, 'ah-ah': 2, 'bucket': 2, 'empty': 2, 'filled': 1, 'pieces': 2, 'evolved': 2, 'puppy': 2, 'going': 2, 'tomato': 3, 'juice': 1, 'warmth': 1, 'breath': 1, 'hands': 1, "you're": 1, "you'll": 1, "i'm": 1, "i'd": 1, "that's": 1, "what's": 1, "can't": 1, "'til": 1, 'called': 1, 'cell': 1, 'evolved,': 2, 'gone': 1, 'since': 1, 'left': 1, 'old': 1, 'self': 1, 'into': 2, 'piece': 1, 'shit': 1, 'word': 1, 'stay': 1, 'could': 1, 'fruit': 1, 'dog': 1, 'ruff': 1, 'full': 1, 'makes': 1, 'marks': 1, 'nail': 1, 'friend': 1, 'leg': 1, 'odd': 1}

def _key(text: str) -> str:
    return re.sub("^[^\\w']+|[^\\w'-]+$", '', text.lower()).strip('"')

def guess(word: str) -> int:
    w = re.sub('[^a-z]', '', word.lower())
    if not w:
        return 1
    n = len(re.findall('[aeiouy]+', w))
    if w.endswith('e') and (not w.endswith(('le', 'ee'))) and (n > 1):
        n -= 1
    return max(1, n)

def count(lid: int, wi: int) -> int:
    k = _key(L.by_id[lid].words[wi].text)
    return COUNT.get(k, guess(k))

def _span(lid: int, wi: int) -> tuple[float, float]:
    words = L.by_id[lid].words
    a, b = (words[wi].start, words[wi].end)
    if wi + 1 < len(words):
        b = min(b, words[wi + 1].start)
    return (a, max(b, a + 0.1))

def syl(lid: int, wi: int, n: int | None=None) -> list[float]:
    """Times of the n sung syllables of word wi (n defaults to count())."""
    n = count(lid, wi) if n is None else n
    a, b = _span(lid, wi)
    if n <= 1:
        return [a]
    inside = [(t, s) for t, s in VOCAL if a + 0.1 < t < b - 0.02]
    if len(inside) > n - 1:
        inside = sorted(sorted(inside, key=lambda v: -v[1])[:n - 1])
    out = [a] + [t for t, _s in inside]
    while len(out) < n:
        last = out[-1]
        k = n - len(out)
        out.append(last + (b - last) / (k + 1))
        out.sort()
    return out[:n]

def line(lid: int, counts: dict | None=None) -> list[tuple[float, int, int]]:
    """Every sung syllable of line lid: (time, word index, syllable index). counts overrides {wi: n}."""
    out = []
    for wi in range(len(L.by_id[lid].words)):
        n = (counts or {}).get(wi)
        for j, t in enumerate(syl(lid, wi, n)):
            out.append((t, wi, j))
    return out

def times(lid: int, counts: dict | None=None, wi0: int=0) -> list[float]:
    return [t for t, wi, _j in line(lid, counts) if wi >= wi0]

def place(text: str, lid: int, wi0: int=0, counts: dict | None=None, at: list | None=None):
    """[(ch, t)]: the non-punctuation characters of text on consecutive syllables of line lid from word
    wi0 (or on the explicit times `at`); punctuation shares the time of the character before it."""
    ts = list(at) if at is not None else times(lid, counts, wi0)
    out, j = ([], 0)
    for ch in text:
        if ch in PUNCT and out:
            out.append((ch, out[-1][1]))
        else:
            out.append((ch, ts[min(j, len(ts) - 1)]))
            j += 1
    if j > len(ts):
        raise ValueError(f'{j} characters on {len(ts)} syllables of line {lid}')
    return out

def shown(seq, t: float) -> str:
    """The text of a placed sequence visible at t."""
    return ''.join((ch for ch, at in seq if at <= t))

def ime(t0: float, words: list[str], div: int=2, step: int=1) -> list[tuple[float, str]]:
    """Pinyin IME commits: word k on the (k*step)-th 1/div-beat step after t0."""
    return [(tl.grid(t0, k * step, div), w) for k, w in enumerate(words)]

def typed(commits, t: float) -> str:
    return ''.join((w for at, w in commits if at <= t))
if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    for Lx in L.lines:
        cs = [count(Lx.id, i) for i in range(len(Lx.words))]
        print(f'{Lx.id:3d} {Lx.start:7.2f} n={sum(cs):2d} {cs}')
