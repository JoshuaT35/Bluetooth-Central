import asyncio
from bleak import BleakScanner, BleakClient

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
        if client.is_connected:
            print(f"Connected to {selected_device.name} ({selected_device.address}).")
            # Perform operations with the connected device here
        else:
            print(f"Failed to connect to {selected_device.name} ({selected_device.address}).")

# Run the main function
asyncio.run(scan_and_connect())
