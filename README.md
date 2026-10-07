# Brat-Tierfarm XL – Huhn, Kuh, Schwein (Minecraft Java 26.3, Litematica)

> **Weitere Farm in diesem Repo:** [Weizenfarm-Hochhaus mit 14 Bauern (Brot/Weizen, 2×1 Chunks, 23 hoch)](WEIZENFARM.md)

Litematica-Vorlage für eine Survival-Farm. Sie tötet Tiere, ohne den Bestand zu verringern, und liefert
das Fleisch **gleich gebraten**, weil die Tiere durch Lava sterben.

**Datei:** [`schematics/Brat-Tierfarm-XL_Huhn_Kuh_Schwein.litematic`](schematics/Brat-Tierfarm-XL_Huhn_Kuh_Schwein.litematic)

| | |
|---|---|
| Minecraft | Java Edition **26.3** (Litematica-Format Version 7, DataVersion 5023) |
| Größe | 16 × 13 × 32 Blöcke (genau **1 × 2 Chunks**, 13 hoch) |
| Huhn | vollautomatisch: Eier → Werfer → Küken → gebraten |
| Kuh / Schwein | Futterstation: du fütterst per Rechtsklick, alles Weitere läuft automatisch |
| Lager | je Tierart eigene Doppelkisten im Kellergang, kein Sortierer nötig |

