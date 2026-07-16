from __future__ import absolute_import

from PySide6 import QtCore
from PySide6 import QtWidgets

from viewline import constants


class NormalCheckbox(QtWidgets.QCheckBox):

    def __init__(self, parent, label, **kwargs):

        # Initialize QLabel
        super(NormalCheckbox, self).__init__(parent)

        self.setText(label)
        self.setChecked(kwargs.get("checked", False))

        direction = kwargs.get("direction", QtCore.Qt.LayoutDirection.LeftToRight)

        self.setLayoutDirection(direction)


if __name__ == "__main__":
    pass
