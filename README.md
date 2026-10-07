# Brat-Tierfarm XL – Huhn, Kuh, Schwein (Minecraft Java 26.3, Litematica)

Litematica-Vorlage für eine Survival-Farm, die Tiere tötet, ohne den Bestand zu verringern, und das
Fleisch dabei **gleich gebraten** liefert (Lava-Tod → gebratene Drops).

**Datei:** [`schematics/Brat-Tierfarm-XL_Huhn_Kuh_Schwein.litematic`](schematics/Brat-Tierfarm-XL_Huhn_Kuh_Schwein.litematic)

| | |
|---|---|
| Minecraft | Java Edition **26.3** (Litematica-Format Version 7, DataVersion 5023) |
| Größe | 16 × 13 × 32 Blöcke (genau **1 × 2 Chunks**, 13 hoch) |
| Huhn | vollautomatisch (Eier → Spender → Küken → gebraten) |
| Kuh / Schwein | Futterstation: du fütterst per Rechtsklick, alles Weitere läuft automatisch |
| Lager | je Tierart eigene Doppelkisten im Kellergang (kein Sortierer nötig) |

> ⚠️ **Stand: Version 1, noch nicht vollständig.** Die Hühnerseite ist getestet und funktioniert.
> Bei Kühen und Schweinen bleibt im Test noch ein Teil der ausgewachsenen Tiere im Aufzuchtbecken
> hängen (siehe [Bekannte Probleme](#bekannte-probleme)). Mit dem Bau der Kuh-/Schweine-Seite besser
> auf Version 2 warten.

---

## 1. Importieren und platzieren

1. Litematica + MaLiLib für 26.3 installieren.
2. Die `.litematic`-Datei nach `.minecraft/schematics/` kopieren.
3. Im Spiel: `M` → *Load Schematics* → Datei wählen → *Load*.
4. Platzierung so verschieben, dass
   - **Ebene 0 (die Kisten) auf Bodenhöhe** liegt (eine Ebene über Gras/Erde),
   - die Farm an einer **Chunkgrenze** ausgerichtet ist (F3 + G zeigt Chunkgrenzen). Sie belegt dann
     genau 1 × 2 Chunks.
5. Den Boden unter der Farm vorher ebnen. Der Kellergang benutzt den natürlichen Boden als Fußboden.

Koordinaten in dieser Anleitung sind **relativ zur Schematic**:
x = nach Osten (0–15), y = Höhe (0 = Kisten), z = nach Süden (0–31).

## 2. Aufbau im Überblick

```
Draufsicht (Norden oben)
z  0–10   KUH      [Zuchtgänge West] [Graben] [Laufsteg + Kellergang] [Graben] [Zuchtgänge Ost]
z 10–20   SCHWEIN  gleich aufgebaut
z 21–31   HUHN     2 Brutmodule (West/Ost), Galerie, Rampe (Ostseite) und Treppe zum Laufsteg
```

### Kuh und Schwein: so funktioniert es

```
Schnitt durch eine Gehegehälfte
y10–11  Zuchtgänge: je 1 Block breit zwischen Vollblock + Stufe (1,5 hoch, Tiere springen nicht drüber)
y9      Boden der Zuchtgänge = offene Falltüren (Klappe an der Nordkante, Spalt 13/16)
        → Erwachsene (0,9 breit) stehen auf der Klappe, Babys (0,45) fallen sofort durch
y8      Beckendecke mit Fallöffnung unter jedem Zuchtgang
y7      Wasserklinge (fließt nach Osten) + Fallstreifen aus Falltüren unter den Zuchtgängen
y6      Aufzuchtbecken: Babys berühren das Wasser nicht und bleiben stehen;
        ausgewachsene Tiere ragen ins Wasser und werden zum Graben (x6 bzw. x9) geschoben
y2–y5   Graben → flacher Tötungsstrom (y2) → Lavazelle (Lava auf y3): Kopf in der Lava → gebraten
y1/y0   2 Trichter → Doppelkiste (im Kellergang)
```

- Ein Baby entsteht immer mittig über dem Spalt, weil die Eltern im 1 Block breiten Gang mittig
  stehen. Es fällt deshalb sofort nach unten. Die Elterntiere bleiben immer oben.
- Wasser und Lava berühren sich nirgends: Dazwischen sitzt ein Schild, das keine Flüssigkeit durchlässt
  und keine Kollision hat.
- Die Drops steigen höchstens 0,63 Blöcke hoch, die Lava beginnt erst 1 Block über dem Boden. Es
  verbrennt nichts.

### Huhn: so funktioniert es

- Die Zuchthennen stehen in einer Reihe aus 3 Trichtern (je Modul, Höhe y3). Ihre Eier laufen über die
  Trichterkette in einen Spender.
- Ein Komparator liest den Trichter über dem Spender. Jedes durchlaufende Ei erzeugt einen Puls, und der
  Spender verschießt das vorherige Ei in die Kükenzelle. Die Schaltung kann nicht hängen bleiben.
- In der Kükenzelle stehen die Küken auf einer Steinsäge (9/16 hoch) unter einem Lavakessel. Küken
  passen darunter. Ein ausgewachsenes Huhn ragt in den Kessel und stirbt gebraten.
- Die Drops stoßen am Kesselboden an und fallen über 2 Trichter in die Doppelkiste.

## 3. Material (exakt aus der Schematic)

| Material | Anzahl | Hinweis |
|---|---:|---|
| Bruchstein | 1 797 | |
| Bruchsteinstufe | 226 | |
| Eichenfalltür | 155 | Holz; nicht brennbar |
| Fackel | 53 | |
| Bruchsteinmauer | 46 | |
| Glas | 42 | |
| Eichenschild (Wandschild) | 32 | wasser-/lavadicht ohne Kollision |
| Wasserquelle | 24 | aus einer unendlichen Wasserquelle schöpfen |
| **Trichter** | **18** | **90 Eisen** |
| Kiste | 12 | 6 Doppelkisten |
| Bruchsteintreppe | 11 | Rampe und Treppe |
| Eichenzauntor | 8 | |
| **Lava** | **4 + 4** | **8 Eimer Lava** (4 Lavazellen + 4 Kessel) |
| Kessel | 4 | 28 Eisen |
| Steinsäge | 4 | 4 Eisen |
| Leiter | 4 | |
| Spender | 2 | je 1 Bogen + 1 Redstone |
| **Komparator** | **2** | **2 Netherquarz** |
| Redstone-Staub | 2 | |

**Seltenes Material insgesamt:** ca. 122 Eisen und 2 Netherquarz. Alles andere ist Bruchstein, Holz,
Glas und Wasser.

## 4. Bauen (Reihenfolge)

1. **Von unten nach oben bauen.** Litematicas *Easy Place* sorgt für die richtige Ausrichtung von
   Falltüren, Schildern, Trichtern und Kisten. Mit dem *Schematic Verifier* prüfen.
2. **Falltüren genau wie in der Vorlage setzen.** Die Gitter-Falltüren der Zuchtgänge und Fallstreifen
   sind *offen*, mit der Klappe an der Nordkante. Die Bodenfalltüren sind *geschlossen* (untere Hälfte).
3. **Schilder vor dem Wasser** setzen (Graben y7 und über dem letzten Stromfeld y3).
4. **Wasser setzen.** Im Becken an die Westkante (Ostseite gespiegelt), im Tötungsstrom am Nordende. Das
   fließende Wasser entsteht von selbst.
5. **Lava ganz zum Schluss**, erst die 4 Lavazellen, dann die 4 Kessel befüllen.
6. Der Verifier zeigt fließendes Wasser erst grün, wenn es fertig geflossen ist.

## 5. Befüllen

**Wege:** Rampe an der Ostseite (x15, z26–30) → Galerie (y4) → Treppe (x7, z21–26) → Laufsteg (y10)
→ Futtergang (in jeder Gehegehälfte bei z = 3 bzw. 13). Vom Kellergang (Eingang im Norden) führt eine
Leiter mit Falltür bei x8/z27 auf die Galerie.

**Kühe / Schweine:**
- Tiere mit Weizen bzw. Karotten über Rampe → Galerie → Treppe → Laufsteg → Futtergang führen.
- Im Futtergang durch das Zauntor in einen Zuchtgang lassen.
- Pro Zuchtgang passen 5 Tiere, pro Hälfte also 10, pro Tierart 20 Elterntiere.

**Hühner:**
- Hennen in die Zuchtpens (oben offen, Glasrand) bringen: Eier von der Galerie hineinwerfen oder Hühner
  hineinlocken.
- Nachzüchten im Pen mit Samen.
- **Höchstens ~20 Hennen pro Trichterfeld**, also ca. 60 pro Modul (ab 24 Tieren auf einem Feld tötet
  Entity-Cramming).

## 6. Bedienung und Ertrag

- **Kühe/Schweine:** Vom Futtergang (oder vom Laufsteg für den inneren Gang) per Rechtsklick füttern;
  man reicht über die Stufen-Wand.
  - Alle 5 Minuten möglich (Zucht-Abklingzeit).
  - Bei vollem Besatz entstehen pro Fütterung etwa 10 Babys je Tierart. Nach 20 Minuten Wachstum
    landen pro Tier im Schnitt ~2 gebratene Steaks bzw. Koteletts in der Kiste (Kuh zusätzlich ~1 Leder).
- **Huhn:** Ab 6 Hennen pro Modul geht es von allein. Jede Henne legt etwa alle 5–10 Minuten ein Ei, aus
  jedem 8. Ei schlüpft ein Küken. Mit ~60 Hennen pro Modul ergibt das rund 60 gebratene Hähnchen pro
  Stunde und Modul, dazu Federn.
- **Kisten:** im Kellergang (x7–8, y0–1).

| Tierart | Kisten (x, y, z) |
|---|---|
| Kuh | (6,0,8–9) und (9,0,8–9) |
| Schwein | (6,0,18–19) und (9,0,18–19) |
| Huhn | (6,0,26–27) und (9,0,26–27) |

## 7. Getestet auf einem echten 26.3-Server

Alle Werte stammen aus automatischen Läufen auf einem headless Minecraft-26.3-Server. Die Farm wurde dort
Block für Block per `/setblock` gebaut. Es gab 4 × 6 Elterntiere je Art, 24 Hennen und drei
Fütterungsrunden, danach rund 44 000 Ticks Zeitraffer.

| Prüfpunkt | Ergebnis |
|---|---|
| Gebauter Zustand = Schematic (inkl. Mauerverbindungen, Kisten, Wasserstände) | ✅ 0 Abweichungen |
| Blöcke nach dem Test unverändert (keine Lecks, kein Obsidian/Bruchstein aus Wasser+Lava) | ✅ |
| Feuer | ✅ keins |
| Elterntiere bleiben vollzählig | ✅ alle (Kuh, Schwein, Hennen) |
| Babys fallen aus den Zuchtgängen ins Becken | ✅ 100 % |
| Huhn: nur gebratenes Fleisch | ✅ (8–16 Hähnchen + Federn je Testlauf) |
| Kuh/Schwein: gebratenes Fleisch, ~2 pro Tier | ✅ für alle Tiere, die die Lava erreichen |
| Kuh/Schwein: jedes ausgewachsene Tier erreicht die Lava | ❌ siehe unten |

## Bekannte Probleme

- **Ausgewachsene Kühe/Schweine bleiben im Aufzuchtbecken hängen.** Im letzten Testlauf erreichten etwa
  die Hälfte die Lava. Die anderen wurden unter den Fallstreifen (Falltür-Klappen in der Wasserschicht)
  erwachsen, verhaken sich an der Klappe und werden nicht vom Wasser erfasst. Sie sterben nicht, sammeln
  sich aber im Becken. Daran wird gearbeitet (Version 2).
- **Vereinzelt rohes Rindfleisch:** In einem Lauf kamen 2 rohe statt gebratene Stücke an. Die Ursache ist
  noch nicht geklärt.
- **Kühe und Schweine** lassen sich in Vanilla nur per Hand füttern. Die Futterstation ist daher
  halbautomatisch.

---

## Für Bastler: Generator und Test

Die Schematic wird aus Python-Code erzeugt (nur Standardbibliothek, Python ≥ 3.10):

```bash
python3 build.py        # schreibt schematics/Brat-Tierfarm-XL_Huhn_Kuh_Schwein.litematic
```

| Datei | Inhalt |
|---|---|
| `farm/model.py` | Blockmodell (Module Kuh/Schwein/Huhn, Wege), berechnet Mauer-/Kisten-/Redstone-Zustände und den Wasserfluss |
| `farm/litematic.py` | Writer/Reader für `.litematic` (Version 7, Bit-Packing wie `LitematicaBitArray`) |
| `farm/nbt.py` | minimaler NBT-Reader/Writer |
| `farm/blocks.py`, `farm/data/blocks_26.3.json` | Blockzustände, geprüft gegen die Blockliste von 26.3 |
| `farm/commands.py` | dasselbe Modell als `/setblock`-Befehle |
| `tests/ingame/run_test.py` | Ingame-Test per RCON: bauen, zurücklesen (Region-Dateien), Tiere simulieren, Kisten auswerten |

Ingame-Test (eigener Testserver mit `enable-rcon=true`, `rcon.password=farmtest`,
`pause-when-empty-seconds=0`, Flachwelt):

```bash
python3 tests/ingame/run_test.py --server-dir <server-ordner> all
```
