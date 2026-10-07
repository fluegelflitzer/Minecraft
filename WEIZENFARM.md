# Weizenfarm mit 4 Bauern – Brot und Weizen vollautomatisch (Minecraft Java 26.3, Litematica)

Litematica-Vorlage für eine Dorfbewohner-Farm nach der Idee aus dem Video
[„WEIZEN FARM“ (ErikOnHisPeriod, Design Qix)](https://www.youtube.com/watch?v=XMGt4UanPsQ):
Bauern ernten, pflanzen nach, backen Brot und werfen ihren Überschuss einem anderen Dorfbewohner zu –
diese Würfe landen in Kisten.

**Datei:** [`schematics/Weizenfarm_4_Bauern.litematic`](schematics/Weizenfarm_4_Bauern.litematic)

| | |
|---|---|
| Minecraft | Java Edition **26.3** (Litematica-Format Version 7, DataVersion 5023) |
| Größe | 31 × 5 × 31 Blöcke – passt in **2 × 2 Chunks**, nur **4 hoch** (+ Blitzableiter) |
| Ertrag | im Dauertest ≈ **120 Brot + 60 Weizen pro Stunde** (Echtzeit, Farm geladen) |
| Lager | 4 Kisten, von außen durch ein Loch in der Wand zu leeren |
| Eisen | 40 (8 Trichter) |
| Dorfbewohner | 8: 4 Bauern + 4 „Sammler“ (beliebige Dorfbewohner) |

> **Stand: im Spiel getestet.** Die Farm wurde auf einem echten 26.3-Server Block für Block gebaut,
> zurückgelesen (0 Abweichungen) und mit echten Dorfbewohnern 23 Spieltage im Zeitraffer betrieben –
> Ergebnisse unter [Getestet](#6-getestet-auf-einem-echten-263-server).

---

## 1. So funktioniert sie

```
 Draufsicht (ein Modul, Nordwest; die anderen drei sind gespiegelt)

   #######o########     o  Loch in der Außenwand, dahinter die Kiste (von außen öffnen)
   #.....#S#......#     S  Sammler (Dorfbewohner), steht auf der Kiste; # daneben Glas 2 hoch
   #.....#T#......#     T  Schlitz-Trichter (fängt die Würfe) -> Trichter darunter -> Kiste
   #......B.......#        # neben T: Glas 1 hoch | B: hier steht der Bauer beim Zuwerfen
   #...~......~...#     ~  Wasser (obere Bruchsteinstufe, mit Wasser gefüllt)
   #..............#     .  Acker mit Weizen
   #..............#
   #......C.......#     C  Kompostierer (Arbeitsplatz des Bauern), darüber Leuchtstein
   #..............#
   Z..............#     Z  Zauntor (Eingang für dich)
   #..............#
   #...~......~...#
   #..............#
   #..............#
   #..............#
   ################     # Glas (Wände 3 hoch, Dach aus Glas)
```

1. **Ernten und Backen:** In jedem der 4 Glasmodule arbeitet genau ein Bauer. Er erntet reifen
   Weizen, pflanzt nach und backt am Kompostierer Brot (3 Weizen → 1 Brot), solange er höchstens
   36 Brot trägt. Überzählige Samen kompostiert er; das Knochenmehl streut er selbst auf das Feld.
2. **Abgeben:** Trifft ein Bauer einen anderen Dorfbewohner, wirft er ihm **alles Brot über 24 Stück**
   und **die Hälfte seines Weizens ab 33 Stück** zu (Spielmechanik „Essen teilen“). Dieser andere
   Dorfbewohner ist der **Sammler**: Er sitzt in einer engen Zelle an der Außenwand.
3. **Der Sichtschlitz:** Vor der Zelle steht ein Trichter in Feldhöhe, darüber ist bis zum Glasdach
   **1 Block Luft**. Durch diesen Schlitz sehen sich Bauer und Sammler (beide haben die Augen auf
   1,62 Blöcken Höhe), aber kein Dorfbewohner passt hindurch (sie brauchen 1,95 Blöcke).
   Der Bauer stellt sich direkt vor den Trichter und wirft – die Würfe landen auf dem Trichter.
4. **Einsaugen:** Geworfene Items darf 10 Ticks lang niemand aufheben. Der Trichter saugt sie
   innerhalb von höchstens 8 Ticks ein und gibt sie über einen zweiten Trichter in die Kiste unter
   dem Sammler. Fällt ein Wurf zu kurz, hebt der Bauer ihn wieder auf und wirft ihn beim nächsten
   Treffen erneut – es geht nichts verloren.

**Warum getrennte Module?** Das war die wichtigste Erkenntnis aus dem Test: Sehen sich zwei Bauern,
versuchen sie sich zu vermehren. Ohne Betten scheitert das, aber **jeder Versuch kostet beide je
3 Brot** – in einem gemeinsamen Feld kam deshalb **kein einziges Brot** in der Kiste an. Die Sammler
haben kein Essen und vermehren sich daher nie; die Glaswände sorgen dafür, dass jeder Bauer nur
seinen eigenen Sammler sieht.

**Unterschiede zum Video:** Das Video baut 4 runde Glaskuppeln um eine Mitte mit Glocke und Wassergraben
und arbeitet mit umbenannter Roter Bete im Inventar der Dorfbewohner. Diese Vorlage nutzt dasselbe Grundprinzip
(4 getrennte Bauern, Brot über Weitergabe einsammeln), aber in einer eckigen, am Code von 26.3
geprüften Form: eine Sammler-Zelle mit Sichtschlitz pro Modul statt der gemeinsamen Mitte, keine
Glocke (die Bauern tauschen in ihrer Freizeit, dafür braucht es keinen Treffpunkt) und keine
umbenannten Items. Damit passt die Farm in 31 × 31 × 5 und braucht nur 8 Trichter.

---

## 2. Importieren und platzieren

1. Litematica + MaLiLib für 26.3 installieren, die `.litematic` nach `.minecraft/schematics/` kopieren.
2. Im Spiel: `M` → *Load Schematics* → Datei wählen → *Load*.
3. Platzierung so verschieben, dass
   - **Ebene 0 (der Acker) auf Bodenhöhe** liegt: Der Acker ersetzt die oberste Gras-/Erdschicht,
     du kannst das Gras direkt mit der Hacke bearbeiten. Unter der Farm muss nichts gebaut werden.
   - die Farm in **4 Chunks** liegt: Ecke an eine Chunkgrenze legen (`F3 + G` zeigt die Grenzen).
     So ist die ganze Farm geladen, sobald du in der Nähe bist.
4. Drehen/Spiegeln ist erlaubt. Die Kisten sitzen dann an den entsprechenden Seiten.

---

## 3. Bau-Reihenfolge

1. **Acker und Wasser:** Boden einebnen, Acker hacken. An den 16 Wasserstellen (`~`) eine
   **obere** Bruchsteinstufe setzen und mit einem Wassereimer füllen (mit einer Endlosquelle
   reichen 2 Eimer). Die Bauern laufen darüber.
2. **Wände:** Außenwände und das Trennkreuz in der Mitte aus Glas, **3 Blöcke hoch**. Die Trennwände
   dürfen keine Lücke haben – die Bauern dürfen sich nicht sehen. Je Modul ein Zauntor als Eingang
   (Dorfbewohner öffnen keine Zauntore).
3. **Lampen:** In der Modulmitte Bruchstein in den Acker, Kompostierer darauf, Leuchtstein darüber.
4. **Sammler-Zellen** (je Modul, an der Außenwand):
   - **Kiste** in die Ackerebene, Vorderseite nach außen. Den Wandblock davor **weglassen**
     (das ist das Loch, durch das du die Kiste öffnest).
   - **Trichter** feldseitig vor die Kiste, auf die Kiste zeigend (Schleichen + auf die Kiste klicken).
   - **Schlitz-Trichter** auf diesen Trichter, nach unten zeigend (auf die Oberseite des unteren
     Trichters klicken).
   - **Glas:** links und rechts neben der Zelle je 2 hoch, links und rechts neben dem Schlitz-Trichter
     je 1 hoch. **Über dem Schlitz-Trichter bleibt Luft bis zum Dach** – das ist der Sichtschlitz.
5. **Dach** aus Glas über alles (Ebene 3), **Blitzableiter** auf die Dachmitte. Ein Blitz verwandelt
   Dorfbewohner in Hexen; der Blitzableiter fängt alle Blitze im Umkreis von 128 Blöcken.
6. **Weizen pflanzen:** das ganze Feld mit Weizensamen bepflanzen. Die Bauern pflanzen danach selbst
   nach, auf ein leeres Feld setzen sie aber nur ~10 Samen, weil sie den Rest kompostieren.

## 4. Dorfbewohner einsetzen

- **Sammler (4×):** Die beiden Glasblöcke der Außenwand über dem Kistenloch entfernen, einen beliebigen
  Dorfbewohner (ohne Beruf, Nitwit oder mit Beruf – egal) mit Lore oder Boot hineinbringen, bis er
  auf der Kiste steht, Glas wieder einsetzen. Er kann von dort keinen Arbeitsblock erreichen und
  nimmt daher keinem Bauern den Kompostierer weg.
- **Bauern (4×, genau einer pro Modul):** durch das Zauntor mit Lore oder Boot ins Modul bringen.
  Ein Dorfbewohner ohne Beruf nimmt den Kompostierer und wird Bauer.
- Eine Glocke oder Betten braucht die Farm nicht.

## 5. Betrieb

- Die Kisten (je 27 Plätze ≈ 1 700 Items) **regelmäßig leeren**. Ist eine Kiste voll, staut sich der
  Trichter; dann hebt der Bauer seine Würfe wieder auf (kein Verlust), aber auch der Sammler kann
  Brot aufheben – und mit Brot im Inventar könnten Bauer und Sammler Brot bei Vermehrungsversuchen essen.
- Die Farm arbeitet nur, solange ihre Chunks geladen sind (du bist in Simulationsdistanz).
- **Anlaufzeit:** Die Bauern werfen erst, wenn sie über 24 Brot bzw. über 32 Weizen tragen – das erste
  Brot kommt nach etwa 3 Spieltagen (1 Spieltag = 20 Minuten).

---

## 6. Getestet auf einem echten 26.3-Server

Testumgebung wie bei der Tierfarm: headless 26.3-Server, Farm per `/setblock` gebaut, Blöcke aus den
Regionsdateien zurückgelesen, dann im Zeitraffer (`/tick sprint`) mit echten Dorfbewohnern betrieben.

Feld zu Beginn voll bepflanzt (Weizen in zufälligem Alter), 4 Bauern + 4 Sammler, Zahlen jeweils zur
Mittagszeit des Spieltags:

| Spieltag | Kisten: Brot | Kisten: Weizen | Brot / Weizen bei den Bauern | bei den Sammlern | liegende Items |
|---:|---:|---:|---|---|---:|
| 1 | 0 | 0 | 19 / 22 | leer | 0 |
| 3 | 2 | 0 | 95 / 50 | leer | 0 |
| 5 | 109 | 0 | 85 / 36 | leer | 1 |
| 10 | 296 | 103 | 88 / 84 | leer | 0 |
| 15 | 525 | 188 | 85 / 64 | leer | 0 |
| 20 | 717 | 316 | 88 / 86 | leer | 0 |
| 23 | **824** | **372** | 106 / 71 | leer | 2 |

- **Bau:** 0 Befehle ohne Wirkung, Rücklesen aus den Regionsdateien: **0 Abweichungen**.
- **Dauerleistung** (Tag 6 bis 23): **≈ 41 Brot + 21 Weizen pro Spieltag**, also ≈ 120 Brot + 60 Weizen
  pro Stunde Echtzeit. Alle 4 Kompostierer blieben die ganze Zeit von ihren 4 Bauern besetzt.
- **Nichts geht verloren:** Die Sammler hatten nie etwas im Inventar, es lagen fast keine Items herum
  (frische Ernte, die der Bauer gleich aufhebt).
- **Vergleich, warum getrennte Module:** Mit 4 Bauern in *einem* Feld kamen in 10 Spieltagen
  **0 Brot** an – die Bauern aßen ihr Brot bei Vermehrungsversuchen.
- Eine Vorversion mit gleicher Mechanik (zusätzliche Erdschicht unter dem Acker) lief 16 Spieltage:
  557 Brot + 263 Weizen.

---

## Grenzen

- **Der Ertrag hängt an der Bauern-KI, nicht am Feld.** Im Test standen meist über die Hälfte der
  Pflanzen reif auf dem Feld; ein Bauer erntet nur einen Teil davon. Mehr Ertrag gibt es nur mit mehr
  Bauern (z. B. eine zweite Farm), nicht mit mehr Acker.
- **Bauern horten Samen** (im Test 100–220 Stück, mehrere Inventarplätze). Das blieb über den ganzen
  Test stabil. Liefert ein Bauer trotzdem einmal dauerhaft nichts mehr (etwa weil sein Inventar so voll
  Samen ist, dass kein Platz für Weizen bleibt), ersetze ihn durch einen neuen Dorfbewohner.
- **Niemals zwei Bauern in ein Modul** und keine Lücken in den Trennwänden – sonst essen sie das Brot
  bei Vermehrungsversuchen.
- Weitere Dorfbewohner in der Nähe stören nicht, solange sie nicht in die Module gelangen.
- Was der Zeitraffer-Test nicht abdeckt: Bauen in Survival (Litematica zeigt dir jeden Block an),
  Transport der Dorfbewohner, Spieler-Interaktion (Handel mit den Bauern ist erlaubt, ändert nichts).

---

## Selbst nachprüfen

```bash
python3 build_weizen.py                    # Prüfungen + .litematic + Materialliste
python3 tests/ingame/weizen_test.py --server-dir <server> build              # bauen + zurücklesen
python3 tests/ingame/weizen_test.py --server-dir <server> sim --plant --days 30   # Dauertest
```

`weizenfarm/model.py` beschreibt die Farm, `weizenfarm/checks.py` prüft statisch (Blockzustände 26.3,
Größe ≤ 2×2 Chunks und ≤ 24 hoch, jedes Feld bewässert und frei, kein dunkler Spawnplatz,
Sammler-Zellen dicht mit offenem Sichtschlitz).

## Materialliste

| Menge | Material |
|---:|---|
| 1504 | Glas (Dach 961, Wände) |
| 740 | Ackerboden (Erde/Gras mit der Hacke) |
| 16 | Bruchsteinstufe (obere Hälfte, mit Wasser gefüllt) + 2 Wassereimer |
| 16 | Erde (unter den Zellenwänden) |
| 8 | Trichter (= **40 Eisen**) |
| 4 | Kiste |
| 4 | Komposter |
| 4 | Leuchtstein (Block) |
| 4 | Bruchstein |
| 4 | Eichenzauntor |
| 1 | Blitzableiter (3 Kupferbarren) |
| bis 740 | Weizensamen zum ersten Bepflanzen |
| 8 | Dorfbewohner (4 Bauern + 4 Sammler) |

Glas lässt sich bei den Wänden durch jeden anderen vollen Block ersetzen (z. B. Bruchstein) – wichtig
ist nur, dass die Trennwände lückenlos sind. Das Dach muss bleiben: Es bildet den Sichtschlitz.
