# 🌐 Distributed Systems Workshops

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![C](https://img.shields.io/badge/C-Standard-00599C?style=for-the-badge&logo=c&logoColor=white)
![ZeroMQ](https://img.shields.io/badge/ZeroMQ-Messaging-orange?style=for-the-badge)
![lxml](https://img.shields.io/badge/lxml-XML%20Processing-green?style=for-the-badge)
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
│   ├── DNS_lookup (Record types & Exceptions)
│   └── LDAP (Directory & Authentication)
│
├── 📁 Workshop_4_Coordination
│   ├── Centralized UTC Server
│   ├── Decentralized P2P Time Sync (peer.py)
│   ├── Vector Clocks (Causality tracking)
│   └── Mutual Exclusion (Centralized & Token Ring)
│
├── 📁 Workshop_5_Distributed_DataBases
│   ├── Part 1: Primary-Replica Replication & Sharding
│   └── Part 2: Concurrency Control (Lost Updates, Lag, Deadlocks)
│
├── 📁 Workshop_6_Middleware
│   ├── Activity1: Binary RPC Middleware (Python ↔ C, struct.pack)
│   ├── Activity2: JSON-RPC over TCP (Python ↔ C)
│   ├── Activity3: Function Registry & Dynamic Dispatch
│   └── Activity4: Message Queues (Redis Pub/Sub & Push-Pull, Python & C)
│
└── 📁 Workshop_7_XML
    ├── schemas/ingestion.xsd  (External upload contract)
    ├── schemas/internal.xsd   (Internal routing contract)
    └── test_parser.py         (Pipeline simulation)
```

## Workshops Overview

### 1️⃣ Workshop 1: Client-Server Fundamentals
**Focus:** Low-level programming with Sockets in C (Winsock) and Python.

### 2️⃣ Workshop 2: Advanced Patterns
**Focus:** Scalable Architectures with Middleware (ZeroMQ). Includes RMI, Pub-Sub, and Pipeline patterns.

### 3️⃣ Workshop 3: DNS and LDAP Implementation
**Focus:** Name Resolution and Directory Services. Programmatic DNS queries and LDAP authentication logic.

### 4️⃣ Workshop 4: Coordination, Logical Time & Mutual Exclusion
**Focus:** Handling Time and Shared Resources.
*   **Clock Sync:** Centralized (UTC) and Decentralized (Berkeley-like) synchronization.
*   **Logical Time:** Vector Clocks for causality tracking.
*   **Mutual Exclusion:** Managing shared resource access via Centralized Coordinators and Decentralized Token Rings.

### 5️⃣ Workshop 5: Distributed Databases (Scalability & Consistency)
**Focus:** Data Partitioning and Concurrency in a Distributed Environment.
*   **Replication & Sharding:** Implementing Primary-Replica redundancy and Horizontal/Vertical sharding.
*   **Concurrency Control:** Analyzing and solving anomalies like Lost Updates, Replica Lag, and Deadlocks using GTID and MySQL Row-level locking.

### 6️⃣ Workshop 6: Middleware & Message Queues
**Focus:** Cross-language RPC and asynchronous messaging patterns.
*   **Binary RPC:** Custom middleware using `struct.pack` for serialization between Python and C.
*   **JSON-RPC:** Human-readable RPC protocol over raw TCP sockets.
*   **Function Registry:** Dynamic dispatch with a server-side registry pattern.
*   **Message Queues:** Redis-based Push-Pull and Pub-Sub patterns in both Python and C.

### 7️⃣ Workshop 7: XML Schema Validation & Message Routing
**Focus:** Enforcing data contracts in a distributed pipeline using XSD schemas.
*   **Schema Validation:** `lxml`-based validator wrapping two XSD contracts (ingestion & internal).
*   **Pipeline Simulation:** End-to-end flow from external client upload → Broker validation → internal queue → Router Worker classification.
*   **Security Testing:** Rejection of malformed/malicious payloads at the schema boundary.

## 🚀 Technologies & Libraries
*   **Core:** Python 3.11+, GCC Compiler.
*   **Databases:** MySQL 8.0+, Docker & Docker Compose.
*   **Messaging:** [ZeroMQ (pyzmq)](https://zeromq.org/), Redis (Push-Pull & Pub-Sub).
*   **XML Processing:** `lxml` with XSD schema validation.
*   **Libraries:** `dnspython`, `xmlrpc`, `threading`, `struct`.

---
*Created with ❤️ by KevJoss.*