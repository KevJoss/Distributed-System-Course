import zmq, time, pickle, sys

context = zmq.Context()
me = str(sys.argv[1])
r = context.socket(zmq.PULL)

HOST = 'localhost'
PORT_BROKER = '17001'

p = "tcp://" + HOST + ":" + PORT_BROKER

r.connect(p)

count = 1
while True:
    work = pickle.loads(r.recv())
    print(count)
    count += 1
    time.sleep(work[1] * 0.01)
