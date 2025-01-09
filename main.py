import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QSpinBox, QHBoxLayout
)
from PyQt5.QtCore import QTimer
import psutil
import sqlite3

class SystemMonitorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.update_interval = 1000
        self.is_recording = False
        self.start_time = None

        # Database setup
        self.conn = sqlite3.connect("system_usage.db")
        self.cursor = self.conn.cursor()
        self.create_table()

        self.init_ui()


    def init_ui(self):
        self.setWindowTitle("System Monitor")
        self.setGeometry(100, 100, 400, 200)


        self.layout = QVBoxLayout()

        self.cpu_label = QLabel("CPU Usage: 0%")
        self.ram_label = QLabel("RAM Usage: 0%")
        self.disk_label = QLabel("Disk Usage: 0%")
        self.layout.addWidget(self.cpu_label)
        self.layout.addWidget(self.ram_label)
        self.layout.addWidget(self.disk_label)
        self.interval_label = QLabel("Update Interval (ms):")
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(100, 10000)
        self.interval_spinbox.setValue(1000)
        self.interval_spinbox.valueChanged.connect(self.set_update_interval)
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(self.interval_label)
        interval_layout.addWidget(self.interval_spinbox)
        self.layout.addLayout(interval_layout)
        self.start_button = QPushButton("Start Recording")
        self.start_button.clicked.connect(self.start_recording)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setVisible(False)
        self.layout.addWidget(self.stop_button)

        self.timer_label = QLabel("Recording Time: 0s")
        self.timer_label.setVisible(False)
        self.layout.addWidget(self.timer_label)

        self.setLayout(self.layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(self.update_interval)

    def set_update_interval(self, value):
        self.update_interval = value
        self.timer.setInterval(self.update_interval)

    def update_metrics(self):
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        self.cpu_label.setText(f"CPU Usage: {cpu_usage}%")
        self.ram_label.setText(f"RAM Usage: {ram_usage}%")
        self.disk_label.setText(f"Disk Usage: {disk_usage}%")

        if self.is_recording:
            self.record_metrics(cpu_usage, ram_usage, disk_usage)
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.setText(f"Recording Time: {elapsed_time}s")

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_usage (
                timestamp INTEGER,
                cpu_usage REAL,
                ram_usage REAL,
                disk_usage REAL
            )
        """)
        self.conn.commit()

    def record_metrics(self, cpu, ram, disk):
        timestamp = int(time.time())
        self.cursor.execute("INSERT INTO system_usage (timestamp, cpu_usage, ram_usage, disk_usage) VALUES (?, ?, ?, ?)",
                            (timestamp, cpu, ram, disk))
        self.conn.commit()

    def start_recording(self):
        self.is_recording = True
        self.start_time = time.time()
        self.start_button.setVisible(False)
        self.stop_button.setVisible(True)
        self.timer_label.setVisible(True)

    def stop_recording(self):
        self.is_recording = False
        self.start_time = None
        self.start_button.setVisible(True)
        self.stop_button.setVisible(False)
        self.timer_label.setVisible(False)
        self.timer_label.setText("Recording Time: 0s")

    def closeEvent(self, event):
        self.conn.close()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemMonitorApp()
    window.show()
    sys.exit(app.exec_())
