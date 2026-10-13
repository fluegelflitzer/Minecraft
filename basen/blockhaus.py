"""Blockhaus mit Veranda: Wände aus liegenden Fichtenstämmen mit überstehenden Eckköpfen, Schleppdach
über der Veranda, Bruchsteinkamin am Ostgiebel.

Haus 13 x 9 (x 3..15, z 3..11), Wände y2..5, Balkenkranz y6, Satteldach (First in x-Richtung) bis y11.
Innen: Wohnküche mit Kamin, Esstisch und Kochecke; Vorratskammer unter dem Dachboden; Dachboden mit
zwei Betten (Leiter an der Kammerwand). Veranda (z 12..14) mit Geländer, Stühlen und Laternen.
"""
from __future__ import annotations

from farm.blocks import B

from . import kit
from .kit import Bau

SIZE = (19, 14, 18)
X0, Z0, X1, Z1 = 3, 3, 15, 11
LOG = "spruce_log"
ROOF = "cobbled_deepslate"
ORTGANG = "spruce"


def _walls(m: Bau) -> None:
    """Blockwände: Reihen wechseln sich ab, an jeder Ecke steht abwechselnd ein Kopf nach außen über."""
    for y in range(2, 6):
        if y % 2 == 0:  # Nord-/Südwand durchgehend mit Köpfen in x-Richtung
            for x in range(X0 - 1, X1 + 2):
                m.put(x, y, Z0, LOG, axis="x")
                m.put(x, y, Z1, LOG, axis="x")
            for z in range(Z0 + 1, Z1):
                m.put(X0, y, z, LOG, axis="z")
                m.put(X1, y, z, LOG, axis="z")
        else:  # Ost-/Westwand durchgehend mit Köpfen in z-Richtung
            for z in range(Z0 - 1, Z1 + 2):
                m.put(X0, y, z, LOG, axis="z")
                m.put(X1, y, z, LOG, axis="z")
            for x in range(X0 + 1, X1):
                m.put(x, y, Z0, LOG, axis="x")
                m.put(x, y, Z1, LOG, axis="x")
    kit.balkenkranz(m, X0, Z0, X1, Z1, 6, LOG)


def _window(m: Bau, xs, zs, ys, aussen: str, sims: bool = True) -> None:
    for x in xs:
        for z in zs:
            for y in ys:
                m.put(x, y, z, "glass_pane")
            if sims:
                sx, sy, sz = kit.step((x, min(ys) - 1, z), aussen)
                if m.get(sx, sy, sz).id == "air":
                    m.put(sx, sy, sz, "spruce_trapdoor", facing=aussen, half="top")


