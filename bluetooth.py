import asyncio
from bleak import BleakScanner, BleakClient

# IMU sensor UUIDs
SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
SWITCH_CHARACTERISTIC_ACCEL_X_UUID = "19B10010-E8F2-537E-4F6C-D104768A1214"
SWITCH_CHARACTERISTIC_ACCEL_Y_UUID = "19B10020-E8F2-537E-4F6C-D104768A1214"
SWITCH_CHARACTERISTIC_ACCEL_Z_UUID = "19B10030-E8F2-537E-4F6C-D104768A1214"
SWITCH_CHARACTERISTIC_GYRO_X_UUID = "19B10040-E8F2-537E-4F6C-D104768A1214"
SWITCH_CHARACTERISTIC_GYRO_Y_UUID = "19B10050-E8F2-537E-4F6C-D104768A1214"
SWITCH_CHARACTERISTIC_GYRO_Z_UUID = "19B10060-E8F2-537E-4F6C-D104768A1214"

async def connect_to_arduino():
    print("Scanning for devices...")

    # Scan for devices advertising the desired service UUID
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
    
    selected_device = devices[choice]
    print(f"\nConnecting to {selected_device.name} ({selected_device.address})...")

    # Connect to the device
    async with BleakClient(selected_device.address) as client:
        if not client.is_connected:
            print(f"Failed to connect to {selected_device.name}.")
            return

        print(f"Connected to {selected_device.name}.")
        
        # Read the value of the characteristics
        try:
            while True:
                ax = await client.read_gatt_char(SWITCH_CHARACTERISTIC_ACCEL_X_UUID)
                ay = await client.read_gatt_char(SWITCH_CHARACTERISTIC_ACCEL_Y_UUID)
                az = await client.read_gatt_char(SWITCH_CHARACTERISTIC_ACCEL_Z_UUID)
                gx = await client.read_gatt_char(SWITCH_CHARACTERISTIC_GYRO_X_UUID)
                gy = await client.read_gatt_char(SWITCH_CHARACTERISTIC_GYRO_Y_UUID)
                gz = await client.read_gatt_char(SWITCH_CHARACTERISTIC_GYRO_Z_UUID)

                # # Decode and print values (given by CHATGPT, idk if needed)
                # ax_val = int.from_bytes(ax, byteorder='little', signed=True)
                # ay_val = int.from_bytes(ay, byteorder='little', signed=True)
                # az_val = int.from_bytes(az, byteorder='little', signed=True)
                # gx_val = int.from_bytes(gx, byteorder='little', signed=True)
                # gy_val = int.from_bytes(gy, byteorder='little', signed=True)
                # gz_val = int.from_bytes(gz, byteorder='little', signed=True)

                # debug
                # print(f"Value of ax characteristic {SWITCH_CHARACTERISTIC_ACCEL_X_UUID}: {ax}\n")
                # print(f"Value of ay characteristic {SWITCH_CHARACTERISTIC_ACCEL_Y_UUID}: {ay}\n")
                # print(f"Value of az characteristic {SWITCH_CHARACTERISTIC_ACCEL_Z_UUID}: {az}\n")
                # print(f"Value of gx characteristic {SWITCH_CHARACTERISTIC_GYRO_X_UUID}: {gx}\n")
                # print(f"Value of gy characteristic {SWITCH_CHARACTERISTIC_GYRO_Y_UUID}: {gy}\n")
                # print(f"Value of gz characteristic {SWITCH_CHARACTERISTIC_GYRO_Z_UUID}: {gz}\n")

        except asyncio.CancelledError:
            print("Disconnecting...")
        except KeyboardInterrupt:
            print("Keyboard interrupt received. Disconnecting...")
        except Exception as e:
            print(f"Error interacting with characteristic: {e}")


if __name__ == "__main__":
    asyncio.run(connect_to_arduino())
