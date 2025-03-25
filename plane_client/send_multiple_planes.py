# Launches NUM_PLANES threads
# Each thread sends a randomized landing request using your existing send_landing_request() function
# Adds a small time.sleep(0.1) delay to simulate slightly staggered arrivals

import threading
import time
from send_landing_request import send_landing_request

# Number of planes to send
NUM_PLANES = 10  # you can increase this number

# Send one plane in a thread
def send_plane():
    send_landing_request()

def main():
    threads = []

    for _ in range(NUM_PLANES):
        thread = threading.Thread(target=send_plane)
        thread.start()
        threads.append(thread)
        time.sleep(0.1)  # slight delay to avoid message congestion

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
