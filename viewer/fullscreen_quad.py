"""
Fullscreen Quad

Renders a fullscreen rectangle for texture display.

Responsibilities:
    * Create OpenGL vertex buffers.
    * Upload fullscreen quad geometry.
    * Draw the quad.
    * Release GPU resources.

Architecture:

        Texture
           │
           ▼
    Fullscreen Quad
           │
           ▼
       Fragment Shader
           │
           ▼
         Screen
"""

import numpy
import ctypes

from OpenGL import GL


class FullscreenQuad(object):
    """Fullscreen rendering quad."""

    def __init__(self):
        """Initialize quad."""

        self.vao = 0
        self.vbo = 0

    def initialize(self):
        """Create OpenGL buffers."""

        # position.xy
        # texcoord.xy

        vertices = numpy.array(
            [
                # x     y      u     v
                -1.0,
                -1.0,
                0.0,
                1.0,
                1.0,
                -1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                0.0,
                -1.0,
                -1.0,
                0.0,
                1.0,
                1.0,
                1.0,
                1.0,
                0.0,
                -1.0,
                1.0,
                0.0,
                0.0,
            ],
            dtype=numpy.float32,
        )

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        GL.glBindVertexArray(self.vao)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)

        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)
        stride = 4 * 4

        # Position
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, False, stride, ctypes.c_void_p(0))

        # UV
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, False, stride, ctypes.c_void_p(8))

        GL.glBindVertexArray(0)

    def draw(self):
        """Render fullscreen quad."""

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
        GL.glBindVertexArray(0)

    def destroy(self):
        """Release GPU resources."""

        if self.vbo:
            GL.glDeleteBuffers(1, [self.vbo])

        if self.vao:
            GL.glDeleteVertexArrays(1, [self.vao])

        self.vbo = 0
        self.vao = 0


if __name__ == "__main__":
    pass
