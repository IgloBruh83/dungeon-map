from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent

class Subwindow(QWidget):
    def __init__(self, title: str = "Subwindow", parent: QWidget = None):
        super().__init__(parent)

        self.resize(300, 250)
        self.setMinimumSize(200, 150)

        self._is_dragging = False
        self._drag_position = QPoint()

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setStyleSheet("""
                    Subwindow {
                        background-color: #3d2b1f;
                        border-radius: 2px;
                    }
                """)

        # --- Title Bar ---
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(30)
        self.title_bar.setObjectName("TitleBar")

        self.title_layout = QHBoxLayout(self.title_bar)
        self.title_layout.setContentsMargins(10, 0, 5, 0)
        self.title_layout.setSpacing(10)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
                    QLabel {
                        background-color: transparent;
                        font-size: 12px;
                        padding-left: 2px;
                    }
                """)

        self.title_bar.setStyleSheet("""
                    QFrame#TitleBar {
                        background-color: #2a211a; 
                        border-top: 3px solid #000000;
                        border-left: 3px solid #000000;
                        border-right: 3px solid #000000;
                        border-bottom: none;
                    }
                """)
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()

        self.btn_close = QPushButton("×")
        self.btn_close.setFixedSize(22, 22)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #5d4037;
                color: #e0d2b4;
                border: 1px solid #1a110a;
                border-radius: 2px;
                font-size: 14px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #9e2a2b; /* Червонуватий відтінок при наведенні */
                border-color: #c5a059;
            }
            QPushButton:pressed {
                background-color: #3e2723;
            }
        """)
        self.btn_close.clicked.connect(self.close)
        self.title_layout.addWidget(self.btn_close)

        # --- Body ---
        self.body_frame = QFrame()
        self.body_frame.setObjectName("BodyFrame")
        self.body_frame.setStyleSheet("""
                    QFrame#BodyFrame {
                        background-color: #3d2b1f; 
                        border-bottom: 3px solid #000000;
                        border-left: 3px solid #000000;
                        border-right: 3px solid #000000;
                        border-top: none;
                    }
                """)

        self.body_layout = QVBoxLayout(self.body_frame)
        self.body_layout.setContentsMargins(10, 10, 10, 10)

        self.main_layout.addWidget(self.title_bar)
        self.main_layout.addWidget(self.body_frame, stretch=1)

        self.title_bar.mousePressEvent = self._title_press_event
        self.title_bar.mouseMoveEvent = self._title_move_event
        self.title_bar.mouseReleaseEvent = self._title_release_event

    def mousePressEvent(self, event: QMouseEvent):
        self.raise_()
        super().mousePressEvent(event)

    def _title_press_event(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.raise_()
            self._is_dragging = True
            self._drag_position = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def _title_move_event(self, event: QMouseEvent):
        if self._is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def _title_release_event(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            event.accept()