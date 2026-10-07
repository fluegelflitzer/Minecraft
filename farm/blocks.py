"""Blockzustände (Name + Properties), validiert gegen die Blockliste von Minecraft 26.3."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

_DATA = json.loads((Path(__file__).parent / "data" / "blocks_26.3.json").read_text())

DATA_VERSION = 5023  # Minecraft Java 26.3 ("world_version" aus version.json)
MC_VERSION = "26.3"


@dataclass(frozen=True)
class Block:
    name: str
    props: tuple = field(default_factory=tuple)  # sortierte (key, value)-Paare

    @property
    def id(self) -> str:
        return self.name.split(":", 1)[1]

    def prop(self, key: str) -> str:
        return dict(self.props)[key]

    def with_props(self, **changes) -> "Block":
        props = dict(self.props)
        for key, value in changes.items():
            if key not in props:
                raise KeyError(f"{self.name} hat keine Eigenschaft {key}")
            props[key] = _fmt(value)
        return Block(self.name, tuple(sorted(props.items())))

    def __str__(self) -> str:
        if not self.props:
            return self.name
        return self.name + "[" + ",".join(f"{k}={v}" for k, v in self.props) + "]"


def _fmt(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def B(block_id: str, **props) -> Block:
    """Vollständigen Blockzustand bauen: nicht angegebene Eigenschaften = Standardwerte von 26.3."""
    name = block_id if ":" in block_id else "minecraft:" + block_id
    if name not in _DATA:
        raise KeyError(f"Block {name} nicht in blocks_26.3.json")
    spec = _DATA[name]
    full = dict(spec["default"])
    for key, value in props.items():
        if key not in spec["properties"]:
            raise KeyError(f"{name} hat keine Eigenschaft {key}")
        value = _fmt(value)
        if value not in spec["properties"][key]:
            raise ValueError(f"{name}: {key}={value} ungültig, erlaubt: {spec['properties'][key]}")
        full[key] = value
    return Block(name, tuple(sorted(full.items())))


def parse(state: str) -> Block:
    """'minecraft:x[a=b,c=d]' -> Block (ohne Ergänzung von Standardwerten)."""
    if "[" in state:
        name, rest = state.split("[", 1)
        props = tuple(sorted(tuple(p.split("=", 1)) for p in rest.rstrip("]").split(",") if p))
    else:
        name, props = state, ()
    if ":" not in name:
        name = "minecraft:" + name
    return Block(name, props)


AIR = B("air")

# Richtungen
DIRS = {"north": (0, 0, -1), "south": (0, 0, 1), "west": (-1, 0, 0), "east": (1, 0, 0), "up": (0, 1, 0), "down": (0, -1, 0)}
OPPOSITE = {"north": "south", "south": "north", "west": "east", "east": "west", "up": "down", "down": "up"}
MIRROR_X = {"west": "east", "east": "west"}
