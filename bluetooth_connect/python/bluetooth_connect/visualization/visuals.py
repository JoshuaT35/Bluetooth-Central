import matplotlib.pyplot as plt
import collections
import numpy as np
# from calculation.kinematics import get_current_position, get_current_vel
from ahrs.filters import Madgwick
from ahrs.common.orientation import q2R
from math import atan2, sqrt, pi, radians

# maximum number of data that should be plotted at a time
MAX_NUM_DATA_PLOT = 100

def rotate_to_world_frame(ax, ay, az, pitch_deg, roll_deg):
    pitch = radians(pitch_deg)
    roll = radians(roll_deg)

    # Rotation matrix: pitch (Y), then roll (X)
    R = np.array([
        [np.cos(pitch), np.sin(roll)*np.sin(pitch), np.cos(roll)*np.sin(pitch)],
        [0,             np.cos(roll),              -np.sin(roll)],
        [-np.sin(pitch), np.sin(roll)*np.cos(pitch), np.cos(roll)*np.cos(pitch)]
    ])
    
    acc_body = np.array([ax, ay, az])
    acc_world = R @ acc_body
    return acc_world


## --- 2d plotting ---
# async def plot_2d_data(ax, data_queue):
#     # data lists to store timestamps and x, y, z values
#     # NOTE: use a queue or deque instead to avoid memory overflow?
#     xdata, ydata, zdata = [], [], []
#     timestamp = []
#     first_time_unit = 0

#     # to check if this is the first reading we get
#     initial_reading = True

#     # continuously retrieve data and plot it
#     while True:
#         # get data
#         data = await data_queue.get()
#         x, y, z, t = data

#         # mark the initial reading
#         if initial_reading:
#             initial_reading = False
#             first_time_unit = t
        
#         # Append the data to respective lists for plotting
#         # first time unit may not be 0.
#         # to set scale to begin at 0, we do current time (t) - previous time unit (first_time_unit)
#         timestamp.append(t-first_time_unit)
#         xdata.append(x)
#         ydata.append(y)
#         zdata.append(z)
        
#         # Clear the plot to redraw it with the updated data
#         ax.clear()
        
#         # Plot x, y, z values with respect to time (timestamp)
#         ax.plot(timestamp, xdata, label="X", color="r")
#         ax.plot(timestamp, ydata, label="Y", color="g")
#         ax.plot(timestamp, zdata, label="Z", color="b")
        
#         ax.set_xlabel('Time (ms)')  # Label for x-axis
#         ax.set_ylabel('Values')  # Label for y-axis
#         ax.set_title('Real-Time Plot of x, y, z')  # Title of the plot
        
#         ax.legend()  # Show legend
        
#         plt.draw()  # Redraw the plot
#         plt.pause(0.05)  # Non-blocking pause to update the plot


# --- 3d plotting ---
async def plot_3d_data(axes, data_queue):
    # variables
    prev_time = 0
    prev_vel = np.zeros(3)
    prev_pos = np.zeros(3)
    # prev_time = 0
    # prev_vel = [0, 0, 0]
    # prev_pos = [0, 0, 0]
    # current_vel = [0, 0, 0] # initial velocity for x, y, z is 0 (assumption: sensor not currently moving at the beginning)
    # current_pos = [0, 0, 0] # initial position for x, y, z is 0 (assumption: position of origin)

    # data lists to store timestamps and x, y, z values
    xdata = collections.deque(maxlen=MAX_NUM_DATA_PLOT)
    ydata = collections.deque(maxlen=MAX_NUM_DATA_PLOT)
    zdata = collections.deque(maxlen=MAX_NUM_DATA_PLOT)

    # Orientation tracking
    pitch = 0.0
    roll = 0.0
    alpha = 0.98

    madgwick = Madgwick()
    q = np.array([1.0, 0.0, 0.0, 0.0])  # Initial quaternion

    # check if this is the first reading we get
    initial_reading = True

    while True:
        # get data
        data = await data_queue.get()
        # a_ -> units of g
        # g_ -> units of degrees/s
        # timestamp -> units of ms (milliseconds)
        ax, ay, az, gx, gy, gz, timestamp = data

        # convert from g to m/s^2
        aX *= 9.81
        aY *= 9.81
        aZ *= 9.81


        # if initial reading, do no calculations (we have nothing over time to compare with)
        if initial_reading:
            initial_reading = False
            continue

        # Time delta in seconds (convert from ms to s)
        dt = (timestamp - prev_time) / 1000.0

        # --- Complementary filter for orientation ---
        accelPitch = atan2(ax, sqrt(ay**2 + az**2)) * 180 / pi
        accelRoll  = atan2(ay, sqrt(ax**2 + az**2)) * 180 / pi

        pitch = alpha * (pitch + gy * dt) + (1 - alpha) * accelPitch
        roll  = alpha * (roll  + gx * dt) + (1 - alpha) * accelRoll

        # --- Rotate acceleration to world frame ---
        acc_world = rotate_to_world_frame(ax, ay, az, pitch, roll)

        # --- Remove gravity from world-frame Z ---
        acc_world[2] -= 9.81  # If Z is up in your world frame

        # --- Integrate to get velocity and position ---
        current_vel = prev_vel + acc_world * dt
        current_pos = prev_pos + current_vel * dt

        # append new position data to current position data
        xdata.append(current_pos[0])
        ydata.append(current_pos[1])
        zdata.append(current_pos[2])

        # print("position is ", current_pos[0], " ", current_pos[1], " ", current_pos[2])
        
        # update prev variables to track new data
        prev_time = timestamp
        prev_vel = current_vel
        prev_pos = current_pos

        # NOTE: since plt.show() is in main, the plotting code below MUST occur no matter what
        axes.clear()  # Clear previous data
        axes.plot3D(list(xdata), list(ydata), list(zdata), 'gray')  # Plot the new data
        plt.draw()  # Redraw the plot
        plt.pause(0.05)  # Non-blocking pause to update the plot