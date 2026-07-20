"""
Copyright (c) 2026, Motion-Craft Technology All rights reserved.

Author:
    Subin. Gopi (subing85@gmail.com).

Module:
    ./widgets/viewer.py

Description:
    Provides the primary media display component used by the Review Player application.

Responsibilities:
    - OpenGL-based image rendering
    - Video frame display
    - Image sequence preview
    - Dynamic fit-to-window scaling
    - Aspect ratio preservation
    - Annotation rendering
    - Watermark and overlay rendering
    - Playback frame visualization
    - Frame export and rendering

Responsibilities:
    - Display source media frames.
    - Manage OpenGL rendering.
    - Maintain viewport calculations.
    - Render annotations.
    - Render watermarks and overlays.
    - Handle user interaction tools.
    - Export annotated frames.

Main Components:
    ViewerWidget:
        OpenGL-powered media display widget.

    AnnotationManager:
        Handles drawing, editing, moving,
        erasing, and rendering annotations.

    Overlay System:
        Handles watermark rendering.

Features:
    - OpenGL frame rendering.
    - Dynamic viewport resizing.
    - Aspect ratio preservation.
    - Annotation rendering.
    - Pencil annotations.
    - Rectangle annotations.
    - Ellipse annotations.
    - Text annotations.
    - Annotation move tool.
    - Annotation erase tool.
    - Annotation undo support.
    - Overlay rendering system.
    - Text watermark support.
    - Image watermark support.
    - Opacity control.
    - Font customization.
    - Playback frame visualization.
    - Frame export rendering.

Overlay Positions:
    - top_left
    - top_center
    - top_right
    - center
    - bottom_left
    - bottom_center
    - bottom_right

Overlay Types:
    text:
        Dynamic text overlays.

    image:
        Image/logo overlays.

Architecture:
    ViewerWidget
        │
        ├── OpenGL Renderer
        │       │
        │       └── Media Frame Display
        │
        ├── Annotation Layer
        │       │
        │       ├── Pencil
        │       ├── Rectangle
        │       ├── Ellipse
        │       ├── Text
        │       └── Selection Tools
        │
        └── Overlay Layer
                │
                ├── Text Watermarks
                └── Image Watermarks

Rendering Pipeline:
    Source Frame
        ↓
    OpenGL Draw
        ↓
    QPainter Overlay
        ↓
    Annotation Rendering
        ↓
    Watermark Rendering

Export Pipeline:
    Source Frame
        ↓
    Annotation Rendering
        ↓
    Watermark Rendering
        ↓
    QImage Output

Notes:
    - Annotations are stored separately from source media.
    - Watermarks are display-only elements.
    - Watermarks are excluded from annotation undo history.
    - Export rendering uses source-frame resolution rather than viewport resolution.
"""

from __future__ import absolute_import

import numpy

from OpenGL import GL

from PySide6 import QtGui
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtOpenGLWidgets

from viewline import utils
from viewline import logger
from viewline import constants


from viewline.materials.gl_shader import GLShader
from viewline.materials.gl_texture import GLTexture
from viewline.materials.gl_screen import FullscreenQuad
from viewline.materials.gl_ocio_shader import OCIOShader

from viewline.widgets.annotations import Sketch

from viewline.widgets.buttons import TxtButton
from viewline.widgets.buttons import OpenButton
from viewline.widgets.buttons import LoopButton
from viewline.widgets.buttons import MoveButton
from viewline.widgets.buttons import UndoButton
from viewline.widgets.buttons import OcioButton
from viewline.widgets.buttons import ColorButton
from viewline.widgets.buttons import ClearButton
from viewline.widgets.buttons import ArrowButton
from viewline.widgets.buttons import FilterButton
from viewline.widgets.buttons import PencilButton
from viewline.widgets.buttons import EraserButton
from viewline.widgets.buttons import RenderButton
from viewline.widgets.buttons import RecapsButton
from viewline.widgets.buttons import ForwardButton
from viewline.widgets.buttons import EllipseButton
from viewline.widgets.buttons import BackwardButton
from viewline.widgets.buttons import RectangleButton
from viewline.widgets.buttons import PlayPauseButton
from viewline.widgets.buttons import WatermarkMenuButton

from viewline.widgets.sliders import VolumeSlider

from viewline.widgets.labels import ThicknesLabel
from viewline.widgets.labels import ToolNameLabel

from viewline.widgets.comboboxs import FbsCombobox
from viewline.widgets.comboboxs import AovsCombobox

from viewline.widgets.timeline import TimelineWidget

from viewline.widgets.layouts import VerticalLayout
from viewline.widgets.layouts import HorizontalLayout
from viewline.widgets.layouts import HorizontalSpacer

from viewline.widgets.lineedits import ThicknesSpinBox
from viewline.widgets.fontdialog import TxtInputDialog

LOGGER = logger.getLogger(__name__)


