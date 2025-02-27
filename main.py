import asyncio
from bluetooth import ble_connect_imu
from visualization import start_plot

async def print_data(data_queue):
    while True:
        # Get data from the queue and print it
        data = await data_queue.get()
        print(f"Received data: {data}")
        print("\n")
        # You can put a condition to stop printing if needed, e.g., after certain number of data points.
        data_queue.task_done()

async def main():
    data_queue = asyncio.Queue()

    # Start BLE connection and data collection
    ble_task = asyncio.create_task(ble_connect_imu(data_queue))
    print_task = asyncio.create_task(print_data(data_queue))
    
    await ble_task  # Keeps the BLE connection alive
    await print_task

if __name__ == "__main__":
    asyncio.run(main())
