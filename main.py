import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from _networking.networkExecutor import NetworkExecutor
from _networking.networkManager import NetworkManager
from _pages.appPage import AppPage
from _pages.worldPage import WorldPage
from _util.localization import Loc
from _widgets.realClock import RealClock
from _widgets.subwindow import Subwindow

from config import Config as cfg

Loc.load('en_US')
_t = Loc.tr


class Main (QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.tab_bar = QFrame()
        self.tab_bar.setFixedHeight(40)
        self.tab_bar.setStyleSheet("background-color: #3d2b1f;")

        self.tab_layout = QHBoxLayout(self.tab_bar)
        self.btn_tab1 = QPushButton(_t("ui.tabs.tabletop"))
        self.tab_layout.addWidget(self.btn_tab1)
        self.tab_layout.setContentsMargins(10, 0, 10, 0)

        tab_button_style = """
            QPushButton {
        background-color: #5d4037;
        color: #e0d2b4;
        border: 2px solid #2b1d0e;
        border-radius: 2px;
        padding: 4px 20px;
        font-size: 14px;
        font-family: 'Georgia', serif;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #795548;
        border-color: #c5a059;
    }
    QPushButton:pressed {
        background-color: #3e2723;
        color: #c5a059;
    }
        """

        self.btn_tab1.setStyleSheet(tab_button_style)

        self.tab_layout.addStretch()

        self.clock = RealClock()
        self.tab_layout.addWidget(self.clock)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #1a110a;")

        self.stacked_widget.addWidget(WorldPage())

        self.main_layout.addWidget(self.tab_bar)
        self.main_layout.addWidget(self.stacked_widget)

        self.btn_tab1.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()

    network_manager = NetworkManager(cfg.server)
    network_executor = NetworkExecutor()
    cfg.net = network_executor

    network_manager.packageReceived.connect(network_executor.onRecievedEvent)
    network_manager.connected.connect(network_executor.onConnected)
    network_manager.connectionLost.connect(network_executor.onLostConnection)
    network_executor.sendRequest.connect(network_manager.sendPackage_slot)
    app.aboutToQuit.connect(network_manager.stop)

    app.network_manager = network_manager
    app.network_executor = network_executor

    network_manager.run()

    sys.exit(app.exec())