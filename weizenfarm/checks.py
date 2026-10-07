"""Statische Prüfungen der Weizenfarm (laufen vor jedem Export)."""
from __future__ import annotations

from farm.blocks import _DATA
from farm.model import Model

from . import model as wm

MAX_XZ, MAX_Y = 32, 24


def check_states(m: Model) -> list[str]:
    """Jeder Blockzustand existiert so in 26.3 (Name, Eigenschaften, Werte, vollständig)."""
    errors = set()
    for b in m.blocks.values():
        spec = _DATA.get(b.name)
        props = dict(b.props)
        if spec is None:
            errors.add(f"Unbekannter Block {b.name}")
        elif set(props) != set(spec["properties"]) or any(v not in spec["properties"][k] for k, v in props.items()):
            errors.add(f"Ungültiger Zustand {b}")
    return sorted(errors)


def check_footprint(m: Model) -> list[str]:
    sx, sy, sz = m.size
    errors = []
    if sx > MAX_XZ or sz > MAX_XZ:
        errors.append(f"Grundriss {sx}x{sz} größer als 2x2 Chunks")
    if sy > MAX_Y:
        errors.append(f"Höhe {sy} größer als {MAX_Y}")
    return errors


def _is_water(m: Model, pos) -> bool:
    b = m.get(*pos)
    return b.id == "water" or ("waterlogged" in dict(b.props) and b.prop("waterlogged") == "true")


def check_hydration(m: Model) -> list[str]:
    """Jeder Acker hat Wasser im Umkreis von 4 Blöcken (gleiche Höhe) und Luft darüber."""
    water = [p for p in m.blocks if _is_water(m, p)]
    errors = []
    for (x, y, z), b in m.blocks.items():
        if b.id != "farmland":
            continue
        if not any(wy == y and abs(wx - x) <= 4 and abs(wz - z) <= 4 for wx, wy, wz in water):
            errors.append(f"Acker {(x, y, z)} ohne Wasser in Reichweite")
        if m.get(x, y + 1, z).id != "air":
            errors.append(f"Acker {(x, y, z)} nicht frei nach oben")
    return errors


def check_light(m: Model) -> list[str]:
    """Kein Platz mit tragender Oberseite und 2 Blöcken Luft darüber bleibt ohne Blocklicht (Monster)."""
    lamps = [p for p, b in m.blocks.items() if b.id == "glowstone"]
    sx, sy, sz = m.size
    errors = []
    for (x, y, z), b in m.blocks.items():
        top_solid = b.id in ("dirt", "cobblestone", "glass") or (b.id.endswith("_slab") and b.prop("type") != "bottom")
        if not top_solid or not (0 < x < sx - 1 and 0 < z < sz - 1) or y + 2 >= sy:
            continue
        if m.get(x, y + 1, z).id != "air" or m.get(x, y + 2, z).id != "air":
            continue
        # Licht innerhalb desselben Moduls (keine Wand dazwischen): Manhattan-Abstand < 15
        same = [L for L in lamps if (L[0] < wm.MID) == (x < wm.MID) and (L[2] < wm.MID) == (z < wm.MID)]
        if not any(abs(L[0] - x) + abs(L[1] - (y + 1)) + abs(L[2] - z) < 15 for L in same):
            errors.append(f"Dunkle Stelle {(x, y + 1, z)}")
    return errors


def check_collectors(m: Model) -> list[str]:
    """Sammler-Zelle: Kiste als Boden, Schlitz-Trichter davor -> Trichter -> Kiste, Zelle dicht, Schlitz frei."""
    errors = []
    for (x, y, z) in m.notes["cell"]:
        dz = 1 if z < wm.MID else -1  # Richtung ins Modul
        out = "north" if dz == 1 else "south"
        want = {
            (x, y - 1, z): ("chest", None),
            (x, y, z + dz): ("hopper", "down"),
            (x, y - 1, z + dz): ("hopper", out),
            (x, y + 2, z): ("glass", None),
            (x - 1, y, z): ("glass", None), (x + 1, y, z): ("glass", None),
            (x - 1, y + 1, z): ("glass", None), (x + 1, y + 1, z): ("glass", None),
            (x, y, z - dz): ("glass", None), (x, y + 1, z - dz): ("glass", None),
            (x, y + 1, z + dz): ("air", None),  # Sichtschlitz
            (x, y - 1, z - dz): ("air", None),  # Loch in der Außenwand vor der Kiste
        }
        for pos, (bid, facing) in want.items():
            b = m.get(*pos)
            if b.id != bid or (facing and b.prop("facing") != facing):
                errors.append(f"Sammler {(x, y, z)}: {pos} ist {b}, erwartet {bid} {facing or ''}")
        if m.get(x, y, z).id != "air" or m.get(x, y + 1, z).id != "air":
            errors.append(f"Sammler {(x, y, z)}: Zelle nicht frei")
    return errors


def run_all(m: Model) -> list[str]:
    errors = []
    for check in (check_states, check_footprint, check_hydration, check_light, check_collectors):
        errors += check(m)
    return errors
