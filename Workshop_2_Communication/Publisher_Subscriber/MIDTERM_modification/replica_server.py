import zmq
import threading

publishers_registry = {}

# Función para el thread 1 que recibe la información desde el MAIN mediante el uso de PULL.
def receive_updates():
    context = zmq.Context()
    socket_PULL = context.socket(zmq.PULL)
    socket_PULL.bind("tcp://*:5556")

    print("Thread: Listening for updates from main on port 5556...")

    while True:
        message = socket_PULL.recv_json()
        if 'service_name' not in message:
            socket_REP.send_json({"error": "Missing service_name field"})
            continue

        service_name = message['service_name']

        print(f"Registering service on replica server '{service_name}'...")

        publishers_registry[service_name] = {
            'IP_dir': message['IP_dir'],
            'PORT': message['PORT']
        }

        print(f"Registry updated: {publishers_registry}")

# Función para el thread 2 que actua cómo el servidor main en caso de caída (Solo para envíar información de servicios, más no para registrarlos)
def answer_queries():
    context = zmq.Context()
    socket_REP = context.socket(zmq.REP)
    socket_REP.bind("tcp://*:5558")

    print("Thread: Listening for queries from consumers on port 5558...")

    while True:
        message = socket_REP.recv_json()
        if 'service_name' not in message:
            socket_REP.send_json({"error": "Missing service_name field"})
            continue

        service_name = message['service_name']

        if service_name in publishers_registry:
            socket_REP.send_json(publishers_registry[service_name])
        else:
            socket_REP.send_json({"error": "Service not found"})
    
if __name__ == '__main__':
    thread_updates = threading.Thread(target=receive_updates)
    thread_queries = threading.Thread(target=answer_queries)
    
    thread_updates.daemon = True
    thread_queries.daemon = True

    thread_updates.start()
    thread_queries.start()

    print("Replica Server running...")

    try:
        shutdown_event = threading.Event()
        while True:
            shutdown_event.wait()
    except KeyboardInterrupt:
        print("\nShutting down replica server...")
    

