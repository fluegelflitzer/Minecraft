"""Blockmodell der Brat-Tierfarm XL (Huhn, Kuh, Schwein) – 16 x 32 Blöcke (1x2 Chunks).

Koordinaten: x = Ost (0..15), y = Höhe (0 = Kisten auf dem Boden), z = Süd (0..31).

Höhen der Kuh-/Schwein-Sektionen:
  y0 Kisten | y1 Trichter / Strom-Boden | y2 Tötungsstrom (Wasser) + Lavazelle (Mauer bzw. Lesepult)
  y3 Lava über der Tötungszelle | y5 Unterbau | y6 Aufzuchtbecken | y7 Wasserklinge
  y8 Beckendecke | y9 Zuchtgänge: Boden aus offenen Falltüren | y10-11 Zuchtgänge (Wände:
  Vollblock + Stufe = 1,5 hoch) | y10 Futtergang/Laufsteg-Boden (Spieler steht 1 Block höher
  als die Tiere und füttert über die Stufe)
"""
from __future__ import annotations

from .blocks import AIR, B, DIRS, MIRROR_X, OPPOSITE, Block

SIZE_X, SIZE_Y, SIZE_Z = 16, 13, 32

# Höhen
Y_CHEST, Y_HOPPER, Y_STREAM, Y_LAVA = 0, 1, 2, 3
Y_SUPPORT, Y_GROW, Y_BLADE, Y_CEIL, Y_GRID, Y_PEN, Y_DECK = 5, 6, 7, 8, 9, 10, 10

COBBLE = B("cobblestone")
GLASS = B("glass")
WALL = B("cobblestone_wall")
SLAB_FLOOR = B("cobblestone_slab", type="bottom")
LAVA = B("lava", level=0)
WATER = B("water", level=0)

# Sektionen (Nord-Wandreihe Z0)
COW_Z0 = 0
PIG_Z0 = 10
CHICKEN_Z = 26  # Reihe der Kükenzellen
CORRIDORS = (1, 7)  # Zuchtgänge (z-Versatz zu Z0), beide an einer Außenwand; Futterdeck Z0+3..Z0+5
SLAB = B("cobblestone_slab", type="bottom")


class Model:
    def __init__(self, sx=SIZE_X, sy=SIZE_Y, sz=SIZE_Z):
        self.size = (sx, sy, sz)
        self.blocks: dict[tuple[int, int, int], Block] = {}
        self.notes: dict[str, list[tuple[int, int, int]]] = {}  # benannte Positionen (für Tests/Checks)

    def inside(self, x, y, z) -> bool:
        sx, sy, sz = self.size
        return 0 <= x < sx and 0 <= y < sy and 0 <= z < sz

    def set(self, x, y, z, block: Block) -> None:
        if not self.inside(x, y, z):
            raise ValueError(f"Block außerhalb des Modells: {(x, y, z)} {block}")
        if block == AIR:
            self.blocks.pop((x, y, z), None)
        else:
            self.blocks[(x, y, z)] = block

    def get(self, x, y, z) -> Block:
        return self.blocks.get((x, y, z), AIR)

    def fill(self, x1, y1, z1, x2, y2, z2, block: Block) -> None:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, block)

    def note(self, key: str, pos) -> None:
        self.notes.setdefault(key, []).append(tuple(pos))


class Half:
    """Schreibt in das Modell, optional an der Mittelachse gespiegelt (x -> 15 - x, Ost <-> West)."""

    def __init__(self, model: Model, mirror: bool):
        self.m = model
        self.mirror = mirror

    def x(self, x: int) -> int:
        return SIZE_X - 1 - x if self.mirror else x

    def blk(self, block: Block) -> Block:
        if not self.mirror:
            return block
        props = dict(block.props)
        if props.get("facing") in MIRROR_X:
            block = block.with_props(facing=MIRROR_X[props["facing"]])
        return block

    def d(self, direction: str) -> str:
        return MIRROR_X.get(direction, direction) if self.mirror else direction

    def set(self, x, y, z, block: Block) -> None:
        self.m.set(self.x(x), y, z, self.blk(block))

    def fill(self, x1, y1, z1, x2, y2, z2, block: Block) -> None:
        self.m.fill(self.x(x1), y1, z1, self.x(x2), y2, z2, self.blk(block))

    def note(self, key: str, x, y, z) -> None:
        self.m.note(key, (self.x(x), y, z))


