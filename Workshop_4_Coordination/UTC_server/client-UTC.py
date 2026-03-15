import zmq
import threading
import time

hostname = "localhost"
port = "5000"

def utc_time_client():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)  
    
    socket.connect("tcp://" + hostname + ":" + port) 

    socket.send_string("Time request")

    utc_time = socket.recv().decode('utf-8')
    
    print(f"Received UTC time: {utc_time}")

if __name__ == "__main__":
    c = [ ]
    for ii in range(3):
        # Note: target should be the function reference, not the call
        c.append(threading.Thread(target=utc_time_client, args=()))
        c[ii].start()
        time.sleep(2)
        c[ii].join()
        
    print('Done')
