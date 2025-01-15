import asyncio
from bleak import BleakScanner, BleakClient

# Replace these with the actual UUIDs of your Arduino device
SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
CHARACTERISTIC_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"

async def scan_and_connect():
    print("Scanning for Bluetooth devices...")
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

    async with BleakClient(selected_device.address) as client:
        if not client.is_connected:
            print(f"Failed to connect to {selected_device.name}.")
            return
        
        print(f"Connected to {selected_device.name} ({selected_device.address}).")
        # Perform operations with the connected device here

        try:
            # value = await client.read_gatt_char(CHARACTERISTIC_UUID)
            # print(f"Value from characteristic {CHARACTERISTIC_UUID}: {value}\n")
            # write a non zero value
            write_value = b'\x00'
            await client.write_gatt_char(CHARACTERISTIC_UUID, write_value)
            print("wrote a value")

        except Exception as e:
            print(f"Error interacting with characteristic: {e}")

# Run the main function
asyncio.run(scan_and_connect())