# --------------------------------------------------------------------------- Kuh / Schwein

def breeding_half(h: Half, z0: int, species: str) -> None:
    """Eine Gehegehälfte (Westseite, gespiegelt = Ostseite).

    Zwei Zuchtgänge (z0+1 und z0+7, x1..5, je 1 Block breit zwischen Vollblöcken): Boden aus offenen
    Falltüren (Spalt 13/16). Erwachsene (0,9) stehen auf der Klappe, ein Baby (0,45) entsteht mittig
    über dem Spalt und fällt durch einen Falltür-Streifen trocken ins Aufzuchtbecken (y6). Die Klappen
    der Fallstreifen liegen an der Außenwand: wird ein Tier erwachsen, schiebt das Spiel es von der
    Klappe weg in die Nachbarzeile – dort erfasst es die Wasserklinge (y7, fließt nach Osten) und schiebt
    es in den Graben (x6) -> Tötungsstrom (y2) -> Lavazelle -> 2 Trichter -> Doppelkiste.
    """
    zn, zs = z0, z0 + 8  # Nord-/Südwand
    zk = z0 + 9  # Lavazelle
    grid = B("oak_trapdoor", facing="south", half="bottom", open=True)  # Klappe an der Nordkante
    c1, c2 = (zn + c for c in CORRIDORS)

    # --- Unterbau und Aufzuchtbecken (y5..y8)
    # Alle Böden einer Tierart liegen auf gleicher Höhe (Kuh 6,0 / Schwein 6,5), damit das Spiel ein
    # wachsendes Tier seitlich aus dem Fallstreifen schieben kann.
    #   Kuh:     Stein (y5) + Standschild (y6, hält das Wasser, keine Kollision)
    #   Schwein: Stufe (y6); im Fallstreifen Mauer-Grat (y5, Oberkante 6,5)
    # Fallstreifen: offene Falltür an der Wand (y6) = Sperre, damit kein Baby unter die Klappe rutscht;
    # darüber ein Wandschild (y7, trocken, wasserdicht).
    h.fill(0, Y_SUPPORT, zn, 5, Y_SUPPORT, zs, COBBLE)
    h.fill(0, Y_GROW, zn, 0, Y_BLADE, zs, COBBLE)  # Westwand
    h.fill(0, Y_GROW, zn, 6, Y_BLADE, zn, COBBLE)  # Nordwand
    h.fill(0, Y_GROW, zs, 6, Y_BLADE, zs, COBBLE)  # Südwand
    strip_facing = {c1: "south", c2: "north"}  # Klappe liegt an der Wand (Nord- bzw. Südkante)
    xe = 5
    for z in range(zn + 1, zs):
        for x in range(1, 6):
            if z in strip_facing and x <= xe:
                barrier = B("oak_trapdoor", facing=strip_facing[z], half="bottom", open=True)
                if species == "pig":
                    h.set(x, Y_SUPPORT, z, WALL)  # Mauer-Grat: Oberkante 6,5 wie die Stufen
                    if x == 5:
                        # offenes Zauntor im Graben (keine Kollision): der Grat bekommt einen Arm bis zur
                        # Grabenkante, damit kein Tier auf einem Absatz im Graben hängen bleibt
                        h.set(6, Y_SUPPORT, z, B("oak_fence_gate", facing="north", open=True))
                h.set(x, Y_GROW, z, barrier)  # Sperre auf Babyhöhe
                h.set(x, Y_BLADE, z, barrier)  # bis zur Decke: niemand kann oben drauf stehen
            else:
                h.set(x, Y_GROW, z, B("oak_sign") if species == "cow" else SLAB_FLOOR)
        if z not in strip_facing:
            h.set(1, Y_BLADE, z, WATER)  # Quellen der Wasserklinge (fließt nach Osten)
    h.fill(0, Y_CEIL, zn, 6, Y_CEIL, zs, COBBLE)  # Beckendecke
    h.note(f"{species}_grow", 1, Y_GROW, zn + 1)
    h.note(f"{species}_grow", 5, Y_BLADE, zs - 1)

    # --- Graben x6: Wandschild in der Klingenebene (wasserdicht, ohne Kollision), darunter offen
    for z in range(zn + 1, zs):
        h.set(6, Y_BLADE, z, B("oak_wall_sign", facing="west"))
    h.fill(5, Y_LAVA, zn + 1, 5, 4, zs - 1, COBBLE)  # Westwand des Grabens unter dem Becken
    h.fill(6, Y_LAVA, zn, 6, Y_BLADE, zn, COBBLE)
    h.fill(6, Y_LAVA + 1, zs, 6, Y_BLADE, zs, COBBLE)

    # --- Zuchtgänge (y9 Gitter, y10-11 Raum), Wände (Vollblock y10 + Stufe y11), Futterdeck z0+3..z0+5
    h.fill(0, Y_GRID, zn, 6, Y_PEN, zs, COBBLE)
    for z in (c1, c2):
        h.fill(1, Y_CEIL, z, xe, Y_CEIL, z, AIR)  # Fallöffnung in der Beckendecke
        h.fill(1, Y_GRID, z, xe, Y_GRID, z, grid)
        h.fill(1, Y_PEN, z, xe, Y_PEN, z, AIR)
        h.note(f"{species}_pen", 1, Y_PEN, z)
        h.note(f"{species}_pen", xe, Y_PEN + 1, z)
    for z in (zn, zn + 2, zs - 2, zs):
        h.fill(0, Y_PEN + 1, z, 6, Y_PEN + 1, z, SLAB)
    for z in (c1, c2, zn + 3, zn + 4, zn + 5):
        h.set(0, Y_PEN + 1, z, SLAB)  # Westrand
    for z in (c1, c2):
        h.fill(xe + 1, Y_PEN + 1, z, 6, Y_PEN + 1, z, SLAB)  # Ostende der Gänge
    # Tore vom Futterdeck in die Zuchtgänge (zum Hineinführen der Tiere)
    h.set(3, Y_PEN + 1, zn + 2, B("oak_fence_gate", facing="north"))
    h.set(3, Y_PEN + 1, zs - 2, B("oak_fence_gate", facing="north"))
    for x in (1, 5):
        h.set(x, Y_PEN + 1, zn + 4, B("torch"))

    # --- Tötungsstrom x6, y2 (Quelle im Norden, fließt nach Süden bis z0+8 = Stufe 1)
    h.fill(5, Y_STREAM, zn, 5, Y_STREAM, zk, COBBLE)
    h.fill(7, Y_STREAM, zn, 7, Y_STREAM, zk, COBBLE)
    h.set(6, Y_STREAM, zn, COBBLE)
    h.fill(6, Y_HOPPER, zn + 1, 6, Y_HOPPER, zs - 1, COBBLE)
    h.set(6, Y_STREAM, zn + 1, WATER)
    # Tötungsstelle: Das Tier steht im letzten Wasserfeld (zs) und ragt nur knapp in die Lavazelle (zk):
    # dort hält es ein Sperrblock auf, über dem die Lava liegt (y3). Das Tier berührt sie nur mit dem Kopf.
    #   Kuh:     Schleifstein (Rad ab 0,125 vom Rand)
    #   Schwein: Amboss quer (Sockel 0,25 hoch hebt das Schwein an, Kopf 3,15; Oberteil ab 0,1875 vom Rand)
    # Weniger als 0,225 (halbe Babybreite): Ein Baby kommt mit seinem Mittelpunkt nie in die Lavazelle.
    # Stünde es darin, würde es wegen der Kollision des Blocks springen und mit dem Kopf in die Lava geraten.
    # In Lava will jedes Tier nach oben schwimmen – die Decke über zs verhindert das, deshalb entstehen die
    # Drops immer knapp über dem Boden und steigen höchstens bis 2,99 (Lava beginnt bei 3,0):
    #   Kuh (1,4 hoch):     obere Stufe (Unterkante 3,5) -> Füße höchstens 2,1
    #   Schwein (0,9 hoch): seitlich zeigender Trichter (Unterkante 3,25) -> Füße höchstens 2,35
    # Decke und Sperrblock lassen keine Flüssigkeit hinein und halten Wasser und Lava getrennt.
    h.set(5, Y_LAVA, zs, COBBLE)
    if species == "cow":
        h.set(6, Y_LAVA, zs, B("cobblestone_slab", type="top"))
        h.set(6, Y_STREAM, zk, B("grindstone", face="floor", facing="north"))
    else:
        h.set(6, Y_LAVA, zs, B("hopper", facing="east"))  # nur als Decke, zeigt in den Kern
        h.set(6, Y_STREAM, zk, B("anvil", facing="east"))
    h.set(7, Y_LAVA, zs, COBBLE)
    h.set(6, 4, zs, COBBLE)
    h.set(6, Y_LAVA, zk, LAVA)
    h.note(f"{species}_lava", 6, Y_LAVA, zk)
    for x, y, z in ((5, Y_LAVA, zk), (7, Y_LAVA, zk), (6, Y_STREAM, zk + 1), (6, Y_LAVA, zk + 1), (6, 4, zk),
                    (5, Y_STREAM, zk), (7, Y_STREAM, zk)):
        h.set(x, y, z, COBBLE)
    h.note(f"{species}_stream", 6, Y_STREAM, zn + 1)
    h.note(f"{species}_stream", 6, 6, zk)
    # 2 Trichter -> Doppelkiste (Front zum Kellergang)
    for z in (zs, zk):
        h.set(6, Y_HOPPER, z, B("hopper", facing="down"))
        h.set(6, Y_CHEST, z, B("chest", facing="east"))
        h.note(f"{species}_chest", 6, Y_CHEST, z)
    h.set(6, Y_HOPPER, zk + 1, COBBLE)
    h.set(6, Y_CHEST, zk + 1, COBBLE)
    # Kellergang-Westwand unter dem Strom schließen
    h.fill(6, Y_CHEST, zn, 6, Y_CHEST, zs - 1, COBBLE)
    h.set(6, Y_HOPPER, zn, COBBLE)
    # Licht unter dem Becken (Fackeln auf dem natürlichen Boden)
    for x, z in ((1, zn + 2), (4, zn + 2), (1, zn + 6), (4, zn + 6)):
        h.set(x, Y_CHEST, z, B("torch"))


