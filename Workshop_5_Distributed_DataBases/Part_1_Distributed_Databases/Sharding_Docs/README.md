# 🏗️ Data Sharding: Horizontal & Vertical

This section explores how to partition databases across multiple nodes to improve performance and scalability.

## ↔️ Horizontal Sharding
Data is split by rows. In this workshop, we use **ID Parity** (Even IDs on Primary, Odd IDs on Replica).

### Implementation
Run the sharding script to distribute data.


### Cross-Shard Query
To view the complete dataset, we use a `UNION ALL` operation on the replica node.
```sql
SELECT * FROM node_primary.sensors
UNION ALL
SELECT * FROM node_replica.sensors;
```

---

## ↕️ Vertical Sharding
Data is split by domain/columns. Administrative data stays on the Primary, while high-frequency sensor data is replicated/sharded to the Replica.

### Implementation
Joining tables across different specialized databases/nodes.

### Cross-Shard Query
```sql
SELECT * FROM agro_enterprise_sensors.cultivos_sensores 
JOIN agro_enterprise_admin.cultivos ON id_cultivo = id;
```
