"""Baukasten für rustikale Basen: Wände, Fachwerk, Satteldächer, Fenster, Türen, Betten, Kamine, Deko.

Koordinaten: x = Osten, y = oben, z = Süden. Ebene y = 0 ist die Geländeoberfläche: Was dort steht
(Wege, Fundament), ersetzt das Gras; Luft auf y = 0 heißt „Gelände bleibt, wie es ist“.
Ab y = 1 bedeutet Luft wirklich Luft.
"""
from __future__ import annotations

from farm.blocks import AIR, B, DIRS, Block
from farm.model import Model

from .katalog import CCW, CW, OPP


class Bau(Model):
    """Blockmodell einer Basis (Größe fest, Blöcke außerhalb sind ein Fehler)."""

    def __init__(self, key: str, titel: str, size: tuple[int, int, int], beschreibung: str):
        super().__init__(*size)
        self.key, self.titel, self.beschreibung = key, titel, beschreibung

    def put(self, x, y, z, block_id: str, **props) -> Block:
        b = B(block_id, **props)
        self.set(x, y, z, b)
        return b

    def clear(self, x, y, z) -> None:
        self.set(x, y, z, AIR)


def step(pos, d, n=1):
    dx, dy, dz = DIRS[d]
    return (pos[0] + dx * n, pos[1] + dy * n, pos[2] + dz * n)


# --------------------------------------------------------------------------- Grundformen

def ring(m: Bau, x0, z0, x1, z1, y, block: Block) -> None:
    """Rechteck-Umriss in einer Ebene."""
    for x in range(x0, x1 + 1):
        m.set(x, y, z0, block)
        m.set(x, y, z1, block)
    for z in range(z0, z1 + 1):
        m.set(x0, y, z, block)
        m.set(x1, y, z, block)


def flaeche(m: Bau, x0, z0, x1, z1, y, block: Block) -> None:
    m.fill(x0, y, z0, x1, y, z1, block)


def wand(m: Bau, x0, z0, x1, z1, y0, y1, block: Block) -> None:
    for y in range(y0, y1 + 1):
        ring(m, x0, z0, x1, z1, y, block)


def pfosten(m: Bau, x, z, y0, y1, log: str) -> None:
    for y in range(y0, y1 + 1):
        m.put(x, y, z, log, axis="y")


def balkenkranz(m: Bau, x0, z0, x1, z1, y, log: str, ecken: str = "y") -> None:
    """Liegende Stämme rund um ein Rechteck: an Nord-/Südseite in x-Richtung, an Ost-/Westseite in z-Richtung.
    Ecken stehen senkrecht: daran lassen sich die liegenden Reihen ohne Hilfsblock ansetzen."""
    for x in range(x0 + 1, x1):
        m.put(x, y, z0, log, axis="x")
        m.put(x, y, z1, log, axis="x")
    for z in range(z0 + 1, z1):
        m.put(x0, y, z, log, axis="z")
        m.put(x1, y, z, log, axis="z")
    for x, z in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
        m.put(x, y, z, log, axis=ecken)


# --------------------------------------------------------------------------- Dach

