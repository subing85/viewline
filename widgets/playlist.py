# Copyright (c) 2026, Motion-Craft Technology All rights reserved.
# Author: Subin. Gopi (subing85@gmail.com).
# Description: Review Player Qt Custom playlist widget module.
# WARNING! All changes made in this file will be lost when recompiling source file!

from __future__ import absolute_import


from PySide6 import QtCore
from PySide6 import QtWidgets

from widgets.layouts import VerticalLayout
from widgets.layouts import HorizontalLayout

from widgets.labels import ProjectIconLabel
from widgets.comboboxs import ProjectCombobox
from widgets.treewidgets import PlaylistTreewidget


class PlaylistGroup(QtWidgets.QWidget):

    project_changed = QtCore.Signal(dict)
    click_widgetitem = QtCore.Signal(bool, dict)

    def __init__(self, parent, *args, **kwargs):
        super(PlaylistGroup, self).__init__(parent)

        self.projects = kwargs.get("projects")

        self.verticallayout = VerticalLayout(self, space=10, margins=(0, 0, 0, 0))

        self.projectGroupbox = QtWidgets.QGroupBox(self)
        self.verticallayout.addWidget(self.projectGroupbox)

        self.horizontallayout = HorizontalLayout(
            self.projectGroupbox, space=10, margins=(10, 10, 10, 10)
        )

        self.projectIconLabel = ProjectIconLabel(self)
        self.horizontallayout.addWidget(self.projectIconLabel)

        self.projectCombobox = ProjectCombobox(self, key="name")
        self.projectCombobox.setItems(contextList=self.projects)
        self.projectCombobox.project_changed.connect(self.set_project)

        self.horizontallayout.addWidget(self.projectCombobox)

        self.playlistTreewidget = PlaylistTreewidget(self)
        self.verticallayout.addWidget(self.playlistTreewidget)

        self.set_project(self.projects[0])

        self.playlistTreewidget.itemClicked.connect(self.open_media)
        self.playlistTreewidget.itemDoubleClicked.connect(self.play_media)

    def set_project(self, context):
        self.projectIconLabel.setThumbnail(context["image"])
        self.project_changed.emit(context)

    def set_current_project(self, project):
        self.projectCombobox.setValue(project)

    def set_versions(self, versions):
        self.playlistTreewidget.setValues(versions)

    def open_media(self, widgetitem):
        self.click_widgetitem.emit(False, widgetitem.context)

    def play_media(self, widgetitem):
        self.click_widgetitem.emit(True, widgetitem.context)


if __name__ == "__main__":
    pass
