#version 330 core

in vec2 uv;

out vec4 FragColor;

uniform sampler2D imageTexture;

// Display controls such as "Exposure", "Gamma", "Brightness", "Contrast",  "Stauration", "Hue", "Gain", "Offset"

uniform float uExposure = 0.0; // Stops (-10 -> +10)
uniform float uGamma = 1.0; // 0.1 -> 5.0
uniform float uBrightness = 0.0; // -1 -> +1
uniform float uContrast = 1.0; // 0 -> 3
uniform float uSaturation = 1.0; // 0 -> 2
uniform float uHue = 0.0; // Degrees (-180 -> +180)
uniform float uGain = 1.0; // 0 -> 4
uniform float uOffset = 0.0; // -1 -> +1
uniform vec3  uOverlayColor = vec3(1.0, 1.0, 1.0);
uniform float uOverlayOpacity = 0.0;


// Style controls such as "Sepia", Negate, Posterize, Gradient, Cartoon

uniform float uSepia = 0.0; // 0.0 -> 1.0
uniform float uNegate = 0.0; // 0.0 -> 1.0
uniform float uPosterize = 0.0; // 0.0 -> 3.2
uniform float uGradient = 0.0; // 0.0 -> 3.2
uniform vec3 uGradientColorA = vec3(1.0, 0.0, 0.0); // Red
uniform vec3 uGradientColorB = vec3(0.0, 0.0, 1.0); // Blue
uniform float uCartoon = 0.0;


// Filter controls such as Sharpen, Blur, Motion blur, Noise, Denoiser

uniform float uBlur = 0.0;
uniform float uMotionBlur = 0.0;

uniform float uSharpen = 0.0;
uniform float uNoise = 0.0;
uniform vec2 uResolution;
uniform float uDenoiser;


//
uniform vec2 uTexelSize;

const vec3 LUMA = vec3(0.2126, 0.7152, 0.0722);

vec3 hueRotate(vec3 color, float angle)
{
    float rad = radians(angle);

    float s = sin(rad);
    float c = cos(rad);

    mat3 m = mat3(
        0.213 + c * 0.787 - s * 0.213,
        0.715 - c * 0.715 - s * 0.715,
        0.072 - c * 0.072 + s * 0.928,

        0.213 - c * 0.213 + s * 0.143,
        0.715 + c * 0.285 + s * 0.140,
        0.072 - c * 0.072 - s * 0.283,

        0.213 - c * 0.213 - s * 0.787,
        0.715 - c * 0.715 + s * 0.715,
        0.072 + c * 0.928 + s * 0.072
    );

    return clamp(m * color, 0.0, 1.0);
}


float random(vec2 seed)
{
    return fract(sin(dot(seed, vec2(12.9898, 78.233))) * 43758.5453);
}



