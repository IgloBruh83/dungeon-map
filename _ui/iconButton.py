from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton

class IconButton (QPushButton):
    def __init__(self, icon_path, tooltip="", size=36, icon_size=24):
        super().__init__()
        self.setFixedSize(size, size)
        icon = QIcon(icon_path)
        self.setIcon(icon)
        self.setIconSize(QSize(icon_size, icon_size))
        if tooltip != "":
            self.setToolTip(tooltip)

        self.qss = """
            QPushButton {
                /* Злегка висвітлена база: приємний горіхово-коричневий без зайвої рудості */
                background-color: #6d4c41;
                color: #e8dfca; /* Світлий пергаментний текст */

                font-family: 'Georgia', 'Times New Roman', serif;
                font-size: 13px;
                font-weight: bold;
                padding: 4px 12px;

                /* Блік став кремово-пастельним (без жовтизни), а тінь залишається глибокою шоколадною */
                border-top: 2px solid #857069;
                border-left: 2px solid #857069;
                border-right: 2px solid #301f1a;
                border-bottom: 2px solid #301f1a;

                border-radius: 0px; 
            }

            QPushButton:hover {
                /* Акуратний софт-ап при наведенні */
                background-color: #7d574c;
            }

            QPushButton:pressed, QPushButton:checked {
                /* Втиснутий стан стає темнішим */
                background-color: #5c3d36;
                color: #bcaaa4; /* Текст злегка приглушується в тон дерева */

                /* Інверсія рамок для 3D ефекту */
                border-top: 2px solid #301f1a;
                border-left: 2px solid #301f1a;
                border-right: 2px solid #857069;
                border-bottom: 2px solid #857069;

                /* Фізичний зсув контенту вглиб екрану */
                padding-top: 5px;
                padding-left: 13px;
                padding-bottom: 3px;
                padding-right: 11px;
            }
        """
        self.setStyleSheet(self.qss)

