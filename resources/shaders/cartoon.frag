#version 330 core

in vec2 uv;

out vec4 FragColor;

uniform sampler2D imageTexture;

uniform vec2 uTexelSize;
uniform float uCartoon;

void main()
{
    vec3 color = texture(imageTexture, uv).rgb;

    if (uCartoon > 0.0)
    {
        // -------------------------------------------------
        // Color quantization
        // -------------------------------------------------

        float levels = mix(12.0, 3.0, uCartoon);
        vec3 cartoonColor = floor(color * levels + 0.5) / levels;

        // -------------------------------------------------
        // Sobel edge detection
        // -------------------------------------------------

        float tl = dot(
            texture(imageTexture, uv + vec2(-uTexelSize.x,uTexelSize.y)).rgb,
            vec3(0.299, 0.587, 0.114)
        );

        float tc = dot(
            texture(imageTexture, uv + vec2(0.0, uTexelSize.y)).rgb,
            vec3(0.299, 0.587, 0.114)
        );

        float tr = dot(
            texture(imageTexture, uv + vec2(uTexelSize.x, uTexelSize.y)).rgb,
            vec3(0.299, 0.587, 0.114)
        );

        float ml = dot(
            texture(imageTexture, uv + vec2(-uTexelSize.x, 0.0)).rgb,
            vec3(0.299, 0.587, 0.114)
        );

        float mr = dot(
            texture(imageTexture, uv + vec2(uTexelSize.x, 0.0)).rgb,
            vec3(0.299, 0.587, 0.114)
        );

        float bl = dot(
            texture(imageTexture, uv + vec2(-uTexelSize.x, -uTexelSize.y)).rgb,
            vec3(0.299, 0.587, 0.114)
        );

        float bc = dot(
            texture(imageTexture, uv + vec2(0.0, -uTexelSize.y)).rgb,
            vec3(0.299, 0.587, 0.114)
        );

        float br = dot(
            texture(imageTexture, uv + vec2(uTexelSize.x, -uTexelSize.y)).rgb,
            vec3(0.299, 0.587, 0.114)
        );

        float gx = -tl -2.0 * ml -bl +tr +2.0 * mr +br;
        float gy = -tl -2.0 * tc -tr +bl +2.0 * bc +br;

        float edge = sqrt(gx * gx + gy * gy);

        // Strong black outline.
        edge = smoothstep(0.08, 0.25, edge);
        vec3 cartoon = mix(cartoonColor, vec3(0.0), edge);
        color = mix(color, cartoon, uCartoon);
    }

    FragColor = vec4(color, 1.0);
}