class ViewFrame(QtWidgets.QFrame):
    """
    Main viewer container widget.

    Acts as the primary media viewing workspace of the Review Player application.

    Data Flow:
        Media Source
                ↓
          ViewerWidget
                ↓
          OpenGL Display
                ↓
        Annotation Layer

    Notes:
        - Acts as the central viewer workspace.
        - Coordinates playback and annotation tools.
        - ViewerWidget performs all rendering operations.
        - Timeline controls are isolated from rendering logic.

    """

    def __init__(self, parent, *args, **kwargs):
        super(ViewFrame, self).__init__(parent)

        # Apply frame appearance
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)

        # Main Layout, Root viewer layout
        self.verticallayout = VerticalLayout(self, space=10, margins=(10, 10, 10, 10))

        # --------------------------------------------------
        # Viewer Toolbar
        # --------------------------------------------------
        # Annotation and viewer controls
        self.viewToolbarLayout = ViewToolbarLayout(None, space=20, margins=(5, 5, 5, 5))
        self.verticallayout.addLayout(self.viewToolbarLayout)

        # --------------------------------------------------
        # OpenGL Viewer
        # --------------------------------------------------
        self.viewer = GLViewer(self)
        self.verticallayout.addWidget(self.viewer)

        # --------------------------------------------------
        # Timeline Widget
        # --------------------------------------------------
        # Frame navigation widget
        self.timeline = TimelineWidget()
        self.verticallayout.addWidget(self.timeline)

        # --------------------------------------------------
        # Playback Toolbar
        # --------------------------------------------------
        # Playback control toolbar
        self.timelineToolbarLayout = TimelineToolbarLayout(None, space=10, margins=(5, 5, 5, 5))
        self.verticallayout.addLayout(self.timelineToolbarLayout)


