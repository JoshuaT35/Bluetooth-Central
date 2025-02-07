import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import asyncio

# Data storage (Fixed-length deque)
BUFFER_SIZE = 100
time_series = deque(maxlen=BUFFER_SIZE)
ax_series = deque(maxlen=BUFFER_SIZE)
ay_series = deque(maxlen=BUFFER_SIZE)
az_series = deque(maxlen=BUFFER_SIZE)

async def update_data(data_queue):
    """Fetches data from queue and updates the series"""
    while True:
        while not data_queue.empty():
            timestamp, ax, ay, az = await data_queue.get()
            time_series.append(timestamp)
            ax_series.append(ax)
            ay_series.append(ay)
            az_series.append(az)
        await asyncio.sleep(0.05)

def update_plot(frame):
    """Matplotlib animation update function"""
    if not time_series:  # Handle empty deque case
        return ax_line, ay_line, az_line  # Return unchanged artists
    
    ax_line.set_data(time_series, ax_series)
    ay_line.set_data(time_series, ay_series)
    az_line.set_data(time_series, az_series)

    ax.set_xlim(max(0, time_series[0]), time_series[-1] if time_series else 10)
    return ax_line, ay_line, az_line

def start_plot(data_queue):
    """Launches the Matplotlib real-time plot"""
    global ax, ax_line, ay_line, az_line

    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    fig, ax = plt.subplots()
    ax.set_title("Real-time IMU Data")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Acceleration")
    ax.set_xlim(0, 10)
    ax.set_ylim(-2000, 2000)

    ax_line, = ax.plot([], [], label="Accel X", color="r")
    ay_line, = ax.plot([], [], label="Accel Y", color="g")
    az_line, = ax.plot([], [], label="Accel Z", color="b")

    ax.legend()

    loop = asyncio.get_event_loop()
    loop.create_task(update_data(data_queue))  # Run update loop in background

    ani = animation.FuncAnimation(fig, update_plot, interval=50, cache_frame_data=False)

    plt.show()
