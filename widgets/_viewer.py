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

    render_finished = QtCore.Signal(str)

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
        self.image_width = None
        self.image_height = None

        self.displaySettings = None

        self.set_samples(value=constants.VIEWER_SAMPLES_RATE)

        self.sketch = Sketch()

    def set_display_settings(self, display_settings):
        self.displaySettings = display_settings

    def set_samples(self, value=8):
        """
        0 : Disabled
        2: Low quality
        4: Good
        8: Very good (recommended)
        16: Highest (hardware dependent)
        """

        surfaceFormat = QtGui.QSurfaceFormat()
        surfaceFormat.setSamples(value)
        self.setFormat(surfaceFormat)

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
        self.sketch.set_frame(frame)

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

        # Clear annotations
        self.sketch.clear_all()

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

        # Draw overlays by position
        # for position in self.overlay_options:
        #     self.draw_overlay_position(painter, rect, position)

        # Draw pencil annotations
        self.sketch.draw(
            painter, point_converter=self.image_to_widget_point, rect=self.display_rect
        )

        painter.end()

    def set_overlay_options(self, watermarks):

        import json

        print(json.dumps(watermarks, indent=4))

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

    def render_current_frame(self):
        """
        Render source frame with annotations.

        Returns:
            QImage
        """

        if self.frame is None:
            return None

        frame = self.frame.copy()

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
