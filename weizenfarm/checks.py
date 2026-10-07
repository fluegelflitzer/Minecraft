"""Statische Prüfungen der Weizenfarm (laufen vor jedem Export)."""
from __future__ import annotations

from collections import deque

from farm.blocks import _DATA
from farm.model import Model

from . import model as wm

MAX_X, MAX_Z, MAX_Y = 32, 16, 23  # 2 x 1 Chunks, 23 hoch

# Blöcke, durch die Blocklicht ungehindert geht (Weizen wächst später in der Luft über dem Acker)
_TRANSPARENT = {"air", "glass", "oak_fence_gate", "ladder"}
_LIGHT_SOURCES = {"jack_o_lantern", "glowstone"}


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
    if sx > MAX_X or sz > MAX_Z:
        errors.append(f"Grundriss {sx}x{sz} größer als 2x1 Chunks")
    if sy > MAX_Y:
        errors.append(f"Höhe {sy} größer als {MAX_Y}")
    return errors


def _is_water(b) -> bool:
    return b.id == "water" or dict(b.props).get("waterlogged") == "true"


def check_hydration(m: Model) -> list[str]:
    """Jeder Acker hat Wasser im Umkreis von 4 Blöcken (gleiche Höhe) und Luft darüber."""
    water = [p for p, b in m.blocks.items() if _is_water(b)]
    errors = []
    for (x, y, z), b in m.blocks.items():
        if b.id != "farmland":
            continue
        if not any(wy == y and abs(wx - x) <= 4 and abs(wz - z) <= 4 for wx, wy, wz in water):
            errors.append(f"Acker {(x, y, z)} ohne Wasser in Reichweite")
        if m.get(x, y + 1, z).id != "air":
            errors.append(f"Acker {(x, y, z)} nicht frei nach oben")
    return errors


def block_light(m: Model) -> dict:
    """Blocklicht (vereinfacht, konservativ): breitet sich nur durch Luft/Glas/Tore aus, -1 je Block."""
    sx, sy, sz = m.size
    light, q = {}, deque()
    for p, b in m.blocks.items():
        if b.id in _LIGHT_SOURCES:
            light[p] = 15
            q.append(p)
    while q:
        x, y, z = q.popleft()
        v = light[(x, y, z)] - 1
        if v <= 0:
            continue
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            n = (x + dx, y + dy, z + dz)
            if not (0 <= n[0] < sx and 0 <= n[1] < sy and 0 <= n[2] < sz):
                continue
            if m.get(*n).id in _TRANSPARENT and light.get(n, 0) < v:
                light[n] = v
                q.append(n)
    return light


def check_light(m: Model) -> list[str]:
    """Weizen braucht Licht >= 9 (ohne Himmelslicht gerechnet); keine dunkle Stelle für Monster im Inneren."""
    light = block_light(m)
    errors = []
    for (x, y, z), b in m.blocks.items():
        if b.id == "farmland" and light.get((x, y + 1, z), 0) < 9:
            errors.append(f"Zu dunkel für Weizen über {(x, y, z)}: {light.get((x, y + 1, z), 0)}")
    sx, sy, sz = m.size
    for (x, y, z), b in m.blocks.items():
        top_solid = b.id in ("dirt", "cobblestone", "glass", "cobbled_deepslate") or (b.id.endswith("_slab") and b.prop("type") != "bottom")
        inside = 0 < x < sx - 1 and 0 < z < wm.WALL_Z[1] and x not in (15, 16)
        if top_solid and inside and y + 2 < sy and m.get(x, y + 1, z).id == "air" \
                and m.get(x, y + 2, z).id == "air" and light.get((x, y + 1, z), 0) == 0:
            errors.append(f"Dunkle Stelle {(x, y + 1, z)}")
    return errors


_STEP = {"down": (0, -1, 0), "north": (0, 0, -1), "south": (0, 0, 1), "west": (-1, 0, 0), "east": (1, 0, 0)}


def follow_hoppers(m: Model, pos) -> tuple | None:
    """Folgt einer Trichterkette bis zum Behälter; liefert dessen Position (oder None)."""
    seen = set()
    while m.get(*pos).id == "hopper" and pos not in seen:
        seen.add(pos)
        d = _STEP[m.get(*pos).prop("facing")]
        pos = (pos[0] + d[0], pos[1] + d[1], pos[2] + d[2])
    return pos if m.get(*pos).id == "chest" else None


def check_collectors(m: Model) -> list[str]:
    """Sammler-Zelle dicht, Sichtschlitze frei, Decke darüber; alle Trichter enden in der Zentralkiste."""
    errors = []
    chests = set(m.notes["chest"])
    for (x, y, z) in m.notes["cell"]:
        want = {(x, y - 1, z): "dirt", (x, y, z - 1): "cobbled_deepslate", (x, y + 1, z - 1): "cobbled_deepslate",
                (x, y, z + 1): "hopper", (x, y + 1, z + 1): "hopper"}
        for sx in (x - 1, x + 1):
            want[(sx, y, z)] = "hopper"
            want[(sx, y, z + 1)] = "hopper"
            want[(sx, y, z - 1)] = "cobbled_deepslate"
            for dz in (-1, 0, 1):
                want[(sx, y + 1, z + dz)] = "air"  # Sichtschlitz
        for pos, bid in want.items():
            if m.get(*pos).id != bid:
                errors.append(f"Sammler {(x, y, z)}: {pos} ist {m.get(*pos)}, erwartet {bid}")
        if m.get(x, y, z).id != "air" or m.get(x, y + 1, z).id != "air":
            errors.append(f"Sammler {(x, y, z)}: Zelle nicht frei")
        for sx in (x - 1, x, x + 1):  # Decke über Zelle und Schlitzen: voller Block
            for dz in ((-1, 0, 1) if sx != x else (0,)):
                if m.get(sx, y + 2, z + dz).id in ("air", "farmland"):
                    errors.append(f"Sammler {(x, y, z)}: keine Decke über {(sx, y + 1, z + dz)}")
        for start in ((x - 1, y, z), (x + 1, y, z), (x - 1, y, z + 1), (x + 1, y, z + 1)):
            end = follow_hoppers(m, start)
            if end not in chests:
                errors.append(f"Trichter {start} endet nicht in der Zentralkiste, sondern bei {end}")
    for pos in chests:
        above = m.get(pos[0], pos[1] + 1, pos[2])
        if above.id not in ("air", "glass", "hopper"):
            errors.append(f"Kiste {pos} lässt sich nicht öffnen: {above} darüber")
    return errors


def run_all(m: Model) -> list[str]:
    errors = []
    for check in (check_states, check_footprint, check_hydration, check_light, check_collectors):
        errors += check(m)
    return errors
