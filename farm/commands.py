"""Das Modell als /setblock-Befehlsfolge (für den Ingame-Test): erst Tragendes, dann Technik, Flüssigkeiten zuletzt."""
from __future__ import annotations

from .blocks import Block
from .model import Model

_SOLID_FIRST = {"cobbled_deepslate", "glass"}
_FLUIDS = {"water", "lava"}


def _phase(block: Block) -> int:
    if block.id in _SOLID_FIRST:
        return 0
    if block.id in _FLUIDS:
        return 3 if block.id == "lava" else 2
    if block.id in ("torch", "redstone_wire", "ladder", "oak_wall_sign"):
        return 1
    return 1


def setblock_commands(m: Model, origin: tuple[int, int, int], include_flowing: bool = False) -> list[str]:
    ox, oy, oz = origin
    items = []
    for (x, y, z), block in m.blocks.items():
        if block.id == "water" and block.prop("level") != "0" and not include_flowing:
            continue  # fließendes Wasser entsteht von selbst
        items.append((_phase(block), y, z, x, block))
    items.sort(key=lambda t: t[:4])
    return [f"setblock {ox + x} {oy + y} {oz + z} {block}" for _, y, z, x, block in items]
