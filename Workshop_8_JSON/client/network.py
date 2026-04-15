import socket
import json
import time
import jsonschema
from jsonschema import validate
from config import Config


class NetworkManager:
    def __init__(self):
        self.client_tcp = None
        self.connected = False
        self.receive_buffer = ""
        self.pending_transactions = {}  # Stores timestamps for RTT calculation

    def connect(self):
        self.client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_tcp.settimeout(5.0)
        try:
            self.client_tcp.connect((Config.SERVER_IP, Config.TCP_PORT_SERVER))
            self.client_tcp.setblocking(False)
            self.connected = True
            print("[NETWORK] Connected to server successfully.")
            return True
        except Exception as e:
            print(f"[NETWORK] Connection failed: {e}")
            self.connected = False
            return False

    def send_json(self, data_dictionary, schema=None):
        if not self.connected:
            return

        event_type = data_dictionary.get("type", "UNKNOWN")

        # ACTIVITY 1: Validation
        if schema:
            try:
                validate(instance=data_dictionary, schema=schema)
                print(f"[VALIDATION] Schema validation PASSED for {event_type}")
            except jsonschema.exceptions.ValidationError as e:
                print(f"[VALIDATION ERROR] JSON does not match schema: {e.message}")
                return

        try:
            # Measure Serialization Overhead
            start_overhead = time.perf_counter_ns()
            message = json.dumps(data_dictionary) + "\n"
            end_overhead = time.perf_counter_ns()
            serialization_time_us = (end_overhead - start_overhead) / 1000.0

            # Measure Data Amount (Bytes)
            byte_size = len(message.encode("utf-8"))

            print(f"\n[METRICS - SEND] Event: {event_type}")
            print(f" -> Size Transferred: {byte_size} bytes")
            print(f" -> Serialization Overhead: {serialization_time_us:.2f} µs")

            # Store timestamp for latency
            self.pending_transactions[event_type] = time.perf_counter()
            self.client_tcp.send(message.encode("utf-8"))

        except Exception as e:
            print(f"Error sending data: {e}")

    def receive_json(self, schema=None):
        if not self.connected:
            return None

        try:
            data = self.client_tcp.recv(4096).decode("utf-8")
            if data:
                self.receive_buffer += data
                if "\n" in self.receive_buffer:
                    parts = self.receive_buffer.split("\n")
                    self.receive_buffer = parts.pop()

                    for json_packet in parts:
                        if json_packet.strip():
                            # Measure Deserialization Overhead
                            start_overhead = time.perf_counter_ns()
                            parsed_json = json.loads(json_packet)
                            end_overhead = time.perf_counter_ns()

                            deserialization_time_us = (
                                end_overhead - start_overhead
                            ) / 1000.0
                            response_type = parsed_json.get("type", "UNKNOWN")

                            # Calculate Latency (RTT)
                            latency_ms = 0.0
                            # Map response back to request (e.g., JOIN_REQUEST -> QUEUE_STATUS)
                            request_key = (
                                "JOIN"
                                if response_type in ["QUEUE_STATUS", "MATCH_FOUND"]
                                else response_type.replace("_RESULT", "")
                            )

                            if request_key in self.pending_transactions:
                                latency_ms = (
                                    time.perf_counter()
                                    - self.pending_transactions[request_key]
                                ) * 1000.0
                                del self.pending_transactions[request_key]

                            print(f"\n[METRICS - RECV] Event: {response_type}")
                            print(
                                f" -> Deserialization Overhead: {deserialization_time_us:.2f} µs"
                            )
                            if latency_ms > 0:
                                print(
                                    f" -> Transfer Latency (RTT): {latency_ms:.2f} ms"
                                )

                            # ACTIVITY 1: Validation on received data
                            if schema:
                                try:
                                    validate(instance=parsed_json, schema=schema)
                                    print(
                                        f"[VALIDATION] Schema validation PASSED for received {response_type}"
                                    )
                                except jsonschema.exceptions.ValidationError as e:
                                    print(
                                        f"[VALIDATION ERROR] Received JSON invalid: {e.message}"
                                    )
                                    return None

                            return parsed_json

        except BlockingIOError:
            pass
        except Exception as e:
            print(f"Error receiving data: {e}")
            self.connected = False

        return None
