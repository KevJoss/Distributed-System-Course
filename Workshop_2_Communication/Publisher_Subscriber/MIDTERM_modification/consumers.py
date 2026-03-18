import sys
import zmq

if len(sys.argv) < 2:
    print("Use: python consumer.py <service_name>")
    sys.exit()

service_name = sys.argv[1]

context = zmq.Context()

print(f"Searching for service '{service_name}'...")

socket_QUERY = context.socket(zmq.REQ)
socket_QUERY.setsockopt(zmq.RCVTIMEO, 3000)

query = {
    "type": 'query',
    "service_name": service_name
}

publisher_info = None

try:
    print("Trying main server (port 5555)...")
    socket_QUERY.connect("tcp://localhost:5555")
    socket_QUERY.send_json(query)
    response = socket_QUERY.recv_json()

    if "error" not in response:
        publisher_info = response
        print(f"Main server responded: {response}")
    else:
         print(f"Service not found in main server")

except zmq.Again:

    print("Main server not responding, trying replica...")
    socket_QUERY.close()
    socket_QUERY = context.socket(zmq.REQ)
    socket_QUERY.setsockopt(zmq.RCVTIMEO, 3000)
    try:
        socket_QUERY.connect("tcp://localhost:5558")
        socket_QUERY.send_json(query)
        response = socket_QUERY.recv_json()
        
        if "error" not in response:
            publisher_info = response
            print(f"Replica server responded: {response}")
        else:
            print(f"Service not found in replica server")
    
    except zmq.Again:
        print("Replica server also not responding!")
        sys.exit(1)

if publisher_info is None:
    print("Could not locate service")
    sys.exit(1)

socket_QUERY.close()

print(f"\n--- Publisher found at {publisher_info['IP_dir']}:{publisher_info['PORT']} ---\n")

# Conectar directamente al publisher
socket_PUBLISHER = context.socket(zmq.REQ)
socket_PUBLISHER.connect(f"tcp://{publisher_info['IP_dir']}:{publisher_info['PORT']}")

# Solicitar datos del servicio
request = {"request": "get_data"}
socket_PUBLISHER.send_json(request)
service_data = socket_PUBLISHER.recv_json()

print(f"Service response:")
print(f"Service: {service_data['service']}")
print(f"Data: {service_data['data']}")

socket_PUBLISHER.close()