def breeding_section(m: Model, z0: int, species: str) -> None:
    breeding_half(Half(m, False), z0, species)
    breeding_half(Half(m, True), z0, species)
    # Kern (x7-8) zwischen den Gräben bis zum Laufsteg (y10)
    m.fill(7, Y_STREAM, z0, 8, Y_PEN, z0 + 10, COBBLE)


# --------------------------------------------------------------------------- Huhn

def chicken_module(h: Half) -> None:
    """Brutmodul: 3 Zuchttrichter -> Werfer -> Kükenzelle 1x2 (Steinsäge unter Lavakessel)."""
    z = CHICKEN_Z
    # Kükenzelle
    h.set(5, 2, z - 1, B("dispenser", facing="south"))
    h.note("chicken_dispenser", 5, 2, z - 1)
    for x in (5, 6):
        h.set(x, 2, z, B("stonecutter", facing="north"))
        h.set(x, 3, z, B("lava_cauldron"))
        h.note("chicken_cell", x, 2, z)
    for pos in ((4, 2, z), (6, 2, z - 1), (5, 2, z + 1), (6, 2, z + 1), (7, 2, z)):
        h.set(*pos, GLASS)  # Glas: Küken landen teils in der Wand, Glas erstickt nicht
    for pos in ((4, 3, z), (7, 3, z), (5, 3, z + 1), (6, 3, z + 1), (6, 3, z - 1)):
        h.set(*pos, COBBLE)
    # Sammeltrichter -> Doppelkiste (Front zum Kellergang)
    h.set(5, 1, z, B("hopper", facing="east"))
    h.set(6, 1, z, B("hopper", facing="down"))
    h.set(6, 0, z, B("chest", facing="east"))
    h.set(6, 0, z + 1, B("chest", facing="east"))
    h.note("chicken_chest", 6, 0, z)
    h.note("chicken_chest", 6, 0, z + 1)
    h.set(4, 1, z, COBBLE)
    # Zuchttrichter (Hennen stehen darin) -> Werfer (dispenser)
    h.set(5, 3, z - 1, B("hopper", facing="down"))
    h.set(4, 3, z - 1, B("hopper", facing="east"))
    h.set(3, 3, z - 1, B("hopper", facing="east"))
    for x in (3, 4, 5):
        h.note("chicken_breeder", x, 4, z - 1)
    h.set(3, 2, z - 1, COBBLE)
    h.set(4, 2, z - 1, COBBLE)
    # Takt: Komparator liest den Zuchttrichter -> Block -> Staub darunter -> Block neben dem Werfer
    h.set(5, 3, z - 2, B("comparator", facing="south"))
    h.set(5, 2, z - 2, COBBLE)
    h.set(5, 3, z - 3, COBBLE)
    h.set(5, 2, z - 3, B("redstone_wire"))
    h.set(5, 1, z - 3, COBBLE)
    h.set(4, 3, z - 2, COBBLE)
    h.set(3, 3, z - 2, COBBLE)
    # Zuchtpen y4-5 (Glas), oben offen
    for x in (3, 4, 5):
        h.set(x, 4, z - 2, GLASS)
        h.set(x, 5, z - 2, GLASS)
        h.set(x, 4, z, GLASS)
        h.set(x, 5, z, GLASS)
    for x in (2, 6):
        h.set(x, 4, z - 1, GLASS)
        h.set(x, 5, z - 1, GLASS)
    h.set(2, 3, z - 1, COBBLE)
    h.set(6, 3, z - 1, COBBLE)


