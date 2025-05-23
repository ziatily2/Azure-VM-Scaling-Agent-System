import psutil
import time

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

if __name__ == "__main__":
    for _ in range(5):
        cpu_usage = get_cpu_usage()
        print(f"Utilisation CPU: {cpu_usage}%")
        time.sleep(1)
    print("monitor_cpu.py terminé après 5 cycles")