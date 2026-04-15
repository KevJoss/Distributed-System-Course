#!/usr/bin/env python3
import socket, struct, threading

VERSION = 1

def _send_all(sock, b: bytes):
    total = 0
    while total < len(b):
        n = sock.send(b[total:])
        if n <= 0:
            raise ConnectionError("send failed")
        total += n

def _recv_exact(sock, n: int) -> bytes:
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("socket closed")
        buf += chunk
    return buf

def send_request(sock: socket.socket, call_id: int, method: str, params: list[int]) -> None:
    method_b = method.encode("utf-8")
    if len(method_b) > 65535:
        raise ValueError("method too long")
    if len(params) > 65535:
        raise ValueError("too many params")
    body = struct.pack("!IIHH", VERSION, call_id, len(method_b), len(params)) + method_b
    for p in params:
        body += struct.pack("!q", int(p))  # int64
    frame = struct.pack("!I", len(body)) + body
    _send_all(sock, frame)

def recv_request(sock: socket.socket):
    (frame_len,) = struct.unpack("!I", _recv_exact(sock, 4))
    body = _recv_exact(sock, frame_len)
    off = 0
    version, call_id, mlen, argc = struct.unpack_from("!IIHH", body, off); off += 12
    method = body[off:off+mlen].decode("utf-8"); off += mlen
    params = []
    for _ in range(argc):
        (val,) = struct.unpack_from("!q", body, off); off += 8
        params.append(val)
    return version, call_id, method, params

def send_response(sock: socket.socket, call_id: int, status: int, result: int = 0, error: str = ""):
    if status == 0:
        body = struct.pack("!IIIqH", VERSION, call_id, 0, int(result), 0)
    else:
        err_b = error.encode("utf-8")
        if len(err_b) > 65535:
            err_b = err_b[:65535]
        body = struct.pack("!IIIqH", VERSION, call_id, 1, 0, len(err_b)) + err_b
    frame = struct.pack("!I", len(body)) + body
    _send_all(sock, frame)

def recv_response(sock: socket.socket):
    (frame_len,) = struct.unpack("!I", _recv_exact(sock, 4))
    body = _recv_exact(sock, frame_len)
    version, call_id, status, result, err_len = struct.unpack_from("!IIIqH", body, 0)
    off = struct.calcsize("!IIIqH")
    err = ""
    if status != 0 and err_len > 0:
        err = body[off:off+err_len].decode("utf-8")
    return version, call_id, status, result, err

def start_server(port: int, registry: dict[str, callable]):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", port))
        s.listen(16)
        print(f"[PY] RPC server listening on 0.0.0.0:{port}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=_handle_client, args=(conn, addr, registry), daemon=True).start()

def _handle_client(conn: socket.socket, addr, registry):
    with conn:
        try:
            ver, call_id, method, params = recv_request(conn)
            if ver != VERSION:
                send_response(conn, call_id, 1, error="version mismatch"); return
            fn = registry.get(method)
            if not fn:
                send_response(conn, call_id, 1, error=f"unknown method '{method}'"); return
            try:
                res = fn(*params)
            except TypeError as te:
                send_response(conn, call_id, 1, error=f"arg error: {te}"); return
            send_response(conn, call_id, 0, result=int(res))
        except Exception as e:
            try: send_response(conn, 0, 1, error=str(e))
            except Exception: pass