class ViewToolbarLayout(HorizontalLayout):
    """
    Provides all viewer-related controls used for media review, annotation drawing, rendering, watermark display, and recap management.

    Responsibilities:
        - Manage annotation tool selection.
        - Manage drawing attributes.
        - Manage AOV selection.
        - Manage watermark visibility.
        - Manage frame rendering actions.
        - Manage recap panel visibility.
        - Emit viewer interaction signals.

    Features:
        - AOV selection.
        - Pencil drawing tool.
        - Ellipse drawing tool.
        - Rectangle drawing tool.
        - Text annotation tool.
        - Move annotation tool.
        - Eraser tool.
        - Thickness control.
        - Eraser radius control.
        - Color picker.
        - Undo support.
        - Clear support.
        - Watermark controls.
        - Frame rendering.
        - Recap panel controls.

    Architecture:
        ViewToolbarLayout
            │
            ├── AOV Controls
            │
            ├── Annotation Tools
            │       ├── Pencil
            │       ├── Arrow
            │       ├── Ellipse
            │       ├── Rectangle
            │       ├── Text
            │       ├── Move
            │       └── Eraser
            │
            ├── Drawing Controls
            │       ├── Thickness
            │       ├── Radius
            │       └── Color
            │
            ├── Edit Actions
            │       ├── Undo
            │       └── Clear
            │
            ├── Viewer Actions
            │       ├── Watermarks
            │       └── Render
            │
            └── Review Actions
                    └── Recaps

    Signal Flow:
        User Interaction
                ↓
        Toolbar Widgets
                ↓
        ViewToolbarLayout
                ↓
        ViewerWidget / ViewFrame
    """

    # Signal emitted when click open button
    open_trigger = QtCore.Signal(bool)

    # Signal emitted when click ocio button
    ocio_trigger = QtCore.Signal(bool)

    # Signal emitted when click filter button
    filter_trigger = QtCore.Signal(bool)

    # Signal emitted when current AOV changes
    aov_changed = QtCore.Signal(str)

    # Signal emitted when drawing thickness changes
    thicknes_changed = QtCore.Signal(float)

    # Signal emitted when eraser radius changes
    radius_changed = QtCore.Signal(float)

    # Signal emitted when drawing color changes
    color_changed = QtCore.Signal(tuple)

    # Signal emitted when drawing tool state changes
    draw_enabled = QtCore.Signal(str, bool, object)

    # Signal emitted when undo is requested
    undo_stack = QtCore.Signal()

    # Signal emitted when clear is requested
    clear_stack = QtCore.Signal()

    # Signal emitted when watermark settings change
    water_marks = QtCore.Signal(bool, str, str, dict)

    # Signal emitted when frame render is requested
    trigger_render = QtCore.Signal()

    # Signal emitted when recap panel visibility changes
    trigger_recaps = QtCore.Signal(bool)

    def __init__(self, parent, *args, **kwargs):
        """
        Initialize viewer toolbar.

        Args:
            parent (QtWidgets.QWidget):
                Parent widget.
        """

        # Initialize base horizontal layout
        super(ViewToolbarLayout, self).__init__(parent, *args, **kwargs)

        # Build toolbar UI
        self.setupUi()

    def setupUi(self):
        """
        Build viewer toolbar user interface.

        """

        # Open media button
        self.openButton = OpenButton(None, tooltip="Open Media (Ctrl+O)", width=22, height=22)
        self.addWidget(self.openButton)

        # --------------------------------------------------
        # OCIO Selection
        # --------------------------------------------------
        self.ocioButton = OcioButton(None)
        self.addWidget(self.ocioButton)

        # --------------------------------------------------
        # Color Filter Selection
        # --------------------------------------------------
        self.filterButton = FilterButton(None)
        self.addWidget(self.filterButton)

        # --------------------------------------------------
        # AOV Selection
        # --------------------------------------------------
        self.aovsCombobox = AovsCombobox(None)
        self.addWidget(self.aovsCombobox)

        # Spacer after AOV selector
        self.horizontalspacer1 = HorizontalSpacer()
        self.addItem(self.horizontalspacer1)

        # --------------------------------------------------
        # Active Tool Display
        # --------------------------------------------------

        # Displays currently active annotation tool
        self.toolNameLabel = ToolNameLabel(None)
        self.addWidget(self.toolNameLabel)

        # --------------------------------------------------
        # Annotation Tools
        # --------------------------------------------------

        # Pencil drawing tool
        self.pencilButton = PencilButton(
            None, tooltip="Pencil Tool", checkable=True, width=22, height=22
        )
        self.addWidget(self.pencilButton)

        # Arrow annotation tool
        self.arrowButton = ArrowButton(
            None, tooltip="Arrow Shape", checkable=True, width=22, height=22
        )

        # Hidden until arrow support is enabled
        self.arrowButton.setVisible(False)
        self.addWidget(self.arrowButton)

        # Ellipse annotation tool
        self.ellipseButton = EllipseButton(
            None, tooltip="Ellipse Shape", checkable=True, width=22, height=22
        )
        self.addWidget(self.ellipseButton)

        # Rectangle annotation tool
        self.rectangleButton = RectangleButton(
            None, tooltip="Rectangle Shape", checkable=True, width=22, height=22
        )
        self.addWidget(self.rectangleButton)

        # Eraser tool
        self.eraserButton = EraserButton(
            None, tooltip="Erasier Tool", checkable=True, width=22, height=22
        )
        self.eraserButton.setCheckable(True)
        self.addWidget(self.eraserButton)

        # --------------------------------------------------
        # Drawing Controls
        # --------------------------------------------------

        # Thickness label
        self.thicknesLabel = ThicknesLabel(None, "Thicknes")
        self.addWidget(self.thicknesLabel)

        # Annotation thickness control
        self.thicknesSpinBox = ThicknesSpinBox(None, 3, tooltip="Strokes Size")
        self.addWidget(self.thicknesSpinBox)

        # Eraser radius control
        self.radiusSpinBox = ThicknesSpinBox(None, 10, tooltip="Eraser Size")

        # Hidden until eraser tool becomes active
        self.radiusSpinBox.setVisible(False)
        self.addWidget(self.radiusSpinBox)

        # Annotation color picker
        self.colorButton = ColorButton(
            None, tooltip="Pick Color", color=constants.DEFAULT_SKETCH_COLOR, width=22, height=22
        )
        self.addWidget(self.colorButton)

        # --------------------------------------------------
        # Text Annotation Tool
        # --------------------------------------------------

        # Text annotation tool
        self.txtButton = TxtButton(None, tooltip="Text Tool", checkable=True, width=22, height=22)
        self.addWidget(self.txtButton)

        # --------------------------------------------------
        # Move Tool
        # --------------------------------------------------

        # Move existing annotations
        self.moveButton = MoveButton(None, tooltip="Move Tool", checkable=True, width=22, height=22)
        self.addWidget(self.moveButton)

        # --------------------------------------------------
        # Edit Actions
        # --------------------------------------------------

        # Undo last annotation action
        self.undoButton = UndoButton(None, tooltip="Undo", width=22, height=22)
        self.addWidget(self.undoButton)

        # Clear all annotations
        self.clearButton = ClearButton(None, tooltip="Clear", width=22, height=22)
        self.addWidget(self.clearButton)

        self.horizontalspacer2 = HorizontalSpacer()
        self.addItem(self.horizontalspacer2)

        # --------------------------------------------------
        # Watermark Controls
        # --------------------------------------------------

        # Watermark display configuration menu
        self.watermarkMenuButton = WatermarkMenuButton(
            None, tooltip="Water mark display menu", width=32, height=32
        )
        self.addWidget(self.watermarkMenuButton)

        # Spacer before render controls
        self.horizontalspacer3 = HorizontalSpacer()
        self.addItem(self.horizontalspacer3)

        # --------------------------------------------------
        # Rendering Controls
        # --------------------------------------------------

        # Render current frame with annotations

        self.renderButton = RenderButton(None, tooltip="Render Current Frame", width=22, height=22)
        self.addWidget(self.renderButton)

        # Spacer before recap controls
        self.horizontalspacer4 = HorizontalSpacer()
        self.addItem(self.horizontalspacer4)

        # --------------------------------------------------
        # Review Controls
        # --------------------------------------------------

        # Toggle recap panel visibility
        self.recapsButton = RecapsButton(
            None, tooltip="Display Recap Panel", width=32, height=32, checkable=True
        )
        self.addWidget(self.recapsButton)

        # --------------------------------------------------
        # Signal Connections
        # --------------------------------------------------

        # Open media action
        self.openButton.clicked.connect(self.open)

        # Call Ocio widget
        self.ocioButton.clicked.connect(self.call_ocio)

        # Call Filter widget
        self.filterButton.clicked.connect(self.call_filter)

        # AOV selection
        self.aovsCombobox.currentTextChanged.connect(self.set_current_aov)

        # Thickness control
        self.thicknesSpinBox.thicknes_changed.connect(self.set_current_thicknes)

        # Radius control
        self.radiusSpinBox.thicknes_changed.connect(self.set_current_radius)

        # Color picker
        self.colorButton.color_changed.connect(self.set_current_color)

        # Annotation tools
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

        # Undo action
        self.undoButton.clicked.connect(self.undo_strokes)

        # Clear action
        self.clearButton.clicked.connect(self.clear_strokes)

        # Watermark menu
        self.watermarkMenuButton.menu.display_changed.connect(self.set_water_marks)

        # Render current frame
        self.renderButton.clicked.connect(self.render)

        # Toggle recap panel
        self.recapsButton.toggled.connect(self.set_recaps)

    def update_watermarks(self, context, **kwargs):
        """
        Update watermark display configuration.

        Refreshes watermark values displayed inside the watermark menu using the supplied context information.

        Args:
            context (dict):
                Current media or project context.

            **kwargs:
                Additional watermark data.
        """

        # Update watermark menu contents
        self.watermarkMenuButton.menu.update_watermarks(context, **kwargs)

    def open(self):
        """
        Trigger open media action.

        Emits timeline open request.
        """

        # Notify timeline controller

        self.open_trigger.emit(False)

    def call_ocio(self):
        self.ocio_trigger.emit(True)

    def call_filter(self):
        self.filter_trigger.emit(True)

    def set_aovs(self, typed, aovs):
        """
        Populate available AOVs.

        Enables the AOV selector when sequence media contains multiple AOV layers.

        Args:
            typed (str):
                Media type.

            aovs (list):
                Available AOV names.
        """

        # Enable AOV selection for sequences
        if typed == "sequence":
            # Enable combobox
            self.aovsCombobox.setEnabled(True)

            # Remove previous AOV entries
            self.aovsCombobox.clear()

            # Add new AOV entries
            self.aovsCombobox.addItems(aovs)
        else:
            # Remove all AOV entries
            self.aovsCombobox.clear()

            # Disable combobox
            self.aovsCombobox.setEnabled(False)

    def set_current_aov(self, aov):
        """
        Emit selected AOV.

        Args:
            aov (str):
                Selected AOV name.
        """

        # Forward selected AOV
        self.aov_changed.emit(aov)

    def set_current_thicknes(self, value):
        """
        Emit drawing thickness value.

        Args:
            value (float):
                Annotation thickness.
        """

        # Forward thickness value
        self.thicknes_changed.emit(value)

    def set_current_radius(self, value):
        """
        Emit eraser radius value.

        Args:
            value (float):
                Eraser radius.
        """

        # Forward radius value
        self.radius_changed.emit(value)

    def set_current_color(self, value):
        """
        Emit selected annotation color.

        Args:
            value (tuple):
                RGB color tuple.
        """

        # Forward selected color
        self.color_changed.emit(value)

    def set_draw_enabled(self, tool, enabled):
        """
        Activate drawing tool.

        Ensures only one annotation tool remains active at a time and updates related UI controls.

        Args:
            tool (str):
                Tool identifier.

            enabled (bool):
                Tool enabled state.
        """

        # List of available drawing tools
        buttons = [
            self.pencilButton,
            self.arrowButton,
            self.ellipseButton,
            self.rectangleButton,
            self.eraserButton,
            self.txtButton,
            self.moveButton,
        ]

        # Disable all other tools
        for button in buttons:
            if button.name == button:
                continue
            button.setChecked(False)

        # Update current tool label
        self.toolNameLabel.setValue(enabled, tool)

        # Launch text annotation dialog
        if tool == "txt" and enabled:
            # Create dialog
            txtInputDialog = TxtInputDialog(self.parentWidget())

            # Receive text settings
            txtInputDialog.value_changed.connect(self.txt_value_changed)

            # Open dialog
            txtInputDialog.exec()

            # Reset text tool button
            self.txtButton.setChecked(False)

            return

        # Switch to eraser controls
        if tool == "eraser":
            # Hide thickness control
            self.thicknesSpinBox.setVisible(False)

            # Show radius control
            self.radiusSpinBox.setVisible(True)

            # Update label
            self.thicknesLabel.setValue("Radius")
        else:
            # Hide radius control
            self.radiusSpinBox.setVisible(False)

            # Show thickness control
            self.thicknesSpinBox.setVisible(True)

            # Update label
            self.thicknesLabel.setValue("Thicknes")

        # Notify viewer
        self.draw_enabled.emit(tool, enabled, None)

    def txt_value_changed(self, tool, enabled, font):
        """
        Forward text annotation settings.

        Args:
            tool (str):
                Tool identifier.

            enabled (bool):
                Tool state.

            font (dict):
                Text formatting settings.
        """

        # Forward text settings
        self.draw_enabled.emit(tool, enabled, font)

    def undo_strokes(self):
        """
        Trigger undo operation.

        Emits undo request signal.
        """

        # Emit undo signal
        self.undo_stack.emit()

    def clear_strokes(self):
        """
        Trigger clear operation.

        Emits clear request signal.
        """

        # Emit clear signal
        self.clear_stack.emit()

    def set_water_marks(self, *args):
        """
        Forward watermark updates.

        Args:
            *args:
                Watermark update parameters.
        """

        # Emit watermark update signal
        self.water_marks.emit(*args)

    def render(self):
        """
        Trigger frame render operation.

        Emits render request signal.
        """

        # Emit render signal
        self.trigger_render.emit()

    def set_recaps(self, enabled):
        """
        Toggle recap panel visibility.

        Args:
            enabled (bool):
                Recap panel state.
        """

        # Emit recap visibility state
        self.trigger_recaps.emit(enabled)


