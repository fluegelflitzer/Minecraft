"""Bauplan für Bots: alle Blöcke in einer Reihenfolge, die im Survival ohne Hilfsblöcke funktioniert.

Für jeden Schritt steht drin, gegen welche Fläche welches schon gesetzten Blocks (oder des Geländes)
geklickt wird, wohin der Bot dabei schaut und ob er die obere oder untere Hälfte der Fläche trifft.
Die Regeln stammen aus dem Platzierungscode von Minecraft 26.3 (getStateForPlacement der Blöcke):
  - Stämme, Heuballen, Ketten: Achse = Achse der angeklickten Fläche
  - Treppen: facing = Blickrichtung; half = oben, wenn Unterseite oder obere Hälfte einer Seitenfläche
  - Stufen: type wie half bei Treppen
  - Falltüren: an einer Seitenfläche -> facing = diese Fläche, half nach Trefferhöhe;
    auf einer Oberseite -> half=bottom, facing = Gegenrichtung des Blicks
  - Öfen, Kisten, Lesepult usw.: Vorderseite zeigt zum Bot (facing = Gegenrichtung des Blicks)
  - Tür: facing = Blickrichtung, Scharnier aus den Nachbarblöcken bzw. der getroffenen Hälfte
  - Bett: Fußende auf dem Klickziel, Kopfende in Blickrichtung
  - Laterne: hängend, wenn der Bot nach oben schaut und die Unterseite des Blocks darüber anklickt
  - Kiste: verbindet sich mit einer einzelnen Nachbarkiste gleicher Richtung, außer beim Schleichen
"""
from __future__ import annotations

import heapq
import json
from collections import Counter
from dataclasses import dataclass, field

from farm.blocks import DIRS, Block
from farm.model import Model

from .katalog import CCW, CW, OPP, FACE_PLAYER, eintrag, full_block, sturdy

HORIZ = ("north", "east", "south", "west")
AXIS_DIRS = {"x": ("west", "east"), "y": ("down", "up"), "z": ("north", "south")}

# Blöcke, die erst gesetzt werden, wenn ihre Umgebung fertig ist (Reihenfolge innerhalb einer Ebene)
PRIO = {"voll": 0, "saeule": 0, "gerichtet": 1, "laub": 1, "treppe": 1, "stufe": 1, "mauer": 1, "zaun": 1,
        "scheibe": 2, "zauntor": 2, "falltuer": 2, "kette": 2, "kiste": 3, "deko": 3, "bett": 3, "tuer": 4,
        "teppich": 4, "pflanze": 4, "laterne": 4, "fackel": 4, "wandfackel": 4, "leiter": 4, "lagerfeuer": 3}

# Formen, die einen tragenden Block darunter brauchen (Überleben im Spiel) und darauf gesetzt werden
NEEDS_BELOW = {"tuer", "teppich", "pflanze", "fackel", "deko", "bett", "lagerfeuer"}


@dataclass
class Schritt:
    pos: tuple
    block: Block
    item: str
    klick: tuple | None = None
    seite: str = ""
    blick: str | None = None
    hoehe: str | None = None
    extra: list = field(default_factory=list)
    teile: list = field(default_factory=list)  # weitere Positionen, die derselbe Klick füllt (Tür oben, Bettkopf)
    aktion: str = "setzen"  # setzen | hilfsblock (Erde setzen, kommt gleich wieder weg) | abbauen
    klick_gelaende: bool = False  # angeklickt wird natürliches Gelände, kein gesetzter Block

    def as_json(self, nr: int) -> dict:
        if self.aktion == "abbauen":
            return {"nr": nr, "aktion": "abbauen", "pos": list(self.pos)}
        d = {"nr": nr, "aktion": self.aktion, "pos": list(self.pos), "block": self.block.name,
             "zustand": {k: v for k, v in self.block.props}, "item": "minecraft:" + self.item,
             "klick": {"block": list(self.klick), "seite": self.seite}}
        if self.klick_gelaende:
            d["klick"]["gelaende"] = True
        if self.blick:
            d["blick"] = self.blick
        if self.hoehe:
            d["treffer"] = self.hoehe
        if self.extra:
            d["extra"] = self.extra
        if self.teile:
            d["fuellt_auch"] = [list(p) for p in self.teile]
        return d


def _nb(p, d, n=1):
    dx, dy, dz = DIRS[d]
    return (p[0] + dx * n, p[1] + dy * n, p[2] + dz * n)


