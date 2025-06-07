from maya import cmds
from maya import OpenMayaUI as omui
from maya.app.general import mayaMixin
from PySide2 import QtWidgets
import shiboken2

class ViewportWindow(mayaMixin.MayaQWidgetDockableMixin, QtWidgets.QWidget):
    """Simple window that embeds a Maya 3D viewport."""

    def __init__(self, parent=None):
        super(ViewportWindow, self).__init__(parent=parent)
        self.setWindowTitle("PySide2 Viewport Example")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        panel_name = cmds.modelPanel(menuBarVisible=False)
        ptr = omui.MQtUtil.findControl(panel_name)
        if ptr:
            widget = shiboken2.wrapInstance(int(ptr), QtWidgets.QWidget)
            layout.addWidget(widget)
        else:
            label = QtWidgets.QLabel("Could not create modelPanel")
            layout.addWidget(label)


def show():
    """Utility function to display the viewport window."""
    global _window
    try:
        _window.close()
        _window.deleteLater()
    except Exception:
        pass
    _window = ViewportWindow()
    _window.show(dockable=True)
