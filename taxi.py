import zmq
import sys
import time
import os
import threading

def display_grid(x_pos, y_pos, sizeN, sizeM):
    os.system('clear')
    for i in range(sizeN):
        row = ""
        for j in range(sizeM):
            if i == x_pos and j == y_pos:
                row += "[  T  ]"
            else:
                row += "[     ]"
        print(row)

def send_position(pub_socket, taxi_id, x_pos, y_pos):
    position_data = f"mov:{taxi_id},{x_pos},{y_pos}"
    pub_socket.send_string(position_data)
    print(f"Taxi {taxi_id} ha enviado su posición actual: ({x_pos}, {y_pos})")

def countdown_thread(countdown_flag, speed,pub_socket, taxi_id, sizeN, sizeM):
    global x_pos, y_pos
    while True:
        countdown_time = speed
        while countdown_time > 0 and countdown_flag.is_set():
            print(f"Cuenta regresiva para enviar actualización: {countdown_time} segundos", end="\r")
            time.sleep(1)
            countdown_time -= 1

        if countdown_flag.is_set():
            x_pos = (x_pos + 1) % sizeN
            y_pos = (y_pos + 1) % sizeM
            display_grid(x_pos, y_pos, sizeN, sizeM)
            send_position(pub_socket, taxi_id, x_pos, y_pos)

taxi_id = int(sys.argv[1])
sizeN = int(sys.argv[2])
sizeM = int(sys.argv[3])
x_pos = int(sys.argv[4])
y_pos = int(sys.argv[5])
speed = int(sys.argv[6])
serv = sys.argv[7]
x_posH = x_pos
y_posH = y_pos

context = zmq.Context()

# Publicador (PUB) para enviar la posición del taxi al servidor
pub_socket = context.socket(zmq.PUB)
pub_socket.connect("tcp://localhost:5550")
# Suscriptor (SUB) para recibir servicios asignados
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("tcp://localhost:5551")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, str(taxi_id))

print(f"Taxi {taxi_id} esperando por clientes...")
time.sleep(1)
try:
    taxi_data = f"ins:{taxi_id},{x_pos},{y_pos},{speed},{serv}"
    pub_socket.send_string(taxi_data)
    print(f"Taxi {taxi_id} registrado en el sistema.")
except Exception as e:
    print(f"Error al registrar el taxi: {e}")

display_grid(x_pos, y_pos, sizeN, sizeM)

countdown_flag = threading.Event()
countdown_flag.set()

countdown_thread_instance = threading.Thread(target=countdown_thread, args=(countdown_flag, speed, pub_socket, taxi_id, sizeN, sizeM))
countdown_thread_instance.daemon = True
countdown_thread_instance.start()

try:
    service = False
    service_end_time = 0

    while True:
        try:
            message = sub_socket.recv_string(flags=zmq.NOBLOCK)
            if f"Servicio asignado" in message:
                os.system('clear')
                print(f"Taxi {taxi_id} en servicio.")
                countdown_flag.clear()
                service = True
                service_end_time = time.time() + 30
        except zmq.Again:
            pass

        if service:
            if time.time() >= service_end_time:
                print(f"Taxi {taxi_id} ha completado el servicio.")
                service = False
                x_pos = x_posH
                y_pos = y_posH
                display_grid(x_pos, y_pos, sizeN, sizeM)
                send_position(pub_socket, taxi_id, x_pos, y_pos)
                countdown_flag.set()

except KeyboardInterrupt:
    print("\nTaxi interrumpido. Cerrando la conexión...")
finally:
    pub_socket.close()
    sub_socket.close()
    context.term()
    print("Conexión cerrada.")
