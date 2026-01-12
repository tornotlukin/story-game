## shader_library.rpy - Reusable shader effects library
##
## GLSL shaders ported from Phaser.js to work with Ren'Py 8.5.2.
## Each shader is registered with renpy.register_shader() and can be
## applied via transforms defined in shader_transforms.rpy.
##
## Phaser uniform translations:
##   uMainSampler -> tex0
##   outTexCoord -> v_tex_coord
##   resolution -> u_model_size
##   boundedSampler() -> texture2D with clamped coords
##
## Related files: shader_transforms.rpy, docs/shader_porting_guide.md

################################################################################
## Helper: Bounded Sampler Function (prevents edge artifacts)
## All shaders include this as needed for proper edge handling
################################################################################

################################################################################
## Glow Shaders (Phaser Glow Filter)
################################################################################

init python:

    # Outer/Inner Glow Effect - Simple 8-sample version for compatibility
    renpy.register_shader("shader.glow", variables="""
        uniform float u_outer_strength;
        uniform float u_inner_strength;
        uniform vec4 u_glow_color;
        uniform float u_scale;
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec2 px = (1.0 / u_model_size) * u_scale * 9.0;

        float totalAlpha = 0.0;

        // 8 samples in cardinal + diagonal directions (unrolled for compatibility)
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(0.0, px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(0.0, -px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, 0.0), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, 0.0), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, -px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, -px.y), 0.0, 1.0)).a;

        vec4 color = texture2D(tex0, v_tex_coord);
        float alphaRatio = totalAlpha / 8.0;

        // Inner glow
        float innerGlowStrength = min(1.0, (1.0 - alphaRatio) * u_inner_strength * color.a);
        vec4 innerColor = mix(color, u_glow_color, innerGlowStrength);

        // Outer glow
        float outerGlowAlpha = alphaRatio * u_outer_strength * (1.0 - color.a);
        vec4 outerGlowColor = u_glow_color * min(1.0 - innerColor.a, outerGlowAlpha);

        gl_FragColor = innerColor + outerGlowColor;
    """)

    # Pulsing glow (animated) - Simple 8-sample version for compatibility
    renpy.register_shader("shader.glow_pulse", variables="""
        uniform float u_strength;
        uniform float u_speed;
        uniform vec4 u_glow_color;
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Wrap time to avoid float precision issues with large values
        float wrapped_time = mod(u_time, 628.318); // ~100 cycles of 2*PI
        float pulse = (sin(wrapped_time * u_speed) + 1.0) * 0.5;
        float strength = u_strength * (0.5 + pulse * 0.5);

        vec2 px = (1.0 / u_model_size) * (6.0 + pulse * 6.0);

        float totalAlpha = 0.0;

        // 8 samples unrolled for compatibility
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(0.0, px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(0.0, -px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, 0.0), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, 0.0), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, -px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, -px.y), 0.0, 1.0)).a;

        vec4 color = texture2D(tex0, v_tex_coord);
        float alphaRatio = totalAlpha / 8.0;

        float outerGlowAlpha = alphaRatio * strength * (1.0 - color.a);
        vec4 glowColor = u_glow_color * outerGlowAlpha;

        gl_FragColor = color + glowColor;
    """)


################################################################################
## Blur Shaders (Phaser Blur Filters)
################################################################################

