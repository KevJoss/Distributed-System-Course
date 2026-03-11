# Importa la librería zmq (ZeroMQ), que proporciona una forma eficiente de comunicación por red mediante paso de mensajes
import zmq
# Importa la librería threading, que permite la ejecución de múltiples hilos de manera paralela/concurrente
import threading
# Importa la librería time, utilizada para acceder y manipular el tiempo, o provocar pausas (delays) en la ejecución
import time

# Especifica la dirección del servidor a conectarse. "localhost" hace referencia a tu propia computadora
hostname = "localhost"
# Especifica el puerto de comunicación, una puerta virtual en tu computadora para esta aplicación en específico
port = "5000"

# Define la función principal que ejecutará el cliente para interactuar con el servidor de tiempo
def utc_time_client():
    """
    ¿QUÉ ES EL CONTEXTO EN ZEROMQ Y POR QUÉ EL SOCKET DEPENDE DE ÉL?
    
    1. El "Contexto" (zmq.Context):
       Imagina el contexto como el motor central o el "sistema operativo" de ZeroMQ 
       dentro de tu aplicación. ZeroMQ no usa sockets "crudos" o básicos, sino que 
       crea una infraestructura propia muy robusta: un grupo de hilos invisibles en 
       segundo plano que gestionan envíos, colas de mensajes, intentos de reconexión 
       automáticos, etc. El "Contexto" es el contenedor y administrador global de 
       todos esos recursos. Un programa generalmente necesita un solo Contexto.
       
    2. ¿Por qué el socket depende del contexto?
       Como el contexto maneja todo el trabajo pesado detrás de escena (la red real), 
       un socket de ZeroMQ no puede existir por sí solo, no sabría cómo despachar nada. 
       El socket es solo tu "interfaz" programática para hablar con el contexto. 
       Por eso siempre le pedimos al contexto que nos fabrique el socket: `context.socket(...)`.
       
    3. Patrón o comportamiento REQUEST (zmq.REQ):
       ZeroMQ es inteligente y usa patrones (patrones de diseño de mensajería). Al pedirle
       al contexto un socket `zmq.REQ` (Request o Petición), no te da un tubo vacío, te da 
       un socket con reglas muy estrictas de tipo "Cliente-Servidor sincrónico". 
       Un socket REQ te OBLIGA a operar en este ciclo exacto: 
       --> Enviar Petición --> Esperar Respuesta (bloqueado) --> Recibir Respuesta --> etc.
       Si intentas enviar dos peticiones seguidas sin recibir, el socket dará error. 
       Garantiza el orden en la coordinación de mensajes.
    """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)  # REQ significa Request
    
    # Inicia la conexión con el servidor a través de TCP, indicando el hostname y puerto determinados previamente
    socket.connect("tcp://" + hostname + ":" + port)  # Connect to the server's port

    # Envía un mensaje inicial (una petición) en forma de texto plano al servidor para iniciar el intercambio
    # Send a request for UTC time
    socket.send_string("Time request")

    # Queda en estado de espera (bloqueado) hasta recibir la respuesta; luego decodifica la respuesta binaria a texto UTF-8
    # Receive the UTC time from the server
    utc_time = socket.recv().decode('utf-8')
    
    # Imprime en la consola o terminal el valor de la hora que devolvió el servidor
    print(f"Received UTC time: {utc_time}")

# Condición especial en Python: el bloque a continuación se ejecuta solo si ejecutas directamente este script
if __name__ == "__main__":
    """
    ¿POR QUÉ USAR HILOS (THREADS) Y QUÉ HACEN AQUÍ?
    
    1. El Propósito de los Hilos (Threads):
       Por defecto, un programa corre "línea por línea" en un solo camino (un hilo principal).
       Los hilos permiten crear "ramas" secundarias que pueden trabajar al mismo tiempo (concurrencia).
       En este código, se usan hilos para simular que 3 clientes completamente independientes 
       están solicitando la hora al servidor simultáneamente o de forma paralela, usando el 
       mismo script en vez de tener que abrir 3 terminales distintas.
       
    2. Creación y la lista 'c':
       Se crea una lista vacía `c = []` simplemente para guardar los "controles remotos" de 
       cada hilo hijo. El ciclo `for` se repetirá 3 veces y en cada iteración prepara un hilo 
       con el comando `threading.Thread(...)`, diciéndole que su misión (target) será ejecutar 
       la función `utc_time_client`.
       
       (Nota de bug original en tu código: `target=utc_time_client()` tiene paréntesis. Eso hace 
       que Python evalúe/ejecute la función ahí mismo en el hilo principal bloqueándolo, anulando 
       la idea de crear un "hijo". Lo correcto sería pasar la referencia sin paréntesis: `target=utc_time_client`).
       
    3. El método `.start()`:
       Crear un hilo (como se vio en el paso anterior) es como preparar a un atleta en la línea de salida. 
       Todavía no está corriendo. El método `c[ii].start()` es el pitazo inicial. Le indica al 
       sistema operativo: "Ahora sí, dele vida a este hilo para que trabaje en segundo plano
       haciendo la función que le asigné antes".
       
    4. El método `.join()` y la estructura del bucle:
       Los hilos hijos corren separados del hilo "Padre/Principal". El problema es que si el hilo principal 
       llega rápidamente a la última línea y termina el programa, asesinará forzosamente a todos los 
       hilos hijos, hayan terminado o no su petición.
       El método `.join()` frena en seco al hilo principal y le dice: "Congélate aquí, no continúes 
       hasta que mi amigo (el hilo `c[ii]`) haya terminado de recibir su petición al 100% y finalice".
       
       *OJO con la lógica de este bucle*: Como el código hace Start -> Sleep de 2 segs -> Join (todo 
       adentro del mismo bucle for iteración por iteración), en la práctica el código bloquea al 
       siguiente hilo hasta que el anterior haya terminado. Crea Hilo 1, espera que acabe, y recién 
       luego Crea Hilo 2. Es decir, los está ejecutando en estricto orden secuencial, anulando 
       el propósito de los hilos de ir "al mismo tiempo".
    """
    c = [ ]
    for ii in range(3):
        c.append(threading.Thread(target=utc_time_client(), args=()))
        c[ii].start()
        time.sleep(2)
        c[ii].join()
        
    print('Done')
