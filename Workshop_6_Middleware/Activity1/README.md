# Activity 1 — Message-Passing Middleware (Python & C)

## Python
### Run server
```bash
cd python
python3 server.py --port 5000
```
### Send a message
```bash
python3 client.py --host 127.0.0.1 --port 5000 --source-id 7 --text "hello from python"
```

## C
### Build
```bash
cd c
make
```
### Run server
```bash
./server 5000
```
### Send a message
```bash
./client 127.0.0.1 5000 42 "hello from C"
```

### Notes
- Both stacks implement a **framed** protocol to avoid partial read issues.
- Python uses **JSON** envelope; C uses a **binary header** plus raw text payload.
- Metadata includes: `version`, `timestamp_ms`, `source_id`, and payload.