init python:

    # Gaussian Blur 9-tap - alpha-weighted to preserve transparency
    renpy.register_shader("shader.blur_gaussian", variables="""
        uniform vec2 u_offset;
        uniform float u_strength;
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // 9-tap Gaussian blur with alpha weighting
        vec2 resolution = u_model_size;
        vec2 off1 = vec2(1.3846153846) * u_offset * u_strength;
        vec2 off2 = vec2(3.2307692308) * u_offset * u_strength;

        // Gaussian weights
        float w0 = 0.2270270270;
        float w1 = 0.3162162162;
        float w2 = 0.0702702703;

        vec4 s0 = texture2D(tex0, clamp(v_tex_coord, 0.0, 1.0));
        vec4 s1 = texture2D(tex0, clamp(v_tex_coord + (off1 / resolution), 0.0, 1.0));
        vec4 s2 = texture2D(tex0, clamp(v_tex_coord - (off1 / resolution), 0.0, 1.0));
        vec4 s3 = texture2D(tex0, clamp(v_tex_coord + (off2 / resolution), 0.0, 1.0));
        vec4 s4 = texture2D(tex0, clamp(v_tex_coord - (off2 / resolution), 0.0, 1.0));

        // Weight colors by alpha to avoid dark edges
        float totalWeight = s0.a * w0 + s1.a * w1 + s2.a * w1 + s3.a * w2 + s4.a * w2;
        vec3 colorAcc = s0.rgb * s0.a * w0 + s1.rgb * s1.a * w1 + s2.rgb * s2.a * w1 +
                        s3.rgb * s3.a * w2 + s4.rgb * s4.a * w2;

        vec3 finalColor = totalWeight > 0.0 ? colorAcc / totalWeight : vec3(0.0);
        float finalAlpha = s0.a * w0 + s1.a * w1 + s2.a * w1 + s3.a * w2 + s4.a * w2;

        gl_FragColor = vec4(finalColor, finalAlpha);
    """)

    # Gaussian Blur 13-tap - alpha-weighted to preserve transparency
    renpy.register_shader("shader.blur_gaussian_high", variables="""
        uniform vec2 u_offset;
        uniform float u_strength;
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // 13-tap Gaussian blur with alpha weighting
        vec2 resolution = u_model_size;
        vec2 off1 = vec2(1.411764705882353) * u_offset * u_strength;
        vec2 off2 = vec2(3.2941176470588234) * u_offset * u_strength;
        vec2 off3 = vec2(5.176470588235294) * u_offset * u_strength;

        // Gaussian weights
        float w0 = 0.1964825501511404;
        float w1 = 0.2969069646728344;
        float w2 = 0.09447039785044732;
        float w3 = 0.010381362401148057;

        vec4 s0 = texture2D(tex0, clamp(v_tex_coord, 0.0, 1.0));
        vec4 s1 = texture2D(tex0, clamp(v_tex_coord + (off1 / resolution), 0.0, 1.0));
        vec4 s2 = texture2D(tex0, clamp(v_tex_coord - (off1 / resolution), 0.0, 1.0));
        vec4 s3 = texture2D(tex0, clamp(v_tex_coord + (off2 / resolution), 0.0, 1.0));
        vec4 s4 = texture2D(tex0, clamp(v_tex_coord - (off2 / resolution), 0.0, 1.0));
        vec4 s5 = texture2D(tex0, clamp(v_tex_coord + (off3 / resolution), 0.0, 1.0));
        vec4 s6 = texture2D(tex0, clamp(v_tex_coord - (off3 / resolution), 0.0, 1.0));

        // Weight colors by alpha to avoid dark edges
        float totalWeight = s0.a * w0 + s1.a * w1 + s2.a * w1 + s3.a * w2 + s4.a * w2 + s5.a * w3 + s6.a * w3;
        vec3 colorAcc = s0.rgb * s0.a * w0 + s1.rgb * s1.a * w1 + s2.rgb * s2.a * w1 +
                        s3.rgb * s3.a * w2 + s4.rgb * s4.a * w2 +
                        s5.rgb * s5.a * w3 + s6.rgb * s6.a * w3;

        vec3 finalColor = totalWeight > 0.0 ? colorAcc / totalWeight : vec3(0.0);
        float finalAlpha = s0.a * w0 + s1.a * w1 + s2.a * w1 + s3.a * w2 + s4.a * w2 + s5.a * w3 + s6.a * w3;

        gl_FragColor = vec4(finalColor, finalAlpha);
    """)

    # Simple box blur (faster, lower quality) - alpha-weighted to avoid edges
    renpy.register_shader("shader.blur_box", variables="""
        uniform float u_radius;
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec2 px = 1.0 / u_model_size;
        vec3 colorAcc = vec3(0.0);
        float alphaAcc = 0.0;
        float weightSum = 0.0;
        float sampleCount = 0.0;

        for (float x = -3.0; x <= 3.0; x += 1.0) {
            for (float y = -3.0; y <= 3.0; y += 1.0) {
                vec2 sampleCoord = clamp(v_tex_coord + vec2(x, y) * px * u_radius, 0.0, 1.0);
                vec4 samp = texture2D(tex0, sampleCoord);

                // Weight color by alpha to avoid dark edges from transparent pixels
                float weight = samp.a;
                colorAcc += samp.rgb * weight;
                weightSum += weight;
                alphaAcc += samp.a;
                sampleCount += 1.0;
            }
        }

        vec3 finalColor = weightSum > 0.0 ? colorAcc / weightSum : vec3(0.0);
        float finalAlpha = alphaAcc / sampleCount;

        gl_FragColor = vec4(finalColor, finalAlpha);
    """)

    # Bokeh Blur - Simplified for performance, preserves alpha
    renpy.register_shader("shader.blur_bokeh", variables="""
        uniform float u_radius;
        uniform float u_amount;
        uniform float u_contrast;
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Simplified Bokeh blur - 22 samples in golden angle spiral
        #define GOLDEN_ANGLE 2.39996323

        vec2 resolution = u_model_size;
        vec2 pixel = vec2(resolution.y / resolution.x, 1.0) * u_radius * 0.025;

        vec3 acc = vec3(0.0);
        vec3 div = vec3(0.0);
        float alphaAcc = 0.0;
        float alphaDiv = 0.0;
        float r = 1.0;

        // 22 iterations instead of 100
        for (int i = 0; i < 22; i++) {
            float angle = float(i) * GOLDEN_ANGLE;
            r += 1.0 / r;
            vec2 sampleOffset = (r - 1.0) * vec2(cos(angle), sin(angle)) * 0.06;
            vec2 sampleCoord = clamp(v_tex_coord + pixel * sampleOffset, 0.0, 1.0);
            vec4 samp = texture2D(tex0, sampleCoord);

            // Weight by alpha to avoid edge artifacts
            float weight = samp.a;
            vec3 col = samp.rgb;
            col = u_contrast > 0.0 ? col * col * (1.0 + u_contrast) : col;
            vec3 bokeh = vec3(0.5) + pow(col, vec3(10.0)) * u_amount;

            acc += col * bokeh * weight;
            div += bokeh * weight;
            alphaAcc += samp.a;
            alphaDiv += 1.0;
        }

        vec3 finalColor = div.r > 0.0 ? acc / div : vec3(0.0);
        float finalAlpha = alphaAcc / alphaDiv;

        gl_FragColor = vec4(finalColor, finalAlpha);
    """)

    # Radial blur (motion blur from center) - alpha-weighted
    renpy.register_shader("shader.blur_radial", variables="""
        uniform float u_strength;
        uniform vec2 u_center;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec2 dir = v_tex_coord - u_center;
        vec3 colorAcc = vec3(0.0);
        float alphaAcc = 0.0;
        float weightSum = 0.0;
        const int SAMPLES = 12;

        for (int i = 0; i < SAMPLES; i++) {
            float t = float(i) / float(SAMPLES - 1);
            vec2 sampleCoord = clamp(v_tex_coord - dir * t * u_strength, 0.0, 1.0);
            vec4 samp = texture2D(tex0, sampleCoord);

            // Weight by alpha to avoid dark edges
            colorAcc += samp.rgb * samp.a;
            weightSum += samp.a;
            alphaAcc += samp.a;
        }

        vec3 finalColor = weightSum > 0.0 ? colorAcc / weightSum : vec3(0.0);
        float finalAlpha = alphaAcc / float(SAMPLES);

        gl_FragColor = vec4(finalColor, finalAlpha);
    """)


