import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QTransform

from _models.location import Location
from _models.entity import Entity
from _submodels.entityInstance import EntityInstance
from _util.grid import Grid
from config import Config as cfg


class LocationInstance(QGraphicsScene):
    def __init__(self, obj: Location):
        super().__init__(parent=None)
        self.obj = obj

        self.setSceneRect(0, 0, self.obj.dim_x, self.obj.dim_y)

        self.bg = QGraphicsPixmapItem()
        self.bg.setPos(0, 0)
        self.bg.setZValue(-50)
        self.addItem(self.bg)
        self.updateBgGraphics()

        self.grid = Grid()
        self.grid.setZValue(-49)
        self.addItem(self.grid)

        self.entityInstances = {}
        self.updateInstances()

        # --- ЛОГІКА ФАНТОМА СПАВНУ ---
        self.active_spawn_preset_path = ""
        self.active_spawn_data = None

        self.phantom = QGraphicsPixmapItem()
        self.phantom.setOpacity(0.5)  # Напівпрозорий
        self.phantom.setZValue(100)  # Поверх усього
        self.phantom.hide()
        self.addItem(self.phantom)

    def setActiveSpawnPreset(self, file_path: str):
        self.active_spawn_preset_path = file_path

        if not file_path:
            self.phantom.hide()
            self.active_spawn_data = None
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.active_spawn_data = json.load(file)
            dummy_entity = Entity.load(self.active_spawn_data, self.obj, lambda: -1)
            pixmap = QPixmap(dummy_entity.spriteUrl)
            basic_scale = dummy_entity.size.cell_size / max(pixmap.width(), 1)

            self.phantom.setPixmap(pixmap)
            self.phantom.setScale(basic_scale * dummy_entity.scale)

            self.phantom.setOffset(-pixmap.width() / 2, -pixmap.height() / 2)
            self.phantom.show()

        except Exception as e:
            print(f"[Помилка] Не вдалося завантажити пресет для фантома: {e}")
            self.phantom.hide()

    def updateBgGraphics(self):
        if not self.obj.map_bg:
            return
        pixmap_path = f"graphics/maps/{self.obj.map_bg}"
        pixmap = QPixmap(pixmap_path)
        self.bg.setPixmap(pixmap)

        if pixmap.width() > 0 and pixmap.height() > 0:
            scale_x = self.width() / pixmap.width()
            scale_y = self.height() / pixmap.height()
            self.bg.setTransform(QTransform().scale(scale_x, scale_y))

    def updateInstances(self):
        for ent_id, entity in self.obj.entities.items():
            if ent_id not in self.entityInstances:
                self._addEntityInstance(entity)
            else:
                self.entityInstances[ent_id].updateVisual()
        for ent_id in list(self.entityInstances.keys()):
            if ent_id not in self.obj.entities:
                self._removeEntityInstance(ent_id)

    def _addEntityInstance(self, entity: Entity):
        _ = EntityInstance(entity)
        self.addItem(_)
        self.entityInstances[entity.id] = _
        _.updateVisual()

    def _removeEntityInstance(self, entity_id: int):
        _ = self.entityInstances.pop(entity_id, None)
        if _ is not None:
            self.removeItem(_)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        if self.phantom.isVisible():
            self.phantom.setPos(event.scenePos())

    def mousePressEvent(self, event):
        if self.phantom.isVisible() and event.button() == Qt.MouseButton.LeftButton:
            spawn_x = event.scenePos().x()
            spawn_y = event.scenePos().y()

            payload = self.active_spawn_data.copy()
            payload["transform"]["pos"] = [spawn_x, spawn_y]

            cfg.net.sendEvent("REQ_ENTITY_ADD", payload)
            event.accept()
            return

        super().mousePressEvent(event)