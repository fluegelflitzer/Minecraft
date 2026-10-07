"""Materialliste der Weizenfarm (Gegenstände für den Survival-Bau) aus dem Blockmodell."""
from __future__ import annotations

from collections import Counter

from farm.model import Model


_ITEM = {
    "glass": "Glas (nur über der Zentralkiste)",
    "cobbled_deepslate": "Bruchtiefenschiefer",
    "farmland": "Ackerboden (Erde mit der Hacke)",
    "dirt": "Erde",
    "cobblestone": "Bruchstein",
    "hopper": "Trichter",
    "chest": "Kiste",
    "composter": "Komposter",
    "jack_o_lantern": "Kürbislaterne",
    "glowstone": "Leuchtstein (Block)",
    "oak_fence_gate": "Eichenzauntor",
    "ladder": "Leiter",
    "lightning_rod": "Blitzableiter",
}
IRON = {"Trichter": 5}
COPPER = {"Blitzableiter": 3}


def _item(b) -> str:
    if b.id == "cobblestone_slab":
        if b.prop("waterlogged") == "true":
            return "Bruchsteinstufe (untere Hälfte, mit Wasser gefüllt)"
        return "Bruchsteinstufe (obere Hälfte, Balkonboden)"
    return _ITEM[b.id]


def materials(m: Model) -> Counter:
    return Counter(_item(b) for b in m.blocks.values())


def extras(m: Model) -> Counter:
    """Was außer Blöcken gebraucht wird: Wasser, Saatgut, Dorfbewohner."""
    c = Counter()
    c["Wassereimer (für die Wasserstufen; mit Endlosquelle reichen 2)"] = 2
    c["Weizensamen zum ersten Bepflanzen (ein Teil reicht, die Bauern pflanzen nach)"] = sum(
        1 for b in m.blocks.values() if b.id == "farmland")
    farmers = len(m.notes["lamp"])
    collectors = len(m.notes["cell"])
    c[f"Dorfbewohner: {farmers} Bauern (oder ohne Beruf, sie nehmen den Komposter) + {collectors} Sammler (beliebig)"] = \
        farmers + collectors
    return c


def iron(c: Counter) -> int:
    return sum(c[k] * v for k, v in IRON.items())


def copper(c: Counter) -> int:
    return sum(c[k] * v for k, v in COPPER.items())

