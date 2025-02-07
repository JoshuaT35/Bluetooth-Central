import asyncio
from bluetooth import ble_connect_imu
from visualization import start_plot
import threading

async def main():
    data_queue = asyncio.Queue()

    # Start BLE connection and data collection
    ble_task = asyncio.create_task(ble_connect_imu(data_queue))

    # Start the real-time plot in a separate thread
    plotting_thread = threading.Thread(target=start_plot, args=(data_queue,))
    plotting_thread.start()
    # start_plot(data_queue)

    await ble_task  # Keeps the BLE connection alive

if __name__ == "__main__":
    asyncio.run(main())
