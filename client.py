import sys
import socket
import time
import zmq

X = sys.argv[1]
Y = sys.argv[2]
wait_time = sys.argv[3]

time.sleep(int(wait_time))

try:
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:5552")
    service_request = f"serv:{X},{Y}"
    socket.send_string(service_request)
    socket.close()
except Exception as e:
    print(f"Error al conectarse con el servidor: {e}")