def chicken_section(m: Model) -> None:
    z = CHICKEN_Z
    for mirror in (False, True):
        chicken_module(Half(m, mirror))
    # Galerie (y4) über den Modulen
    for x in range(1, 15):
        for zz in range(21, 31):
            if m.get(x, 4, zz) == AIR:
                m.set(x, 4, zz, COBBLE)
    for mirror in (False, True):
        h = Half(m, mirror)
        for x in (3, 4, 5):
            h.set(x, 4, z - 1, AIR)  # Pen-Innenraum
        for x, zz in ((2, 22), (2, 29), (5, 29)):
            h.set(x, 0, zz, B("torch"))  # Licht unter der Galerie
    # Geländer (Mauern y5) mit Öffnung für die Rampe
    for zz in range(21, 31):
        m.set(1, 5, zz, WALL)
        m.set(14, 5, zz, WALL)
    for x in range(1, 15):
        m.set(x, 5, 21, WALL)
        m.set(x, 5, 30, WALL)
    m.set(14, 5, 26, AIR)
    for x, zz in ((1, 21), (14, 21), (1, 30), (14, 30), (1, 25), (14, 23)):
        m.set(x, 6, zz, B("torch"))
    # Rampe vom Boden auf die Galerie (Ostseite, Treppenstufen) – für Spieler und Tiere
    for i, (y, zz) in enumerate(((0, 30), (1, 29), (2, 28), (3, 27), (4, 26))):
        m.set(15, y, zz, B("cobblestone_stairs", facing="north"))
    # Treppe von der Galerie auf den Laufsteg (x7, nach Norden ansteigend)
    for y, zz in ((5, 26), (6, 25), (7, 24), (8, 23), (9, 22), (10, 21)):
        m.set(7, y, zz, B("cobblestone_stairs", facing="north"))


