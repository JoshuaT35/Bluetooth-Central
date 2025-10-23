import matplotlib.pyplot as plt
import collections
import numpy as np
from ahrs.filters import Madgwick
from ahrs.common.orientation import q2euler
from math import atan2, sqrt, pi, radians

MAX_NUM_DATA_PLOT = 100

def rotate_to_world_frame(ax, ay, az, pitch_deg, roll_deg):
    pitch = radians(pitch_deg)
    roll = radians(roll_deg)

    R = np.array([
        [np.cos(pitch), np.sin(roll)*np.sin(pitch), np.cos(roll)*np.sin(pitch)],
        [0,             np.cos(roll),              -np.sin(roll)],
        [-np.sin(pitch), np.sin(roll)*np.cos(pitch), np.cos(roll)*np.cos(pitch)]
    ])

    acc_body = np.array([ax, ay, az])
    acc_world = R @ acc_body
    return acc_world

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
        x, y, z, gx, gy, gz, t = data

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

async def plot_3d_data(axes, data_queue):
    prev_time = None
    prev_vel = np.zeros(3)
    prev_pos = np.zeros(3)

    xdata = collections.deque(maxlen=MAX_NUM_DATA_PLOT)
    ydata = collections.deque(maxlen=MAX_NUM_DATA_PLOT)
    zdata = collections.deque(maxlen=MAX_NUM_DATA_PLOT)

    # Complementary Filter init
    pitch_cf = 0.0
    roll_cf = 0.0
    alpha = 0.98

    # Madgwick Filter init
    madgwick = Madgwick()
    q = np.array([1.0, 0.0, 0.0, 0.0])

    while True:
        # Fetch sensor data
        ax, ay, az, gx, gy, gz, timestamp = await data_queue.get()

        # Convert g to m/s^2
        ax *= 9.81
        ay *= 9.81
        az *= 9.81

        # Skip first reading
        if prev_time is None:
            prev_time = timestamp
            continue

        # Time delta in seconds
        dt = (timestamp - prev_time) / 1000.0

        ### --- Complementary Filter ---
        accelPitch = atan2(ax, sqrt(ay**2 + az**2)) * 180 / pi
        accelRoll  = atan2(ay, sqrt(ax**2 + az**2)) * 180 / pi

        pitch_cf = alpha * (pitch_cf + gy * dt) + (1 - alpha) * accelPitch
        roll_cf  = alpha * (roll_cf  + gx * dt) + (1 - alpha) * accelRoll

        ### --- Madgwick Filter Update ---
        gyro_rad = np.radians([gx, gy, gz])  # convert deg/s to rad/s
        acc = np.array([ax, ay, az])
        q = madgwick.updateIMU(q=q, gyr=gyro_rad, acc=acc)

        # Get roll, pitch, yaw from quaternion
        roll_m, pitch_m, yaw_m = np.degrees(q2euler(q))

        ### --- Acceleration in world frame (using complementary filter angles) ---
        acc_world = rotate_to_world_frame(ax, ay, az, pitch_cf, roll_cf)

        # Remove gravity from Z
        acc_world[2] -= 9.81

        ### --- Integrate to get velocity and position ---
        current_vel = prev_vel + acc_world * dt
        current_pos = prev_pos + current_vel * dt

        # Store for plotting
        xdata.append(current_pos[0])
        ydata.append(current_pos[1])
        zdata.append(current_pos[2])

        # Update previous values
        prev_time = timestamp
        prev_vel = current_vel
        prev_pos = current_pos

        ### --- Plot ---
        axes.clear()
        axes.plot3D(list(xdata), list(ydata), list(zdata), 'gray')
        axes.set_title(f"Roll: {roll_cf:.2f}° | Pitch: {pitch_cf:.2f}°\nMadgwick RPY: {roll_m:.1f}°, {pitch_m:.1f}°, {yaw_m:.1f}°")
        plt.draw()
        plt.pause(0.05)
