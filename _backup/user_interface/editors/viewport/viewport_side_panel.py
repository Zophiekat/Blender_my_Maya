# viewport_side_panel.py

import sys
import os
import importlib
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance


import user_interface.widget_classes.Bqt_Panel_c as _bqt_mod
importlib.reload(_bqt_mod)
from user_interface.widget_classes.Bqt_Panel_c import Bqt_Panel



class FloatingSidePanel(QtWidgets.QWidget):
    """
    Frameless floating side panel pinned to the right edge
    of a Maya modelPanel. Contains collapsible Bqt_Panel sections.
    """
    def __init__(self, panelName=None, parent=None):
        # Determine parent (Maya main window) if none specified
        if parent is None:
            main_ptr = omui.MQtUtil.mainWindow()
            parent = wrapInstance(int(main_ptr), QtWidgets.QWidget) if main_ptr else None
        super(FloatingSidePanel, self).__init__(parent)

        # Window settings: frameless tool window, translucent
        flags = QtCore.Qt.FramelessWindowHint | QtCore.Qt.SubWindow | QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Main scroll area
        scroll = QtWidgets.QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        # Container for panels
        container = QtWidgets.QWidget()
        scroll.setWidget(container)

        # Layout for this widget
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Vertical layout for panels
        self.content_layout = QtWidgets.QVBoxLayout(container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(4)

        # Create and add Bqt_Panel sections
        self.transforms_panel = Bqt_Panel("Transforms", parent=container)
        self.custom_panel     = Bqt_Panel("Custom Attributes", parent=container)
        self.content_layout.addWidget(self.transforms_panel)
        self.content_layout.addWidget(self.custom_panel)
        self.content_layout.addStretch()

        # Determine which panel to attach to
        self.panel_name = panelName
        if not panelName:
            # fallback to first modelPanel in scene
            panels = cmds.getPanel(type='modelPanel') or []
            self.panel_name = panels[0] if panels else None

        # Wrap and install filter to track moves/resizes
        ptr = omui.MQtUtil.findLayout(self.panel_name) or omui.MQtUtil.findControl(self.panel_name)
        self.panel_widget = wrapInstance(int(ptr), QtWidgets.QWidget) if ptr else None
        if self.panel_widget:
            self.panel_widget.installEventFilter(self)
            self.updatePosition()

    def updatePosition(self):
        """Snap panel to the right edge of the modelPanel, matching height."""
        if not self.panel_widget:
            return
        rect = self.panel_widget.rect()
        top_right = self.panel_widget.mapToGlobal(rect.topRight())
        height = rect.height()
        width = self.width()
        x = top_right.x() - width
        y = top_right.y()
        self.setGeometry(x, y, width, height)

    def eventFilter(self, obj, event):
        # Re-anchor on panel move/resize
        if obj is self.panel_widget and event.type() in (QtCore.QEvent.Resize, QtCore.QEvent.Move):
            self.updatePosition()
        return super(FloatingSidePanel, self).eventFilter(obj, event)

# Entry point for external use
def run(panelName=None, ctrlName=None):
    """
    Instantiate or refresh the side panel.
    - If `panelName` is provided, attach directly to that modelPanel.
    - Else if `ctrlName` is provided, look for a modelPanel child under the workspaceControl.
    - Else fallback to the first modelPanel in the scene.
    """
    global floating_panel
    try:
        floating_panel.close()
        floating_panel.deleteLater()
    except:
        pass

    # Determine which panel to anchor to
    target_panel = None
    if panelName:
        target_panel = panelName
    elif ctrlName and cmds.workspaceControl(ctrlName, q=True, exists=True):
        children = cmds.paneLayout(ctrlName, q=True, childArray=True) or []
        for child in children:
            if cmds.modelPanel(child, exists=True):
                target_panel = child
                break
    if not target_panel:
        panels = cmds.getPanel(type='modelPanel') or []
        target_panel = panels[0] if panels else None

    # Instantiate anchored to target_panel
    floating_panel = FloatingSidePanel(panelName=target_panel)

if __name__ == '__main__':
    run()
