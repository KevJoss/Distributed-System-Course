#!/usr/bin/env python3
import argparse
from middleware import send_message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python middleware client")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=5000, help="Server port")
    parser.add_argument("--source-id", type=int, default=1, help="Source ID")
    parser.add_argument("--text", default="hello from python client", help="Payload text message")
    args = parser.parse_args()

    payload = {"type": "text", "message": args.text}
    send_message(args.host, args.port, args.source_id, payload)
    print("[PY] Message sent.")