class Planer:
    def __init__(self, m: Model):
        self.m = m
        self.world: dict[tuple, Block] = {}  # bereits gesetzte Blöcke
        self.reserved: set = set()
        sx, sy, sz = m.size
        self.size = m.size
        self.errors: list[str] = []

    # --- Gelände: alles unter y=0 und Luft auf y=0 (natürlicher Boden)
    def ground(self, p) -> bool:
        x, y, z = p
        if y < 0:
            return True
        return y == 0 and self.m.get(x, y, z).id == "air"

    def solid_target(self, p) -> Block | None:
        """Block, gegen den man klicken kann (gesetzt oder Gelände). Gelände zählt als voller Block."""
        if p in self.world:
            return self.world[p]
        if self.ground(p):
            return GROUND
        return None

    def center_support(self, p, face) -> bool:
        b = self.solid_target(p)
        if b is None:
            return False
        if b is GROUND or sturdy(b, face):
            return True
        e = eintrag(b)
        if e and e.form in ("zaun", "mauer"):
            return True
        if e and e.form == "kette" and b.prop("axis") == "y":
            return True
        return False

    # --- Klickmöglichkeiten
    def options(self, p, b: Block):
        """Liste möglicher (klickblock, seite, hoehe) für Block b an Position p, in Vorzugsreihenfolge."""
        e = eintrag(b)
        f = e.form
        below, above = _nb(p, "down"), _nb(p, "up")

        def have(q):
            return self.solid_target(q) is not None

        out = []
        if f in ("saeule", "kette"):
            for d in AXIS_DIRS[b.prop("axis")]:
                q = _nb(p, d)
                if have(q):
                    out.append((q, OPP[d], None))
            return out
        if f in ("treppe", "stufe"):
            half = b.prop("half") if f == "treppe" else b.prop("type")
            if half == "double":
                return []
            if half == "bottom" and have(below):
                out.append((below, "up", None))
            if half == "top" and have(above):
                out.append((above, "down", None))
            for d in HORIZ:
                q = _nb(p, d)
                if have(q):
                    out.append((q, OPP[d], "oben" if half == "top" else "unten"))
            return out
        if f == "falltuer":
            facing, half = b.prop("facing"), b.prop("half")
            q = _nb(p, OPP[facing])
            if have(q):
                out.append((q, facing, "oben" if half == "top" else "unten"))
            if half == "bottom" and have(below):
                out.append((below, "up", None))
            if half == "top" and have(above):
                out.append((above, "down", None))
            return out
        if f in ("wandfackel", "leiter"):
            facing = b.prop("facing")
            q = _nb(p, OPP[facing])
            if have(q) and (self.solid_target(q) is GROUND or sturdy(self.solid_target(q), facing)):
                out.append((q, facing, None))
            return out
        if f == "laterne":
            if b.prop("hanging") == "true":
                if self.center_support(above, "down"):
                    out.append((above, "down", None))
            elif self.center_support(below, "up"):
                out.append((below, "up", None))
            return out
        if f in NEEDS_BELOW:
            if f == "tuer":
                ok = self.solid_target(below) is GROUND or (below in self.world and sturdy(self.world[below], "up"))
            elif f == "pflanze":
                ok = self.solid_target(below) is GROUND or (below in self.world and
                                                             self.world[below].id in ("dirt", "coarse_dirt", "moss_block"))
            elif f == "deko" and b.id.endswith("pressure_plate"):
                ok = self.center_support(below, "up")
            else:
                ok = have(below)
            if ok:
                out.append((below, "up", None))
            return out
        # alles andere: irgendein Nachbar, bevorzugt darunter
        for d in ("down", "north", "east", "south", "west", "up"):
            q = _nb(p, d)
            if have(q):
                out.append((q, OPP[d], None))
        return out

    def blick(self, b: Block) -> str | None:
        e = eintrag(b)
        if e.form in ("treppe", "tuer", "bett", "zauntor", "lagerfeuer"):
            return b.prop("facing")
        if b.id == "barrel":
            fc = b.prop("facing")
            return {"up": "unten", "down": "oben"}.get(fc, OPP.get(fc))
        if b.id in FACE_PLAYER and "facing" in dict(b.props):
            return OPP[b.prop("facing")]
        if e.form == "laterne":
            return "oben" if b.prop("hanging") == "true" else "unten"
        return None

    # --- Sonderfälle beim Setzen
    def door_hinge(self, p, facing) -> tuple[str | None, str | None]:
        """(erzwungenes Scharnier oder None, nötige Klickhälfte)."""
        up = _nb(p, "up")
        left, right = CCW[facing], CW[facing]

        def full(q):
            t = self.solid_target(q)
            return t is not None and (t is GROUND or full_block(t))

        i = -int(full(_nb(p, left))) - int(full(_nb(up, left))) + int(full(_nb(p, right))) + int(full(_nb(up, right)))
        ld = self.world.get(_nb(p, left))
        rd = self.world.get(_nb(p, right))
        left_door = ld is not None and ld.id.endswith("_door") and ld.prop("half") == "lower"
        right_door = rd is not None and rd.id.endswith("_door") and rd.prop("half") == "lower"
        if (not left_door or right_door) and i <= 0:
            if (not right_door or left_door) and i >= 0:
                return None, None
            return "left", None
        return "right", None

    def chest_type(self, p, facing) -> str:
        for d, t in ((CW[facing], "left"), (CCW[facing], "right")):
            n = self.world.get(_nb(p, d))
            if n is not None and n.id == "chest" and n.prop("facing") == facing and n.prop("type") == "single":
                return t
        return "single"

    # --- Hauptschleife
    def plan(self) -> list[Schritt]:
        m = self.m
        todo: dict[tuple, Block] = {}
        parts: dict[tuple, list] = {}
        for p, b in m.blocks.items():
            e = eintrag(b)
            if e is None:
                self.errors.append(f"{p}: {b.name} ist kein erlaubter Block")
                continue
            if e.form == "tuer" and b.prop("half") == "upper":
                continue
            if e.form == "bett" and b.prop("part") == "head":
                continue
            todo[p] = b
            if e.form == "tuer":
                parts[p] = [_nb(p, "up")]
            elif e.form == "bett":
                parts[p] = [_nb(p, b.prop("facing"))]
        for ps in parts.values():
            self.reserved.update(ps)

        heap = []

        def key(p):
            e = eintrag(todo[p])
            return (p[1], PRIO[e.form], p[2], p[0])

        def push(p):
            if p in todo and self.options(p, todo[p]) and self.extra_ok(p, todo[p]):
                heapq.heappush(heap, (key(p), p))

        for p in todo:
            push(p)
        steps: list[Schritt] = []
        done = set()
        scaffold_for: dict[tuple, list] = {}
        left_by_y = Counter(p[1] for p in todo)

        def try_scaffold(cands) -> bool:
            for p in sorted(cands, key=key):
                col = self.scaffold(p, todo[p])
                if col:
                    scaffold_for[p] = col
                    for c in col:
                        q, seite = self.any_click(c)
                        steps.append(Schritt(c, SCAFFOLD, "dirt", q, seite, aktion="hilfsblock",
                                             klick_gelaende=self.solid_target(q) is GROUND))
                        self.world[c] = SCAFFOLD
                    heapq.heappush(heap, (key(p), p))
                    return True
            return False

        while True:
            # Ebene für Ebene: hängt die unterste offene Ebene fest, zuerst dort einen Hilfsblock versuchen
            lowest = min((y for y, n in left_by_y.items() if n), default=None)
            if lowest is None:
                break
            if not heap or heap[0][0][0] > lowest:
                stuck = [p for p in todo if p not in done and p[1] == lowest]
                if not try_scaffold(stuck) and not heap:
                    if not try_scaffold([p for p in todo if p not in done]):
                        break
            _, p = heapq.heappop(heap)
            if p in done:
                continue
            b = todo[p]
            opts = self.options(p, b)
            if not opts or not self.extra_ok(p, b):
                continue
            q, seite, hoehe = opts[0]
            e = eintrag(b)
            s = Schritt(p, b, e.item, q, seite, self.blick(b), hoehe, teile=parts.get(p, []),
                        klick_gelaende=self.solid_target(q) is GROUND)
            if p[1] == 0:
                s.extra.append("vorher den Geländeblock an dieser Stelle abbauen")
            if e.form == "tuer":
                forced, _ = self.door_hinge(p, b.prop("facing"))
                want = b.prop("hinge")
                if forced is None:
                    half = CCW[b.prop("facing")] if want == "left" else CW[b.prop("facing")]
                    s.extra.append(f"Oberseite in der Hälfte Richtung {half} anklicken (Scharnier {want})")
                elif forced != want:
                    self.errors.append(f"Tür {p}: Scharnier wäre {forced}, geplant {want}")
            if e.form == "kiste":
                t = self.chest_type(p, b.prop("facing"))
                want = b.prop("type")
                if want == "single" and t != "single":
                    s.extra.append("schleichen (sonst verbindet sich die Kiste mit der Nachbarkiste)")
                elif want != "single" and t not in ("single", want):
                    self.errors.append(f"Kiste {p}: würde {t}, geplant {want}")
            if e.form == "laterne" and b.prop("hanging") == "true":
                s.extra.append("nach oben schauen")
            steps.append(s)
            done.add(p)
            left_by_y[p[1]] -= 1
            self.world[p] = b
            for t in parts.get(p, []):
                self.world[t] = m.get(*t)
            for c in reversed(scaffold_for.pop(p, [])):
                steps.append(Schritt(c, SCAFFOLD, "dirt", aktion="abbauen"))
                del self.world[c]
            # Nachbarn neu prüfen
            for d in DIRS:
                for n in (_nb(p, d), _nb(_nb(p, d), "up"), _nb(_nb(p, d), "down")):
                    if n in todo and n not in done:
                        push(n)
            for d in HORIZ:
                for n in (_nb(_nb(p, d), CW[d]),):
                    if n in todo and n not in done:
                        push(n)
        missing = [p for p in todo if p not in done]
        for p in missing[:20]:
            self.errors.append(f"{p}: {todo[p]} lässt sich nicht setzen (keine passende Fläche zum Anklicken)")
        if len(missing) > 20:
            self.errors.append(f"... und {len(missing) - 20} weitere")
        return steps

    def any_click(self, p):
        for d in ("down", "north", "east", "south", "west", "up"):
            q = _nb(p, d)
            if self.solid_target(q) is not None:
                return q, OPP[d]
        return None, None

    def scaffold(self, p, b: Block) -> list | None:
        """Hilfsblock (oder kurze Säule aus Hilfsblöcken) neben p, gegen den sich b richtig setzen lässt."""
        e = eintrag(b)
        f = e.form
        if f in ("saeule", "kette"):
            dirs = AXIS_DIRS[b.prop("axis")]
        elif f in ("treppe", "stufe"):
            half = b.prop("half") if f == "treppe" else b.prop("type")
            dirs = HORIZ + (("down",) if half == "bottom" else ("up",))
        elif f == "falltuer":
            dirs = (OPP[b.prop("facing")],)
        elif f in ("wandfackel", "leiter", "laterne", "tuer") or f in NEEDS_BELOW:
            return None
        else:
            dirs = ("down",) + HORIZ
        sx, sy, sz = self.size
        best = None
        for d in dirs:
            q = _nb(p, d)
            col = []
            r = q
            while True:
                if r in self.world or self.ground(r) or not (-2 <= r[0] <= sx + 1 and 1 <= r[1] <= sy + 1
                                                             and -2 <= r[2] <= sz + 1):
                    col = None
                    break
                col.insert(0, r)
                if self.any_click(r)[0] is not None:
                    break
                r = _nb(r, "down")
                if len(col) > 8:
                    col = None
                    break
            if col and (best is None or len(col) < len(best)):
                best = col
        return best

    def extra_ok(self, p, b: Block) -> bool:
        """Zusatzbedingungen: Tür erst, wenn ihre Nachbarn stehen; Bett/Tür brauchen freie zweite Hälfte."""
        e = eintrag(b)
        if e.form == "tuer":
            facing = b.prop("facing")
            up = _nb(p, "up")
            for q in (_nb(p, CCW[facing]), _nb(p, CW[facing]), _nb(up, CCW[facing]), _nb(up, CW[facing])):
                if self.m.get(*q).id != "air" and q not in self.world and not self.ground(q):
                    if eintrag(self.m.get(*q)) and eintrag(self.m.get(*q)).form == "tuer":
                        continue
                    return False
        return True


