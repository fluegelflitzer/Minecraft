"""Ingame-Test der Weizenfarm auf dem headless 26.3-Testserver (per RCON).

  python3 tests/ingame/weizen_test.py --server-dir <dir> build
  python3 tests/ingame/weizen_test.py --server-dir <dir> sim --plant --days 30
Schritte: build (bauen + Regionsdateien zurücklesen), readback, sim (4 Bauern + 4 Sammler einsetzen,
Tage im Zeitraffer; je Vierteltag Kisteninhalt, Brot/Weizen bei den Bauern, Inventar der Sammler,
herumliegende Items). --plant bepflanzt das Feld vorab mit Weizen in zufälligem Alter, --keep setzt
eine laufende Simulation fort, --no-collector lässt die Sammler weg (Vergleich).
Hinweis: per /summon erzeugte Dorfbewohner haben CanPickUpLoot=0 – der Test setzt es wie im
Survival auf 1, sonst heben die Bauern nichts auf.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from farm.blocks import AIR  # noqa: E402
from farm.commands import setblock_commands  # noqa: E402
from weizenfarm import model as wm  # noqa: E402
import anvil  # noqa: E402
import rcon  # noqa: E402
from run_test import count, wait_ticks  # noqa: E402

ORIGIN = (64, -61, 0)  # Flachwelt: der Acker (Ebene 0) ersetzt das Gras auf y=-61


def w(x, y, z):
    return ORIGIN[0] + x, ORIGIN[1] + y, ORIGIN[2] + z


def chest_items(r, pos) -> Counter:
    from run_test import chest_items as ci
    import run_test
    run_test.ORIGIN = ORIGIN
    return ci(r, pos)


def box(lo, hi):
    (x0, y0, z0), (x1, y1, z1) = w(*lo), w(*hi)
    return f"x={x0},y={y0},z={z0},dx={x1 - x0},dy={y1 - y0},dz={z1 - z0}"


def prepare(r) -> None:
    for rule, value in (("spawn_mobs", "false"), ("spawn_monsters", "false"), ("advance_time", "true"),
                        ("advance_weather", "false"), ("send_command_feedback", "true")):
        r.cmd(f"gamerule {rule} {value}")
    r.cmd("weather clear")
    x0, _, z0 = w(-8, 0, -8)
    x1, _, z1 = w(39, 0, 39)
    r.cmd(f"forceload add {x0} {z0} {x1} {z1}")


def build(r, m) -> None:
    sx, sy, sz = m.size
    x0, y0, z0 = w(-1, 0, -1)
    x1, y1, z1 = w(sx, sy + 2, sz)
    r.cmd(f"kill @e[type=!minecraft:player,{box((-1, 0, -1), (sx, sy + 2, sz))}]")
    r.cmd(f"fill {x0} {y0} {z0} {x1} {y1} {z1} minecraft:air")
    errors = [c for c in setblock_commands(m, ORIGIN) if "Changed the block" not in r.cmd(c)]
    print(f"Bau: {len(errors)} Befehle ohne Änderung", errors[:5])
    time.sleep(5)


def readback(r, server_dir: Path, m) -> list:
    r.cmd("save-all flush")
    time.sleep(1.0)
    sx, sy, sz = m.size
    x0, y0, z0 = w(0, 0, 0)
    world = server_dir / "world" / "dimensions" / "minecraft" / "overworld"
    raw = anvil.read_blocks(world if (world / "region").exists() else server_dir / "world",
                            x0, y0, z0, x0 + sx - 1, y0 + sy - 1, z0 + sz - 1)
    diffs = []
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                want = m.get(x, y, z)
                have = raw.get((x0 + x, y0 + y, z0 + z), AIR)
                if have.name == "minecraft:cave_air":
                    have = AIR
                if want != have:
                    diffs.append(((x, y, z), str(want), str(have)))
    return diffs


def villagers(r) -> list:
    """Beruf, Position (relativ), Inventar aller Test-Dorfbewohner."""
    out = r.cmd("execute as @e[type=minecraft:villager,tag=wf] run data get entity @s")
    res = []
    for part in out.split("has the following entity data: ")[1:]:
        inv = Counter()
        for cnt, name in re.findall(r'count: (\d+), id: "minecraft:([a-z_]+)"', part[part.find("Inventory:"):]):
            inv[name] += int(cnt)
        pos = re.search(r"Pos: \[([-\d.]+)d, ([-\d.]+)d, ([-\d.]+)d\]", part)
        prof = re.search(r'profession: "minecraft:([a-z_]+)"', part)
        rel = tuple(round(float(v) - o, 1) for v, o in zip(pos.groups(), ORIGIN))
        res.append((prof.group(1) if prof else "?", rel, dict(inv)))
    return res


def status(r, m) -> dict:
    chest = Counter()
    for pos in m.notes["chest"]:
        chest += chest_items(r, pos)
    area = box((0, 0, 0), m.size)
    vs = villagers(r)
    return {"kiste": dict(chest), "berufe": dict(Counter(v[0] for v in vs)),
            "items_liegen": count(r, f"@e[type=minecraft:item,{area}]"),
            "brot_bei_bauern": sum(v[2].get("bread", 0) for v in vs if v[0] == "farmer"),
            "weizen_bei_bauern": sum(v[2].get("wheat", 0) for v in vs if v[0] == "farmer"),
            "bei_sammlern": dict(sum((Counter(v[2]) for v in vs if v[0] != "farmer"), Counter()))}


def sim(r, m, args) -> None:
    if args.keep:
        return run_days(r, m, args)
    r.cmd("kill @e[type=minecraft:villager]")
    r.cmd("kill @e[type=minecraft:item]")
    for pos in m.notes["chest"]:
        X, Y, Z = w(*pos)
        r.cmd(f"data merge block {X} {Y} {Z} {{Items:[]}}")
    r.cmd("time set 0")
    if args.plant:
        rnd = random.Random(1)
        for (x, y, z), b in m.blocks.items():
            if b.id == "farmland":
                X, Y, Z = w(x, y + 1, z)
                r.cmd(f"setblock {X} {Y} {Z} minecraft:wheat[age={rnd.randint(0, 7)}]")
    for (x, y, z) in m.notes["lamp"]:
        X, Y, Z = w(x + (1 if x < m.size[0] // 2 else -1), y, z + (1 if z < m.size[2] // 2 else -1))
        r.cmd(f'summon minecraft:villager {X + 0.5} {Y} {Z + 0.5} {{Tags:["wf"],CanPickUpLoot:1b,'
              f'Inventory:[{{id:"minecraft:wheat_seeds",count:{args.seeds}}}]}}')
    if not args.no_collector:
        for (x, y, z) in m.notes["cell"]:
            X, Y, Z = w(x, y, z)
            r.cmd(f'summon minecraft:villager {X + 0.5} {Y} {Z + 0.5} {{Tags:["wf","sammler"],CanPickUpLoot:1b}}')
    run_days(r, m, args)


def run_days(r, m, args) -> None:
    for day in range(args.days):
        for part in range(4):
            wait_ticks(r, 6000)
            st = status(r, m)
            print(f"Tag {day + 1}.{part + 1}:", json.dumps(st, ensure_ascii=False, default=str), flush=True)
    for v in villagers(r):
        print("  ", v)
    for pos in m.notes["chest"]:
        print("   Kiste", pos, dict(chest_items(r, pos)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server-dir", required=True, type=Path)
    ap.add_argument("--password", default="farmtest")
    ap.add_argument("step", choices=["build", "readback", "sim", "all"])
    ap.add_argument("--days", type=int, default=5)
    ap.add_argument("--seeds", type=int, default=32)
    ap.add_argument("--plant", action="store_true", help="Feld vorab mit Weizen (zufälliges Alter) bepflanzen")
    ap.add_argument("--keep", action="store_true", help="laufende Simulation fortsetzen")
    ap.add_argument("--no-collector", action="store_true", help="ohne Sammler (Vergleich)")
    args = ap.parse_args()
    m = wm.build()
    r = rcon.connect(args.password)
    prepare(r)
    if args.step in ("build", "all"):
        build(r, m)
    if args.step in ("build", "readback", "all"):
        diffs = readback(r, args.server_dir, m)
        print(f"Readback: {len(diffs)} Abweichungen")
        for d in diffs[:30]:
            print("  ", d)
    if args.step in ("sim", "all"):
        sim(r, m, args)


if __name__ == "__main__":
    main()
