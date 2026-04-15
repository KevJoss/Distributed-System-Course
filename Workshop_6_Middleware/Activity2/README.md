# Activity 2 — RPC-like Middleware (Python & C, interoperable)

## Methods
- add(a,b)
- multiply(a,b)
- fib(n)
- pow(a,b) with b>=0

## Python
```bash
cd python
python3 server.py --port 6000
python3 client.py --host 127.0.0.1 --port 6000 --method add --params 2 3
python3 client.py --host 127.0.0.1 --port 6000 --method fib --params 10
```

## C
```bash
cd c
make
./server 6000
./client 127.0.0.1 6000 add 4 5
./client 127.0.0.1 6000 fib 10
```

## Cross-language
- Start C server: `./server 6000`
- Python client: `python3 ../python/client.py --host 127.0.0.1 --port 6000 --method multiply --params 6 7`
