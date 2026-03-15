import zmq
import argparse
import time

def parse_arguments():
    parser = argparse.ArgumentParser(description="Servidor Central de Exclusión Mutua")
    parser.add_argument("-p", "--port", type=str, required=True, help="Puerto de escucha del servidor (ej. 5000)")
    return parser.parse_args()

def main():
    args = parse_arguments()
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    
    try:
        socket.bind(f"tcp://*:{args.port}")
    except Exception as e:
        print(f"[Error Crítico] No se pudo levantar el servidor en el puerto {args.port}: {e}")
        return

    # Estado del recurso
    resource_in_use = False
    current_user = None
    queue = [] # Lista para guardar los IDs de los clientes en espera

    print(f"=== Servidor Central de Recursos iniciado en el puerto {args.port} ===")

    while True:
        try:
            # Esperamos un mensaje en formato JSON
            message = socket.recv_json()
            action = message.get("action")
            client_id = message.get("client_id")

            if action == "REQUEST":
                if not resource_in_use:
                    # El recurso está libre, se lo damos
                    resource_in_use = True
                    current_user = client_id
                    socket.send_json({"status": "GRANT"})
                    print(f"[ASIGNADO] Recurso otorgado al Cliente {client_id}.")
                else:
                    # El recurso está ocupado, lo ponemos en cola
                    if client_id not in queue:
                        queue.append(client_id)
                    socket.send_json({"status": "QUEUED"})
                    print(f"[EN COLA] Cliente {client_id} añadido a la cola. Cola actual: {queue}")

            elif action == "CHECK":
                # El cliente pregunta si ya es su turno
                if current_user == client_id:
                    socket.send_json({"status": "GRANT"})
                elif client_id in queue and not resource_in_use and queue[0] == client_id:
                    # El recurso se liberó y es el primero de la cola
                    resource_in_use = True
                    current_user = client_id
                    queue.pop(0) # Lo sacamos de la cola
                    socket.send_json({"status": "GRANT"})
                    print(f"[ASIGNADO] Cliente {client_id} sale de la cola y toma el recurso. Cola: {queue}")
                else:
                    socket.send_json({"status": "WAIT"})

            elif action == "RELEASE":
                # El cliente libera el recurso
                if current_user == client_id:
                    resource_in_use = False
                    current_user = None
                    print(f"[LIBERADO] El Cliente {client_id} ha liberado el recurso compartido.")
                    socket.send_json({"status": "ACK"})
                else:
                    socket.send_json({"status": "ERROR", "msg": "No tenías el recurso asignado."})
            else:
                socket.send_json({"status": "ERROR", "msg": "Acción desconocida."})

        except KeyboardInterrupt:
            print("\nApagando servidor...")
            break
        except Exception as e:
            print(f"[Error en Servidor] {e}")
            socket.send_json({"status": "ERROR", "msg": str(e)})

if __name__ == "__main__":
    main()
