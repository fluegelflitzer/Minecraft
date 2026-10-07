"""Blockmodell der Weizenfarm mit Bauern-Dorfbewohnern – 31 x 31 Blöcke (passt in 2x2 Chunks), 5 hoch (4 + Blitzableiter).

Prinzip (Idee aus dem Video „WEIZEN FARM“ von ErikOnHisPeriod, Design Qix; Mechanik am Code von 26.3 geprüft):
- 4 Glasmodule (je 14 x 14 Acker), in jedem genau 1 Bauer mit Kompostierer (Laterne: Kompostierer +
  Leuchtstein). Er erntet reifen Weizen, pflanzt nach und backt am Kompostierer Brot
  (3 Weizen -> 1 Brot, solange er höchstens 36 Brot trägt).
- Die Bauern sehen einander nicht (Glaswände). Sonst würden sie ständig versuchen, sich zu vermehren,
  und dabei jedes Mal je 3 Brot essen (ohne Betten scheitert die Vermehrung).
- In jedem Modul sitzt ein „Sammler“ (beliebiger Dorfbewohner ohne Beruf) in einer Zelle an der
  Außenwand. Trifft der Bauer ihn (Abstand höchstens ~2,2 Blöcke, freie Sicht), wirft er ihm alles
  Brot über 24 Stück und die Hälfte seines Weizens ab 33 Stück zu.
- Bauer und Sammler trennt ein Trichter in Feldhöhe, darüber ein Sichtschlitz unter dem Glasdach:
  Durch den Schlitz sehen sie sich, aber kein Dorfbewohner passt hindurch (nur 1 Block hoch).
  Die Würfe landen auf dem Trichter, der sie (vor Ablauf der 10-Tick-Aufhebesperre) einsaugt und
  über einen zweiten Trichter in die Kiste unter dem Sammler gibt. Die Kiste öffnet man von außen.

Koordinaten: x = Ost (0..30), y = Höhe, z = Süd (0..30).
  y0 Ackerboden (auf Bodenhöhe), Wasserstufen, Kiste, Trichter | y1 Weizen, Kompostierer, Schlitz-Trichter
  y2 Leuchtstein, Sichtschlitz | y3 Glasdach | y4 Blitzableiter (Mitte)
Das Modul Nordwest wird gebaut, die anderen drei sind Spiegelungen davon.
"""
from __future__ import annotations

from farm.blocks import AIR, B
from farm.model import Model, _neighbor

N = 31
SIZE = (N, 5, N)
Y_FIELD, Y_CROP, Y_LAMP, Y_ROOF, Y_ROD = 0, 1, 2, 3, 4
MID = N // 2  # Trennwände zwischen den Modulen bei x = 15 und z = 15

GLASS = B("glass")
DIRT = B("dirt")
COBBLE = B("cobblestone")
FARMLAND = B("farmland", moisture=7)
WATER_SLAB = B("cobblestone_slab", type="top", waterlogged=True)

# Modul Nordwest (Acker x 1..14, z 1..14); die anderen Module entstehen durch Spiegelung
LAMP = (7, 7)  # Kompostierer (Arbeitsplatz des Bauern)
WATER = [(4, 4), (4, 11), (11, 4), (11, 11)]  # wassergefüllte Stufen: jeder Acker höchstens 4 Blöcke entfernt
CELL = (7, 1)  # Sammler-Zelle an der Nordwand (Kiste darunter)
GATE = (0, 9)  # Zauntor in der Westwand

MIRRORS = {"nw": (False, False), "ne": (True, False), "sw": (False, True), "se": (True, True)}
FLIP_X = {"east": "west", "west": "east"}
FLIP_Z = {"north": "south", "south": "north"}


class Module:
    """Schreibt das Nordwest-Modul gespiegelt in das Modell."""

    def __init__(self, m: Model, name: str):
        self.m, self.name = m, name
        self.fx, self.fz = MIRRORS[name]

    def pos(self, x, z):
        return (N - 1 - x if self.fx else x), (N - 1 - z if self.fz else z)

    def face(self, d: str) -> str:
        if self.fx:
            d = FLIP_X.get(d, d)
        if self.fz:
            d = FLIP_Z.get(d, d)
        return d

    def set(self, x, y, z, block):
        if "facing" in dict(block.props):
            block = block.with_props(facing=self.face(block.prop("facing")))
        px, pz = self.pos(x, z)
        self.m.set(px, y, pz, block)

    def note(self, key, x, y, z):
        px, pz = self.pos(x, z)
        self.m.note(key, (px, y, pz))


def build() -> Model:
    m = Model(*SIZE)
    for x in range(N):
        for z in range(N):
            wall = x in (0, N - 1, MID) or z in (0, N - 1, MID)
            m.set(x, Y_ROOF, z, GLASS)
            for y in (Y_FIELD, Y_CROP, Y_LAMP):
                if wall:
                    m.set(x, y, z, GLASS)
            if not wall:
                m.set(x, Y_FIELD, z, FARMLAND)
    for name in MIRRORS:
        module(Module(m, name))
    # Blitzableiter: lenkt Blitze im Umkreis von 128 Blöcken auf sich (sonst würden getroffene Dorfbewohner zu Hexen)
    m.set(MID, Y_ROD, MID, B("lightning_rod", facing="up"))
    finalize(m)
    return m


def module(h: Module) -> None:
    for x, z in WATER:
        h.set(x, Y_FIELD, z, WATER_SLAB)
    lx, lz = LAMP
    h.set(lx, Y_FIELD, lz, COBBLE)
    h.set(lx, Y_CROP, lz, B("composter"))
    h.set(lx, Y_LAMP, lz, B("glowstone"))
    h.note("lamp", lx, Y_CROP, lz)
    collector(h)
    gx, gz = GATE
    h.set(gx, Y_CROP, gz, B("oak_fence_gate", facing="east"))
    h.set(gx, Y_LAMP, gz, AIR)


def collector(h: Module) -> None:
    """Sammler-Zelle an der Nordwand.

    Schnitt (Blick von Osten, z nach rechts):        Draufsicht y2 / y3 (x nach rechts):
        y3  Dach  Dach  Dach  Dach                          x: 6 7 8
        y2  Glas  Samm. Schlitz .     <- Sichtlinie     z1    G S G    (y1 und y2; S = Sammler)
        y1  Glas  Samm. Trichter Bauer                  z2    G T G    (y1; darüber y2 frei)
        y0  Loch  Kiste <-Trichter Acker                z3    . B .    (B = Standplatz des Bauern)
            z0    z1    z2       z3
    """
    cx, cz = CELL
    h.set(cx, Y_FIELD, cz, B("chest", facing="north"))  # Boden der Zelle, von außen durch das Wandloch zu öffnen
    h.set(cx, Y_FIELD, cz - 1, AIR)  # Loch in der Außenwand vor der Kiste
    h.set(cx, Y_FIELD, cz + 1, B("hopper", facing="north"))  # -> Kiste
    h.set(cx, Y_CROP, cz + 1, B("hopper", facing="down"))  # Schlitz-Trichter (fängt die Würfe)
    for x in (cx - 1, cx + 1):
        for z in (cz, cz + 1):
            h.set(x, Y_FIELD, z, DIRT)
            h.set(x, Y_CROP, z, GLASS)
        h.set(x, Y_LAMP, cz, GLASS)  # Zellenwand neben dem Sammler; vor der Zelle (z2) bleibt y3 frei
    h.note("cell", cx, Y_CROP, cz)
    h.note("chest", cx, Y_FIELD, cz)


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
