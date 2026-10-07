"""Materialliste der Weizenfarm (Gegenstände für den Survival-Bau) aus dem Blockmodell."""
from __future__ import annotations

from collections import Counter

from farm.model import Model

_ITEM = {
    "glass": "Glas",
    "farmland": "Ackerboden (Erde/Gras mit der Hacke)",
    "dirt": "Erde",
    "cobblestone": "Bruchstein",
    "cobblestone_slab": "Bruchsteinstufe (obere Hälfte, mit Wasser gefüllt)",
    "hopper": "Trichter",
    "chest": "Kiste",
    "composter": "Komposter",
    "glowstone": "Leuchtstein (Block)",
    "oak_fence_gate": "Eichenzauntor",
    "lightning_rod": "Blitzableiter",
}
IRON = {"Trichter": 5}
COPPER = {"Blitzableiter": 3}


def materials(m: Model) -> Counter:
    return Counter(_ITEM[b.id] for b in m.blocks.values())


def extras(m: Model) -> Counter:
    """Was außer Blöcken gebraucht wird: Wasser, Saatgut, Dorfbewohner."""
    c = Counter()
    c["Wassereimer (für die Wasserstufen; mit Endlosquelle reichen 2)"] = 2
    c["Weizensamen zum ersten Bepflanzen (ein Teil reicht, die Bauern pflanzen nach)"] = sum(
        1 for b in m.blocks.values() if b.id == "farmland")
    c["Dorfbewohner: 4 Bauern (oder ohne Beruf, sie nehmen den Komposter) + 4 Sammler (beliebig)"] = 8
    return c


def iron(c: Counter) -> int:
    return sum(c[k] * v for k, v in IRON.items())


def copper(c: Counter) -> int:
    return sum(c[k] * v for k, v in COPPER.items())
