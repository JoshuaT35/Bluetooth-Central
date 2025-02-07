import asyncio
from bluetooth import ble_connect_imu
from visualization import start_plot

async def main():
    data_queue = asyncio.Queue()

    # Start BLE connection and data collection
    ble_task = asyncio.create_task(ble_connect_imu(data_queue))

    # Start the real-time plot
    start_plot(data_queue)

    await ble_task  # Keeps the BLE connection alive

if __name__ == "__main__":
    asyncio.run(main())
