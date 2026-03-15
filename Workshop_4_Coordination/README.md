# Workshop 4: Coordination and Time Synchronization

This workshop explores one of the most fundamental challenges in distributed systems: **Clock Synchronization**. In a world without a perfectly shared global clock, nodes must coordinate to agree on a common sense of time.

## 📁 Contents

1.  **UTC_server**: A centralized model where a master server provides the ground truth time to multiple clients.
2.  **Global_Time_without_UTC_server (`peer.py`)**: A decentralized (Peer-to-Peer) model where nodes synchronize with each other using the Berkeley-like averaging algorithm.

---

## 🕒 Peer-to-Peer Synchronization (`peer.py`)

The `peer.py` script implements a fully decentralized synchronization system. Every node is simultaneously a **Server** (answering time requests) and a **Client** (polling neighbors for their time).

### Key Features

*   **Multithreading:** Uses a background daemon thread to handle incoming ZMQ-REP requests while the main thread manages the client polling cycle.
*   **ZeroMQ REQ/REP:** High-performance messaging pattern for reliable request-reply interactions between peers.
*   **Network Latency Compensation:** Implements logic inspired by **Cristian's Algorithm**. It measures the Round-Trip Time (RTT) and adjusts the received time by `RTT/2` to account for transmission delay.
*   **Robustness Filter:** To prevent a single faulty node from corrupting the network, the script discards any received time that deviates by more than a defined threshold (10 seconds) from the local clock.
*   **Drift Simulation:** Periodically injects a random drift into the local clock to simulate hardware imperfections, ensuring the synchronization algorithm is constantly challenged.

### How to Run

1.  Open multiple terminal windows.
2.  Run several instances of the script using different ports from the allowed list (`5001-5005`):
    ```bash
    python peer.py 5001
    python peer.py 5002
    python peer.py 5003
    ```
3.  Observe how the nodes detect each other, exchange times, and converge to a common average despite the simulated clock drift and network latency.

---
*Developed as part of the Distributed Systems course at Yachay Tech.*
