from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from config import Config as cfg

class Grid (QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.grid_size = cfg.gridSize
        self.pen = QPen(QColor(*cfg.gridColor))
        self.pen.setWidthF(cfg.gridThickness)
        self.pen.setCosmetic(True)
        self.setZValue(cfg.zGrid)

    def boundingRect(self):
        if self.scene():
            return self.scene().sceneRect()
        return QRectF(0, 0, 1000, 1000)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None):
        rect = self.boundingRect()
        left = int(rect.left())
        top = int(rect.top())
        right = int(rect.right())
        bottom = int(rect.bottom())
        painter.setPen(self.pen)
        # Vertical lines
        x = left - (left % self.grid_size)
        while x <= right:
            painter.drawLine(x, top, x, bottom)
            x += self.grid_size
        # Horizontal lines
        y = top - (top % self.grid_size)
        while y <= bottom:
            painter.drawLine(left, y, right, y)
            y += self.grid_size