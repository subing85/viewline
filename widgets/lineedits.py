from __future__ import absolute_import

from PySide6 import QtGui
from PySide6 import QtCore
from PySide6 import QtWidgets


class ThicknesSpinBox(QtWidgets.QDoubleSpinBox):

    thicknes_changed = QtCore.Signal(float)

    def __init__(self, parent, value, **kwargs):
        super(ThicknesSpinBox, self).__init__(parent)

        decimals = kwargs.get("decimals") or 1
        minimum = kwargs.get("minimum") or 0.00
        maximum = kwargs.get("maximum") or 999999999.00

        self.setDecimals(2)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)

        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)

        alignments = {
            "left": QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
            "right": QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter,
            "Center": QtCore.Qt.AlignCenter,
        }

        if kwargs.get("alignment") and kwargs["alignment"] in alignments:
            self.setAlignment(alignments[kwargs["alignment"]])

        self.setMinimumSize(QtCore.QSize(106, 0))
        # self.setMaximumSize(QtCore.QSize(106, 30))

        self.valueChanged.connect(self.value_change)

    def value_change(self):
        self.thicknes_changed.emit(self.value())


class FontSizeSpinBox(QtWidgets.QSpinBox):

    def __init__(self, parent, value, **kwargs):
        super(FontSizeSpinBox, self).__init__(parent)

        minimum = kwargs.get("minimum") or 0
        maximum = kwargs.get("maximum") or 999999999

        self.setMinimum(minimum)
        self.setMaximum(maximum)

        self.setSingleStep(1)

        self.setValue(value)

        # self.fontSizeComboBox = QtWidgets.QSpinBox(self)
        # completer = QtWidgets.QCompleter(
        #     ["100", "200", "300", "400"]
        # )

        # self.fontSizeComboBox.lineEdit().setCompleter(completer)


if __name__ == "__main__":
    pass