> **Stand: Version 2, im Spiel getestet.** Die Farm wurde auf einem echten 26.3-Server Block für Block
> gebaut und mit Tieren durchgespielt. Dabei gab es nur gebratenes Fleisch, keine verbrannten Drops,
> kein als Baby gestorbenes Tier, kein Feuer und keine hängenden Tiere (Details unter
> [Testergebnisse](#7-getestet-auf-einem-echten-263-server)). Was der automatische Test *nicht*
> abdecken kann, steht unter [Grenzen](#grenzen).

---

## 1. Importieren und platzieren

1. Litematica + MaLiLib für 26.3 installieren.
2. Die `.litematic`-Datei nach `.minecraft/schematics/` kopieren.
3. Im Spiel: `M` → *Load Schematics* → Datei wählen → *Load*.
4. Platzierung so verschieben, dass
   - **Ebene 0 (die Kisten) auf Bodenhöhe** liegt, also eine Ebene über Gras/Erde,
   - die Farm an einer **Chunkgrenze** ausgerichtet ist (F3 + G zeigt Chunkgrenzen). Sie belegt dann
     genau 1 × 2 Chunks.
5. Den Boden unter der Farm vorher ebnen. Der Kellergang benutzt den natürlichen Boden als Fußboden.

Koordinaten in dieser Anleitung sind **relativ zur Schematic**:
x = nach Osten (0–15), y = Höhe (0 = Kisten), z = nach Süden (0–31).

## 2. Aufbau im Überblick

```
Draufsicht (Norden oben)
z  0–9    KUH      [Zuchtgänge West] [Graben] [Laufsteg + Kellergang] [Graben] [Zuchtgänge Ost]
z 10–19   SCHWEIN  gleich aufgebaut
z 21–31   HUHN     2 Brutmodule (West/Ost), Galerie, Rampe (Ostseite) und Treppe zum Laufsteg
```

### Kuh und Schwein: so funktioniert es

```
Schnitt durch eine Gehegehälfte
y10–11  2 Zuchtgänge je 5 Tiere, 1 Block breit; Wände Vollblock + Stufe (1,5 hoch, Tiere springen
        nicht drüber). Dazwischen das Futterdeck: Du stehst 1 Block höher und fütterst über die Stufe.
y9      Boden der Zuchtgänge = offene Falltüren (Spalt 13/16)
        → Erwachsene (0,9 breit) stehen auf der Klappe, Babys (0,45) fallen sofort durch
y8      Beckendecke mit Fallöffnung unter jedem Zuchtgang
y6–7    Aufzuchtbecken: Babys wachsen hier auf. Darüber liegt die Wasserklinge (y7, fließt nach
        Osten). Babys sind zu klein, um sie im Stehen zu berühren. Ausgewachsene Tiere ragen hinein und
        werden in den Graben geschoben. (Springt ein Baby hinein, landet es auch im Strom und wartet
        dort – siehe Tötungsstelle.)
y3–6    Graben (x6 bzw. x9)
y2      flacher Tötungsstrom → Tötungsstelle (siehe unten)
y1/y0   2 Trichter → Doppelkiste (im Kellergang)
```

- **Babys:** Die Eltern stehen im 1 Block breiten Gang mittig, deshalb entsteht ein Baby immer über
  dem Spalt und fällt sofort ins Becken. Die Elterntiere bleiben immer oben.
- **Fallstreifen:** Unter jedem Zuchtgang führt ein trockener Fallstreifen ins Becken. Offene Falltüren
  an der Wand sorgen dafür, dass ein Tier, das dort erwachsen wird, in die Wasserklinge geschoben wird.
  - Kuhbecken: Boden aus Stein mit Standschildern darauf (die Schilder halten das Wasser).
  - Schweinebecken: Bruchsteinstufen; im Fallstreifen ein Grat aus Bruchsteinmauern.
- **Tötungsstelle:** Das Tier steht im letzten Wasserfeld und ragt nur knapp in die Lavazelle. Dort
  hält es ein Sperrblock auf, über dem die Lava liegt:
  - Kühe: ein **Schleifstein** (sein Rad beginnt 0,125 hinter der Kante);
  - Schweine: ein quer gestellter **Amboss**. Sein Sockel hebt das Schwein um 0,25 an, sodass der Kopf
    die Lava erreicht. Das Oberteil beginnt 0,1875 hinter der Kante.
  - Beide Abstände sind kleiner als eine halbe Babybreite. Ein Kalb oder Ferkel, das in den Strom
    geraten ist, kommt deshalb mit seinem Mittelpunkt nie in die Lavazelle. Dort würde es nämlich
    springen und mit dem Kopf in die Lava geraten. So wartet es gefahrlos, bis es erwachsen ist.
  - Ein Tier, das Lava berührt, will darin nach oben schwimmen. Die **Decke** über dem letzten
    Wasserfeld verhindert das: bei Kühen eine obere Bruchsteinstufe, bei Schweinen ein seitlich
    zeigender Trichter (er dient nur als Decke mit genau passender Unterkante).
  - Darum sterben die Tiere immer knapp über dem Boden. Ihre Drops steigen höchstens bis 2,99 Blöcke
    über Ebene 0, die Lava beginnt erst bei 3,0. **Es kann nichts verbrennen.** Das gilt auch, wenn der
    Trichter gerade beschäftigt ist und ein Drop ein paar Ticks liegen bleibt.
- **Wasser und Lava** berühren sich nirgends. Stufe, Trichter, Schleifstein, Amboss, Schilder und
  Falltüren lassen keine Flüssigkeit hinein.

### Huhn: so funktioniert es

- Die Zuchthennen stehen in einer Reihe aus 3 Trichtern (je Modul, Höhe y3). Ihre Eier laufen über die
  Trichterkette in einen Werfer.
- Ein Komparator liest den Trichter über dem Werfer. Jedes durchlaufende Ei erzeugt einen Puls, und der
  Werfer verschießt das vorherige Ei in die Kükenzelle. Die Schaltung kann nicht hängen bleiben.
- In der Kükenzelle stehen die Küken auf einer Steinsäge (9/16 hoch) unter einem Lavakessel. Küken
  passen darunter, ein ausgewachsenes Huhn ragt in den Kessel und stirbt gebraten.
- Die Drops stoßen am Kesselboden an und fallen über 2 Trichter in die Doppelkiste.

## 3. Material (exakt aus der Schematic)

| Material | Anzahl | Hinweis |
|---|---:|---|
| Bruchstein | 1 777 | |
| Bruchsteinstufe | 184 | |
| Eichenfalltür | 121 | |
| Eichenschild | 78 | Stand- und Wandschilder; wasserdicht ohne Kollision |
| Bruchsteinmauer | 66 | |
| Fackel | 45 | |
| Glas | 42 | |
| Wasserquelle | 24 | aus einer unendlichen Wasserquelle schöpfen |
| **Trichter** | **20** | **100 Eisen** (2 davon nur als Decke an den Schweine-Tötungsstellen) |
| Kiste | 12 | 6 Doppelkisten |
| Eichenzauntor | 12 | |
| Bruchsteintreppe | 11 | Rampe und Treppe |
| **Lava** | **4 + 4** | **8 Eimer Lava** (4 Tötungsstellen + 4 Kessel) |
| Kessel | 4 | 28 Eisen |
| Steinsäge | 4 | 4 Eisen |
| Leiter | 4 | |
| Schleifstein | 2 | Tötungsstellen Kuh |
| **Amboss** | **2** | **62 Eisen**, Tötungsstellen Schwein |
| Werfer | 2 | je 7 Bruchstein + 1 Bogen + 1 Redstone (nicht verwechseln mit dem Spender ohne Bogen – der lässt Eier nur fallen) |
| **Komparator** | **2** | **2 Netherquarz** |
| Redstone-Staub | 2 | |

**Seltenes Material insgesamt:** 194 Eisen und 2 Netherquarz. Alles andere ist Bruchstein, Holz,
Glas und Wasser.

## 4. Bauen (Reihenfolge)

1. **Von unten nach oben bauen.** Litematicas *Easy Place* sorgt für die richtige Ausrichtung von
   Falltüren, Schildern, Trichtern, Stufen und Kisten. Mit dem *Schematic Verifier* prüfen.
2. **Ausrichtung genau wie in der Vorlage** (der Verifier zeigt Abweichungen):
   - Die Gitter-Falltüren der Zuchtgänge und Fallstreifen sind *offen*.
   - Über dem letzten Stromfeld der Kühe liegt eine *obere* Stufe.
   - Die Schleifsteine (Kuh) stehen *auf dem Boden*, das Rad in Nord-Süd-Richtung.
   - Die Ambosse (Schwein) liegen *quer* (Ost-West), sonst kommt das Schwein nicht an die Lava.
   - Der Decken-Trichter über dem letzten Stromfeld der Schweine zeigt *zur Seite* in den Kern.
3. **Alles Trockene zuerst**: Schilder (Becken, Graben) sowie Stufe, Trichter, Schleifstein und Amboss
   an den Tötungsstellen.
4. **Wasser setzen**:
   - Becken: Quellen an der Außenkante (x1 bzw. x14), aber nicht in den Fallstreifen.
   - Tötungsstrom: Quelle am Nordende.
   - Das fließende Wasser entsteht von selbst.
5. **Lava ganz zum Schluss**: erst die 4 Tötungsstellen (über Schleifstein bzw. Amboss), dann die
   4 Kessel befüllen.
6. Der Verifier zeigt fließendes Wasser erst grün, wenn es fertig geflossen ist.

## 5. Befüllen

**Wege:** Rampe an der Ostseite (x15, z26–30) → Galerie (y4) → Treppe (x7, z21–26) → Laufsteg (y10)
→ Futterdeck (in jeder Gehegehälfte bei z = 3–5 bzw. 13–15). Vom Kellergang (Eingang im Norden) führt
eine Leiter mit Falltür bei x8/z27 auf die Galerie.

**Kühe / Schweine:**
- Tiere mit Weizen bzw. Karotten (oder an der Leine) über Rampe → Galerie → Treppe → Laufsteg →
  Futterdeck führen.
- Durch das Zauntor im Futterdeck in einen Zuchtgang lassen, danach das Tor schließen.
- Pro Zuchtgang 5 Tiere, pro Hälfte 10, pro Tierart 20 Elterntiere.

**Hühner:**
- Hennen in die Zuchtpens bringen (oben offen, Glasrand): Eier von der Galerie hineinwerfen oder Hühner
  hineinlocken.
- Nachzüchten im Pen mit Samen.
- **Höchstens ~20 Hennen pro Trichterfeld**, also ca. 60 pro Modul. Ab 24 Tieren auf einem Feld tötet
  Entity-Cramming.

## 6. Bedienung und Ertrag

- **Kühe/Schweine:** Vom Futterdeck aus per Rechtsklick füttern. Du stehst 1 Block höher als die
  Tiere und reichst über die Stufe; zur Not stellst du dich auf die Stufe.
  - Füttern ist alle 5 Minuten möglich (Zucht-Abklingzeit).
  - Pro Fütterung entstehen etwa 8–10 Babys je Tierart. 20 Minuten später landen pro Tier im Schnitt
    2 gebratene Steaks bzw. Koteletts in der Kiste (Kuh zusätzlich 1 Leder).
  - Wer alle 5 Minuten füttert, bekommt etwa 200–240 Steaks bzw. Koteletts pro Stunde und Tierart.
- **Huhn:** Läuft ab 6 Hennen pro Modul von allein.
  - Jede Henne legt etwa alle 5–10 Minuten ein Ei, aus jedem 8. Ei schlüpft ein Küken.
  - Mit ~60 Hennen pro Modul ergibt das rund 65 gebratene Hähnchen pro Stunde und Modul, dazu Federn.
- **Kisten:** im Kellergang (x7–8, y0–1).

| Tierart | Kisten (x, y, z) |
|---|---|
| Kuh | (6,0,8–9) und (9,0,8–9) |
| Schwein | (6,0,18–19) und (9,0,18–19) |
| Huhn | (6,0,26–27) und (9,0,26–27) |

## 7. Getestet auf einem echten 26.3-Server

Alle Werte stammen aus automatischen Läufen auf einem headless Minecraft-26.3-Server
(`tests/ingame/run_test.py`). Die Farm wurde dort Block für Block per `/setblock` gebaut und
zurückgelesen.

| Prüfpunkt | Ergebnis |
|---|---|
| Gebauter Zustand = Schematic (inkl. Mauerverbindungen, Kisten, Wasserstände) | ✅ 0 Abweichungen |
| Datei unabhängig mit *litemapy* gelesen | ✅ 0 Abweichungen |
| Brandtest: Feuer überall erlaubt, Zufallsticks ×333, 3000 Ticks (Kontrolle: Holz neben Lava brennt ab) | ✅ kein Feuer, keine Blockänderung |
| Statische Prüfung: Wasser und Lava berühren sich nicht, keine Stelle, an der Lava Feuer legen kann | ✅ |
| Kuh: Tod mit den Füßen bei höchstens 2,10 (Lava ab 3,0), Drops kommen höchstens bis 2,83 | ✅ gemessen |
| Schwein: Tod mit den Füßen bei höchstens 2,35, Drops kommen höchstens bis 2,99 | ✅ gemessen |
| Schweine einzeln: jedes Tier liefert 1–3 gebratene Koteletts, keins geht leer aus | ✅ 30 von 30 |
| Schweine im Gedränge (Amboss-Stelle, 4 Läufe, 205 Tiere) | ✅ 1,91 Koteletts/Tier (erwartet 2), nur gebraten |
| Kühe (Stelle mit gleicher Decke, 115 Tiere) | ✅ Steaks und Leder im Erwartungswert, nur gebraten |
| **Bilanz** mit 4 Fütterungsrunden: Kuh 37 Geburten → 37 erwachsen und verarbeitet, 0 als Baby gestorben | ✅ |
| **Bilanz**: Schwein 39 Geburten → 39 erwachsen und verarbeitet, 0 als Baby gestorben | ✅ |
| Davon im Tötungsstrom gewartet, bis sie erwachsen waren: 18 Kälber, 19 Ferkel | ✅ keins gestorben |
| Elterntiere bleiben vollzählig (20 Kühe, 20 Schweine) | ✅ |
| Gesamtsimulation (4 Fütterungsrunden + 22 Minuten Zeitraffer, dazu 24 Hennen): am Ende nur noch die Elterntiere, kein Tier hängt fest, kein Gegenstand liegt herum | ✅ |
| Kisten danach: 74 gebratene Steaks + 40 Leder, 97 gebratene Koteletts, 7 gebratene Hähnchen + 7 Federn, **kein rohes Fleisch** | ✅ |
| Hennen bleiben vollzählig, Küken werden erst als Huhn gebraten | ✅ |
| Blöcke nach der Simulation unverändert (keine Lecks, kein Obsidian/Bruchstein aus Wasser + Lava) | ✅ |

## Grenzen

- **Kühe und Schweine** lassen sich in Vanilla nur per Hand füttern. Die Futterstation ist daher
  halbautomatisch.
- **Nicht automatisch getestet:**
  - das Füttern durch einen echten Spieler: Die Reichweite ist nachgerechnet, im Test wurden die
    Tiere per Befehl verliebt gemacht;
  - das Hineinführen der Tiere über Rampe und Treppen;
  - der Import mit dem Litematica-Mod selbst. Die Datei wurde mit einem eigenen Decoder und mit der
    unabhängigen Bibliothek *litemapy* blockgenau gegen das Modell geprüft.
- Babys springen im Becken, um den Eltern zu folgen, und geraten dabei oft (etwa jedes zweite) über
  die Wasserklinge in den Tötungsstrom. Das ist gewollt unschädlich: Sie warten dort, bis sie
  erwachsen sind, und landen dann gebraten in der Kiste.

---

## Für Bastler: Generator und Test

Die Schematic wird aus Python-Code erzeugt (nur Standardbibliothek, Python ≥ 3.10):

```bash
python3 build.py   # prüft das Modell, schreibt die .litematic und gibt die Materialliste aus
```

| Datei | Inhalt |
|---|---|
| `farm/model.py` | Blockmodell (Module Kuh/Schwein/Huhn, Wege), berechnet Mauer-/Kisten-/Redstone-Zustände und den Wasserfluss |
| `farm/checks.py` | statische Prüfungen: Grundfläche, Wasser/Lava getrennt, keine Stelle, an der Lava Feuer entzünden kann |
| `farm/materials.py` | Materialliste, Eisen- und Quarzbedarf |
| `farm/litematic.py` | Writer/Reader für `.litematic` (Version 7, Bit-Packing wie `LitematicaBitArray`) |
| `farm/nbt.py` | minimaler NBT-Reader/Writer |
| `farm/blocks.py`, `farm/data/blocks_26.3.json` | Blockzustände, geprüft gegen die Blockliste von 26.3 |
| `farm/commands.py` | dasselbe Modell als `/setblock`-Befehle |
| `tests/ingame/run_test.py` | Ingame-Test per RCON: bauen, zurücklesen (Region-Dateien), Brandtest, Tiere simulieren, Kisten auswerten |

Ingame-Test (eigener Testserver mit `enable-rcon=true`, `rcon.password=farmtest`,
`pause-when-empty-seconds=0`, Flachwelt):

```bash
python3 tests/ingame/run_test.py --server-dir <server-ordner> all      # bauen, Brandtest, Simulation
python3 tests/ingame/run_test.py --server-dir <server-ordner> bilanz   # Geburten vs. als Baby gestorben
```
