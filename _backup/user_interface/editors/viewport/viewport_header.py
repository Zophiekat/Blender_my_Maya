## viewport_header.py

import sys
from PySide2 import QtWidgets, QtCore

class ViewportHeader(QtWidgets.QFrame):
    def __init__(self, panelName, parent=None):
        super().__init__(parent)
        self.panelName = panelName
        self.setObjectName("viewportHeader")

        # Window hints: frameless, no shadow, stay on top, child of parent
        flags = (
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.SubWindow |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.NoDropShadowWindowHint
        )
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        # Dummy button for testing
        btn = QtWidgets.QPushButton("HeaderButton")
        layout.addWidget(btn)
