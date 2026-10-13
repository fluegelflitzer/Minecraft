"""Blockkatalog für bot-baubare Survival-Basen.

Nur Blöcke, die
  - im Survival ohne Behutsamkeit und ohne Nether/End zu bekommen sind,
  - mit genau einem Rechtsklick in ihren Endzustand gesetzt werden (Tür und Bett setzen beide Hälften selbst),
  - nicht wachsen, nicht fallen und nicht fließen.
Jeder Eintrag sagt, wie der Block geformt ist (für Nachbarzustände, Licht und Bauplan) und welcher
Gegenstand dafür ins Inventar gehört.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from farm.blocks import Block

_NAMES = json.loads((Path(__file__).parent / "data" / "namen_de.json").read_text())

WOODS = ("oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry")
STONES = {  # Grundblock -> hat Treppe/Stufe/Mauer
    "cobblestone": "cobblestone", "mossy_cobblestone": "mossy_cobblestone", "stone": "stone",
    "stone_bricks": "stone_brick", "mossy_stone_bricks": "mossy_stone_brick", "bricks": "brick",
    "andesite": "andesite", "polished_andesite": "polished_andesite", "cobbled_deepslate": "cobbled_deepslate",
    "deepslate_bricks": "deepslate_brick", "deepslate_tiles": "deepslate_tile", "smooth_stone": "smooth_stone",
}
COLORS = ("white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray", "cyan",
          "purple", "blue", "brown", "green", "red", "black")
FLOWERS = ("dandelion", "poppy", "blue_orchid", "allium", "azure_bluet", "red_tulip", "orange_tulip", "white_tulip",
           "pink_tulip", "oxeye_daisy", "cornflower", "lily_of_the_valley")


@dataclass(frozen=True)
class Eintrag:
    form: str  # voll, saeule, gerichtet, stufe, treppe, zaun, zauntor, scheibe, mauer, tuer, falltuer, bett,
    #            laterne, kette, fackel, wandfackel, leiter, teppich, pflanze, kiste, lagerfeuer, laub, deko
    item: str  # Gegenstand (Minecraft-ID ohne Namespace)
    licht: int = 0
    durchsichtig: bool = False  # lässt Licht durch (für die Lichtprüfung)
    werkzeug: str = ""  # besonderes Werkzeug zum Beschaffen, z. B. "Schere"


def _form_of(bid: str) -> Eintrag | None:
    for w in WOODS:
        if bid == f"{w}_planks":
            return Eintrag("voll", bid)
        if bid in (f"{w}_log", f"{w}_wood"):
            return Eintrag("saeule", bid)
        if bid == f"{w}_stairs":
            return Eintrag("treppe", bid, durchsichtig=True)
        if bid == f"{w}_slab":
            return Eintrag("stufe", bid, durchsichtig=True)
        if bid == f"{w}_fence":
            return Eintrag("zaun", bid, durchsichtig=True)
        if bid == f"{w}_fence_gate":
            return Eintrag("zauntor", bid, durchsichtig=True)
        if bid == f"{w}_door":
            return Eintrag("tuer", bid, durchsichtig=True)
        if bid == f"{w}_trapdoor":
            return Eintrag("falltuer", bid, durchsichtig=True)
        if bid == f"{w}_pressure_plate":
            return Eintrag("deko", bid, durchsichtig=True)
        if bid == f"{w}_leaves":
            return Eintrag("laub", bid, durchsichtig=True, werkzeug="Schere")
    for full, pre in STONES.items():
        if bid == full:
            return Eintrag("voll", bid)
        if bid == f"{pre}_stairs":
            return Eintrag("treppe", bid, durchsichtig=True)
        if bid == f"{pre}_slab":
            return Eintrag("stufe", bid, durchsichtig=True)
        if bid == f"{pre}_wall":
            return Eintrag("mauer", bid, durchsichtig=True)
    for c in COLORS:
        if bid == f"{c}_bed":
            return Eintrag("bett", bid, durchsichtig=True)
        if bid == f"{c}_carpet":
            return Eintrag("teppich", bid, durchsichtig=True)
        if bid == f"{c}_wool":
            return Eintrag("voll", bid)
    if bid in FLOWERS:
        return Eintrag("pflanze", bid, durchsichtig=True)
    return _SPECIAL.get(bid)


_SPECIAL = {
    "glass": Eintrag("voll", "glass", durchsichtig=True),
    "glass_pane": Eintrag("scheibe", "glass_pane", durchsichtig=True),
    "lantern": Eintrag("laterne", "lantern", licht=15, durchsichtig=True),
    "iron_chain": Eintrag("kette", "iron_chain", durchsichtig=True),
    "torch": Eintrag("fackel", "torch", licht=14, durchsichtig=True),
    "wall_torch": Eintrag("wandfackel", "torch", licht=14, durchsichtig=True),
    "campfire": Eintrag("lagerfeuer", "campfire", licht=15, durchsichtig=True),
    "ladder": Eintrag("leiter", "ladder", durchsichtig=True),
    "chest": Eintrag("kiste", "chest", durchsichtig=True),
    "barrel": Eintrag("gerichtet", "barrel"),
    "crafting_table": Eintrag("voll", "crafting_table"),
    "furnace": Eintrag("gerichtet", "furnace"),
    "smoker": Eintrag("gerichtet", "smoker"),
    "blast_furnace": Eintrag("gerichtet", "blast_furnace"),
    "bookshelf": Eintrag("voll", "bookshelf"),
    "hay_block": Eintrag("saeule", "hay_block"),
    "composter": Eintrag("deko", "composter", durchsichtig=True),
    "cauldron": Eintrag("deko", "cauldron", durchsichtig=True),
    "smithing_table": Eintrag("voll", "smithing_table"),
    "fletching_table": Eintrag("voll", "fletching_table"),
    "cartography_table": Eintrag("voll", "cartography_table"),
    "loom": Eintrag("gerichtet", "loom"),
    "stonecutter": Eintrag("deko", "stonecutter", durchsichtig=True),
    "lectern": Eintrag("deko", "lectern", durchsichtig=True),
    "flower_pot": Eintrag("deko", "flower_pot", durchsichtig=True),
    "coarse_dirt": Eintrag("voll", "coarse_dirt"),
    "moss_block": Eintrag("voll", "moss_block"),
    "moss_carpet": Eintrag("teppich", "moss_carpet", durchsichtig=True),
    "pumpkin": Eintrag("voll", "pumpkin"),
    "carved_pumpkin": Eintrag("gerichtet", "carved_pumpkin"),
    "jack_o_lantern": Eintrag("gerichtet", "jack_o_lantern", licht=15),
}

# Gerichtete Blöcke, deren Vorderseite beim Setzen zum Spieler zeigt (facing = Gegenrichtung des Blicks)
FACE_PLAYER = {"furnace", "smoker", "blast_furnace", "loom", "stonecutter", "lectern", "carved_pumpkin",
               "jack_o_lantern", "chest"}

# Blöcke mit voller Kollisionsform (Bett, Kiste usw. zählen nicht dazu) – wichtig für Türscharniere
FULL_FORMS = {"voll", "saeule", "gerichtet", "laub"}

# Ausnahmen bei Verbindungen (Zäune, Scheiben, Mauern verbinden sich nicht damit)
CONNECT_EXCEPTIONS = ("_leaves", "pumpkin", "jack_o_lantern", "melon")


def eintrag(block: Block | str) -> Eintrag | None:
    bid = block if isinstance(block, str) else block.id
    if bid == "air":
        return None
    return _form_of(bid)


def name_de(item: str) -> str:
    return _NAMES.get(item, item)


def is_logs_tag(bid: str) -> bool:
    return bid.endswith(("_log", "_wood", "_stem", "_hyphae"))


def full_block(block: Block) -> bool:
    """Volle Kollisionsform (1 x 1 x 1)."""
    e = eintrag(block)
    if e is None:
        return False
    if e.form in FULL_FORMS:
        return True
    if e.form == "stufe":
        return block.prop("type") == "double"
    return False


def sturdy(block: Block, face: str) -> bool:
    """Ist die Seite `face` dieses Blocks eine volle, tragende Fläche (isFaceSturdy, FULL)?"""
    e = eintrag(block)
    if e is None:
        return False
    if e.form in FULL_FORMS:
        return True
    if e.form == "stufe":
        t = block.prop("type")
        return t == "double" or (t == "bottom" and face == "down") or (t == "top" and face == "up")
    if e.form == "treppe":
        half = block.prop("half")
        if face == "up":
            return half == "top"
        if face == "down":
            return half == "bottom"
        shape, facing = block.prop("shape"), block.prop("facing")
        if shape == "straight":
            return face == facing
        if shape == "inner_left":
            return face in (facing, CCW[facing])
        if shape == "inner_right":
            return face in (facing, CW[facing])
        return False
    if block.id == "composter":  # Wände und Boden voll, oben offen
        return face != "up"
    if e.form == "falltuer":
        if block.prop("open") == "true":
            return face == OPP[block.prop("facing")]
        half = block.prop("half")
        return (face == "down" and half == "bottom") or (face == "up" and half == "top")
    return False


CW = {"north": "east", "east": "south", "south": "west", "west": "north"}
CCW = {v: k for k, v in CW.items()}
OPP = {"north": "south", "south": "north", "east": "west", "west": "east", "up": "down", "down": "up"}
