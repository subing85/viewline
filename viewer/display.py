from __future__ import absolute_import


class ParametereSetting(object):
    """Single display setting with value and range information."""

    def __init__(
        self, name, label, control, minimum, maximum, default, decimals=2, color_control=None
    ):
        self.name = name
        self.label = label
        self.control = control
        self.color_control = color_control

        self.minimum = float(minimum)
        self.maximum = float(maximum)
        self.default = float(default)
        self.decimals = int(decimals)

        self._value = self.default

        if self.color_control:
            self.color = (1.0, 0.0, 0.0)
            self.is_color = True
        else:
            self.color = None
            self.is_color = False

    @property
    def value(self):
        """Return the current value."""
        return self._value

    @value.setter
    def value(self, value):
        """Set and clamp the current value."""
        self._value = max(self.minimum, min(float(value), self.maximum))

    def reset(self):
        """Reset the setting to its default value."""
        self.value = self.default

    def slider_range(self):
        """Return the integer range required by QSlider."""
        scale = 10**self.decimals

        return (int(self.minimum * scale), int(self.maximum * scale))

    def slider_value(self):
        """Return the current value converted to a QSlider integer."""
        scale = 10**self.decimals

        return int(round(self.value * scale))

    def value_from_slider(self, value):
        """Convert a QSlider integer value to the setting value."""
        scale = 10**self.decimals

        return float(value) / scale

    def set_color(self, color):
        self.color = color


class DisplaySettings(object):
    """Display settings for the Viewline viewer."""

    def __init__(self):

        self.exposure = ParametereSetting(
            name="exposure",
            label="Exposure",
            control="uExposure",
            minimum=-10.0,
            maximum=10.0,
            default=0.0,
            decimals=2,
        )

        self.gamma = ParametereSetting(
            name="gamma",
            label="Gamma",
            control="uGamma",
            minimum=0.1,
            maximum=5.0,
            default=1.0,
            decimals=2,
        )

        self.brightness = ParametereSetting(
            name="brightness",
            label="Brightness",
            control="uExposure",
            minimum=-1.0,
            maximum=1.0,
            default=0.0,
            decimals=2,
        )

        self.contrast = ParametereSetting(
            name="contrast",
            label="Contrast",
            control="uContrast",
            minimum=0.0,
            maximum=3.0,
            default=1.0,
            decimals=2,
        )

        self.saturation = ParametereSetting(
            name="saturation",
            label="Saturation",
            control="uSaturation",
            minimum=0.0,
            maximum=2.0,
            default=1.0,
            decimals=2,
        )

        self.hue = ParametereSetting(
            name="hue",
            label="Hue",
            control="uHue",
            minimum=-180.0,
            maximum=180.0,
            default=0.0,
            decimals=1,
        )

        self.gain = ParametereSetting(
            name="gain",
            label="Gain",
            control="uGain",
            minimum=0.0,
            maximum=4.0,
            default=1.0,
            decimals=2,
        )

        self.offset = ParametereSetting(
            name="offset",
            label="Offset",
            control="uOffset",
            minimum=-1.0,
            maximum=1.0,
            default=0.0,
            decimals=2,
        )

        self.overlay_opacity = ParametereSetting(
            name="overlay",
            label="Overlay",
            control="uOverlayOpacity",
            color_control="uOverlayColor",
            minimum=0.0,
            maximum=1.0,
            default=0.0,
            decimals=2,
        )

    def parameters(self):
        result = [
            self.exposure,
            self.gamma,
            self.brightness,
            self.contrast,
            self.saturation,
            self.hue,
            self.gain,
            self.offset,
            self.overlay_opacity,
        ]

        return result


class StyleSettings(object):
    """Style settings for the Viewline viewer."""

    def __init__(self):

        self.sepia = ParametereSetting(
            name="sepia",
            label="Sepia",
            control="uSepia",
            minimum=-0.0,
            maximum=1.0,
            default=0.0,
            decimals=2,
        )

        self.negate = ParametereSetting(
            name="negate",
            label="Negate Colors",
            control="uNegate",
            minimum=0.0,
            maximum=1.0,
            default=0.0,
            decimals=2,
        )

        self.posterize = ParametereSetting(
            name="posterize",
            label="Posterize",
            control="uPosterize",
            minimum=0.0,
            maximum=32.0,
            default=0.0,
            decimals=0,
        )

        self.gradient = ParametereSetting(
            name="gradient",
            label="Gradient",
            control="uGradient",
            minimum=0.0,
            maximum=1.0,
            default=0.0,
            decimals=2,
        )

        self.cartoon = ParametereSetting(
            name="cartoon",
            label="Cartoon",
            control="uCartoon",
            minimum=0.0,
            maximum=1.0,
            default=0.0,
            decimals=2,
        )

    def parameters(self):
        return [
            self.sepia,
            self.negate,
            self.posterize,
            self.gradient,
            self.cartoon,
        ]


class FilterSettings(object):
    """Filter settings for the Viewline viewer."""

    def __init__(self):
        self.sharpen = ParametereSetting(
            name="sharpen",
            label="Sharpen",
            control="uSharpen",
            minimum=0.0,
            maximum=10.0,
            default=0.0,
            decimals=2,
        )

        self.blur = ParametereSetting(
            name="blur",
            label="Blur",
            control="uBlur",
            minimum=0.0,
            maximum=1.0,
            default=0.0,
            decimals=2,
        )

        self.motion_blur = ParametereSetting(
            name="motion_blur",
            label="Motion Blur",
            control="uMotionBlur",
            minimum=0.0,
            maximum=1.0,
            default=0.0,
            decimals=2,
        )

        self.noise = ParametereSetting(
            name="noise",
            label="Noise",
            control="uNoise",
            minimum=0.0,
            maximum=1.0,
            default=0.0,
            decimals=2,
        )

        self.denoiser = ParametereSetting(
            name="denoiser",
            label="Denoiser",
            control="uDenoiser",
            minimum=0.0,
            maximum=1.0,
            default=0.0,
            decimals=2,
        )

    def parameters(self):
        return [
            self.sharpen,
            self.blur,
            self.motion_blur,
            self.noise,
            self.denoiser,
        ]


if __name__ == "__main__":
    pass