def build(roof: str | None = None, ortgang: str | None = None) -> Bau:
    global ROOF, ORTGANG
    ROOF, ORTGANG = roof or ROOF, ortgang or ORTGANG
    m = Bau("blockhaus", "Blockhaus mit Veranda", SIZE,
            "Rustikales Blockhaus aus Fichtenstämmen, 13x9, mit Veranda, Kamin, Vorratskammer und Dachboden")
    cobble, mossy = B("cobblestone"), B("mossy_cobblestone")

    # Sockel und Böden
    kit.ring(m, X0, Z0, X1, Z1, 1, cobble)
    for x, z in ((3, 6), (7, 3), (15, 9), (12, 11), (5, 11)):
        m.set(x, 1, z, mossy)
    kit.flaeche(m, X0 + 1, Z0 + 1, X1 - 1, Z1 - 1, 1, B("oak_planks"))
    _walls(m)

    # Dach: Satteldach, Südseite läuft als Schleppdach über die Veranda weiter
    kit.satteldach(m, X0 - 1, X1 + 1, Z0 - 1, Z1 + 1, 6, f"{ROOF}_stairs", first=f"{ROOF}_slab",
                   giebel=B("spruce_planks"), giebel_x=(X0, X1))
    for i, z in enumerate((Z1 + 2, Z1 + 3)):
        for x in range(X0 - 1, X1 + 2):
            m.put(x, 5 - i, z, f"{ROOF}_stairs", facing="north")
    # Ortgang (Dachkante an den Giebeln) in Kontrastfarbe
    for (px, py, pz), b in list(m.blocks.items()):
        if px in (X0 - 1, X1 + 1) and py >= 4 and b.id.startswith(ROOF):
            if b.id.endswith("_stairs"):
                m.put(px, py, pz, f"{ORTGANG}_stairs", facing=b.prop("facing"))
            else:
                m.put(px, py, pz, f"{ORTGANG}_slab", type="bottom")

    # Veranda: Bretterboden, Pfosten, Geländer, Treppe
    zv = Z1 + 3  # Vorderkante
    kit.flaeche(m, X0, Z1 + 1, X1, zv, 1, B("spruce_planks"))
    for x in (X0, 7, 11, X1):
        kit.pfosten(m, x, zv, 2, 3, LOG)
    for x in range(X0 + 1, X1):
        if x not in (7, 11, 9):
            m.put(x, 2, zv, "spruce_fence")
    for z in (Z1 + 1, Z1 + 2):
        m.put(X0, 2, z, "spruce_fence")
        m.put(X1, 2, z, "spruce_fence")
    m.put(9, 1, zv + 1, "spruce_stairs", facing="north")
    for x in (5, 13):
        kit.haengelaterne(m, x, 4, Z1 + 2)
    # Verandamöbel: zwei Stühle mit Tischchen, Fässer
    m.put(4, 2, Z1 + 1, "spruce_stairs", facing="west")
    m.put(5, 2, Z1 + 1, "spruce_fence")
    m.put(5, 3, Z1 + 1, "spruce_pressure_plate")
    m.put(6, 2, Z1 + 1, "spruce_stairs", facing="east")
    m.put(14, 2, Z1 + 1, "barrel", facing="up")
    m.put(13, 2, Z1 + 1, "barrel", facing="up")

    # Tür und Fenster
    kit.tuer(m, 9, 2, Z1, "spruce", facing="north", hinge="left")
    _window(m, (5, 6), (Z1,), (3, 4), "south", sims=False)
    _window(m, (12, 13), (Z1,), (3, 4), "south", sims=False)
    _window(m, (6, 7), (Z0,), (3, 4), "north")
    _window(m, (11, 12), (Z0,), (3, 4), "north")
    _window(m, (X0,), (6, 7, 8), (3, 4, 5), "west")
    _window(m, (X1,), (4, 10), (3, 4, 5), "east")
    _window(m, (X0,), (7,), (8,), "west", sims=False)  # Giebelfenster

    # Kamin außen am Ostgiebel: unten 3 breit, oben 1 breit, Lagerfeuer obendrauf
    cx = X1 + 1
    for z in (6, 7, 8):
        for y in range(1, 5):
            m.set(cx, y, z, cobble)
    m.set(cx, 2, 6, mossy)
    m.put(cx, 5, 6, "cobblestone_stairs", facing="south")
    m.put(cx, 5, 8, "cobblestone_stairs", facing="north")
    for y in range(5, 13):
        m.set(cx, y, 7, cobble)
    m.put(cx, 13, 7, "campfire", facing="west")

    # --- Innen
    # Trennwand zur Vorratskammer (x 4..7) unter dem Dachboden, Tür in der Mitte
    for z in range(Z0 + 1, Z1):
        for y in range(2, 6):
            m.put(8, y, z, "spruce_planks")
    kit.tuer(m, 8, 2, 7, "spruce", facing="west", hinge="left")
    # Dachboden x 4..8 auf y6, Geländer, Leiter an der Kammerwand
    kit.flaeche(m, X0 + 1, Z0 + 1, 8, Z1 - 1, 6, B("spruce_planks"))
    for z in (4, 5, 6, 7, 8, 10):
        m.put(8, 7, z, "spruce_fence")
    for y in range(2, 7):
        m.put(9, y, 9, "ladder", facing="east")
    kit.bett(m, 5, 7, 6, "blue", facing="west")
    kit.bett(m, 5, 7, 8, "blue", facing="west")
    m.put(4, 7, 7, "chest", facing="east")
    m.put(7, 7, 5, "barrel", facing="up")
    kit.haengelaterne(m, 6, 9, 7, kette=1)

    # Vorratskammer: Kisten, Fässer, Laterne
    kit.doppelkiste(m, 4, 2, 4, facing="south", richtung="east")
    kit.doppelkiste(m, 4, 2, 10, facing="north", richtung="east")
    m.put(6, 2, 4, "barrel", facing="up")
    m.put(7, 2, 4, "barrel", facing="up")
    m.put(4, 3, 4, "barrel", facing="up")
    m.put(4, 2, 7, "crafting_table")
    m.put(4, 2, 6, "barrel", facing="east")
    kit.haengelaterne(m, 6, 5, 7)

    # Wohnküche (x 9..14): Kamin, Kochecke, Esstisch, Teppich
    m.put(14, 2, 7, "campfire", facing="west")
    for z in (6, 8):
        m.set(14, 2, z, cobble)
        m.put(14, 3, z, "cobblestone_stairs", facing="east", half="top")
    m.set(14, 3, 7, cobble)
    for y in (4, 5):
        m.set(14, y, 7, cobble)
    m.put(10, 2, 4, "crafting_table")
    m.put(11, 2, 4, "furnace", facing="south")
    m.put(12, 2, 4, "smoker", facing="south")
    m.put(13, 2, 4, "barrel", facing="south")
    m.put(14, 2, 4, "cauldron")
    for z in (6, 7, 8):
        m.put(11, 2, z, "spruce_fence")
        m.put(11, 3, z, "spruce_pressure_plate")
        m.put(10, 2, z, "spruce_stairs", facing="west")
    for z in (6, 7, 8):
        m.put(13, 2, z, "red_carpet")
    m.put(12, 2, 10, "bookshelf")
    m.put(13, 2, 10, "bookshelf")
    m.put(14, 2, 10, "chest", facing="west")
    # Querbalken unter dem Dach mit Hängelaternen
    for z in range(Z0 + 1, Z1):
        m.put(12, 7, z, LOG, axis="z")
    kit.haengelaterne(m, 12, 6, 6)
    kit.haengelaterne(m, 12, 6, 9)

    # --- Außen: Holzstapel am Westgiebel, Weg, Laternenpfahl, Büsche, Blumen
    for z in range(5, 10):
        for y in (1, 2):
            m.put(2, y, z, LOG, axis="x")
        m.put(1, 1, z, LOG, axis="x")
    for z in (zv + 2, zv + 3):
        m.put(9, 0, z, "coarse_dirt")
        m.put(8 + (z % 2), 0, z, "coarse_dirt")
    kit.laternenpfahl(m, 7, 1, zv + 2, "spruce_fence")
    # Büsche an den Südecken (an ihnen setzt der Bot auch die erste Stammreihe der Südwand an)
    kit.busch(m, [(16, 1, 12), (17, 1, 12), (16, 2, 12), (17, 1, 11), (17, 2, 11), (1, 1, 12), (1, 1, 11), (1, 2, 12),
                  (1, 2, 11)], "oak_leaves")
    kit.busch(m, [(17, 1, 3), (17, 1, 4), (17, 2, 3), (1, 1, 2), (2, 1, 2)], "spruce_leaves")
    for x, z, f in ((4, zv + 1, "poppy"), (5, zv + 1, "dandelion"), (12, zv + 1, "cornflower"), (13, zv + 1, "poppy"),
                    (14, zv + 1, "oxeye_daisy"), (6, zv + 2, "allium"), (11, zv + 2, "azure_bluet")):
        m.put(x, 1, z, f)
    return m
