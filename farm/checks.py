"""Statische Prüfungen des Blockmodells (laufen bei jedem build.py).

Die Blocklisten stammen aus dem Code von Minecraft 26.3 (Blocks.java: `.ignitedByLava()`, Block-Tag
`minecraft:blocks_motion`) und decken alle Blöcke ab, die das Modell verwendet.
"""
from __future__ import annotations

from .blocks import AIR
from .model import Model

# Blöcke, an denen Lava Feuer entzünden kann (Blocks.java: .ignitedByLava())
IGNITED_BY_LAVA = {
    "minecraft:oak_trapdoor", "minecraft:oak_sign", "minecraft:oak_wall_sign", "minecraft:oak_fence_gate",
    "minecraft:chest", "minecraft:lectern", "minecraft:oak_planks", "minecraft:oak_slab", "minecraft:oak_log",
}
# Blöcke ohne diese Eigenschaft (zur Kontrolle, dass jeder verwendete Block eingeordnet ist)
NOT_IGNITED_BY_LAVA = {
    "minecraft:cobblestone", "minecraft:cobblestone_slab", "minecraft:cobblestone_wall",
    "minecraft:cobblestone_stairs", "minecraft:glass", "minecraft:hopper", "minecraft:torch",
    "minecraft:wall_torch", "minecraft:ladder", "minecraft:lantern", "minecraft:stonecutter",
    "minecraft:grindstone", "minecraft:anvil",
    "minecraft:dispenser", "minecraft:comparator", "minecraft:redstone_wire", "minecraft:lava_cauldron",
    "minecraft:water", "minecraft:lava", "minecraft:stone", "minecraft:stone_bricks", "minecraft:smooth_stone_slab",
}
# Block-Tag minecraft:blocks_motion (stoppt Lavas Suche nach einem Brandplatz)
BLOCKS_MOTION = {
    "minecraft:cobblestone", "minecraft:cobblestone_slab", "minecraft:cobblestone_wall",
    "minecraft:cobblestone_stairs", "minecraft:glass", "minecraft:hopper", "minecraft:oak_trapdoor",
    "minecraft:oak_fence_gate", "minecraft:chest", "minecraft:lectern", "minecraft:lantern",
    "minecraft:grindstone", "minecraft:anvil",
    "minecraft:stonecutter", "minecraft:dispenser", "minecraft:lava_cauldron", "minecraft:stone",
    "minecraft:stone_bricks", "minecraft:oak_planks", "minecraft:oak_slab", "minecraft:oak_log",
    "minecraft:smooth_stone_slab",
}

_FACES = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def _add(p, d):
    return p[0] + d[0], p[1] + d[1], p[2] + d[2]


def check_known_blocks(m: Model) -> list[str]:
    known = IGNITED_BY_LAVA | NOT_IGNITED_BY_LAVA
    return sorted({f"Block ohne Brand-Einordnung: {b.name}" for b in m.blocks.values() if b.name not in known})


def check_footprint(m: Model) -> list[str]:
    sx, sy, sz = m.size
    errors = []
    if (sx, sz) != (16, 32):
        errors.append(f"Grundfläche {sx}x{sz} statt 16x32")
    if sy > 20:
        errors.append(f"Höhe {sy} > 20")
    return errors


def check_water_lava(m: Model) -> list[str]:
    """Wasser und Lava dürfen sich an keiner Fläche berühren (sonst Obsidian/Bruchstein)."""
    errors = []
    for p, b in m.blocks.items():
        if b.id != "lava":
            continue
        for d in _FACES:
            nb = m.get(*_add(p, d))
            if nb.id == "water" or dict(nb.props).get("waterlogged") == "true":
                errors.append(f"Lava {p} berührt Wasser bei {_add(p, d)}")
    return errors


def lava_fire_spots(m: Model) -> set:
    """Alle Luftfelder, an denen Lava (LavaFluid.randomTick) Feuer setzen könnte."""
    spots = set()

    def ignited(q):
        return m.get(*q).name in IGNITED_BY_LAVA

    for p, b in m.blocks.items():
        if b.id != "lava":
            continue
        # passes == 0: Nachbarn auf Lavahöhe, die selbst entzündbar sind und Luft darüber haben
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                q = _add(p, (dx, 0, dz))
                if ignited(q) and m.get(*_add(q, (0, 1, 0))) == AIR:
                    spots.add(_add(q, (0, 1, 0)))
        # passes 1..2: zufälliger Weg nach oben; Luft mit entzündbarem Nachbarn fängt Feuer,
        # Blöcke aus blocks_motion beenden die Suche, alles andere wird durchlaufen
        frontier = {p}
        for _ in range(2):
            nxt = set()
            for f in frontier:
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        q = _add(f, (dx, 1, dz))
                        blk = m.get(*q)
                        if blk == AIR:
                            if any(ignited(_add(q, d)) for d in _FACES):
                                spots.add(q)
                            nxt.add(q)
                        elif blk.name not in BLOCKS_MOTION:
                            nxt.add(q)
            frontier = nxt
    return spots


def check_fire(m: Model) -> list[str]:
    return [f"Lava kann bei {q} Feuer entzünden" for q in sorted(lava_fire_spots(m))]


def run_all(m: Model) -> list[str]:
    return check_known_blocks(m) + check_footprint(m) + check_water_lava(m) + check_fire(m)
