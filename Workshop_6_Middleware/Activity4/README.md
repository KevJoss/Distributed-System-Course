
# Middleware Workshop — RabbitMQ (Message-Oriented Middleware)

**Message-Oriented Middleware** using **RabbitMQ**. 

## Contents
```
Middleware-RabbitMQ-Workshop/
├─ README.md                  ← this file
├─ python-basic/              ← queue (point-to-point) example
│  ├─ producer.py
│  ├─ consumer.py
│  └─ requirements.txt
├─ python-pubsub/             ← pub/sub (fanout) example
│  ├─ pub.py
│  ├─ sub.py
│  └─ requirements.txt
└─ c-basic/                   ← minimal C producer/consumer
   ├─ c_producer.c
   ├─ c_consumer.c
   └─ Makefile
```

---

## 0) Prerequisites (choose one path)

### A) Native install (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y rabbitmq-server python3 python3-pip build-essential librabbitmq-dev
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
sudo systemctl status rabbitmq-server --no-pager
```

Enable the management UI (dashboard):
```bash
sudo rabbitmq-plugins enable rabbitmq_management
# Dashboard: http://localhost:15672
# Default user: guest / pass: guest (only from localhost by default)
```

Create a user for remote access (optional but recommended):
```bash
sudo rabbitmqctl add_user student student123
sudo rabbitmqctl set_user_tags student administrator
sudo rabbitmqctl set_permissions -p / student ".*" ".*" ".*"
```

Open firewall if needed:
```bash
sudo ufw allow 5672   # AMQP
sudo ufw allow 15672  # Management UI
```

### B) Docker (any OS with Docker)
```bash
docker run -d --name rabbit   -p 5672:5672 -p 15672:15672   rabbitmq:3-management
# Dashboard: http://localhost:15672  (user: guest, pass: guest)
```

### C) Windows (Chocolatey)
Open an elevated PowerShell:
```powershell
choco install rabbitmq
rabbitmq-plugins enable rabbitmq_management
```
Dashboard at `http://localhost:15672`.

---

## 1) Python — Queue (point-to-point)

Install dependencies:
```bash
cd python-basic
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start a consumer:
```bash
python consumer.py
```
In another terminal, send a message:
```bash
python producer.py
```

**Across two machines:** replace `'localhost'` in scripts with the **broker IP** and ensure ports **5672**/**15672** are reachable.

---

## 2) Python — Pub/Sub (fanout broadcast)

Install deps:
```bash
cd python-pubsub
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start two subscribers (two terminals or two machines):
```bash
python sub.py
python sub.py
```
Publish a message (new terminal):
```bash
python pub.py "hello to everyone"
```
Both subscribers should display the message.

---

## 3) C — Minimal producer/consumer (optional)

Build:
```bash
cd c-basic
make
```

Run in separate terminals:
```bash
./c_consumer
./c_producer
```

> If `librabbitmq-dev` was not found, install it (Ubuntu/Debian):  
> `sudo apt install -y librabbitmq-dev build-essential`

---

## 4) Management UI (proof of work)

Open http://localhost:15672 → **Queues** tab: you should see a queue `hello` with message rates.  
Pub/Sub: check **Exchanges** → `logs` (fanout).  
Take screenshots for your deliverables.

---

## 5) Troubleshooting

- **Remote login with `guest` fails**  
  By default, `guest` can only log in from localhost. Create a new user (e.g., `student`) as shown above.

- **Consumer prints nothing**  
  Ensure queue names match exactly; if you used manual acknowledgments, call `basic_ack`. Check firewall.

- **Persistence expectations**  
  For durability across broker restarts: declare **durable queues** and use `delivery_mode=2` for messages. Persistence applies after the broker flushes to disk.

- **Network issues**  
  Use broker IP rather than hostname. Open ports **5672/15672** on the broker host. Verify connectivity with `telnet BROKER_IP 5672` or `nc -vz BROKER_IP 5672`.

---
