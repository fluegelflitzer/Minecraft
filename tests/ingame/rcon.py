"""Kleiner RCON-Client (Source-RCON-Protokoll) für den headless Testserver."""
from __future__ import annotations

import socket
import struct
import time


class Rcon:
    def __init__(self, host: str = "127.0.0.1", port: int = 25575, password: str = "", timeout: float = 120.0):
        self._addr = (host, port, password, timeout)
        self._open()

    def _open(self) -> None:
        host, port, password, timeout = self._addr
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self._id = 0
        if self._request(3, password)[0] == -1:
            raise PermissionError("RCON-Login fehlgeschlagen")

    def _send(self, kind: int, body: str) -> int:
        self._id += 1
        data = body.encode("utf-8")
        packet = struct.pack("<ii", self._id, kind) + data + b"\x00\x00"
        self.sock.sendall(struct.pack("<i", len(packet)) + packet)
        return self._id

    def _recv_exact(self, n: int) -> bytes:
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("RCON-Verbindung getrennt")
            buf += chunk
        return buf

    def _recv(self) -> tuple[int, int, str]:
        (length,) = struct.unpack("<i", self._recv_exact(4))
        payload = self._recv_exact(length)
        req_id, kind = struct.unpack("<ii", payload[:8])
        return req_id, kind, payload[8:-2].decode("utf-8", errors="replace")

    def _request(self, kind: int, body: str) -> tuple[int, str]:
        self._send(kind, body)
        req_id, _, text = self._recv()
        return req_id, text

    def cmd(self, command: str) -> str:
        """Befehl ausführen; bei Verbindungsabbruch einmal neu verbinden und wiederholen."""
        try:
            return self._cmd(command)
        except (ConnectionError, OSError):
            time.sleep(1)
            self._open()
            return self._cmd(command)

    def _cmd(self, command: str) -> str:
        """Lange Antworten werden über ein Endmarker-Paket zusammengesetzt."""
        main_id = self._send(2, command)
        marker_id = self._send(2, "seed")  # Server antwortet in Reihenfolge -> Marker beendet die Antwort
        parts = []
        while True:
            req_id, _, text = self._recv()
            if req_id == main_id:
                parts.append(text)
            elif req_id == marker_id:
                break
        return "".join(parts)

    def close(self) -> None:
        self.sock.close()


def connect(password: str, port: int = 25575, wait: float = 180.0) -> Rcon:
    deadline = time.time() + wait
    while True:
        try:
            return Rcon(port=port, password=password)
        except OSError:
            if time.time() > deadline:
                raise
            time.sleep(2)
