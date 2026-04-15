#!/usr/bin/env python3
import argparse, json, socket
from rpc_json import call, send_json, recv_json

def lookup(reg_host, reg_port, name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((reg_host, reg_port))
        send_json(s, {"op":"lookup","name":name})
        resp = recv_json(s)
        if resp.get("status")!="ok": raise RuntimeError(resp.get("error","lookup failed"))
        return resp["host"], int(resp["port"])

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Python JSON-RPC client with naming lookup (Activity 3)")
    ap.add_argument("--host", default=None, help="Service host; if omitted, use registry lookup")
    ap.add_argument("--port", type=int, default=None, help="Service port; if omitted, use registry lookup")
    ap.add_argument("--method", default="sum_list")
    ap.add_argument("--params", default='[1,2,3]', help="JSON parameters (list/dict/scalar)")
    ap.add_argument("--registry-host", default="127.0.0.1")
    ap.add_argument("--registry-port", type=int, default=7001)
    ap.add_argument("--service-name", default="calc_service")
    args = ap.parse_args()

    host, port = args.host, args.port
    if host is None or port is None:
        host, port = lookup(args.registry_host, args.registry_port, args.service_name)
        print(f"[PY] Resolved {args.service_name} -> {host}:{port}")

    params = json.loads(args.params)
    resp = call(host, port, args.method, params)
    print(json.dumps(resp, indent=2))