# --------------------------------------------------------------------------- Kellergang, Leiter

def corridor(m: Model) -> None:
    # Kellergang x7-8, y0-1, z0..27 (Boden = natürlicher Untergrund); Decke y2
    m.fill(7, 2, 21, 8, 3, 28, COBBLE)
    m.set(7, 2, CHICKEN_Z, GLASS)
    m.set(8, 2, CHICKEN_Z, GLASS)
    m.fill(7, 0, 28, 8, 1, 28, COBBLE)  # Südende
    m.fill(6, 0, 21, 6, 1, 25, COBBLE)
    m.fill(9, 0, 21, 9, 1, 25, COBBLE)
    for z in (2, 7, 12, 17, 23):
        m.set(7, 0, z, B("torch"))
    # Leiter Kellergang -> Galerie, oben mit geschlossener Falltür (Tiere laufen darüber)
    for y in range(0, 5):
        m.set(8, y, 28, COBBLE)
    for y in range(0, 4):
        m.set(8, y, 27, B("ladder", facing="north"))
    m.set(8, 4, 27, B("oak_trapdoor", facing="north", half="top", open=False))
    m.set(7, 4, 27, COBBLE)
    # Laufsteg: Absturzsicherung an den Enden
    for x in (7, 8):
        m.set(x, Y_PEN + 1, 0, WALL)
    m.set(8, Y_PEN + 1, 20, WALL)


def build() -> Model:
    m = Model()
    breeding_section(m, COW_Z0, "cow")
    breeding_section(m, PIG_Z0, "pig")
    for z in (2, 6, 12, 16):
        m.set(8, Y_PEN + 1, z, B("torch"))  # Laufsteg
    chicken_section(m)
    corridor(m)
    finalize(m)
    return m


# --------------------------------------------------------------------------- Zustände berechnen

def _neighbor(m: Model, pos, direction):
    dx, dy, dz = DIRS[direction]
    return m.get(pos[0] + dx, pos[1] + dy, pos[2] + dz)


