from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class RealClock (QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 15, 0)
        self.layout.setSpacing(0)

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(
            "color: #c5a059; font-size: 13px; font-weight: bold; background: transparent; margin-top: 5px;"
        )
        self.layout.addWidget(self.time_label)

        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet(
            "color: #8d6e63; font-size: 11px; background: transparent; margin-top: -5px;"
        )
        self.layout.addWidget(self.date_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("HH:mm"))
        self.date_label.setText(now.toString("dd.MM.yyyy"))