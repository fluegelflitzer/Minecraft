"""Gehöft: Fachwerk-Bauernhaus, Scheune, offene Werkstatt, Weide, Bauerngarten und Hof auf 2 x 2 Chunks.

Lageplan (x nach Osten 0..31, z nach Süden 0..31):
  Bauernhaus  x 2..14,  z 3..11 (Obergeschoss kragt nach Norden und Süden je 1 Block aus)
  Scheune     x 18..28, z 3..15 (First Nord-Süd, Tor im Südgiebel)
  Werkstatt   x 2..10,  z 15..21 (nach Osten und Süden offen, Esse am Westgiebel)
  Weide       x 17..29, z 19..29 (Zaun, Tor im Norden, Unterstand, Tränke)
  Garten      x 2..12,  z 24..29 (Zaun, Blumenbeete, Komposter)
  Hof         Wege aus grober Erde und Bruchstein, Feuerstelle, Hoftor im Süden, Laternenpfähle, Hofbaum
"""
from __future__ import annotations

from farm.blocks import B

from . import kit
from .kit import Bau

SIZE = (32, 20, 32)
FRAME = "dark_oak_log"
FILL = "birch_planks"
ROOF = "brick"  # Ziegeldach


def _fenster(m: Bau, xs, zs, ys) -> None:
    for x in xs:
        for z in zs:
            for y in ys:
                m.put(x, y, z, "glass_pane")


