-- =============================================================================
-- WORKSHOP 5: DISTRIBUTED DATABASES IMPLEMENTATION
-- This script contains all commands for Replication and Sharding.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- SECTION 1: REPLICATION SETUP (PRIMARY NODE)
-- -----------------------------------------------------------------------------

-- 1.1 Create Replication User
CREATE USER 'replica_user'@'%' IDENTIFIED WITH mysql_native_password BY 'replica_password';
GRANT REPLICATION SLAVE ON *.* TO 'replica_user'@'%';
FLUSH PRIVILEGES;

-- 1.2 Verify Master Status (Required for Replica configuration)
-- Note: Save 'File' and 'Position' values.
SHOW MASTER STATUS;

-- 1.3 Create Test Database to verify link
CREATE DATABASE IF NOT EXISTS db_test_replication;
USE db_test_replication;
CREATE TABLE IF NOT EXISTS test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(100),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO test (description) VALUES ('Initial replication test record');

-- -----------------------------------------------------------------------------
-- SECTION 2: REPLICATION SETUP (REPLICA NODE)
-- -----------------------------------------------------------------------------

-- 2.1 Connect to Primary (Run on Replica)
-- CHANGE MASTER TO 
--   MASTER_HOST='db_primary',
--   MASTER_USER='replica_user',
--   MASTER_PASSWORD='replica_password',
--   MASTER_LOG_FILE='mysql-bin.000001', -- Update with actual file
--   MASTER_LOG_POS=154;                -- Update with actual position
-- START SLAVE;
-- SHOW SLAVE STATUS\G;

-- -----------------------------------------------------------------------------
-- SECTION 3: HORIZONTAL SHARDING (ID PARITY STRATEGY)
-- -----------------------------------------------------------------------------

-- 3.1 Primary Node: Shard 1 (Even IDs)
CREATE DATABASE IF NOT EXISTS users_shard_even;
USE users_shard_even;
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(80)
);
INSERT INTO users VALUES (2, 'Alice', 'alice@example.com'), (4, 'David', 'david@example.com');

-- 3.2 Replica Node: Shard 2 (Odd IDs)
CREATE DATABASE IF NOT EXISTS users_shard_odd;
USE users_shard_odd;
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(80)
);
INSERT INTO users VALUES (1, 'Bob', 'bob@example.com'), (3, 'Charlie', 'charlie@example.com');

-- 3.3 Cross-Shard Query (Run on Replica)
-- SELECT * FROM users_shard_even.users UNION ALL SELECT * FROM users_shard_odd.users;

-- -----------------------------------------------------------------------------
-- SECTION 4: VERTICAL SHARDING (DOMAIN SPECIALIZATION)
-- -----------------------------------------------------------------------------

-- 4.1 Primary Node: Administrative Data
CREATE DATABASE IF NOT EXISTS agro_enterprise_admin;
USE agro_enterprise_admin;
CREATE TABLE IF NOT EXISTS crops_admin (
    id INT PRIMARY KEY,
    crop_name VARCHAR(50),
    planting_date DATE
);
INSERT INTO crops_admin VALUES (1, 'Cacao Fino Aroma', '2024-01-10'), (2, 'Cafe Arabiga', '2024-02-10');

-- 4.2 Replica Node: Sensor Data
CREATE DATABASE IF NOT EXISTS agro_enterprise_sensors;
USE agro_enterprise_sensors;
CREATE TABLE IF NOT EXISTS crops_sensors (
    id INT PRIMARY KEY,
    ph_level DECIMAL(3,1),
    avg_temp DECIMAL(4,1),
    soil_notes TEXT
);
INSERT INTO crops_sensors VALUES 
(1, 6.5, 25.4, 'High hydration clay soil'), 
(2, 5.8, 22.1, 'Volcanic soil, slightly acidic');

-- 4.3 Vertical Fragment Join Query (Run on Replica)
-- SELECT a.*, s.ph_level, s.avg_temp 
-- FROM agro_enterprise_admin.crops_admin a 
-- JOIN agro_enterprise_sensors.crops_sensors s ON a.id = s.id;
