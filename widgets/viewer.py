"""
Copyright (c) 2026, Motion-Craft Technology All rights reserved.
Author: Subin. Gopi (subing85@gmail.com).
Description: Review Player Qt OpenGL media viewer widget module.
WARNING! All changes made in this file will be lost when recompiling source file!

This module contains the main media viewer widget used by the Review Player application.

The viewer widget is responsible for:

    - OpenGL-based image rendering
    - Video frame display
    - Image sequence preview
    - Dynamic fit-to-window scaling
    - Aspect ratio preservation
    - Watermark and overlay rendering
    - Text and image overlays
    - Playback frame display

Main Components:
    ViewerWidget:
        OpenGL-powered media display widget.

Features:
    - OpenGL frame rendering
    - Dynamic viewport resizing
    - Aspect ratio preservation
    - Overlay rendering system
    - Text watermark support
    - Image watermark support
    - Opacity control
    - Font customization
    - Playback frame visualization

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

Rendering Pipeline:
    Media Frame
        ↓
    OpenGL Draw
        ↓
    QPainter Overlay
        ↓
    Watermark Rendering
"""

import numpy

import resources
import constants

from OpenGL import GL

from PySide6 import QtGui
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtOpenGLWidgets

from widgets.styles import Font
from widgets.pixmaps import PathPixmap


