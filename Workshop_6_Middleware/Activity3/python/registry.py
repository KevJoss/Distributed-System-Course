#!/usr/bin/env python3
"""
Simple naming registry.
Protocol (JSON-framed, one request per connection):
  Register: {"op":"register","name":"calc_service","host":"127.0.0.1","port":7000}
  Lookup:   {"op":"lookup","name":"calc_service"}
Responses:
  {"status":"ok"} or {"status":"ok","host":"...","port":7000} or {"status":"error","error":"..."}
"""
import socket, struct, json, threading

def _send_all(sock,b):
    off=0
    while off<len(b):
        n=sock.send(b[off:])
        if n<=0: raise ConnectionError("send failed")
        off+=n
def _recv_exact(sock,n):
    buf=b''
    while len(buf)<n:
        c=sock.recv(n-len(buf))
        if not c: raise ConnectionError("closed")
        buf+=c
    return buf
def send_json(sock,obj):
    data=json.dumps(obj).encode('utf-8')
    _send_all(sock, struct.pack("!I", len(data)) + data)
def recv_json(sock):
    (l,)=struct.unpack("!I", _recv_exact(sock,4))
    return json.loads(_recv_exact(sock,l).decode('utf-8'))

class Registry:
    def __init__(self): self.map = {}
    def register(self, name, host, port):
        self.map[name] = (host, int(port))
    def lookup(self, name):
        if name in self.map: return self.map[name]
        raise KeyError("not found")

def start_registry(port:int=7001):
    reg = Registry()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", port))
        s.listen(64)
        print(f"[PY] Registry on 0.0.0.0:{port}")
        while True:
            c,a = s.accept()
            threading.Thread(target=handle_client, args=(c,reg), daemon=True).start()

def handle_client(conn, reg: 'Registry'):
    with conn:
        try:
            req = recv_json(conn)
            if req.get("op")=="register":
                name=req["name"]; host=req["host"]; port=int(req["port"])
                reg.register(name,host,port)
                send_json(conn, {"status":"ok"})
            elif req.get("op")=="lookup":
                name=req["name"]
                host,port = reg.lookup(name)
                send_json(conn, {"status":"ok","host":host,"port":port})
            else:
                send_json(conn, {"status":"error","error":"unknown op"})
        except Exception as e:
            try: send_json(conn, {"status":"error","error":str(e)})
            except Exception: pass

if __name__=="__main__":
    start_registry()
