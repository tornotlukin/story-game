## shader_plasma.rpy - Plasma and wave interference effects
##
## Animated plasma patterns created by combining multiple sine waves.
## Classic demoscene-style effects with customizable colors and speed.
##
## Shaders:
##   - shader.plasma_waves - Colorful plasma wave interference
##   - shader.plasma_simple - Simplified plasma (faster)
##   - shader.plasma_overlay - Plasma blended with images
##
## @tool-category: Plasma
## @tool-description: Animated plasma and wave interference patterns

init python:

    # =========================================================================
    # shader.plasma_waves - Full plasma wave effect
    # =========================================================================

    # @shader: shader.plasma_waves
    # @description: Animated plasma waves with customizable colors
    # @animated
    # @param u_speed: float, range=0.2-3.0, default=1.0, description=Animation speed
    # @param u_scale: float, range=0.5-3.0, default=1.0, description=Pattern scale
    # @param u_complexity: float, range=0.5-2.0, default=1.0, description=Wave complexity
    # @param u_color1: color, default=#FF0000, description=Primary color
    # @param u_color2: color, default=#00FF00, description=Secondary color
    # @param u_color3: color, default=#0000FF, description=Tertiary color
    # @param u_color_speed: float, range=0.1-2.0, default=1.0, description=Color cycling speed
    renpy.register_shader("shader.plasma_waves", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_scale;
        uniform float u_complexity;
        uniform vec3 u_color1;
        uniform vec3 u_color2;
        uniform vec3 u_color3;
        uniform float u_color_speed;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        void main() {
            vec4 origColor = texture2D(tex0, v_tex_coord);
            vec2 position = v_tex_coord * u_scale;

            float t = u_time * u_speed;

            // Wave interference pattern (from original shader)
            float value = 0.0;
            value += sin(position.x * cos(t / 15.0) * 80.0 * u_complexity)
                   + cos(position.y * cos(t / 15.0) * 10.0 * u_complexity);
            value += sin(position.y * sin(t / 10.0) * 40.0 * u_complexity)
                   + cos(position.x * sin(t / 25.0) * 40.0 * u_complexity);
            value += sin(position.x * sin(t / 5.0) * 10.0 * u_complexity)
                   + sin(position.y * sin(t / 35.0) * 80.0 * u_complexity);
            value *= sin(t / 10.0) * 0.5;

            // Normalize value to 0-1 range
            float v = value * 0.5 + 0.5;

            // Color cycling
            float ct = u_time * u_color_speed;
            float phase1 = sin(v * 3.14159 + ct) * 0.5 + 0.5;
            float phase2 = sin(v * 3.14159 + ct + 2.094) * 0.5 + 0.5;
            float phase3 = sin(v * 3.14159 + ct + 4.189) * 0.5 + 0.5;

            // Mix the three colors based on phases
            vec3 color = u_color1 * phase1 + u_color2 * phase2 + u_color3 * phase3;
            color = clamp(color, 0.0, 1.0);

            gl_FragColor = vec4(color, origColor.a);
        }
    """)

    # =========================================================================
    # shader.plasma_classic - Classic plasma (original colors preserved)
    # =========================================================================

    # @shader: shader.plasma_classic
    # @description: Classic demoscene plasma with original color formula
    # @animated
    # @param u_speed: float, range=0.2-3.0, default=1.0, description=Animation speed
    # @param u_scale: float, range=0.5-3.0, default=1.0, description=Pattern scale
    # @param u_red_mult: float, range=0.0-2.0, default=1.0, description=Red channel multiplier
    # @param u_green_mult: float, range=0.0-2.0, default=0.5, description=Green channel multiplier
    # @param u_blue_mult: float, range=0.0-2.0, default=0.75, description=Blue channel multiplier
    # @param u_blue_speed: float, range=0.1-2.0, default=1.0, description=Blue channel animation speed
    renpy.register_shader("shader.plasma_classic", variables="""
        uniform sampler2D tex0;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_scale;
        uniform float u_red_mult;
        uniform float u_green_mult;
        uniform float u_blue_mult;
        uniform float u_blue_speed;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        void main() {
            vec4 origColor = texture2D(tex0, v_tex_coord);
            vec2 position = v_tex_coord * u_scale;

            float t = u_time * u_speed;

            // Original wave pattern
            float color = 0.0;
            color += sin(position.x * cos(t / 15.0) * 80.0) + cos(position.y * cos(t / 15.0) * 10.0);
            color += sin(position.y * sin(t / 10.0) * 40.0) + cos(position.x * sin(t / 25.0) * 40.0);
            color += sin(position.x * sin(t / 5.0) * 10.0) + sin(position.y * sin(t / 35.0) * 80.0);
            color *= sin(t / 10.0) * 0.5;

            // Original color formula with adjustable multipliers
            vec3 rgb;
            rgb.r = color * u_red_mult;
            rgb.g = color * u_green_mult;
            rgb.b = sin(color + t / 3.0 * u_blue_speed) * u_blue_mult;

            // Normalize to visible range
            rgb = rgb * 0.5 + 0.5;

            gl_FragColor = vec4(rgb, origColor.a);
        }
    """)

    # =========================================================================
    # shader.plasma_gradient - Plasma with gradient color mapping
    # =========================================================================

    # @shader: shader.plasma_gradient
    # @description: Plasma with smooth gradient between two colors
    # @animated
    # @param u_speed: float, range=0.2-3.0, default=1.0, description=Animation speed
    # @param u_scale: float, range=0.5-3.0, default=1.0, description=Pattern scale
    # @param u_color_low: color, default=#000033, description=Color for low values
    # @param u_color_mid: color, default=#FF00FF, description=Color for mid values
    # @param u_color_high: color, default=#FFFF00, description=Color for high values
    renpy.register_shader("shader.plasma_gradient", variables="""
        uniform sampler2D tex0;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_scale;
        uniform vec3 u_color_low;
        uniform vec3 u_color_mid;
        uniform vec3 u_color_high;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        void main() {
            vec4 origColor = texture2D(tex0, v_tex_coord);
            vec2 position = v_tex_coord * u_scale;

            float t = u_time * u_speed;

            float value = 0.0;
            value += sin(position.x * cos(t / 15.0) * 80.0) + cos(position.y * cos(t / 15.0) * 10.0);
            value += sin(position.y * sin(t / 10.0) * 40.0) + cos(position.x * sin(t / 25.0) * 40.0);
            value += sin(position.x * sin(t / 5.0) * 10.0) + sin(position.y * sin(t / 35.0) * 80.0);
            value *= sin(t / 10.0) * 0.5;

            // Normalize to 0-1
            float v = clamp(value * 0.25 + 0.5, 0.0, 1.0);

            // Three-color gradient
            vec3 color;
            if (v < 0.5) {
                color = mix(u_color_low, u_color_mid, v * 2.0);
            } else {
                color = mix(u_color_mid, u_color_high, (v - 0.5) * 2.0);
            }

            gl_FragColor = vec4(color, origColor.a);
        }
    """)

    # =========================================================================
    # shader.plasma_overlay - Plasma blended with original image
    # =========================================================================

    # @shader: shader.plasma_overlay
    # @description: Plasma effect blended with underlying image
    # @animated
    # @param u_speed: float, range=0.2-3.0, default=1.0, description=Animation speed
    # @param u_scale: float, range=0.5-3.0, default=1.0, description=Pattern scale
    # @param u_opacity: float, range=0.1-1.0, default=0.5, description=Plasma opacity
    # @param u_blend_mode: float, range=0.0-3.0, default=1.0, description=Blend mode (0=mix, 1=screen, 2=multiply, 3=overlay)
    # @param u_color1: color, default=#FF0066, description=Primary color
    # @param u_color2: color, default=#00FFFF, description=Secondary color
    renpy.register_shader("shader.plasma_overlay", variables="""
        uniform sampler2D tex0;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_scale;
        uniform float u_opacity;
        uniform float u_blend_mode;
        uniform vec3 u_color1;
        uniform vec3 u_color2;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        void main() {
            vec4 origColor = texture2D(tex0, v_tex_coord);

            if (origColor.a < 0.01) {
                gl_FragColor = origColor;
                return;
            }

            vec2 position = v_tex_coord * u_scale;
            float t = u_time * u_speed;

            float value = 0.0;
            value += sin(position.x * cos(t / 15.0) * 80.0) + cos(position.y * cos(t / 15.0) * 10.0);
            value += sin(position.y * sin(t / 10.0) * 40.0) + cos(position.x * sin(t / 25.0) * 40.0);
            value += sin(position.x * sin(t / 5.0) * 10.0) + sin(position.y * sin(t / 35.0) * 80.0);
            value *= sin(t / 10.0) * 0.5;

            float v = value * 0.5 + 0.5;
            vec3 plasmaColor = mix(u_color1, u_color2, v);

            // Blend modes
            vec3 result;
            if (u_blend_mode < 0.5) {
                // Simple mix
                result = mix(origColor.rgb, plasmaColor, u_opacity);
            } else if (u_blend_mode < 1.5) {
                // Screen
                vec3 screened = 1.0 - (1.0 - origColor.rgb) * (1.0 - plasmaColor);
                result = mix(origColor.rgb, screened, u_opacity);
            } else if (u_blend_mode < 2.5) {
                // Multiply
                vec3 multiplied = origColor.rgb * plasmaColor;
                result = mix(origColor.rgb, multiplied, u_opacity);
            } else {
                // Additive
                result = origColor.rgb + plasmaColor * u_opacity;
                result = clamp(result, 0.0, 1.0);
            }

            gl_FragColor = vec4(result, origColor.a);
        }
    """)

    # =========================================================================
    # shader.plasma_fire - Fire-colored plasma
    # =========================================================================

    # @shader: shader.plasma_fire
    # @description: Plasma with fire/lava color palette
    # @animated
    # @param u_speed: float, range=0.2-3.0, default=1.5, description=Animation speed
    # @param u_scale: float, range=0.5-3.0, default=1.0, description=Pattern scale
    # @param u_intensity: float, range=0.5-2.0, default=1.0, description=Fire intensity
    renpy.register_shader("shader.plasma_fire", variables="""
        uniform sampler2D tex0;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_scale;
        uniform float u_intensity;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        void main() {
            vec4 origColor = texture2D(tex0, v_tex_coord);
            vec2 position = v_tex_coord * u_scale;

            float t = u_time * u_speed;

            float value = 0.0;
            value += sin(position.x * cos(t / 15.0) * 80.0) + cos(position.y * cos(t / 15.0) * 10.0);
            value += sin(position.y * sin(t / 10.0) * 40.0) + cos(position.x * sin(t / 25.0) * 40.0);
            value += sin(position.x * sin(t / 5.0) * 10.0) + sin(position.y * sin(t / 35.0) * 80.0);
            value *= sin(t / 10.0) * 0.5;

            float v = clamp((value * 0.5 + 0.5) * u_intensity, 0.0, 1.0);

            // Fire gradient: black -> red -> orange -> yellow -> white
            vec3 color;
            if (v < 0.25) {
                color = mix(vec3(0.0, 0.0, 0.0), vec3(0.5, 0.0, 0.0), v * 4.0);
            } else if (v < 0.5) {
                color = mix(vec3(0.5, 0.0, 0.0), vec3(1.0, 0.3, 0.0), (v - 0.25) * 4.0);
            } else if (v < 0.75) {
                color = mix(vec3(1.0, 0.3, 0.0), vec3(1.0, 0.8, 0.0), (v - 0.5) * 4.0);
            } else {
                color = mix(vec3(1.0, 0.8, 0.0), vec3(1.0, 1.0, 0.8), (v - 0.75) * 4.0);
            }

            gl_FragColor = vec4(color, origColor.a);
        }
    """)
