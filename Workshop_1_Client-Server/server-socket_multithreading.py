from socket import *
import time
import threading


def handle_client(conn, addr):
    print(f"[NEW THREAD] In response to {addr}")
    try:
        sentence_bytes = conn.recv(1024)
        print(sentence_bytes)
        if not sentence_bytes:
            print(f"Client {addr} closed the connection cleanly.")
            return
        sentence = sentence_bytes.decode()
        print("I received:", sentence)
        
        capitalizedSentence = sentence.upper()
        time.sleep(2)
        
        conn.send(capitalizedSentence.encode())
    except ConnectionResetError:
        print(f"Error: The client {addr} abruptly closed the connection.")

    except Exception as e:
        print(f"Unexpected error with {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection to {addr} terminated.")
    return

def main():
    host = ""
    port = 12000
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((host, port))
    serverSocket.listen(5)
    print("Server running on port", port)

    while True:
        connectionSocket, addr = serverSocket.accept()
        print('Connected to:', addr[0], ':', addr[1])
        thread = threading.Thread(target=handle_client, args=(connectionSocket, addr))
        thread.start()

if __name__ == '__main__':
    main()