"""Blockmodell der Weizenfarm-Hochhaus – 32 x 16 Blöcke (2 x 1 Chunks), 23 hoch, 7 Etagen, 14 Bauern.

Prinzip (Idee aus dem Video „WEIZEN FARM“ von ErikOnHisPeriod, Design Qix; Mechanik am Code von 26.3 geprüft
und im Spiel getestet):
- Jede Etage hat 2 Module (je 14 x 13 Acker), in jedem genau 1 Bauer mit Kompostierer (Laterne:
  Bruchstein + Kompostierer + Kürbislaterne). Er erntet reifen Weizen, pflanzt nach und backt am
  Kompostierer Brot (3 Weizen -> 1 Brot, solange er höchstens 36 Brot trägt).
- 1 „Sammler“ (beliebiger Dorfbewohner) pro Etage sitzt in einer Zelle mitten in der Trennwand. Trifft ein
  Bauer ihn (Abstand höchstens ~2,2 Blöcke, freie Sicht), wirft er ihm alles Brot über 24 Stück und die
  Hälfte seines Weizens ab 33 Stück zu.
- Bauer und Sammler trennt ein Trichter in Feldhöhe, darüber ein Sichtschlitz unter der Decke: Durch den
  Schlitz sehen sie sich, aber kein Dorfbewohner passt hindurch (nur 1 Block hoch). Die Würfe landen auf
  dem Trichter, der sie vor Ablauf der 10-Tick-Aufhebesperre einsaugt.
- Die beiden Bauern einer Etage sehen sich durch die Schlitze, kommen sich aber nie näher als 3,6 Blöcke.
  Vermehrungsversuche brechen deshalb ab, bevor jemand Brot isst (das passiert erst bei <= 2,24 Blöcken).
  Etagen sind durch massive Decken getrennt.
- Alle Trichter speisen ein senkrechtes Trichterrohr in der Trennwand; es endet im Erdgeschoss in einer
  Doppelkiste, die man von beiden Modulen aus öffnet.
- Ohne Himmelslicht: Kürbislaternen im Boden sorgen für Licht >= 9 auf jedem Feld.
- Der Acker einer Etage ist zugleich die Decke der Etage darunter.
- Südseite: 1 Block breiter Balkon mit Leiter, von dem aus jedes Modul durch ein Zauntor erreichbar ist.
- Wände und Dach aus Bruchtiefenschiefer.

Koordinaten: x = Ost (0..31), y = Höhe (0..22), z = Süd (0..15).
  Etage k (0..6): y = 3k Ackerboden | 3k+1 Weizen, Kompostierer, Schlitz-Trichter, Tor
                  3k+2 Kürbislaterne über dem Kompostierer, Sichtschlitz | 3k+3 Decke = Acker der Etage darüber
  y21 Dach | y22 Blitzableiter
Das Westmodul wird gebaut, das Ostmodul ist seine Spiegelung (x -> 31 - x).
"""
from __future__ import annotations

from farm.blocks import AIR, B
from farm.model import Model, _neighbor

NX, NZ = 32, 16
FLOORS, FLOOR_H = 7, 3
Y_ROOF = FLOORS * FLOOR_H  # 21
Y_ROD = Y_ROOF + 1  # 22
SIZE = (NX, Y_ROD + 1, NZ)

WALL_X = (0, 15)  # Westmodul: Außenwand x0, Trennwand x15 (Ostmodul gespiegelt: x31, x16)
WALL_Z = (0, 14)  # Nordwand, Balkonwand
BALCONY_Z = 15
LADDER_X = 0  # Leiter am Westende des Balkons

WALL = B("cobbled_deepslate")
GLASS = B("glass")  # nur über der Zentralkiste: ein voller Block darüber würde sie nicht öffnen lassen
DIRT = B("dirt")
COBBLE = B("cobblestone")
FARMLAND = B("farmland", moisture=7)
# Untere Stufe mit Wasser: ihr Boden ist dicht. Eine obere Stufe würde nach unten in die Etage darunter auslaufen.
WATER_SLAB = B("cobblestone_slab", type="bottom", waterlogged=True)
PLATFORM = B("cobblestone_slab", type="top")
LIGHT = B("jack_o_lantern", facing="south")

