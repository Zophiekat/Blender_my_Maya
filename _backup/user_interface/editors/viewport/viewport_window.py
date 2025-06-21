## viewport_window.py

import sys
from importlib import reload
import maya.utils
from maya import cmds, OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import importlib

# Ensure Maya can import your header and side-panel modules
sys.path.append('/Users/zophiekat/Github_Repositories/Blender_my_Maya')

# Reload side-panel module and class
import user_interface.editors.viewport.viewport_side_panel as vsp
importlib.reload(vsp)
FloatingSidePanel = vsp.FloatingSidePanel

# Reload header module and class
import user_interface.editors.viewport.viewport_header as vh
importlib.reload(vh)
ViewportHeader = vh.ViewportHeader

# Globals
_PANEL_NAME = None
_CTRL_NAME = 'MyViewportControl'


def _cleanup():
    global _PANEL_NAME
    print('[Viewport] Running cleanup')
    try:
        if _PANEL_NAME and cmds.panel(_PANEL_NAME, exists=True):
            cmds.deleteUI(_PANEL_NAME, panel=True)
            print(f'[Viewport] Deleted old panel {_PANEL_NAME}')
            _PANEL_NAME = None
        if cmds.workspaceControl(_CTRL_NAME, q=True, exists=True):
            cmds.deleteUI(_CTRL_NAME)
            print(f'[Viewport] Deleted workspaceControl {_CTRL_NAME}')
    except Exception as e:
        print(f'[Viewport] Exception during cleanup: {e}')


def _real_show():
    global _PANEL_NAME
    print('[Viewport] _real_show starting')
    _cleanup()

    # Create modelPanel inside a workspaceControl
    try:
        print('[Viewport] Creating modelPanel and workspaceControl')
        _PANEL_NAME = cmds.modelPanel(menuBarVisible=False)
        cmds.workspaceControl(_CTRL_NAME, label='My Viewport', retain=False)
        cmds.control(_PANEL_NAME, edit=True, parent=_CTRL_NAME)
        cmds.setFocus(_PANEL_NAME)
        print(f'[Viewport] modelPanel: {_PANEL_NAME} under workspaceControl: {_CTRL_NAME}')
    except Exception as e:
        print(f'[Viewport] Failed to create viewport window: {e}')
        return

    # Wrap the workspaceControl widget
    try:
        ptr_ctrl = omui.MQtUtil.findControl(_CTRL_NAME)
        host_widget = wrapInstance(int(ptr_ctrl), QtWidgets.QWidget)
        print(f'[Viewport] host_widget obtained: {host_widget}')
    except Exception as e:
        print(f'[Viewport] Failed to wrap workspaceControl: {e}')
        return

    # Helper to get host_widget global geometry
    def get_global_rect(widget):
        try:
            local_geo = widget.geometry()
            top_left = widget.mapToGlobal(QtCore.QPoint(0, 0))
            return QtCore.QRect(top_left.x(), top_left.y(), local_geo.width(), local_geo.height())
        except Exception:
            return QtCore.QRect(0, 0, 0, 0)

    # Create panels immediately
    _create_panels(host_widget, get_global_rect, host_widget.window())
    print('[Viewport] _real_show finished')


def _create_panels(host_widget, get_global_rect, main_window):
    print('[Viewport] _create_panels starting')
    try:
        rect = get_global_rect(host_widget)
        panel_w = 200
        header_h = 30

        # Instantiate side panel
        try:
            print('[Viewport] Instantiating side panel')
            side_panel = FloatingSidePanel(panelName=_PANEL_NAME, parent=main_window)
            print(f'[Viewport] side_panel created: {side_panel}')
        except Exception as e:
            print(f'[Viewport] Failed to create side_panel: {e}')
            return

        # Instantiate header panel
        try:
            print('[Viewport] Instantiating header panel')
            header_panel = ViewportHeader(panelName=_PANEL_NAME, parent=main_window)
            print(f'[Viewport] header_panel created: {header_panel}')
        except Exception as e:
            print(f'[Viewport] Failed to create header_panel: {e}')
            return

        # Common flags
        flags = (
            QtCore.Qt.Tool |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.NoDropShadowWindowHint
        )
        for panel in (header_panel, side_panel):
            try:
                panel.setWindowFlags(flags)
                panel.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
            except Exception as e:
                print(f'[Viewport] Error setting flags on panel {panel}: {e}')

        # Position header at top
        try:
            header_panel.setGeometry(
                rect.x(),
                rect.y(),
                rect.width(),
                header_h
            )
            side_panel.setGeometry(
                rect.x() + rect.width() - panel_w,
                rect.y() + header_h,
                panel_w,
                rect.height() - header_h
            )
        except Exception as e:
            print(f'[Viewport] Error setting initial geometry: {e}')

        header_panel.show()
        side_panel.show()
        print('[Viewport] Panels shown')

        # Watch main_window for move/resize
        class MainWatcher(QtCore.QObject):
            def __init__(self, host, side, header, side_w, header_h):
                super(MainWatcher, self).__init__(main_window)
                self.host = host
                self.side = side
                self.header = header
                self.side_w = side_w
                self.header_h = header_h

            def eventFilter(self, obj, event):
                if obj is main_window and event.type() in (QtCore.QEvent.Move, QtCore.QEvent.Resize):
                    try:
                        r = get_global_rect(self.host)
                        # Update header at top
                        self.header.setGeometry(
                            r.x(),
                            r.y(),
                            r.width(),
                            self.header_h
                        )
                        # Update side panel below header
                        self.side.setGeometry(
                            r.x() + r.width() - self.side_w,
                            r.y() + self.header_h,
                            self.side_w,
                            r.height() - self.header_h
                        )
                    except Exception as e:
                        print(f'[Viewport] Exception in MainWatcher eventFilter: {e}')
                return super(MainWatcher, self).eventFilter(obj, event)

        watcher = MainWatcher(host_widget, side_panel, header_panel, panel_w, header_h)
        main_window.installEventFilter(watcher)
        main_window._watcher = watcher
        print('[Viewport] _create_panels finished')
    except Exception as e:
        print(f'[Viewport] Unexpected exception in _create_panels: {e}')

# Defer execution until Maya UI is ready
maya.utils.executeDeferred(_real_show)
