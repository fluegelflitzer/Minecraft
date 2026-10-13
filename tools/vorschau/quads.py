"""Blockmodelle aus dem Minecraft-Client auflösen und als texturierte Vierecke exportieren.

Eingabe: {(x, y, z): Block} (farm.blocks.Block), Pfad zu den entpackten Client-Assets (assets_holen.py).
Ausgabe: atlas.png + scene.json (Vierecke mit Atlas-UVs und Helligkeit), gerendert von render.mjs.
Unterstützt Blockstate-Varianten und Multipart, Modell-Vererbung, Element-Drehungen, Varianten-Drehung
(x/y), Flächen-Culling an vollen Nachbarblöcken, Biom-Tönung für Laub. Truhen (Block-Entity) als einfacher Kasten.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

from PIL import Image

FACES = ("down", "up", "north", "south", "west", "east")
NORMALS = {"down": (0, -1, 0), "up": (0, 1, 0), "north": (0, 0, -1), "south": (0, 0, 1), "west": (-1, 0, 0), "east": (1, 0, 0)}
SHADE = {"up": 1.0, "down": 0.5, "north": 0.8, "south": 0.8, "west": 0.6, "east": 0.6}
FOLIAGE = (0x59, 0xAE, 0x30)
GRASS = (0x79, 0xC0, 0x5A)
SPRUCE = (0x61, 0x99, 0x61)
BIRCH = (0x80, 0xA7, 0x55)


class Assets:
    def __init__(self, root: Path):
        self.root = Path(root) / "assets" / "minecraft"
        self._tex: dict[str, int] = {}
        self.textures: list[Image.Image] = []

    @lru_cache(maxsize=None)
    def blockstate(self, block_id: str) -> dict:
        p = self.root / "blockstates" / f"{block_id}.json"
        return json.loads(p.read_text())

    @lru_cache(maxsize=None)
    def model(self, name: str) -> dict:
        name = name.split(":", 1)[-1]
        data = json.loads((self.root / "models" / f"{name}.json").read_text())
        if "parent" in data:
            parent = self.model(data["parent"])
            merged = dict(parent)
            tex = dict(parent.get("textures", {}))
            tex.update(data.get("textures", {}))
            merged["textures"] = tex
            if "elements" in data:
                merged["elements"] = data["elements"]
            return merged
        return data

    def texture_index(self, ref: str) -> int:
        name = ref.split(":", 1)[-1]
        if name not in self._tex:
            p = self.root / "textures" / f"{name}.png"
            img = Image.open(p).convert("RGBA")
            w, h = img.size
            if h > w:  # animiert: erstes Bild
                img = img.crop((0, 0, w, w))
            if img.size != (16, 16):
                img = img.resize((16, 16), Image.NEAREST)
            self._tex[name] = len(self.textures)
            self.textures.append(img)
        return self._tex[name]


def _resolve_tex(textures: dict, ref: str) -> str:
    seen = 0
    if isinstance(ref, dict):
        ref = ref.get("sprite", "minecraft:block/missing")
    while ref.startswith("#"):
        ref = textures.get(ref[1:], "minecraft:block/missing")
        if isinstance(ref, dict):
            ref = ref.get("sprite", "minecraft:block/missing")
        seen += 1
        if seen > 10:
            break
    return ref


def _matches(cond: dict, props: dict) -> bool:
    if "OR" in cond:
        return any(_matches(c, props) for c in cond["OR"])
    if "AND" in cond:
        return all(_matches(c, props) for c in cond["AND"])
    for k, v in cond.items():
        if props.get(k) not in str(v).split("|"):
            return False
    return True


def models_for(assets: Assets, block_id: str, props: dict) -> list[dict]:
    bs = assets.blockstate(block_id)
    out = []
    if "variants" in bs:
        for key, val in bs["variants"].items():
            if key == "" or all(props.get(k) == v for k, v in (p.split("=") for p in key.split(","))):
                out.append(val[0] if isinstance(val, list) else val)
                break
    else:
        for part in bs["multipart"]:
            if "when" not in part or _matches(part["when"], props):
                a = part["apply"]
                out.append(a[0] if isinstance(a, list) else a)
    return out


def _rot(v, axis, deg, origin):
    """Punkt v um Achse durch origin drehen (Grad, Minecraft-Konvention)."""
    if deg == 0:
        return v
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    x, y, z = (v[i] - origin[i] for i in range(3))
    if axis == "x":
        y, z = y * c - z * s, y * s + z * c
    elif axis == "y":
        x, z = x * c + z * s, -x * s + z * c
    else:
        x, y = x * c - y * s, x * s + y * c
    return (x + origin[0], y + origin[1], z + origin[2])


def _face_corners(f, t, face):
    x0, y0, z0 = f
    x1, y1, z1 = t
    # Ecken gegen den Uhrzeigersinn von außen gesehen, Start oben links passend zur UV-Konvention
    return {
        "down": [(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)],
        "up": [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
        "north": [(x1, y1, z0), (x0, y1, z0), (x0, y0, z0), (x1, y0, z0)],
        "south": [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)],
        "west": [(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)],
        "east": [(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)],
    }[face]


def _default_uv(f, t, face):
    x0, y0, z0 = f
    x1, y1, z1 = t
    return {
        "down": [x0, 16 - z1, x1, 16 - z0],
        "up": [x0, z0, x1, z1],
        "north": [16 - x1, 16 - y1, 16 - x0, 16 - y0],
        "south": [x0, 16 - y1, x1, 16 - y0],
        "west": [z0, 16 - y1, z1, 16 - y0],
        "east": [16 - z1, 16 - y1, 16 - z0, 16 - y0],
    }[face]


def _rot_dir(d, xrot, yrot):
    v = NORMALS[d]
    v = _rot(v, "x", -xrot, (0, 0, 0))
    v = _rot(v, "y", -yrot, (0, 0, 0))
    v = tuple(round(c) for c in v)
    for k, n in NORMALS.items():
        if n == v:
            return k
    return d


def _normal_name(n):
    best, bv = "up", -2
    for k, v in NORMALS.items():
        dot = sum(a * b for a, b in zip(n, v))
        if dot > bv:
            best, bv = k, dot
    return best


FULL_OPAQUE_CACHE: dict = {}


def is_full_opaque(assets: Assets, block) -> bool:
    key = block
    if key in FULL_OPAQUE_CACHE:
        return FULL_OPAQUE_CACHE[key]
    res = False
    bid = block.id
    if not any(s in bid for s in ("glass", "leaves", "ice", "slime", "honey", "barrier", "spawner")):
        try:
            ms = models_for(assets, bid, dict(block.props))
            if len(ms) == 1:
                m = assets.model(ms[0]["model"])
                els = m.get("elements", [])
                res = len(els) == 1 and els[0]["from"] == [0, 0, 0] and els[0]["to"] == [16, 16, 16]
        except FileNotFoundError:
            res = False
    FULL_OPAQUE_CACHE[key] = res
    return res


def block_quads(assets: Assets, pos, block, neighbor):
    """neighbor(dir) -> Block in Nachbarrichtung."""
    props = dict(block.props)
    bid = block.id
    quads = []
    if bid in ("chest", "trapped_chest"):
        return _chest_quads(assets, pos, props, neighbor)
    for mref in models_for(assets, bid, props):
        model = assets.model(mref["model"])
        xrot, yrot = mref.get("x", 0), mref.get("y", 0)
        textures = model.get("textures", {})
        for el in model.get("elements", []):
            f, t = el["from"], el["to"]
            erot = el.get("rotation")
            for face, fd in el.get("faces", {}).items():
                cull = fd.get("cullface")
                if cull:
                    real = _rot_dir(cull, xrot, yrot)
                    nb = neighbor(real)
                    if nb is not None and is_full_opaque(assets, nb):
                        continue
                corners = _face_corners(f, t, face)
                uv = fd.get("uv") or _default_uv(f, t, face)
                pts = []
                for c in corners:
                    p = c
                    if erot:
                        p = _rot(p, erot["axis"], erot["angle"], erot["origin"])
                    p = _rot(p, "x", -xrot, (8, 8, 8))
                    p = _rot(p, "y", -yrot, (8, 8, 8))
                    pts.append(p)
                # Normale aus den Punkten
                a, b, c = pts[0], pts[1], pts[2]
                u = [b[i] - a[i] for i in range(3)]
                v = [c[i] - a[i] for i in range(3)]
                n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
                shade = SHADE[_normal_name(n)] if model.get("shade", True) and fd.get("shade", True) is not False else 1.0
                tex = _resolve_tex(textures, fd["texture"])
                ti = assets.texture_index(tex)
                u0, v0, u1, v1 = uv
                uvs = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
                r = fd.get("rotation", 0)
                for _ in range(r // 90):
                    uvs = uvs[1:] + uvs[:1]
                tint = None
                if "tintindex" in fd:
                    if "spruce" in bid:
                        tint = SPRUCE
                    elif "birch" in bid:
                        tint = BIRCH
                    elif "leaves" in bid or "vine" in bid:
                        tint = FOLIAGE
                    else:
                        tint = GRASS
                world = [(pos[0] + p[0] / 16, pos[1] + p[1] / 16, pos[2] + p[2] / 16) for p in pts]
                quads.append((world, uvs, ti, shade, tint))
    return quads


def _chest_quads(assets, pos, props, neighbor):
    # vereinfachte Truhe: Kasten 1..15 aus Truhentextur-Ausschnitten (Holz + Beschlag)
    quads = []
    ti = assets.texture_index("minecraft:block/spruce_planks")
    lock = assets.texture_index("minecraft:block/iron_block")
    typ = props.get("type", "single")
    facing = props.get("facing", "north")
    x0, x1, z0, z1 = 1, 15, 1, 15
    # Doppeltruhe: zur Partnerseite bündig
    if typ != "single":
        cw = {"north": "east", "east": "south", "south": "west", "west": "north"}[facing]
        side = cw if typ == "left" else {"east": "west", "west": "east", "north": "south", "south": "north"}[cw]
        if side == "east":
            x1 = 16
        if side == "west":
            x0 = 0
        if side == "south":
            z1 = 16
        if side == "north":
            z0 = 0
    f, t = (x0, 0, z0), (x1, 14, z1)
    for face in FACES:
        corners = _face_corners(f, t, face)
        uv = _default_uv(f, t, face)
        u0, v0, u1, v1 = uv
        world = [(pos[0] + p[0] / 16, pos[1] + p[1] / 16, pos[2] + p[2] / 16) for p in corners]
        quads.append((world, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], ti, SHADE[face] * 0.9, (200, 150, 90)))
    # Schloss vorne
    d = facing
    if d in ("north", "south"):
        zz = z0 - 0.01 if d == "north" else z1 + 0.01
        f2, t2 = (7, 7, zz), (9, 11, zz)
        face = d
    else:
        xx = x0 - 0.01 if d == "west" else x1 + 0.01
        f2, t2 = (xx, 7, 7), (xx, 11, 9)
        face = d
    corners = _face_corners(f2, t2, face)
    world = [(pos[0] + p[0] / 16, pos[1] + p[1] / 16, pos[2] + p[2] / 16) for p in corners]
    quads.append((world, [(0, 0), (4, 0), (4, 4), (0, 4)], lock, SHADE[face], None))
    return quads


def export(blocks: dict, assets_root, out_dir, ground: set | None = None, ground_margin: int = 4, size=None):
    """blocks: {(x,y,z): Block}; ground: Positionen (x,z), an denen auf Ebene 0 natürlicher Boden liegt."""
    from farm.blocks import B  # noqa

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    assets = Assets(assets_root)
    allb = dict(blocks)
    if size is not None:
        sx, sy, sz = size
        grass = B("grass_block")
        dirt = B("dirt")
        for x in range(-ground_margin, sx + ground_margin):
            for z in range(-ground_margin, sz + ground_margin):
                if (x, 0, z) not in allb:
                    allb[(x, 0, z)] = grass
                allb[(x, -1, z)] = dirt

    def nb_func(p):
        def f(d):
            n = NORMALS[d]
            return allb.get((p[0] + n[0], p[1] + n[1], p[2] + n[2]))
        return f

    all_quads = []
    for p, b in allb.items():
        if b.id == "air":
            continue
        try:
            all_quads.extend(block_quads(assets, p, b, nb_func(p)))
        except FileNotFoundError as e:
            print("fehlt:", b, e)
    # Atlas
    n = len(assets.textures)
    cols = math.ceil(math.sqrt(n))
    atlas = Image.new("RGBA", (cols * 16, cols * 16), (0, 0, 0, 0))
    for i, img in enumerate(assets.textures):
        atlas.paste(img, ((i % cols) * 16, (i // cols) * 16))
    atlas.save(out_dir / "atlas.png")
    W = cols * 16
    pos, uv, col = [], [], []
    for world, uvs, ti, shade, tint in all_quads:
        ox, oy = (ti % cols) * 16, (ti // cols) * 16
        tr, tg, tb = (c / 255 for c in tint) if tint else (1, 1, 1)
        for k in (0, 1, 2, 0, 2, 3):
            pos.extend(world[k])
            u, v = uvs[k]
            uv.extend(((ox + u) / W, 1 - (oy + v) / W))
            col.extend((shade * tr, shade * tg, shade * tb))
    scene = {"pos": [round(v, 4) for v in pos], "uv": [round(v, 6) for v in uv], "col": [round(v, 3) for v in col]}
    (out_dir / "scene.json").write_text(json.dumps(scene, separators=(",", ":")))
    return len(all_quads)
