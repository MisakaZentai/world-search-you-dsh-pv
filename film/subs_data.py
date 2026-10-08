"""Chinese chunk alignment, supplied locally; numeric relations are in data/zh_alignment.json."""
from pv_text import chinese_input, load_alignment

ALIGN = load_alignment()
DROP = '，、'
ZH_EDIT = {}

def zh_line(lid):
    return chinese_input().get('display', {}).get(str(lid))
