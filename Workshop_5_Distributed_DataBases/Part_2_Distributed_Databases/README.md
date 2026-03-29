# 🛡️ Concurrency Control & Replica Lag

This section documents the exploration of common anomalies in distributed databases and their solutions using MySQL 8.x.

## 📋 Experiments & Solutions

### 1. Lost Update Anomaly
Demonstrates how concurrent transactions can overwrite each other without proper locking.

**Impact:** Data loss (e.g., balance updates being ignored).

**Solution:** **Pessimistic Locking** (`SELECT ... FOR UPDATE`).

---

### 2. Replica Lag (Consistency)
Solves the "inconsistency of reading after writing" by coordinating the replica with the primary's GTID.

**Commands Used:**
```sql
-- On Primary:
SELECT @@GLOBAL.gtid_executed;

-- On Replica:
SELECT WAIT_FOR_EXECUTED_GTID_SET('<GTID>', 5);
```

---

### 3. Deadlock (The Deadly Embrace)
Forces a circular lock wait and observes the InnoDB Deadlock Detector in action.

**Error Found:** `ERROR 1213 (40001): Deadlock found when trying to get lock`.

**Solution:** **Consistent Locking Order**. By ensuring all transactions lock IDs in the same order (increasing), the circular dependency is impossible.

## 🏗️ Infrastructure
This part uses a specific `docker-compose.yaml` with **GTID Mode enabled** and **ROW-based binlogging**.

```bash
docker-compose up -d
```
