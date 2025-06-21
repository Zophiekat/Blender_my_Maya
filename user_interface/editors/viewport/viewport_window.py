## viewport_window.py

import sys
import maya.utils
from maya import cmds, OpenMayaUI as omui
from maya.OpenMayaUI import MUiMessage
from OpenGL import GL
from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
import importlib

# Path setup for custom modules
sys.path.append('/Users/zophiekat/Github_Repositories/Blender_my_Maya')

# Reload and import side-panel and header modules
import user_interface.editors.viewport.viewport_side_panel as vsp
importlib.reload(vsp)
FloatingSidePanel = vsp.FloatingSidePanel

import user_interface.editors.viewport.viewport_header as vh
importlib.reload(vh)
ViewportHeader = vh.ViewportHeader

# Globals
_PANEL_NAME = None
_CTRL_NAME = 'MyViewportControl'
_mask_callback_id = None

# Render widget offscreen to QImage
def render_widget_to_image(widget):
    widget.resize(widget.sizeHint())
    image = QtGui.QImage(widget.size(), QtGui.QImage.Format_RGBA8888)
    image.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(image)
    widget.render(painter)
    painter.end()
    return image

# Convert QImage to OpenGL Texture
def qimage_to_gl_texture(qimage):
    qimage = qimage.convertToFormat(QtGui.QImage.Format_RGBA8888)
    width, height = qimage.width(), qimage.height()
    ptr = qimage.bits()
    ptr.setsize(qimage.byteCount())
    img_data = ptr.asarray()
    texture = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, width, height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, img_data)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    return texture, width, height

# Draw texture in viewport
def draw_texture_in_viewport(texture_id, width, height, x, y):
    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glBegin(GL.GL_QUADS)
    GL.glTexCoord2f(0.0, 1.0); GL.glVertex2f(x, y)
    GL.glTexCoord2f(1.0, 1.0); GL.glVertex2f(x + width, y)
    GL.glTexCoord2f(1.0, 0.0); GL.glVertex2f(x + width, y + height)
    GL.glTexCoord2f(0.0, 0.0); GL.glVertex2f(x, y + height)
    GL.glEnd()
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    GL.glDisable(GL.GL_TEXTURE_2D)
    GL.glDisable(GL.GL_BLEND)

# Cleanup previous resources
def _cleanup():
    global _PANEL_NAME, _mask_callback_id
    if _mask_callback_id:
        try:
            MUiMessage.removeCallback(_mask_callback_id)
        except:
            pass
        _mask_callback_id = None
    if _PANEL_NAME and cmds.panel(_PANEL_NAME, exists=True):
        cmds.deleteUI(_PANEL_NAME, panel=True)
        _PANEL_NAME = None
    if cmds.workspaceControl(_CTRL_NAME, q=True, exists=True):
        cmds.deleteUI(_CTRL_NAME)

# Main OpenGL draw callback
def _mask_callback(view, clientData):
    view.beginGL()
    vw, vh = view.portWidth(), view.portHeight()

    # Header widget rendering
    header_widget = ViewportHeader(panelName=_PANEL_NAME)
    header_img = render_widget_to_image(header_widget)
    header_tex, header_w, header_h = qimage_to_gl_texture(header_img)

    # Side widget rendering
    side_widget = FloatingSidePanel(panelName=_PANEL_NAME)
    side_img = render_widget_to_image(side_widget)
    side_tex, side_w, side_h = qimage_to_gl_texture(side_img)

    # Drawing textures
    draw_texture_in_viewport(header_tex, header_w, header_h, 0, vh - header_h)
    draw_texture_in_viewport(side_tex, side_w, side_h, vw - side_w, 0)

    view.endGL()

def _install_mask():
    global _mask_callback_id, _PANEL_NAME
    view = omui.M3dView()
    omui.M3dView.getM3dViewFromModelPanel(_PANEL_NAME, view)
    _mask_callback_id = MUiMessage.add3dViewPostRenderMsgCallback(view, _mask_callback, None)

# Setup workspace control and viewport
def _real_show():
    global _PANEL_NAME
    _cleanup()
    _PANEL_NAME = cmds.modelPanel(menuBarVisible=False)
    cmds.workspaceControl(_CTRL_NAME, label='My Viewport', retain=False)
    cmds.control(_PANEL_NAME, edit=True, parent=_CTRL_NAME)
    cmds.setFocus(_PANEL_NAME)
    _install_mask()

# Run when Maya UI is ready
maya.utils.executeDeferred(_real_show)
