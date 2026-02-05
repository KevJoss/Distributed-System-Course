# Distributed Systems - Workshop 1: Client/Server Architecture

This repository contains the source code for **Workshop 1: Client-Server**, developed for the Distributed Systems course at **Yachay Tech (Semester I 2026)**.

The project demonstrates the implementation of a TCP Client-Server architecture using **Sockets**, focused on robust connection handling, data transmission, and concurrency.

## 📋 Project Overview

The objective of this workshop is to understand the low-level communication protocols by implementing raw sockets in two different programming languages:

1.  **Python:** High-level implementation focused on logic and random data generation.
2.  **C (Windows/Winsock):** Low-level implementation managing memory, headers, and system calls manually.

### Key Features
*   **TCP/IP Communication:** Reliable connection using the 3-way handshake mechanism.
*   **Multithreading:**
    *   **Python:** Uses the `threading` module to handle multiple clients simultaneously.
    *   **C:** Uses the Windows API (`CreateThread`) for concurrent client handling.
*   **Interactive & Automated Clients:**
    *   Clients that send random strings / bulk messages.
    *   Interactive command-line interfaces (CLI) for user input.
*   **Cross-Compatibility:** The Client (C) can talk to the Server (Python) and vice-versa, as they share the standard TCP protocol.

---

## 📂 Project Structure

```text
Workshop_1_Client-Server/
│
├── server-socket_multithreading.py  # Python Server (Handles multiple clients)
├── client_messages_random.py        # Python Client (Sends random burst of strings)
│
└── C_version_client-server/         # C Implementation (Windows)
    ├── server-socket.c              # C Server (Multithreaded with Winsock)
    └── client-socket.c              # C Client (Interactive Loop)
```

---

## 🚀 Usage Instructions

### 1. Python Implementation

Ensure you have **Python 3.x** installed.

**Running the Server:**
The server listens on `127.0.0.1` port `12000`.
```bash
python server-socket_multithreading.py
```

**Running the Client:**
This client generates random strings and sends them to the server.
```bash
python client_messages_random.py
```

---

### 2. C Implementation (Windows)

**Prerequisites:**
*   **OS:** Windows (Code uses `<winsock2.h>` and `<windows.h>`).
*   **Compiler:** GCC (MinGW) or Visual Studio `cl`.

**Compilation:**
You must link the **Winsock library** (`-lws2_32`) during compilation.

> **Compile Server:**
> ```powershell
> gcc C_version_client-server/server-socket.c -o server.exe -lws2_32
> ```

> **Compile Client:**
> ```powershell
> gcc C_version_client-server/client-socket.c -o client.exe -lws2_32
> ```

**Execution:**
1.  Start the Server:
    ```powershell
    .\server.exe
    ```
2.  Start one (or more) Clients in new terminals:
    ```powershell
    .\client.exe
    ```

---

## 🧠 Technical Details

### Multithreading Approach
*   **Server Logic:** The server enters an infinite loop `while(1)` where it waits for connections using `accept()`.
*   **Concurrency:** When a client connects, the server spawns a **new thread** immediately. The main thread goes back to listening, while the new thread handles the specific client's request (Echo/Uppercase processing).

### Data Flow
1.  **Connection:** 3-Way Handshake established on Port 12000.
2.  **Request:** Client sends a text string (e.g., "hello world").
3.  **Processing:** Server receives bytes, converts text to **UPPERCASE** (simulating a service), and waits 3 seconds (simulating workload).
4.  **Response:** Server sends back the processed string (e.g., "HELLO WORLD").
5.  **Termination:** Client can choose to send another message or close the connection (sending TCP FIN).

---

## 👤 Author
**Student:** Kevin Sánchez
**Course:** Distributed Systems
**University:** Yachay Tech