_FULL_SOLID = {"minecraft:cobblestone", "minecraft:glass", "minecraft:stone", "minecraft:oak_planks", "minecraft:dispenser"}


def _wall_connects(nb: Block, toward: str) -> bool:
    if nb.id.endswith("_wall"):
        return True
    if nb.name in _FULL_SOLID:
        return True
    if nb.id.endswith("fence_gate"):
        facing = nb.prop("facing")
        # Zauntor verbindet, wenn die Richtung quer zur Tor-Ausrichtung liegt
        return {"north": "ns", "south": "ns", "east": "ew", "west": "ew"}[facing] != {"north": "ns", "south": "ns", "east": "ew", "west": "ew"}[toward]
    return False


_POST_OVERRIDE = {"minecraft:torch", "minecraft:oak_sign", "minecraft:redstone_torch"}


def _finalize_wall(m: Model, pos, block: Block) -> Block:
    sides = {}
    for d in ("north", "east", "south", "west"):
        sides[d] = "low" if _wall_connects(_neighbor(m, pos, d), d) else "none"
    above = _neighbor(m, pos, "up")
    n, s, e, w = (sides[k] == "none" for k in ("north", "south", "east", "west"))
    corner = (n and s and e and w) or (n != s) or (e != w)
    up = (above.id.endswith("_wall") and above.prop("up") == "true") or corner or above.name in _POST_OVERRIDE
    return block.with_props(up=up, **sides)


def finalize(m: Model) -> None:
    """Abhängige Zustände berechnen (Mauern, Tore, Kisten, Redstone) und Wasserfluss ergänzen."""
    for pos, block in list(m.blocks.items()):
        if block.id == "cobblestone_wall":
            m.blocks[pos] = _finalize_wall(m, pos, block)
        elif block.id == "oak_fence_gate":
            axis = ("north", "south") if block.prop("facing") in ("east", "west") else ("east", "west")
            in_wall = any(_neighbor(m, pos, d).id.endswith("_wall") for d in axis)
            m.blocks[pos] = block.with_props(in_wall=in_wall)
        elif block.id == "redstone_wire":
            m.blocks[pos] = block.with_props(north="side", south="side", east="side", west="side")
    for pos, block in list(m.blocks.items()):
        if block.id == "chest":
            facing = block.prop("facing")
            cw = {"north": "east", "east": "south", "south": "west", "west": "north"}[facing]
            ccw = OPPOSITE[cw]
            kind = "single"
            for d, t in ((cw, "left"), (ccw, "right")):
                nb = _neighbor(m, pos, d)
                if nb.id == "chest" and nb.prop("facing") == facing:
                    kind = t
            m.blocks[pos] = block.with_props(type=kind)
    simulate_water(m)


def _water_passable(m: Model, pos) -> bool:
    return m.inside(*pos) and m.get(*pos) == AIR


def simulate_water(m: Model) -> None:
    """Wasserausbreitung wie in Minecraft für ebene Flächen ohne Abflusslöcher (BFS, -1 pro Block).

    Erzeugt die fließenden Wasserzustände, damit der Litematica-Verifier nach dem Befüllen grün zeigt.
    Abflusslöcher (Luft unter Wasser) sind ein Konstruktionsfehler und werden gemeldet.
    """
    sources = [p for p, b in m.blocks.items() if b.id == "water" and b.prop("level") == "0"]
    amount: dict[tuple[int, int, int], int] = {}
    frontier = [(p, 8) for p in sources]
    for p in sources:
        amount[p] = 8
    while frontier:
        nxt = []
        for (x, y, z), a in frontier:
            if a <= 1:
                continue
            for d in ("north", "south", "east", "west"):
                dx, _, dz = DIRS[d]
                q = (x + dx, y, z + dz)
                if q in amount and amount[q] >= a - 1:
                    continue
                if q not in amount and not _water_passable(m, q):
                    continue
                if q in amount and amount[q] == 8:
                    continue
                amount[q] = a - 1
                nxt.append((q, a - 1))
        frontier = nxt
    for q, a in amount.items():
        below = (q[0], q[1] - 1, q[2])
        if m.inside(*below) and m.get(*below) == AIR and a < 8:
            raise ValueError(f"Wasser würde bei {q} nach unten abfließen")
        if a < 8:
            m.blocks[q] = B("water", level=8 - a)
