import asyncio
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError
import kinematics_calc as kmc
from collections import deque
import struct

# IMU sensor UUIDs
SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
SWITCH_CHARACTERISTIC_ACCEL_X_UUID = "19B10010-E8F2-537E-4F6C-D104768A1214"
SWITCH_CHARACTERISTIC_ACCEL_Y_UUID = "19B10020-E8F2-537E-4F6C-D104768A1214"
SWITCH_CHARACTERISTIC_ACCEL_Z_UUID = "19B10030-E8F2-537E-4F6C-D104768A1214"
# SWITCH_CHARACTERISTIC_GYRO_X_UUID = "19B10040-E8F2-537E-4F6C-D104768A1214"
# SWITCH_CHARACTERISTIC_GYRO_Y_UUID = "19B10050-E8F2-537E-4F6C-D104768A1214"
# SWITCH_CHARACTERISTIC_GYRO_Z_UUID = "19B10060-E8F2-537E-4F6C-D104768A1214"
SWITCH_CHARACTERISTIC_TIME_UUID = "19B10070-E8F2-537E-4F6C-D104768A1214"


# Data storage (Fixed-length deque for real-time plotting)
BUFFER_SIZE = 100  # Store last 100 data points
time_series = deque(maxlen=BUFFER_SIZE)
ax_series = deque(maxlen=BUFFER_SIZE)
ay_series = deque(maxlen=BUFFER_SIZE)
az_series = deque(maxlen=BUFFER_SIZE)

# Async queue for sharing data
dataQueue = asyncio.Queue()


async def ble_read_imu_data(client, dataQueue):
    """Continuously read data from BLE and push to queue"""
    try:
        while True:
            # get raw byte data
            ax = await client.read_gatt_char(SWITCH_CHARACTERISTIC_ACCEL_X_UUID)
            ay = await client.read_gatt_char(SWITCH_CHARACTERISTIC_ACCEL_Y_UUID)
            az = await client.read_gatt_char(SWITCH_CHARACTERISTIC_ACCEL_Z_UUID)
            # gx = await client.read_gatt_char(SWITCH_CHARACTERISTIC_GYRO_X_UUID)
            # gy = await client.read_gatt_char(SWITCH_CHARACTERISTIC_GYRO_Y_UUID)
            # gz = await client.read_gatt_char(SWITCH_CHARACTERISTIC_GYRO_Z_UUID)
            # time = await client.read_gatt_char(SWITCH_CHARACTERISTIC_TIME_UUID)

            # convert from byte array to int
            # time = int.from_bytes(time, byteorder='little', signed=False)

            # Convert from byte array to float (4 bytes per float)
            ax = struct.unpack('f', ax)[0]
            ay = struct.unpack('f', ay)[0]
            az = struct.unpack('f', az)[0]

            # debug: print data
            # print(f"ax is {ax}, ")
            # print(f"ay is {ay}, ")
            # print(f"az is {az}, ")
            # print(f"time is {time}, ")

            # Add timestamp
            timestamp = asyncio.get_event_loop().time()

            print(f"time is {timestamp}, ")
            print("\n")

            # Send data to queue
            await dataQueue.put((timestamp, ax, ay, az))

            await asyncio.sleep(0.05)  # Adjust as needed for your update rate

    except asyncio.CancelledError:
        print("Disconnecting...")
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Disconnecting...")
    except Exception as e:
        print(f"Error interacting with characteristic: {e}")




async def ble_connect_imu(dataQueue):
    print("Scanning for devices...")

    devices = await BleakScanner.discover()

    if not devices:
        print("No devices found. Make sure Bluetooth is enabled and try again.")
        return

    print("\nFound devices:")
    for i, device in enumerate(devices):
        print(f"{i}: {device.name} ({device.address})")

    try:
        choice = int(input("\nEnter the number of the device you want to connect to: "))
        if choice < 0 or choice >= len(devices):
            print("Invalid choice. Exiting.")
            return
    except ValueError:
        print("Invalid input. Please enter a number. Exiting.")
        return

    print(f"choice is {choice}\n")
    selected_device = devices[choice]
    print(f"\nConnecting to {selected_device.name} ({selected_device.address})...")

    async with BleakClient(selected_device.address, timeout=20) as client:
        if not client.is_connected:
            print(f"Failed to connect to {selected_device.name}.")
            return

        print(f"Connected to {selected_device.name}.")
        await ble_read_imu_data(client, dataQueue)
