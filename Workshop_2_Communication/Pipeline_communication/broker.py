import zmq

context = zmq.Context()

frontend = context.socket(zmq.PULL)
frontend.bind("tcp://localhost:17000")


backend = context.socket(zmq.PUSH)
backend.bind("tcp://localhost:17001")

zmq.proxy(frontend,backend)