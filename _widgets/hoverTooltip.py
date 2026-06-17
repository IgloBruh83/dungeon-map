from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class HoverTooltip(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.setStyleSheet("""
            HoverTooltip {
                background-color: #2a211a;
                border: 2px solid #000000;
                border-radius: 4px;
            }
            QLabel {
                color: #e0d2b4;
                background-color: transparent;
                font-family: sans-serif;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 8, 10, 8)
        self.layout.setSpacing(4)

        self.lbl_name = QLabel()
        self.lbl_name.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;")

        self.lbl_info = QLabel()
        self.lbl_info.setStyleSheet("font-size: 11px; color: #a3947c; font-style: italic; margin-top: -3px;")

        self.lbl_health = QLabel()
        self.lbl_health.setStyleSheet("font-size: 12px;")

        self.layout.addWidget(self.lbl_name)
        self.layout.addWidget(self.lbl_info)
        self.layout.addWidget(self.lbl_health)

        self.hide()

    def set_data(self, name: str, info: str, health_html: str):
        self.lbl_name.setText(name)
        self.lbl_info.setText(info)
        self.lbl_health.setText(health_html)
        self.adjustSize()