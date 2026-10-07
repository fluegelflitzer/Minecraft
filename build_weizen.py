"""Erzeugt die Litematica-Datei der Weizenfarm: python3 build_weizen.py"""
from pathlib import Path

from farm import litematic
from weizenfarm import checks, materials, model

OUT = Path(__file__).parent / "schematics" / "Weizenfarm_Hochhaus_14_Bauern.litematic"


def main() -> None:
    m = model.build()
    errors = checks.run_all(m)
    if errors:
        raise SystemExit("Prüfung fehlgeschlagen:\n  " + "\n  ".join(errors))
    OUT.parent.mkdir(exist_ok=True)
    litematic.write(
        m, OUT,
        name="Weizenfarm Hochhaus 14 Bauern",
        author="fluegelflitzer",
        description="Dorfbewohner-Weizen-/Brotfarm, 7 Etagen, 14 Bauern + 7 Sammler, Minecraft Java 26.3 (32x16x23)",
    )
    size, blocks = litematic.read_blocks(OUT)
    assert size == m.size and blocks == m.blocks, "Rücklese-Prüfung fehlgeschlagen"
    print(f"{OUT} geschrieben: {size[0]}x{size[1]}x{size[2]}, {len(blocks)} Blöcke")
    mat = materials.materials(m)
    for item, n in mat.most_common():
        print(f"  {n:5d}  {item}")
    for item, n in materials.extras(m).items():
        print(f"  {n:5d}  {item}")
    print(f"  Eisen gesamt: {materials.iron(mat)}, Kupfer: {materials.copper(mat)}")


if __name__ == "__main__":
    main()
