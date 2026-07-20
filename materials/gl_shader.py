"""
OpenGL Shader

Generic GLSL shader wrapper used by the Viewline GPU rendering
pipeline.

Responsibilities:
    * Compile GLSL vertex shaders.
    * Compile GLSL fragment shaders.
    * Link shader programs.
    * Report compile and link errors.
    * Bind and release shader programs.
    * Set shader uniforms.

Notes:
    This class is renderer-independent and may be reused by
    texture rendering, OCIO display transforms, annotations,
    overlays, and future GPU effects.
"""

from OpenGL import GL

from viewline import resources


class GLShader(object):
    """OpenGL shader program."""

    def __init__(self):
        """Initialize shader."""

        # OpenGL program object.
        self.program = 0

        # Compiled shader objects.
        self.vertex_shader = 0
        self.fragment_shader = 0

    def initialize(self, name="display"):
        """Load shader source files.

        Args:
            vertex_path (str):
                Vertex shader file.

            fragment_path (str):
                Fragment shader file.
        """

        vertex_source, fragment_source = resources.readShader(name)

        self.compile(vertex_source, fragment_source)

    def compile(self, vertex_source, fragment_source):
        """Compile and link a shader program.

        Args:
            vertex_source (str):
                GLSL vertex shader source.

            fragment_source (str):
                GLSL fragment shader source.
        """

        self.destroy()

        # Vertex shader
        self.vertex_shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)

        GL.glShaderSource(self.vertex_shader, vertex_source)
        GL.glCompileShader(self.vertex_shader)

        self._check_shader(self.vertex_shader, "Vertex Shader")

        # Fragment shader
        self.fragment_shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)

        GL.glShaderSource(self.fragment_shader, fragment_source)
        GL.glCompileShader(self.fragment_shader)

        self._check_shader(self.fragment_shader, "Fragment Shader")

        # Link program
        self.program = GL.glCreateProgram()

        GL.glAttachShader(self.program, self.vertex_shader)
        GL.glAttachShader(self.program, self.fragment_shader)
        GL.glLinkProgram(self.program)

        self._check_program()

    def destroy(self):
        """Release GPU shader resources."""

        if self.program:
            GL.glDeleteProgram(self.program)

        if self.vertex_shader:
            GL.glDeleteShader(self.vertex_shader)

        if self.fragment_shader:
            GL.glDeleteShader(self.fragment_shader)

        self.program = 0
        self.vertex_shader = 0
        self.fragment_shader = 0

    def bind(self):
        """Bind shader program."""

        GL.glUseProgram(self.program)

    def release(self):
        """Unbind shader program."""

        GL.glUseProgram(0)

    def uniform_location(self, name):
        """Return uniform location."""

        return GL.glGetUniformLocation(self.program, name)

    def set_uniform_int(self, name, value):
        """Set integer uniform."""

        location = self.uniform_location(name)

        GL.glUniform1i(location, value)

    def set_uniform_float(self, name, value):
        """Set float uniform."""

        location = self.uniform_location(name)

        GL.glUniform1f(location, value)

    def set_uniform_vec2(self, name, x, y):
        """Set vec2 uniform."""

        location = self.uniform_location(name)

        GL.glUniform2f(location, x, y)

    def set_uniform_vec3(self, name, x, y, z):
        """Set vec3 uniform."""

        location = self.uniform_location(name)

        GL.glUniform3f(location, x, y, z)

    def set_uniform_vec4(self, name, value):
        """Set vec4 uniform."""

        location = GL.glGetUniformLocation(self.program, name)

        GL.glUniform4f(
            location,
            float(value[0]),
            float(value[1]),
            float(value[2]),
            float(value[3]),
        )

    def set_uniform_mat4(self, name, matrix):
        """Set mat4 uniform."""

        location = self.uniform_location(name)

        GL.glUniformMatrix4fv(location, 1, False, matrix)

    def _check_shader(self, shader, label):
        """Validate shader compilation."""

        status = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)

        if status:
            return

        log = GL.glGetShaderInfoLog(shader)

        raise RuntimeError(f"{label} Compile Error\n\n{log.decode()}")

    def _check_program(self):
        """Validate program linking."""

        status = GL.glGetProgramiv(self.program, GL.GL_LINK_STATUS)

        if status:
            return

        log = GL.glGetProgramInfoLog(self.program)

        raise RuntimeError(f"Shader Link Error\n\n{log.decode()}")


if __name__ == "__main__":
    pass
