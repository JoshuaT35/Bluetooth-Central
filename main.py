import asyncio
from bleak import BleakScanner, BleakClient

# Replace these with the actual UUIDs of your Arduino device
SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
CHARACTERISTIC_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"

async def connect_to_arduino():
    print("Scanning for devices...")

    # Scan for devices advertising the desired service UUID
    devices = await BleakScanner.discover(service_uuids=[SERVICE_UUID])

    if not devices:
        print(f"No devices found advertising service UUID: {SERVICE_UUID}")
        return

    # Assuming the first device is your Arduino
    arduino_device = devices[0]
    print(f"Found device: {arduino_device.name} ({arduino_device.address})")

    # Connect to the device
    async with BleakClient(arduino_device.address) as client:
        if not client.is_connected:
            print(f"Failed to connect to {arduino_device.name}.")
            return

        print(f"Connected to {arduino_device.name}.")
        
        # Read the value of the characteristic
        try:
            value = await client.read_gatt_char(CHARACTERISTIC_UUID)
            print(f"Value from characteristic {CHARACTERISTIC_UUID}: {value}\n")

        except Exception as e:
            print(f"Error interacting with characteristic: {e}")

if __name__ == "__main__":
    asyncio.run(connect_to_arduino())
