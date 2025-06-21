# Bqt_Editor_Region.py

from PySide2 import QtWidgets, QtCore

class Bqt_Editor_Region(QtWidgets.QGroupBox):
    """
    A transparent, click-through overlay region implemented as a child QGroupBox.
    When the host widget is closed or destroyed, these children go away automatically.
    """

    def __init__(self, host, side, thickness, view_debug=False):
        # parent it to the host (paneLayout widget)
        super(Bqt_Editor_Region, self).__init__(host)
        self.host       = host
        self.side       = side
        self.thickness  = thickness
        self.view_debug = view_debug

        # no title, flat look
        self.setTitle("")
        self.setFlat(True)

        # click-through
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

        # debug coloring or fully transparent
        style = self._debug_styles()[side] if view_debug else "background: transparent;"
        self.setStyleSheet(style)
        print(f"[Region __init__] side={side!r}, thickness={thickness}, view_debug={view_debug}")
        print(f"[Region __init__] applied stylesheet for {side}: {style}")

        # watch host resizes/moves
        host.installEventFilter(self)

        # initial layout & show
        self.update_geometry()
        self.show()

    def eventFilter(self, obj, event):
        if obj is self.host and event.type() in (QtCore.QEvent.Resize, QtCore.QEvent.Move):
            self.update_geometry()
        return super(Bqt_Editor_Region, self).eventFilter(obj, event)

    def update_geometry(self):
        pw = self.host.width()
        ph = self.host.height()

        if self.side == 'top':
            x, y, w, h = 0, 0, pw, self.thickness
        elif self.side == 'bottom':
            x, y, w, h = 0, ph - self.thickness, pw, self.thickness
        elif self.side == 'left':
            top_ = getattr(self.host, 'top', None)
            bot_ = getattr(self.host, 'bottom', None)
            y0   = top_.thickness if top_ else 0
            h0   = ph - y0 - (bot_.thickness if bot_ else 0)
            x, y, w, h = 0, y0, self.thickness, h0
        elif self.side == 'right':
            top_ = getattr(self.host, 'top', None)
            bot_ = getattr(self.host, 'bottom', None)
            y0   = top_.thickness if top_ else 0
            h0   = ph - y0 - (bot_.thickness if bot_ else 0)
            x, y, w, h = pw - self.thickness, y0, self.thickness, h0
        elif self.side == 'main':
            top_ = getattr(self.host, 'top', None)
            bot_ = getattr(self.host, 'bottom', None)
            y0   = top_.thickness if top_ else 0
            h0   = ph - y0 - (bot_.thickness if bot_ else 0)
            x, y, w, h = 0, y0, pw, h0
        else:
            return

        # place relative to host
        self.setGeometry(x, y, w, h)
        # ensure it stays above the viewport
        self.raise_()

    def _debug_styles(self):
        return {
            'top':    "background-color: rgba(0,255,0,25); border:1px solid rgba(0,255,0,255);",
            'bottom': "background-color: rgba(255,255,255,25); border:1px solid rgba(255,255,255,255);",
            'left':   "background-color: rgba(0,0,255,25); border:1px solid rgba(0,0,255,255);",
            'right':  "background-color: rgba(255,0,0,25); border:1px solid rgba(255,0,0,255);",
            'main':   "background-color: rgba(255,255,0,25); border:1px solid rgba(255,255,0,255);",
        }
