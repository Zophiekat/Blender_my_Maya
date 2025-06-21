from PySide2 import QtWidgets, QtCore

class Bqt_Checkbox(QtWidgets.QCheckBox):
    """
    A custom QCheckBox styled with rounded corners and a Blender‐style checkmark.
    """
    def __init__(self, parent=None):
        super(Bqt_Checkbox, self).__init__(parent)

        # Apply the provided stylesheet:
        self.setStyleSheet("""
        QCheckBox {
            border-radius: 4px;
        }

        QCheckBox::indicator {
            width: 12px;
            height: 12px;
            border: 1px solid #3D3D3D;
            border-radius: 4px;
            border-style: solid;
            padding: 2px; /* Ensure consistent padding */
        }

        QCheckBox::indicator:checked {
            background-color: #4F6FAE;
            image: url(:/icons/blender_icon_checkmark.png);
            background-position: center;
            background-repeat: no-repeat;
        }

        QCheckBox::indicator:unchecked {
            background-color: #545454;
        }

        QCheckBox::indicator:unchecked:hover {
            background-color: #656565;
        }
        """)