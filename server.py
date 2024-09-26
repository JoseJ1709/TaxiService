import socket
import threading
import json
import subprocess
import os
import zmq

taxi_registry = {
    "onservice":[],
    "service_history": {},
    "services_failed": {
        "num": 0
    }
}

N = 5
M = 5

def save_taxi(data):
    print("Guardando taxi")
    try:
        taxi_id, x_pos, y_pos, speed, serv = data.split(',')
        if taxi_id not in taxi_registry:
            taxi_registry[taxi_id] = {
                "taxi_id": int(taxi_id),
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

def check_taxi_service(taxi_id):
    try:
        with open('taxi_log.json', 'r') as log_file:
            taxi_registry = json.load(log_file)
        taxi_id_str = int(taxi_id)
        if taxi_id_str in taxi_registry.get("onservice", []):
            print(f"El taxi {taxi_id} ha vuelto al servicio")
            taxi_registry["onservice"].remove(taxi_id_str)
            with open('taxi_log.json', 'w') as log_file:
                json.dump(taxi_registry, log_file, indent=4)
            print(f"Taxi {taxi_id} removido de la lista de onservice.")
        else:
            pass
    except Exception as e:
        print(f"Error verificando servicio del taxi: {e}")
def move_taxi(data):
    try:
        taxi_id, x_pos, y_pos = data.split(',')
        taxi_id = int(taxi_id)
        check_taxi_service(taxi_id)
        x_pos = int(x_pos)
        y_pos = int(y_pos)

        with open('taxi_log.json', 'r') as log_file:
            taxi_registry = json.load(log_file)
            taxi_registry[str(taxi_id)]["x_pos"] = x_pos
            taxi_registry[str(taxi_id)]["y_pos"] = y_pos
            taxi_registry[str(taxi_id)]["position_history"].append((x_pos, y_pos))
        with open('taxi_log.json', 'w') as log_file:
            json.dump(taxi_registry, log_file, indent=4)

    except Exception as e:
        print(f"Error reciviendo/guardando movimiento del taxi: {e}")


def nearest_taxi(X, Y):
    print("Buscando taxi más cercano")
    try:
        with open('taxi_log.json', 'r') as log_file:
            taxi_registry = json.load(log_file)
            nearest_taxi = None
            min_distance = float('inf')
            for taxi_id, taxi_info in taxi_registry.items():
                if taxi_id != "service_history" and taxi_id != "services_failed" and taxi_id != "onservice":
                    x_pos = taxi_info.get("x_pos")
                    y_pos = taxi_info.get("y_pos")
                    if x_pos is not None and y_pos is not None:
                        distance = abs(x_pos - X) + abs(y_pos - Y)
                        if distance < min_distance:
                            min_distance = distance
                            nearest_taxi = taxi_id
            return nearest_taxi
    except Exception as e:
        print(f"Error buscando taxi más cercano: {e}")

def onservice(taxi_id):
    print("Poniendo taxi en servicio")
    try:
        with open('taxi_log.json', 'r') as log_file:
            taxi_registry = json.load(log_file)
            if "onservice" not in taxi_registry:
                taxi_registry["onservice"] = []
            if taxi_id not in taxi_registry["onservice"]:
                taxi_registry["onservice"].append(int(taxi_id))
            with open('taxi_log.json', 'w') as log_file:
                json.dump(taxi_registry, log_file, indent=4)
    except Exception as e:
        print(f"Error poniendo taxi en servicio: {e}")
def assing_service(data):
    print("Asignando servicio")
    try:
        X,Y = data.split(',')
        X = int(X)
        Y = int(Y)
        near = nearest_taxi(X,Y)
        print(f"Taxi más cercano: {near}")
        onservice(near)
        service_info = f"Servicio asignado: {X},{Y}"
        print(f"Enviando servicio al taxi {near}")
        pub_socket.send_string(f"{near}:{service_info}")


    except Exception as e:
        print(f"Error asignando servicio: {e}")
def open_display_terminal():
    command = f'kitty --hold python3 display_positions.py {N} {M}'
    subprocess.Popen(command, shell=True)

def handle_positions():
    while True:
        message = sub_socket.recv_string()
        prefix, data = message.split(':')
        if prefix == "ins":
            save_taxi(data)
        elif prefix == "mov":
            print(f"Actualización de posición recibida: {message}")
            move_taxi(data)

context = zmq.Context()

# Patrón PUB/SUB para recibir actualizaciones de taxis
sub_socket = context.socket(zmq.SUB)
sub_socket.bind("tcp://*:5550")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")  # Escuchar todos los mensajes

# Patrón PUB para asignar servicios
pub_socket = context.socket(zmq.PUB)
pub_socket.bind("tcp://*:5551")

# Patrón REQ/REP para recibir solicitudes de usuarios
rep_socket = context.socket(zmq.REP)
rep_socket.bind("tcp://*:5552")

# Hilo para manejar las posiciones de los taxis
thread = threading.Thread(target=handle_positions)
thread.start()

display_thread = threading.Thread(target=open_display_terminal)
display_thread.start()


try:
    while True:
        message = rep_socket.recv_string()
        print(f"Solicitud recibida: {message}")
        prefix,data = message.split(':')
        if prefix == "serv":
            assing_service(data)
            rep_socket.send_string("Servicio asignado")
        else:
            rep_socket.send_string("Solicitud no válida")

except KeyboardInterrupt:
    print("Cerrando servidor...")

finally:
    sub_socket.close()
    pub_socket.close()
    rep_socket.close()
    context.term()