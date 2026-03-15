import zmq
import sys
import time
import threading
import random

# --- GLOBALS ---
clock_offset = 0.0 

def get_local_time():
    """Returns the simulated local time (system time + offset)."""
    global clock_offset
    return time.time() + clock_offset

# --- CONFIGURATION ---
ALL_PORTS = ['5001', '5002', '5003', '5004', '5005']

try: 
    NODE_PORT = sys.argv[1]
except IndexError:
    print("Error: Missing parameter.")
    print("Usage: python peer.py <PORT>")
    sys.exit(1)

if NODE_PORT not in ALL_PORTS:
    print(f"Error: Invalid Port. Please choose from: {ALL_PORTS}")
    sys.exit(1)

# List of neighbor ports (all available ports except my own)
NEIGHBOR_PORTS = [p for p in ALL_PORTS if p != NODE_PORT]

# --- SERVER THREAD ---
def server_logic(listen_port):
    """
    This thread acts as the server, listening for time requests from other peers.
    """
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{listen_port}")
    print(f"[SERVER] Listening on port {listen_port}...")

    while True:
        # Wait for a request
        request_msg = socket.recv_string()
        
        # Respond with our adjusted local time
        current_time_str = str(get_local_time())
        socket.send_string(current_time_str)

# Start the background server thread
server_thread_instance = threading.Thread(target=server_logic, args=(NODE_PORT,))
server_thread_instance.daemon = True
server_thread_instance.start()

# --- CLIENT LOGIC (MAIN THREAD) ---
print(f"[CLIENT] Starting clock synchronization node on port {NODE_PORT}...")
zmq_context = zmq.Context()

while True:
    received_times = []
    
    # 1. Capture our own current time to include in the average
    start_time = get_local_time()
    received_times.append(start_time)

    # 2. Poll neighbors for their times
    for p in NEIGHBOR_PORTS:
        client_socket = zmq_context.socket(zmq.REQ)
        # Set a 1-second timeout for receiving messages
        client_socket.setsockopt(zmq.RCVTIMEO, 1000) 
        
        try:
            client_socket.connect(f"tcp://localhost:{p}")
            
            # --- LATENCY MEASUREMENT START ---
            request_time = time.time()  # Monitor send time
            client_socket.send_string("TIME_REQUEST")
            
            response = client_socket.recv_string()
            arrival_time = time.time()  # Monitor receive time
            
            # Total Round-Trip Time (delay)
            rtt = arrival_time - request_time
            # Assumption: The server captured the time at exactly RTT/2
            latency_compensated_time = float(response) + (rtt / 2)
            
            received_times.append(latency_compensated_time)
            print(f"[CLIENT] Neighbor {p}: Time={response}, RTT={rtt:.6f}s, Adjusted={latency_compensated_time:.4f}")
            # --- LATENCY MEASUREMENT END ---
        except zmq.Again:
            print(f"[CLIENT] Neighbor on port {p} is offline.")
        finally:
            client_socket.close()

    # --- COORDINATION ALGORITHM (AVERAGING WITH ROBUSTNESS FILTER) ---
    MAX_DEVIATION = 10.0  # Seconds. Any peer beyond this is considered "faulty" or "malicious"
    
    # Filter received times to exclude outliers
    valid_times = []
    for t in received_times:
        if abs(t - start_time) < MAX_DEVIATION:
            valid_times.append(t)
        else:
            print(f"[SECURITY] Discarding outlier time from neighbor: {t:.4f} (Too far from local clock)")

    if len(valid_times) > 1:
        # Calculate the average only using the "sane" nodes
        average_time = sum(valid_times) / len(valid_times)
        time_adjustment = average_time - start_time
        clock_offset += time_adjustment
        
        print(f"\n[CLOCK] Synchronizing: Average={average_time:.4f}, Adjustment Applied={time_adjustment:.4f}")
    else:
        print("\n[CLOCK] No valid neighbors (within tolerance) for synchronization.")

    print(f"[CLOCK] Current Adjusted Local Time: {get_local_time():.4f}")
    print("-" * 60)
    
    # Wait before the next synchronization cycle
    time.sleep(5)

    # --- RANDOM DRIFT SIMULATION ---
    # We simulate hardware clock imperfection by adding a random drift
    drift_value = random.uniform(-0.1, 0.1)
    clock_offset += drift_value
    print(f"[DRIFT] Random desynchronization of {drift_value:.4f} seconds added.")
