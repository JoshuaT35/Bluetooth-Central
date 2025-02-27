import threading
import time
import matplotlib.pyplot as plt
from random import randint

# Simulate Bluetooth data reception
def receive_data():
    while True:
        # Simulate receiving data (replace with actual Bluetooth code)
        data = randint(1, 100)
        data_queue.append(data)
        time.sleep(1)

# Update plot with received data
def update_plot():
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()
    x_vals = []
    y_vals = []

    while True:
        if data_queue:
            data = data_queue.pop(0)
            x_vals.append(len(x_vals))
            y_vals.append(data)
            ax.clear()
            ax.plot(x_vals, y_vals)
            plt.draw()
            plt.pause(0.1)

# Initialize shared data queue
data_queue = []

# Create and start the receiving thread
data_thread = threading.Thread(target=receive_data)
data_thread.start()

# Create and start the plotting thread
plot_thread = threading.Thread(target=update_plot)
plot_thread.start()

# Keep the main thread running to handle plotting and receiving
while True:
    time.sleep(1)
