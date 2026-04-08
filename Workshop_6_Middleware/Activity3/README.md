# Activity 3 — Serialization & Transparency + Naming Service (Python & C)

This activity extends Activity 2 by adding:
- **Complex data serialization** using **JSON-framed RPC** (arrays, objects, scalars).
- **Fault handling** with error responses.
- A **naming registry** so clients can resolve `service_name → host:port`.

Both Python and C share the **same wire format**: a 4-byte big-endian length followed by a UTF‑8 JSON document.

## Python

### 1) Start the registry
```bash
cd python
python3 registry.py  # defaults to port 7001
```

### 2) Start the service and (optionally) register it
```bash
python3 server.py --port 7000 --registry-host 127.0.0.1 --registry-port 7001 --name calc_service
```

### 3) Call methods (with registry lookup)
```bash
python3 client.py --registry-host 127.0.0.1 --registry-port 7001 --service-name calc_service \
  --method sum_list --params '[[1,2,3,4,5]]'

python3 client.py --registry-host 127.0.0.1 --registry-port 7001 --service-name calc_service \
  --method add --params '{"a":7,"b":8}'

python3 client.py --registry-host 127.0.0.1 --registry-port 7001 --service-name calc_service \
  --method echo --params '[{"user":"alice","roles":["student","admin"]}]'
```

> You can also bypass the registry by specifying `--host` and `--port`.

## C

### Build
```bash
cd c
make
```

### 1) Start the registry
./registry --port 7001

### 2) Start the service and (optionally) register it
./server --port 7000 --registry-host 127.0.0.1 --registry-port 7001 --name calc_service


### 3) Call methods (with registry lookup)
```bash
./client --registry-host 127.0.0.1 --registry-port 7001 --service-name calc_service \
  --method sum_list --params-json '[10,20,30]'
./client --registry-host 127.0.0.1 --registry-port 7001 --service-name calc_service \
  --method add --params-json '{"a":2,"b":9}'
./client --registry-host 127.0.0.1 --registry-port 7001 --service-name calc_service \
  --method echo --params-json '{"msg":"hello","arr":[1,2,3]}'
```

### Notes on the C server
- It **parses ints** from objects for `add`/`multiply` and **arrays of ints** for `sum_list`.
- `echo` simply returns the params JSON as the result (demonstrates transporting complex objects without deep parsing).
- Error handling returns a JSON error message.

## Cross-language
- Start the **C server**, use the **Python client** (or vice versa). The JSON wire format is shared, so interop works.

---

Have fun exploring **serialization choices** and how a **naming registry** improves *location transparency*!