################################################################################
## Distortion Shaders (Phaser Distortion Filters)
################################################################################

init python:

    # Barrel/Fisheye Distortion - Ported from Phaser barrel.js
    renpy.register_shader("shader.distort_barrel", variables="""
        uniform float u_amount;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser barrel distortion
        vec2 xy = 2.0 * v_tex_coord - 1.0;
        vec2 texCoord = v_tex_coord;

        if (length(xy) < 1.0) {
            float theta = atan(xy.y, xy.x);
            float radius = pow(length(xy), u_amount);
            texCoord = 0.5 * (vec2(radius * cos(theta), radius * sin(theta)) + 1.0);
        }

        gl_FragColor = texture2D(tex0, clamp(texCoord, 0.0, 1.0));
    """)

    # Displacement Map - Ported from Phaser displacement.js
    renpy.register_shader("shader.distort_displacement", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_displacement_map;
        uniform vec2 u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser displacement filter
        vec2 disp = (-vec2(0.5, 0.5) + texture2D(u_displacement_map, v_tex_coord).rg) * u_amount;
        gl_FragColor = texture2D(tex0, clamp(v_tex_coord + disp, 0.0, 1.0));
    """)

    # Wave Distortion (horizontal waves)
    renpy.register_shader("shader.distort_wave", variables="""
        uniform float u_amplitude;
        uniform float u_frequency;
        uniform float u_speed;
        uniform sampler2D tex0;
        uniform float u_time;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Wrap time to avoid float precision issues
        float wrapped_time = mod(u_time, 628.318);
        float wave = sin(v_tex_coord.y * u_frequency + wrapped_time * u_speed) * u_amplitude;
        vec2 texCoord = clamp(v_tex_coord + vec2(wave, 0.0), 0.0, 1.0);
        gl_FragColor = texture2D(tex0, texCoord);
    """)

    # Ripple Distortion (circular waves from center)
    renpy.register_shader("shader.distort_ripple", variables="""
        uniform float u_amplitude;
        uniform float u_frequency;
        uniform float u_speed;
        uniform vec2 u_center;
        uniform sampler2D tex0;
        uniform float u_time;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Wrap time to avoid float precision issues
        float wrapped_time = mod(u_time, 628.318);
        vec2 delta = v_tex_coord - u_center;
        float dist = length(delta);
        float wave = sin(dist * u_frequency - wrapped_time * u_speed) * u_amplitude;
        vec2 dir = normalize(delta + 0.0001);
        vec2 texCoord = clamp(v_tex_coord + dir * wave, 0.0, 1.0);
        gl_FragColor = texture2D(tex0, texCoord);
    """)

    # Screen shake/jitter
    renpy.register_shader("shader.distort_shake", variables="""
        uniform float u_intensity;
        uniform float u_speed;
        uniform sampler2D tex0;
        uniform float u_time;
        uniform vec2 u_model_size;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Wrap time to avoid float precision issues
        float t = mod(u_time * u_speed, 628.318);
        vec2 offset = vec2(
            sin(t * 17.0) * cos(t * 23.0),
            sin(t * 19.0) * cos(t * 29.0)
        ) * u_intensity / u_model_size;
        gl_FragColor = texture2D(tex0, clamp(v_tex_coord + offset, 0.0, 1.0));
    """)


################################################################################
## Color Matrix Shader (Phaser ColorMatrix)
################################################################################

init python:

    # Color Matrix - Ported from Phaser colormatrix.js
    # Use a 20-element array for full color matrix transformation
    renpy.register_shader("shader.color_matrix", variables="""
        uniform float u_matrix[20];
        uniform float u_alpha;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser color matrix filter
        vec4 c = texture2D(tex0, v_tex_coord);

        if (u_alpha == 0.0) {
            gl_FragColor = c;
            return;
        }

        if (c.a > 0.0) {
            c.rgb /= c.a;
        }

        vec4 result;
        result.r = (u_matrix[0] * c.r) + (u_matrix[1] * c.g) + (u_matrix[2] * c.b) + (u_matrix[3] * c.a) + u_matrix[4];
        result.g = (u_matrix[5] * c.r) + (u_matrix[6] * c.g) + (u_matrix[7] * c.b) + (u_matrix[8] * c.a) + u_matrix[9];
        result.b = (u_matrix[10] * c.r) + (u_matrix[11] * c.g) + (u_matrix[12] * c.b) + (u_matrix[13] * c.a) + u_matrix[14];
        result.a = (u_matrix[15] * c.r) + (u_matrix[16] * c.g) + (u_matrix[17] * c.b) + (u_matrix[18] * c.a) + u_matrix[19];

        vec3 rgb = mix(c.rgb, result.rgb, u_alpha);
        rgb *= result.a;

        gl_FragColor = vec4(rgb, result.a);
    """)


################################################################################
## Color Adjustment Shaders (Simplified color effects)
################################################################################

init python:

    # Grayscale - preserves transparency
    renpy.register_shader("shader.color_grayscale", variables="""
        uniform float u_amount;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
        vec3 grayColor = vec3(gray);
        vec3 result = mix(color.rgb, grayColor, u_amount);
        // Preserve original RGB for transparent pixels
        result = mix(color.rgb, result, color.a);
        gl_FragColor = vec4(result, color.a);
    """)

    # Sepia Tone - preserves transparency
    renpy.register_shader("shader.color_sepia", variables="""
        uniform float u_amount;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        vec3 sepia;
        sepia.r = dot(color.rgb, vec3(0.393, 0.769, 0.189));
        sepia.g = dot(color.rgb, vec3(0.349, 0.686, 0.168));
        sepia.b = dot(color.rgb, vec3(0.272, 0.534, 0.131));
        vec3 result = mix(color.rgb, sepia, u_amount);
        // Preserve original RGB for transparent pixels
        result = mix(color.rgb, result, color.a);
        gl_FragColor = vec4(result, color.a);
    """)

    # Invert Colors - preserves transparency by not inverting transparent pixels
    renpy.register_shader("shader.color_invert", variables="""
        uniform float u_amount;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        // Only invert RGB where there's actual alpha, prevents white fringing on transparency
        vec3 inverted = 1.0 - color.rgb;
        vec3 result = mix(color.rgb, inverted, u_amount);
        // Preserve original RGB for fully transparent pixels to avoid white edges
        result = mix(color.rgb, result, color.a);
        gl_FragColor = vec4(result, color.a);
    """)

    # Brightness/Contrast/Saturation - preserves transparency
    renpy.register_shader("shader.color_adjust", variables="""
        uniform float u_brightness;
        uniform float u_contrast;
        uniform float u_saturation;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);

        // Brightness
        vec3 result = color.rgb + u_brightness;

        // Contrast
        result = (result - 0.5) * u_contrast + 0.5;

        // Saturation
        float gray = dot(result, vec3(0.299, 0.587, 0.114));
        result = mix(vec3(gray), result, u_saturation);

        // Preserve original RGB for transparent pixels to avoid colored edges
        result = clamp(result, 0.0, 1.0);
        result = mix(color.rgb, result, color.a);
        gl_FragColor = vec4(result, color.a);
    """)

    # Hue Shift - preserves transparency
    renpy.register_shader("shader.color_hue", variables="""
        uniform float u_shift;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);

        // RGB to HSV
        float maxC = max(max(color.r, color.g), color.b);
        float minC = min(min(color.r, color.g), color.b);
        float delta = maxC - minC;

        float h = 0.0;
        if (delta > 0.0) {
            if (maxC == color.r) {
                h = mod((color.g - color.b) / delta, 6.0);
            } else if (maxC == color.g) {
                h = (color.b - color.r) / delta + 2.0;
            } else {
                h = (color.r - color.g) / delta + 4.0;
            }
            h /= 6.0;
        }
        float s = maxC > 0.0 ? delta / maxC : 0.0;
        float v = maxC;

        // Shift hue
        h = mod(h + u_shift, 1.0);

        // HSV to RGB
        float c = v * s;
        float x = c * (1.0 - abs(mod(h * 6.0, 2.0) - 1.0));
        float m = v - c;

        vec3 rgb;
        if (h < 1.0/6.0) rgb = vec3(c, x, 0.0);
        else if (h < 2.0/6.0) rgb = vec3(x, c, 0.0);
        else if (h < 3.0/6.0) rgb = vec3(0.0, c, x);
        else if (h < 4.0/6.0) rgb = vec3(0.0, x, c);
        else if (h < 5.0/6.0) rgb = vec3(x, 0.0, c);
        else rgb = vec3(c, 0.0, x);

        vec3 result = rgb + m;
        // Preserve original RGB for transparent pixels
        result = mix(color.rgb, result, color.a);
        gl_FragColor = vec4(result, color.a);
    """)

    # Color Tint/Overlay - preserves transparency
    renpy.register_shader("shader.color_tint", variables="""
        uniform vec4 u_tint_color;
        uniform float u_amount;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        vec3 tinted = color.rgb * u_tint_color.rgb;
        vec3 result = mix(color.rgb, tinted, u_amount);
        // Preserve original RGB for transparent pixels
        result = mix(color.rgb, result, color.a);
        gl_FragColor = vec4(result, color.a);
    """)


################################################################################
## Blend Mode Shaders (Ported from Phaser blend.js)
################################################################################

init python:

    # Multiply Blend
    renpy.register_shader("shader.blend_multiply", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);
        vec4 result = base * blend;
        gl_FragColor = mix(base, result, u_amount);
    """)

    # Screen Blend
    renpy.register_shader("shader.blend_screen", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);
        vec4 result = 1.0 - (1.0 - base) * (1.0 - blend);
        gl_FragColor = mix(base, result, u_amount);
    """)

    # Overlay Blend - inline expressions for GPU compatibility
    renpy.register_shader("shader.blend_overlay", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser overlay blend - inlined for compatibility
        #define OVERLAY(b, l) ((b) < 0.5 ? 2.0 * (b) * (l) : 1.0 - 2.0 * (1.0 - (b)) * (1.0 - (l)))

        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);

        vec4 result = vec4(
            OVERLAY(base.r, blend.r),
            OVERLAY(base.g, blend.g),
            OVERLAY(base.b, blend.b),
            OVERLAY(base.a, blend.a)
        );

        gl_FragColor = mix(base, result, u_amount);
    """)

    # Soft Light Blend - inline expressions for GPU compatibility
    renpy.register_shader("shader.blend_soft_light", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser soft light blend - inlined for compatibility
        #define SOFTLIGHT(b, l) ((l) < 0.5 ? (2.0 * (b) * (l) + (b) * (b) * (1.0 - 2.0 * (l))) : (sqrt(b) * (2.0 * (l) - 1.0) + 2.0 * (b) * (1.0 - (l))))

        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);

        vec4 result = vec4(
            SOFTLIGHT(base.r, blend.r),
            SOFTLIGHT(base.g, blend.g),
            SOFTLIGHT(base.b, blend.b),
            SOFTLIGHT(base.a, blend.a)
        );

        gl_FragColor = mix(base, result, u_amount);
    """)

    # Hard Light Blend - inline expressions for GPU compatibility
    renpy.register_shader("shader.blend_hard_light", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser hard light blend - inlined for compatibility
        #define HARDLIGHT(b, l) ((l) < 0.5 ? 2.0 * (b) * (l) : 1.0 - 2.0 * (1.0 - (b)) * (1.0 - (l)))

        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);

        vec4 result = vec4(
            HARDLIGHT(base.r, blend.r),
            HARDLIGHT(base.g, blend.g),
            HARDLIGHT(base.b, blend.b),
            HARDLIGHT(base.a, blend.a)
        );

        gl_FragColor = mix(base, result, u_amount);
    """)

    # Color Dodge Blend - inline expressions for GPU compatibility
    renpy.register_shader("shader.blend_color_dodge", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser color dodge blend - inlined for compatibility
        #define DODGE(b, l) ((l) >= 1.0 ? (l) : min(1.0, (b) / (1.0 - (l))))

        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);

        vec4 result = vec4(
            DODGE(base.r, blend.r),
            DODGE(base.g, blend.g),
            DODGE(base.b, blend.b),
            DODGE(base.a, blend.a)
        );

        gl_FragColor = mix(base, result, u_amount);
    """)

    # Color Burn Blend - inline expressions for GPU compatibility
    renpy.register_shader("shader.blend_color_burn", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser color burn blend - inlined for compatibility
        #define BURN(b, l) ((l) <= 0.0 ? (l) : 1.0 - min(1.0, (1.0 - (b)) / (l)))

        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);

        vec4 result = vec4(
            BURN(base.r, blend.r),
            BURN(base.g, blend.g),
            BURN(base.b, blend.b),
            BURN(base.a, blend.a)
        );

        gl_FragColor = mix(base, result, u_amount);
    """)

    # Difference Blend
    renpy.register_shader("shader.blend_difference", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);
        vec4 result = abs(base - blend);
        gl_FragColor = mix(base, result, u_amount);
    """)

    # Exclusion Blend
    renpy.register_shader("shader.blend_exclusion", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);
        vec4 result = base + blend - 2.0 * base * blend;
        gl_FragColor = mix(base, result, u_amount);
    """)