def bauernhaus(m: Bau) -> None:
    x0, x1, z0, z1 = 2, 14, 3, 11
    cobble, mossy, sb = B("cobblestone"), B("mossy_cobblestone"), B("stone_bricks")
    # Sockel, Boden, Erdgeschoss aus Bruchstein mit Ecksteinen
    kit.ring(m, x0, z0, x1, z1, 1, sb)
    kit.flaeche(m, x0 + 1, z0 + 1, x1 - 1, z1 - 1, 1, B("spruce_planks"))
    kit.wand(m, x0, z0, x1, z1, 2, 5, cobble)
    for i, (x, z) in enumerate(((x0, z0), (x1, z0), (x0, z1), (x1, z1))):
        for y in range(2, 6):
            m.set(x, y, z, sb)
    for x, y, z in ((4, 2, z0), (9, 4, z0), (x0, 3, 5), (x1, 2, 8), (6, 5, z1), (12, 2, z1), (x0, 5, 9)):
        m.set(x, y, z, mossy)
    # Decke/Obergeschossboden y6: Balkenkranz, Auskragung nach Norden und Süden (Schwelle + Knaggen)
    kit.flaeche(m, x0 + 1, z0 + 1, x1 - 1, z1 - 1, 6, B("spruce_planks"))
    kit.balkenkranz(m, x0, z0, x1, z1, 6, FRAME)
    for x in range(x0, x1 + 1):  # Schwelle; Enden senkrecht, damit sich die Reihe ohne Hilfsblock ansetzen lässt
        ax = "y" if x in (x0, x1) else "x"
        m.put(x, 6, z0 - 1, FRAME, axis=ax)
        m.put(x, 6, z1 + 1, FRAME, axis=ax)
    for x in (x0, 5, 11, x1):
        m.put(x, 5, z0 - 1, "dark_oak_stairs", facing="south", half="top")
        m.put(x, 5, z1 + 1, "dark_oak_stairs", facing="north", half="top")
    # Obergeschoss y7..9 in Fachwerk (Pfosten alle 3 Blöcke, Gefache aus Birkenbrettern), Rähm y10
    uz0, uz1 = z0 - 1, z1 + 1
    kit.wand(m, x0, uz0, x1, uz1, 7, 9, B(FILL))
    for x in range(x0, x1 + 1, 3):
        kit.pfosten(m, x, uz0, 7, 9, FRAME)
        kit.pfosten(m, x, uz1, 7, 9, FRAME)
    for z in (uz0, 7, uz1):
        kit.pfosten(m, x0, z, 7, 9, FRAME)
        kit.pfosten(m, x1, z, 7, 9, FRAME)
    kit.balkenkranz(m, x0, uz0, x1, uz1, 10, FRAME)
    # Ziegeldach, First in x-Richtung; Giebel in Fachwerk
    kit.satteldach(m, x0 - 1, x1 + 1, uz0 - 1, uz1 + 1, 10, f"{ROOF}_stairs", first=f"{ROOF}_slab",
                   giebel=B(FILL), giebel_x=(x0, x1))
    for x in (x0, x1):
        for y in range(11, 16):
            m.put(x, y, 7, FRAME, axis="y")
    for (px, py, pz), b in list(m.blocks.items()):
        if px in (x0 - 1, x1 + 1) and b.id.startswith(ROOF):
            if b.id.endswith("_stairs"):
                m.put(px, py, pz, "dark_oak_stairs", facing=b.prop("facing"))
            else:
                m.put(px, py, pz, "dark_oak_slab", type="bottom")
    # Fenster
    _fenster(m, (4, 5), (z1,), (3, 4))
    _fenster(m, (11, 12), (z1,), (3, 4))
    _fenster(m, (5, 10), (z0,), (3, 4))
    _fenster(m, (x0,), (6, 7, 8), (3, 4))
    _fenster(m, (x1,), (5, 9), (3, 4))
    _fenster(m, (3, 4, 9, 10), (uz1,), (8,))
    _fenster(m, (6, 7, 12, 13), (uz0,), (8,))
    _fenster(m, (x0, x1), (4, 5, 9, 10), (8,))
    _fenster(m, (x0,), (7,), (12, 13))
    _fenster(m, (x1,), (6, 8), (12,))
    # Haustür unter der Auskragung, Stufe, Laterne
    kit.tuer(m, 8, 2, z1, "spruce", facing="north", hinge="right")
    m.put(8, 1, z1 + 1, "stone_brick_stairs", facing="north")
    kit.haengelaterne(m, 7, 5, z1 + 1)
    kit.haengelaterne(m, 9, 5, z0 - 1)
    # Kamin innen an der Ostwand, durch den First, Lagerfeuer obendrauf
    m.put(13, 2, 7, "campfire", facing="west")
    for z in (6, 8):
        m.set(13, 2, z, sb)
        m.put(13, 3, z, "stone_brick_stairs", facing="east", half="top")
    for y in range(3, 18):
        m.set(13, y, 7, sb if y < 6 else cobble)
    m.put(13, 18, 7, "campfire", facing="south")

    # Erdgeschoss innen: Treppe an der Nordwand nach oben, Küche, Stube
    for i, x in enumerate(range(4, 8)):
        m.put(x, 2 + i, 4, "spruce_stairs", facing="east")
    for x in (5, 6, 7):
        m.clear(x, 6, 4)
        m.put(x, 7, 5, "spruce_fence")
    m.put(4, 7, 5, "spruce_fence")
    m.put(4, 7, 4, "spruce_fence")
    m.put(12, 2, 4, "smoker", facing="south")
    m.put(11, 2, 4, "furnace", facing="south")
    m.put(13, 2, 4, "barrel", facing="up")
    m.put(13, 2, 5, "barrel", facing="west")
    m.put(13, 2, 10, "crafting_table")
    kit.doppelkiste(m, 12, 2, 10, facing="north", richtung="west")
    for z in (6, 7, 8):
        m.put(9, 2, z, "spruce_fence")
        m.put(9, 3, z, "spruce_pressure_plate")
        m.put(8, 2, z, "spruce_stairs", facing="west")
        m.put(10, 2, z, "spruce_stairs", facing="east")
    for x in range(3, 7):
        for z in range(7, 10):
            m.put(x, 2, z, "green_carpet")
    m.put(3, 2, 10, "bookshelf")
    m.put(3, 3, 10, "bookshelf")
    m.put(4, 2, 10, "bookshelf")
    m.put(3, 2, 6, "barrel", facing="east")
    for x, z in ((5, 8), (9, 5), (11, 9)):
        kit.haengelaterne(m, x, 5, z)

    # Obergeschoss: Schlafkammer mit zwei Betten, Kisten, Laternen am Kehlbalken
    kit.bett(m, 4, 7, 8, "red", facing="west")
    kit.bett(m, 4, 7, 10, "red", facing="west")
    m.put(3, 7, 9, "chest", facing="east")
    kit.bett(m, 11, 7, 10, "white", facing="east")
    m.put(12, 7, 9, "chest", facing="west")
    m.put(9, 7, 11, "barrel", facing="north")
    m.put(10, 7, 4, "bookshelf")
    m.put(11, 7, 4, "bookshelf")
    m.put(12, 7, 4, "lectern", facing="south")
    for x in range(6, 10):
        for z in range(7, 10):
            m.put(x, 7, z, "brown_carpet")
    for x in (4, 9):  # Kehlbalken zwischen den Dachflächen
        for z in range(z0 + 1, z1):
            m.put(x, 12, z, FRAME, axis="z")
        kit.haengelaterne(m, x, 11, 7)


