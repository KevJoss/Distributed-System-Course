from socket import *
import random
import string

# Assign the IP addres and the port of the server to connect
serverName = "127.0.0.1"
serverPort = 12000

# A flag to always execute a iteration in the while loop
next = True
number_messages = random.randint(1,20)
length_strings = 10

randomly_strings = [''.join(random.choices(string.ascii_letters, k=length_strings)).lower() for i in range(number_messages)]

print(randomly_strings)

try:
    for text in randomly_strings:
        # Create a new socket for each connection
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        
        print(f"Sending: {text}")
        clientSocket.send(text.encode())
        
        modifiedSentence = clientSocket.recv(1024)
    
        if not modifiedSentence:
            print("The server closed the connection without responding.")
        else:
            print("From Server:", modifiedSentence.decode())
            
        clientSocket.close()

except ConnectionRefusedError:
    print("ERROR: Could not connect. Is the server turned on?")
    next = False
except ConnectionResetError:
    print("ERROR: The server terminated the connection while we were waiting.")
except KeyboardInterrupt:
    print("\nLeaving at the user's request...")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    print("Done processing messages.")