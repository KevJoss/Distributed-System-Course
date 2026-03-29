# 🔄 Primary-Replica Replication

This document outlines the steps to configure unidirectional replication between `db_primary` and `db_replica`.

## ⚙️ Configuration Steps

### 1. Primary Node Setup
Configuration of binary logs and replication user.

**Commands:**
```sql
-- Check Master Status (Save File and Position)
SHOW MASTER STATUS;

-- Create Replica User
CREATE USER 'replica_user'@'%' IDENTIFIED BY 'replica_password';
GRANT REPLICATION SLAVE ON *.* TO 'replica_user'@'%';
FLUSH PRIVILEGES;
```

---

### 2. Replica Node Linkage
Linking the replica to the primary using the logged position.

**Link Command:**
```sql
CHANGE MASTER TO
  MASTER_HOST='db_primary',
  MASTER_USER='replica_user',
  MASTER_PASSWORD='replica_password',
  MASTER_LOG_FILE='mysql-bin.000001',
  MASTER_LOG_POS=xxxx;

START SLAVE;
```

---

### 3. Verification
Evidence on terminal of database synchronization from Primary to Replica.