def scheune(m: Bau) -> None:
    x0, x1, z0, z1 = 18, 28, 3, 15
    cobble = B("cobblestone")
    kit.ring(m, x0, z0, x1, z1, 1, cobble)
    kit.flaeche(m, x0 + 1, z0 + 1, x1 - 1, z1 - 1, 1, B("coarse_dirt"))
    kit.wand(m, x0, z0, x1, z1, 2, 7, B("spruce_planks"))
    for z in (z0, 7, 11, z1):
        kit.pfosten(m, x0, z, 2, 7, FRAME)
        kit.pfosten(m, x1, z, 2, 7, FRAME)
    for x in (21, 25):
        kit.pfosten(m, x, z1, 2, 7, FRAME)
        kit.pfosten(m, x, z0, 2, 7, FRAME)
    kit.balkenkranz(m, x0, z0, x1, z1, 8, FRAME)
    kit.satteldach(m, x0 - 1, x1 + 1, z0 - 1, z1 + 1, 8, "dark_oak_stairs", first="dark_oak_slab",
                   giebel=B("spruce_planks"), giebel_x=(z0, z1), first_achse="z")
    for (px, py, pz), b in list(m.blocks.items()):
        if pz in (z0 - 1, z1 + 1) and b.id.startswith("dark_oak") and py >= 8 and x0 - 1 <= px <= x1 + 1:
            if b.id.endswith("_stairs"):
                m.put(px, py, pz, "spruce_stairs", facing=b.prop("facing"))
            else:
                m.put(px, py, pz, "spruce_slab", type="bottom")
    # Tor im Südgiebel (3 breit, 4 hoch) mit Sturz, Ladeluke darüber mit Lastbalken und Laterne
    for x in (22, 23, 24):
        for y in range(2, 6):
            m.clear(x, y, z1)
    for x in range(21, 26):
        m.put(x, 6, z1, FRAME, axis="x")
    m.clear(23, 10, z1)
    m.clear(23, 11, z1)
    m.put(23, 12, z1 + 1, FRAME, axis="z")
    kit.haengelaterne(m, 23, 10, z1 + 1, kette=1)
    for x in (21, 25):  # Kragbalken neben dem Tor mit Laterne
        m.put(x, 6, z1 + 1, FRAME, axis="z")
        kit.haengelaterne(m, x, 5, z1 + 1)
    # kleine Tür im Nordgiebel, Fenster
    kit.tuer(m, 23, 2, z0, "spruce", facing="south", hinge="left")
    m.put(23, 5, z0 - 1, FRAME, axis="z")
    kit.haengelaterne(m, 23, 4, z0 - 1)
    _fenster(m, (x0, x1), (5, 9, 13), (5,))
    # innen: Boxen an der Westseite, Heu, Heuboden im Norden mit Leiter
    for z in range(z0 + 1, z1):
        if z not in (6, 10):
            m.put(21, 2, z, "spruce_fence")
    m.put(21, 2, 6, "spruce_fence_gate", facing="east")
    m.put(21, 2, 10, "spruce_fence_gate", facing="east")
    for x in (19, 20):
        m.put(x, 2, 8, "spruce_fence")
        m.put(x, 2, 12, "spruce_fence")
    m.put(19, 2, 4, "composter")
    m.put(19, 2, 9, "cauldron")
    m.put(19, 2, 13, "cauldron")
    for x, z, h in ((27, 13, 2), (27, 14, 3), (26, 14, 2), (27, 12, 1), (26, 13, 1), (25, 14, 1)):
        for y in range(2, 2 + h):
            m.put(x, y, z, "hay_block", axis="y")
    kit.flaeche(m, x0 + 1, z0 + 1, x1 - 1, 7, 8, B("spruce_planks"))
    for y in range(2, 9):
        m.put(24, y, z0 + 1, "ladder", facing="south")
    for x in range(x0 + 1, x1):
        if x != 24:
            m.put(x, 9, 8, "spruce_fence")
    for x, z in ((20, 5), (21, 5), (21, 4), (26, 5), (26, 6), (25, 5), (22, 6)):
        m.put(x, 9, z, "hay_block", axis="y")
    m.put(20, 10, 5, "hay_block", axis="y")
    for z in (11, 14):  # Kehlbalken von Dachfläche zu Dachfläche
        for x in range(20, 27):
            m.put(x, 10, z, FRAME, axis="x")
        kit.haengelaterne(m, 23, 9, z)
    kit.haengelaterne(m, 22, 7, 5)


