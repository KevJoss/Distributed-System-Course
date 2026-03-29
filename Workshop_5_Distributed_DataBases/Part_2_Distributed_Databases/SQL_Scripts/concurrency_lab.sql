-- =============================================================================
-- WORKSHOP 5 - PART 2: CONCURRENCY CONTROL & REPLICA LAG
-- =============================================================================

-- -----------------------------------------------------------------------------
-- SECTION 1: INFRASTRUCTURE & REPLICATION SETUP
-- -----------------------------------------------------------------------------

-- [PRIMARY NODE] Create replication user
CREATE USER IF NOT EXISTS 'repl'@'%' IDENTIFIED WITH mysql_native_password BY 'repl';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
FLUSH PRIVILEGES;

-- [REPLICA NODE] Connect to Primary via GTID
-- STOP REPLICA;
-- CHANGE REPLICATION SOURCE TO
--   SOURCE_HOST='mysql-primary',
--   SOURCE_USER='repl',
--   SOURCE_PASSWORD='repl',
--   SOURCE_AUTO_POSITION=1;
-- START REPLICA;
-- SHOW REPLICA STATUS\G

-- -----------------------------------------------------------------------------
-- SECTION 2: INITIAL DATA SEEDING (Run on Primary)
-- -----------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS lab;
USE lab;

DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    id INT PRIMARY KEY,
    owner VARCHAR(50),
    balance INT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

INSERT INTO accounts (id, owner, balance) VALUES (1, 'Alice', 1000), (2, 'Bob', 1000);

-- -----------------------------------------------------------------------------
-- SECTION 3: LOST UPDATE ANOMALY
-- -----------------------------------------------------------------------------

-- SCENARIO: Two concurrent sessions read 1000 and calculate based on that stale value.

-- Session A:
-- SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- START TRANSACTION;
-- SELECT balance FROM accounts WHERE id = 1; -- Returns 1000
-- UPDATE accounts SET balance = 1100 WHERE id = 1;

-- Session B:
-- SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- START TRANSACTION;
-- SELECT balance FROM accounts WHERE id = 1; -- Still returns 1000 (Anomaly!)
-- UPDATE accounts SET balance = 950 WHERE id = 1; -- Will wait for Session A
-- COMMIT;

-- -----------------------------------------------------------------------------
-- SECTION 4: SOLUTION - PESSIMISTIC LOCKING
-- -----------------------------------------------------------------------------

-- Session A:
-- START TRANSACTION;
-- SELECT balance FROM accounts WHERE id = 1 FOR UPDATE; -- Blocks others from read/write
-- UPDATE accounts SET balance = balance + 100 WHERE id = 1;
-- COMMIT;

-- Session B: 
-- START TRANSACTION;
-- SELECT balance FROM accounts WHERE id = 1 FOR UPDATE; -- Waits immediately here
-- UPDATE accounts SET balance = balance - 50 WHERE id = 1;
-- COMMIT;

-- -----------------------------------------------------------------------------
-- SECTION 5: REPLICA LAG & GTID COORDINATION
-- -----------------------------------------------------------------------------

-- [PRIMARY] Get executed GTID set after a write
-- UPDATE accounts SET balance = balance + 1 WHERE id = 1;
-- SELECT @@GLOBAL.gtid_executed\G -- Copy this value

-- [REPLICA] Wait for the specific transaction before reading
-- SELECT WAIT_FOR_EXECUTED_GTID_SET('<PASTED_GTID>', 5);
-- SELECT * FROM accounts WHERE id = 1;

-- -----------------------------------------------------------------------------
-- SECTION 6: DEADLOCK DEMONSTRATION & FIX
-- -----------------------------------------------------------------------------

-- [Primary] Setup
-- UPDATE accounts SET balance = 1000 WHERE id IN (1, 2);

-- ANOMALY: Opposite locking order
-- Session A: UPDATE id=1 -> SLEEP(2) -> UPDATE id=2
-- Session B: UPDATE id=2 -> SLEEP(2) -> UPDATE id=1 (DEADLOCK!)

-- FIX: Consistent locking order
-- Both sessions: SELECT * FROM accounts WHERE id IN (1, 2) FOR UPDATE;
-- (MySQL locks in ascending ID order, preventing the cycle).