class TimelineToolbarLayout(HorizontalLayout):
    """
    Timeline playback toolbar layout.

    Provides transport controls used for media playback, navigation, looping, and FPS management.

    Responsibilities:
        - Media open action
        - Playback control
        - Frame navigation
        - Loop state management
        - FPS selection
        - Timeline signal routing

    Features:
        - Open media button
        - Previous frame navigation
        - Play / Pause control
        - Next frame navigation
        - Loop playback toggle
        - FPS preset selector
        - Timeline event forwarding

    Components:
        OpenButton:
            Opens media files.

        BackwardButton:
            Moves to previous frame.

        PlayPauseButton:
            Controls playback state.

        ForwardButton:
            Moves to next frame.

        LoopButton:
            Enables continuous playback.

        FbsCombobox:
            Controls playback FPS.

    Architecture:
        Open Button
            ↓
        Timeline Event
            ↓
        Media Loader

        Backward Button
            ↓
        Timeline Event
            ↓
        Previous Frame

        Play / Pause Button
            ↓
        Timeline Event
            ↓
        Playback Controller

        Forward Button
            ↓
        Timeline Event
            ↓
        Next Frame

        Loop Button
            ↓
        Loop State
            ↓
        Playback Controller

        FPS Combobox
            ↓
        FPS Context
            ↓
        Viewer Playback Rate

    Signals:
        fps_chanaged(dict):
            Emitted when FPS preset changes.

        trigger_timeline(str, bool):
            Emitted for timeline actions.

            Supported actions:

                - open
                - Backward
                - play_pause
                - forward
                - loop

    Notes:
        This layout contains no playback logic.
        It only provides user controls and emits
        timeline-related signals for the player.
    """

    # Signal emitted when fps value changes
    fps_chanaged = QtCore.Signal(dict)

    # Signal emitted when timeline tools clicked
    trigger_timeline = QtCore.Signal(str, bool)

    # Signal emitted when volume value changes
    volume_changed = QtCore.Signal(float)

    def __init__(self, parent, *args, **kwargs):
        """
        Initialize timeline toolbar layout.

        Creates the toolbar container and builds all timeline playback controls.

        Args:
            parent (QtWidgets.QWidget):
                Parent widget.

            *args:
                Additional positional arguments.

            **kwargs:
                Additional keyword arguments.
        """

        # Initialize base horizontal layout
        super(TimelineToolbarLayout, self).__init__(parent, *args, **kwargs)

        # Build interface
        self.setupUi()

    def setupUi(self):
        """
        Build timeline toolbar user interface.

        Creates playback controls, FPS selector, spacers, and signal connections used by the timeline toolbar.
        """
        # FPS selector combobox
        self.fpsCombobox = FbsCombobox(None)

        # Listen for FPS changes
        self.fpsCombobox.fps_changed.connect(self.update_fps)
        self.addWidget(self.fpsCombobox)

        # Loop playback button
        self.loopButton = LoopButton(
            None, tooltip="Loop the timeline (Ctrl+L)", width=32, height=32
        )
        self.addWidget(self.loopButton)

        # Left spacer
        self.horizontalspacer1 = HorizontalSpacer()
        self.addItem(self.horizontalspacer1)

        # Previous frame button
        self.backwardButton = BackwardButton(
            None, tooltip="Backward Frame (<)", width=22, height=22
        )
        self.addWidget(self.backwardButton)

        # Play / Pause button
        self.playPauseButton = PlayPauseButton(None, tooltip="Play (space)", width=32, height=32)
        self.addWidget(self.playPauseButton)

        # Next frame button
        self.forwardButton = ForwardButton(None, tooltip="Forward Frame (>)", width=22, height=22)
        self.addWidget(self.forwardButton)

        # Right spacer
        self.horizontalspacer2 = HorizontalSpacer()
        self.addItem(self.horizontalspacer2)

        self.volumeSlider = VolumeSlider(None)
        self.addWidget(self.volumeSlider)

        # Previous frame action
        self.backwardButton.clicked.connect(self.backward)

        # Play / Pause action
        self.playPauseButton.clicked.connect(self.play_pause)

        # Next frame action
        self.forwardButton.clicked.connect(self.forward)

        # Loop action
        self.loopButton.toggled.connect(self.loop)

        self.volumeSlider.valueChanged.connect(self.volume_control)

    def backward(self):
        """
        Trigger previous frame action.

        Emits timeline Backward request.
        """

        # Notify timeline controller

        self.trigger_timeline.emit("backward", False)

    def play_pause(self):
        """
        Trigger play / pause action.

        Emits playback toggle request.
        """

        # Notify timeline controller

        self.trigger_timeline.emit("play_pause", False)

    def forward(self):
        """
        Trigger next frame action.

        Emits timeline forward request.
        """

        # Notify timeline controller

        self.trigger_timeline.emit("forward", False)

    def loop(self, enabled):
        """
        Toggle playback looping.

        Args:
            enabled (bool):
                Loop playback state.
        """

        # Notify timeline controller

        self.trigger_timeline.emit("loop", enabled)

    def volume_control(self, value):
        self.volume_changed.emit(value / 100)

    def reset_fps(self, typed, fps):
        """
        Reset FPS combobox selection.

        Updates the FPS selector to match the playback FPS of the currently loaded video media.

        Args:
            typed (str):
                Media type.

            fps (float):
                Playback FPS value.
        """

        # Only applies to video media
        if typed != "movie":
            return

        # Find matching FPS preset
        context = self.fpsCombobox.findByKey(fps, "value")

        # Ignore unsupported FPS values
        if not context:
            return

        # Update selected FPS preset
        self.fpsCombobox.setValue(context)

    def update_fps(self, value):
        """
        Forward FPS selection changes.

        Args:
            value (dict):
                Selected FPS context.
        """

        # Emit FPS update signal
        self.fps_chanaged.emit(value)