def werkstatt(m: Bau) -> None:
    x0, x1, z0, z1 = 2, 10, 15, 21
    cobble, sb = B("cobblestone"), B("stone_bricks")
    kit.flaeche(m, x0, z0, x1, z1, 1, sb)
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if (x * 7 + z * 3) % 5 == 0:
                m.set(x, 1, z, cobble)
    # Rückwände (Norden, Westen) aus Bruchstein, Pfosten an der offenen Seite
    for y in range(2, 6):
        for x in range(x0, x1 + 1):
            m.set(x, y, z0, cobble)
        for z in range(z0, z1 + 1):
            m.set(x0, y, z, cobble)
    for x, z in ((x1, z0), (x1, 18), (x1, z1), (6, z1), (x0, z1)):
        kit.pfosten(m, x, z, 2, 5, FRAME)
    kit.balkenkranz(m, x0, z0, x1, z1, 6, FRAME)
    kit.satteldach(m, x0 - 1, x1 + 1, z0 - 1, z1 + 1, 6, "spruce_stairs", first="spruce_slab",
                   giebel=B("spruce_planks"), giebel_x=(x0, x1))
    # Esse am Westgiebel: Kamin durch den First
    for y in range(2, 12):
        m.set(x0, y, 18, cobble)
    m.put(x0, 12, 18, "campfire", facing="east")
    m.put(3, 2, 18, "blast_furnace", facing="east")
    m.put(3, 2, 17, "furnace", facing="east")
    m.put(3, 2, 19, "smoker", facing="east")
    for z in (17, 18, 19):
        m.put(3, 3, z, "stone_brick_stairs", facing="west", half="top")
    m.put(3, 4, 18, "stone_bricks")
    m.put(3, 5, 18, "stone_bricks")
    m.put(4, 2, 16, "smithing_table")
    m.put(5, 2, 16, "stonecutter", facing="south")
    m.put(6, 2, 16, "crafting_table")
    kit.doppelkiste(m, 7, 2, 16, facing="south", richtung="east")
    m.put(9, 2, 16, "cauldron")
    m.put(3, 2, 20, "barrel", facing="up")
    m.put(3, 3, 20, "barrel", facing="up")
    m.put(4, 2, 20, "barrel", facing="east")
    m.put(7, 2, 19, "spruce_log", axis="y")  # Hackklotz
    for x in (4, 8):
        for z in range(z0 + 1, z1):
            m.put(x, 7, z, FRAME, axis="z")
        kit.haengelaterne(m, x, 6, 18)
    # Holzstapel an der Südseite
    for x in (3, 4, 5):
        for y in (2, 3):
            m.put(x, y, z1, "spruce_log", axis="x")


