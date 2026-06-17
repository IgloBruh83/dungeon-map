import os
import json
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLineEdit,
                               QPushButton, QListWidget, QListWidgetItem)
from PySide6.QtCore import Signal, Qt
from _widgets.subwindow import Subwindow
from config import Config as cfg

from _util.localization import Loc
_t = Loc.tr


class SpawnMenuWindow(Subwindow):
    # Сигнал, який передає шлях до вибраного файлу (або None, якщо зняли виділення)
    presetSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__("Spawn Entity", parent)
        self.presets_dir = "entities"

        # Створюємо папку, якщо її ще немає
        if not os.path.exists(self.presets_dir):
            os.makedirs(self.presets_dir)

        # --- UI Елементи ---
        top_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(_t("ui.misc.searchBar"))
        self.search_bar.setStyleSheet("background-color: #1a110a; color: #e0d2b4; border: 1px solid #000;")
        self.search_bar.textChanged.connect(self.filter_list)

        self.btn_refresh = QPushButton("↻")
        self.btn_refresh.setFixedSize(24, 24)
        self.btn_refresh.setStyleSheet("background-color: #5d4037; color: white; border: 1px solid #000;")
        self.btn_refresh.clicked.connect(self.refresh_list)

        top_layout.addWidget(self.search_bar)
        top_layout.addWidget(self.btn_refresh)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget { background-color: #2a211a; color: #e0d2b4; border: 1px solid #000; outline: none; }
            QListWidget::item:selected { background-color: #9e2a2b; }
        """)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)

        self.body_layout.addLayout(top_layout)
        self.body_layout.addWidget(self.list_widget)

        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        if not os.path.exists(self.presets_dir):
            return

        for filename in os.listdir(self.presets_dir):
            if filename.endswith(".json"):
                item = QListWidgetItem(filename.replace(".json", ""))
                item.setData(Qt.ItemDataRole.UserRole, os.path.join(self.presets_dir, filename))
                self.list_widget.addItem(item)

    def filter_list(self, text):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def on_selection_changed(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            file_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.presetSelected.emit(file_path)
        else:
            self.presetSelected.emit("")

    def closeEvent(self, event):
        self.list_widget.clearSelection()
        if hasattr(cfg, 'worldViewport') and cfg.worldViewport:
            cfg.worldViewport.btn_select_menu.setChecked(True)

        super().closeEvent(event)