# Westmodul (Acker x 1..14, z 1..13); Ostmodul gespiegelt (Acker x 17..30)
LAMP_W, LAMP_E = (8, 7), (22, 7)  # Kompostierer: beide 7 Blöcke vom Sammler entfernt, genau vor seinem Fenster
WATER = [(4, 4), (11, 4), (4, 10), (11, 10)]  # Wasserstufen (untere Hälfte): jeder Acker höchstens 4 Blöcke entfernt
# Kürbislaternen im Acker: zusammen mit der Laterne über dem Kompostierer Licht >= 9 auf jedem Feld
LIGHTS_W = [(3, 5), (9, 11), (11, 2), (1, 12), (13, 9), (1, 1)]
LIGHTS_E = [(28, 5), (23, 11), (20, 2), (30, 12), (18, 9), (30, 1)]
BALCONY_LIGHTS = (8, 23)  # Kürbislaternen im Balkonboden: dort spawnen nachts keine Monster
CELL = (15, 7)  # Sammler-Zelle mittig in der Trennwand, zwischen beiden Modulen
PIPE = (15, 8)  # senkrechtes Trichterrohr direkt neben der Zelle
CHEST = [(15, 9), (16, 9)]  # Zentralkiste (Doppelkiste) im Erdgeschoss, in der Trennwand
GATE_X = 12  # Zauntor in der Balkonwand

FLIP = {"east": "west", "west": "east"}


def floor_y(k: int) -> int:
    return k * FLOOR_H


class Half:
    """Schreibt das Westmodul, gespiegelt (x -> 31 - x) für das Ostmodul."""

    def __init__(self, m: Model, east: bool):
        self.m, self.east = m, east

    def x(self, x: int) -> int:
        return NX - 1 - x if self.east else x

    def set(self, x, y, z, block):
        if self.east and "facing" in dict(block.props):
            block = block.with_props(facing=FLIP.get(block.prop("facing"), block.prop("facing")))
        self.m.set(self.x(x), y, z, block)


def build() -> Model:
    m = Model(*SIZE)
    for k in range(FLOORS):
        for east in (False, True):
            module(Half(m, east), floor_y(k), LAMP_E if east else LAMP_W, LIGHTS_E if east else LIGHTS_W)
        collector(m, floor_y(k))
        balcony(m, floor_y(k))
    for x in range(NX):
        for z in range(NZ):
            m.set(x, Y_ROOF, z, WALL)
    for y in range(1, floor_y(FLOORS - 1) + 2):
        m.set(LADDER_X, y, BALCONY_Z, B("ladder", facing="south"))
    central_chest(m)
    # Blitzableiter: lenkt Blitze im Umkreis von 128 Blöcken auf sich (getroffene Dorfbewohner würden zu Hexen)
    m.set(15, Y_ROD, 7, B("lightning_rod", facing="up"))
    finalize(m)
    return m


def module(h: Half, f: int, lamp, lights) -> None:
    crop, slit = f + 1, f + 2
    for x in range(WALL_X[0], WALL_X[1] + 1):
        for z in range(WALL_Z[0], WALL_Z[1] + 1):
            wall = x in WALL_X or z in WALL_Z
            for y in (f, crop, slit):
                if wall:
                    h.set(x, y, z, WALL)
            if not wall:
                h.set(x, f, z, FARMLAND)
    for x, z in WATER:
        h.set(x, f, z, WATER_SLAB)
    for x, z in lights:
        h.m.set(x, f, z, LIGHT)  # absolute Koordinaten (West und Ost getrennt berechnet)
    lx, lz = lamp
    h.m.set(lx, f, lz, COBBLE)
    h.m.set(lx, crop, lz, B("composter"))
    h.m.set(lx, slit, lz, LIGHT)
    h.m.note("lamp", (lx, crop, lz))
    # Eingang vom Balkon: Zauntor, darüber frei (Kopfhöhe für dich; Dorfbewohner kommen nicht über das Tor)
    h.set(GATE_X, crop, WALL_Z[1], B("oak_fence_gate", facing="south"))
    h.set(GATE_X, slit, WALL_Z[1], AIR)


