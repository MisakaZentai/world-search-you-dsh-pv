"""dsh pane, r5 batch 2, interlude 3 (260.88-273.39; REVISE_R4_20261004.md §3.15, D34): the merged one's session as
pages/g_mirror.py shows it, then the sessions wearing her persona archived one a stab (inside/i5_times.py CLOSES,
269.06 ... 272.96), the way dsh archives a session: hover its row, its actions button (…), the menu, 归档会话.

Native behaviour (read-only, <local-production-path>
  - a session row's actions are a Menu on the row's `…` button (IconEllipsisOutline16): 重命名 (IconEditOutline16),
    分叉会话 (IconBranchOutline16), 归档会话 (IconArchiveOutline20 at 16) (SessionNodeItem, about lines 935-1030;
    zh strings "rename", "menu.fork", "menu.archiveSession" about lines 2600-2607);
  - an archived session leaves the session list (sessionVisible: `!archived.has(session.id)`, about line 338);
  - archiving the session that is open clears the selection (about lines 153-156): the main column is left empty.
There is no close button (r4's × on the avatar was not dsh's). The session rail of avatars, her archived session at
its foot with the 已归档 badge, and the menu's look (.pv-menu) are this project's (ui/host.html), as before.

From FOUND (273.39) the pane is group H's (D33: pages/h_a.py); your pointer goes down to her session and presses on
the last frame of this page (LAST_T), so her session opens on the very next frame.

r5 round 2 (D35):
  - no empty main column: the last session archived is the open one (the merged's). The archive is clicked on its
    stab (272.96) and the row collapses as before, but the open session's page stays until your click on her
    session lands (LAST_T): the frame after the archive's last one is hers (r5a showed dsh's empty main column for
    four frames, 273.21-273.33, and it read as a flash). Nothing new is drawn: the rows, the menu and the pointer are
    the ones above; only when the selection changes is moved to your click.
  - the second turn's 用时 is 12.2 秒 (groups/g_r5.py's send time, 248.42, to <eos> on line 63, 260.665), as G's page
    has it (r5 round 2, the 2-C batch).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from icons import svg
import cast
from groups import g_mirror as G
from inside import i5_times as I5
from pages import g as PG
from pages import g_mirror as GM
from pages.common import AV, COL, blink, color, dsh, ease
M = 'merged'
LAST_T = (int(round(I5.FOUND * 24)) - 1) / 24
TAIL2_OLD, TAIL2 = ('10.8秒', '12.2秒')
CLOSES = I5.CLOSES
SESSIONS = I5.SESSIONS
GONE = 0.22
ITEM_Y0, PITCH = (54, 38)
DOTS_XY = (43, 69)
MENU_XY = (54, 50)
ARCHIVE_XY = (100, 131)
HER_XY = (26, 518)
REST_XY = (102, 40)
MENU = [('IconEditOutline16', 16, '重命名'), ('IconBranchOutline16', 16, '分叉会话'), ('IconArchiveOutline20', 16, '归档会话')]

def closed_u(t: float, k: int) -> float:
    return ease.ease_io(ease.prog(t, CLOSES[k], CLOSES[k] + GONE))

def first_open(t: float) -> int | None:
    """Index of the first session not archived yet (it is the top item once the one before has collapsed)."""
    for k in range(len(SESSIONS)):
        if t < CLOSES[k]:
            return k
    return None

def menu_state(t: float):
    """(open 0..1, hovered row or None) for the archive of the session closed next."""
    for at in CLOSES:
        if at - 0.22 <= t < at + 0.06:
            op = ease.prog(t, at - 0.22, at - 0.18) * (1 - ease.prog(t, at, at + 0.06))
            return (op, 2 if t >= at - 0.08 else None)
    return (0.0, None)

def rail(t: float) -> str:
    """pages/g.py's rail_g with dsh's row actions: on hover the item shows its … button (no × of our own)."""
    items = []
    k_next = first_open(t)
    for k, who in enumerate(SESSIONS):
        c = closed_u(t, k)
        if c >= 1:
            continue
        av = PG.av_at(t) if who == M else AV
        active = who == M
        hover = 0.0
        if k == k_next and CLOSES[k] - 0.34 <= t:
            hover = 1.0
        if k < len(CLOSES) and CLOSES[k] <= t:
            hover = 1 - c
        dots = f'<span style="position:absolute;right:-9px;top:7px;width:16px;height:16px;border-radius:5px;display:flex;align-items:center;justify-content:center;background:var(--dsw-alias-bg-base);border:.5px solid var(--dsw-alias-border-l2);color:var(--dsw-alias-label-secondary);opacity:{hover:.2f}">{svg('IconEllipsisOutline16', 12)}</span>'
        bar = '<span style="position:absolute;left:-12px;top:7px;width:3px;height:16px;border-radius:2px;background:var(--dsw-alias-label-primary)"></span>' if active else ''
        items.append(f'<div style="position:relative;width:30px;height:{30 * (1 - c):.1f}px;margin-bottom:{8 * (1 - c):.1f}px;opacity:{1 - c:.2f}">{bar}<img src="{av}" style="width:30px;height:30px;border-radius:8px;display:block;box-shadow:0 0 0 2px {color(who)}">{dots}</div>')
    her = '<div style="position:relative;width:30px;height:30px"><img src="{}" style="width:30px;height:30px;border-radius:8px;display:block;filter:grayscale(1) brightness(1.08) contrast(.82);opacity:.75"><span class="pv-badge">已归档</span></div>'.format(AV)
    return f'<div class="pv-rail" style="gap:0;padding-top:12px"><div class="pv-new" style="margin-bottom:8px">{svg('IconPlusOutline16', 16)}</div>{''.join(items)}<div style="flex:1"></div>{her}<div style="height:14px"></div></div>'

def menu(t: float) -> str:
    op, hov = menu_state(t)
    if op <= 0.01:
        return ''
    rows = []
    for i, (icon, size, label) in enumerate(MENU):
        cls = 'pv-mi' + (' hov' if i == hov else '')
        rows.append(f'<div class="{cls}" style="gap:8px"><span style="display:inline-flex;width:16px;color:var(--dsw-alias-label-secondary)">{svg(icon, size)}</span>{dsh.esc(label)}</div>')
    x, y = MENU_XY
    return f'<div class="pv-menu" style="left:{x}px;top:{y}px;right:auto;bottom:auto;width:128px;opacity:{op:.2f}">{''.join(rows)}</div>'

def pointer(t: float) -> str:
    """Rest on its avatar; from the frame's return, for each session: to its …, press, down to 归档会话, press
    on the stab; at last down to her archived session, press on FOUND."""
    if t < I5.G5:
        return ''
    pts = [(I5.G5, REST_XY), (I5.TURN_BAR + 0.5, REST_XY)]
    presses = []
    for at in CLOSES:
        pts += [(at - 0.3, DOTS_XY), (at - 0.22, DOTS_XY), (at - 0.04, ARCHIVE_XY), (at + 0.05, ARCHIVE_XY)]
        presses += [at - 0.22, at]
    pts += [(LAST_T - 0.06, HER_XY)]
    presses.append(LAST_T)
    x, y = pts[0][1]
    for (ta, pa), (tb, pb) in zip(pts, pts[1:]):
        if t >= tb:
            x, y = pb
        elif t >= ta:
            u = ease.ease_io(ease.prog(t, ta, tb))
            x, y = (ease.lerp(pa[0], pb[0], u), ease.lerp(pa[1], pb[1], u))
            break
    press = 0.0
    for at in presses:
        if at - 0.05 <= t < at + 0.12:
            press = max(press, 1 - abs(t - at) / 0.12)
    return dsh.pointer(x, y, press)

def rows(t: float) -> str:
    """The merged one's session (pages/g_mirror.py), the second turn's 用时 as r5 has it."""
    out = GM.rows(t)
    old, new = (dsh.tail(TAIL2_OLD, '23:59'), dsh.tail(TAIL2, '23:59'))
    return out.replace(old, new)

def body(t: float) -> str:
    if t >= I5.FOUND:
        return GM.her_session(t)
    comp = dsh.composer(cast.name(M), COL[M], typed=GM.typed(t), caret_on=blink(t))
    if GM.running(t):
        comp = comp.replace(GM.SEND_SVG, GM.STOP_SVG, 1)
    turns = (t >= G.FLOWER) + (t >= G.SEE_SEND)
    main = dsh.header('大肥鱼', cast.name(M), COL[M], AV, '在线') + f'<div id="timeline">{rows(t)}</div>' + comp + dsh.stats(turns, 0, 'preview API')
    return f'<div class="pv-root">{rail(t)}<div class="pv-main">{main}</div>{menu(t)}{pointer(t)}</div>'