################################################################################
## Retro/Stylized Shaders
################################################################################

init python:

    # Pixelate - Ported from Phaser pixelate.js
    renpy.register_shader("shader.retro_pixelate", variables="""
        uniform float u_pixel_size;
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser pixelate filter
        float pixelSize = max(2.0, u_pixel_size);
        vec2 resolution = u_model_size;
        vec2 center = pixelSize * floor(v_tex_coord * resolution / pixelSize) + pixelSize * vec2(0.5, 0.5);
        vec2 corner1 = center + pixelSize * vec2(-0.5, -0.5);
        vec2 corner2 = center + pixelSize * vec2(0.5, -0.5);
        vec2 corner3 = center + pixelSize * vec2(0.5, 0.5);
        vec2 corner4 = center + pixelSize * vec2(-0.5, 0.5);

        vec4 pixel = 0.4 * texture2D(tex0, center / resolution);
        pixel += 0.15 * texture2D(tex0, corner1 / resolution);
        pixel += 0.15 * texture2D(tex0, corner2 / resolution);
        pixel += 0.15 * texture2D(tex0, corner3 / resolution);
        pixel += 0.15 * texture2D(tex0, corner4 / resolution);

        gl_FragColor = pixel;
    """)

    # CRT Scanlines
    renpy.register_shader("shader.retro_scanlines", variables="""
        uniform float u_intensity;
        uniform float u_count;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        float scanline = sin(v_tex_coord.y * u_count * 3.14159) * 0.5 + 0.5;
        scanline = pow(scanline, 1.5);
        color.rgb *= 1.0 - (u_intensity * (1.0 - scanline));
        gl_FragColor = color;
    """)

    # Vignette (darkened edges)
    renpy.register_shader("shader.retro_vignette", variables="""
        uniform float u_intensity;
        uniform float u_radius;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        vec2 center = v_tex_coord - 0.5;
        float dist = length(center);
        float vignette = smoothstep(u_radius, u_radius - 0.3, dist);
        color.rgb *= mix(1.0 - u_intensity, 1.0, vignette);
        gl_FragColor = color;
    """)

    # Chromatic Aberration (RGB split)
    renpy.register_shader("shader.retro_chromatic", variables="""
        uniform float u_amount;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec2 dir = v_tex_coord - 0.5;
        float dist = length(dir);
        vec2 offset = dir * dist * u_amount;

        float r = texture2D(tex0, clamp(v_tex_coord + offset, 0.0, 1.0)).r;
        float g = texture2D(tex0, v_tex_coord).g;
        float b = texture2D(tex0, clamp(v_tex_coord - offset, 0.0, 1.0)).b;
        float a = texture2D(tex0, v_tex_coord).a;

        gl_FragColor = vec4(r, g, b, a);
    """)

    # Glitch Effect
    renpy.register_shader("shader.retro_glitch", variables="""
        uniform float u_intensity;
        uniform float u_speed;
        uniform sampler2D tex0;
        uniform float u_time;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Wrap time to avoid float precision issues
        float t = mod(u_time * u_speed, 628.318);

        // Random-ish function
        float rand = fract(sin(dot(vec2(floor(v_tex_coord.y * 20.0), floor(t * 10.0)), vec2(12.9898, 78.233))) * 43758.5453);

        // Horizontal offset glitch
        float glitchOffset = 0.0;
        if (rand > 0.9) {
            glitchOffset = (rand - 0.9) * 10.0 * u_intensity;
        }

        vec2 uv = v_tex_coord;
        uv.x += glitchOffset * sin(t * 100.0);
        uv = clamp(uv, 0.0, 1.0);

        // Color channel split
        float r = texture2D(tex0, clamp(uv + vec2(u_intensity * 0.01, 0.0), 0.0, 1.0)).r;
        float g = texture2D(tex0, uv).g;
        float b = texture2D(tex0, clamp(uv - vec2(u_intensity * 0.01, 0.0), 0.0, 1.0)).b;
        float a = texture2D(tex0, uv).a;

        gl_FragColor = vec4(r, g, b, a);
    """)


