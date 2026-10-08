"""The nine objects of the chorus grid (REVISE_R4_20261004.md §3.8, DECISIONS D34 / D4): pixel pictures at the
first Super Mario Bros.' precision, 16 x 16, each in three or four colours plus the ink outline, in the colours the
things really have (purple eggplant, wooden table, blue-point cat, steak under mushroom sauce, flower, hand ...).
D4 makes these cells the one exception to "paper, three inks and her blue". Every object keeps one small patch of
her blue ("you can see her in almost everything"): the shim under the table's short leg, the scratches on the
eggplant, the cat's eyes, the flag in the steak, one petal, a ring, the knob of the jigsaw piece, the glint in the
lenses, the plaster on the heart.

  SPRITES[name] = (rows, palette)   rows: 16 strings of 16 characters; palette: {char: colour | "her"}
  draw(d, name, x, y, px, her_rgb, ink)   paint one sprite with its top-left at (x, y), px screen pixels a cell

'.' is transparent, 'K' the outline (ink), 'B' her blue. Names are the file names of tl.WRITES' E2 entries.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
_WOOD, _WOOD_D = ((201, 141, 79), (139, 90, 46))
_PURPLE, _PURPLE_L, _LEAF = ((106, 61, 154), (154, 111, 200), (90, 143, 60))
_CREAM, _POINT = ((241, 231, 211), (110, 90, 78))
_MEAT, _FAT, _SAUCE = ((206, 96, 98), (241, 226, 200), (122, 78, 42))
_PETAL, _CENTRE, _STEM = ((228, 114, 143), (239, 196, 60), (79, 138, 60))
_SKIN, _SKIN_D = ((242, 201, 161), (211, 154, 112))
_PIECE, _PIECE_D = ((232, 182, 76), (190, 138, 47))
_LENS, _GLINT = ((42, 45, 54), (236, 232, 222))
_RED, _RED_L = ((216, 67, 79), (240, 138, 148))
SPRITES = {'table_2': (['................', '................', '................', '..KKKKKKKKKKKK..', '.KWWWWWWWWWWWWK.', 'KWWWWWWWWWWWWWWK', 'KKKKKKKKKKKKKKKK', 'KDDDDDDDDDDDDDDK', 'KKKKKKKKKKKKKKKK', '.KDK........KDK.', '.KDK........KDK.', '.KDK........KDK.', '.KDK........KDK.', '.KDK........KKK.', '.KDK.......BBBBB', '.KKK.......BBBBB'], {'K': 'ink', 'W': _WOOD, 'D': _WOOD_D, 'B': 'her'}), 'eggplant_3': (['..........KK....', '.........KGGK...', '......KKKGGKKK..', '.....KGGGGGGGGK.', '.....KPKGKKGKK..', '....KPPPKKPPK...', '...KPPLPPPPPPK..', '..KPPLLPPPBPPK..', '..KPLLPPPBPPPK..', '.KPPLPPPPPPBPK..', '.KPLPPPPPPBPPK..', '.KPPPPPPPBPPK...', '.KPPPPPPPPPPK...', '..KPPPPPPPPK....', '...KKPPPPKK.....', '.....KKKK.......'], {'K': 'ink', 'P': _PURPLE, 'L': _PURPLE_L, 'G': _LEAF, 'B': 'her'}), 'cat_2': (['..KK........KK..', '.KDDK......KDDK.', '.KDDDKKKKKKDDDK.', '.KCDDDDDDDDDDCK.', 'KCCDDDDDDDDDDCCK', 'KCCDBBDDDDBBDCCK', 'KCCDDKDDDDKDDCCK', '.KCCDDDKKDDDCCK.', '..KCCCDDDDCCCK..', '..KCCCCCCCCCCK..', '.KCCCCCCCCCCCCK.', '.KCCCCCCCCCCCCKK', '.KCCCCCCCCCCCCKD', '.KCCCCCCCCCCCCKD', '.KDDKCCCCCCKDDKD', '..KKKKKKKKKKKKKK'], {'K': 'ink', 'C': _CREAM, 'D': _POINT, 'B': 'her'}), 'steak_2': (['................', '..........K.....', '..........KBBB..', '....KKKKKKKBB...', '..KKFFFFFFKKK...', '.KFFMMMMMMMMFK..', 'KFFMMMAAAMMMMFK.', 'KFMMMAAAAAMMMMFK', 'KFMMMMAAMMMKKMFK', 'KFMMMMMAMMKFFKFK', 'KFMMMMMMMMKFFKFK', '.KFMMMMMMMMKKMFK', '.KFFMMMMMMMMMFK.', '..KKFFFFFFFFFK..', '....KKKKKKKKK...', '................'], {'K': 'ink', 'M': _MEAT, 'F': _FAT, 'A': _SAUCE, 'B': 'her'}), 'flower_2': (['......KKKK......', '.....KRRRRK.....', '..KKKKRRRRKKKK..', '.KRRRKKRRKKBBBK.', '.KRRRRKYYKBBBBK.', '..KRRKYYYYKBBK..', '...KKYYYYYYKK...', '..KRRKYYYYKRRK..', '.KRRRRKKKKRRRRK.', '.KRRRK.KGK.KRRK.', '..KKK..KGK..KK..', '.......KGK......', '..KKK..KGK.KKK..', '.KGGGK.KGKKGGGK.', '..KKGGKKGKGGKK..', '....KKKKGKKK....'], {'K': 'ink', 'R': _PETAL, 'Y': _CENTRE, 'G': _STEM, 'B': 'her'}), 'human_9': (['......KK........', '...KK.KSK.KK....', '..KSK.KSK.KSK...', '..KSK.KSK.KSK.KK', '..KSK.KSK.KSKKSK', '..KSK.KSK.KSKKSK', 'KKKSKKKSKKBBKSK.', 'KSKSSKSSSKSSKSK.', 'KSKSSSSSSSSSSSK.', 'KSSSSSSSSSSSSSK.', '.KSSSSSDSSSSSSK.', '.KSSSSSDDSSSSK..', '..KSSSSSSSSSSK..', '...KSSSSSSSSK...', '...KSSSSSSSSK...', '...KKKKKKKKKK...'], {'K': 'ink', 'S': _SKIN, 'D': _SKIN_D, 'B': 'her'}), 'piece': (['....KKKK........', '...KBBBBK.......', '...KBBBBK.......', '...KKBBKK.......', 'KKKKKBBKKKKK....', 'KYYYYYYYYYDK....', 'KYYYYYYYYYDKKKK.', 'KYYYYYYYYYDKYYDK', 'KYYYYYYYYYYYYYDK', 'KYYYYYYYYYYYYYDK', 'KYYYYYYYYYDKYYDK', 'KYYYKKKKYYDKKKK.', 'KYYK....KYDK....', 'KDDK....KDDK....', 'KKKKK..KKKKK....', '................'], {'K': 'ink', 'Y': _PIECE, 'D': _PIECE_D, 'B': 'her'}), 'dope': (['................', '................', '................', '................', 'KKKKKKKKKKKKKKKK', 'KLLLLLLKKLLLLLLK', 'KLWWLLLKKLWWLLLK', 'KLWLLLLKKLWLLLLK', '.KLLLLBK.KLLLLBK', '.KLLLBBK.KLLLBBK', '..KLLLK...KLLLK.', '...KKK.....KKK..', '................', '................', '................', '................'], {'K': 'ink', 'L': _LENS, 'W': _GLINT, 'B': 'her'}), 'love': (['................', '..KKKK....KKKK..', '.KRRRRK..KRRRRK.', 'KRPPRRRKKRRRRRRK', 'KRPRRRRRRRRRRRRK', 'KRRRRRRRRRRRRRRK', 'KRRRRRRRRRBBRRRK', '.KRRRRRRRBBBBRK.', '..KRRRRRBBBBRK..', '...KRRRRRBBRK...', '....KRRRRRRK....', '.....KRRRRK.....', '......KRRK......', '.......KK.......', '................', '................'], {'K': 'ink', 'R': _RED, 'P': _RED_L, 'B': 'her'})}
for _name, (_rows, _pal) in SPRITES.items():
    assert len(_rows) == 16 and all((len(r) == 16 for r in _rows)), _name
    assert set(''.join(_rows)) <= set(_pal) | {'.'}, (_name, set(''.join(_rows)) - set(_pal))
    assert len(set(_pal.values()) - {'ink', 'her'}) <= 3, _name

def draw(d, name, x, y, px, her_rgb, ink, alpha_rgb=None, her_mask=None):
    """Paint sprite `name` with its top-left at (x, y), px screen pixels per cell. her_rgb colours the 'B'
    cells; alpha_rgb(c) (optional) maps every colour (used to fade an empty cell in). her_mask: if given, only
    the 'B' cells are painted (for the "everything" flash)."""
    rows, pal = SPRITES[name]
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == '.':
                continue
            if her_mask is not None and ch != 'B':
                continue
            c = pal[ch]
            c = her_rgb if c == 'her' else ink if c == 'ink' else c
            if alpha_rgb is not None:
                c = alpha_rgb(c)
            x0, y0 = (int(round(x + i * px)), int(round(y + j * px)))
            x1, y1 = (max(x0, int(round(x + (i + 1) * px)) - 1), max(y0, int(round(y + (j + 1) * px)) - 1))
            d.rectangle((x0, y0, x1, y1), fill=c)
