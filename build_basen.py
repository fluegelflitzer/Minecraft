"""Erzeugt die rustikalen Basen: python3 build_basen.py [name ...]

Für jede Basis: Prüfungen, schematics/Basis_*.litematic, bauplaene/*.json (Reihenfolge + Klick-Hinweise
für Bots) und die Materialliste auf der Konsole.
"""
import importlib
import sys
from pathlib import Path

from basen import bauplan, material, pruefung, zustaende
from farm import litematic

ROOT = Path(__file__).parent
BASEN = {
    "starterhuette": "Basis_1_Starterhuette_Fichtenkate.litematic",
    "blockhaus": "Basis_2_Blockhaus_mit_Veranda.litematic",
    "gehoeft": "Basis_3_Gehoeft.litematic",
}
STAMP = 1_791_878_400_000  # fester Zeitstempel (2026-10-13) -> gleiche Datei bei gleichem Modell


def build(key: str) -> None:
    fname = BASEN[key]
    m = importlib.import_module(f"basen.{key}").build()
    zustaende.finalisieren(m)
    errors = pruefung.run_all(m)
    if errors:
        raise SystemExit(f"{key}: Prüfung fehlgeschlagen:\n  " + "\n  ".join(errors))
    out = ROOT / "schematics" / fname
    litematic.write(m, out, name=m.titel, author="fluegelflitzer", description=m.beschreibung + " (Minecraft Java 26.3)",
                    timestamp_ms=STAMP)
    size, blocks = litematic.read_blocks(out)
    assert size == m.size and blocks == m.blocks, "Rücklese-Prüfung fehlgeschlagen"
    steps, plan_errors = bauplan.plan(m)
    assert not plan_errors
    mat = material.liste(steps)
    plan_path = ROOT / "bauplaene" / f"{key}.json"
    plan_path.parent.mkdir(exist_ok=True)
    plan_path.write_text(bauplan.to_json(m, steps, mat))
    sx, sy, sz = m.size
    dark, lit, ground = pruefung.dunkle_stellen(m)
    print(f"{out.name}: {sx}x{sy}x{sz}, {len(blocks)} Blöcke, {len(steps)} Bauschritte, "
          f"Gelände beleuchtet {lit}/{ground}")
    c = material.zaehlen(steps)
    for d in mat:
        print(f"  {d['anzahl']:5d}  {d['name']}" + (f"  ({d['werkzeug']})" if "werkzeug" in d else ""))
    print(f"  Eisen gesamt: {material.eisen(c):.1f} Barren")


def main() -> None:
    for key in sys.argv[1:] or BASEN:
        build(key)


if __name__ == "__main__":
    main()
