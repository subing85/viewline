from PySide6 import QtCore
from PySide6 import QtWidgets


from widgets.pixmaps import NamePixmapIcon


class IconButton(QtWidgets.QPushButton):
    name = "icon"

    def __init__(self, parent, **kwargs):
        super(IconButton, self).__init__(parent)

        self.width = kwargs.get("width", 22)
        self.height = kwargs.get("height", 22)
        self.locked = False if kwargs.get("locked") == False else True

        self.setToolTip(kwargs.get("toolTip", "unknown"))
        self.setFlat(True)

        icon = NamePixmapIcon(self.name)
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(self.width, self.height))

        if self.locked:
            self.setMinimumSize(QtCore.QSize(self.width, self.height))
            self.setMaximumSize(QtCore.QSize(self.width, self.height))


class OpenButton(IconButton):
    name = "open"

class BackwordButton(IconButton):
    name = "backward"


class PlayButton(IconButton):
    name = "play"


class ForwardButton(IconButton):
    name = "forward"


class LoopButton(IconButton):
    name = "loop"
