import os

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from _models.entity import Entity
from _util.vector2 import Vector2
from config import Config as cfg


class EntityInstance (QGraphicsObject):
    def __init__(self, obj: Entity):
        super().__init__(parent=None)
        self.obj = obj

        self.pixmap = QPixmap(64, 64)
        self.basicScale = obj.size.cell_size / max(self.pixmap.width(), 1)
        self._cached_shape = self._generate_precise_shape()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(10)

        self.targetPos = Vector2(self.obj.x, self.obj.y)

        # --- Логіка мережевого перетягування ---
        self.is_dragging = False

        self.move_timer = QTimer(self)
        self.move_timer.setInterval(200)
        self.move_timer.timeout.connect(self._send_move_tick)

        # --- Логіка інтерполяції ---
        self.lerp_timer = QTimer(self)
        self.lerp_timer.setInterval(1000 // cfg.unitLerpFreq)
        self.lerp_timer.timeout.connect(self._process_lerp)

        self._is_hovered = False

    def updateVisual(self):
        self.prepareGeometryChange()
        obj = self.obj
        self.pixmap =  QPixmap(obj.spriteUrl)
        if obj.flipX:
            self.pixmap = self.pixmap.transformed(QTransform().scale(-1, 1))
        self.basicScale = obj.size.cell_size / max(self.pixmap.width(), 1)
        self._cached_shape = self._generate_precise_shape()
        self.setScale(self.basicScale * obj.scale)
        self.setPos(obj.x, obj.y)
        self.setRotation(obj.rotation)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, obj.movable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, obj.movable)

    def boundingRect(self) -> QRectF:
        return QRectF(
            -self.pixmap.width() / 2,
            -self.pixmap.height() / 2,
            self.pixmap.width(),
            self.pixmap.height()
        )

    def paint(self, painter: QPainter, option, widget=None):
        if self._is_hovered:
            color = QColor(self.obj.fraction.color)

            pen = QPen(color)
            pen.setCosmetic(True)
            pen.setWidth(2)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            painter.drawPath(self._cached_shape)
        painter.drawPixmap(
            int(-self.pixmap.width() / 2),
            int(-self.pixmap.height() / 2),
            self.pixmap
        )

    def _generate_precise_shape(self) -> QPainterPath:
        mask = self.pixmap.mask()
        region = QRegion(mask)
        path = QPainterPath()
        for rect in region:
            path.addRect(QRectF(rect))
        offset_transform = QTransform().translate(
            -self.pixmap.width() / 2,
            -self.pixmap.height() / 2
        )
        return offset_transform.map(path)

    def shape(self) -> QPainterPath:
        return self._cached_shape

    def _send_move_tick(self):
        self.obj.x = self.pos().x()
        self.obj.y = self.pos().y()
        cfg.net.sendEvent("REQ_ENTITY_MOVE",
                          {"id": self.obj.id,
                           "pos": [self.pos().x(), self.pos().y()]})

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if hasattr(cfg, 'worldViewport') and cfg.worldViewport.is_damage_tool_active():
                cfg.worldViewport.apply_damage_to_entity(self.obj)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        super().mouseMoveEvent(event)

        if self.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsMovable:
            if not self.is_dragging:
                self.is_dragging = True
                self.lerp_timer.stop()
                self.move_timer.start()
                self._send_move_tick()
                # --- ВИМИКАЄМО ХОВЕР НА ЧАС ДРАГУ ---
                self._is_hovered = False
                self.update()
                if hasattr(cfg, 'worldViewport') and cfg.worldViewport:
                    cfg.worldViewport.hideTooltip()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_dragging:
                self.is_dragging = False
                self.move_timer.stop()
                self.obj.x = self.pos().x()
                self.obj.y = self.pos().y()
                cfg.net.sendEvent("REQ_ENTITY_MOVE_END",
                                  {"id": self.obj.id,
                                   "pos": [self.pos().x(), self.pos().y()]})
                # --- ПОВЕРТАЄМО ХОВЕР, ЯКЩО МИШКА ВСЕ ЩЕ ТУТ ---
                if self.isUnderMouse():
                    self._is_hovered = True
                    self.update()
                    if hasattr(cfg, 'worldViewport') and cfg.worldViewport:
                        cfg.worldViewport.showEntityTooltip(self.obj)

    def updatePosition(self):
        self.targetPos = Vector2(self.obj.x, self.obj.y)
        if not self.is_dragging and not self.lerp_timer.isActive():
            self.lerp_timer.start()

    def _process_lerp(self):
        current_pos = Vector2(self.pos().x(), self.pos().y())

        if current_pos.checkConvergence(self.targetPos):
            self.setPos(self.targetPos.x, self.targetPos.y)
            self.lerp_timer.stop()
            return
        new_pos = current_pos.lerp(self.targetPos, cfg.unitLerpFactor)
        self.setPos(new_pos.x, new_pos.y)

    def forceDrop(self, true_x: float, true_y: float):
        self.is_dragging = False
        self.move_timer.stop()
        self.lerp_timer.stop()
        self.ungrabMouse()
        self.clearFocus()
        self.setPos(true_x, true_y)
        self.obj.x = true_x
        self.obj.y = true_y

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        super().hoverEnterEvent(event)
        if self.is_dragging: return
        self._is_hovered = True
        self.update()
        if hasattr(cfg, 'worldViewport') and cfg.worldViewport:
            cfg.worldViewport.showEntityTooltip(self.obj)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent):
        super().hoverMoveEvent(event)
        if self.is_dragging: return
        if hasattr(cfg, 'worldViewport') and cfg.worldViewport:
            cfg.worldViewport.moveTooltip()

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        super().hoverLeaveEvent(event)
        if self.is_dragging: return
        self._is_hovered = False
        self.update()
        if hasattr(cfg, 'worldViewport') and cfg.worldViewport:
            cfg.worldViewport.hideTooltip()

    def contextMenuEvent(self, event: QGraphicsSceneContextMenuEvent):
        if not self.isSelected():
            self.scene().clearSelection()
            self.setSelected(True)

        if hasattr(cfg, 'worldViewport') and cfg.worldViewport:
            cfg.worldViewport.showEntityContextMenu(
                event.screenPos(),
                self.scene().selectedItems()
            )