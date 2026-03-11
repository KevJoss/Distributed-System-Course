# Importa la librería zmq (ZeroMQ) para manejar la comunicación asíncrona de red mediante paso de mensajes
import zmq
# Importa la librería time para manejar y formatear lo que el reloj interno de la computadora marca
import time

# Define el puerto por el que el servidor aceptará conexiones entrantes. Debe ser el mismo que usa el cliente
port = "5000"

# Define la función principal que contiene toda la lógica y el ciclo de vida de este servidor
def utc_time_server():
    # Crea inicialmente un contexto de ZeroMQ para englobar el objeto de comunicación en el proceso subyacente del sistema
    context = zmq.Context()
    
    # Crea un socket bajo el patrón "REP" (Reply/Respuesta). Es la contraparte necesaria para REQ. 
    # El orden estricto de funcionamiento de un REP es: Recibir la petición primero -> Enviar la respuesta después.
    socket = context.socket(zmq.REP)  	# REP stands for Reply
    
    # Vincula o "bindea" el socket al puerto usando el protocolo TCP. "tcp://*:[puerto]" indica que el servidor va
    # a escuchar en todas las interfaces de red local (*) las peticiones que ingresen por el puerto 5000.
    socket.bind("tcp://*:" + port)  	# Bind to port 5000

    # Imprime en consola un mensaje de confirmación de que el servidor está levantado y listo para operar
    print("UTC Time Server running...")

    # Se inicia un ciclo infinito (while True) que mantendrá al servidor funcionando permanentemente (escuchando)
    while True:
        # El programa del servidor se detiene y espera (bloqueado) en esta línea de forma indefinida hasta que 
        # algún cliente envíe un mensaje a través del puerto
        # Wait for next request from client
        message = socket.recv()
        
        # Una vez que llega un mensaje, lo lee en binario, lo decodifica a texto legible UTF-8 usando decode() y lo imprime
        print(f"Received request: {message.decode()}")

        # time.gmtime() devuelve el tiempo estándar en horas ajustado a universal UTC actualmente. 
        # time.strftime() coge ese objeto de tiempo en crudo y lo formatea a un string más estructurado y legible: (Año-Mes-Día Hora:Minuto:Segundo)
        # Get UTC time
        utc_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

        # Despacha la cadena de texto con la hora directamente de regreso a través del socket al mismo cliente que hizo la petición
        # Send UTC time back to client
        socket.send_string(utc_time)
        
        # Deja un log o registro impreso de forma local en el servidor, mostrando la hora exacta que acaba de despachar
        print(f"Sent UTC time: {utc_time}")

# Condición especial en Python: valida si este documento se corre directamente desde la línea de comandos
if __name__ == "__main__":
    # Inicia oficialmente y llama a la función servidora bloqueando todo lo demás por el ciclo infinito
    utc_time_server()
