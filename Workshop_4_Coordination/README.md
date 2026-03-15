# Workshop 4: Coordination and Time Synchronization

This workshop explores fundamental challenges in distributed systems: **Clock Synchronization**, **Logical Clocks**, and **Mutual Exclusion**.

## 📁 Contents

1.  **UTC_server**: A centralized model where a master server provides the ground truth time to multiple clients.
2.  **Global_Time_without_UTC_server (`peer.py`)**: A decentralized (Peer-to-Peer) model where nodes synchronize with each other using the Berkeley-like averaging algorithm.
3.  **Vector_Clocks (`vector_clocks.py`)**: Implementation of logical clocks to track causality and event ordering in a distributed system.
4.  **Mutual_Exclusion**:
    *   **Central_Resource_Management_Server**: A centralized coordinator for resource locking.
    *   **Distributed_Token_Ring_approach (`token_ring.py`)**: A decentralized algorithm for distributed locking without a central authority.

---

## 🕒 Peer-to-Peer Synchronization (`peer.py`)

Implementation of a decentralized synchronization system. Every node is simultaneously a **Server** and a **Client**.

### Key Features
*   **Multithreading:** Background daemon thread for ZMQ-REP.
*   **ZeroMQ REQ/REP:** For reliable state exchange.
*   **Latency Compensation:** Cristian's logic (`RTT/2`).
*   **Robustness Filter:** Discards outliers (>10s deviation).

---

## ⌛ Vector Clocks (`vector_clocks.py`)

Logical clocks used to determine the partial ordering of events and detect causality violations.

### Key Features
*   **Internal Events:** Local state changes.
*   **Message Passing:** Sending and receiving timestamps to synchronize logical time.
*   **Causality Tracking:** Comparing vectors to determine if an event happened before, after, or concurrently with another.

---

## 💍 Mutual Exclusion

### 1. Central Resource Management
A coordinator manages a queue of requests for a single shared resource.
*   **Server:** Grants permissions and handles the queue.
*   **Clients:** Request access and wait for the "Grant" signal.

### 2. Token Ring (`token_ring.py`)
Nodes form a logical ring and pass a "Token". Only the token holder can enter the **Critical Section**.
*   **ZeroMQ PUSH/PULL:** High-performance unidirectional messaging.
*   **Circular Topology:** Automatic token passing logic.

---
*Developed as part of the Distributed Systems course at Yachay Tech.*