def collector(m: Model, f: int) -> None:
    """Sammler-Zelle mittig in der Trennwand: 1 Sammler für beide Bauern der Etage.

    Draufsicht (x nach rechts, z nach unten), Ebene f+1 / f+2:
         x: 13 14 15 16 17
      z6     .  W  W  W  .      W Bruchtiefenschiefer (in f+2 nur bei x15, sonst Sichtschlitz)
      z7     B  T  S  T  B      S Sammler, T Schlitz-Trichter, B Standplatz der Bauern (West / Ost)
      z8     .  U  R  U  .      U Trichter ins Rohr R (darüber Sichtschlitz), R Trichterrohr nach unten
    Die Bauern sehen den Sammler (und einander) durch die Schlitze in Augenhöhe, kommen aber nie näher
    als 3,6 Blöcke zueinander. Die Würfe landen auf den Trichtern T oder U.
    """
    cx, cz = CELL
    px, pz = PIPE
    crop, slit = f + 1, f + 2
    m.set(cx, f, cz, DIRT)  # Boden der Zelle
    for x in (cx - 1, cx + 1):  # Westseite x14 (im Westmodul), Ostseite x16 (in der Trennwand)
        toward = "east" if x < cx else "west"
        for z in (cz - 1, cz, cz + 1):
            m.set(x, f, z, DIRT)
            m.set(x, slit, z, AIR)  # Sichtschlitz, 3 breit
        m.set(x, crop, cz, B("hopper", facing="south"))  # Schlitz-Trichter -> Trichter daneben
        m.set(x, crop, cz + 1, B("hopper", facing=toward))  # -> Trichterrohr
        m.set(x, crop, cz - 1, WALL)
    m.set(cx, crop, cz - 1, WALL)
    m.set(cx, slit, cz - 1, WALL)
    m.set(cx, crop, cz, AIR)
    m.set(cx, slit, cz, AIR)
    for y in (f, crop, slit):  # Trichterrohr: senkrecht durch alle Etagen nach unten
        m.set(px, y, pz, B("hopper", facing="down"))
    m.note("cell", (cx, crop, cz))


def central_chest(m: Model) -> None:
    """Unteres Rohrende (Erdgeschoss, Feldhöhe+1) gibt seitlich in die Doppelkiste in der Trennwand."""
    px, pz = PIPE
    m.set(px, 0, pz, WALL)  # unter dem Rohr: Rohr endet eine Ebene höher
    m.set(px, 1, pz, B("hopper", facing="south"))
    for x, z in CHEST:
        m.set(x, 1, z, B("chest", facing="south"))
        m.set(x, 2, z, GLASS)  # über einer Kiste darf kein voller Block liegen, sonst geht sie nicht auf
        m.note("chest", (x, 1, z))


def balcony(m: Model, f: int) -> None:
    """Balkon (z15) auf Höhe der Etage: Laufplatte, oben 1 Block über dem Etagenboden."""
    for x in range(NX):
        if x != LADDER_X:
            m.set(x, f, BALCONY_Z, LIGHT if x in BALCONY_LIGHTS else PLATFORM)


def finalize(m: Model) -> None:
    from farm.blocks import OPPOSITE
    for pos, block in list(m.blocks.items()):
        if block.id == "chest":
            facing = block.prop("facing")
            cw = {"north": "east", "east": "south", "south": "west", "west": "north"}[facing]
            kind = "single"
            for d, t in ((cw, "left"), (OPPOSITE[cw], "right")):
                nb = _neighbor(m, pos, d)
                if nb.id == "chest" and nb.prop("facing") == facing:
                    kind = t
            m.blocks[pos] = block.with_props(type=kind)
