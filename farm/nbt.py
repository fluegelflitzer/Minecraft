"""Minimal NBT (Named Binary Tag) reader/writer, nur Standardbibliothek.

Python-Darstellung:
  Compound -> dict, String -> str, List -> TagList, sonstige Zahlen über die
  Wrapper-Klassen (Byte, Short, Int, Long, Float, Double, IntArray, LongArray,
  ByteArray), damit der Tag-Typ beim Schreiben eindeutig ist.
"""
from __future__ import annotations

import gzip
import io
import struct

TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG, TAG_FLOAT, TAG_DOUBLE = range(7)
TAG_BYTE_ARRAY, TAG_STRING, TAG_LIST, TAG_COMPOUND, TAG_INT_ARRAY, TAG_LONG_ARRAY = range(7, 13)


class _Num:
    tag = -1
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return type(self) is type(other) and self.value == other.value

    def __repr__(self):
        return f"{type(self).__name__}({self.value!r})"


class Byte(_Num):
    tag = TAG_BYTE


class Short(_Num):
    tag = TAG_SHORT


class Int(_Num):
    tag = TAG_INT


class Long(_Num):
    tag = TAG_LONG


class Float(_Num):
    tag = TAG_FLOAT


class Double(_Num):
    tag = TAG_DOUBLE


class ByteArray(_Num):
    tag = TAG_BYTE_ARRAY


class IntArray(_Num):
    tag = TAG_INT_ARRAY


class LongArray(_Num):
    tag = TAG_LONG_ARRAY


class TagList(list):
    """NBT-Liste mit festem Elementtyp (für leere Listen wichtig)."""

    def __init__(self, elem_tag: int, items=()):
        super().__init__(items)
        self.elem_tag = elem_tag


def _tag_of(value) -> int:
    if isinstance(value, _Num):
        return value.tag
    if isinstance(value, str):
        return TAG_STRING
    if isinstance(value, TagList):
        return TAG_LIST
    if isinstance(value, dict):
        return TAG_COMPOUND
    raise TypeError(f"Kein NBT-Typ für {value!r}")


def _write_str(out: io.BytesIO, s: str) -> None:
    data = s.encode("utf-8")  # reicht für ASCII/BMP-Text (kein Modified-UTF-8 nötig)
    out.write(struct.pack(">H", len(data)))
    out.write(data)


def _write_payload(out: io.BytesIO, tag: int, value) -> None:
    if tag == TAG_BYTE:
        out.write(struct.pack(">b", value.value))
    elif tag == TAG_SHORT:
        out.write(struct.pack(">h", value.value))
    elif tag == TAG_INT:
        out.write(struct.pack(">i", value.value))
    elif tag == TAG_LONG:
        out.write(struct.pack(">q", value.value))
    elif tag == TAG_FLOAT:
        out.write(struct.pack(">f", value.value))
    elif tag == TAG_DOUBLE:
        out.write(struct.pack(">d", value.value))
    elif tag == TAG_BYTE_ARRAY:
        out.write(struct.pack(">i", len(value.value)))
        out.write(struct.pack(f">{len(value.value)}b", *value.value))
    elif tag == TAG_STRING:
        _write_str(out, value)
    elif tag == TAG_LIST:
        elem = value.elem_tag if len(value) else (value.elem_tag if value.elem_tag else TAG_END)
        out.write(struct.pack(">bi", elem, len(value)))
        for item in value:
            if _tag_of(item) != elem:
                raise TypeError("Gemischte Typen in NBT-Liste")
            _write_payload(out, elem, item)
    elif tag == TAG_COMPOUND:
        for key, item in value.items():
            t = _tag_of(item)
            out.write(struct.pack(">b", t))
            _write_str(out, key)
            _write_payload(out, t, item)
        out.write(b"\x00")
    elif tag == TAG_INT_ARRAY:
        out.write(struct.pack(">i", len(value.value)))
        out.write(struct.pack(f">{len(value.value)}i", *value.value))
    elif tag == TAG_LONG_ARRAY:
        out.write(struct.pack(">i", len(value.value)))
        out.write(struct.pack(f">{len(value.value)}q", *value.value))
    else:
        raise ValueError(tag)


def dumps(root: dict, root_name: str = "") -> bytes:
    out = io.BytesIO()
    out.write(struct.pack(">b", TAG_COMPOUND))
    _write_str(out, root_name)
    _write_payload(out, TAG_COMPOUND, root)
    return out.getvalue()


def write_gzip(path, root: dict, root_name: str = "") -> None:
    data = dumps(root, root_name)
    # mtime=0 -> reproduzierbare Dateien
    with open(path, "wb") as fh, gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
        gz.write(data)


# ---------------------------------------------------------------- Lesen

class _Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def take(self, fmt: str):
        size = struct.calcsize(fmt)
        vals = struct.unpack_from(fmt, self.data, self.pos)
        self.pos += size
        return vals

    def string(self) -> str:
        (n,) = self.take(">H")
        s = self.data[self.pos:self.pos + n].decode("utf-8")
        self.pos += n
        return s

    def payload(self, tag: int):
        if tag == TAG_BYTE:
            return Byte(self.take(">b")[0])
        if tag == TAG_SHORT:
            return Short(self.take(">h")[0])
        if tag == TAG_INT:
            return Int(self.take(">i")[0])
        if tag == TAG_LONG:
            return Long(self.take(">q")[0])
        if tag == TAG_FLOAT:
            return Float(self.take(">f")[0])
        if tag == TAG_DOUBLE:
            return Double(self.take(">d")[0])
        if tag == TAG_BYTE_ARRAY:
            (n,) = self.take(">i")
            return ByteArray(list(self.take(f">{n}b")))
        if tag == TAG_STRING:
            return self.string()
        if tag == TAG_LIST:
            elem, n = self.take(">bi")
            return TagList(elem, [self.payload(elem) for _ in range(n)])
        if tag == TAG_COMPOUND:
            result = {}
            while True:
                (t,) = self.take(">b")
                if t == TAG_END:
                    return result
                key = self.string()
                result[key] = self.payload(t)
        if tag == TAG_INT_ARRAY:
            (n,) = self.take(">i")
            return IntArray(list(self.take(f">{n}i")))
        if tag == TAG_LONG_ARRAY:
            (n,) = self.take(">i")
            return LongArray(list(self.take(f">{n}q")))
        raise ValueError(f"Unbekannter Tag {tag}")


def loads(data: bytes) -> tuple[str, dict]:
    r = _Reader(data)
    (tag,) = r.take(">b")
    if tag != TAG_COMPOUND:
        raise ValueError("Wurzel ist kein Compound")
    name = r.string()
    return name, r.payload(TAG_COMPOUND)


def read_gzip(path) -> tuple[str, dict]:
    with gzip.open(path, "rb") as fh:
        return loads(fh.read())
