import zmq
import time

port = "5000"

def utc_time_server():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:" + port)

    print("UTC Time Server running...")

    while True:
        message = socket.recv()
        print(f"Received request: {message.decode()}")

        utc_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        socket.send_string(utc_time)
        print(f"Sent UTC time: {utc_time}")

if __name__ == "__main__":
    utc_time_server()
