import zmq, time, random

context = zmq.Context()
publisher = context.socket(zmq.PUB)

HOST = 'localhost'
PORT = '15000'

p = "tcp://" + HOST + ":" + PORT
publisher.bind(p)

while True:
    time.sleep(1)

    # 1. Publisher for SysAdmin
    cpu = random.randint(0,100)
    ram = random.randint(8,32)
    publisher.send_string(f"SYSADMIN CPU usage: {cpu}%")
    publisher.send_string(f"SYSADMIN RAM usage: {ram}%")

    # 2. Publisher for finance
    market_shares = random.uniform(150.0, 200.0)
    publisher.send_string(f"STOCK Amazon stock market shares today: {market_shares:.2f}")

