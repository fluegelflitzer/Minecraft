"""Nachbarabhängige Blockzustände so berechnen, wie Minecraft 26.3 sie beim Bauen setzt.

Litematica vergleicht beim Prüfen den vollen Blockzustand. Ein Zaun ohne die richtigen Verbindungen
oder eine Treppe mit falscher Eckform zählt dort als Fehler, obwohl der Bot alles richtig gesetzt hat.
Deshalb rechnet dieses Modul die Zustände nach den Regeln aus dem Spielcode:
  Treppenformen (StairBlock.getStairsShape), Zäune (FenceBlock.connectsTo), Glasscheiben
  (IronBarsBlock.attachsTo), Mauern inkl. hoch/niedrig und Pfosten (WallBlock), Zauntore in Mauern,
  Laub-Abstand zum nächsten Stamm, Signalfeuer über Heuballen.
Der Ingame-Test baut die Basis im Spiel und vergleicht jeden Zustand mit dieser Rechnung.
"""
from __future__ import annotations

from collections import deque

from farm.blocks import B, DIRS, Block
from farm.model import Model

from .katalog import CCW, CONNECT_EXCEPTIONS, CW, OPP, eintrag, is_logs_tag, sturdy

HORIZ = ("north", "east", "south", "west")


def nb(m: Model, pos, d) -> Block:
    dx, dy, dz = DIRS[d]
    return m.get(pos[0] + dx, pos[1] + dy, pos[2] + dz)


def _form(b: Block) -> str | None:
    e = eintrag(b)
    return e.form if e else None


def _exception(b: Block) -> bool:
    return b.id.endswith(CONNECT_EXCEPTIONS)


# --------------------------------------------------------------------------- Treppen

def _is_stairs(b: Block) -> bool:
    return _form(b) == "treppe"


def stairs_shape(m: Model, pos, b: Block) -> str:
    facing, half = b.prop("facing"), b.prop("half")

    def can_take(face):
        n = nb(m, pos, face)
        return not _is_stairs(n) or n.prop("facing") != facing or n.prop("half") != half

    back = nb(m, pos, facing)
    if _is_stairs(back) and back.prop("half") == half:
        f2 = back.prop("facing")
        if _axis(f2) != _axis(facing) and can_take(OPP[f2]):
            return "outer_left" if f2 == CCW[facing] else "outer_right"
    front = nb(m, pos, OPP[facing])
    if _is_stairs(front) and front.prop("half") == half:
        f3 = front.prop("facing")
        if _axis(f3) != _axis(facing) and can_take(f3):
            return "inner_left" if f3 == CCW[facing] else "inner_right"
    return "straight"


def _axis(d: str) -> str:
    return "x" if d in ("east", "west") else "z"


# --------------------------------------------------------------------------- Zäune, Scheiben, Mauern

def _gate_connects(gate: Block, d: str) -> bool:
    """FenceGateBlock.connectsToDirection: Tor-Ausrichtung quer zur Richtung."""
    return _axis(gate.prop("facing")) == _axis(CW[d])


def fence_connects(fence: Block, n: Block, d: str) -> bool:
    f = _form(n)
    if f == "zaun":
        return (n.id == "nether_brick_fence") == (fence.id == "nether_brick_fence")
    if f == "zauntor":
        return _gate_connects(n, d)
    return not _exception(n) and sturdy(n, OPP[d])


def pane_connects(n: Block, d: str) -> bool:
    f = _form(n)
    if f in ("scheibe", "mauer"):
        return True
    return not _exception(n) and sturdy(n, OPP[d])


def wall_connects(n: Block, d: str) -> bool:
    f = _form(n)
    if f in ("mauer", "scheibe"):
        return True
    if f == "zauntor":
        return _gate_connects(n, d)
    return not _exception(n) and sturdy(n, OPP[d])


def _above_covers(above: Block, d: str | None) -> bool:
    """Deckt der Block darüber die Mauerseite (bzw. den Pfosten bei d=None) ab? Vereinfachung:
    volle Blöcke und Unterseiten-tragende Formen decken alles ab, Mauern ihren Pfosten und verbundene Seiten."""
    if above.id == "air":
        return False
    if sturdy(above, "down"):
        return True
    f = _form(above)
    if d is None and (f == "zaun" or (f == "laterne" and above.prop("hanging") == "false")
                      or (f == "kette" and above.prop("axis") == "y")):
        return True  # schmale Form mittig auf dem Pfosten
    if _form(above) == "mauer":
        if d is None:
            return above.prop("up") == "true"
        return above.prop(d) != "none"
    return False


