import json
import os
import sys
import time

N = int(sys.argv[1])
M = int(sys.argv[2])

while True:
    os.system('clear')

    try:
        grid = [["[     ]" for _ in range(M)] for _ in range(N)]

        with open('taxi_log.json', 'r') as log_file:
            taxi_registry = json.load(log_file)

        for taxi_id, taxi_info in taxi_registry.items():
            if taxi_id not in ["service_history", "services_failed", "onservice"]:
                x_pos = taxi_info["x_pos"]
                y_pos = taxi_info["y_pos"]
                if 0 <= x_pos < N and 0 <= y_pos < M:
                    if int(taxi_id) in taxi_registry.get("onservice", []):
                        grid[x_pos][y_pos] = "[     ]"
                    else:
                        grid[x_pos][y_pos] = f"[T{taxi_id}]"

    except Exception as e:
        print(f"Error reading taxi positions from JSON: {e}")

    for row in grid:
        print("".join(row))

    print("\n--- Updating every second ---")
    time.sleep(1)