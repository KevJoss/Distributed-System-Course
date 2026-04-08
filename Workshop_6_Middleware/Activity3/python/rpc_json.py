#!/usr/bin/env python3
"""
JSON-framed RPC (compatible with C implementation).
Each frame is:
  uint32 length (big-endian) + UTF-8 JSON document

Request JSON:
  {"version":1,"call_id":1,"method":"sum_list","params":[1,2,3]}

Response JSON:
  {"version":1,"call_id":1,"status":"ok","result":<json>}
  or
  {"version":1,"call_id":1,"status":"error","error":"message"}
"""
import socket, struct, json, threading

VERSION = 1

def _send_all(sock, b: bytes):
    off = 0
    while off < len(b):
        n = sock.send(b[off:])
        if n <= 0:
            raise ConnectionError("send failed")
        off += n

def _recv_exact(sock, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("socket closed")
        buf += chunk
    return buf

def send_json(sock: socket.socket, obj: dict):
    data = json.dumps(obj).encode("utf-8")
    header = struct.pack("!I", len(data))
    _send_all(sock, header + data)

def recv_json(sock: socket.socket) -> dict:
    (length,) = struct.unpack("!I", _recv_exact(sock, 4))
    data = _recv_exact(sock, length)
    return json.loads(data.decode("utf-8"))

def call(host: str, port: int, method: str, params):
    req = {"version": VERSION, "call_id": 1, "method": method, "params": params}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        send_json(s, req)
        resp = recv_json(s)
    return resp

def start_server(port: int, registry=None, name: str|None=None, methods: dict|None=None):
    if methods is None: methods = {}
    # Optional: register this service
    if registry and name:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(registry)
                send_json(s, {"op":"register","name":name,"host":"127.0.0.1","port":port})
                _ = recv_json(s)
                print(f"[PY] Registered service '{name}' -> 127.0.0.1:{port} at registry {registry}")
        except Exception as e:
            print(f"[PY] Registry register failed: {e}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("", port))
        srv.listen(32)
        print(f"[PY] JSON-RPC server on 0.0.0.0:{port}")
        while True:
            conn, addr = srv.accept()
            threading.Thread(target=_handle_client, args=(conn, addr, methods), daemon=True).start()

def _handle_client(conn, addr, methods):
    with conn:
        try:
            req = recv_json(conn)
            if req.get("version") != VERSION:
                send_json(conn, {"version":VERSION,"call_id":req.get("call_id",0),"status":"error","error":"version mismatch"})
                return
            m = req.get("method","")
            params = req.get("params", None)
            if m not in methods:
                send_json(conn, {"version":VERSION,"call_id":req.get("call_id",0),"status":"error","error":f"unknown method '{m}'"})
                return

            # Allow positional (list) or named (dict) params
            fn = methods[m]
            if isinstance(params, list):
                result = fn(*params)
            elif isinstance(params, dict):
                result = fn(**params)
            else:
                result = fn(params)
            send_json(conn, {"version":VERSION,"call_id":req.get("call_id",0),"status":"ok","result":result})
        except Exception as e:
            try:
                send_json(conn, {"version":VERSION,"call_id":0,"status":"error","error":str(e)})
            except Exception:
                pass
