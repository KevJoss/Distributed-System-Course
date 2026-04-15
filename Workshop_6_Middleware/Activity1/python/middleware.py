#!/usr/bin/env python3
"""
Simple message-passing middleware (Python).
Features:
- Adds metadata (timestamp_ms, source_id, version)
- Length-prefixed JSON framing to avoid partial reads
- Helper server loop and client send function
"""
import socket, json, time, struct, threading
from typing import Callable, Dict, Any, Tuple

VERSION = 1

def _send_frame(sock: socket.socket, payload_bytes: bytes) -> None:
    header = struct.pack("!I", len(payload_bytes))  # 4-byte length prefix (network byte order)
    sock.sendall(header + payload_bytes)

def _recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Socket closed while receiving data")
        buf += chunk
    return buf

def _recv_frame(sock: socket.socket) -> bytes:
    raw_len = _recv_exact(sock, 4)
    (length,) = struct.unpack("!I", raw_len)
    if length > 10 * 1024 * 1024:  # 10 MB safety limit
        raise ValueError("Frame too large")
    return _recv_exact(sock, length)

def send_message(host: str, port: int, source_id: int, message: Dict[str, Any]) -> None:
    """
    Sends a structured JSON message with middleware metadata.
    """
    envelope = {
        "version": VERSION,
        "timestamp_ms": int(time.time() * 1000),
        "source_id": int(source_id),
        "payload": message,
    }
    data = json.dumps(envelope).encode("utf-8")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        _send_frame(s, data)

def start_server(port: int, handler: Callable[[Dict[str, Any], Tuple[str, int]], None]) -> None:
    """
    Starts a simple TCP server that receives framed JSON messages.
    The handler is called with (message_dict, client_address).
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("", port))
        srv.listen(8)
        print(f"[PY] Middleware server listening on 0.0.0.0:{port}")
        while True:
            conn, addr = srv.accept()
            threading.Thread(target=_handle_client, args=(conn, addr, handler), daemon=True).start()

def _handle_client(conn: socket.socket, addr: Tuple[str, int], handler):
    with conn:
        try:
            frame = _recv_frame(conn)
            msg = json.loads(frame.decode("utf-8"))
            handler(msg, addr)
        except Exception as e:
            print(f"[PY] Error handling client {addr}: {e}")
