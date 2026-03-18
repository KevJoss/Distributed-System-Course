import sys
import zmq

if len(sys.argv) < 3:
    print("Use python publishers.py <service_name> <port>")
    sys.exit(1)

service_name = sys.argv[1]
port = int(sys.argv[2])

context = zmq.Context()

socket_REQ = context.socket(zmq.REQ)
socket_REQ.connect("tcp://localhost:5555")

register = {
    "type": "register",
    "service_name": service_name,
    "IP_dir": "127.0.0.1",
    "PORT": port
}

print(f"Registering service '{service_name}' on port {port}...")
socket_REQ.send_json(register)
response = socket_REQ.recv_json()
print(f"Server response: {response}")

socket_REP = context.socket(zmq.REP)
socket_REP.bind(f"tcp://*:{port}")
print(f"Publisher '{service_name}' listening on port {port}...")

SERVICE_DATA = {
    "weather": {"temperature": "25°C", "condition": "sunny", "humidity": "60%"},
    "news": {"headline": "Python is the most popular language", "date": "2024-03-18"},
    "temperature": {"value": "22°C", "location": "Quito"},
    "stock": {"company": "AAPL", "price": "$150.25", "change": "+2.5%"}
}

while True:
    request = socket_REP.recv_json()
    
    if service_name in SERVICE_DATA:
        data = SERVICE_DATA[service_name]
    else:
        data = f"Generic data for {service_name}"
    
    response = {
        "service": service_name,
        "data": data 
    }
    
    socket_REP.send_json(response)
    print(f"✓ Served request: {request}")