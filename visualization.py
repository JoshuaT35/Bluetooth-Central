import matplotlib.pyplot as plt
from kinematics_calc import get_current_position, get_current_vel

## --- 2d plotting ---
async def plot_2d_data(ax, data_queue):
    # data lists to store timestamps and x, y, z values
    # NOTE: use a queue or deque instead to avoid memory overflow?
    xdata, ydata, zdata = [], [], []
    timestamp = []
    first_time_unit = 0

    # check if this is the first reading we get
    initial_reading = True
    while True:
        # get data
        data = await data_queue.get()
        t, x, y, z = data

        if initial_reading:
            initial_reading = False
            first_time_unit = t
        
        # Append the data to respective lists for plotting
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
    prev_vel = []
    prev_pos = []

        # data lists to store timestamps and x, y, z values
    # NOTE: use a queue or deque instead to avoid memory overflow?
    xdata, ydata, zdata = [], [], []
    timestamp = []

    # check if this is the first reading we get
    initial_reading = True

    while True:
        # get data
        data = await data_queue.get()
        timestamp, ax, ay, az = data

        # if initial reading, store the values but do no calculations (we have nothing over time to compare with)
        if initial_reading:
            initial_reading = False
            prev_time = timestamp
            prev_vel = [0, 0, 0]    # velocity for x, y, z is 0 (assumption: sensor not currently moving at the beginning)
            prev_pos = [0, 0, 0]    # position for x, y, z is 0 (assumption: origin)

        # secondary and more data points obtained
        else:
            # get difference in time and update prev time to track current time
            delta_time = timestamp - prev_time
            prev_time = timestamp

            # get the current position and velocity
            prev_pos = get_current_position([ax, ay, az], prev_vel, prev_pos, delta_time)
            prev_vel = get_current_vel([ax, ay, az], prev_vel, delta_time)

            # append new data to current data
            xdata.append(prev_pos[0])
            ydata.append(prev_pos[1])
            zdata.append(prev_pos[2])

        # append data to the queue (note: since plt.show() is in main, the plotting code below MUST occur no matter what)
        xdata.append(ax)
        ydata.append(ay)
        zdata.append(az)

        print("hit!")
        axes.clear()  # Clear previous data
        axes.plot3D(xdata, ydata, zdata, 'gray')  # Plot the new data
        plt.draw()  # Redraw the plot
        plt.pause(0.05)  # Non-blocking pause to update the plot
