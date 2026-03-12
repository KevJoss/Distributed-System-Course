import zmq
import argparse
import time
import random
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description="Cliente para Exclusión Mutua Centralizada")
    parser.add_argument("-i", "--client_id", type=str, required=True, help="ID único de este cliente (ej. C1)")
    parser.add_argument("-s", "--server_ip", type=str, default="localhost", help="IP del servidor (por defecto localhost)")
    parser.add_argument("-p", "--server_port", type=str, required=True, help="Puerto del servidor")
    parser.add_argument("-n", "--requests", type=int, required=True, help="Número de veces que solicitará el recurso")
    return parser.parse_args()

def send_message(socket, action, client_id):
    """Función auxiliar para enviar mensajes y manejar la respuesta."""
    try:
        socket.send_json({"action": action, "client_id": client_id})
        return socket.recv_json()
    except Exception as e:
        print(f"[Error de Conexión] No se pudo comunicar con el servidor: {e}")
        return {"status": "ERROR"}

def main():
    args = parse_arguments()
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    
    # Manejo de errores de conexión (timeout de 3 segundos)
    socket.setsockopt(zmq.RCVTIMEO, 3000)
    socket.connect(f"tcp://{args.server_ip}:{args.server_port}")

    print(f"=== Cliente {args.client_id} Iniciado ===")

    for i in range(1, args.requests + 1):
        print(f"\n--- Intento {i}/{args.requests} de acceder al recurso ---")
        time.sleep(random.uniform(1.0, 3.0)) # Espera antes de querer el recurso
        
        reply = send_message(socket, "REQUEST", args.client_id)
        status = reply.get("status")

        # Bucle de espera (Polling) si estamos en cola
        while status in ["QUEUED", "WAIT"]:
            print("[ESPERANDO] El recurso está ocupado. Esperando en cola...")
            time.sleep(2) # Esperamos 2 segundos antes de volver a preguntar
            reply = send_message(socket, "CHECK", args.client_id)
            status = reply.get("status")
            
            if status == "ERROR":
                print("[Error] Problema al chequear estado. Abortando.")
                sys.exit(1)

        if status == "GRANT":
            print(f">>> [ACCESO CONCEDIDO] El Cliente {args.client_id} está usando el recurso compartido...")
            # Simulamos que usar el recurso toma tiempo (Sección Crítica)
            time.sleep(random.uniform(2.0, 5.0))
            print(f"<<< [TERMINADO] El Cliente {args.client_id} finalizó su tarea.")
            
            # Liberamos el recurso
            send_message(socket, "RELEASE", args.client_id)
        else:
            print(f"[Error Inesperado] Estado recibido: {status}")

    print(f"\n=== Cliente {args.client_id} ha finalizado todas sus tareas ===")

if __name__ == "__main__":
    main()
