from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QTextEdit, QComboBox
)

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

        # Scan
        self.scan_button = QPushButton("Scan")
        layout.addWidget(self.scan_button)

        # Connect
        self.connect_button = QPushButton("Connect")
        layout.addWidget(self.connect_button)

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
