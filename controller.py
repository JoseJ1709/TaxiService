import sys
import threading
import subprocess
def run_taxi(taxi_id,N,M,x,y,speed,serv):
    command = f'kitty --hold python3 taxi.py {taxi_id} {N} {M} {x} {y} {speed} {serv}'
    subprocess.run(command,shell=True)

def create_clients(X,Y,wait_time):
    command = f'kitty --hold python3 client.py {X} {Y} {wait_time}'
    subprocess.run(command,shell=True)

if __name__ == '__main__':
    if len(sys.argv) >1 :
        N = sys.argv[1]
        M = sys.argv[2]
        wait_time = sys.argv[3]

        client_thread = threading.Thread(target=create_clients, args=(N,M,wait_time))
        client_thread.start()
    else:
        with open('initial_config.txt', 'r') as file:
            for line in file:
                taxi_id,sizeN,sizeM,x_pos, y_pos, speed,serv = line.strip().split(',')
                taxi_thread = threading.Thread(target=run_taxi, args=(taxi_id,sizeN,sizeM,x_pos,y_pos,speed,serv))
                taxi_thread.start()

        for thread in threading.enumerate():
            if thread is not threading.main_thread():
                thread.join()
