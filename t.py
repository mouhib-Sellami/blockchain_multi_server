import time
import threading

c = 0

def count_loop():
    global c

    while True:
        c += 1
        time.sleep(1)

th = threading.Thread(target=count_loop)
th.start()

time.sleep(1)
print('Count:', c)
