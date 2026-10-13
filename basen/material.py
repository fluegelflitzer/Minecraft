"""Materialliste einer Basis (Gegenstände fürs Inventar), mit deutschen Namen und Eisenbedarf."""
from __future__ import annotations

from collections import Counter

from .katalog import eintrag, name_de

# Eisenbarren je Gegenstand (Vanilla-Rezepte; Nuggets anteilig)
IRON = {"lantern": 8 / 9, "iron_chain": 1 + 2 / 9, "cauldron": 7, "blast_furnace": 5, "smithing_table": 2,
        "stonecutter": 1}


def zaehlen(steps) -> Counter:
    return Counter(s.item for s in steps if s.aktion == "setzen")


def hilfsbloecke(steps) -> int:
    """Wie viele Hilfsblöcke gleichzeitig stehen (so viele Erde braucht der Bot im Inventar)."""
    now = most = 0
    for s in steps:
        now += {"hilfsblock": 1, "abbauen": -1}.get(s.aktion, 0)
        most = max(most, now)
    return most


def stapel(n: int, size: int = 64) -> str:
    if n < size:
        return str(n)
    s, r = divmod(n, size)
    return f"{s} St." + (f" + {r}" if r else "")


def liste(steps) -> list[dict]:
    c = zaehlen(steps)
    out = []
    for item, n in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])):
        e = eintrag(item)
        stack = 1 if item.endswith("_bed") else 64
        d = {"item": "minecraft:" + item, "name": name_de(item), "anzahl": n, "stapel": stapel(n, stack)}
        if e is not None and e.werkzeug:
            d["werkzeug"] = e.werkzeug
        out.append(d)
    h = hilfsbloecke(steps)
    if h:
        out.append({"item": "minecraft:dirt", "name": name_de("dirt"), "anzahl": h, "stapel": str(h),
                    "hinweis": "Hilfsblöcke: werden kurz gesetzt und gleich wieder abgebaut"})
    return out


def eisen(c: Counter) -> float:
    return sum(c[k] * v for k, v in IRON.items())
