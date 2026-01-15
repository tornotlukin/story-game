## shader_kaleidoscope.rpy - Kaleidoscope and bounce effects
##
## Fractal kaleidoscope patterns with controllable bounce/pulse
## and customizable color palettes.
##
## Shaders:
##   - shader.kaleidoscope_bounce - Bouncing kaleidoscope with color control
##   - shader.kaleidoscope_static - Non-bouncing kaleidoscope
##   - shader.kaleidoscope_overlay - Kaleidoscope blended with images
##
## @tool-category: Kaleidoscope
## @tool-description: Fractal kaleidoscope with bounce and color control

init python:

    # =========================================================================
    # shader.kaleidoscope_bounce - Bouncing kaleidoscope
    # =========================================================================

    # @shader: shader.kaleidoscope_bounce
    # @description: Kaleidoscope with controllable bounce and colors
    # @animated
    # @param u_speed: float, range=0.2-3.0, default=1.0, description=Animation speed
    # @param u_bounce_speed: float, range=0.2-3.0, default=1.0, description=Bounce pulse speed
    # @param u_bounce_count: float, range=0.0-20.0, default=0.0, description=Number of bounces (0 = infinite)
    # @param u_bounce_amplitude: float, range=0.1-2.0, default=1.0, description=Bounce intensity
    # @param u_iterations: float, range=4.0-24.0, default=16.0, description=Fractal detail
    # @param u_color1: color, default=#FF0066, description=Primary tint color
    # @param u_color2: color, default=#00FFCC, description=Secondary tint color
    # @param u_color3: color, default=#FFCC00, description=Tertiary tint color
    # @param u_color_speed: float, range=0.1-3.0, default=1.0, description=Color cycling speed
    # @param u_intensity: float, range=0.005-0.05, default=0.015, description=Pattern intensity
    renpy.register_shader("shader.kaleidoscope_bounce", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_bounce_speed;
        uniform float u_bounce_count;
        uniform float u_bounce_amplitude;
        uniform float u_iterations;
        uniform vec3 u_color1;
        uniform vec3 u_color2;
        uniform vec3 u_color3;
        uniform float u_color_speed;
        uniform float u_intensity;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        #define TAU 7.28318530718

        void main() {
            vec4 origColor = texture2D(tex0, v_tex_coord);

            vec2 uv = v_tex_coord - 0.5;

            // Mirror for kaleidoscope effect
            uv = abs(uv);

            // Bounce calculation
            float bounceTime = u_time * u_bounce_speed;
            float bounce;

            if (u_bounce_count < 0.5) {
                // Infinite bouncing
                bounce = sin(bounceTime) * u_bounce_amplitude;
            } else {
                // Limited bounces
                float totalDuration = u_bounce_count * 3.14159;
                if (bounceTime < totalDuration) {
                    // Still bouncing - decay over time
                    float decay = 1.0 - (bounceTime / totalDuration);
                    bounce = sin(bounceTime) * u_bounce_amplitude * decay;
                } else {
                    // Stopped bouncing
                    bounce = 0.0;
                }
            }

            uv *= bounce;

            vec2 p = mod(uv * TAU, TAU) - 1.0;
            vec2 i = p;
            float c = 0.005;
            float inten = u_intensity;

            float t_base = u_time * u_speed;

            int maxIter = int(u_iterations);
            for (int n = 0; n < 24; n++) {
                if (n >= maxIter) break;

                float t = 0.4 * (t_base + 23.0) * (1.0 - (11.5 / float(n + 99)));
                i = p + vec2(
                    cos(t - i.x) + sin(t + i.y),
                    sin(t - i.y) + cos(t + i.x)
                );
                c += 1.0 / length(vec2(
                    p.x / (sin(i.x + t) / inten),
                    p.y / (cos(i.y + t) / inten)
                ));
            }

            c /= float(maxIter);
            c = 1.0 - pow(c, 52.0);

            // Color calculation with customizable tints
            float ct = u_time * u_color_speed;
            vec3 tint = u_color1 * (0.5 + 0.5 * cos(ct))
                      + u_color2 * (0.5 + 0.5 * cos(ct + 2.094))
                      + u_color3 * (0.5 + 0.5 * cos(ct + 4.189));
            tint = normalize(tint) * 0.8 + 0.2;

            vec3 baseColor = vec3(pow(abs(c), 1.0));
            baseColor = clamp(baseColor * baseColor, 0.0, 1.0);

            vec3 finalColor = (sin(ct + baseColor) + 2.0) * tint;
            finalColor = clamp(finalColor, 0.0, 1.0);

            gl_FragColor = vec4(finalColor, origColor.a);
        }
    """)

    # =========================================================================
    # shader.kaleidoscope_infinite - Infinite smooth bounce
    # =========================================================================

    # @shader: shader.kaleidoscope_infinite
    # @description: Continuously bouncing kaleidoscope
    # @animated
    # @param u_speed: float, range=0.2-3.0, default=1.0, description=Animation speed
    # @param u_bounce_speed: float, range=0.2-3.0, default=1.0, description=Bounce speed
    # @param u_color_mode: float, range=0.0-2.0, default=0.0, description=Color mode (0=rainbow, 1=monochrome, 2=custom)
    # @param u_hue_offset: float, range=0.0-1.0, default=0.0, description=Hue offset for rainbow mode
    # @param u_custom_color: color, default=#FF00FF, description=Custom base color (mode 2)
    renpy.register_shader("shader.kaleidoscope_infinite", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_bounce_speed;
        uniform float u_color_mode;
        uniform float u_hue_offset;
        uniform vec3 u_custom_color;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        #define TAU 7.28318530718
        #define MAX_ITER 16

        vec3 hsv2rgb(float h, float s, float v) {
            vec3 c = clamp(abs(fract(h + vec3(0.0, 2.0/3.0, 1.0/3.0)) * 6.0 - 3.0) - 1.0, 0.0, 1.0);
            return v * mix(vec3(1.0), c, s);
        }

        void main() {
            vec4 origColor = texture2D(tex0, v_tex_coord);

            vec2 uv = v_tex_coord - 0.5;
            uv = abs(uv);
            uv *= sin(u_time * u_bounce_speed);

            vec2 p = mod(uv * TAU, TAU) - 1.0;
            vec2 i = p;
            float c = 0.005;
            float inten = 0.015;

            float t_base = u_time * u_speed;

            for (int n = 0; n < MAX_ITER; n++) {
                float t = 0.4 * (t_base + 23.0) * (1.0 - (11.5 / float(n + 99)));
                i = p + vec2(
                    cos(t - i.x) + sin(t + i.y),
                    sin(t - i.y) + cos(t + i.x)
                );
                c += 1.0 / length(vec2(
                    p.x / (sin(i.x + t) / inten),
                    p.y / (cos(i.y + t) / inten)
                ));
            }

            c /= float(MAX_ITER);
            c = 1.0 - pow(c, 52.0);

            vec3 finalColor;
            if (u_color_mode < 0.5) {
                // Rainbow mode
                float hue = fract(u_time * 0.1 + c * 0.5 + u_hue_offset);
                finalColor = hsv2rgb(hue, 0.8, clamp(c + 0.5, 0.0, 1.0));
            } else if (u_color_mode < 1.5) {
                // Monochrome mode
                finalColor = vec3(c);
            } else {
                // Custom color mode
                finalColor = u_custom_color * (c * 0.5 + 0.5);
            }

            gl_FragColor = vec4(finalColor, origColor.a);
        }
    """)

    # =========================================================================
    # shader.kaleidoscope_limited - Limited bounce count
    # =========================================================================

    # @shader: shader.kaleidoscope_limited
    # @description: Kaleidoscope that bounces a set number of times then stops
    # @animated
    # @param u_speed: float, range=0.2-3.0, default=1.0, description=Animation speed
    # @param u_bounce_count: float, range=1.0-10.0, default=3.0, description=Number of bounces
    # @param u_bounce_decay: float, range=0.5-1.0, default=0.8, description=Bounce decay rate
    # @param u_final_scale: float, range=0.1-1.0, default=0.5, description=Final resting scale
    # @param u_color1: color, default=#FF0088, description=Primary color
    # @param u_color2: color, default=#00CCFF, description=Secondary color
    renpy.register_shader("shader.kaleidoscope_limited", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_bounce_count;
        uniform float u_bounce_decay;
        uniform float u_final_scale;
        uniform vec3 u_color1;
        uniform vec3 u_color2;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        #define TAU 7.28318530718
        #define MAX_ITER 16

        void main() {
            vec4 origColor = texture2D(tex0, v_tex_coord);

            vec2 uv = v_tex_coord - 0.5;
            uv = abs(uv);

            // Limited bouncing with decay
            float bounceTime = u_time * 2.0;
            float bouncePhase = bounceTime / 3.14159;
            float bounce;

            if (bouncePhase < u_bounce_count) {
                // Still bouncing
                float currentBounce = floor(bouncePhase);
                float decay = pow(u_bounce_decay, currentBounce);
                bounce = abs(sin(bounceTime)) * decay;
                // Gradually approach final scale
                float progress = bouncePhase / u_bounce_count;
                bounce = mix(bounce, u_final_scale, progress * progress);
            } else {
                // Stopped - hold at final scale
                bounce = u_final_scale;
            }

            uv *= bounce;

            vec2 p = mod(uv * TAU, TAU) - 1.0;
            vec2 i = p;
            float c = 0.005;
            float inten = 0.015;

            float t_base = u_time * u_speed;

            for (int n = 0; n < MAX_ITER; n++) {
                float t = 0.4 * (t_base + 23.0) * (1.0 - (11.5 / float(n + 99)));
                i = p + vec2(
                    cos(t - i.x) + sin(t + i.y),
                    sin(t - i.y) + cos(t + i.x)
                );
                c += 1.0 / length(vec2(
                    p.x / (sin(i.x + t) / inten),
                    p.y / (cos(i.y + t) / inten)
                ));
            }

            c /= float(MAX_ITER);
            c = 1.0 - pow(c, 52.0);

            // Two-color gradient
            vec3 color = mix(u_color1, u_color2, c);
            color *= (0.5 + 0.5 * sin(u_time + c * 3.0));

            gl_FragColor = vec4(color, origColor.a);
        }
    """)

    # =========================================================================
    # shader.kaleidoscope_overlay - Blended with images
    # =========================================================================

    # @shader: shader.kaleidoscope_overlay
    # @description: Kaleidoscope effect blended with underlying image
    # @animated
    # @param u_speed: float, range=0.2-3.0, default=1.0, description=Animation speed
    # @param u_bounce_speed: float, range=0.2-3.0, default=1.0, description=Bounce speed
    # @param u_opacity: float, range=0.1-1.0, default=0.5, description=Effect opacity
    # @param u_blend_mode: float, range=0.0-2.0, default=1.0, description=Blend (0=mix, 1=screen, 2=add)
    renpy.register_shader("shader.kaleidoscope_overlay", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_bounce_speed;
        uniform float u_opacity;
        uniform float u_blend_mode;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        #define TAU 7.28318530718
        #define MAX_ITER 12

        void main() {
            vec4 origColor = texture2D(tex0, v_tex_coord);

            if (origColor.a < 0.01) {
                gl_FragColor = origColor;
                return;
            }

            vec2 uv = v_tex_coord - 0.5;
            uv = abs(uv);
            uv *= sin(u_time * u_bounce_speed);

            vec2 p = mod(uv * TAU, TAU) - 1.0;
            vec2 i = p;
            float c = 0.005;
            float inten = 0.015;

            float t_base = u_time * u_speed;

            for (int n = 0; n < MAX_ITER; n++) {
                float t = 0.4 * (t_base + 23.0) * (1.0 - (11.5 / float(n + 99)));
                i = p + vec2(
                    cos(t - i.x) + sin(t + i.y),
                    sin(t - i.y) + cos(t + i.x)
                );
                c += 1.0 / length(vec2(
                    p.x / (sin(i.x + t) / inten),
                    p.y / (cos(i.y + t) / inten)
                ));
            }

            c /= float(MAX_ITER);
            c = 1.0 - pow(c, 52.0);

            // Rainbow tint
            vec3 tint = 0.5 + 0.5 * cos(u_time + c + vec3(0.0, 2.0, 4.0));
            vec3 kColor = tint * (c * 0.5 + 0.5);

            vec3 result;
            if (u_blend_mode < 0.5) {
                result = mix(origColor.rgb, kColor, u_opacity);
            } else if (u_blend_mode < 1.5) {
                vec3 screened = 1.0 - (1.0 - origColor.rgb) * (1.0 - kColor);
                result = mix(origColor.rgb, screened, u_opacity);
            } else {
                result = origColor.rgb + kColor * u_opacity;
                result = clamp(result, 0.0, 1.0);
            }

            gl_FragColor = vec4(result, origColor.a);
        }
    """)
