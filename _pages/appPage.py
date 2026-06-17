from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout

class AppPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.body_widget = None

        self.footer = QFrame()
        self.footer.setFixedHeight(45)
        self.footer.setStyleSheet("background-color: #3d2b1f; border: none;")

        self.footer_layout = QHBoxLayout(self.footer)
        self.footer_layout.setContentsMargins(10, 0, 10, 0)
        self.footer_layout.setSpacing(10)

        self.main_layout.addWidget(self.footer)

    def setBodyWidget(self, widget: QWidget):
        if self.body_widget is not None:
            self.main_layout.removeWidget(self.body_widget)
            self.body_widget.deleteLater()
        self.body_widget = widget
        self.main_layout.insertWidget(0, self.body_widget)