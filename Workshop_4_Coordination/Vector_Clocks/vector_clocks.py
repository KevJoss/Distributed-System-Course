import zmq
import threading
import time
import json
import random
import sys
import argparse

class VectorClockNode:
    # La clase VectorClockNode se mantiene exactamente igual que antes.
    # No es necesario cambiar la lógica de los relojes lógicos, solo cómo recibe los parámetros.
    def __init__(self, process_id, total_processes, my_port, peer_ports):
        self.process_id = process_id
        self.total_processes = total_processes
        self.vector = [0] * total_processes
        self.my_port = my_port
        self.peer_ports = peer_ports
        self.lock = threading.Lock()
        self.running = True

    def increment_own_clock(self):
        with self.lock:
            self.vector[self.process_id] += 1
            return list(self.vector)

    def update_clock_on_receive(self, received_vector):
        with self.lock:
            self.vector[self.process_id] += 1
            for k in range(self.total_processes):
                self.vector[k] = max(self.vector[k], received_vector[k])
            return list(self.vector)

    def receiver_thread(self):
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        try:
            socket.bind(f"tcp://*:{self.my_port}")
            socket.setsockopt(zmq.RCVTIMEO, 1000) 
            
            while self.running:
                try:
                    message = socket.recv_string()
                    data = json.loads(message)
                    sender_id = data['sender_id']
                    received_vector = data['vector']
                    
                    self.update_clock_on_receive(received_vector)
                    print(f"\n[RECEPCIÓN] Mensaje de Proceso {sender_id}. Vector recibido: {received_vector}")
                    print(f" -> Mi nuevo vector actual: {self.vector}")
                except zmq.error.Again:
                    continue 
                except json.JSONDecodeError:
                    print("\n[Error] Formato de mensaje corrupto recibido.")
        except Exception as e:
            print(f"\n[Error Crítico en Receptor] {e}")

    def sender_logic(self, num_messages):
        context = zmq.Context()
        
        for _ in range(num_messages):
            time.sleep(random.uniform(2.0, 5.0)) 
            
            if not self.peer_ports:
                print("No hay peers configurados para enviar.")
                break

            target_port = random.choice(self.peer_ports)
            current_vector = self.increment_own_clock()
            
            data = {
                "sender_id": self.process_id,
                "vector": current_vector
            }
            
            try:
                socket = context.socket(zmq.PUSH)
                socket.connect(f"tcp://localhost:{target_port}")
                socket.send_string(json.dumps(data))
                socket.close()
                print(f"\n[ENVÍO] Enviando a puerto {target_port}. Mi vector actual: {current_vector}")
            except Exception as e:
                print(f"\n[Error de Conexión] No se pudo enviar al puerto {target_port}: {e}")

def parse_arguments():
    """Configura y valida los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description="Simulador de Relojes Vectoriales en Sistemas Distribuidos.")
    
    # Definimos los inputs que el programa espera recibir
    parser.add_argument("-t", "--total_processes", type=int, required=True, help="Total de procesos en la red.")
    parser.add_argument("-i", "--process_id", type=int, required=True, help="ID de este proceso (empezando desde 0).")
    parser.add_argument("-p", "--port", type=str, required=True, help="Puerto de escucha para este proceso.")
    parser.add_argument("-r", "--peers", type=str, required=True, help="Puertos de los peers separados por coma (ej. 6001,6002).")
    parser.add_argument("-m", "--messages", type=int, required=True, help="Número de mensajes a enviar.")

    return parser.parse_args()

def main():
    # Obtenemos los argumentos ya validados
    args = parse_arguments()

    # Validación adicional de lógica
    if args.process_id < 0 or args.process_id >= args.total_processes:
        print(f"\n[Error] El ID del proceso debe estar entre 0 y {args.total_processes - 1}.")
        sys.exit(1)

    # Convertimos el string de peers "6001,6002" en una lista de strings ["6001", "6002"]
    peer_ports = [p.strip() for p in args.peers.split(",") if p.strip()]

    print(f"=== Nodo de Reloj Vectorial {args.process_id} Iniciado ===")
    
    node = VectorClockNode(args.process_id, args.total_processes, args.port, peer_ports)

    receiver = threading.Thread(target=node.receiver_thread, daemon=True)
    receiver.start()

    node.sender_logic(args.messages)

    print("\n[Info] Envíos finalizados. Esperando 5 segundos por si hay mensajes en camino...")
    time.sleep(5)
    node.running = False
    print(f"=== Simulación finalizada. Vector Final del Proceso {args.process_id}: {node.vector} ===")

if __name__ == "__main__":
    main()
