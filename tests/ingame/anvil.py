"""Blöcke direkt aus den Region-Dateien (.mca, Anvil-Format) einer gespeicherten Welt lesen."""
from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from farm.blocks import _DATA as _BLOCK_DATA, Block  # noqa: E402
from farm.nbt import loads  # noqa: E402


def _read_chunk(region: Path, cx: int, cz: int) -> dict | None:
    data = region.read_bytes()
    idx = 4 * ((cx & 31) + (cz & 31) * 32)
    (entry,) = struct.unpack(">I", data[idx:idx + 4])
    offset, sectors = entry >> 8, entry & 0xFF
    if offset == 0 or sectors == 0:
        return None
    start = offset * 4096
    length, ctype = struct.unpack(">IB", data[start:start + 5])
    payload = data[start + 5:start + 4 + length]
    if ctype == 2:
        raw = zlib.decompress(payload)
    elif ctype == 1:
        import gzip
        raw = gzip.decompress(payload)
    elif ctype == 3:
        raw = payload
    else:
        raise ValueError(f"Kompression {ctype} nicht unterstützt")
    return loads(raw)[1]


def _palette_entry(entry) -> Block:
    """Palette-Eintrag: 'name' (26.x), {'': name} (heterogene Liste), {id, properties} (26.x)
    oder klassisch {Name, Properties}."""
    if isinstance(entry, str):
        name, props = entry, {}
    elif "" in entry:
        name, props = entry[""], {}
    else:
        name = entry.get("Name", entry.get("id"))
        props = entry.get("Properties", entry.get("properties", {}))
    # 26.x speichert Standardwerte nicht mit -> ergänzen (soweit der Block bekannt ist)
    full = dict(_BLOCK_DATA.get(name, {}).get("default", {}))
    full.update(props)
    return Block(name, tuple(sorted(full.items())))


def read_blocks(world: Path, x0: int, y0: int, z0: int, x1: int, y1: int, z1: int) -> dict:
    """Liefert {(x, y, z): Block} (Weltkoordinaten) für den Quader x0..x1, y0..y1, z0..z1."""
    result = {}
    for cx in range(x0 >> 4, (x1 >> 4) + 1):
        for cz in range(z0 >> 4, (z1 >> 4) + 1):
            region = world / "region" / f"r.{cx >> 5}.{cz >> 5}.mca"
            chunk = _read_chunk(region, cx, cz)
            if chunk is None:
                continue
            for section in chunk["sections"]:
                sy = section["Y"].value
                if sy * 16 > y1 or sy * 16 + 15 < y0 or "block_states" not in section:
                    continue
                bs = section["block_states"]
                palette = []
                for entry in bs["palette"]:
                    palette.append(_palette_entry(entry))
                data = bs["data"].value if "data" in bs else None
                bits = max(4, (len(palette) - 1).bit_length())
                per_long = 64 // bits
                mask = (1 << bits) - 1
                for ly in range(16):
                    y = sy * 16 + ly
                    if not y0 <= y <= y1:
                        continue
                    for lz in range(16):
                        z = cz * 16 + lz
                        if not z0 <= z <= z1:
                            continue
                        for lx in range(16):
                            x = cx * 16 + lx
                            if not x0 <= x <= x1:
                                continue
                            if data is None:
                                state = palette[0]
                            else:
                                i = ly * 256 + lz * 16 + lx
                                word = data[i // per_long] & 0xFFFFFFFFFFFFFFFF
                                state = palette[(word >> ((i % per_long) * bits)) & mask]
                            result[(x, y, z)] = state
    return result
