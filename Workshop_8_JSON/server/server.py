import socket
import json
import time
import jsonschema
from jsonschema import validate
from schemas import INITIAL_CONNECT_SCHEMA, MATCH_FOUND_RESPONSE_SCHEMA

SERVER_IP = "0.0.0.0"
TCP_PORT_SERVER = 8080


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, TCP_PORT_SERVER))
    server_socket.listen(1)

    print(f"[SERVER] Listening on {SERVER_IP}:{TCP_PORT_SERVER}...")

    while True:
        conn, addr = server_socket.accept()
        print(f"\n[SERVER] Client connected from {addr}")
        handle_client(conn)


def handle_client(conn):
    buffer = ""
    try:
        while True:
            data = conn.recv(4096).decode("utf-8")
            if not data:
                break

            buffer += data
            if "\n" in buffer:
                parts = buffer.split("\n")
                buffer = parts.pop()

                for packet in parts:
                    if not packet.strip():
                        continue

                    # Start measuring server processing overhead
                    start_overhead = time.perf_counter_ns()

                    try:
                        req_dict = json.loads(packet)
                    except json.JSONDecodeError:
                        print("[SERVER ERROR] Invalid JSON received.")
                        continue

                    event_type = req_dict.get("type", "UNKNOWN")

                    # ---------------------------------------------------------
                    # ACTIVITY 1: Request with Schema Validation
                    # ---------------------------------------------------------
                    if event_type == "INITIAL_CONNECT":
                        print(f"\n[SERVER - ACTIVITY 1] Received {event_type}")
                        try:
                            # 1. Validate incoming request
                            validate(instance=req_dict, schema=INITIAL_CONNECT_SCHEMA)
                            print(" -> Request validation PASSED")

                            # 2. Build response
                            response_dict = {
                                "type": "MATCH_FOUND",
                                "payload": {
                                    "you": req_dict["payload"]["player_id"],
                                    "opponent": "Enemy_Bot",
                                    "session_id": "sess-9999",
                                    "global_player_id": 1,
                                },
                            }

                            # 3. Validate outgoing response
                            validate(
                                instance=response_dict,
                                schema=MATCH_FOUND_RESPONSE_SCHEMA,
                            )
                            print(" -> Response validation PASSED")

                        except jsonschema.exceptions.ValidationError as e:
                            print(f" -> [VALIDATION ERROR] {e.message}")
                            continue

                    # ---------------------------------------------------------
                    # ACTIVITY 2: Request without Schema
                    # ---------------------------------------------------------
                    elif event_type == "BUY_UNIT":
                        print(
                            f"\n[SERVER - ACTIVITY 2] Received {event_type} (No Schema)"
                        )

                        # Process logic directly
                        unit_type = req_dict["payload"]["unit_type"]

                        # Build response without validation
                        response_dict = {
                            "type": "BUY_UNIT_RESULT",
                            "status": "accepted",
                            "payload": {
                                "unit_id": 1001,
                                "spawn_x": 300,
                                "spawn_y": 450,
                                "new_balance": 500,
                            },
                        }

                    else:
                        print(f"[SERVER] Unknown event: {event_type}")
                        continue

                    # Serialize and measure total overhead for this transaction
                    response_json = json.dumps(response_dict) + "\n"

                    end_overhead = time.perf_counter_ns()
                    processing_us = (end_overhead - start_overhead) / 1000.0

                    print(f" -> Server Processing Overhead: {processing_us:.2f} µs")

                    # Send response back to client
                    conn.send(response_json.encode("utf-8"))

    except ConnectionResetError:
        print("[SERVER] Client disconnected abruptly.")
    except Exception as e:
        print(f"[SERVER] Error: {e}")
    finally:
        conn.close()
        print("[SERVER] Connection closed. Waiting for new client...")


if __name__ == "__main__":
    start_server()