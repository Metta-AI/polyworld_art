"""Generate editable lobby layouts with three explicit typography tokens."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent


def icon(name, extra=''):
    """Reference a shared Polyworld icon without embedding screenshot pixels."""
    return f'<img class="icon {extra}" src="../../../../icons/{name}.png" alt="">'


def button(label, name='', extra='', disabled=False):
    """Build a consistently sized text and icon control."""
    disabled_attr = ' disabled' if disabled else ''
    return f'<button class="control {extra}"{disabled_attr}>{icon(name) if name else ""}{label}</button>'


def page(name, title, subtitle, contents):
    """Wrap a screen in the shared font and component style sheet."""
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=1672, initial-scale=1">
<title>{title}</title><link rel="stylesheet" href="ui.css"></head>
<body><main class="screen {name}">
<header class="header"><img class="crest" src="../../../../icons/battle.png" alt="">
<div class="heading"><div class="brand">GODS OF THE ARENA</div><h1>{title}</h1>
<p class="subtitle">{subtitle}</p></div></header>{contents}</main>
<script src="audit.js"></script></body></html>'''


def slot(number, name, bot=False, human=False):
    """Create one un-drafted human, bot or empty player assignment."""
    classes = 'slot' + (' blue-slot' if number > 5 else '') + (' selected' if number == 3 else '')
    mark = 'character' if human else ('settings' if bot else 'cross')
    badge = '<span class="badge human">HUMAN</span>' if human else ('<span class="badge">BOT</span>' if bot else '')
    return f'<div class="{classes}"><span class="seat">{number}</span><span class="avatar">{icon(mark)}</span><span class="name">{name}</span>{badge}{icon("chevron_down", "chevron")}</div>'


def stepper(value):
    """Create a numeric stepper with icons independent of text sizing."""
    return f'<div class="stepper"><button aria-label="Decrease">{icon("minus")}</button><span>{value}</span><button aria-label="Increase">{icon("cross")}</button></div>'


def dropdown(value):
    """Create a field-like dropdown control."""
    return f'<button class="control dropdown"><span>{value}</span>{icon("chevron_down", "small")}</button>'


def setting(label, value):
    """Align a setting label and its control in the standard grid."""
    return f'<div class="setting"><span>{label}</span>{value}</div>'


def toggle(on):
    """Draw a toggle with vector geometry rather than font glyphs."""
    return f'<div class="toggle {"on" if on else ""}" role="switch" aria-checked="{str(on).lower()}"><span></span></div>'


MAP = '''<div class="map" aria-label="Illustrative map preview"><svg viewBox="0 0 456 148" role="img" aria-label="Arena terrain preview">
<rect width="456" height="148" fill="#294236"/>
<path d="M0 108 55 69 90 91 139 34 181 49 241 14 274 36 333 14 389 55 456 36V148H0Z" fill="#3c583a"/>
<path d="M-20 125 62 99 113 64 173 91 229 48 301 80 365 39 480 60" stroke="#5f502d" stroke-width="29" fill="none"/>
<path d="M-20 125 62 99 113 64 173 91 229 48 301 80 365 39 480 60" stroke="#aa9560" stroke-width="19" fill="none"/>
<path d="M180 148 200 118 181 96 199 74 227 81 237 111 255 126 248 148Z" fill="#0d6b88"/>
<path d="M183 143 203 119 188 97 201 84" stroke="#3da5bb" stroke-width="3" fill="none"/>
<g fill="#173627" stroke="#496744" stroke-width="3"><circle cx="25" cy="29" r="20"/><circle cx="69" cy="24" r="15"/><circle cx="130" cy="126" r="16"/><circle cx="302" cy="119" r="23"/><circle cx="387" cy="111" r="17"/><circle cx="421" cy="20" r="17"/><circle cx="151" cy="20" r="14"/></g>
<g transform="translate(49 69)"><rect x="-13" y="-12" width="26" height="33" fill="#7797a2"/><path d="m-20-12 20-22 20 22Z" fill="#20a9ee"/><rect x="-4" y="5" width="8" height="16" fill="#182c37"/></g>
<g transform="translate(405 71)"><rect x="-13" y="-12" width="26" height="33" fill="#8d7b68"/><path d="m-20-12 20-22 20 22Z" fill="#eb4a37"/><rect x="-4" y="5" width="8" height="16" fill="#33251b"/></g>
</svg></div>'''

roster = '<section class="panel roster"><div class="teams-header">'
roster += f'<div class="team-heading red">{icon("tower", "large")}<h2>RED TEAM</h2></div><p class="hint muted">Click a slot to choose a player.</p>'
roster += f'<div class="team-heading blue">{icon("tower", "large")}<h2>BLUE TEAM</h2></div></div><div class="slots">'
assignments = [(1, 'You', False, True), (6, 'Bot 1', True, False), (2, 'Bot 1', True, False), (7, 'Bot 3', True, False), (3, 'Add player', False, False), (8, 'Bot 2', True, False), (4, 'Bot 2', True, False), (9, 'Add player', False, False), (5, 'Add player', False, False), (10, 'Add player', False, False)]
roster += ''.join(slot(*row) for row in assignments) + '</div>'
roster += f'<div class="fill-strip"><div class="fill-row"><strong>Fill remaining slots</strong><button class="control dropdown">{icon("settings", "small")}<span>Bot N</span>{icon("chevron_down", "small")}</button>{button("Fill 4 empty slots")}{button("Shuffle players", "shuffle")}</div><p class="fill-helper">Fill keeps assigned humans and bots.</p></div></section>'

settings = f'<section class="panel settings"><div class="panel-title">{icon("settings")}<h2>MATCH SETTINGS</h2></div>{MAP}'
settings += setting('Map preset', dropdown('Custom'))
settings += setting('Match seed', f'<div class="with-dice">{stepper("54")}{button("", "dice")}</div>')
settings += setting('Map seed', stepper('54'))
settings += setting('Max ticks', stepper('28,800'))
settings += setting('Spawn interval', dropdown('480 ticks'))
settings += setting('Draft mode', dropdown('Unique'))
settings += setting('Map size', stepper('116'))
settings += setting('Camps touch roads', toggle(True))
settings += setting('Wait for LLM', toggle(False))
settings += '<div class="disclosures">'
settings += f'<button class="control disclosure">{icon("terrain")}<span>Map generation</span>{icon("chevron_down", "small")}</button>'
settings += f'<button class="control disclosure">{icon("settings")}<span>Advanced settings</span>{icon("chevron_down", "small")}</button></div></section>'
battle = f'<div class="columns">{roster}{settings}</div><footer class="footer">{button("Back", "arrow_left", "back")}{button("START GAME", "arrow_right", "primary start")}</footer>'
(ROOT / 'battle-setup.html').write_text(page('battle', 'BATTLE SETUP', 'Assign players. Configure your match.', battle))

server = f'<section class="panel server-bar"><strong>Server</strong><input class="field" value="ws://127.0.0.1:9911/ws" aria-label="Server address">{button("Reconnect")}<div class="connection">{icon("status", "dot")}<span>Connected</span></div></section>'
rooms = '<section class="panel room-list"><div class="room-title">'
rooms += f'<div class="title-group">{icon("units", "large")}<div><h2>PUBLIC ROOMS</h2><p class="room-subtitle muted">Rooms for your game version</p></div></div>{button("Refresh", "loop")}</div>'
rooms += f'<div class="search">{icon("search")}<input class="field" placeholder="Search rooms..." aria-label="Search rooms"></div><div class="room-table">'
rooms += '<div class="room-row table-head"><span>ROOM</span><span class="room-count">PLAYERS</span><span>STATUS</span><span></span></div>'
room_data = [('Casual arena', '4 / 10'), ('Evening skirmish', '7 / 10'), ('Bot testing', '1 / 10'), ('Red vs blue', '9 / 10'), ('Full house', '10 / 10')]
for index, (name, count) in enumerate(room_data):
    full = index == 4
    rooms += f'<div class="room-row {"selected" if index == 0 else ""}"><strong>{name}</strong><span class="room-count">{count}</span><span class="status">{icon("status", "dot full" if full else "dot")}{"Full" if full else "Open"}</span>{button("Full" if full else "Join", disabled=full)}</div>'
rooms += f'</div><div class="pagination"><span>5 rooms</span><div class="pages">{button("Previous", disabled=True)}<span>1 / 1</span>{button("Next", disabled=True)}</div></div></section>'
create = f'<section class="panel create-panel"><div class="panel-title">{icon("cross", "large")}<h2>CREATE ROOM</h2></div>'
create += '<label for="room-name">Room name</label><input id="room-name" class="field" value="GotA room"><span>Visibility</span>'
create += f'<div class="segmented">{button("Public", "globe", "selected")}{button("Private", "lock")}</div><p class="helper">Public rooms appear in the room list.</p>'
create += f'{button("CREATE ROOM", "cross", "primary wide")}<p class="helper center">Players and match settings come next.</p><div class="rule"></div>'
create += f'<div class="panel-title invite-title">{icon("link")}<h2>JOIN BY INVITE</h2></div><label for="invite">Invite link or code</label><input id="invite" class="field" placeholder="Paste invite...">{button("Join room", "arrow_right", "wide invite-join", True)}</section>'
multiplayer = server + f'<div class="columns">{rooms}{create}</div><footer class="footer">{button("Back", "arrow_left", "back")}</footer>'
(ROOT / 'multiplayer.html').write_text(page('multiplayer', 'MULTIPLAYER', 'Create a room or join a battle.', multiplayer))
