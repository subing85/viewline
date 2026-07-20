from OpenGL import GL


class GLTexture3D:

    def __init__(self):

        self.texture = None

    def initialize(self):

        self.texture = GL.glGenTextures(1)

        GL.glBindTexture(
            GL.GL_TEXTURE_3D,
            self.texture,
        )

        GL.glTexParameteri(
            GL.GL_TEXTURE_3D,
            GL.GL_TEXTURE_MIN_FILTER,
            GL.GL_LINEAR,
        )

        GL.glTexParameteri(
            GL.GL_TEXTURE_3D,
            GL.GL_TEXTURE_MAG_FILTER,
            GL.GL_LINEAR,
        )

        GL.glTexParameteri(
            GL.GL_TEXTURE_3D,
            GL.GL_TEXTURE_WRAP_S,
            GL.GL_CLAMP_TO_EDGE,
        )

        GL.glTexParameteri(
            GL.GL_TEXTURE_3D,
            GL.GL_TEXTURE_WRAP_T,
            GL.GL_CLAMP_TO_EDGE,
        )

        GL.glTexParameteri(
            GL.GL_TEXTURE_3D,
            GL.GL_TEXTURE_WRAP_R,
            GL.GL_CLAMP_TO_EDGE,
        )

        GL.glBindTexture(
            GL.GL_TEXTURE_3D,
            0,
        )

    def upload(self, lut, size):

        GL.glBindTexture(
            GL.GL_TEXTURE_3D,
            self.texture,
        )

        GL.glTexImage3D(
            GL.GL_TEXTURE_3D,
            0,
            GL.GL_RGB32F,
            size,
            size,
            size,
            0,
            GL.GL_RGB,
            GL.GL_FLOAT,
            lut,
        )

        GL.glBindTexture(
            GL.GL_TEXTURE_3D,
            0,
        )

    def bind(self, unit):

        GL.glActiveTexture(GL.GL_TEXTURE0 + unit)

        GL.glBindTexture(
            GL.GL_TEXTURE_3D,
            self.texture,
        )
