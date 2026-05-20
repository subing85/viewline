"""
Copyright (c) 2026, Motion-Craft Technology All rights reserved.
Author: Subin. Gopi (subing85@gmail.com).
Description: Review Player Qt custom playlist widget module.
WARNING! All changes made in this file will be lost when recompiling source file!

This module contains the primary playlist UI components used by the Review Player application.

The playlist system is responsible for:

    - Displaying project lists
    - Managing version/media playlists
    - Handling project switching
    - Displaying project thumbnails
    - Emitting media selection events
    - Providing playback interaction support

Main Components:
    PlaylistGroup:
        Main playlist container widget.

Features:
    - Project selection
    - Playlist browsing
    - Thumbnail preview support
    - Media open/play interaction
    - Signal-driven UI updates
    - Version/media list integration

Widget Architecture:
    PlaylistGroup
        ├── ProjectIconLabel
        ├── ProjectCombobox
        └── PlaylistTreewidget

Signals:
    project_changed:
        Emitted when the active project changes.

    click_widgetitem:
        Emitted when media items are clicked or double-clicked.
"""

from __future__ import absolute_import

from PySide6 import QtCore
from PySide6 import QtWidgets

from widgets.layouts import VerticalLayout
from widgets.layouts import HorizontalLayout

from widgets.labels import ProjectIconLabel
from widgets.comboboxs import ProjectCombobox
from widgets.treewidgets import PlaylistTreewidget


class PlaylistGroup(QtWidgets.QWidget):
    """
    Main playlist container widget.

    This widget combines:

        - Project selector
        - Project thumbnail preview
        - Media/version playlist browser

    The playlist group acts as the central media browsing interface inside the Review Player application.

    Signals:
        project_changed (dict):
            Emitted when the active project changes.

        click_widgetitem (bool, dict):
            Emitted when a media item is clicked or double-clicked.

            Arguments:
                bool:
                    Playback state request.

                    - False = open media
                    - True = play media

                dict:
                    Media/version context.

    Example:
        >>> playlist = PlaylistGroup(parent, projects=data)
    """

    project_changed = QtCore.Signal(dict)
    click_widgetitem = QtCore.Signal(bool, dict)

    def __init__(self, parent, *args, **kwargs):
        """
        Initialize playlist widget.

        Args:
            parent (QtWidgets.QWidget):
                Parent widget.

            *args:
                Additional positional arguments.

            **kwargs:
                Optional keyword arguments.

                projects (list):
                    Project context list.
        """

        super(PlaylistGroup, self).__init__(parent)

        # Store project data
        self.projects = kwargs.get("projects")

        # Main vertical layout
        self.verticallayout = VerticalLayout(self, space=5, margins=(0, 0, 0, 0))

        # Project header group
        self.projectGroupbox = QtWidgets.QGroupBox(self)
        self.verticallayout.addWidget(self.projectGroupbox)

        # Header horizontal layout
        self.horizontallayout = HorizontalLayout(
            self.projectGroupbox, space=10, margins=(10, 10, 10, 10)
        )

        # Project thumbnail preview
        self.projectIconLabel = ProjectIconLabel(self)
        self.horizontallayout.addWidget(self.projectIconLabel)

        # Project selector combobox
        self.projectCombobox = ProjectCombobox(self, key="name")
        self.projectCombobox.setItems(contextList=self.projects)
        self.projectCombobox.project_changed.connect(self.set_project)

        self.horizontallayout.addWidget(self.projectCombobox)

        # Playlist tree widget
        self.playlistTreewidget = PlaylistTreewidget(self)
        self.verticallayout.addWidget(self.playlistTreewidget)

        # Set initial project
        if self.projects:
            self.set_project(self.projects[0])

        # Connect playlist interactions
        self.playlistTreewidget.itemClicked.connect(self.open_media)
        self.playlistTreewidget.itemDoubleClicked.connect(self.play_media)

    def set_project(self, context):
        """
        Set current active project.

        This updates:

            - Project thumbnail
            - Current project context
            - UI project state

        Args:
            context (dict):
                Project context dictionary.

        Example:
            >>> widget.set_project(project)
        """

        # Update project thumbnail
        self.projectIconLabel.setThumbnail(context["image"])

        # Store thumbnail pixmap in context
        context["value"] = self.projectIconLabel.pixmap()

        # Emit project change signal
        self.project_changed.emit(context)

    def set_current_project(self, project):
        """
        Set current project in project combobox.

        Args:
            project (dict):
                Project context dictionary.
        """

        self.projectCombobox.setValue(project)

    def set_versions(self, versions):
        """
        Populate playlist with versions/media items.

        Args:
            versions (list):
                Media/version context list.

        Example:
            >>> widget.set_versions(versions)
        """

        self.playlistTreewidget.setValues(versions)

    def open_media(self, widgetitem):
        """
        Emit media open request. Triggered when a playlist item is single-clicked.

        Args:
            widgetitem (PlaylistWidgetItem):
                Selected playlist item.
        """

        self.click_widgetitem.emit(False, widgetitem.context)

    def play_media(self, widgetitem):
        """
        Emit media playback request. Triggered when a playlist item is double-clicked.

        Args:
            widgetitem (PlaylistWidgetItem):
                Selected playlist item.
        """

        self.click_widgetitem.emit(True, widgetitem.context)


if __name__ == "__main__":
    pass
