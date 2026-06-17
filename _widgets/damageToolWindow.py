from PySide6.QtWidgets import QVBoxLayout, QLabel, QSpinBox, QComboBox
from PySide6.QtCore import Qt
from _widgets.subwindow import Subwindow
from _enum.damageType import DamageType
from config import Config as cfg


class DamageToolWindow(Subwindow):
    def __init__(self, parent=None):
        super().__init__("Damage / Healing", parent)
        self.resize(250, 150)

        self.spin_amount = QSpinBox()
        self.spin_amount.setRange(-999, 999)
        self.spin_amount.setValue(0)
        self.spin_amount.setStyleSheet("background-color: #2a211a; color: #e0d2b4; min-height: 20px; padding: 8px;")

        self.combo_type = QComboBox()
        self.combo_type.setStyleSheet("background-color: #2a211a; color: #e0d2b4; min-height: 20px; padding: 8px;")

        self.body_layout.addWidget(self.spin_amount)
        self.body_layout.addWidget(self.combo_type)
        self.body_layout.addStretch()

        self.spin_amount.valueChanged.connect(self._on_value_changed)

        self._on_value_changed(0)

    def _on_value_changed(self, value):
        current_data = self.combo_type.currentData()

        self.combo_type.clear()

        if value < 0:
            self.combo_type.addItem(DamageType.TRUE.label, DamageType.TRUE)
        else:
            for dt in DamageType:
                self.combo_type.addItem(dt.label, dt)

            idx = self.combo_type.findData(current_data)
            if idx >= 0:
                self.combo_type.setCurrentIndex(idx)

    def closeEvent(self, event):
        if hasattr(cfg, 'worldViewport') and cfg.worldViewport:
            cfg.worldViewport.btn_select_menu.setChecked(True)

        super().closeEvent(event)