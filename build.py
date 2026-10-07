"""Erzeugt die Litematica-Datei der Brat-Tierfarm XL: python3 build.py"""
from pathlib import Path

from farm import litematic, model

OUT = Path(__file__).parent / "schematics" / "Brat-Tierfarm-XL_Huhn_Kuh_Schwein.litematic"


def main() -> None:
    m = model.build()
    OUT.parent.mkdir(exist_ok=True)
    litematic.write(
        m, OUT,
        name="Brat-Tierfarm XL",
        author="fluegelflitzer",
        description="Huhn/Kuh/Schwein, Lava-Kochfarm fuer Minecraft Java 26.3 (16x32)",
    )
    size, blocks = litematic.read_blocks(OUT)
    assert size == m.size and blocks == m.blocks, "Rücklese-Prüfung fehlgeschlagen"
    print(f"{OUT} geschrieben: {size[0]}x{size[1]}x{size[2]}, {len(blocks)} Blöcke")


if __name__ == "__main__":
    main()
