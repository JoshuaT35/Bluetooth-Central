# -------------------------------------------
# Uncomment code if on Windows:
# import sys
# sys.coinit_flags = 0  # 0 means MTA

# # Try to undo STA initialization if it happened
# try:
#     from bleak.backends.winrt.util import allow_sta
#     # tell Bleak we are using a graphical user interface that has been properly
#     # configured to work with asyncio
#     allow_sta()
# except ImportError:
#     # other OSes and older versions of Bleak will raise ImportError which we
#     # can safely ignore
#     pass
# -------------------------------------------


import asyncio
import matplotlib.pyplot as plt

from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

from plotting.visualization import plot_2d_data
from core.device_profiles import AVAILABLE_DEVICES
from gui.main_window import MainWindow
from bluetooth.ble_imu_manager import BLEImuManager


async def scan(gui, ble):
    """
    Callback triggered when the Scan button is clicked.
    Uses the selected device profile from the GUI.
    """
    profile = gui.selected_profile
    if not profile:
        gui.append_log("No device profile selected.")
        return

    devices = await ble.scan_devices(profile["SERVICE_UUID"])
    if devices:
        for d in devices:
            gui.append_log(f"Found: {d.name}  ({d.address})")


async def connect_and_stream(gui, ble, data_queue):
    """
    Connect to first matching device and start IMU read loop.
    """
    profile = gui.selected_profile
    if not profile:
        gui.append_log("No device profile selected.")
        return

    await ble.connect(
        data_queue,
        profile["SERVICE_UUID"],
        profile["TIME_UUID"],
        profile["ACCEL_X_UUID"],
        profile["ACCEL_Y_UUID"],
        profile["ACCEL_Z_UUID"],
        profile["GYRO_X_UUID"],
        profile["GYRO_Y_UUID"],
        profile["GYRO_Z_UUID"],
    )


async def disconnect(gui, ble):
    """
    Disconnect from the Bluetooth device.
    """
    if not ble.is_connected:
        gui.append_log("No device is currently connected.")
        return

    gui.append_log("Disconnecting...")
    await ble.disconnect()
    gui.append_log("Disconnected.")


async def main_async():
    """
    Runs inside the qasync event loop.
    """
    # Qt application
    # app = QApplication(sys.argv)
    app = QApplication()

    # qasync event loop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # BLE + GUI setup
    ble = BLEImuManager()
    gui = MainWindow(AVAILABLE_DEVICES)

    # Forward BLE log messages into GUI
    ble.status.connect(gui.append_log)

    # Data queue for IMU readings
    data_queue = asyncio.Queue()

    # Button wiring
    gui.scan_button.clicked.connect(
        lambda: asyncio.create_task(scan(gui, ble))
    )
    gui.connect_button.clicked.connect(
        lambda: asyncio.create_task(connect_and_stream(gui, ble, data_queue))
    )
    gui.disconnect_button.clicked.connect(
        lambda: asyncio.create_task(disconnect(gui, ble))
    )

    # Write Low Power Mode
    gui.low_power_button.clicked.connect(
        lambda: asyncio.create_task(
            ble.set_power_mode(
                gui.selected_profile["POWER_MODE_UUID"],
                0  # MODE_LOW
            )
        )
    )

    # Write High Power Mode
    gui.high_power_button.clicked.connect(
        lambda: asyncio.create_task(
            ble.set_power_mode(
                gui.selected_profile["POWER_MODE_UUID"],
                1  # MODE_HIGH
            )
        )
    )

    gui.show()

    # Use GUI's axes
    ax = gui.ax
    canvas = gui.canvas

    # Plot loop
    loop.create_task(plot_2d_data(ax, canvas, data_queue))

    # Run forever
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    asyncio.run(main_async())