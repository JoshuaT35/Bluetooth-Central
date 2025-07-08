import matplotlib.pyplot as plt
import collections
from kinematics_calc import get_current_position, get_current_vel

# maximum number of data that should be plotted at a time
MAX_NUM_DATA_PLOT = 100

## --- 2d plotting ---
async def plot_2d_data(ax, data_queue):
    # data lists to store timestamps and x, y, z values
    # NOTE: use a queue or deque instead to avoid memory overflow?
    xdata, ydata, zdata = [], [], []
    timestamp = []
    first_time_unit = 0

    # to check if this is the first reading we get
    initial_reading = True

    # continuously retrieve data and plot it
    while True:
        # get data
        data = await data_queue.get()
        x, y, z, t = data

        # mark the initial reading
        if initial_reading:
            initial_reading = False
            first_time_unit = t
        
        # Append the data to respective lists for plotting
        # first time unit may not be 0.
        # to set scale to begin at 0, we do current time (t) - previous time unit (first_time_unit)
        timestamp.append(t-first_time_unit)
        xdata.append(x)
        ydata.append(y)
        zdata.append(z)
        
        # Clear the plot to redraw it with the updated data
        ax.clear()
        
        # Plot x, y, z values with respect to time (timestamp)
        ax.plot(timestamp, xdata, label="X", color="r")
        ax.plot(timestamp, ydata, label="Y", color="g")
        ax.plot(timestamp, zdata, label="Z", color="b")
        
        ax.set_xlabel('Time (ms)')  # Label for x-axis
        ax.set_ylabel('Values')  # Label for y-axis
        ax.set_title('Real-Time Plot of x, y, z')  # Title of the plot
        
        ax.legend()  # Show legend
        
        plt.draw()  # Redraw the plot
        plt.pause(0.05)  # Non-blocking pause to update the plot


# --- 3d plotting ---
async def plot_3d_data(axes, data_queue):
    # variables
    prev_time = 0
    prev_vel = [0, 0, 0]
    prev_pos = [0, 0, 0]
    current_vel = [0, 0, 0] # initial velocity for x, y, z is 0 (assumption: sensor not currently moving at the beginning)
    current_pos = [0, 0, 0] # initial position for x, y, z is 0 (assumption: position of origin)

    # data lists to store timestamps and x, y, z values
    xdata = collections.deque(maxlen=MAX_NUM_DATA_PLOT)
    ydata = collections.deque(maxlen=MAX_NUM_DATA_PLOT)
    zdata = collections.deque(maxlen=MAX_NUM_DATA_PLOT)

    # check if this is the first reading we get
    initial_reading = True

    while True:
        # get data
        data = await data_queue.get()
        ax, ay, az, timestamp = data

        # if initial reading, do no calculations (we have nothing over time to compare with)
        if initial_reading:
            initial_reading = False

        # secondary and more data points obtained
        else:
            # get difference in time
            delta_time = timestamp - prev_time

            # get the current position based on acceleration, previous velocity, previous position, and time between
            current_pos = get_current_position([ax, ay, az], prev_vel, prev_pos, delta_time)

            # NOTE: current_vel is actually only used to update prev_vel.
            # so theoretically we can just assign this value to prev_vel directly
            current_vel = get_current_vel([ax, ay, az], prev_vel, delta_time)

        # append new position data to current position data
        xdata.append(current_pos[0])
        ydata.append(current_pos[1])
        zdata.append(current_pos[2])
        
        # update prev variables to track new data
        prev_time = timestamp
        prev_vel = current_vel
        prev_pos = current_pos

        # NOTE: since plt.show() is in main, the plotting code below MUST occur no matter what
        axes.clear()  # Clear previous data
        axes.plot3D(list(xdata), list(ydata), list(zdata), 'gray')  # Plot the new data
        plt.draw()  # Redraw the plot
        plt.pause(0.05)  # Non-blocking pause to update the plot
