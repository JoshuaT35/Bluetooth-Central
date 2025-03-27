import asyncio
import matplotlib.pyplot as plt

from bluetooth import ble_connect_imu
from visualization import plot_2d_data

async def main():
    # figure and axis for 2D plot
    fig, ax = plt.subplots()

    # stores collected data
    data_queue = asyncio.Queue()

    # create BLE connection and data collection tasks
    ble_task = asyncio.create_task(ble_connect_imu(data_queue))
    plot_task = asyncio.create_task(plot_2d_data(ax, data_queue))

    # main waits for these tasks to complete (which is ideally never)
    await ble_task
    await plot_task

    # idk if this works, might be a replacement for the above awaits
    # await asyncio.gather(ble_task, plot_task)

if __name__ == "__main__":
    asyncio.run(main())
    plt.show()