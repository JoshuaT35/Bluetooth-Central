import asyncio
from bluetooth import ble_connect_imu
from visualization import start_plot
from kinematics_calc import get_current_position
import matplotlib.pyplot as plt

## --- 2d plotting ---
async def print_data(data_queue):
    while True:
        data = await data_queue.get()
        print(f"Received data")
        print("\n")
        t, x, y, z = data
        
        # Append the data to respective lists for plotting
        timestamp.append(t)
        xdata.append(x)
        ydata.append(y)
        zdata.append(z)
        
        # Clear the plot and redraw it with the updated data
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

async def main():
    data_queue = asyncio.Queue()

    # Start BLE connection and data collection
    ble_task = asyncio.create_task(ble_connect_imu(data_queue))
    print_task = asyncio.create_task(print_data(data_queue))

    await ble_task  # Keeps the BLE connection alive
    await print_task

# Setup the 2D plot
fig, ax = plt.subplots()  # Create a figure and axis for 2D plot
timestamp, xdata, ydata, zdata = [], [], [], []  # Data lists to store timestamps and x, y, z values
asyncio.run(main())
plt.show()

## --- 3d plotting ---
# async def plot_data(data_queue):
#     initial_reading = True
#     while True:
#         # get data
#         data = await data_queue.get()
#         timestamp, ax, ay, az = data

#         # if initial reading, wait until we get the next reading
#         if initial_reading:
#             initial_reading = False
#             prev_time = timestamp
#             prev_vel = [0, 0, 0]
#             prev_pos = [0, 0, 0]
#         # secondary+ data points obtained
#         else:
#             print("here now\n")
#             # get change in time and update prev time
#             delta_time = timestamp - prev_time
#             prev_time = timestamp
#             print("1\n")

#             # get the current position and velocity
#             prev_pos, prev_vel = get_current_position([ax, ay, az], prev_vel, prev_pos, delta_time)
#             print("2\n")

#             # append new data
#             xdata.append(prev_pos[0])
#             ydata.append(prev_pos[1])
#             zdata.append(prev_pos[2])
#             print("over here\n")

#         # xdata.append(ax)
#         # ydata.append(ay)
#         # zdata.append(az)
#         print("hit!")
#         axes.clear()  # Clear previous data
#         axes.plot3D(xdata, ydata, zdata, 'gray')  # Plot the new data
#         plt.draw()  # Redraw the plot
#         plt.pause(0.05)  # Non-blocking pause to update the plot


# async def main():
#     data_queue = asyncio.Queue()

#     # Start BLE connection and data collection
#     ble_task = asyncio.create_task(ble_connect_imu(data_queue))
#     plot_task = asyncio.create_task(plot_data(data_queue))

#     await ble_task  # Keeps the BLE connection alive
#     await plot_task

# # Setup the 3D plot
# fig = plt.figure()
# axes = fig.add_subplot(111, projection='3d')
# xdata = []
# ydata = []
# zdata = []

# # calulation data
# prev_vel = [0, 0, 0]
# prev_pos = [0, 0, 0]
# prev_time = 0

# # run async tasks
# asyncio.run(main())

# # show the plot
# plt.show()