class GLViewer(QtOpenGLWidgets.QOpenGLWidget):
    """Modern OpenGL image viewer."""

    render_finished = QtCore.Signal(str)

    def __init__(self, parent=None):
        """Create OpenGL viewer."""

        super().__init__(parent)

        # Expand inside layouts.

        # Configure expanding size policy
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding
        )

        self.setSizePolicy(sizePolicy)

        # Enable multisampling.

        self.set_samples(constants.VIEWER_SAMPLES_RATE)

        self.ocio_processor = None

        # OpenGL resources.

        self.texture = None
        self.shader = None
        self.quad = None
        self.ocio_shader = None  # GPU OCIO shader
        self.use_ocio = False

        # Current image.

        self.numpy_frame = None

        # Image size.
        self.image_width = 0
        self.image_height = 0
        self.channels = None

        # Display rectangle.
        self.display_rect = QtCore.QRect()

        # Timeline.
        self.current_frame = None

        # Camera
        # Current zoom factor.
        # 1.0 = Fit
        # 2.0 = 200%

        self.zoom = 1.0

        # Pan offset (normalized).
        self.pan = QtCore.QPointF(0.0, 0.0)

        # Viewer mode.
        self.fit_mode = True

        self.display_parameter = None
        self.style_parameter = None
        self.filter_parameter = None

        # Annotation system.
        self.sketch = Sketch()

    def set_samples(self, samples=8):
        """Configure OpenGL multisampling."""

        surface = QtGui.QSurfaceFormat()
        surface.setSamples(samples)
        self.setFormat(surface)

    def initializeGL(self):
        """Initialize OpenGL resources."""

        # Background colour.
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)

        # Enable alpha blending.
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # Create fullscreen quad.
        self.quad = FullscreenQuad()
        self.quad.initialize()

        # Create texture.
        self.texture = GLTexture()
        self.texture.initialize()

        # Compile default shader.
        self.shader = GLShader()
        self.shader.initialize(name="display")

        # if self.ocio_processor:
        self.build_ocio_shader()

    def resizeGL(self, width, height):
        """Viewport resized."""

        GL.glViewport(0, 0, width, height)

    def set_frame(self, frame):
        """Update current image.

        Args:
            frame (numpy.ndarray):
                RGB or RGBA image.
        """

        # Store frame.
        self.numpy_frame = frame

        if frame is None:
            return

        # Image size.
        # self.image_width = frame.width
        # self.image_height = frame.height
        self.image_height, self.image_width, self.channels = frame.shape

        # Texture upload happens inside paintGL().
        self.update()

    def clear(self):
        """Clear viewer."""

        self.numpy_frame = None

        # self.texture.clear()

        self.sketch.clear_all()

        self.update()

    def set_current_frame(self, frame):
        """Update timeline."""

        self.current_frame = frame

        self.sketch.set_frame(frame)

    def paintGL(self):
        """Render current frame.

        Rendering Pipeline

            CPU Image
                │
                ▼
            GL Texture
                │
                ▼
            Fragment Shader
                │
                ▼
            Fullscreen Quad
                │
                ▼
            Screen
        """

        # Clear framebuffer.
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Nothing to draw.
        if self.numpy_frame is None:
            return

        self.texture.upload(self.numpy_frame)

        # Calculate display rectangle.
        self.update_display_rect()

        # Bind texture.
        self.texture.bind(0)

        if self.use_ocio:
            self.active_shader = self.ocio_shader
        else:
            self.active_shader = self.shader

        # Use texture shader.
        self.active_shader.bind()

        dpr = self.devicePixelRatioF()

        viewport_width = int(self.width() * dpr)
        viewport_height = int(self.height() * dpr)

        # Physical OpenGL viewport size.
        self.active_shader.set_uniform_vec2(
            "viewportSize",
            float(viewport_width),
            float(viewport_height),
        )

        # Fitted image rectangle.
        self.active_shader.set_uniform_vec4(
            "displayRect",
            (
                float(self.display_rect.left()),
                float(self.display_rect.top()),
                float(self.display_rect.width()),
                float(self.display_rect.height()),
            ),
        )

        # Texture unit.
        self.active_shader.set_uniform_int("imageTexture", 0)

        if self.display_parameter:
            self.active_shader.set_uniform_float(
                self.display_parameter.control, self.display_parameter.value
            )

            if self.display_parameter.is_color:
                self.active_shader.set_uniform_vec3(
                    self.display_parameter.color_control, *self.display_parameter.color
                )

        if self.style_parameter:
            self.active_shader.set_uniform_float(
                self.style_parameter.control, self.style_parameter.value
            )

        if self.filter_parameter:
            self.active_shader.set_uniform_vec2(
                "uTexelSize", 1.0 / self.image_width, 1.0 / self.image_height
            )

            self.active_shader.set_uniform_vec2(
                "uResolution",
                float(self.image_width),
                float(self.image_height),
            )

            self.active_shader.set_uniform_float(
                self.filter_parameter.control, self.filter_parameter.value
            )

        # Draw fullscreen quad.
        self.quad.draw()

        # Release shader.
        self.active_shader.release()

        # Release texture.
        self.texture.release()

        # Draw overlays.
        self.draw_overlay()

    def update_display_rect(self):
        """Calculate fitted display rectangle."""

        if self.numpy_frame is None:
            return

        # Device scale.
        dpr = self.devicePixelRatioF()

        viewport_width = int(self.width() * dpr)
        viewport_height = int(self.height() * dpr)

        # Image aspect.
        image_aspect = self.image_width / self.image_height

        viewport_aspect = viewport_width / viewport_height

        # Fit image.
        if image_aspect > viewport_aspect:
            draw_width = viewport_width
            draw_height = int(draw_width / image_aspect)
        else:
            draw_height = viewport_height
            draw_width = int(draw_height * image_aspect)

        # Center image.
        x = int((viewport_width - draw_width) / 2)
        y = int((viewport_height - draw_height) / 2)

        # Logical coordinates.
        self.display_rect = QtCore.QRect(
            int(x / dpr), int(y / dpr), int(draw_width / dpr), int(draw_height / dpr)
        )

    def fit_to_window(self):
        """Fit image inside viewer."""

        self.fit_mode = True
        self.zoom = 1.0

        self.pan = QtCore.QPointF()

        self.update()

    def set_actual_size(self):
        """Display image at 100%."""

        self.fit_mode = False
        self.zoom = 1.0

        self.pan = QtCore.QPointF()

        self.update()

    def set_zoom(self, zoom):
        """Set viewer zoom.

        Args:
            zoom (float):
                Zoom factor.
        """

        self.fit_mode = False

        self.zoom = max(0.05, min(zoom, 32.0))

        self.update()

    def zoom_in(self):
        """Increase zoom."""

        self.set_zoom(self.zoom * 1.25)

    def zoom_out(self):
        """Decrease zoom."""

        self.set_zoom(self.zoom / 1.25)

    def set_pan(self, x, y):
        """Move camera.

        Args:
            x (float):
                Horizontal offset.

            y (float):
                Vertical offset.
        """

        self.pan = QtCore.QPointF(x, y)

        self.update()

    def reset_view(self):
        """Reset camera."""

        self.zoom = 1.0

        self.pan = QtCore.QPointF()

        self.fit_mode = True

        self.update()

    def wheelEvent(self, event):
        """Mouse wheel zoom."""

        delta = event.angleDelta().y()

        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def _mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self._last_pan_pos = event.position()
            return

        super().mousePressEvent(event)

    def _mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.MiddleButton:
            delta = event.position() - self._last_pan_pos
            self._last_pan_pos = event.position()

            self.pan += QtCore.QPointF(delta.x(), -delta.y())
            self.update()
            return

        super().mouseMoveEvent(event)

    def _mousePressEvent(self, event):
        if not self.sketch.enabled:
            return

        point = self.widget_to_image_point(event.position().toPoint())

        self.sketch.mousePressEvent(point)

        self.update()

    def mousePressEvent(self, event):
        if not self.sketch.enabled:
            return

        point = self.widget_to_image_point(event.position().toPoint())

        self.sketch.mousePressEvent(point)

        self.update()

    def mouseMoveEvent(self, event):
        if not self.sketch.enabled:
            return

        if not (event.buttons() & QtCore.Qt.LeftButton):
            return

        point = self.widget_to_image_point(event.position().toPoint())

        self.sketch.mouseMoveEvent(point)

        self.update()

    def mouseReleaseEvent(self, event):

        if not self.sketch.enabled:
            return

        point = self.widget_to_image_point(event.position().toPoint())

        self.sketch.mouseReleaseEvent(point)

        self.update()

    def undo_strokes(self):
        """
        Undo current frame annotation.
        """

        self.sketch.undo()

        self.update()

    def clear_strokes(self):
        """
        clear current frame annotation.
        """

        self.sketch.clear_all()

        self.update()

    def draw_overlay(self):
        """
        Draw all overlays.

        This method handles:
            - Text overlays
            - Image overlays
            - Overlay antialiasing
            - Overlay positioning
        """

        # Create painter
        painter = QtGui.QPainter(self)

        # Enable render quality
        # painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        # painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        # painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        # Draw pencil annotations
        self.sketch.draw(
            painter, point_converter=self.image_to_widget_point, rect=self.display_rect
        )

        painter.end()

    def set_overlay_options(self, watermarks):
        self.sketch.set_overlays(watermarks)
        self.update()

    def set_overlay_option(self, checked, key, position, context):
        self.sketch.set_overlay(checked, key, position, context)
        self.update()

    def set_sketch_enabled(self, tool, enabled, font):
        """
        Enable or disable pencil tool.

        Args:
            enabled (bool): Pencil tool state.
        """

        if not self.current_frame:
            return

        self.sketch.set_tool(tool)
        self.sketch.set_enabled(enabled)

        self.sketch.set_image_size(self.image_width, self.image_height)
        self.sketch.set_eraser_radius(10)
        self.sketch.set_txt_font(font)

    def widget_to_image_point(self, point):
        """
        Convert widget position to normalized image space.
        """

        rect = self.display_rect

        x = (point.x() - rect.left()) / float(rect.width())
        y = (point.y() - rect.top()) / float(rect.height())

        x = max(0.0, min(1.0, x))
        y = max(0.0, min(1.0, y))

        return (x, y)

    def image_to_widget_point(self, point):
        """
        Convert normalized image space to widget coordinates.
        """

        rect = self.display_rect

        x = rect.left() + (point[0] * rect.width())
        y = rect.top() + (point[1] * rect.height())

        return QtCore.QPointF(x, y)

    def render_current_frame(self):
        """
        Render source frame with annotations.

        Returns:
            QImage
        """

        if self.numpy_frame is None:
            return None

        # Convert AVFrame -> RGB NumPy image.
        frame = self.numpy_frame.to_ndarray(format="rgb24")
        frame = numpy.ascontiguousarray(frame)

        height, width, channels = frame.shape
        frame = numpy.ascontiguousarray(frame)

        if channels == 4:
            image = QtGui.QImage(
                frame.data, width, height, width * 4, QtGui.QImage.Format_RGBA8888
            ).copy()
        else:
            image = QtGui.QImage(
                frame.data,
                width,
                height,
                width * 3,
                QtGui.QImage.Format_RGB888,
            ).copy()

        painter = QtGui.QPainter(image)
        self.sketch.set_frame(self.current_frame)

        image_rect = QtCore.QRect(0, 0, width, height)
        self.sketch.draw(
            painter,
            point_converter=lambda point: QtCore.QPointF(
                point[0] * width,
                point[1] * height,
            ),
            rect=image_rect,
        )

        painter.end()

        return image

    def save_frame(self, filepath, post_process=False):
        image = self.render_current_frame()

        if image:
            utils.makedirs(filepath)
            image.save(filepath)
            LOGGER.info(f"Succeed, render to {filepath}")

            if post_process:
                self.render_finished.emit(filepath)
        else:
            LOGGER.error(f"Failure render to {filepath}")

            if post_process:
                self.render_finished.emit(None)

    def set_ocio(self, processor):
        """Update the active OCIO display transform."""

        self.ocio_processor = processor

        # Rebuild GPU shader if OpenGL already exists.
        self.build_ocio_shader()

        self.update()

    def build_ocio_shader(self):
        """Build GPU OCIO shader."""

        # if not self.ocio_processor:
        #     return

        self.ocio_shader = OCIOShader(None)
        self.ocio_shader.build(self.ocio_processor)

        self.ocio_shader.release()

        self.use_ocio = self.ocio_processor.enabled

    def display_changed(self, parameter):
        self.display_parameter = parameter
        self.update()

    def style_changed(self, parameter):
        self.style_parameter = parameter
        self.update()

    def filter_changed(self, parameter):
        self.filter_parameter = parameter
        self.update()


if __name__ == "__main__":
    pass
