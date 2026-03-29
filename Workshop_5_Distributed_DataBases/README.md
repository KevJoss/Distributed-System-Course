# Workshop 5: Distributed Databases - Replication & Sharding

This workshop implements a distributed MySQL environment using a Primary-Replica architecture and data sharding strategies (Horizontal and Vertical).

## 📂 Project Structure

```text
Workshop_5_Distributed_DataBases/
├── Part_1_Distributed_Databases/
│   ├── Replication_Docs/      # Documentation for Primary-Replica setup
│   ├── Sharding_Docs/         # Documentation for Horizontal & Vertical sharding
│   ├── SQL_Scripts/           # Managed SQL scripts (Part 1)
│   └── docker-compose.yaml     # Infrastructure definition (Part 1)
├── Part_2_Distributed_Databases/
│   ├── SQL_Scripts/           # Managed SQL scripts (Part 2)
│   ├── README.md              # Documentation for Concurrency Control
│   └── docker-compose.yaml     # Infrastructure definition (Part 2 - GTID)
└── README.md                   # Main Overview
```

## 🚀 Execution Guide

### 1. Launch Containers
Ensure you are in the directory of the Part you want to execute:
```bash
docker-compose up -d
```

### 2. Implementation Flow
1. **Replication & Sharding (Part 1):** Follow the [Replication Guide](./Part_1_Distributed_Databases/Replication_Docs/README.md) and [Sharding Guide](./Part_1_Distributed_Databases/Sharding_Docs/README.md).
2. **Concurrency Control (Part 2):** Follow the [Concurrency Control Guide](./Part_2_Distributed_Databases/README.md) to explore Lost Update, Replica Lag, and Deadlocks.

---
*Distributed Systems Workshop - Yachay Tech*
