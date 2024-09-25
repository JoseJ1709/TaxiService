import sys
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_HOST = "localhost"
server_PORT = 5050

try:
    server_socket.connect((server_HOST, server_PORT ))

    taxi_id = sys.argv[1]
    sizeN = sys.argv[2]
    sizeM = sys.argv[3]
    x_pos = sys.argv[4]
    y_pos = sys.argv[5]
    speed = sys.argv[6]
    serv = sys.argv[7]


    taxi_data = f"{taxi_id},{x_pos},{y_pos},{speed},{serv}"
    server_socket.send(taxi_data.encode())

except KeyboardInterrupt:
    print("\nCliente interrumpido. Cerrando la conexión...")
finally:
        print("Conexión cerrada.")