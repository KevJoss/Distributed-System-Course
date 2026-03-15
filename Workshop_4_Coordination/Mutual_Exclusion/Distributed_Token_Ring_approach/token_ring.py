import zmq
import sys
import time
import random

# Definimos el anillo
RING_PORTS = ['5001', '5002', '5003', '5004', '5005']

try:
    MY_PORT = sys.argv[1]
except IndexError:
    print("Usage: python token_ring.py <PORT>")
    sys.exit(1)

# Calculamos quién es el siguiente en el círculo
my_index = RING_PORTS.index(MY_PORT)
next_index = (my_index + 1) % len(RING_PORTS)
NEXT_PORT = RING_PORTS[next_index]

print(f"[NODE] My port: {MY_PORT} | Passing token to: {NEXT_PORT}")

# --- ZMQ SETUP ---
context = zmq.Context()

# Socket to RECEIVE the token (PULL)
receiver = context.socket(zmq.PULL)
receiver.bind(f"tcp://*:{MY_PORT}")

# Socket to SEND the token (PUSH)
sender = context.socket(zmq.PUSH)
sender.connect(f"tcp://localhost:{NEXT_PORT}")

# --- INITIALIZATION ---
# We need someone to start the game. Let's make the first port (5001) 
# the one that creates the token after a short delay (to let others start).
if MY_PORT == '5001':
    print("[INIT] I'm the first node. Generating token in 5 seconds...")
    time.sleep(5)
    sender.send_string("TOKEN")

# --- MAIN LOOP ---
while True:
    print("[WAITING] Waiting for the token...")
    token = receiver.recv_string()
    
    print(f"\n[TOKEN] I have the token! (Received from previous node)")
    
    # --- CRITICAL SECTION SIMULATION ---
    # Decide randomly if we want to use the "Shared Resource"
    if random.choice([True, False]):
        print("[RESOURCE] Entering Critical Section...")
        work_time = random.uniform(1, 3)
        time.sleep(work_time)
        print(f"[RESOURCE] Work done in {work_time:.2f}s. Leaving Critical Section.")
    else:
        print("[RESOURCE] Nothing to do, bypassing Critical Section.")
    
    # --- PASS THE TOKEN ---
    print(f"[SENDING] Passing token to {NEXT_PORT}...")
    time.sleep(1) # Small delay to make logs readable
    sender.send_string("TOKEN")
