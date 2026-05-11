import numpy as np

from PySide6 import QtWidgets
from PySide6 import QtOpenGLWidgets

from OpenGL.GL import *


class ViewerWidget(QtOpenGLWidgets.QOpenGLWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding
        )

        self.setSizePolicy(sizePolicy)

        self.frame = None

    def set_frame(self, frame):

        self.frame = frame

        self.update()

    def initializeGL(self):

        glClearColor(0.1, 0.1, 0.1, 1.0)

    def resizeGL(self, width, height):

        glViewport(0, 0, width, height)

    def paintGL(self):

        glClear(GL_COLOR_BUFFER_BIT)

        if self.frame is None:
            return

        image = np.flipud(self.frame)

        image = np.ascontiguousarray(image)

        image_height, image_width, channels = image.shape

        # viewport_width = self.width()
        # viewport_height = self.height()

        dpr = self.devicePixelRatioF()

        viewport_width = int(self.width() * dpr)
        viewport_height = int(self.height() * dpr)

        image_aspect = image_width / image_height

        viewport_aspect = viewport_width / viewport_height

        # --------------------------------------------------
        # Fit Image
        # --------------------------------------------------

        if image_aspect > viewport_aspect:
            draw_width = viewport_width
            draw_height = int(draw_width / image_aspect)

        else:
            draw_height = viewport_height
            draw_width = int(draw_height * image_aspect)

        # --------------------------------------------------
        # Compute fit scale
        # --------------------------------------------------

        # scale_x = viewport_width / image_width
        # scale_y = viewport_height / image_height

        # scale = min(scale_x, scale_y)

        # draw_width = int(image_width * scale)
        # draw_height = int(image_height * scale)

        # --------------------------------------------------
        # Center image
        # --------------------------------------------------

        x = int((viewport_width - draw_width) / 2)
        y = int((viewport_height - draw_height) / 2)

        # print("\n")
        # print("Image", image_width, image_height)
        # print("viewport", viewport_width, viewport_height)
        # print("draw", draw_width, draw_height)
        # print("final", x, y)
        # print("\n")

        # --------------------------------------------------
        # Configure 2D projection
        # --------------------------------------------------

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glOrtho(0, viewport_width, 0, viewport_height, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # --------------------------------------------------
        # Draw image
        # --------------------------------------------------

        glRasterPos2i(x, y)

        glPixelZoom(draw_width / image_width, draw_height / image_height)

        glDrawPixels(image_width, image_height, GL_RGB, GL_UNSIGNED_BYTE, image)

        # Reset zoom
        glPixelZoom(1, 1)


"""

class ViewerWidget(QtOpenGLWidgets.QOpenGLWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.frame = None

    def set_frame(self, frame):

        self.frame = frame

        self.update()

    def initializeGL(self):

        glClearColor(0.1, 0.1, 0.1, 1.0)

    def resizeGL(self, width, height):

        glViewport(0, 0, width, height)

    def paintGL(self):

        glClear(GL_COLOR_BUFFER_BIT)

        if self.frame is None:
            return

        image = np.flipud(self.frame)

        image = np.ascontiguousarray(image)

        height, width, channels = image.shape

        glRasterPos2f(-1, -1)

        glDrawPixels(
            width,
            height,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            image
        )

"""
