"""
OpenGL Texture

Lightweight wrapper around an OpenGL 2D texture used by the
Viewline GPU rendering pipeline.

Responsibilities:
    * Create an OpenGL texture.
    * Destroy GPU resources.
    * Upload image data.
    * Bind and release textures.
    * Resize automatically when image dimensions change.

Notes:
    This class does not perform any image processing or color
    management. It simply transfers decoded image data into GPU
    memory.

Typical Usage:

    texture = GLTexture()

    texture.create()

    texture.upload(
        width,
        height,
        image,
    )

    texture.bind()

    ...
"""

import av
import numpy

from OpenGL import GL


class GLTexture(object):
    """OpenGL 2D texture."""

    def __init__(self):
        """Initialize texture."""

        # OpenGL texture identifier.
        self.texture = 0

        # Texture size.
        self.width = 0
        self.height = 0

        # Internal pixel format.
        self.internal_format = GL.GL_RGB8

        # Source pixel format.
        self.pixel_format = GL.GL_RGB

        # Pixel type.
        self.pixel_type = GL.GL_UNSIGNED_BYTE

    def initialize(self):

        self.texture = GL.glGenTextures(1)

        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)

        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def create(self):
        """Create the OpenGL texture."""

        if self.texture:
            return

        self.texture = GL.glGenTextures(1)

        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)

        # Filtering
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        # Wrapping
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def destroy(self):
        """Release GPU texture."""

        if not self.texture:
            return

        GL.glDeleteTextures([self.texture])

        self.texture = 0

        self.width = 0
        self.height = 0

    def upload(self, image):
        """Upload image pixels.

        Args:
            width (int):
                Image width.

            height (int):
                Image height.

            pixels (numpy.ndarray):
                RGB image data.
        """

        if not self.texture:
            self.create()

        if isinstance(image, av.VideoFrame):
            image = image.to_ndarray(format="rgb24")

        image = numpy.ascontiguousarray(image)

        height, width = image.shape[:2]

        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)

        # Allocate storage only when size changes.
        if width != self.width or height != self.height:

            self.width = width
            self.height = height

            GL.glTexImage2D(
                GL.GL_TEXTURE_2D,
                0,
                self.internal_format,
                width,
                height,
                0,
                self.pixel_format,
                self.pixel_type,
                None,
            )

        # Upload pixels.
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)

        GL.glTexSubImage2D(
            GL.GL_TEXTURE_2D,
            0,
            0,
            0,
            width,
            height,
            self.pixel_format,
            self.pixel_type,
            image,
        )

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def bind(self, unit=0):
        """Bind texture.

        Args:
            unit (int):
                Texture unit.
        """

        GL.glActiveTexture(GL.GL_TEXTURE0 + unit)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)

    def release(self):
        """Unbind texture."""

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)


if __name__ == "__main__":
    pass
