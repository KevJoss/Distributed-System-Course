#!/usr/bin/env python3
import argparse, socket
from rpc import send_request, recv_response

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Python RPC client")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=6000)
    ap.add_argument("--method", default="add")
    ap.add_argument("--params", nargs="*", type=int, default=[2,3])
    args = ap.parse_args()

    call_id = 1
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args.host, args.port))
        send_request(s, call_id, args.method, args.params)
        ver, cid, status, result, err = recv_response(s)
        if status==0:
            print(f"[PY] result={result}")
        else:
            print(f"[PY] error: {err}")