class ViewerWidget(QtOpenGLWidgets.QOpenGLWidget):
    """
    OpenGL-based media viewer widget.

    This widget provides the primary media display system for the Review Player application.

    Features:
        - OpenGL rendering
        - Frame display
        - Overlay rendering
        - Watermark support
        - Dynamic scaling
        - Aspect ratio preservation
        - Text overlays
        - Image overlays

    Overlay Support:
        - Text watermarks
        - Logo overlays
        - Dynamic frame display
        - Resolution display
        - Opacity control
    """

    def __init__(self, parent=None):
        """
        Initialize viewer widget.

        Args:
            parent (QtWidgets.QWidget, optional):
                Parent widget.
        """

        super().__init__(parent)

        # Configure expanding size policy
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding
        )

        self.setSizePolicy(sizePolicy)

        # Current media frame
        self.frame = None

        # Current playback frame number
        self.current_frame = None

        # Source image dimensions
        self.image_height = None
        self.image_width = None

        # Overlay storage
        self.overlay_options = {
            "top_left": dict(),
            "top_right": dict(),
            "top_center": dict(),
            "center": dict(),
            "bottom_left": dict(),
            "bottom_right": dict(),
            "bottom_center": dict(),
        }

        # Cached overlay pixmaps
        self.overlay_pixmaps = dict()

    def set_frame(self, frame):
        """
        Set current display frame.

        Args:
            frame (numpy.ndarray):
                Image frame buffer.
        """

        self.frame = frame

        # Refresh OpenGL widget
        self.update()

    def set_current_frame(self, frame):
        """
        Set current playback frame number.

        Args:
            frame (int):
                Current frame number.
        """

        self.current_frame = frame

    def initializeGL(self):
        """
        Initialize OpenGL state.

        Configure default OpenGL clear color.
        """

        GL.glClearColor(0.1, 0.1, 0.1, 1.0)

    def resizeGL(self, width, height):
        """
        Handle OpenGL viewport resize.

        Args:
            width (int):
                Viewport width.

            height (int):
                Viewport height.
        """

        # Update OpenGL viewport
        GL.glViewport(0, 0, width, height)

    def clear(self):
        """
        Clear viewer contents.

        Removes current frame and refreshes display.
        """

        self.frame = None

        # Refresh widget
        self.update()

    def paintGL(self):
        """
        Render OpenGL frame.

        This method handles:
            - Frame rendering
            - Dynamic image scaling
            - Aspect ratio preservation
            - OpenGL viewport drawing
            - Overlay rendering
        """

        # Clear OpenGL buffer
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        if self.frame is None:
            return

        # Flip image vertically for OpenGL
        image = numpy.flipud(self.frame)

        # Ensure contiguous memory layout
        image = numpy.ascontiguousarray(image)

        # Extract image information
        self.image_height, self.image_width, channels = image.shape

        # Device pixel ratio
        dpr = self.devicePixelRatioF()

        # Physical viewport size
        viewport_width = int(self.width() * dpr)
        viewport_height = int(self.height() * dpr)

        # Aspect ratios
        image_aspect = self.image_width / self.image_height
        viewport_aspect = viewport_width / viewport_height

        # Fit image into viewport
        if image_aspect > viewport_aspect:
            draw_width = viewport_width
            draw_height = int(draw_width / image_aspect)
        else:
            draw_height = viewport_height
            draw_width = int(draw_height * image_aspect)

        # Center image inside viewport
        x = int((viewport_width - draw_width) / 2)
        y = int((viewport_height - draw_height) / 2)

        # Configure projection matrix (2D projection)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()

        GL.glOrtho(0, viewport_width, 0, viewport_height, -1, 1)

        # Configure model matrix
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        # Draw image pixels
        GL.glRasterPos2i(x, y)
        GL.glPixelZoom(draw_width / self.image_width, draw_height / self.image_height)

        # OpenGL image format
        gl_format = GL.GL_RGBA if channels == 4 else GL.GL_RGB

        # Render pixels
        GL.glDrawPixels(self.image_width, self.image_height, gl_format, GL.GL_UNSIGNED_BYTE, image)

        # Reset zoom state
        GL.glPixelZoom(1, 1)

        # Convert display rect into logical coordinates
        logical_draw_width = int(draw_width / dpr)
        logical_draw_height = int(draw_height / dpr)

        logical_x = int(x / dpr)
        logical_y = int(y / dpr)

        # Store display rectangle for overlays
        self.display_rect = QtCore.QRect(
            logical_x, logical_y, logical_draw_width, logical_draw_height
        )

        # Draw overlays
        self.draw_overlay()

    def set_overlay_options(self, watermarks):
        """
        Set all overlay options.

        Args:
            watermarks (dict):
                Watermark configuration dictionary.
        """

        for position, values in watermarks.items():
            for context in values:
                self.set_overlay_option(context["checked"], context["code"], position, context)

    def set_overlay_option(self, checked, key, position, context):
        """
        Update a single overlay option.

        Args:
            checked (bool):
                Overlay enabled state.

            key (str):
                Overlay identifier.

            position (str):
                Overlay screen position.

            context (dict):
                Overlay settings.
        """

        # Create position group if missing
        if position not in self.overlay_options:
            self.overlay_options[position] = dict()

        # Create overlay entry if missing
        if key not in self.overlay_options[position]:
            self.overlay_options[position][key] = dict()

        # Store overlay configuration
        self.overlay_options[position][key] = context
        self.overlay_options[position][key]["checked"] = checked

        # Refresh widget
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
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        rect = self.display_rect

        # Draw overlays by position
        for position in self.overlay_options:
            self.draw_overlay_position(painter, rect, position)

        painter.end()

    def draw_overlay_position(self, painter, rect, position):
        """
        Draw overlays for a specific position group.

        Args:
            painter (QtGui.QPainter):
                Painter object.

            rect (QtCore.QRect):
                Display rectangle.

            position (str):
                Overlay position.
        """

        overlays = self.overlay_options.get(position, dict())
        if not overlays:
            return

        metrics = QtGui.QFontMetrics(painter.font())
        margin, spacing = 20, 20

        # Resolve overlay anchor position
        if position == "top_left":
            x = rect.left() + margin
            y = rect.top() + margin  # 40
            align = "left"
        elif position == "top_center":
            x = rect.center().x()
            y = rect.top() + margin  # 40
            align = "center"
        elif position == "top_right":
            x = rect.right() - margin
            y = rect.top() + margin  # 40
            align = "right"
        elif position == "bottom_left":
            x = rect.left() + margin
            y = rect.bottom() - margin  # 40
            align = "left"
        elif position == "bottom_center":
            x = rect.center().x()
            y = rect.bottom() - metrics.descent() - 10
            align = "center"
        elif position == "bottom_right":
            x = rect.right() - margin
            y = rect.bottom() - margin  # 40
            align = "right"
        elif position == "center":
            x = rect.center().x()
            y = rect.center().y()
            align = "center"
        else:
            return

        # Bottom positions render upward
        reverse_vertical = position in ["bottom_left", "bottom_center", "bottom_right"]

        # Draw overlays
        for key, context in overlays.items():
            if not context.get("checked"):
                continue

            typed = context.get("type", "text")

            # Draw image overlay
            if typed == "image":
                pixmap = context["value"]
                scaled = pixmap.scaledToHeight(50, QtCore.Qt.SmoothTransformation)
                draw_x = x

                # Horizontal alignment
                if align == "center":
                    draw_x -= scaled.width() / 2
                elif align == "right":
                    draw_x -= scaled.width()

                # Vertical direction (TOP / BOTTOM DIRECTION)
                if reverse_vertical:
                    draw_y = y - scaled.height()
                else:
                    draw_y = y

                # Set overlay opacity
                opacity = context.get("opacity", 1.0)
                painter.setOpacity(opacity)

                # Draw image
                path = painter.drawPixmap(int(draw_x), int(draw_y), scaled)

                # Reset Opacity
                painter.setOpacity(1.0)

                # Vertical spacing offset
                offset = scaled.height() + 10

                if reverse_vertical:
                    y -= offset
                else:
                    y += offset

            # Draw text overlay
            else:
                # Dynamic overlay text
                if key == "frame":
                    text = f"Frame: {str(self.current_frame).zfill(constants.FRAME_PADDING)}"

                elif key == "resolution":
                    text = f"{self.image_width} x {self.image_height}"
                else:
                    text = (
                        f"{context['label']}: {context['value']}"
                        if context.get("label")
                        else context["value"]
                    )

                # Create font
                font = Font(None, **context["font"])

                # Calculate text bounds
                path = QtGui.QPainterPath()
                path.addText(0, 0, font, text)

                bounds = path.boundingRect()
                text_width = bounds.width()

                draw_x = x

                # Horizontal alignment
                if align == "center":
                    draw_x -= text_width / 2
                elif align == "right":
                    draw_x -= text_width

                # Draw text
                self.draw_overlay_text(painter, draw_x, y, text, context["font"])

                # Vertical spacing
                offset = spacing + context["font"].get("spacing", 0)

                if reverse_vertical:
                    y -= offset
                else:
                    y += offset

    def draw_overlay_text(self, painter, x, y, text, font_data):
        """
        Draw overlay text.

        Args:
            painter (QtGui.QPainter):
                Painter object.

            x (float):
                Draw X position.

            y (float):
                Draw Y position.

            text (str):
                Overlay text.

            font_data (dict):
                Font configuration.

        Returns:
            QtGui.QPainterPath:
                Generated text path.
        """

        # Configure font
        font = Font(None, **font_data)
        painter.setFont(font)

        # Text colors
        fill_color = QtGui.QColor(*font_data.get("fillColor", (255, 255, 255)))
        stroke_color = QtGui.QColor(*font_data.get("strokeColor", (0, 0, 0)))

        stroke_width = font_data.get("stroke", 2)

        # Build text path
        path = QtGui.QPainterPath()
        path.addText(x, y, font, text)

        # Draw text stroke
        if stroke_width > 0:
            pen = QtGui.QPen(stroke_color)
            pen.setWidth(stroke_width)
            painter.strokePath(path, pen)

        # Set text opacity
        opacity = font_data.get("opacity", 1.0)
        painter.setOpacity(opacity)

        # Draw text fill
        painter.fillPath(path, fill_color)

        return path


if __name__ == "__main__":
    pass
