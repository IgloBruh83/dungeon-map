from PySide6.QtWidgets import QFrame


class Separator (QFrame):
    def __init__(self, direction="V"):
        super().__init__(parent=None)
        self.setFrameShape(QFrame.Shape.VLine if direction == "V" else QFrame.Shape.HLine)