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
│   ├── DNS_lookup (Record types & Exceptions)
│   └── LDAP (Directory & Authentication)
│
└── 📁 Workshop_4_Coordination
    ├── Centralized UTC Server
    ├── Decentralized P2P Time Sync (peer.py)
    ├── Vector Clocks (Causality tracking)
    └── Mutual Exclusion (Centralized & Token Ring)
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

## 🚀 Technologies & Libraries
*   **Core:** Python 3.11+, GCC Compiler.
*   **Middleware:** [ZeroMQ (pyzmq)](https://zeromq.org/) for high-performance messaging.
*   **Libraries:** `dnspython`, `xmlrpc`, `threading`.

---
*Created with ❤️ by a KevJoss.*