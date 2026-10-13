"""Lädt den Minecraft-26.3-Client von Mojang und entpackt Blockmodelle und Texturen nach tools/vorschau/.assets.

Die Texturen gehören Mojang und werden deshalb nicht ins Repo eingecheckt, sondern lokal geholt.
  python3 tools/vorschau/assets_holen.py
"""
from __future__ import annotations

import io
import json
import urllib.request
import zipfile
from pathlib import Path

VERSION = "26.3"
OUT = Path(__file__).parent / ".assets"
MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
PREFIXES = ("assets/minecraft/blockstates/", "assets/minecraft/models/block/", "assets/minecraft/textures/block/")


def _get(url: str) -> bytes:
    with urllib.request.urlopen(url) as r:
        return r.read()


def main() -> None:
    manifest = json.loads(_get(MANIFEST))
    url = next(v["url"] for v in manifest["versions"] if v["id"] == VERSION)
    client = json.loads(_get(url))["downloads"]["client"]["url"]
    print("lade", client)
    jar = zipfile.ZipFile(io.BytesIO(_get(client)))
    n = 0
    for name in jar.namelist():
        if name.startswith(PREFIXES) and not name.endswith("/"):
            target = OUT / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(jar.read(name))
            n += 1
    print(f"{n} Dateien nach {OUT}")


if __name__ == "__main__":
    main()
