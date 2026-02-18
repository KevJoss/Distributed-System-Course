# Workshop 2: Communication Patterns in Distributed Systems

This directory contains the implementation of three fundamental communication patterns in distributed systems using **Python** and the **xmlrpc** and **ZeroMQ (zmq)** libraries.

## Workshop Structure

The workshop is divided into three parts, each exploring a different communication architecture:

### 1. RMI (Remote Method Invocation)
Location: `./RMI/`

In this section, a Client-Server system is implemented where the client invokes methods that execute remotely on the server using the **XML-RPC** protocol.

*   **`complex_number_manager_server.py`**: 
    *   Acts as an RPC Server.
    *   Exposes mathematical functions to operate with complex numbers (addition, subtraction, multiplication, division).
    *   Handles data serialization so complex types can be transmitted via XML.
*   **`complex_number_manager_client.py`**: 
    *   Client that connects to the RPC server.
    *   Invokes remote methods as if they were local functions.
    *   Handles responses and errors (such as division by zero).

---

### 2. Publisher-Subscriber (Pub-Sub)
Location: `./Publisher_Subscriber/`

This architecture demonstrates an asynchronous "one-to-many" messaging model, where senders (Publishers) do not know the receivers (Subscribers).

*   **`multiple_publishers.py`**:
    *   Simulates multiple services (SysAdmin, Finance, IoT, News) publishing information.
    *   Uses a `zmq.PUB` socket to broadcast messages with different "Topics".
*   **`multiple_subscriber.py`**:
    *   Client that subscribes to one or more specific topics using `zmq.SUB`.
    *   Filters messages on the client side (receives only what is of interest).
    *   Demonstrates dynamic subscription capabilities to multiple information sources.

---

### 3. Pipeline (Push-Pull)
Location: `./Pipeline_communication/`

Implementation of a parallel processing and task distribution pattern (Fan-out/Worker), using an intermediary **Broker** to decouple producers and consumers.

*   **`broker.py`**:
    *   The central intermediary.
    *   Uses a `zmq.PULL` socket (Frontend) to receive tasks from Sources.
    *   Uses a `zmq.PUSH` socket (Backend) to distribute tasks to Workers.
    *   Utilizes `zmq.proxy` to efficiently relay messages.
*   **`source.py`**:
    *   Task generator (Boss).
    *   Connects to the Broker and sends serialized workloads.
*   **`worker.py`**:
    *   Task processor (Worker).
    *   Connects to the Broker, receives tasks, and simulates processing.
    *   Scalable: You can run multiple workers to process tasks in parallel.

## Requirements

*   Python 3.x
*   `pyzmq` library (`pip install pyzmq`)

## Execution

Each section is designed to be run in separate terminals to simulate the different nodes of the distributed system.