################################################################################
## Light Rays / Shadow Shader (Ported from Phaser shadow.js)
################################################################################

init python:

    # Light rays - use float instead of int for better GPU compatibility
    renpy.register_shader("shader.light_rays", variables="""
        uniform vec2 u_light_position;
        uniform vec4 u_color;
        uniform float u_decay;
        uniform float u_power;
        uniform float u_intensity;
        uniform float u_samples;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser shadow/light rays filter
        const int MAX = 12;

        vec4 texColor = texture2D(tex0, clamp(v_tex_coord, 0.0, 1.0));
        vec2 pc = (u_light_position - v_tex_coord) * u_intensity;
        float shadow = 0.0;
        int sampleCount = int(clamp(u_samples, 1.0, float(MAX)));
        float limit = max(float(MAX), u_samples);

        for (int i = 0; i < MAX; ++i) {
            if (i >= sampleCount) {
                break;
            }
            vec2 sampleCoord = clamp(v_tex_coord + float(i) * u_decay / limit * pc, 0.0, 1.0);
            shadow += texture2D(tex0, sampleCoord).a * u_power;
        }

        float mask = 1.0 - texColor.a;
        gl_FragColor = mix(texColor, u_color, clamp(shadow * mask, 0.0, 1.0));
    """)


################################################################################
## Threshold Shader (Ported from Phaser threshold.js)
################################################################################

