from PySide6.QtWidgets import QGraphicsView, QPushButton, QMenu, QButtonGroup
from PySide6.QtGui import QPainter, QMouseEvent, QWheelEvent, QCursor
from PySide6.QtCore import Qt

from _enum.fraction import Fraction
from _pages.appPage import AppPage
from _ui.iconButton import IconButton
from _widgets.spawnMenuWindow import SpawnMenuWindow
from _widgets.damageToolWindow import DamageToolWindow
from config import Config as cfg
from _widgets.hoverTooltip import HoverTooltip

from _util.localization import Loc
_t = Loc.tr

class InteractiveViewport(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

        # Camera
        self.lastPanPoint = None
        self.zoomFactor = 1.05
        self.bypassMaxZoomOut = True
        self.scale(4, 4)

        # Render flags
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)

        # Scroll bars removal
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("border: none; background-color: #0d0906;")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.lastPanPoint = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.lastPanPoint:
            delta = event.pos() - self.lastPanPoint
            self.lastPanPoint = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.lastPanPoint = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        zoom_in_factor = self.zoomFactor
        zoom_out_factor = 1 / zoom_in_factor
        view_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        if self.scene():
            scene_rect = self.scene().sceneRect().adjusted(5, 5, -5, -5)
        else:
            scene_rect = view_rect
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            new_rect = view_rect.adjusted(
                -(view_rect.width() * (zoom_out_factor - 1)) / 2,
                -(view_rect.height() * (zoom_out_factor - 1)) / 2,
                +(view_rect.width() * (zoom_out_factor - 1)) / 2,
                +(view_rect.height() * (zoom_out_factor - 1)) / 2
            )
            if self.bypassMaxZoomOut or (self.scene() and scene_rect.contains(new_rect)):
                self.scale(zoom_out_factor, zoom_out_factor)
        event.accept()


