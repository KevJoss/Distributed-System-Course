# 🌐 Distributed Systems Workshops

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![C](https://img.shields.io/badge/C-Standard-00599C?style=for-the-badge&logo=c&logoColor=white)
![ZeroMQ](https://img.shields.io/badge/ZeroMQ-Messaging-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

Welcome to the **Distributed Systems** course repository. This repository contains practical implementations and workshops completed during the course at **Yachay Tech**, focusing on inter-process communication, network architectures, and distributed design patterns.

---

## 📂 Repository Structure

```graphql
Distributed_Systems_code
├── 📁 Workshop_1_Client-Server
│   ├── Python Version (TCP/UDP)
│   └── C Version (Sockets)
│
├── 📁 Workshop_2_Communication
│   ├── RMI (Remote Method Invocation)
│   ├── Publisher-Subscriber (ZeroMQ)
│   └── Pipeline/Push-Pull (ZeroMQ Broker)
│
├── 📁 Workshop_3_DNS_LDAP
│   └── DNS_lookup
│
└── 📁 Workshop_4_Coordination
    ├── Centralized UTC Server
    └── Decentralized Peer-to-Peer Time Sync
```

## Workshops Overview

### 1️⃣ Workshop 1: Client-Server Fundamentals
**Focus:** Low-level Socket Programming.
*   Understanding the TCP 3-way handshake.
*   Implementing persistent connections in **C** and **Python**.
*   Handling byte-stream buffering and encoding.

### 2️⃣ Workshop 2: Advanced Patterns
**Focus:** Scalable Architectures with Middleware.
*   **RMI:** Abstracting network calls as local function calls using `xmlrpc`.
*   **Pub-Sub:** Building decoupled systems where publishers don't know subscribers.
*   **Pipeline:** Distributing heavy workloads across multiple workers using a **Broker** architecture.

### 3️⃣ Workshop 3: DNS and LDAP Implementation
**Focus:** Name Resolution and Directory Services.
*   **DNS Lookups:** Querying various DNS records (A, PTR, MX, NS, SOA, CNAME) using Python's `dnspython`.
*   **Custom Resolvers & Errors:** Configuring custom DNS resolvers and handling exceptions like `NXDOMAIN`.

### 4️⃣ Workshop 4: Coordination and Time Synchronization
**Focus:** Clock Synchronization in Distributed Environments.
*   **Centralized UTC Server:** Traditional Client-Server time exchange.
*   **Decentralized P2P Sync:** Implementing coordination using system clocks, ZMQ, and threading without a central server.
*   **Advanced Features:** Network latency compensation (Cristian's logic) and robust outlier filtering.

## 🚀 Technologies & Libraries

*   **Core:** Python 3.11+, GCC Compiler.
*   **Networking:** `socket` (BSD Sockets), `xmlrpc.server`, `dnspython`.
*   **Middleware:** [ZeroMQ (pyzmq)](https://zeromq.org/) for high-performance asynchronous messaging.

## 📦 How to Run

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/your-username/distributed-systems-repo.git
    cd distributed-systems-repo
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Navigate to a specific workshop** and follow its internal `README.md`.

---
*Created with ❤️ by a KevJoss.*