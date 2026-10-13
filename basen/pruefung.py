"""Statische Prüfungen für bot-baubare Survival-Basen.

  katalog     nur erlaubte Blöcke (survival-tauglich, ein Klick, kein Wachsen/Fallen/Fließen), keine Doppelstufen
  zustaende   nachbarabhängige Zustände sind stabil (ein zweites Durchrechnen ändert nichts)
  teile       Türen und Betten vollständig, Doppelkisten paarweise
  stuetzen    Laternen, Fackeln, Leitern, Türen, Teppiche, Blumen haben ihren Halt
  licht       kein Monster-Spawnplatz mit Blocklicht 0 unter Dach oder auf gebauten Flächen
  bauplan     jeder Block lässt sich in der geplanten Reihenfolge mit einem Klick setzen
"""
from __future__ import annotations

from collections import deque

from farm.blocks import DIRS
from farm.model import Model

from . import bauplan, zustaende
from .katalog import CCW, CW, OPP, eintrag, sturdy


def _nb(p, d):
    dx, dy, dz = DIRS[d]
    return (p[0] + dx, p[1] + dy, p[2] + dz)


def check_katalog(m: Model) -> list[str]:
    errors = []
    for p, b in m.blocks.items():
        e = eintrag(b)
        if e is None:
            errors.append(f"{p}: {b} ist nicht im Katalog (nicht bot-/survival-tauglich)")
        elif e.form == "stufe" and b.prop("type") == "double":
            errors.append(f"{p}: Doppelstufe braucht zwei Klicks – volle Blöcke nehmen")
        elif "waterlogged" in dict(b.props) and b.prop("waterlogged") == "true":
            errors.append(f"{p}: {b} ist wassergeflutet")
    return errors


def check_zustaende(m: Model) -> list[str]:
    import copy
    m2 = copy.deepcopy(m)
    return ["Zustand nicht stabil: " + d for d in zustaende.unveraendert_nach_finalisieren(m2)[:10]]


def check_teile(m: Model) -> list[str]:
    errors = []
    for p, b in m.blocks.items():
        e = eintrag(b)
        if e is None:
            continue
        if e.form == "tuer":
            other = _nb(p, "up" if b.prop("half") == "lower" else "down")
            o = m.get(*other)
            same = {k: v for k, v in b.props if k != "half"}
            if o.id != b.id or {k: v for k, v in o.props if k != "half"} != same or o.prop("half") == b.prop("half"):
                errors.append(f"Tür {p}: zweite Hälfte fehlt oder passt nicht")
        elif e.form == "bett":
            f = b.prop("facing")
            other = _nb(p, f if b.prop("part") == "foot" else OPP[f])
            o = m.get(*other)
            if o.id != b.id or o.prop("facing") != f or o.prop("part") == b.prop("part"):
                errors.append(f"Bett {p}: zweite Hälfte fehlt oder passt nicht")
        elif e.form == "kiste" and b.prop("type") != "single":
            f = b.prop("facing")
            d = CW[f] if b.prop("type") == "left" else CCW[f]
            o = m.get(*_nb(p, d))
            want = "right" if b.prop("type") == "left" else "left"
            if o.id != "chest" or o.prop("facing") != f or o.prop("type") != want:
                errors.append(f"Kiste {p}: Partner fehlt")
    return errors


def _center_support(b, face) -> bool:
    if b.id == "air":
        return False
    if sturdy(b, face):
        return True
    e = eintrag(b)
    return bool(e and (e.form in ("zaun", "mauer") or (e.form == "kette" and b.prop("axis") == "y")))


