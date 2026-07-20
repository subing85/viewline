#version 330 core

layout(location = 0) in vec2 position;
layout(location = 1) in vec2 texcoord;

out vec2 uv;

uniform vec2 viewportSize;
uniform vec4 displayRect;

void main()
{
    // Convert [-1, 1] to [0, 1].
    vec2 localPosition = position * 0.5 + 0.5;

    // Position inside the fitted display rectangle.
    vec2 pixelPosition = displayRect.xy + localPosition * displayRect.zw;

    // Convert to NDC.
    vec2 ndc = pixelPosition / viewportSize * 2.0 - 1.0;
    gl_Position = vec4(ndc, 0.0, 1.0);

    uv = texcoord;
}