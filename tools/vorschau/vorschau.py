"""Vorschaubild einer Basis rendern (Original-Blockmodelle und -Texturen aus dem 26.3-Client).

  python3 tools/vorschau/assets_holen.py            # einmalig: Client-Assets laden
  (cd tools/vorschau && npm install)                 # einmalig: three.js + Playwright
  python3 tools/vorschau/vorschau.py blockhaus --ansicht sw --zoom 1.8 -o blockhaus.png
  python3 tools/vorschau/vorschau.py gehoeft --ansicht top --schnitt 6   # Draufsicht, alles über y=6 weggeschnitten
"""
from __future__ import annotations

import argparse
import importlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

import quads  # noqa: E402
from basen import zustaende  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("basis")
    ap.add_argument("--ansicht", default="se", choices=["se", "sw", "ne", "nw", "top", "s", "n"])
    ap.add_argument("--schnitt", type=int, help="nur Blöcke bis zu dieser Höhe zeigen")
    ap.add_argument("--zoom", default="1.5")
    ap.add_argument("--breite", default="1400")
    ap.add_argument("--hoehe", default="900")
    ap.add_argument("--rand", type=int, default=3, help="Grasrand um die Basis")
    ap.add_argument("-o", "--out", default=None)
    a = ap.parse_args()
    m = importlib.import_module(f"basen.{a.basis}").build()
    zustaende.finalisieren(m)
    blocks = {p: b for p, b in m.blocks.items() if a.schnitt is None or p[1] <= a.schnitt}
    scene = HERE / ".szene" / a.basis
    quads.export(blocks, HERE / ".assets", scene, size=m.size, ground_margin=a.rand)
    out = Path(a.out or f"{a.basis}_{a.ansicht}.png").resolve()
    subprocess.run(["node", str(HERE / "render.mjs"), str(scene), str(out), a.ansicht, a.breite, a.hoehe, a.zoom],
                   check=True, cwd=HERE)
    print(out)


if __name__ == "__main__":
    main()
