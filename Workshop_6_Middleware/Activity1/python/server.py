#!/usr/bin/env python3
import argparse
from middleware import start_server

def print_handler(msg, addr):
    print(f"[PY] From {addr}:")
    print(f"  version: {msg.get('version')}")
    print(f"  timestamp_ms: {msg.get('timestamp_ms')}")
    print(f"  source_id: {msg.get('source_id')}")
    print(f"  payload: {msg.get('payload')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python middleware server")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    args = parser.parse_args()
    start_server(args.port, print_handler)
