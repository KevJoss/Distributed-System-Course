import zmq, time, pickle, sys, random

# Is the administrator which manage the threads.
context = zmq.Context()
# sys.argv is a list which contains all text wroten in terminal
me = str(sys.argv[1])
# Lift the socket
s = context.socket(zmq.PUSH)

# Define the two sources in different ports
HOST = 'localhost'
PORT_BROKER = '17000'

p = "tcp://" + HOST + ":" + PORT_BROKER

# Bind the HOST and the PORT
s.connect(p)

for i in range(10):
    workload = random.randint(1, 100)
    s.send(pickle.dumps((me, workload)))

