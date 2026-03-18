import zmq

context = zmq.Context()

socket_REP = context.socket(zmq.REP)
REPPLY_PORT = 5555
# Este bind signfica abre este puerto y acepta conexiones
socket_REP.bind(f'tcp://*:{REPPLY_PORT}')

PUSH_PORT = 5556
socket_PUSH = context.socket(zmq.PUSH)
# Este connect significa conectate hacia este puerto en la dirección IP del servidor nombrado
socket_PUSH.connect(f'tcp://localhost:{PUSH_PORT}')

publishers_registry = {}

print("Main server listen on PORT: ", REPPLY_PORT)

while True:
    message = socket_REP.recv_json()
    if 'service_name' not in message:
        socket_REP.send_json({"error": "Missing service_name field"})
        continue

    if message['type'] == 'register':
        service_name = message['service_name']

        print(f"Registering service '{service_name}'...")

        publishers_registry[service_name] = {
            'IP_dir': message['IP_dir'],
            'PORT': message['PORT']
        }

        socket_PUSH.send_json(message)
        socket_REP.send_json({"status": "success", "message": "Registered successfully"})


    elif message['type'] == 'query':
        service_name = message['service_name']

        if service_name in publishers_registry:
            socket_REP.send_json(publishers_registry[service_name])
        else:
            socket_REP.send_json({"error": "Service not found"})

    else:
        socket_REP.send_json({'error': 'Unrecognized message type'})