void main()
{
    vec4 color = texture(imageTexture, uv);

    // Display //////////////////////////////////////////////

    // Exposure (photographic stops)
    color.rgb *= pow(2.0, uExposure);

    // Gamma
    // color.rgb = pow(max(color.rgb, 0.001), vec3(1.0 / uGamma));
    // float gamma = max(uGamma, 1.0);
    // color.rgb = pow(max(color.rgb, vec3(0.0)), vec3(1.0 / gamma));

    color.rgb = pow(max(color.rgb, 0.00), vec3(1.0 / uGamma));

    // Brightness
    color.rgb += uBrightness;

    // Contrast
    color.rgb = (color.rgb - 0.5) * uContrast + 0.5;

    // Saturation.
    float luma = dot(color.rgb, LUMA);
    color.rgb = mix(vec3(luma), color.rgb, uSaturation);

    // Hue
    color.rgb = hueRotate(color.rgb, uHue);

    // Gain
    color.rgb *= uGain;

    // Offset
    color.rgb += uOffset;

    // Overlay Color
    //color.rgb = mix(color.rgb, uOverlayColor, uOverlayOpacity);
    // result = original × (1 − opacity) + overlay × opacity

    // Overlay Color
    float opacity = clamp(uOverlayOpacity, 0.0, 1.0);
    color.rgb = mix(color.rgb, uOverlayColor, opacity);

    // Style //////////////////////////////////////////////

    // Sepia //
    vec3 sepiaColor;
    sepiaColor.r = dot(color.rgb, vec3(0.393, 0.769, 0.189));
    sepiaColor.g = dot(color.rgb, vec3(0.349, 0.686, 0.168));
    sepiaColor.b = dot(color.rgb, vec3(0.272, 0.534, 0.131));
    color.rgb = mix(color.rgb, sepiaColor, uSepia);

    // Negate Colors
    float negate = clamp(uNegate, 0.0, 1.0);
    vec3 negative = vec3(1.0) - color.rgb;
    color.rgb = mix(color.rgb, negative, negate);

    // Posterize //
    // uPosterize = 0.0  → Original image
    // uPosterize = 2.0  → Strong posterization
    // uPosterize = 4.0  → Fewer color levels
    // uPosterize = 8.0  → Moderate posterization
    // uPosterize = 16.0 → Subtle posterization
    // uPosterize = 32.0 → Very subtle posterization

    float levels = max(uPosterize, 2.0);

    if (uPosterize > 0.0)
    {
        color.rgb = floor(color.rgb * levels) / levels;
    }


    // Posterize //
    float gradient = clamp(uGradient, 0.0, 1.0);
    float factor = (uv.x + uv.y) * 0.5;

    vec3 gradientColor = mix(uGradientColorA, uGradientColorB, factor);
    color.rgb = mix(color.rgb, gradientColor, gradient);


    // Cartoon //
    float cartoon = clamp(uCartoon, 0.0, 1.0);

    if (cartoon > 0.0)
    {
        float luminance = dot(color.rgb, vec3(0.299, 0.587, 0.114));

        vec3 cartoonColor;

        if (luminance < 0.25)
        {
            cartoonColor = vec3(0.05, 0.05, 0.05);
        }
        else if (luminance < 0.50)
        {
            cartoonColor = vec3(0.35, 0.35, 0.35);
        }
        else if (luminance < 0.75)
        {
            cartoonColor = vec3(0.70, 0.70, 0.70);
        }
        else
        {
            cartoonColor = vec3(1.0, 1.0, 1.0);
        }

        color.rgb = mix(color.rgb, cartoonColor, cartoon);
    }

    // Blur //

    float blur = clamp(uBlur, 0.0, 50.0);

    if (blur > 0.0)
    {
        // Blur radius in pixels.
        float radius = blur * 3.0;
        vec2 offset = uTexelSize * radius;
        vec3 blurColor = vec3(0.0);

        // Gaussian-like 3x3 kernel.
        blurColor += texture(imageTexture, uv + vec2(-offset.x,  offset.y)).rgb * 1.0;
        blurColor += texture(imageTexture, uv + vec2(0.0, offset.y)).rgb * 2.0;
        blurColor += texture(imageTexture, uv + vec2(offset.x, offset.y)).rgb * 1.0;
        blurColor += texture(imageTexture, uv + vec2(-offset.x, 0.0)).rgb * 2.0;
        blurColor += texture(imageTexture, uv).rgb * 4.0;
        blurColor += texture(imageTexture, uv + vec2(offset.x, 0.0)).rgb * 2.0;
        blurColor += texture(imageTexture, uv + vec2(-offset.x, -offset.y)).rgb * 1.0;
        blurColor += texture(imageTexture, uv + vec2(0.0, -offset.y)).rgb * 2.0;
        blurColor += texture(imageTexture, uv + vec2(offset.x, -offset.y)).rgb * 1.0;
        blurColor /= 16.0;

        color.rgb = mix(color.rgb, blurColor, blur);
    }

    // Motion Blur //

    float motionBlur = clamp(uMotionBlur, 0.0, 1.0);

    if (motionBlur > 0.0)
    {
        vec3 blurColor = vec3(0.0);

        float samples = 16.0;

        // Horizontal motion blur.
        vec2 direction = vec2(uTexelSize.x, 0.0);

        for (int i = 0; i < 16; i++)
        {
            float index = float(i);

            float offset = (index - 7.5 ) * motionBlur * 2.0;

            blurColor += texture(imageTexture, uv + direction * offset).rgb;
        }

        blurColor /= samples;

        color.rgb = mix(color.rgb, blurColor, motionBlur);
    }

    // Sharpen //

    if (uSharpen > 0.0)
    {
        vec2 offset = uTexelSize;
        vec3 center = texture(imageTexture, uv).rgb;
        vec3 top = texture(imageTexture, uv + vec2(0.0, offset.y)).rgb;
        vec3 bottom = texture(imageTexture, uv - vec2(0.0, offset.y)).rgb;
        vec3 left = texture(imageTexture, uv - vec2(offset.x, 0.0)).rgb;
        vec3 right = texture(imageTexture, uv + vec2(offset.x, 0.0)).rgb;
        vec3 sharpened = center * (1.0 + 4.0 * uSharpen) - (top + bottom + left + right) * uSharpen;

        color.rgb = sharpened;
    }


    // Noise //

    if (uNoise > 0.0)
    {
        float noise = random(uv * uResolution);
        noise = noise * 2.0 - 1.0;
        color.rgb += (noise * uNoise);
    }


    // Denoiser //

    if (uDenoiser > 0.0)
    {
        vec3 center = color.rgb;
        vec3 blurColor = vec3(0.0);
        float totalWeight = 0.0;
        vec2 offset = uTexelSize;

        for (int x = -1; x <= 1; x++)
        {
            for (int y = -1; y <= 1; y++)
            {
                vec2 sampleUV = uv + vec2(float(x) * offset.x, float(y) * offset.y);
                vec3 sampleColor = texture(imageTexture, sampleUV).rgb;
                float distance = length(sampleColor - center);
                // Similar colors receive higher weight.
                float weight = exp(-distance * 20.0);
                blurColor += sampleColor * weight;
                totalWeight += weight;
            }
        }

        blurColor /= totalWeight;
        color.rgb = mix(color.rgb, blurColor, uDenoiser);
    }


    FragColor = color;
}