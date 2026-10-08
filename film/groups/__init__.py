"""One module per group (STORYBOARD_v2 A-H). Each defines register(film) and adds only the shots, LEAD
changes and deep-sea spans of its own time span (tl.span(group)). Shared constants that the dsh pane also
needs (chat text, key times) live at module level so ui/pages/<group>.py can import them."""
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from . import a, b, c, d, e, f, g, h
ALL = [a, b, c, d, e, f, g, h]