def weide(m: Bau) -> None:
    x0, x1, z0, z1 = 17, 29, 19, 29
    for x in range(x0, x1 + 1):
        m.put(x, 1, z0, "spruce_fence")
        m.put(x, 1, z1, "spruce_fence")
    for z in range(z0, z1 + 1):
        m.put(x0, 1, z, "spruce_fence")
        m.put(x1, 1, z, "spruce_fence")
    m.put(23, 1, z0, "spruce_fence_gate", facing="north")
    for x, z in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
        kit.laternenpfahl(m, x, 2, z, "spruce_fence")
    # Unterstand in der Südostecke: 4 Pfosten, Satteldach
    for x, z in ((25, 25), (27, 25), (25, 27), (27, 27)):
        kit.pfosten(m, x, z, 1, 2, "spruce_log")
    kit.balkenkranz(m, 25, 25, 27, 27, 3, "spruce_log")
    kit.satteldach(m, 24, 28, 24, 28, 3, "spruce_stairs", first="spruce_slab", giebel=B("spruce_planks"),
                   giebel_x=(25, 27))
    for x, z in ((26, 26), (26, 27), (25, 26)):
        m.put(x, 1, z, "hay_block", axis="y")
    m.put(26, 2, 26, "hay_block", axis="y")
    kit.haengelaterne(m, 26, 4, 26)
    m.put(18, 1, 20, "cauldron")
    m.put(19, 1, 20, "cauldron")
    m.put(18, 1, 28, "hay_block", axis="y")
    m.put(18, 2, 28, "hay_block", axis="y")
    m.put(19, 1, 28, "hay_block", axis="y")


def garten(m: Bau) -> None:
    x0, x1, z0, z1 = 2, 12, 24, 29
    for x in range(x0, x1 + 1):
        m.put(x, 1, z0, "spruce_fence")
        m.put(x, 1, z1, "spruce_fence")
    for z in range(z0, z1 + 1):
        m.put(x0, 1, z, "spruce_fence")
        m.put(x1, 1, z, "spruce_fence")
    m.put(7, 1, z0, "spruce_fence_gate", facing="north")
    for x, z in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
        m.put(x, 2, z, "lantern")
    beds = ("poppy", "dandelion", "cornflower", "oxeye_daisy", "allium", "azure_bluet", "red_tulip", "orange_tulip",
            "white_tulip")
    for i, x in enumerate(range(x0 + 1, x1)):
        m.put(x, 1, 26, beds[i % len(beds)])
        m.put(x, 1, 28, beds[(i + 4) % len(beds)])
    for x in range(x0 + 1, x1):
        m.put(x, 0, 27, "coarse_dirt")
        if x != 7:
            m.put(x, 0, 25, "coarse_dirt")
    m.put(11, 1, 25, "composter")
    m.put(3, 1, 25, "composter")
    m.put(7, 0, 25, "coarse_dirt")