class WorldPage(AppPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        cfg.worldViewport = self

        self.viewport = InteractiveViewport()

        self.viewport.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.viewport.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.viewport.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)

        self.viewport.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.viewport.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.viewport.setStyleSheet("border: none; background-color: #0d0906;")

        self.setBodyWidget(self.viewport)

        # --- BUTTONS ---

        self.btn_grid = IconButton("graphics/icons/toggle_grid.svg",
                                   tooltip=_t("ui.buttonTooltips.toggleGrid"))
        self.btn_grid.setCheckable(True)
        self.btn_grid.setChecked(True)

        self.btn_select_menu = IconButton("graphics/icons/hand.svg",
                                          tooltip=_t("ui.buttonTooltips.handTool"))
        self.btn_select_menu.setCheckable(True)
        self.btn_select_menu.setChecked(True)

        self.btn_spawn_menu = IconButton("graphics/icons/add_entity.svg",
                                         tooltip=_t("ui.buttonTooltips.spawnMenu"))
        self.btn_spawn_menu.setCheckable(True)

        self.btn_damage_menu = IconButton("graphics/icons/damage_tool.svg",
                                          tooltip=_t("ui.buttonTooltips.damageMenu"))
        self.btn_damage_menu.setCheckable(True)

        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        self.tool_group.addButton(self.btn_select_menu)
        self.tool_group.addButton(self.btn_spawn_menu)
        self.tool_group.addButton(self.btn_damage_menu)

        self.footer_layout.addWidget(self.btn_grid)
        self.footer_layout.addWidget(self.btn_select_menu)
        self.footer_layout.addWidget(self.btn_spawn_menu)
        self.footer_layout.addWidget(self.btn_damage_menu)
        self.footer_layout.addStretch()

        # --- SUBWINDOWS ---

        self.spawn_menu = SpawnMenuWindow(self)
        self.spawn_menu.hide()
        self.spawn_menu.move(20, 20)
        self.spawn_menu.presetSelected.connect(self.on_preset_selected)

        self.damage_window = DamageToolWindow(self)
        self.damage_window.hide()
        self.damage_window.move(20, 20)

        self.tool_group.buttonToggled.connect(self._on_tool_changed)
        self.btn_grid.toggled.connect(self._toggle_grid)

        # --- TOOLTIP ---
        self.tooltip = HoverTooltip(self)

    def _toggle_grid(self, checked):
        self.getLocation.grid.setVisible(checked)

    def _on_tool_changed(self, button, checked):
        if not checked:
            return

        self.spawn_menu.setVisible(self.btn_spawn_menu.isChecked())
        self.damage_window.setVisible(self.btn_damage_menu.isChecked())

        if not self.btn_spawn_menu.isChecked():
            self.spawn_menu.list_widget.clearSelection()
            if self.getLocation:
                self.getLocation.setActiveSpawnPreset("")

    def is_damage_tool_active(self):
        return self.btn_damage_menu.isChecked()

    def apply_damage_to_entity(self, entity_obj):
        amount = self.damage_window.spin_amount.value()
        if amount == 0:
            return
        dmg_type = self.damage_window.combo_type.currentData()

        cfg.net.sendEvent("REQ_ENTITY_DAMAGE", {
            "id": entity_obj.id,
            "amount": amount,
            "type": dmg_type.label
        })

    def showEntityTooltip(self, entity):

        name = entity.displayName if entity.displayName else entity.name
        _1 = entity.fraction.label
        _2 = entity.entityType.label
        info = f"{_t(f"enums.fraction.{_1}")}, {_t(f"enums.entityType.{_2}")}"
        health = entity.health
        max_health = entity.maxHealth
        perc = (health / max_health * 100) if max_health > 0 else 0

        if perc >= 85:
            h_text, color = "5", "#4caf50"
        elif perc >= 60:
            h_text, color = "4", "#8bc34a"
        elif perc >= 25:
            h_text, color = "3", "#ff9800"
        elif perc >= 10:
            h_text, color = "2", "#f44336"
        else:
            h_text, color = "1", "#b71c1c"

        if entity.fraction != Fraction.PARTY:
            health_html = f"<span style='color: {color}; font-weight: bold;'>{_t(f"entityUi.healthTips.{h_text}")}</span>"
        else:
            health_html = f"<span style='color: {color}; font-weight: bold;'>{health}/{max_health}</span>"

        self.tooltip.set_data(name, info, health_html)
        self.tooltip.show()
        self.moveTooltip()

    def showEntityContextMenu(self, screen_pos, selected_items):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu { 
                background-color: #2a211a; 
                color: #e0d2b4; 
                border: 1px solid #000; 
                padding: 4px; 
            }
            QMenu::item { padding: 4px 16px; }
            QMenu::item:selected { background-color: #9e2a2b; }
        """)

        mirror_action = menu.addAction(_t("ui.entityActions.mirror"))
        delete_action = menu.addAction(_t("ui.entityActions.delete"))

        action = menu.exec(screen_pos)

        if action == delete_action:
            for item in selected_items:
                if hasattr(item, 'obj'):
                    cfg.net.sendEvent("REQ_ENTITY_DELETE", {"id": item.obj.id})

        elif action == mirror_action:
            for item in selected_items:
                if hasattr(item, 'obj'):
                    cfg.net.sendEvent("REQ_ENTITY_FLIPX", {
                        "id": item.obj.id,
                        "flipX": not item.obj.flipX
                    })

    def moveTooltip(self):
        if self.tooltip.isVisible():
            local_pos = self.mapFromGlobal(QCursor.pos())
            self.tooltip.move(local_pos.x() + 15, local_pos.y() + 15)

    def hideTooltip(self):
        self.tooltip.hide()

    def on_preset_selected(self, file_path):
        if self.getLocation:
            self.getLocation.setActiveSpawnPreset(file_path)

    def setLocation(self, location_instance):
        if location_instance:
            self.viewport.setScene(location_instance)

    @property
    def getLocation(self):
        return self.viewport.scene()