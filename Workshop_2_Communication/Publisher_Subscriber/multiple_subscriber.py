import zmq
import random

context = zmq.Context()
s = context.socket(zmq.SUB) # <--- Tipo de socket: SUB (Subscriber)

HOST = 'localhost'
PORT = '15000'


p = "tcp://" + HOST + ":" + PORT
s.connect(p) # <--- connect() lo hace el cliente/subscriber

# 1. Suscribirse a un tópico
services = ['SYSADMIN CPU','SYSADMIN RAM','STOCK']
request_services = random.sample(services,k=2)
print("Request for: ", request_services)
s.setsockopt_string(zmq.SUBSCRIBE, request_services[0])
s.setsockopt_string(zmq.SUBSCRIBE, request_services[1])

first_response_service = s.recv().decode("utf-8")
second_response_service = s.recv().decode("utf-8")
print(first_response_service)
print(second_response_service)