def check_stuetzen(m: Model) -> list[str]:
    errors = []

    def below_ok(p):
        q = _nb(p, "down")
        return q[1] < 0 or (q[1] == 0 and m.get(*q).id == "air") or m.get(*q).id != "air"

    for p, b in m.blocks.items():
        e = eintrag(b)
        if e is None:
            continue
        q_below = _nb(p, "down")
        ground_below = q_below[1] < 0 or (q_below[1] == 0 and m.get(*q_below).id == "air")
        if e.form == "laterne":
            if b.prop("hanging") == "true":
                if not _center_support(m.get(*_nb(p, "up")), "down"):
                    errors.append(f"Hängelaterne {p} ohne Halt darüber")
            elif not ground_below and not _center_support(m.get(*q_below), "up"):
                errors.append(f"Laterne {p} ohne Halt darunter")
        elif e.form in ("wandfackel", "leiter"):
            f = b.prop("facing")
            if not sturdy(m.get(*_nb(p, OPP[f])), f):
                errors.append(f"{b.id} {p} ohne tragende Wand")
        elif e.form == "tuer" and b.prop("half") == "lower":
            if not ground_below and not sturdy(m.get(*q_below), "up"):
                errors.append(f"Tür {p} ohne festen Boden")
        elif e.form in ("teppich", "fackel"):
            if not below_ok(p):
                errors.append(f"{b.id} {p} schwebt")
        elif e.form == "pflanze":
            if not ground_below and m.get(*q_below).id not in ("dirt", "coarse_dirt", "moss_block"):
                errors.append(f"Blume {p} nicht auf Erde")
    return errors


# --------------------------------------------------------------------------- Licht

def block_light(m: Model) -> dict:
    light, q = {}, deque()
    for p, b in m.blocks.items():
        e = eintrag(b)
        if e and e.licht:
            light[p] = e.licht
            q.append(p)
    sx, sy, sz = m.size
    while q:
        p = q.popleft()
        v = light[p] - 1
        if v <= 0:
            continue
        for d in DIRS:
            n = _nb(p, d)
            if not (-1 <= n[0] <= sx and 0 <= n[1] <= sy and -1 <= n[2] <= sz):
                continue
            b = m.get(*n) if m.inside(*n) else None
            if b is not None and b.id != "air":
                e = eintrag(b)
                if e is None or not e.durchsichtig or e.form in ("treppe", "stufe"):
                    continue  # Treppen/Stufen vorsichtshalber als lichtdicht gerechnet
                vv = v - (1 if e.form == "laub" else 0)
            else:
                vv = v
            if light.get(n, 0) < vv:
                light[n] = vv
                q.append(n)
    return light


def _spawn_floor(b) -> bool:
    if b.id == "air" or b.id == "glass" or b.id.endswith("_leaves"):
        return False
    e = eintrag(b)
    return sturdy(b, "up") and (e is None or e.licht < 14)


def dunkle_stellen(m: Model) -> tuple[list, int, int]:
    """(Spawnplätze mit Licht 0 unter Dach/auf Gebautem, beleuchtete Geländeplätze, alle Geländeplätze)."""
    light = block_light(m)
    sx, sy, sz = m.size
    top = {}
    for (x, y, z) in m.blocks:
        top[(x, z)] = max(top.get((x, z), -1), y)
    dark, lit_ground, all_ground = [], 0, 0
    for x in range(sx):
        for z in range(sz):
            for y in range(1, sy):
                b = m.get(x, y, z)
                e = eintrag(b) if b.id != "air" else None
                if b.id != "air" and not (e and e.form == "pflanze"):
                    continue
                below = m.get(x, y - 1, z)
                natural = y == 1 and below.id == "air"
                if not natural and not _spawn_floor(below):
                    continue
                covered = top.get((x, z), -1) > y
                if natural and not covered:
                    all_ground += 1
                    lit_ground += light.get((x, y, z), 0) > 0
                    continue
                if light.get((x, y, z), 0) == 0:
                    dark.append((x, y, z))
    return dark, lit_ground, all_ground


def check_licht(m: Model) -> list[str]:
    dark, _, _ = dunkle_stellen(m)
    return [f"Dunkler Spawnplatz {p} (Blocklicht 0)" for p in dark[:15]] + (
        [f"... insgesamt {len(dark)} dunkle Plätze"] if len(dark) > 15 else [])


def check_bauplan(m: Model) -> list[str]:
    _, errors = bauplan.plan(m)
    return errors


def run_all(m: Model) -> list[str]:
    errors = []
    for check in (check_katalog, check_zustaende, check_teile, check_stuetzen, check_licht, check_bauplan):
        errors += [f"[{check.__name__[6:]}] {e}" for e in check(m)]
    return errors
