import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import asyncio

# Use deque to store a fixed number of data points (for example, the last 100 points)
MAX_POINTS = 100

def start_plot(data_queue):
    # Create a figure and axis for the plot
    fig, ax = plt.subplots()

    # Create empty lists to store time and acceleration data
    timestamps = deque(maxlen=MAX_POINTS)
    ax_data = deque(maxlen=MAX_POINTS)
    ay_data = deque(maxlen=MAX_POINTS)
    az_data = deque(maxlen=MAX_POINTS)

    # Set up the plot
    ax.set_title("Acceleration vs Time")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Acceleration (m/s^2)")

    # Initialize the plot lines
    line_ax, = ax.plot([], [], label="ax", color="r")
    line_ay, = ax.plot([], [], label="ay", color="g")
    line_az, = ax.plot([], [], label="az", color="b")

    # Add a legend
    ax.legend()

    def update_plot(frame):
        # Get the data from the queue if available
        while not data_queue.empty():
            timestamp, ax_val, ay_val, az_val = data_queue.get_nowait()

            # Append the data to the lists
            timestamps.append(timestamp)
            ax_data.append(ax_val)
            ay_data.append(ay_val)
            az_data.append(az_val)

        # Update the plot data
        line_ax.set_data(timestamps, ax_data)
        line_ay.set_data(timestamps, ay_data)
        line_az.set_data(timestamps, az_data)

        # Adjust the x-axis limits based on the number of data points
        ax.set_xlim(timestamps[0] if timestamps else 0, timestamps[-1] if timestamps else 1)

        return line_ax, line_ay, line_az

    # Create an animation that updates the plot every 100 ms
    ani = animation.FuncAnimation(fig, update_plot, interval=100)

    # Show the plot
    plt.show()