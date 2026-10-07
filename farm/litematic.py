"""Export des Blockmodells als Litematica-Schematic (.litematic, Format-Version 7)."""
from __future__ import annotations

import time

from . import nbt
from .blocks import AIR, DATA_VERSION, Block
from .model import Model

SCHEMATIC_VERSION = 7
SCHEMATIC_SUB_VERSION = 1


def _pack(values: list[int], bits: int) -> list[int]:
    """Werte wie Litematicas LitematicaBitArray packen (Einträge dürfen über Long-Grenzen laufen)."""
    longs = [0] * ((len(values) * bits + 63) // 64)
    mask = (1 << bits) - 1
    for i, v in enumerate(values):
        start = i * bits
        idx, off = start >> 6, start & 63
        longs[idx] |= (v & mask) << off
        if off + bits > 64:
            longs[idx + 1] |= (v & mask) >> (64 - off)
    # als vorzeichenbehaftete 64-Bit-Zahlen speichern
    return [((x & 0xFFFFFFFFFFFFFFFF) ^ 0x8000000000000000) - 0x8000000000000000 for x in longs]


def unpack(longs: list[int], bits: int, count: int) -> list[int]:
    data = [x & 0xFFFFFFFFFFFFFFFF for x in longs]
    mask = (1 << bits) - 1
    out = []
    for i in range(count):
        start = i * bits
        idx, off = start >> 6, start & 63
        v = data[idx] >> off
        if off + bits > 64:
            v |= data[idx + 1] << (64 - off)
        out.append(v & mask)
    return out


def _state_tag(block: Block) -> dict:
    tag = {"Name": block.name}
    if block.props:
        tag["Properties"] = {k: v for k, v in block.props}
    return tag


def build_nbt(m: Model, name: str, author: str, description: str) -> dict:
    sx, sy, sz = m.size
    palette: list[Block] = [AIR]
    index = {AIR: 0}
    values = []
    for y in range(sy):
        for z in range(sz):
            for x in range(sx):
                b = m.get(x, y, z)
                if b not in index:
                    index[b] = len(palette)
                    palette.append(b)
                values.append(index[b])
    bits = max(2, (len(palette) - 1).bit_length())
    now = int(time.time() * 1000)
    total_blocks = sum(1 for v in values if v != 0)
    xyz = lambda a, b, c: {"x": nbt.Int(a), "y": nbt.Int(b), "z": nbt.Int(c)}  # noqa: E731
    region = {
        "Position": xyz(0, 0, 0),
        "Size": xyz(sx, sy, sz),
        "BlockStatePalette": nbt.TagList(nbt.TAG_COMPOUND, [_state_tag(b) for b in palette]),
        "BlockStates": nbt.LongArray(_pack(values, bits)),
        "TileEntities": nbt.TagList(nbt.TAG_COMPOUND),
        "Entities": nbt.TagList(nbt.TAG_COMPOUND),
        "PendingBlockTicks": nbt.TagList(nbt.TAG_COMPOUND),
        "PendingFluidTicks": nbt.TagList(nbt.TAG_COMPOUND),
    }
    return {
        "MinecraftDataVersion": nbt.Int(DATA_VERSION),
        "Version": nbt.Int(SCHEMATIC_VERSION),
        "SubVersion": nbt.Int(SCHEMATIC_SUB_VERSION),
        "Metadata": {
            "Name": name,
            "Author": author,
            "Description": description,
            "RegionCount": nbt.Int(1),
            "TotalVolume": nbt.Int(sx * sy * sz),
            "TotalBlocks": nbt.Int(total_blocks),
            "TimeCreated": nbt.Long(now),
            "TimeModified": nbt.Long(now),
            "EnclosingSize": xyz(sx, sy, sz),
        },
        "Regions": {name: region},
    }


def write(m: Model, path, name: str, author: str, description: str) -> None:
    nbt.write_gzip(path, build_nbt(m, name, author, description))


def read_blocks(path) -> tuple[tuple[int, int, int], dict]:
    """Eigener Decoder (zur Kontrolle): liefert Größe und {(x, y, z): Block} ohne Luft."""
    _, root = nbt.read_gzip(path)
    region = next(iter(root["Regions"].values()))
    sx, sy, sz = (region["Size"][k].value for k in ("x", "y", "z"))
    palette = [Block(e["Name"], tuple(sorted(e.get("Properties", {}).items()))) for e in region["BlockStatePalette"]]
    bits = max(2, (len(palette) - 1).bit_length())
    values = unpack(region["BlockStates"].value, bits, sx * sy * sz)
    blocks = {}
    i = 0
    for y in range(sy):
        for z in range(sz):
            for x in range(sx):
                b = palette[values[i]]
                if b != AIR:
                    blocks[(x, y, z)] = b
                i += 1
    return (sx, sy, sz), blocks
