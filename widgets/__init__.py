"""
Copyright (c) 2026, Motion-Craft Technology All rights reserved.
Author: Subin. Gopi (subing85@gmail.com).
Description: Main Qt GUI module for the Review Player application.
WARNING! All changes made in this file will be lost when recompiling source file!

This module contains the primary application window and integrates all major UI components, including:

    * Playlist browser
    * OpenGL media viewer
    * Playback timeline
    * Playback controls
    * Overlay/watermark display
    * FPS and AOV management
    * Keyboard shortcuts
    * Media loading and playback control

The MainWindow class acts as the central controller between the playback engine, playlist system, and Qt widgets.
"""

from __future__ import absolute_import

import utils
import logger
import resources
import constants

from PySide6 import QtGui
from PySide6 import QtCore
from PySide6 import QtWidgets

from ocio import OCIOProcessor

from playlist import Projects
from playlist import Versions

from widgets.pixmaps import PathPixmap

from widgets.buttons import TxtButton
from widgets.buttons import HelpButton
from widgets.buttons import OpenButton
from widgets.buttons import LoopButton
from widgets.buttons import MoveButton
from widgets.buttons import UndoButton
from widgets.buttons import ColorButton
from widgets.buttons import ClearButton
from widgets.buttons import ArrowButton
from widgets.buttons import PencilButton
from widgets.buttons import PencilButton
from widgets.buttons import EraserButton
from widgets.buttons import RenderButton
from widgets.buttons import EllipseButton
from widgets.buttons import RectangleButton

from widgets.buttons import ForwardButton
from widgets.buttons import BackwordButton
from widgets.buttons import PlayPauseButton
from widgets.buttons import DisplayMenuButton

from widgets.comboboxs import FbsCombobox
from widgets.comboboxs import AovsCombobox

from widgets.layouts import VerticalLayout
from widgets.layouts import HorizontalLayout
from widgets.layouts import HorizontalSpacer
from widgets.layouts import HorizontalSplitter

from widgets.styles import SetStylesheet
from widgets.labels import ToolNameLabel
from widgets.labels import ThicknesLabel
from widgets.labels import CopyrightLabel
from widgets.fontdialog import TxtInputDialog

from widgets.lineedits import ThicknesSpinBox

from widgets.pixmaps import NamePixmapIcon
from widgets.dialogs import OpenMediaDialog
from widgets.dialogs import FileDialog

from widgets.playlist import PlaylistGroup

from widgets.viewer import ViewerWidget
from widgets.timeline import TimelineWidget

from playback.player import MediaPlayer

