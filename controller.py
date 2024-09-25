import threading
import subprocess

def run_taxi(taxi_id,N,M,x,y,speed,serv):
    command = f'kitty --hold python3 taxi.py {taxi_id} {N} {M} {x} {y} {speed} {serv}'
    subprocess.run(command,shell=True)

with open('initial_config.txt', 'r') as file:
    for line in file:
        taxi_id,sizeN,sizeM,x_pos, y_pos, speed,serv = line.strip().split(',')

        taxi_thread = threading.Thread(target=run_taxi, args=(taxi_id,sizeN,sizeM,x_pos,y_pos,speed,serv))
        taxi_thread.start()

for thread in threading.enumerate():
    if thread is not threading.main_thread():
        thread.join()
