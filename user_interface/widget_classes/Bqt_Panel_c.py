from PySide2 import QtWidgets, QtCore


class Bqt_Panel(QtWidgets.QWidget):
    """
    A simple collapsible panel (no animation).  Clicking the header toggles
    show/hide of its content.  All instances share the same built-in stylesheet.
    Use `panel.content_layout.addWidget(...)` to populate.
    """
    def __init__(self, title, parent=None):
        super(Bqt_Panel, self).__init__(parent)
        self._collapsed = False

        # ─── Main vertical layout ─────────────────────────────────────────────
        self._main_layout = QtWidgets.QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # ─── HEADER ────────────────────────────────────────────────────────────
        self.header = QtWidgets.QFrame(self)
        self.header.setObjectName("bqt_panel_header")
        self.header.setFixedHeight(24)

        # Unified stylesheet for header:
        self.header.setStyleSheet("""
            QFrame#bqt_panel_header {
                background-color: rgba(60, 60, 60, 255);
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)

        self._header_layout = QtWidgets.QHBoxLayout(self.header)
        self._header_layout.setContentsMargins(8, 0, 8, 0)
        self._header_layout.setSpacing(4)

        # Arrow icon: “▼” when expanded, “▶” when collapsed
        self.arrow_label = QtWidgets.QLabel(self.header)
        self.arrow_label.setFixedWidth(12)
        self.arrow_label.setText("▼")  # start expanded

        self.title_label = QtWidgets.QLabel(title, self.header)
        self.title_label.setStyleSheet("QLabel { color: white; }")

        self._header_layout.addWidget(self.arrow_label)
        self._header_layout.addWidget(self.title_label)
        self._header_layout.addStretch(1)

        # Make header clickable:
        self.header.mousePressEvent = self._on_header_clicked

        # ─── CONTENT AREA ─────────────────────────────────────────────────────
        self.content_area = QtWidgets.QWidget(self)
        self.content_area.setObjectName("bqt_panel_content")
        # unified transparent background for all panels’ content:
        self.content_area.setStyleSheet("QWidget#bqt_panel_content { background: transparent; }")

        self._content_layout = QtWidgets.QVBoxLayout(self.content_area)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(4)

        # Expose content_layout so callers can do:
        #    some_panel.content_layout.addWidget(...) 
        self.content_layout = self._content_layout

        # Add header and content to main layout
        self._main_layout.addWidget(self.header)
        self._main_layout.addWidget(self.content_area)

    def _on_header_clicked(self, event):
        """Toggle collapsed/expanded when header is clicked."""
        self.toggle()
        event.accept()

    def collapse(self):
        if self._collapsed:
            return
        self.content_area.hide()
        self.arrow_label.setText("▶")
        # Round all corners when collapsed:
        self.header.setStyleSheet("""
            QFrame#bqt_panel_header {
                background-color: rgba(60, 60, 60, 255);
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border-bottom-left-radius: 6px;
                border-bottom-right-radius: 6px;
            }
        """)
        self._collapsed = True

    def expand(self):
        if not self._collapsed:
            return
        self.content_area.show()
        self.arrow_label.setText("▼")
        # Reset bottom corners to square when expanded:
        self.header.setStyleSheet("""
            QFrame#bqt_panel_header {
                background-color: rgba(60, 60, 60, 255);
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)
        self._collapsed = False

    def toggle(self):
        if self._collapsed:
            self.expand()
        else:
            self.collapse()