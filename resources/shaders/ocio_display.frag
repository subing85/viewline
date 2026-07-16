#version 330 core

in vec2 uv;

out vec4 FragColor;

uniform sampler2D imageTexture;

void main()
{
    vec4 color = texture(imageTexture, uv);

    FragColor = color;
}