def satteldach(m: Bau, x0, x1, z0, z1, y, treppe: str, first: str | None = None, giebel: Block | None = None,
               giebel_x: tuple = (), first_achse: str = "x") -> list:
    """Satteldach mit First in x-Richtung (first_achse="x") über x0..x1, Traufen bei z0 und z1.

    Reihe i liegt auf Höhe y+i bei z0+i (Treppe nach Süden) und z1-i (Treppe nach Norden).
    Ungerade Breite: oben eine untere Stufe `first`. giebel_x: x-Positionen der Giebelwände, die bis unter
    das Dach mit `giebel` geschlossen werden (zwischen den Treppen derselben Höhe).
    Für first_achse="z" wird alles um 90 Grad gedreht (Traufen bei x0 und x1, Giebel bei giebel_x = z-Werte).
    Gibt die Liste der Giebelfeld-Positionen zurück.
    """
    gfeld = []
    if first_achse == "x":
        a0, a1, b0, b1 = x0, x1, z0, z1
        lo_face, hi_face = "south", "north"

        def P(a, yy, b):
            return (a, yy, b)
    else:
        a0, a1, b0, b1 = z0, z1, x0, x1
        lo_face, hi_face = "east", "west"

        def P(a, yy, b):
            return (b, yy, a)
    i = 0
    while b0 + i <= b1 - i:
        yy = y + i
        lo, hi = b0 + i, b1 - i
        for a in range(a0, a1 + 1):
            if lo == hi:
                if first:
                    m.put(*P(a, yy, lo), first, type="bottom")
            else:
                m.put(*P(a, yy, lo), treppe, facing=lo_face, half="bottom")
                m.put(*P(a, yy, hi), treppe, facing=hi_face, half="bottom")
        if giebel is not None and i > 0:  # Reihe 0 liegt auf Höhe des Balkenkranzes
            for a in giebel_x:
                for b in range(lo + 1, hi):
                    m.set(*P(a, yy, b), giebel)
                    gfeld.append(P(a, yy, b))
        i += 1
    return gfeld


def pultdach(m: Bau, x0, x1, z_hoch, z_tief, y_hoch, treppe: str) -> None:
    """Pultdach (Vordach) von z_hoch (oben, an der Hauswand) nach z_tief (unten), eine Reihe pro Block."""
    d = 1 if z_tief > z_hoch else -1
    facing = "north" if d > 0 else "south"
    for i, z in enumerate(range(z_hoch, z_tief + d, d)):
        for x in range(x0, x1 + 1):
            m.put(x, y_hoch - i, z, treppe, facing=facing, half="bottom")


# --------------------------------------------------------------------------- Öffnungen und Möbel

def tuer(m: Bau, x, y, z, holz: str, facing: str, hinge: str = "left") -> None:
    """Tür: facing = Blickrichtung des Spielers beim Setzen (Bot schaut in diese Richtung)."""
    m.put(x, y, z, f"{holz}_door", facing=facing, half="lower", hinge=hinge)
    m.put(x, y + 1, z, f"{holz}_door", facing=facing, half="upper", hinge=hinge)


def bett(m: Bau, x, y, z, farbe: str, facing: str) -> None:
    """Bett: Fußende auf (x, y, z), Kopfende eins weiter in Blickrichtung facing."""
    m.put(x, y, z, f"{farbe}_bed", facing=facing, part="foot")
    hx, hy, hz = step((x, y, z), facing)
    m.put(hx, hy, hz, f"{farbe}_bed", facing=facing, part="head")


def doppelkiste(m: Bau, x, y, z, facing: str, richtung: str) -> None:
    """Zwei Kisten nebeneinander (zweite in `richtung`), Vorderseite nach facing. Typ wie im Spiel:
    die Kiste, deren Partner im Uhrzeigersinn neben ihr steht, ist "left"."""
    a = (x, y, z)
    b = step(a, richtung)
    if richtung == CW[facing]:
        ta, tb = "left", "right"
    elif richtung == CCW[facing]:
        ta, tb = "right", "left"
    else:
        raise ValueError("Doppelkiste muss quer zur Blickrichtung stehen")
    m.put(*a, "chest", facing=facing, type=ta)
    m.put(*b, "chest", facing=facing, type=tb)


def haengelaterne(m: Bau, x, y, z, kette: int = 0) -> None:
    """Laterne hängt an (x, y+1+kette, z); dazwischen `kette` Kettenglieder."""
    for k in range(kette):
        m.put(x, y + 1 + k, z, "iron_chain", axis="y")
    m.put(x, y, z, "lantern", hanging=True)


def laternenpfahl(m: Bau, x, y, z, zaun: str, hoehe: int = 1) -> None:
    for k in range(hoehe):
        m.put(x, y + k, z, zaun)
    m.put(x, y + hoehe, z, "lantern", hanging=False)


def busch(m: Bau, positionen, laub: str) -> None:
    for p in positionen:
        m.put(*p, laub, persistent=True)


def opposite(d: str) -> str:
    return OPP[d]