_POST_OVERRIDE = ("torch", "wall_torch", "_sign", "_banner", "_pressure_plate")


def wall_state(m: Model, pos, b: Block) -> Block:
    above = nb(m, pos, "up")
    sides = {}
    for d in HORIZ:
        if wall_connects(nb(m, pos, d), d):
            sides[d] = "tall" if _above_covers(above, d) else "low"
        else:
            sides[d] = "none"
    up = _raise_post(sides, above)
    return b.with_props(up=up, **sides)


def _raise_post(sides: dict, above: Block) -> bool:
    if _form(above) == "mauer" and above.prop("up") == "true":
        return True
    n, s, e, w = (sides[k] for k in ("north", "south", "east", "west"))
    if (n == s == e == w == "none") or ((n == "none") != (s == "none")) or ((e == "none") != (w == "none")):
        return True
    if (n == "tall" and s == "tall") or (e == "tall" and w == "tall"):
        return False
    return above.id.endswith(_POST_OVERRIDE) or _above_covers(above, None)


# --------------------------------------------------------------------------- Laub

def leaves_distance(m: Model) -> dict:
    dist = {}
    q = deque()
    for p, b in m.blocks.items():
        if is_logs_tag(b.id):
            dist[p] = 0
            q.append(p)
    while q:
        p = q.popleft()
        for d in DIRS:
            dx, dy, dz = DIRS[d]
            n = (p[0] + dx, p[1] + dy, p[2] + dz)
            if n in dist or _form(m.get(*n)) != "laub":
                continue
            if dist[p] + 1 >= 7:
                continue
            dist[n] = dist[p] + 1
            q.append(n)
    return dist


# --------------------------------------------------------------------------- alles zusammen

def finalisieren(m: Model) -> None:
    """Alle nachbarabhängigen Zustände setzen. Reihenfolge: Treppen (beeinflussen tragende Seiten),
    dann Zäune/Scheiben/Tore, dann Mauern von oben nach unten (Pfosten hängt von der Mauer darüber ab)."""
    for pos, b in list(m.blocks.items()):  # Formen hängen nur von facing/half der Nachbarn ab
        if _is_stairs(b):
            m.blocks[pos] = b.with_props(shape=stairs_shape(m, pos, b))
    for pos, b in list(m.blocks.items()):
        f = _form(b)
        if f == "zaun":
            m.blocks[pos] = b.with_props(**{d: fence_connects(b, nb(m, pos, d), d) for d in HORIZ})
        elif f == "scheibe":
            m.blocks[pos] = b.with_props(**{d: pane_connects(nb(m, pos, d), d) for d in HORIZ})
        elif f == "zauntor":
            side = [CW[b.prop("facing")], CCW[b.prop("facing")]]
            m.blocks[pos] = b.with_props(in_wall=any(_form(nb(m, pos, d)) == "mauer" for d in side))
        elif f == "lagerfeuer":
            m.blocks[pos] = b.with_props(signal_fire=nb(m, pos, "down").id == "hay_block")
        elif f == "laub":
            m.blocks[pos] = b.with_props(persistent=True)
    walls = sorted((p for p, b in m.blocks.items() if _form(b) == "mauer"), key=lambda p: -p[1])
    for pos in walls:
        m.blocks[pos] = wall_state(m, pos, m.blocks[pos])
    dist = leaves_distance(m)
    for pos, b in list(m.blocks.items()):
        if _form(b) == "laub":
            m.blocks[pos] = b.with_props(distance=dist.get(pos, 7))


def unveraendert_nach_finalisieren(m: Model) -> list[str]:
    """Kontrolle: ein zweiter Durchlauf darf nichts mehr ändern (Zustände sind stabil)."""
    before = dict(m.blocks)
    finalisieren(m)
    return [f"{p}: {before[p]} -> {m.blocks[p]}" for p in before if before[p] != m.blocks.get(p)]


__all__ = ["finalisieren", "stairs_shape", "B"]