class _Ground:
    name = "gelaende"
    id = "gelaende"
    props = ()


GROUND = _Ground()
SCAFFOLD = Block("minecraft:dirt")


def plan(m: Model) -> tuple[list[Schritt], list[str]]:
    p = Planer(m)
    steps = p.plan()
    return steps, p.errors


def to_json(m, steps: list[Schritt], material: list[dict]) -> str:
    head = {
        "name": m.key,
        "titel": m.titel,
        "beschreibung": m.beschreibung,
        "minecraft": "26.3",
        "groesse": list(m.size),
        "koordinaten": "relativ zur Schematic-Ecke: x = Osten, y = oben, z = Süden",
        "boden_y": 0,
        "regeln": [
            "Ebene y=0 ist die Geländeoberfläche: dort stehende Blöcke ersetzen das Gras, "
            "Luft auf y=0 heißt: Gelände bleibt.",
            "Ab y=1 muss alles, was im Plan nicht vorkommt, Luft sein (Gras, Blumen, Bäume vorher entfernen).",
            "Schritte der Reihe nach ausführen. klick.block ist der Block, dessen Fläche klick.seite angeklickt "
            "wird (klick.gelaende = true: natürlicher Boden, kein gesetzter Block). blick = Blickrichtung des Bots beim Setzen "
            "(oben/unten = steil nach oben/unten schauen). treffer = obere/untere Hälfte der angeklickten Seitenfläche.",
            "fuellt_auch: Diese Positionen füllt das Spiel beim selben Klick (obere Türhälfte, Kopfende vom Bett); "
            "sie müssen vorher frei sein.",
            "Zäune, Scheiben, Mauern und Treppenecken verbinden sich von selbst; der Endzustand steht in der .litematic.",
        ],
        "material": material,
    }
    lines = [json.dumps(s.as_json(i + 1), ensure_ascii=False, separators=(",", ":")) for i, s in enumerate(steps)]
    body = json.dumps(head, ensure_ascii=False, indent=1)
    return body[:-2] + ',\n "schritte": [\n  ' + ",\n  ".join(lines) + "\n ]\n}\n"
