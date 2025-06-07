# MyViewport.py

import importlib
import maya.utils
from maya import cmds, OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.mel as mel
import sys

# adjust this path as needed
sys.path.append('/Users/zophiekat/Github_Repositories/Blender_my_Maya')

# import & reload your Region module so edits take effect immediately
import user_interface.widget_classes.Bqt_Editor_Region as region_mod
importlib.reload(region_mod)
from user_interface.widget_classes.Bqt_Editor_Region import Bqt_Editor_Region

# Globals so we can tear down cleanly
_PANEL_NAME = None
_CTRL_NAME  = 'MyViewportControl'


def _cleanup():
    """Deferred teardown of old UI (modelPanel + workspaceControl)."""
    global _PANEL_NAME

    # delete the old modelPanel first
    if _PANEL_NAME and cmds.panel(_PANEL_NAME, exists=True):
        try:
            cmds.deleteUI(_PANEL_NAME, panel=True)
            print(f"[MyViewport] deleteUI panel {_PANEL_NAME}")
        except Exception as e:
            print(f"[MyViewport] failed to delete panel {_PANEL_NAME}: {e}")
        _PANEL_NAME = None

    # then close & delete the old workspaceControl
    if cmds.workspaceControl(_CTRL_NAME, q=True, exists=True):
        try:
            cmds.workspaceControl(_CTRL_NAME, e=True, close=True)
            print(f"[MyViewport] close workspaceControl {_CTRL_NAME}")
        except Exception as e:
            print(f"[MyViewport] failed to close {_CTRL_NAME}: {e}")
        if cmds.workspaceControl(_CTRL_NAME, q=True, exists=True):
            try:
                cmds.deleteUI(_CTRL_NAME, control=True)
                print(f"[MyViewport] deleteUI workspaceControl {_CTRL_NAME}")
            except Exception as e:
                print(f"[MyViewport] failed to deleteUI {_CTRL_NAME}: {e}")


def _real_show():
    """Build the UI: workspaceControl → paneLayout → modelPanel inside Main region."""
    global _PANEL_NAME

    # 1) Create the workspaceControl (transient)
    cmds.workspaceControl(
        _CTRL_NAME,
        label='Custom Viewport',
        initialWidth=512,
        initialHeight=512,
        retain=False
    )
    print(f"[MyViewport] created workspaceControl {_CTRL_NAME}")

    # 2) Create a paneLayout inside it
    pane = cmds.paneLayout(parent=_CTRL_NAME)
    print(f"[MyViewport] created paneLayout {pane}")

    # 3) Create the modelPanel under that paneLayout
    panel = cmds.modelPanel(parent=pane, menuBarVisible=False)
    _PANEL_NAME = panel
    print(f"[MyViewport] created modelPanel {panel}")

    # 4) Focus our panel so HUD ops target it
    try:
        mel.eval(f'setFocus {panel}')
        print(f"[MyViewport] set focus to panel {panel}")
    except Exception as e:
        print(f"[MyViewport] failed to set focus to {panel}: {e}")

    # 5) Remove any HUDs from our panel only
    for hud in (cmds.headsUpDisplay(listHeadsUpDisplays=True) or []):
        try:
            cmds.headsUpDisplay(hud, remove=True)
            print(f"[MyViewport] removed HUD: {hud}")
        except Exception as e:
            print(f"[MyViewport] failed to remove HUD {hud}: {e}")

    # 6) Wrap the paneLayout as our host QWidget
    panePtr = omui.MQtUtil.findControl(pane)
    host    = wrapInstance(int(panePtr), QtWidgets.QWidget)
    print(f"[MyViewport] wrapped host widget: {host}")

    # 7) Instantiate Regions as children of the paneLayout host
    #    host.main will become the container for the viewport
    T, B, L, R = 30, 30, 30, 30
    host.top    = Bqt_Editor_Region(host, 'top',    T, view_debug=True)
    host.bottom = Bqt_Editor_Region(host, 'bottom', B, view_debug=True)
    host.left   = Bqt_Editor_Region(host, 'left',   L, view_debug=True)
    host.right  = Bqt_Editor_Region(host, 'right',  R, view_debug=True)
    host.main   = Bqt_Editor_Region(host, 'main',   0, view_debug=True)
    print("[MyViewport] Regions instantiated")

    # 8) Wrap the modelPanel widget and re-parent it into host.main
    panelPtr   = omui.MQtUtil.findControl(panel)
    viewWidget = wrapInstance(int(panelPtr), QtWidgets.QWidget)
    # clear any old layout on main, then set a new one
    main_region = host.main
    # Create a layout to host the viewport
    main_region._layout = QtWidgets.QVBoxLayout(main_region)
    main_region._layout.setContentsMargins(0, 0, 0, 0)
    main_region._layout.addWidget(viewWidget)
    print(f"[MyViewport] embedded viewport in Main region: {main_region}")

def show():
    """
    Call this from Maya’s Script Editor.
    If an old control exists, defer its cleanup before building the new UI.
    Otherwise build immediately.
    """
    if cmds.workspaceControl(_CTRL_NAME, q=True, exists=True):
        maya.utils.executeDeferred(lambda: (_cleanup(), _real_show()))
    else:
        _real_show()

show()