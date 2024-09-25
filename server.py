import socket
import threading
import json

taxi_registry = {
    "service_history": {},
    "services_failed": {
        "num": 0
    }
}

def save_taxi(client_socket):
    try:
        data = client_socket.recv(1024).decode()
        taxi_id, x_pos, y_pos, speed, serv = data.split(',')

        if taxi_id not in taxi_registry:
            taxi_registry[taxi_id] = {
                "taxi_id": taxi_id,
                "x_pos": int(x_pos),
                "y_pos": int(y_pos),
                "speed": int(speed),
                "services_aviable": serv,
                "position_history": []
            }
        taxi_registry[taxi_id]["position_history"].append((int(x_pos), int(y_pos)))

        with open('taxi_log.json', 'w') as log_file:
            json.dump(taxi_registry, log_file, indent=4)

    except Exception as e:
        print(f"Error receiving/saving data from taxi: {e}")
    finally:
        client_socket.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_HOST = "localhost"
server_PORT = 5050
server_socket.bind((server_HOST, server_PORT))
server_socket.listen(5)

try:
    while True:
        client_socket, addr = server_socket.accept()
        print("Guardando taxi", client_socket)
        client_thread = threading.Thread(target=save_taxi, args=(client_socket,))
        client_thread.start()
except KeyboardInterrupt:
    print("Cerrrando Servidor")
finally:
    server_socket.close()
    print("Conexión cerrada.")
