# Weizenfarm-Hochhaus – 14 Bauern, Brot und Weizen vollautomatisch (Minecraft Java 26.3, Litematica)

Litematica-Vorlage für eine Dorfbewohner-Farm nach der Idee aus dem Video
[„WEIZEN FARM“ (ErikOnHisPeriod, Design Qix)](https://www.youtube.com/watch?v=XMGt4UanPsQ):
Bauern ernten, pflanzen nach, backen Brot und werfen ihren Überschuss einem anderen Dorfbewohner zu.
Diese Würfe landen in Kisten.

**Datei:** [`schematics/Weizenfarm_Hochhaus_14_Bauern.litematic`](schematics/Weizenfarm_Hochhaus_14_Bauern.litematic)

| | |
|---|---|
| Minecraft | Java Edition **26.3** (Litematica-Format Version 7, DataVersion 5023) |
| Größe | 32 × 23 × 16 Blöcke: genau **2 × 1 Chunks**, **23 hoch**, **7 Etagen** |
| Dorfbewohner | 21: **14 Bauern** (2 pro Etage) + **7 Sammler** (1 pro Etage, mittig) |
| Ertrag | im Test ≈ **440 Brot + 120 Weizen pro Stunde** (Echtzeit, Farm geladen) |
| Lager | 14 Kisten (je Bauer eine, direkt neben dem Sammler) |
| Eisen | 70 (14 Trichter) |

> **Stand: im Spiel getestet.** Die Farm wurde auf einem echten 26.3-Server Block für Block gebaut,
> zurückgelesen (0 Abweichungen) und mit 14 Bauern und 7 Sammlern im Zeitraffer betrieben.
> Ergebnisse unter [Getestet](#6-getestet-auf-einem-echten-263-server).

---

## 1. So funktioniert sie

```
 Draufsicht einer Etage (Norden oben, x 0–31 nach rechts)

   ################################
   #L.............##.............L#      Westmodul (14 × 13)  |  Ostmodul (14 × 13)
   #..........L...##...L..........#
   #..............##..............#      .  Acker mit Weizen
   #...~......~...##...~......~...#      ~  Wasser (untere Bruchsteinstufe, mit Wasser gefüllt)
   #..L...........##...........L..#      L  Kürbislaterne im Acker (Licht für den Weizen)
   #.............###..............#      C  Kompostierer (Arbeitsplatz des Bauern), darüber Kürbislaterne
   #.......C.....TST.....C........#      S  Sammler in seiner Zelle, T Schlitz-Trichter links/rechts
   #.............K#K..............#      K  Kiste (Trichter füllt hinein); # neben S/T/K: Glas
   #............L.##.L............#      Der Bauer steht beim Zuwerfen direkt vor seinem T.
   #...~......~...##...~......~...#
   #........L.....##......L.......#
   #L.............##.............L#
   #..............##..............#
   ############Z######Z############      Z  Zauntor zum Balkon
   H===============================      =  Balkon (obere Bruchsteinstufen), H Leiter
```

1. **Ernten und Backen:** In jedem Modul arbeitet genau ein Bauer. Er erntet reifen Weizen, pflanzt
   nach und backt am Kompostierer Brot (3 Weizen → 1 Brot), solange er höchstens 36 Brot trägt.
   Überzählige Samen kompostiert er; das Knochenmehl streut er selbst auf das Feld.
2. **Abgeben:** Trifft ein Bauer einen anderen Dorfbewohner, wirft er ihm **alles Brot über 24 Stück**
   und **die Hälfte seines Weizens ab 33 Stück** zu. Dieser andere Dorfbewohner ist der **Sammler**.
   Er sitzt in einer engen Zelle mitten in der Trennwand, also genau zwischen den beiden Bauern der Etage.
3. **Die Sichtschlitze:** Links und rechts der Zelle steht je ein Trichter auf Feldhöhe. Darüber ist bis
   zur Decke **1 Block Luft**. Durch diese Schlitze sehen die Bauern den Sammler (Augenhöhe 1,62), aber
   kein Dorfbewohner passt hindurch (er braucht 1,95 Blöcke). Der Bauer stellt sich vor seinen Trichter
   und wirft, die Würfe landen auf dem Trichter.
4. **Einsaugen:** Geworfene Items darf 10 Ticks lang niemand aufheben. Der Trichter saugt sie innerhalb
   von höchstens 8 Ticks ein und gibt sie in die Kiste neben sich. Fällt ein Wurf zu kurz, hebt der
   Bauer ihn wieder auf und wirft ihn beim nächsten Mal erneut. Es geht nichts verloren.

**Warum getrennte Module?** Kommen zwei Bauern nah aneinander heran, versuchen sie sich zu vermehren.
Ohne Betten scheitert das, aber **jeder Versuch kostet beide je 3 Brot**. Gegessen wird nur, wenn die
beiden höchstens 2,24 Blöcke voneinander entfernt sind. Durch die Sammler-Zelle sehen sich die zwei
Bauern einer Etage zwar, kommen aber nie näher als 3,6 Blöcke aneinander heran. Deshalb reicht
**ein Sammler für zwei Bauern**. Etagen sind durch massive Decken getrennt. Der Sammler hat kein
Essen und vermehrt sich nie.

**Licht und Wasser:** In den unteren Etagen kommt kein Himmelslicht von oben. Kürbislaternen im Acker
sorgen dafür, dass jedes Feld mindestens Licht 9 hat (sonst wächst Weizen nicht). Das ist berechnet,
ohne das Licht durch die Glaswände mitzuzählen. Das Wasser steckt in **unteren** Bruchsteinstufen:
Der Acker einer Etage ist die Decke der Etage darunter, und eine obere Stufe würde nach unten auslaufen.

**Unterschiede zum Video:** Das Video baut 4 runde Glaskuppeln um eine Mitte mit Glocke und arbeitet
mit umbenannter Roter Bete. Diese Vorlage nutzt dasselbe Grundprinzip in einer gestapelten, am Code
von 26.3 geprüften Form: 7 Etagen à 2 Bauern, ein Sammler pro Etage, keine Glocke, keine
umbenannten Items.

---

## 2. Importieren und platzieren

1. Litematica + MaLiLib für 26.3 installieren, die `.litematic` nach `.minecraft/schematics/` kopieren.
2. Im Spiel: `M` → *Load Schematics* → Datei wählen → *Load*.
3. Platzierung:
   - **Ebene 0** (Acker der untersten Etage) **auf Bodenhöhe**: Der Acker ersetzt die oberste Gras- bzw.
     Erdschicht.
   - Die Farm genau in **2 Chunks** legen: Ecke an eine Chunkgrenze (`F3 + G`), die lange Seite (32)
     entlang der Chunkreihe.
4. Drehen/Spiegeln ist erlaubt. Der Balkon (eigentlich Südseite) liegt dann entsprechend anders.

## 3. Bau-Reihenfolge

Am einfachsten **Etage für Etage von unten nach oben**, und jede Etage gleich mit Dorfbewohnern
besetzen, bevor die nächste darüber kommt (siehe 4.).

1. **Acker, Wasser, Licht:** Acker hacken. Auf die 4 Wasserstellen pro Modul eine **untere**
   Bruchsteinstufe setzen und mit dem Wassereimer füllen. Kürbislaternen an ihre Stellen im Acker setzen.
2. **Wände:** Außenwände und die doppelte Trennwand aus Glas, je Etage 3 Blöcke hoch. Die Trennwand darf
   außer an der Sammler-Zelle keine Lücke haben.
3. **Lampe:** Bruchstein in den Acker, Kompostierer darauf, Kürbislaterne darüber (bis an die Decke).
4. **Sammler-Zelle** (Etagenmitte, in der Trennwand):
   - Zellenboden: Erde. Vor und hinter der Zelle je 2 Glas übereinander.
   - Links und rechts der Zelle je ein **Trichter**, der in die **Kiste** daneben zeigt (Schleichen + auf
     die Kiste klicken). Auf der anderen Seite des Trichters 1 Glas.
   - Über Trichter, Glas und Kiste bleibt **Luft bis zur Decke**: das ist der Sichtschlitz.
5. **Decke:** Die nächste Etage (ihr Acker) ist die Decke. Über der obersten Etage Glasdach und
   Blitzableiter. Ein Blitz verwandelt Dorfbewohner in Hexen; der Blitzableiter fängt alle Blitze im
   Umkreis von 128 Blöcken.
6. **Balkon und Leiter:** Auf jeder Etage eine Reihe oberer Bruchsteinstufen vor der Südwand, Leiter am
   Westende, je Modul ein Zauntor in der Südwand (darüber frei für deinen Kopf).
7. **Weizen pflanzen:** jedes Feld bepflanzen. Die Bauern pflanzen danach selbst nach. Auf ein leeres
   Feld setzen sie nur ~10 Samen, weil sie den Rest kompostieren.

## 4. Dorfbewohner einsetzen

- **Pro Etage:** 2 Bauern (je einer pro Modul) und 1 Sammler.
- **Sammler:** Glasblock vor oder hinter der Zelle (2 hoch) entfernen, einen beliebigen Dorfbewohner (ohne
  Beruf, Nitwit oder mit Beruf, egal) mit Lore oder Boot hineinbringen, Glas wieder einsetzen. Er
  erreicht von dort keinen Arbeitsblock und nimmt daher keinem Bauern den Kompostierer weg.
- **Bauern:** durch das Zauntor ins Modul bringen. Ein Dorfbewohner ohne Beruf nimmt den Kompostierer
  und wird Bauer. **Niemals zwei Bauern in ein Modul.**
- **Nach oben bringen:** Dorfbewohner können keine Leitern steigen. Am einfachsten setzt du jede Etage
  ein, solange sie noch oben offen ist. Die Dorfbewohner bringst du dafür mit einer Lore auf einer
  provisorischen Schienenrampe außen an der Farm nach oben. Die Rampe baust du danach wieder ab.
- Glocke oder Betten braucht die Farm nicht.

## 5. Betrieb

- **Kisten leeren:** je Modul eine Kiste direkt neben dem Sammler (27 Plätze ≈ 1 700 Items), vom Modul
  aus zu öffnen. Rein über den Balkon und das Zauntor. Ist eine Kiste voll, staut sich der Trichter;
  dann hebt der Bauer seine Würfe wieder auf (kein Verlust).
- Die Farm arbeitet nur, solange ihre Chunks geladen sind (du bist in Simulationsdistanz).
- **Anlaufzeit:** Die Bauern werfen erst, wenn sie über 24 Brot bzw. über 32 Weizen tragen. Das erste
  Brot kommt nach etwa 3 Spieltagen (1 Spieltag = 20 Minuten).

---

## 6. Getestet auf einem echten 26.3-Server

Headless 26.3-Server, Farm per `/setblock` gebaut, Blöcke aus den Regionsdateien zurückgelesen, dann im
Zeitraffer (`/tick sprint`) mit echten Dorfbewohnern betrieben.

Feld zu Beginn voll bepflanzt (Weizen in zufälligem Alter), 14 Bauern + 7 Sammler, Zahlen jeweils zur
Mittagszeit des Spieltags:

| Spieltag | Kisten: Brot | Kisten: Weizen | Brot / Weizen bei den Bauern | bei den Sammlern | liegende Items |
|---:|---:|---:|---|---|---:|
| 1 | 0 | 0 | 68 / 58 | leer | 0 |
| 2 | 0 | 0 | 195 / 151 | leer | 1 |
| 3 | 14 | 21 | 330 / 136 | leer | 2 |
| 4 | 154 | 21 | 334 / 191 | 1 Weizen | 0 |
| 5 | 312 | 64 | 318 / 215 | 1 Weizen | 2 |
| 6 | 488 | 109 | 310 / 130 | 1 Weizen | 0 |
| 7 | 633 | 130 | 306 / 169 | 1 Weizen | 0 |
| 8 | 763 | 130 | 326 / 186 | 1 Weizen | 1 |
| 9 | 910 | 130 | 348 / 143 | 1 Weizen | 2 |
| 10 | 1 031 | 185 | 349 / 204 | 1 Weizen | 2 |
| 11 | 1 188 | 225 | 320 / 271 | 1 Weizen | 1 |
| 12 | **1 328** | **340** | 320 / 208 | 18 Weizen (1 Sammler) | 1 |

- **Bau:** 0 Befehle ohne Wirkung, Rücklesen aus den Regionsdateien: **0 Abweichungen**.
  Der erste Testbau hatte noch *obere* Wasserstufen; deren Wasser lief in die Etage darunter. Seitdem
  sind es untere Stufen.
- **Alle 14 Kompostierer** wurden sofort von den 14 Bauern belegt, die 7 Sammler blieben ohne Beruf.
- **Leistung** (Tag 4 bis 12): ≈ 147 Brot + 40 Weizen pro Spieltag, also ≈ 440 Brot + 120 Weizen pro
  Stunde Echtzeit – gleichmäßig über den ganzen Test.
- **Alle 14 Bauern liefern:** Nach 12 Tagen hatte jede der 14 Kisten 76–110 Brot (dazu bis 103 Weizen).
- **Kaum Verlust:** Fast keine Items lagen herum (frische Ernte, die der Bauer gleich aufhebt).
  Zwei Würfe Weizen landeten nicht auf dem Trichter, sondern beim Sammler (zusammen 18 Weizen in
  12 Tagen). Weizen ist kein Essen für Dorfbewohner und stört nicht; Brot blieb nie beim Sammler.
- **Vergleich, warum getrennte Bauern:** Mit 4 Bauern in *einem* Feld kamen in 10 Spieltagen
  **0 Brot** an, weil die Bauern ihr Brot bei Vermehrungsversuchen aßen.

---

## Grenzen

- **Der Ertrag hängt an der Bauern-KI, nicht am Feld.** Ein Bauer erntet nur einen Teil der reifen
  Pflanzen. Mehr Ertrag gibt es nur mit mehr Bauern.
- **Bauern horten Samen** (100–220 Stück, mehrere Inventarplätze). Das blieb im Test stabil. Liefert
  ein Bauer dauerhaft nichts mehr (etwa weil sein Inventar voller Samen ist und kein Platz für Weizen
  bleibt), ersetze ihn durch einen neuen Dorfbewohner.
- **Niemals zwei Bauern in ein Modul** und keine Lücke in der Trennwand außer der Sammler-Zelle. Sonst
  kommen sich die Bauern nahe genug, um ihr Brot bei Vermehrungsversuchen zu essen.
- Was der Zeitraffer-Test nicht abdeckt: Bauen in Survival (Litematica zeigt dir jeden Block an),
  Transport der Dorfbewohner.

---

## Selbst nachprüfen

```bash
python3 build_weizen.py                                              # Prüfungen + .litematic + Materialliste
python3 tests/ingame/weizen_test.py --server-dir <server> build              # bauen + zurücklesen
python3 tests/ingame/weizen_test.py --server-dir <server> sim --plant --days 12   # Dauertest
```

`weizenfarm/model.py` beschreibt die Farm, `weizenfarm/checks.py` prüft statisch: Blockzustände 26.3,
Größe ≤ 2×1 Chunks und ≤ 23 hoch, jedes Feld bewässert und frei, Licht ≥ 9 auf jedem Feld (nur
Blocklicht), keine dunkle Stelle für Monster, Sammler-Zellen dicht mit offenen Sichtschlitzen.

## Materialliste

| Menge | Material |
|---:|---|
| 2 850 | Glas (Wände und Dach; die Außenwände dürfen auch aus Bruchstein o. Ä. sein) |
| 2 373 | Ackerboden (Erde mit der Hacke) |
| 217 | Bruchsteinstufe, obere Hälfte (Balkonboden) |
| 98 | Kürbislaterne (Kürbis + Fackel) |
| 56 | Bruchsteinstufe, untere Hälfte, mit Wasser gefüllt (+ 2 Wassereimer, Endlosquelle) |
| 49 | Erde (unter Trichtern, Kisten und Zellen) |
| 19 | Leiter |
| 14 | **Trichter** (= **70 Eisen**) |
| 14 | Kiste |
| 14 | Komposter |
| 14 | Bruchstein (unter den Kompostierern) |
| 14 | Eichenzauntor |
| 1 | Blitzableiter (3 Kupferbarren) |
| bis 2 373 | Weizensamen zum ersten Bepflanzen |
| 21 | Dorfbewohner (14 Bauern + 7 Sammler) |
