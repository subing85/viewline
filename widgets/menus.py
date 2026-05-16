
from functools import partial

from PySide6 import QtGui
from PySide6 import QtCore
from PySide6 import QtWidgets

from widgets.pixmaps import NamePixmapIcon



class DisplayMenus(QtWidgets.QMenu):

    values = QtCore.Signal(int)

    def __init__(self, parent, **kwargs):
        super(DisplayMenus, self).__init__(parent)

        self.setTitle("Display")

        self.items = [
            {"code": "frame", "enable": True, "checked": True},
            {"code": "project", "enable": True, "checked": True},
            {"code": "shot", "enable": True, "checked": True},
            {"code": "task", "enable": True, "checked": True},
            {"code": "version", "enable": True, "checked": True},
            {"code": "date", "enable": True, "checked": True},
            {"code": "aritist", "enable": True, "checked": True},
        ]

        for context in self.items:
            action = QtGui.QAction(self)
            action.setCheckable(True)
            action.setChecked(context["checked"])
            action.setText(context["code"])
            action.setEnabled(context["enable"])
            context["action"] = action

            self.addAction(action) # self.addSeparator()
            action.triggered.connect(self.get_display)

        self.setTearOffEnabled(True)

    def get_display(self):
        result = list()
        for context in self.items:
            if not context["action"].isChecked():
                continue
            result.append(context)

        self.values.emit(result)


if __name__ == "__main__":
    pass
