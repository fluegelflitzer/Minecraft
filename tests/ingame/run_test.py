"""Ingame-Test der Farm auf einem headless Minecraft-26.3-Server (per RCON).

Ablauf:
  build    – Farm per /setblock bauen (Flüssigkeiten zuletzt), aus den Region-Dateien zurücklesen
             und Block für Block mit dem Modell vergleichen.
  fire     – Brandtest: Feuer überall erlaubt, Zufallsticks stark erhöht.
  sim      – Tiere einsetzen, „füttern“ (InLove), /tick sprint, danach Kisten, Tiere, Feuer und
             Blöcke prüfen.
  bilanz   – genaue Zählung je Tierart: Geburten, erwachsen geworden, als Baby gestorben.
  all      – build, fire und sim nacheinander.

Server vorbereiten: siehe README (Abschnitt „Für Bastler“). Aufruf:
  python3 tests/ingame/run_test.py --server-dir <dir> all
  python3 tests/ingame/run_test.py --server-dir <dir> bilanz
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

from farm import model as fm  # noqa: E402
from farm.blocks import AIR, Block  # noqa: E402
from farm.commands import setblock_commands  # noqa: E402
from farm.nbt import read_gzip  # noqa: E402
import anvil  # noqa: E402
import rcon  # noqa: E402

ORIGIN = (0, -60, 0)  # Flachwelt: Gras auf y=-61


def w(x, y, z):
    ox, oy, oz = ORIGIN
    return ox + x, oy + y, oz + z


def wait_ticks(r: rcon.Rcon, ticks: int) -> None:
    out = r.cmd(f"tick sprint {ticks}")
    if "Unknown" in out:
        raise RuntimeError(out)
    while True:
        time.sleep(0.5)
        q = r.cmd("tick query")
        if "sprint" not in q.lower() or "running normally" in q.lower():
            break


def prepare(r: rcon.Rcon) -> None:
    for rule, value in (("spawn_mobs", "false"), ("advance_time", "false"), ("advance_weather", "false"),
                        ("spawn_monsters", "false"), ("send_command_feedback", "true")):
        r.cmd(f"gamerule {rule} {value}")
    r.cmd("time set noon")
    r.cmd("weather clear")
    x0, y0, z0 = w(-16, 0, -16)
    x1, y1, z1 = w(31, 0, 47)
    r.cmd(f"forceload add {x0} {z0} {x1} {z1}")


def clear(r: rcon.Rcon) -> None:
    x0, y0, z0 = w(-3, 0, -3)
    x1, y1, z1 = w(18, 14, 34)
    r.cmd(f"kill @e[type=!minecraft:player,x={x0},y={y0},z={z0},dx={x1 - x0},dy={y1 - y0},dz={z1 - z0}]")
    print(r.cmd(f"fill {x0} {y0} {z0} {x1} {y1} {z1} minecraft:air"))
    r.cmd(f"kill @e[type=minecraft:item]")


def build(r: rcon.Rcon, m: fm.Model) -> None:
    clear(r)
    cmds = setblock_commands(m, ORIGIN)
    errors = []
    for c in cmds:
        out = r.cmd(c)
        if "Changed the block" not in out:
            errors.append((c, out))
    print(f"{len(cmds)} setblock-Befehle, {len(errors)} ohne Änderung")
    for c, out in errors[:20]:
        print("  ", c, "->", out)
    time.sleep(10)  # Wasser (5 Ticks/Block) und Lava (30 Ticks) setzen lassen


def readback(r: rcon.Rcon, server_dir: Path, m: fm.Model, name="readback") -> dict:
    """Welt speichern und die Blöcke des Farmbereichs direkt aus den Region-Dateien lesen."""
    r.cmd("save-all flush")
    time.sleep(1.0)
    sx, sy, sz = m.size
    x0, y0, z0 = w(0, 0, 0)
    raw = anvil.read_blocks(server_dir / "world" / "dimensions" / "minecraft" / "overworld"
                            if (server_dir / "world" / "dimensions" / "minecraft" / "overworld" / "region").exists()
                            else server_dir / "world", x0, y0, z0, x0 + sx - 1, y0 + sy - 1, z0 + sz - 1)
    return {(x - x0, y - y0, z - z0): b for (x, y, z), b in raw.items()}


def compare(m: fm.Model, blocks: dict) -> list:
    diffs = []
    sx, sy, sz = m.size
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                want = m.get(x, y, z)
                have = blocks.get((x, y, z), AIR)
                if have.name == "minecraft:cave_air":
                    have = AIR
                if want != have:
                    diffs.append(((x, y, z), str(want), str(have)))
    return diffs


# ------------------------------------------------------------------ Simulation

def box(lo, hi):
    (x0, y0, z0), (x1, y1, z1) = w(*lo), w(*hi)
    return f"x={x0},y={y0},z={z0},dx={x1 - x0},dy={y1 - y0},dz={z1 - z0}"


BABY = '{type:"minecraft:entity_properties",entity:"this",predicate:{"minecraft:flags":{is_baby:true}}}'


def count(r, selector: str, baby: bool | None = None) -> int:
    if baby is not None:
        selector = selector[:-1] + (",tag=t_baby]" if baby else ",tag=!t_baby]")
    out = r.cmd(f"execute if entity {selector}")
    mt = re.search(r"count: (\d+)", out, re.IGNORECASE)
    if mt:
        return int(mt.group(1))
    return 1 if "Test passed" in out else 0


def tag_babies(r) -> None:
    r.cmd("tag @e remove t_baby")
    r.cmd(f"execute as @e[type=!minecraft:player] if predicate {BABY} run tag @s add t_baby")


def chest_items(r, pos) -> Counter:
    x, y, z = w(*pos)
    out = r.cmd(f"data get block {x} {y} {z} Items")
    c = Counter()
    for item in re.findall(r"\{[^{}]*id: \"minecraft:[a-z_]+\"[^{}]*\}", out):
        name = re.search(r'id: "minecraft:([a-z_]+)"', item).group(1)
        cnt = re.search(r"count: (\d+)", item)
        c[name] += int(cnt.group(1)) if cnt else 1
    return c


def summon(r, etype, pos, nbt="{}", n=1):
    x, y, z = w(*pos)
    for _ in range(n):
        r.cmd(f"summon minecraft:{etype} {x + 0.5} {y} {z + 0.5} {nbt}")


def report(r, m: fm.Model) -> dict:
    res = {}
    tag_babies(r)
    for key in ("cow_chest", "pig_chest", "chicken_chest"):
        total = Counter()
        for pos in m.notes[key]:
            total += chest_items(r, pos)
        res[key] = dict(total)
    for sp, z0 in (("cow", fm.COW_Z0), ("pig", fm.PIG_Z0)):
        for side, (xa, xb) in (("W", (1, 5)), ("O", (10, 14))):
            pen = f"@e[type=minecraft:{sp},{box((xa, fm.Y_PEN, z0 + 1), (xb, fm.Y_PEN + 2, z0 + 7))}]"
            grow = f"@e[type=minecraft:{sp},{box((xa, fm.Y_GROW, z0 + 1), (xb, fm.Y_BLADE, z0 + 7))}]"
            xs = 6 if side == "W" else 9
            kill = f"@e[type=minecraft:{sp},{box((xs, fm.Y_STREAM, z0 + 1), (xs, 6, z0 + 9))}]"
            res[f"{sp}_{side}"] = {
                "pen_adult": count(r, pen, False), "pen_baby": count(r, pen, True),
                "grow_adult": count(r, grow, False), "grow_baby": count(r, grow, True),
                "stream_adult": count(r, kill, False), "stream_baby": count(r, kill, True),
            }
    hens = f"@e[type=minecraft:chicken,{box((2, 3, fm.CHICKEN_Z - 1), (13, 5, fm.CHICKEN_Z - 1))}]"
    cells = f"@e[type=minecraft:chicken,{box((4, 2, fm.CHICKEN_Z), (11, 3, fm.CHICKEN_Z))}]"
    res["chicken"] = {"breeders_adult": count(r, hens, False), "breeders_baby": count(r, hens, True),
                      "cell_adult": count(r, cells, False), "cell_baby": count(r, cells, True)}
    res["all"] = {t: count(r, f"@e[type=minecraft:{t}]") for t in ("cow", "pig", "chicken", "item")}
    x0, y0, z0 = w(-2, 0, -2)
    x1, y1, z1 = w(17, 12, 33)
    res["fire"] = r.cmd(f"fill {x0} {y0} {z0} {x1} {y1} {z1} minecraft:air replace minecraft:fire")
    return res


def sim(r, m: fm.Model, args) -> dict:
    r.cmd("kill @e[type=minecraft:item]")
    # Elterntiere: Zuchtgänge voll besetzen (1 Tier pro Feld)
    for sp in ("cow", "pig"):
        notes = m.notes[f"{sp}_pen"]
        for (xa, y, z), (xb, _, _) in zip(notes[::2], notes[1::2]):
            step = 1 if xb >= xa else -1
            for x in range(xa, xb + step, step):
                summon(r, sp, (x, y, z), '{Tags:["parent"]}')
    rng = random.Random(1)
    for pos in m.notes["chicken_breeder"]:
        for _ in range(args.hens):
            summon(r, "chicken", pos, '{Tags:["parent"],EggLayTime:%d}' % rng.randint(20, args.eggtime))
    # Küken direkt in die Kükenzellen (Test des Brat-Mechanismus)
    for pos in m.notes["chicken_cell"]:
        summon(r, "chicken", (pos[0], pos[1] + 1, pos[2]), '{Age:-600}', n=2)
    time.sleep(1)
    print("Start:", json.dumps(report(r, m)))
    for rnd in range(args.rounds):
        for sp in ("cow", "pig"):
            r.cmd(f"data merge entity @e[type=minecraft:{sp},tag=parent,limit=1] {{}}")
            r.cmd(f"execute as @e[type=minecraft:{sp},tag=parent] run data merge entity @s {{Age:0,InLove:600}}")
        wait_ticks(r, args.round_ticks)
        print(f"Runde {rnd + 1}:", json.dumps(report(r, m)))
    wait_ticks(r, args.final_ticks)
    res = report(r, m)
    print("Ende:", json.dumps(res, indent=1))
    return res


def bilanz(r, m: fm.Model, args) -> dict:
    """Genaue Bilanz je Tierart: Geburten, erwachsen geworden, als Baby gestorben.

    Läuft mit erhöhter Tickrate statt /tick sprint, damit jedes Baby kurz vor dem Erwachsenwerden
    (Age >= -400) gesehen und markiert wird. Verschwindet ein Baby ohne diese Markierung, ist es als
    Baby gestorben (es hätte dann kein Fleisch geliefert)."""
    for sp in ("cow", "pig", "chicken", "item"):
        r.cmd(f"kill @e[type=minecraft:{sp}]")
    r.cmd("scoreboard objectives remove age")
    r.cmd("scoreboard objectives add age dummy")
    before = {sp: sum((chest_items(r, p) for p in m.notes[f"{sp}_chest"]), Counter()) for sp in ("cow", "pig")}
    for sp in ("cow", "pig"):
        notes = m.notes[f"{sp}_pen"]
        for (xa, y, z), (xb, _, _) in zip(notes[::2], notes[1::2]):
            step = 1 if xb >= xa else -1
            for x in range(xa, xb + step, step):
                summon(r, sp, (x, y, z), '{Tags:["parent"]}')
    births, grown = Counter(), Counter()

    def sample():
        for sp in ("cow", "pig"):
            sel = f"@e[type=minecraft:{sp},tag=!parent"
            births[sp] += count(r, f"{sel},tag=!b]")
            r.cmd(f"tag {sel},tag=!b] add b")
            r.cmd(f"execute as {sel},tag=b,tag=!near] store result score @s age run data get entity @s Age")
            near = f"{sel},tag=b,tag=!near,scores={{age=-400..}}]"
            grown[sp] += count(r, near)
            r.cmd(f"tag {near} add near")

    def run(ticks):
        t_end = time.time() + ticks / args.rate
        while time.time() < t_end:
            sample()
            time.sleep(0.2)

    r.cmd(f"tick rate {args.rate}")
    try:
        for _ in range(args.rounds):
            r.cmd("execute as @e[tag=parent] run data merge entity @s {Age:0,InLove:600}")
            run(args.round_ticks)
        run(args.final_ticks)
        sample()
    finally:
        r.cmd("tick rate 20")
    res = {}
    for sp in ("cow", "pig"):
        alive = count(r, f"@e[type=minecraft:{sp},tag=!parent]")
        after = sum((chest_items(r, p) for p in m.notes[f"{sp}_chest"]), Counter())
        res[sp] = {"geburten": births[sp], "erwachsen": grown[sp], "als_baby_gestorben": births[sp] - grown[sp] - alive,
                   "noch_lebend": alive, "eltern": count(r, f"@e[type=minecraft:{sp},tag=parent]"),
                   "kisten": dict(after - before[sp])}
    print("Bilanz:", json.dumps(res, ensure_ascii=False))
    return res


def firetest(r, args) -> str:
    """Lava-Brandtest: Feuer überall erlauben (ohne Spieler breitet sich Feuer sonst nicht aus) und die
    Zufallsticks stark erhöhen, damit jede Lava viele hundert Mal versucht, etwas anzuzünden."""
    r.cmd("gamerule fire_spread_radius_around_player -1")
    r.cmd(f"gamerule random_tick_speed {args.random_tick_speed}")
    wait_ticks(r, args.fire_ticks)
    r.cmd("gamerule random_tick_speed 3")
    r.cmd("gamerule fire_spread_radius_around_player 128")
    x0, y0, z0 = w(-2, 0, -2)
    x1, y1, z1 = w(17, 12, 33)
    return r.cmd(f"fill {x0} {y0} {z0} {x1} {y1} {z1} minecraft:air replace minecraft:fire")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server-dir", required=True, type=Path)
    ap.add_argument("--password", default="farmtest")
    ap.add_argument("step", choices=["build", "readback", "sim", "fire", "bilanz", "all"])
    ap.add_argument("--rate", type=int, default=200, help="Tickrate für die Bilanz")
    ap.add_argument("--random-tick-speed", type=int, default=1000)
    ap.add_argument("--fire-ticks", type=int, default=3000)
    ap.add_argument("--parents", type=int, default=10)
    ap.add_argument("--hens", type=int, default=4)
    ap.add_argument("--eggtime", type=int, default=6000)
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--round-ticks", type=int, default=6100)
    ap.add_argument("--final-ticks", type=int, default=26000)
    args = ap.parse_args()

    m = fm.build()
    r = rcon.connect(args.password)
    prepare(r)
    if args.step in ("build", "all"):
        build(r, m)
    if args.step in ("build", "readback", "all"):
        blocks = readback(r, args.server_dir, m)
        diffs = compare(m, blocks)
        print(f"Readback: {len(diffs)} Abweichungen")
        for d in diffs[:60]:
            print("  ", d)
    if args.step in ("fire", "all"):
        print("Brandtest:", firetest(r, args))
        diffs = compare(m, readback(r, args.server_dir, m))
        print(f"Blöcke nach dem Brandtest: {len(diffs)} Abweichungen")
        for d in diffs[:60]:
            print("  ", d)
    if args.step in ("sim", "all"):
        sim(r, m, args)
        blocks = readback(r, args.server_dir, m, "after")
        diffs = compare(m, blocks)
        print(f"Blöcke nach dem Test: {len(diffs)} Abweichungen")
        for d in diffs[:60]:
            print("  ", d)
    if args.step == "bilanz":
        bilanz(r, m, args)


if __name__ == "__main__":
    main()
