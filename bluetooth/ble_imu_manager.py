# -------------------------------------------
# Uncomment code if on Windows:
# import sys
# sys.coinit_flags = 0

# # Try to undo STA initialization if it happened
# try:
#     from bleak.backends.winrt.util import allow_sta
#     # tell Bleak we are using a graphical user interface that has been properly
#     # configured to work with asyncio
#     # allow_sta()
# except ImportError:
#     # other OSes and older versions of Bleak will raise ImportError which we
#     # can safely ignore
#     pass

# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# -------------------------------------------


import asyncio, struct
from PySide6.QtCore import QObject, Signal
from bleak import BleakScanner, BleakClient

class BLEImuManager(QObject):
    status = Signal(str)

    def __init__(self):
        super().__init__()
        self.client = None
        self.is_connected = False
        self.read_task = None


    # ------------------------------------------------------
    # Scan for BLE devices
    # ------------------------------------------------------
    async def scan_devices(self, service_uuid):
        self.status.emit("Scanning for IMU devices...")

        devices = await BleakScanner.discover(
            service_uuids=[service_uuid]
        )

        if not devices:
            self.status.emit("No devices found. Make sure Bluetooth is enabled and try again.")
            return
        else:
            self.status.emit(f"Found {len(devices)} device(s).")

        return devices
    
    # ------------------------------------------------------
    # Connect to IMU device via address
    # ------------------------------------------------------
    async def connect(
        self,
        data_queue,
        service_uuid,
        time_uuid,
        accel_x_uuid,
        accel_y_uuid,
        accel_z_uuid,
        gyro_x_uuid,
        gyro_y_uuid,
        gyro_z_uuid,
    ):
        """
        Connects to the device advertising the given service UUID.
        """
        # Scan for devices that advertise this service
        devices = await self.scan_devices(service_uuid)

        # exit early if there is no device in range
        if not devices:
            return
        
        # select the first device
        dev = devices[0]
        self.status.emit(f"Connecting to {dev.name} ({dev.address})...")
        
        self.client = BleakClient(dev.address, timeout=20)

        try:
            await self.client.connect()
        except Exception as e:
            self.status.emit(f"Failed to connect: {e}")

        if not self.client.is_connected:
            self.status.emit("Connection failed.")

        self.status.emit("Connected!")
        self.is_connected = True

        # Start async IMU polling loop
        self.read_task = asyncio.create_task(
            self._read_imu_loop(
                data_queue,
                time_uuid,
                accel_x_uuid,
                accel_y_uuid,
                accel_z_uuid,
                gyro_x_uuid,
                gyro_y_uuid,
                gyro_z_uuid,
            )
        )

    # ------------------------------------------------------
    # Disconnect cleanly
    # ------------------------------------------------------
    async def disconnect(self):
        self.is_connected = False

        if self.read_task:
            self.read_task.cancel()
            try:
                await self.read_task
            except asyncio.CancelledError:
                pass

        if self.client:
            try:
                await self.client.disconnect()
            except Exception:
                pass

        self.client = None

    # ------------------------------------------------------
    # Internal IMU polling loop
    # ------------------------------------------------------
    async def _read_imu_loop(
        self, 
        data_queue,
        time_uuid,
        accel_x_uuid,
        accel_y_uuid,
        accel_z_uuid,
        gyro_x_uuid,
        gyro_y_uuid,
        gyro_z_uuid,
    ):
        """
        Continuously read characteristics from IMU and enqueue parsed values.
        """
        self.status.emit("Starting IMU data streaming...")

        try:
            while self.is_connected:
                # Read raw byte values
                ax = await self.client.read_gatt_char(accel_x_uuid)
                ay = await self.client.read_gatt_char(accel_y_uuid)
                az = await self.client.read_gatt_char(accel_z_uuid)
                gx = await self.client.read_gatt_char(gyro_x_uuid)
                gy = await self.client.read_gatt_char(gyro_y_uuid)
                gz = await self.client.read_gatt_char(gyro_z_uuid)
                time_bytes = await self.client.read_gatt_char(time_uuid)

                # Convert to int/float
                ax = struct.unpack("f", ax)[0]
                ay = struct.unpack("f", ay)[0]
                az = struct.unpack("f", az)[0]
                gx = struct.unpack("f", gx)[0]
                gy = struct.unpack("f", gy)[0]
                gz = struct.unpack("f", gz)[0]
                t = int.from_bytes(time_bytes, byteorder='little', signed=False)

                # debug: print the data
                # print(ax, ay, az, time_bytes)

                # add to the data queue
                await data_queue.put((ax, ay, az, gx, gy, gz, t))

                await asyncio.sleep(0.0005)

        except asyncio.CancelledError:
            self.status.emit("IMU read loop cancelled (disconnect).")

        except Exception as e:
            self.status.emit(f"IMU read error: {e}")


    # ------------------------------------------------------
    # Write to IMU to turn on certain modes (i.e LOW and HIGH power modes)
    # ------------------------------------------------------
    async def set_power_mode(self, power_mode_uuid: str, mode: int):
        """
        Write a uint8 (0 or 1) to the IMU power mode characteristic.
        mode: 0 = LOW, 1 = HIGH
        """
        if not self.client or not self.client.is_connected:
            self.status.emit("Not connected — cannot change power mode.")
            return

        try:
            # uint8 payload
            data = bytes([mode])
            await self.client.write_gatt_char(power_mode_uuid, data)
            self.status.emit(f"Power mode written: {mode}")

        except Exception as e:
            self.status.emit(f"Failed to write power mode: {e}")