init python:

    renpy.register_shader("shader.threshold", variables="""
        uniform vec4 u_edge1;
        uniform vec4 u_edge2;
        uniform vec4 u_invert;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser threshold filter
        vec4 color = texture2D(tex0, v_tex_coord);
        color = clamp((color - u_edge1) / (u_edge2 - u_edge1), 0.0, 1.0);
        color = mix(color, 1.0 - color, u_invert);
        gl_FragColor = color;
    """)


################################################################################
## Alpha Mask Shader (Ported from Phaser mask.js)
################################################################################

init python:

    # Alpha mask - use float instead of bool for better GPU compatibility
    # u_invert: 0.0 = normal mask, 1.0 = inverted mask
    renpy.register_shader("shader.alpha_mask", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_mask_texture;
        uniform float u_invert;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser mask filter
        vec4 color = texture2D(tex0, v_tex_coord);
        vec4 mask = texture2D(u_mask_texture, v_tex_coord);
        float a = mask.a;
        // u_invert >= 0.5 means inverted
        float maskValue = u_invert >= 0.5 ? (1.0 - a) : a;
        color *= maskValue;
        gl_FragColor = color;
    """)


################################################################################
## Outline/Edge Shaders
################################################################################

init python:

    # Simple Outline
    renpy.register_shader("shader.outline", variables="""
        uniform float u_width;
        uniform vec4 u_outline_color;
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec2 px = u_width / u_model_size;
        vec4 color = texture2D(tex0, v_tex_coord);

        float outline = 0.0;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, 0.0), 0.0, 1.0)).a;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, 0.0), 0.0, 1.0)).a;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(0.0, -px.y), 0.0, 1.0)).a;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(0.0, px.y), 0.0, 1.0)).a;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, -px.y), 0.0, 1.0)).a;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, -px.y), 0.0, 1.0)).a;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, px.y), 0.0, 1.0)).a;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, px.y), 0.0, 1.0)).a;

        outline = min(1.0, outline);
        float outlineAlpha = outline * (1.0 - color.a);

        vec4 result = mix(u_outline_color * outlineAlpha, color, color.a);
        result.a = max(color.a, outlineAlpha);

        gl_FragColor = result;
    """)


################################################################################
## Transition Shaders
################################################################################

init python:

    # Dissolve with pattern
    renpy.register_shader("shader.transition_dissolve", variables="""
        uniform float u_progress;
        uniform float u_smoothness;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);

        // Generate noise pattern
        float noise = fract(sin(dot(v_tex_coord, vec2(12.9898, 78.233))) * 43758.5453);

        float alpha = smoothstep(u_progress - u_smoothness, u_progress + u_smoothness, noise);
        color.a *= alpha;

        gl_FragColor = color;
    """)

    # Wipe transition (directional)
    renpy.register_shader("shader.transition_wipe", variables="""
        uniform float u_progress;
        uniform float u_angle;
        uniform float u_smoothness;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);

        vec2 center = v_tex_coord - 0.5;
        float angle = u_angle * 3.14159 / 180.0;
        float proj = dot(center, vec2(cos(angle), sin(angle))) + 0.5;

        float alpha = smoothstep(u_progress - u_smoothness, u_progress + u_smoothness, proj);
        color.a *= alpha;

        gl_FragColor = color;
    """)
