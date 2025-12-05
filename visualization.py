import matplotlib.pyplot as plt
import collections
import numpy as np
from ahrs.filters import Madgwick
from ahrs.common.orientation import q2euler
from math import atan2, sqrt, pi, radians
from PySide6.QtCore import QTimer
import asyncio
import csv

MAX_NUM_DATA_PLOT = 100


async def test_loop(ax, canvas, data_queue):

    def foo():
        if data_queue.empty():
            # print("Queue is empty")
            return

        try:
            data = data_queue.get_nowait()
        except asyncio.QueueEmpty:
            # print("Queue empty exception")
            return

        x, y, z, gx, gy, gz, t = data
        # print("x is", x)

    # QTimer must have a Qt parent to survive
    timer = QTimer(canvas)
    timer.timeout.connect(foo)
    timer.start(50)

## --- 2d plotting ---
async def plot_2d_data(ax, canvas, data_queue):
    # data lists to store timestamps and x, y, z values
    xdata, ydata, zdata = [], [], []
    timestamp = []
    first_time_unit = 0

    # to check if this is the first reading we get
    initial_reading = True

    # Create/open CSV file and write header
    csv_file = open("accel_log.csv", "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["time", "accel_x", "accel_y", "accel_z"])

    # Set up QTimer to periodically update the plot
    def update_plot():
        nonlocal xdata, ydata, zdata, timestamp, first_time_unit, initial_reading
        try:
            if not data_queue.empty():
                # Get data
                data = data_queue.get_nowait()
                x, y, z, gx, gy, gz, t = data

                # Mark the initial reading
                if initial_reading:
                    initial_reading = False
                    first_time_unit = t

                # get relative time
                rel_time = t - first_time_unit
                
                # Append the data to respective lists for plotting
                timestamp.append(rel_time)
                xdata.append(x)
                ydata.append(y)
                zdata.append(z)

                # ⭐ Write directly to CSV (no RAM accumulation)
                csv_writer.writerow([rel_time, x, y, z])
                
                # Clear the plot to redraw it with the updated data
                ax.clear()
                
                # Plot x, y, z values with respect to time (timestamp)
                ax.plot(timestamp, xdata, label="X-axes", color="r")
                ax.plot(timestamp, ydata, label="Y-axes", color="g")
                ax.plot(timestamp, zdata, label="Z-axes", color="b")
                
                ax.set_xlabel('Time (ms)')  # Label for x-axis
                ax.set_ylabel('Values')  # Label for y-axis
                ax.set_title('Real-Time Plot of acceleration in x, y, z, axis')  # Title of the plot
                
                ax.legend()  # Show legend
                
                canvas.draw()  # Redraw the plot
        except Exception as e:
            print(f"Plot update error: {e}")
    
    # Set up QTimer to update the plot periodically (e.g., every 50ms)
    timer = QTimer(canvas)
    timer.timeout.connect(update_plot)
    timer.start(10)  # Update every 25ms

    # Ensure file closes when the window closes
    canvas.destroyed.connect(lambda: csv_file.close())



# def rotate_to_world_frame(ax, ay, az, pitch_deg, roll_deg):
#     pitch = radians(pitch_deg)
#     roll = radians(roll_deg)

#     R = np.array([
#         [np.cos(pitch), np.sin(roll)*np.sin(pitch), np.cos(roll)*np.sin(pitch)],
#         [0,             np.cos(roll),              -np.sin(roll)],
#         [-np.sin(pitch), np.sin(roll)*np.cos(pitch), np.cos(roll)*np.cos(pitch)]
#     ])

#     acc_body = np.array([ax, ay, az])
#     acc_world = R @ acc_body
#     return acc_world



# async def plot_3d_data(axes, data_queue):
#     prev_time = None
#     prev_vel = np.zeros(3)
#     prev_pos = np.zeros(3)

#     xdata = collections.deque(maxlen=MAX_NUM_DATA_PLOT)
#     ydata = collections.deque(maxlen=MAX_NUM_DATA_PLOT)
#     zdata = collections.deque(maxlen=MAX_NUM_DATA_PLOT)

#     # Complementary Filter init
#     pitch_cf = 0.0
#     roll_cf = 0.0
#     alpha = 0.98

#     # Madgwick Filter init
#     madgwick = Madgwick()
#     q = np.array([1.0, 0.0, 0.0, 0.0])

#     while True:
#         # Fetch sensor data
#         ax, ay, az, gx, gy, gz, timestamp = await data_queue.get()

#         # Convert g to m/s^2
#         ax *= 9.81
#         ay *= 9.81
#         az *= 9.81

#         # Skip first reading
#         if prev_time is None:
#             prev_time = timestamp
#             continue

#         # Time delta in seconds
#         dt = (timestamp - prev_time) / 1000.0

#         ### --- Complementary Filter ---
#         accelPitch = atan2(ax, sqrt(ay**2 + az**2)) * 180 / pi
#         accelRoll  = atan2(ay, sqrt(ax**2 + az**2)) * 180 / pi

#         pitch_cf = alpha * (pitch_cf + gy * dt) + (1 - alpha) * accelPitch
#         roll_cf  = alpha * (roll_cf  + gx * dt) + (1 - alpha) * accelRoll

#         ### --- Madgwick Filter Update ---
#         gyro_rad = np.radians([gx, gy, gz])  # convert deg/s to rad/s
#         acc = np.array([ax, ay, az])
#         q = madgwick.updateIMU(q=q, gyr=gyro_rad, acc=acc)

#         # Get roll, pitch, yaw from quaternion
#         roll_m, pitch_m, yaw_m = np.degrees(q2euler(q))

#         ### --- Acceleration in world frame (using complementary filter angles) ---
#         acc_world = rotate_to_world_frame(ax, ay, az, pitch_cf, roll_cf)

#         # Remove gravity from Z
#         acc_world[2] -= 9.81

#         ### --- Integrate to get velocity and position ---
#         current_vel = prev_vel + acc_world * dt
#         current_pos = prev_pos + current_vel * dt

#         # Store for plotting
#         xdata.append(current_pos[0])
#         ydata.append(current_pos[1])
#         zdata.append(current_pos[2])

#         # Update previous values
#         prev_time = timestamp
#         prev_vel = current_vel
#         prev_pos = current_pos

#         ### --- Plot ---
#         axes.clear()
#         axes.plot3D(list(xdata), list(ydata), list(zdata), 'gray')
#         axes.set_title(f"Roll: {roll_cf:.2f}° | Pitch: {pitch_cf:.2f}°\nMadgwick RPY: {roll_m:.1f}°, {pitch_m:.1f}°, {yaw_m:.1f}°")
#         plt.draw()
#         plt.pause(0.05)
