"""Starterhütte „Fichtenkate“: kleine Hütte aus Fichte und Bruchstein mit Kaminfeuer.

Haus 7 x 7 (x 2..8, z 2..8), Satteldach mit First in Ost-West-Richtung, Kamin an der Ostgiebelwand.
Innen: Bett, Werkbank, Ofen, Räucherofen, Doppelkiste, Fass, Teppich, Hängelaterne.
"""
from __future__ import annotations

from farm.blocks import B

from . import kit
from .kit import Bau

SIZE = (12, 12, 13)


PAL = {"log": "spruce_log", "wand": "oak_planks", "giebel": "spruce_planks", "dach": "spruce",
       "boden": "spruce_planks", "rand": "cobblestone", "sims": "spruce_trapdoor"}


def build(pal: dict | None = None) -> Bau:
    pal = {**PAL, **(pal or {})}
    m = Bau("starterhuette", "Fichtenkate (Starterhütte)", SIZE,
            "Kleine rustikale Starterhütte aus Fichte, Eiche und Bruchstein, 7x7, mit Kamin und Fensterbänken")
    log, planks = pal["log"], B(pal["wand"])
    cobble = B("cobblestone")
    x0, z0, x1, z1 = 2, 2, 8, 8

    # Sockel (y1) aus Bruchstein, Boden aus Fichtenbrettern
    kit.ring(m, x0, z0, x1, z1, 1, cobble)
    kit.flaeche(m, x0 + 1, z0 + 1, x1 - 1, z1 - 1, 1, B(pal["boden"]))
    for x, z in ((2, 4), (8, 7), (5, 2)):
        m.put(x, 1, z, "mossy_cobblestone")

    # Wände y2..4: Fichtenbretter, Eckpfosten und Mittelpfosten aus Fichtenstämmen
    kit.wand(m, x0, z0, x1, z1, 2, 4, planks)
    for x, z in ((x0, z0), (x1, z0), (x0, z1), (x1, z1), (x0, 5), (x1, 5)):
        kit.pfosten(m, x, z, 2, 4, log)
    # Balkenkranz y5
    kit.balkenkranz(m, x0, z0, x1, z1, 5, log)

    # Satteldach (Fichtentreppen), First als Stufe, Giebel aus Fichtenbrettern
    kit.satteldach(m, x0 - 1, x1 + 1, z0 - 1, z1 + 1, 5, pal["dach"] + "_stairs", first=pal["dach"] + "_slab",
                   giebel=B(pal["giebel"]), giebel_x=(x0, x1))
    if pal["rand"]:  # Ortgang (Dachkante an den Giebeln) in anderer Farbe
        for x in (x0 - 1, x1 + 1):
            for (px, py, pz), b in list(m.blocks.items()):
                if px == x and b.id.endswith(("_stairs", "_slab")) and py >= 5:
                    m.put(px, py, pz, pal["rand"] + ("_stairs" if b.id.endswith("_stairs") else "_slab"),
                          **{k: v for k, v in b.props if k in ("facing", "half", "type")})
    # Giebelfenster
    m.put(x0, 7, 5, "glass_pane")
    # Fenster
    for x, y, z, aussen in ((3, 3, z1, "south"), (7, 3, z1, "south"), (x0, 3, 4, "west"), (x0, 3, 6, "west"),
                            (4, 3, z0, "north"), (6, 3, z0, "north")):
        m.put(x, y, z, "glass_pane")
        # Fensterbank: geschlossene Falltür (obere Hälfte) außen unter dem Fenster
        sx, sy, sz = kit.step((x, y - 1, z), aussen)
        if m.get(sx, sy, sz).id == "air":
            m.put(sx, sy, sz, pal["sims"], facing=aussen, half="top")
    # Tür (Süden, Mitte), Stufe davor, Laterne unter dem Dachüberstand
    kit.tuer(m, 5, 2, z1, "spruce", facing="north", hinge="left")
    m.put(5, 1, z1 + 1, "cobblestone_stairs", facing="north")
    kit.haengelaterne(m, 5, 4, z1 + 1)

    # Kamin an der Ostgiebelwand (außen): unten 3 breit, oben 1 breit, Lagerfeuer obendrauf
    cx = x1 + 1
    for z in (4, 5, 6):
        for y in range(1, 4):
            m.set(cx, y, z, cobble)
    m.put(cx, 4, 4, "cobblestone_stairs", facing="south")
    m.put(cx, 4, 6, "cobblestone_stairs", facing="north")
    for y in range(4, 10):
        m.set(cx, y, 5, cobble)
    m.put(cx, 10, 5, "campfire", facing="south")

    # Innen (Boden y1, Möbel y2)
    kit.bett(m, 3, 2, 4, "red", facing="north")
    m.put(4, 2, 3, "crafting_table")
    m.put(7, 2, 5, "furnace", facing="west")
    m.put(7, 2, 6, "smoker", facing="west")
    m.put(7, 2, 3, "barrel", facing="up")
    kit.doppelkiste(m, 3, 2, 6, facing="east", richtung="south")
    for x in range(4, 7):
        for z in range(4, 7):
            m.put(x, 2, z, "brown_carpet")
    kit.haengelaterne(m, 5, 6, 5, kette=2)

    # Draußen: Weg, Büsche, Blumen
    for z in (z1 + 2, z1 + 3, z1 + 4):
        m.put(5, 0, z, "coarse_dirt")
    m.put(4, 0, z1 + 3, "coarse_dirt")
    m.put(6, 0, z1 + 4, "coarse_dirt")
    kit.busch(m, [(1, 1, 8), (1, 1, 7), (1, 2, 8), (9, 1, 8), (10, 1, 8)], "oak_leaves")
    kit.busch(m, [(1, 1, 1), (2, 1, 1), (1, 2, 1)], "spruce_leaves")
    for x, z, f in ((3, 10, "poppy"), (7, 10, "dandelion"), (8, 10, "poppy"), (2, 10, "cornflower"),
                    (10, 7, "oxeye_daisy")):
        m.put(x, 1, z, f)
    return m
