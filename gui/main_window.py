import os
import sys

os.environ["QT_API"] = "PyQt6"

from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QTextEdit, QComboBox
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class MainWindow(QMainWindow):
    def __init__(self, device_profiles):
        super().__init__()

        self.device_profiles = device_profiles  # <-- no UUIDs stored here
        self.selected_profile = None

        layout = QVBoxLayout()

        # Device type selector
        self.profile_box = QComboBox()
        self.profile_box.addItems(device_profiles.keys())
        self.profile_box.currentIndexChanged.connect(self._on_profile_selected)
        layout.addWidget(self.profile_box)

        # Logs
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        # Scan button
        self.scan_button = QPushButton("Scan")
        layout.addWidget(self.scan_button)

        # Connect button
        self.connect_button = QPushButton("Connect")
        layout.addWidget(self.connect_button)

        # Disconnect button
        self.disconnect_button = QPushButton("Disonnect")
        layout.addWidget(self.disconnect_button)

        # Power Mode buttons
        self.low_power_button = QPushButton("Low Power Mode")
        self.high_power_button = QPushButton("High Power Mode")

        layout.addWidget(self.low_power_button)
        layout.addWidget(self.high_power_button)

        # Add Matplotlib canvas for plot
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 🔥 FIX: Automatically select the first device profile on startup
        if self.profile_box.count() > 0:
            self._on_profile_selected(0)

    def _on_profile_selected(self, index):
        key = list(self.device_profiles.keys())[index]
        self.selected_profile = self.device_profiles[key]
    
    def append_log(self, text: str):
        self.log_box.append(text)
