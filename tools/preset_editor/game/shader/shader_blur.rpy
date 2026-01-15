## shader_blur.rpy - Blur effect shaders
##
## Various blur effects including Gaussian, box, bokeh, and radial.
## All use alpha-weighted sampling to preserve PNG transparency.
## Ported from Phaser.js blur filters.
##
## Shaders:
##   - shader.blur_gaussian - 9-tap Gaussian blur
##   - shader.blur_gaussian_high - 13-tap high-quality Gaussian
##   - shader.blur_box - Simple box blur
##   - shader.blur_bokeh - Depth-of-field style bokeh
##   - shader.blur_radial - Motion blur from center
##
## Related files: shader_transforms.rpy

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
