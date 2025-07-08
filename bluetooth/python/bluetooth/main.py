import asyncio
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from bluetooth import start_ble_stream
from visualization import plot_3d_data

async def main():
    # figure and axis for 2D plot
    # fig, ax = plt.subplots()

    # Create 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # stores collected data
    data_queue = asyncio.Queue()

    # Get the current event loop so we can schedule coroutines from threads
    loop = asyncio.get_running_loop()

    # Define the callback that Rust will call
    def callback(ax_val, ay_val, az_val, time_val):
        # Push data to the queue from Rust thread → Python event loop
        asyncio.run_coroutine_threadsafe(
            data_queue.put((ax_val, ay_val, az_val, time_val)),
            loop
        )

    # Start BLE stream (calls Rust, which uses the callback)
    start_ble_stream(callback)

    # create BLE connection and data collection tasks
    # ble_task = asyncio.create_task(start_ble_stream(data_queue))
    plot_task = asyncio.create_task(plot_3d_data(ax, data_queue))

    # main waits for these tasks to complete (which is ideally never)
    # await ble_task
    await plot_task

    # idk if this works, might be a replacement for the above awaits
    # await asyncio.gather(ble_task, plot_task)

if __name__ == "__main__":
    asyncio.run(main())
    plt.show()
