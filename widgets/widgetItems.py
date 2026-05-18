# Copyright (c) 2026, Motion-Craft Technology All rights reserved.
# Author: Subin. Gopi (subing85@gmail.com).
# Description: Review Player Qt QTreeWidgetItem widget module.
# WARNING! All changes made in this file will be lost when recompiling source file!


import utils

from PySide6 import QtCore
from PySide6 import QtWidgets

from widgets.pixmaps import UrlPixmap
from widgets.pixmaps import PathPixmap
from widgets.pixmaps import NamePixmap
from widgets.pixmaps import PixmapIcon


class PlaylistWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent, *args, **kwargs):
        super(PlaylistWidgetItem, self).__init__(parent)

        self.context = args[0]

        self.size = kwargs.get("size", (128, 72))

        self.setFlags(
            QtCore.Qt.ItemIsSelectable
            | QtCore.Qt.ItemIsDropEnabled
            | QtCore.Qt.ItemIsUserCheckable
            | QtCore.Qt.ItemIsEnabled
        )

    def getContext(self):
        return self.context

    def setValue(self, context=None):
        self.context = context or self.context

        values = [
            f"\nVersion: {self.context['code']} | {self.context['id']}",
            f"Task: {self.context['sg_task']['name']}",
            f"Entity: {self.context['entity']['name']}",
            f"Status: {self.context['sg_status_list']}",
            f"created: {self.context['created_at']}",
            f"created By: {self.context['created_by']['name']}\n",
        ]

        self.setText(0, "\n".join(values))
        self.setIndexIcon(self.context.get("image"), index=0)

    def setFonts(self, index, fontSize=None, bold=False):
        fontSize = fontSize or constants.FONT_SIZE
        font = Font(fontSize, family=constants.FONT_FAMILY, bold=bold)
        self.setFont(index, font)

    def setIndexIcon(self, filepath, index=0):
        if filepath:
            pixmap = UrlPixmap(filepath) if utils.isUrl(filepath) else PathPixmap(filepath)
        else:
            pixmap = NamePixmap("unknown")

        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                *self.size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )

        icon = PixmapIcon(pixmap)
        self.setIcon(index, icon)

    def setBackgroundColor(self, index, color):
        qcolor = color if isinstance(color, QtGui.QColor) else QtGui.QColor(*color)
        brush = BackgroundBrush(qcolor)
        self.setBackground(index, brush)

    def setForegroundColor(self, index, color):
        qcolor = color if isinstance(color, QtGui.QColor) else QtGui.QColor(*color)
        brush = ForegroundBrush(qcolor)
        self.setForeground(index, brush)


if __name__ == "__main__":
    pass
