"""Materialliste (Gegenstände, die man zum Bauen braucht) aus dem Blockmodell."""
from __future__ import annotations

from collections import Counter

from .model import Model

# Block -> (Gegenstand, Hinweis); Flüssigkeiten: nur Quellen zählen (fließendes Wasser entsteht von selbst)
_ITEM = {
    "cobblestone": "Bruchstein",
    "cobblestone_slab": "Bruchsteinstufe",
    "cobblestone_wall": "Bruchsteinmauer",
    "cobblestone_stairs": "Bruchsteintreppe",
    "oak_trapdoor": "Eichenfalltür",
    "oak_sign": "Eichenschild",
    "oak_wall_sign": "Eichenschild",
    "oak_fence_gate": "Eichenzauntor",
    "glass": "Glas",
    "torch": "Fackel",
    "wall_torch": "Fackel",
    "ladder": "Leiter",
    "chest": "Kiste",
    "hopper": "Trichter",
    "lava_cauldron": "Kessel",
    "stonecutter": "Steinsäge",
    "dispenser": "Werfer",
    "comparator": "Komparator",
    "redstone_wire": "Redstone-Staub",
    "lantern": "Laterne",
    "lectern": "Lesepult",
    "grindstone": "Schleifstein",
    "anvil": "Amboss",
    "water": "Wassereimer (Quellen)",
    "lava": "Lavaeimer",
}

# Eisen- und Quarzbedarf je Gegenstand (Vanilla-Rezepte)
IRON = {"Trichter": 5, "Kessel": 7, "Steinsäge": 1, "Laterne": 8 / 9, "Amboss": 31}
QUARTZ = {"Komparator": 1}


def materials(m: Model) -> Counter:
    c = Counter()
    for b in m.blocks.values():
        if b.id == "water" and b.prop("level") != "0":
            continue
        c[_ITEM[b.id]] += 1
        if b.id == "lava_cauldron":
            c["Lavaeimer"] += 1
    return c


def iron(c: Counter) -> float:
    return sum(c[k] * v for k, v in IRON.items())


def quartz(c: Counter) -> int:
    return sum(c[k] * v for k, v in QUARTZ.items())