LOGGER = logger.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow):
    """
    Main application window for the Review Player.

    This widget manages:

        * UI layout construction
        * Playback controls
        * Playlist interaction
        * Viewer updates
        * Timeline synchronization
        * Watermark overlays
        * Keyboard shortcuts
        * Media loading workflow
    """

    def __init__(self, parent=None, **kwargs):
        """
        Initialize the main application window.

        Args:
            parent (QtWidgets.QWidget, optional):
                Parent widget.
            **kwargs:
                Additional optional keyword arguments.
        """

        super(MainWindow, self).__init__(parent)

        # Current browse directory used by open dialog
        self.browsepath = None

        # OCIO color processor
        self.ocio = OCIOProcessor()

        # Playback controller
        self.player = MediaPlayer()

        # Load available projects
        self.projects = Projects.get()

        # Currently selected project
        self.current_project = None

        # Build UI
        self.setupUi()

        # Setup window icon
        self.setupIcons()

    def setupUi(self):
        """
        Build and initialize the main user interface.
        """

        # Configure main window size and title
        self.resize(*constants.WINDOW_SIZE)
        self.setWindowTitle(f"{constants.RP_TOOL_NAME}-{constants.RP_VERSION}")

        # Create central widget
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # Main vertical layout
        self.verticallayout = VerticalLayout(self.centralwidget, space=10, margins=(10, 10, 10, 10))

        # Main horizontal splitter
        self.splitter = HorizontalSplitter(self)
        self.verticallayout.addWidget(self.splitter)

        # Playlist Area
        self.playlistGroup = PlaylistGroup(self, projects=self.projects)
        self.splitter.addWidget(self.playlistGroup)

        # Viewer Area
        self.viewerGroupBox = QtWidgets.QGroupBox(self)
        self.splitter.addWidget(self.viewerGroupBox)

        self.verticallayout_viewer = VerticalLayout(
            self.viewerGroupBox, space=10, margins=(10, 10, 10, 10)
        )

        # Top Viewer Toolbar
        self.horizontallayout_panel = HorizontalLayout(None, space=10, margins=(0, 0, 0, 0))
        self.verticallayout_viewer.addLayout(self.horizontallayout_panel)

        # AOV selector
        self.aovsCombobox = AovsCombobox(self)
        self.horizontallayout_panel.addWidget(self.aovsCombobox)

        # Spacer
        self.horizontalspacer1 = HorizontalSpacer()
        self.horizontallayout_panel.addItem(self.horizontalspacer1)

        # Annotation Drawing #####################################

        self.toolNameLabel = ToolNameLabel(self)
        self.horizontallayout_panel.addWidget(self.toolNameLabel)

        # Pencil button
        self.pencilButton = PencilButton(
            self, tooltip="Pencil Tool", checkable=True, width=22, height=22
        )
        self.horizontallayout_panel.addWidget(self.pencilButton)

        self.arrowButton = ArrowButton(
            self, tooltip="Arrow Shape", checkable=True, width=22, height=22
        )
        self.arrowButton.setVisible(False)
        self.horizontallayout_panel.addWidget(self.arrowButton)

        self.ellipseButton = EllipseButton(
            self, tooltip="Ellipse Shape", checkable=True, width=22, height=22
        )
        self.horizontallayout_panel.addWidget(self.ellipseButton)

        self.rectangleButton = RectangleButton(
            self, tooltip="Rectangle Shape", checkable=True, width=22, height=22
        )
        self.horizontallayout_panel.addWidget(self.rectangleButton)

        self.eraserButton = EraserButton(
            self, tooltip="Erasier Tool", checkable=True, width=22, height=22
        )
        self.eraserButton.setCheckable(True)
        self.horizontallayout_panel.addWidget(self.eraserButton)

        self.thicknesLabel = ThicknesLabel(self, "Thicknes")
        self.horizontallayout_panel.addWidget(self.thicknesLabel)

        self.thicknesSpinBox = ThicknesSpinBox(self, 3)
        self.horizontallayout_panel.addWidget(self.thicknesSpinBox)

        self.radiusSpinBox = ThicknesSpinBox(self, 10)
        self.radiusSpinBox.setVisible(False)
        self.horizontallayout_panel.addWidget(self.radiusSpinBox)

        self.colorButton = ColorButton(self, tooltip="Pick Color", width=22, height=22)
        self.horizontallayout_panel.addWidget(self.colorButton)

        self.txtButton = TxtButton(self, tooltip="Text Tool", checkable=True, width=22, height=22)
        self.horizontallayout_panel.addWidget(self.txtButton)

        self.moveButton = MoveButton(self, tooltip="Move Tool", checkable=True, width=22, height=22)
        self.horizontallayout_panel.addWidget(self.moveButton)

        self.undoButton = UndoButton(self, tooltip="Undo", width=22, height=22)
        self.horizontallayout_panel.addWidget(self.undoButton)

        self.clearButton = ClearButton(self, tooltip="Clear", width=22, height=22)
        self.horizontallayout_panel.addWidget(self.clearButton)

        ########################################################

        # Spacer
        self.horizontalspacer2 = HorizontalSpacer()
        self.horizontallayout_panel.addItem(self.horizontalspacer2)

        self.renderButton = RenderButton(self, tooltip="Render Current Frame", width=22, height=22)
        self.horizontallayout_panel.addWidget(self.renderButton)

        self.horizontalspacer3 = HorizontalSpacer()
        self.horizontallayout_panel.addItem(self.horizontalspacer3)

        # Display menu button
        self.displayMenuButton = DisplayMenuButton(
            self, tooltip="Water mark display menu", width=32, height=32
        )
        self.horizontallayout_panel.addWidget(self.displayMenuButton)

        # Help button
        self.helpButton = HelpButton(self, tooltip="Help and Support (F2)", width=32, height=32)
        self.horizontallayout_panel.addWidget(self.helpButton)

        # OpenGL Viewer
        self.viewer = ViewerWidget(self)
        self.verticallayout_viewer.addWidget(self.viewer)

        # Timeline widget
        self.timeline = TimelineWidget()
        self.verticallayout_viewer.addWidget(self.timeline)

        # Playback Controller
        self.horizontallayout_controller = HorizontalLayout(None, space=10, margins=(0, 0, 0, 0))
        self.verticallayout_viewer.addLayout(self.horizontallayout_controller)

        # Open media button
        self.openButton = OpenButton(self, tooltip="Open Media (Ctrl+O)", width=32, height=32)
        self.horizontallayout_controller.addWidget(self.openButton)

        # Spacer
        self.horizontalspacer4 = HorizontalSpacer()
        self.horizontallayout_controller.addItem(self.horizontalspacer4)

        # Previous frame button
        self.backwordButton = BackwordButton(
            self, tooltip="Backword Frame (<)", width=32, height=32
        )
        self.horizontallayout_controller.addWidget(self.backwordButton)

        # Play/Pause button
        self.playPauseButton = PlayPauseButton(self, tooltip="Play (space)", width=42, height=42)
        self.player.set_playbutton(self.playPauseButton)

        # Register button with player
        self.horizontallayout_controller.addWidget(self.playPauseButton)

        # Next frame button
        self.forwardButton = ForwardButton(self, tooltip="Forward Frame (>)", width=32, height=32)
        self.horizontallayout_controller.addWidget(self.forwardButton)

        # Spacer
        self.horizontalspacer5 = HorizontalSpacer()
        self.horizontallayout_controller.addItem(self.horizontalspacer5)

        # Loop toggle button
        self.loopButton = LoopButton(
            self, tooltip="Loop the timeline (Ctrl+L)", width=42, height=32
        )
        self.horizontallayout_controller.addWidget(self.loopButton)

        # FPS selector
        self.fpsCombobox = FbsCombobox(self)
        self.fpsCombobox.fps_changed.connect(self.update_fps)
        self.horizontallayout_controller.addWidget(self.fpsCombobox)

        # Footer
        self.copyrightLabel = CopyrightLabel(self)
        self.verticallayout.addWidget(self.copyrightLabel)

        # Signal Connections
        self.playlistGroup.project_changed.connect(self.set_playlist)
        self.playlistGroup.click_widgetitem.connect(self.play_from_playlist)

        self.aovsCombobox.currentTextChanged.connect(self.player.set_aov)

        self.openButton.clicked.connect(self.openMedia)
        self.playPauseButton.clicked.connect(self.toggle_play_pause)
        self.loopButton.toggled.connect(self.player.set_loop)

        self.player.frame_ready.connect(self.viewer.set_frame)
        self.player.frame_changed.connect(self.timeline.set_current_frame)
        self.player.frame_changed.connect(self.viewer.set_current_frame)
        self.player.cache_changed.connect(self.timeline.set_cached_frames)
        self.timeline.frame_changed.connect(self.seek)

        self.thicknesSpinBox.thicknes_changed.connect(self.viewer.annotations.set_thickness)
        self.radiusSpinBox.thicknes_changed.connect(self.viewer.annotations.set_eraser_radius)
        self.colorButton.color_changed.connect(self.viewer.annotations.set_color)

        self.backwordButton.clicked.connect(self.backword_frame)
        self.forwardButton.clicked.connect(self.forward_frame)

        self.displayMenuButton.menu.display_changed.connect(self.viewer.set_overlay_option)

        # Initialize viewer overlay settings
        self.viewer.set_overlay_options(self.displayMenuButton.menu.watermarks)

        self.helpButton.clicked.connect(self.help)

        # self.pencilButton.toggled.connect(self.set_pencil_enabled)

        self.pencilButton.toggled.connect(lambda enabled: self.set_draw_enabled("pencil", enabled))
        self.arrowButton.toggled.connect(lambda enabled: self.set_draw_enabled("arrow", enabled))
        self.ellipseButton.toggled.connect(
            lambda enabled: self.set_draw_enabled("ellipse", enabled)
        )
        self.rectangleButton.toggled.connect(
            lambda enabled: self.set_draw_enabled("rectangle", enabled)
        )
        self.eraserButton.toggled.connect(lambda enabled: self.set_draw_enabled("eraser", enabled))
        self.txtButton.toggled.connect(lambda enabled: self.set_draw_enabled("txt", enabled))
        self.moveButton.toggled.connect(lambda enabled: self.set_draw_enabled("move", enabled))

        self.undoButton.clicked.connect(self.viewer.undo_strokes)
        self.clearButton.clicked.connect(self.viewer.clear_strokes)

        self.renderButton.clicked.connect(self.render)

        # Keyboard Shortcuts

        # Play / Pause
        self.playShortcut = QtGui.QShortcut(QtGui.QKeySequence("Space"), self)
        self.playShortcut.activated.connect(self.toggle_play_pause)

        # Previous frame
        self.backwordShortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Left), self)
        self.backwordShortcut.activated.connect(self.backword_frame)

        # Next frame
        self.forwardShortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Right), self)
        self.forwardShortcut.activated.connect(self.forward_frame)

        # Open media
        self.openShortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+O"), self)
        self.openShortcut.activated.connect(self.openMedia)

        # Loop toggle
        self.loopShortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+L"), self)
        self.loopShortcut.activated.connect(self.set_loop)

        # Help
        self.helpShortcut = QtGui.QShortcut(QtGui.QKeySequence("F2"), self)
        self.helpShortcut.activated.connect(self.help)

        # Load default playlist
        if self.projects:
            self.set_playlist(self.projects[0])

        # Maximize window if enabled
        if constants.MAXIMIZE:
            self.showMaximized()

        # Apply stylesheet theme
        SetStylesheet(self, theme=constants.DEFAULT_THEME)

        # Initial splitter sizes
        self.splitter.setSizes([300, 1065])

    def setupIcons(self):
        """
        Setup the main window icon.
        """

        pixmap = NamePixmapIcon(constants.RP_TOOL_ICON)
        self.setWindowIcon(pixmap)

    def set_playlist(self, project):
        """
        Update playlist versions based on selected project.

        Args:
            project (dict):
                Project context dictionary.
        """

        self.current_project = project

        # Load project versions
        versions = Versions.get(project)

        # Update playlist widget
        self.playlistGroup.set_versions(versions)

    def play_from_playlist(self, play, context):
        """
        Open media from playlist item.

        Args:
            play (bool):
                Start playback automatically.
            context (dict):
                Playlist version context.
        """

        # Clear viewer if media is missing
        if not context.get("media"):
            self.viewer.clear()
            return

        # Build watermark resources
        logs = {
            "project_logo": self.current_project["value"],
            "studio_logo": PathPixmap(resources.getIconFilepath(constants.STUDIO_NAME)),
        }

        # Update watermark values
        self.displayMenuButton.menu.update_watermarks(context, **logs)

        # Load media
        self.openMedia(filepath=context.get("media"))

        # Start playback if enabled
        if play:
            self.toggle_play_pause()

    def openMedia(self, filepath=None):
        """
        Open media file or sequence.

        Args:
            filepath (str, optional):
                Media file path or sequence pattern.
        """

        # Open browse dialog if filepath is not provided
        if not filepath:
            dialog = OpenMediaDialog(self, browsepath=self.browsepath)
            if dialog.exec():
                filepath = dialog.getfile()
                self.browsepath = utils.dirname(filepath)

            # Update watermark resources
            logs = {"studio_logo": PathPixmap(resources.getIconFilepath(constants.STUDIO_NAME))}
            self.displayMenuButton.menu.update_watermarks(dict(), **logs)

        # Clear current viewer frame
        self.viewer.clear()

        if not filepath:
            return

        # example:
        # /samples/footage/shot-1001-1/shot-1001.####.png

        LOGGER.info(f"Source filepath, {filepath}")

        # Load media into player
        self.player.load(filepath)

        # Sync FPS UI for video files
        self.reset_video_fps()

        # Sequence media supports AOVs
        if self.player.reader.media_type == "sequence":
            self.aovsCombobox.setEnabled(True)
            self.aovsCombobox.clear()
            self.aovsCombobox.addItems(self.player.reader.get_available_aovs())
        else:  # Disable AOVs for video files
            self.aovsCombobox.clear()
            self.aovsCombobox.setEnabled(False)

        # Update timeline range
        self.timeline.set_range(
            constants.START_FRAME, constants.START_FRAME + (self.player.frame_count - 1)
        )

    def set_loop(self):
        """
        Toggle playback loop state.
        """

        enable = False if self.loopButton.isChecked() else True
        self.loopButton.setChecked(enable)

    def toggle_play_pause(self):
        """
        Toggle playback state.
        """

        self.player.toggle_play_pause()

        # Update play button icon
        self.playPauseButton.switch(self.player.is_playing)

        # Sync FPS display
        self.reset_video_fps()

    def seek(self):
        """
        Seek playback to timeline frame.
        """

        self.player.seek(self.timeline.current_frame)

        # Sync FPS display
        self.reset_video_fps()

    def backword_frame(self):
        """
        Move playback backward by one frame.
        """

        self.player.backword_frame()

        # Sync FPS display
        self.reset_video_fps()

    def forward_frame(self):
        """
        Move playback forward by one frame.
        """

        self.player.forward_frame()

        # Sync FPS display
        self.reset_video_fps()

    def reset_video_fps(self):
        """
        Sync FPS combobox with currently loaded video FPS.
        """

        if not self.player.reader:
            return

        # Only applies to video playback
        if self.player.reader.media_type != "video":
            return

        fps = self.player.reader.get_fps(rounded=3)

        # Find matching FPS preset
        context = self.fpsCombobox.findByKey(fps, "value")
        if not context:
            return

        # Update combobox
        self.fpsCombobox.setValue(context)

    def update_fps(self, context):
        """
        Update playback FPS.

        Args:
            context (dict):
                FPS preset context.
        """

        if not context.get("value"):
            LOGGER.info(f"Invalid fps value")
            return

        fps = float(context["value"])

        # Update player FPS
        self.player.set_fps(fps)

    def set_draw_enabled(self, tool, enabled):
        buttons = [
            self.pencilButton,
            self.arrowButton,
            self.ellipseButton,
            self.rectangleButton,
            self.eraserButton,
            self.txtButton,
            self.moveButton,
        ]

        for button in buttons:
            if button.name == button:
                continue
            button.setChecked(False)

        self.toolNameLabel.setValue(enabled, tool)

        if tool == "txt" and enabled:
            txtInputDialog = TxtInputDialog(self)
            txtInputDialog.value_changed.connect(self.viewer.set_sketch_enabled)
            txtInputDialog.exec()
            self.txtButton.setChecked(False)

            return

        if tool == "eraser":
            self.thicknesSpinBox.setVisible(False)
            self.radiusSpinBox.setVisible(True)
            self.thicknesLabel.setValue("Radius")
        else:
            self.radiusSpinBox.setVisible(False)
            self.thicknesSpinBox.setVisible(True)
            self.thicknesLabel.setValue("Thicknes")

        self.viewer.set_sketch_enabled(tool, enabled, None)

    def render(self):
        if not self.viewer.current_frame:
            return

        fileDialog = FileDialog(
            self,
            "Browse your Save directory",
            label="Image",
            extensions=["png", "jpg"],
            browsepath=None,
        )
        filename = f"frame.{self.viewer.current_frame:04d}"

        filepath = fileDialog.savefile(filename)

        if filepath:
            self.viewer.save_frame(filepath)

    def help(self):
        """
        Open support or documentation URL.
        """

        # print(self.splitter.sizes())
        LOGGER.info(f"Support, {constants.WEBLINK}")

        # Open help URL in browser
        utils.openUrl(constants.WEBLINK)


if __name__ == "__main__":
    pass
