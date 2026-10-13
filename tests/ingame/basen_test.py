"""Ingame-Test der rustikalen Basen auf dem headless 26.3-Testserver (per RCON).

  python3 tests/ingame/basen_test.py --server-dir <dir> [basis ...]

Ablauf je Basis:
  1. Bereich leeren, dann jeden Schritt des Bauplans per /setblock ausführen – in genau der Reihenfolge, die der
     Bot benutzt (inklusive oberer Türhälften, Bettkopfenden und Hilfsblöcken, die wieder abgebaut werden).
     Das Spiel berechnet dabei Zaun-, Scheiben-, Mauer- und Treppenzustände selbst aus den Nachbarn.
  2. Ein Spieltag im Zeitraffer mit 100-facher Zufallstick-Rate (Laub, Feuer, Pflanzen hätten Zeit, sich zu ändern).
  3. Welt speichern, alle Blöcke aus den Regionsdateien lesen und mit dem Modell vergleichen.
Server vorbereiten: Flachwelt, enable-rcon=true, rcon.password=farmtest, pause-when-empty-seconds=0.
"""
from __future__ import annotations

import argparse
import importlib
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from basen import bauplan, zustaende  # noqa: E402
from farm.blocks import AIR  # noqa: E402
import anvil  # noqa: E402
import rcon  # noqa: E402
from run_test import wait_ticks  # noqa: E402

GROUND_Y = -61  # Flachwelt: Gras auf y=-61 -> Schematic-Ebene 0 ersetzt das Gras
ORIGINS = {"starterhuette": (200, GROUND_Y, 0), "blockhaus": (240, GROUND_Y, 0), "gehoeft": (300, GROUND_Y, 0)}


def state_str(b) -> str:
    if not b.props:
        return b.name
    return b.name + "[" + ",".join(f"{k}={v}" for k, v in b.props) + "]"


def build(r, key: str):
    m = importlib.import_module(f"basen.{key}").build()
    zustaende.finalisieren(m)
    steps, errors = bauplan.plan(m)
    assert not errors, errors
    ox, oy, oz = ORIGINS[key]
    sx, sy, sz = m.size
    r.cmd(f"forceload add {ox - 16} {oz - 16} {ox + sx + 16} {oz + sz + 16}")
    # Fläche vorbereiten: Gras auf Ebene 0, darüber Luft, 1 Block Rand
    r.cmd(f"kill @e[type=!minecraft:player,x={ox - 2},y={oy},z={oz - 2},dx={sx + 4},dy={sy + 4},dz={sz + 4}]")
    for y in range(oy + sy + 2, oy, -1):
        r.cmd(f"fill {ox - 1} {y} {oz - 1} {ox + sx} {y} {oz + sz} minecraft:air")
    r.cmd(f"fill {ox - 1} {oy} {oz - 1} {ox + sx} {oy} {oz + sz} minecraft:grass_block")
    fails = []
    for s in steps:
        if s.aktion == "abbauen":
            todo = [(s.pos, "minecraft:air")]
        elif s.aktion == "hilfsblock":
            todo = [(s.pos, "minecraft:dirt")]
        else:
            todo = [(p, state_str(m.get(*p))) for p in [s.pos] + list(s.teile)]
        for p, state in todo:
            out = r.cmd(f"setblock {ox + p[0]} {oy + p[1]} {oz + p[2]} {state}")
            if "Changed the block" not in out:
                fails.append((p, out))
    print(f"{key}: {len(steps)} Schritte gesetzt, {len(fails)} ohne Wirkung", fails[:5])
    return m


def readback(r, server_dir: Path, key: str, m) -> list:
    r.cmd("save-all flush")
    time.sleep(2.0)
    ox, oy, oz = ORIGINS[key]
    sx, sy, sz = m.size
    world = server_dir / "world" / "dimensions" / "minecraft" / "overworld"
    world = world if (world / "region").exists() else server_dir / "world"
    raw = anvil.read_blocks(world, ox, oy, oz, ox + sx - 1, oy + sy - 1, oz + sz - 1)
    diffs = []
    for (wx, wy, wz), b in raw.items():
        p = (wx - ox, wy - oy, wz - oz)
        want = m.get(*p)
        if p[1] == 0 and want == AIR:
            continue  # Gelände auf Ebene 0
        if b.name == "minecraft:air" and want == AIR:
            continue
        if b != want:
            diffs.append((p, str(want), str(b)))
    return diffs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--server-dir", required=True, type=Path)
    ap.add_argument("basen", nargs="*", default=list(ORIGINS))
    ap.add_argument("--no-ticks", action="store_true")
    a = ap.parse_args()
    r = rcon.connect("farmtest")
    for rule, value in (("spawn_mobs", "false"), ("spawn_monsters", "false"), ("advance_weather", "false"),
                        ("send_command_feedback", "true"), ("fire_spread_radius_around_player", "128")):
        r.cmd(f"gamerule {rule} {value}")
    r.cmd("weather clear")
    models = {k: build(r, k) for k in a.basen}
    if not a.no_ticks:
        r.cmd("gamerule random_tick_speed 300")
        wait_ticks(r, 24000)
        r.cmd("gamerule random_tick_speed 3")
    ok = True
    for k, m in models.items():
        diffs = readback(r, a.server_dir, k, m)
        print(f"{k}: {len(diffs)} Abweichungen")
        for d in diffs[:25]:
            print("  ", d)
        ok &= not diffs
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
