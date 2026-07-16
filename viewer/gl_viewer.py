"""
Viewline OpenGL Viewer

Modern OpenGL viewer used for displaying movie frames.

Responsibilities
----------------
* Create OpenGL context.
* Initialize shaders.
* Initialize textures.
* Initialize fullscreen quad.
* Receive decoded frames.
* Render textures.

Rendering Pipeline
------------------

MovieReader
      │
      ▼
MoviePlayer
      │
      ▼
GLTexture
      │
      ▼
GLShader
      │
      ▼
FullscreenQuad
      │
      ▼
QOpenGLWidget

Notes
-----
Rendering is entirely GPU based.

No glDrawPixels() is used.
"""

from __future__ import annotations

import numpy

from OpenGL import GL

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtOpenGLWidgets
from PySide6 import QtWidgets

from viewline import utils
from viewline import logger
from viewline import constants

from .fullscreen_quad import FullscreenQuad
from .gl_shader import GLShader
from .gl_texture import GLTexture
from .ocio_shader import OCIOShader

from viewline.widgets.annotations import Sketch


from viewline.ocio import OCIOProcessor

LOGGER = logger.getLogger(__name__)


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

        # self.ocio_processor = OCIOProcessor(config_path="D:/works/developments/devkit/ocio/studio-config-v4.0.0_aces-v2.0_ocio-v2.5.ocio")
        self.ocio_processor = None

        # self.ocio_processor.set_color_space("ACEScg")
        # self.ocio_processor.set_display("sRGB - Display")
        # self.ocio_processor.set_view("ACES 2.0 - SDR 100 nits (Rec.709)")

        # OpenGL resources.

        self.texture = None
        self.shader = None
        self.quad = None
        self.ocio_shader = None  # GPU OCIO shader
        self.use_ocio = False

        # Current image.

        self.frame = None

        # Image size.
        self.image_width = 0
        self.image_height = 0

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
        self.annotations = Sketch()

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
        self.frame = frame

        if frame is None:
            return

        # Image size.
        self.image_width = frame.width
        self.image_height = frame.height

        # Texture upload happens inside paintGL().
        self.update()

    def clear(self):
        """Clear viewer."""

        self.frame = None

        # self.texture.clear()

        self.annotations.clear_all()

        self.update()

    def set_current_frame(self, frame):
        """Update timeline."""

        self.current_frame = frame

        self.annotations.set_frame(frame)

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
        if self.frame is None:
            return

        # Upload image to GPU texture.
        # Future:
        #     Upload only when frame changes.

        self.texture.upload(self.frame)

        # Calculate display rectangle.
        self.update_display_rect()

        # Bind texture.
        self.texture.bind(0)

        # self.use_ocio = False

        if self.use_ocio:
            self.active_shader = self.ocio_shader
        else:
            self.active_shader = self.shader

        # Use texture shader.
        self.active_shader.bind()

        # Texture unit.
        self.active_shader.set_uniform_int("imageTexture", 0)

        # Viewport size.
        self.active_shader.set_uniform_vec2(
            "viewportSize", float(self.width()), float(self.height())
        )

        # Image size.
        self.active_shader.set_uniform_vec2("imageSize", self.image_width, self.image_height)

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

        # Display rectangle.
        self.active_shader.set_uniform_vec4(
            "displayRect",
            (
                self.display_rect.left(),
                self.display_rect.top(),
                self.display_rect.width(),
                self.display_rect.height(),
            ),
        )

        # Draw fullscreen quad.
        self.quad.draw()

        # Release shader.
        self.active_shader.release()

        # Release texture.
        self.texture.release()

        # Draw overlays.
        self.draw_overlay()
        # self.set_ocio(None)

    def update_display_rect(self):
        """Calculate fitted display rectangle."""

        if self.frame is None:
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
        if not self.annotations.enabled:
            return

        point = self.widget_to_image_point(event.position().toPoint())

        self.annotations.mousePressEvent(point)

        self.update()

    def mousePressEvent(self, event):
        if not self.annotations.enabled:
            return

        point = self.widget_to_image_point(event.position().toPoint())

        self.annotations.mousePressEvent(point)

        self.update()

    def mouseMoveEvent(self, event):
        if not self.annotations.enabled:
            return

        if not (event.buttons() & QtCore.Qt.LeftButton):
            return

        point = self.widget_to_image_point(event.position().toPoint())

        self.annotations.mouseMoveEvent(point)

        self.update()

    def mouseReleaseEvent(self, event):

        if not self.annotations.enabled:
            return

        point = self.widget_to_image_point(event.position().toPoint())

        self.annotations.mouseReleaseEvent(point)

        self.update()

    def undo_strokes(self):
        """
        Undo current frame annotation.
        """

        self.annotations.undo()

        self.update()

    def clear_strokes(self):
        """
        clear current frame annotation.
        """

        self.annotations.clear_all()

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

        # Draw pencil annotations
        self.annotations.draw(
            painter, point_converter=self.image_to_widget_point, rect=self.display_rect
        )

        painter.end()

    def set_overlay_options(self, watermarks):
        self.annotations.set_overlays(watermarks)
        self.update()

    def set_overlay_option(self, checked, key, position, context):
        self.annotations.set_overlay(checked, key, position, context)
        self.update()

    def set_sketch_enabled(self, tool, enabled, font):
        """
        Enable or disable pencil tool.

        Args:
            enabled (bool): Pencil tool state.
        """

        if not self.current_frame:
            return

        self.annotations.set_tool(tool)
        self.annotations.set_enabled(enabled)

        self.annotations.set_image_size(self.image_width, self.image_height)
        self.annotations.set_eraser_radius(10)

        self.annotations.set_txt_font(font)

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

        if self.frame is None:
            return None

        # Convert AVFrame -> RGB NumPy image.
        frame = self.frame.to_ndarray(format="rgb24")
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

        self.annotations.set_frame(self.current_frame)

        image_rect = QtCore.QRect(0, 0, width, height)

        self.annotations.draw(
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
        # if self.context() is not None:
        self.build_ocio_shader()

        self.update()

    def build_ocio_shader(self):
        """Build GPU OCIO shader."""

        # if self.ocio_processor is None:
        #    self.use_ocio = False
        #    self.ocio_shader = None
        #    return

        # ocio_processor = OCIOProcessor(config_path="D:/works/developments/devkit/ocio/studio-config-v4.0.0_aces-v2.0_ocio-v2.5.ocio")
        # ocio_processor.set_color_space("sRGB - Display")
        # ocio_processor.set_display("sRGB - Display")
        # ocio_processor.set_view("ACES 2.0 - SDR 100 nits (Rec.709)")

        ocio_processor = self.ocio_processor

        self.ocio_shader = OCIOShader(None)
        self.ocio_shader.build(ocio_processor)

        self.ocio_shader.release()

        self.use_ocio = True

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