def hof(m: Bau) -> None:
    # Wege (Ebene 0: ersetzt das Gras)
    path = set()
    for z in range(13, 32):  # Hauptweg vom Hoftor nach Norden, 2 breit
        path |= {(14, z), (15, z)}
    for x in range(8, 16):  # zur Haustür
        path.add((x, 13))
    for x in range(15, 24):  # zum Scheunentor und Weidetor
        path |= {(x, 17), (x, 18)}
    for z in range(16, 19):
        path |= {(22, z), (23, z), (24, z)}
    for x in range(11, 15):
        path.add((x, 18))
    for z in range(22, 24):
        path |= {(7, z), (8, z)}
    for x in range(7, 15):
        path.add((x, 22))
    for (x, z) in path:
        kind = "cobblestone" if (x * 5 + z * 3) % 7 == 0 else ("mossy_cobblestone" if (x + z * 2) % 11 == 0 else "coarse_dirt")
        m.put(x, 0, z, kind)
    # Hoftor im Süden
    for x in (13, 17):
        kit.pfosten(m, x, 30, 1, 5, FRAME)
    for x in (12, 14, 15, 16, 18):
        m.put(x, 5, 30, FRAME, axis="x")
    for x in (14, 16):
        kit.haengelaterne(m, x, 4, 30)
    for x in (11, 12, 18, 19):
        m.put(x, 1, 30, "spruce_fence")
    # Laternenpfähle
    for x, z in ((16, 13), (12, 19), (16, 24), (20, 16), (11, 13)):
        kit.laternenpfahl(m, x, 1, z, "spruce_fence")
    # Hofbaum (Eiche) zwischen Garten und Weg: Stamm 5 hoch, runde Krone
    tx, tz = 13, 26
    for y in range(1, 6):
        m.put(tx, y, tz, "oak_log", axis="y")
    for y, r in ((3, 1), (4, 2), (5, 2), (6, 1), (7, 0)):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if r == 2 and abs(dx) == 2 and abs(dz) == 2:
                    continue  # Ecken weglassen
                p = (tx + dx, y, tz + dz)
                if m.get(*p).id == "air":
                    m.put(*p, "oak_leaves")
    # Büsche und Blumen
    kit.busch(m, [(1, 1, 12), (1, 1, 11), (1, 2, 12), (15, 1, 2), (16, 1, 2), (16, 1, 3), (30, 1, 4), (30, 1, 5),
                  (30, 2, 5), (30, 1, 14), (30, 1, 15)], "oak_leaves")
    kit.busch(m, [(1, 1, 2), (1, 2, 2), (2, 1, 1), (17, 1, 16), (29, 1, 16)], "spruce_leaves")
    for x, z, f in ((5, 13, "poppy"), (6, 13, "dandelion"), (11, 12, "cornflower"), (3, 13, "allium"),
                    (18, 17, "oxeye_daisy"), (28, 17, "poppy"), (27, 17, "azure_bluet"), (12, 31, "dandelion"),
                    (18, 31, "poppy")):
        if m.get(x, 1, z).id == "air":
            m.put(x, 1, z, f)


def feuerstelle(m: Bau) -> None:
    cx, cz = 12, 16
    m.put(cx, 0, cz, "cobblestone")
    m.put(cx, 1, cz, "campfire", facing="south")
    for x, z in ((cx - 1, cz), (cx + 1, cz), (cx, cz - 1), (cx, cz + 1)):
        m.put(x, 0, z, "cobblestone")
    for x, z in ((cx - 2, cz), (cx + 2, cz), (cx, cz - 2)):  # Baumstumpf-Hocker
        m.put(x, 1, z, "spruce_log", axis="y")


def build() -> Bau:
    m = Bau("gehoeft", "Gehöft", SIZE,
            "Rustikales Gehöft auf 2x2 Chunks: Fachwerk-Bauernhaus, Scheune, Werkstatt, Weide, Garten und Hof")
    bauernhaus(m)
    scheune(m)
    werkstatt(m)
    weide(m)
    garten(m)
    hof(m)
    feuerstelle(m)
    return m
