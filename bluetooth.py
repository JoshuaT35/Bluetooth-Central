import asyncio
from bleak import BleakScanner, BleakClient
import struct

# IMU sensor UUIDs
SERVICE_UUID = "0b91a798-23b1-4369-9d45-a3a26d936904"
SWITCH_CHARACTERISTIC_ACCEL_X_UUID = "026080c9-dc3a-401b-829c-2ee3b5565200"
SWITCH_CHARACTERISTIC_ACCEL_Y_UUID = "e0a0b53e-5c53-4acf-bf79-39d2982362e9"
SWITCH_CHARACTERISTIC_ACCEL_Z_UUID = "94b54966-faa7-48c1-9b53-7e44a9a872be"
# SWITCH_CHARACTERISTIC_GYRO_X_UUID = "d30c8099-5b3e-4d4f-9c42-40b47a3f71ea"
# SWITCH_CHARACTERISTIC_GYRO_Y_UUID = "734c0d37-c4fc-4265-953f-0aa24d28b1a5"
# SWITCH_CHARACTERISTIC_GYRO_Z_UUID = "e51f3e60-3fdd-4591-9910-87362247c68d"
SWITCH_CHARACTERISTIC_CURRENT_TIME_UUID = "72d913bb-e8df-44b8-b8ec-4f098978e0be"


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
            time = await client.read_gatt_char(SWITCH_CHARACTERISTIC_CURRENT_TIME_UUID)

            # convert from byte array to int
            time = int.from_bytes(time, byteorder='little', signed=False)

            # Convert from byte array to float (4 bytes per float)
            ax = struct.unpack('f', ax)[0]
            ay = struct.unpack('f', ay)[0]
            az = struct.unpack('f', az)[0]

            # debug: print data
            # print(f"ax is {ax}, ")
            # print(f"ay is {ay}, ")
            # print(f"az is {az}, ")
            # print(f"time is {time}, ")

            # send data to queue
            await dataQueue.put((time, ax, ay, az))

            # pause data collection (might need to account for this in sensor readings)
            await asyncio.sleep(0.05)

    except asyncio.CancelledError:
        print("Disconnecting...")
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Disconnecting...")
    except Exception as e:
        print(f"Error interacting with characteristic: {e}")



# async function that allows user to select sensor to bluetooth to
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

        #begin reading IMU data
        await ble_read_imu_data(client, dataQueue)
