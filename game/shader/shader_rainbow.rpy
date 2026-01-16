## shader_rainbow.rpy - Rainbow and color cycling effects
##
## Animated rainbow patterns with configurable direction, speed, and style.
## Can be used as overlay effects or standalone patterns.
##
## Shaders:
##   - shader.rainbow_pixel - Pixelated rainbow pattern with flow field
##   - shader.rainbow_gradient - Smooth rainbow gradient overlay
##   - shader.rainbow_tint - Rainbow color cycling tint on images
##
## @tool-category: Rainbow
## @tool-description: Animated rainbow and color cycling effects

init python:

    # =========================================================================
    # shader.rainbow_pixel - Pixelated rainbow with flow field
    # =========================================================================

    # @shader: shader.rainbow_pixel
    # @description: Pixelated rainbow pattern with animated flow field
    # @animated
    # @param u_angle: float, range=0.0-6.28, default=0.785, description=Rainbow direction (radians, 0=right, 1.57=up)
    # @param u_speed: float, range=0.1-5.0, default=1.0, description=Animation speed
    # @param u_scale: float, range=5.0-50.0, default=20.0, description=Pixel grid size
    # @param u_flow_strength: float, range=0.0-0.2, default=0.05, description=Flow field distortion
    # @param u_flow_scale: float, range=1.0-20.0, default=9.0, description=Flow field pattern size
    # @param u_bg_color: color, default=#000000, description=Background color
    # @param u_saturation: float, range=0.5-1.0, default=1.0, description=Rainbow saturation
    renpy.register_shader("shader.rainbow_pixel", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_angle;
        uniform float u_speed;
        uniform float u_scale;
        uniform float u_flow_strength;
        uniform float u_flow_scale;
        uniform vec3 u_bg_color;
        uniform float u_saturation;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_functions="""
        vec3 rbp_digitalRainbow(float value, float sat) {
            float r = clamp(sin(value + 0.0) * 0.5 + 0.5, 0.0, 1.0);
            float g = clamp(sin(value + 2.0944) * 0.5 + 0.5, 0.0, 1.0);
            float b = clamp(sin(value + 4.18879) * 0.5 + 0.5, 0.0, 1.0);
            vec3 rainbow = vec3(r, g, b);
            float gray = dot(rainbow, vec3(0.299, 0.587, 0.114));
            return mix(vec3(gray), rainbow, sat);
        }
    """, fragment_300="""
        vec2 uv = v_tex_coord;
        vec4 origColor = texture2D(tex0, uv);

        float time = u_time * u_speed;

        // Random factor for flow field variation
        float randomFactor = fract(sin(dot(uv, vec2(5555555.9898, 9.233))) * 33758.5453);

        // Flow field direction based on UV and time
        float flowAngle = sin(uv.x * u_flow_scale) + cos(uv.y * u_flow_scale) + time;
        vec2 flowDir = vec2(cos(flowAngle), sin(flowAngle));

        // Apply flow field distortion
        vec2 newUV = uv + flowDir * randomFactor * u_flow_strength;

        // Create pixel grid
        vec2 scaledUV = newUV * u_scale;

        // Checkerboard pattern (determines rainbow vs background)
        float pixelValue = 1.0 - step(0.5, mod(scaledUV.x + scaledUV.y, 2.0));

        // Direction vector for rainbow
        vec2 dir = vec2(cos(u_angle), sin(u_angle));

        // Calculate rainbow phase based on direction
        float rainbowPhase = dot(scaledUV, dir);
        rainbowPhase = mod(time + rainbowPhase, 6.2831);

        // Get rainbow color
        vec3 rainbowColor = rbp_digitalRainbow(rainbowPhase, u_saturation);

        // Combine with background
        vec3 finalColor = mix(u_bg_color, rainbowColor, pixelValue);

        // Preserve alpha from original image
        gl_FragColor = vec4(finalColor, origColor.a);
    """)

    # =========================================================================
    # shader.rainbow_gradient - Smooth rainbow gradient overlay
    # =========================================================================

    # @shader: shader.rainbow_gradient
    # @description: Smooth animated rainbow gradient
    # @animated
    # @param u_angle: float, range=0.0-6.28, default=0.0, description=Gradient direction (radians)
    # @param u_speed: float, range=0.1-3.0, default=0.5, description=Animation speed
    # @param u_frequency: float, range=0.5-5.0, default=1.0, description=Rainbow repetitions
    # @param u_opacity: float, range=0.1-1.0, default=0.5, description=Overlay opacity
    # @param u_blend_mode: float, range=0.0-2.0, default=0.0, description=Blend mode (0=overlay, 1=multiply, 2=screen)
    renpy.register_shader("shader.rainbow_gradient", variables="""
        uniform sampler2D tex0;
        uniform float u_time;
        uniform float u_angle;
        uniform float u_speed;
        uniform float u_frequency;
        uniform float u_opacity;
        uniform float u_blend_mode;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_functions="""
        vec3 rbg_rainbow(float t) {
            float r = sin(t) * 0.5 + 0.5;
            float g = sin(t + 2.0944) * 0.5 + 0.5;
            float b = sin(t + 4.18879) * 0.5 + 0.5;
            return vec3(r, g, b);
        }
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        if (origColor.a < 0.01) {
            gl_FragColor = origColor;
            return;
        }

        // Direction vector
        vec2 dir = vec2(cos(u_angle), sin(u_angle));

        // Calculate position along gradient direction
        float pos = dot(v_tex_coord - 0.5, dir) + 0.5;

        // Rainbow phase
        float phase = pos * u_frequency * 6.2831 + u_time * u_speed;
        vec3 rainbowColor = rbg_rainbow(phase);

        // Blend modes
        vec3 result;
        if (u_blend_mode < 0.5) {
            // Overlay blend
            result = mix(origColor.rgb, rainbowColor, u_opacity);
        } else if (u_blend_mode < 1.5) {
            // Multiply blend
            vec3 multiplied = origColor.rgb * rainbowColor;
            result = mix(origColor.rgb, multiplied, u_opacity);
        } else {
            // Screen blend
            vec3 screened = 1.0 - (1.0 - origColor.rgb) * (1.0 - rainbowColor);
            result = mix(origColor.rgb, screened, u_opacity);
        }

        gl_FragColor = vec4(result, origColor.a);
    """)

    # =========================================================================
    # shader.rainbow_tint - Rainbow color cycling tint
    # =========================================================================

    # @shader: shader.rainbow_tint
    # @description: Cycles image through rainbow colors over time
    # @animated
    # @param u_speed: float, range=0.1-3.0, default=0.5, description=Color cycle speed
    # @param u_intensity: float, range=0.1-1.0, default=0.5, description=Tint intensity
    # @param u_preserve_luminance: float, range=0.0-1.0, default=1.0, description=Keep original brightness
    renpy.register_shader("shader.rainbow_tint", variables="""
        uniform sampler2D tex0;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_intensity;
        uniform float u_preserve_luminance;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_functions="""
        vec3 rbt_rainbow(float t) {
            float r = sin(t) * 0.5 + 0.5;
            float g = sin(t + 2.0944) * 0.5 + 0.5;
            float b = sin(t + 4.18879) * 0.5 + 0.5;
            return vec3(r, g, b);
        }
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        if (origColor.a < 0.01) {
            gl_FragColor = origColor;
            return;
        }

        // Get rainbow color based on time
        float phase = u_time * u_speed;
        vec3 tint = rbt_rainbow(phase);

        // Calculate original luminance
        float lum = dot(origColor.rgb, vec3(0.299, 0.587, 0.114));

        // Apply tint
        vec3 tinted = origColor.rgb * tint;

        // Optionally preserve luminance
        if (u_preserve_luminance > 0.5) {
            float tintedLum = dot(tinted, vec3(0.299, 0.587, 0.114));
            if (tintedLum > 0.01) {
                tinted = tinted * (lum / tintedLum);
            }
        }

        vec3 result = mix(origColor.rgb, tinted, u_intensity);

        gl_FragColor = vec4(result, origColor.a);
    """)

    # =========================================================================
    # shader.rainbow_wave - Rainbow with wave distortion
    # =========================================================================

    # @shader: shader.rainbow_wave
    # @description: Rainbow pattern with animated wave distortion
    # @animated
    # @param u_angle: float, range=0.0-6.28, default=0.0, description=Rainbow direction
    # @param u_speed: float, range=0.1-3.0, default=1.0, description=Animation speed
    # @param u_wave_amp: float, range=0.0-0.1, default=0.02, description=Wave amplitude
    # @param u_wave_freq: float, range=1.0-20.0, default=8.0, description=Wave frequency
    # @param u_frequency: float, range=1.0-10.0, default=3.0, description=Rainbow bands
    # @param u_opacity: float, range=0.1-1.0, default=0.6, description=Effect opacity
    renpy.register_shader("shader.rainbow_wave", variables="""
        uniform sampler2D tex0;
        uniform float u_time;
        uniform float u_angle;
        uniform float u_speed;
        uniform float u_wave_amp;
        uniform float u_wave_freq;
        uniform float u_frequency;
        uniform float u_opacity;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_functions="""
        vec3 rbw_rainbow(float t) {
            float r = sin(t) * 0.5 + 0.5;
            float g = sin(t + 2.0944) * 0.5 + 0.5;
            float b = sin(t + 4.18879) * 0.5 + 0.5;
            return vec3(r, g, b);
        }
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        if (origColor.a < 0.01) {
            gl_FragColor = origColor;
            return;
        }

        float time = u_time * u_speed;

        // Direction vectors (rainbow direction and perpendicular for wave)
        vec2 dir = vec2(cos(u_angle), sin(u_angle));
        vec2 perp = vec2(-dir.y, dir.x);

        // Position along rainbow direction
        float pos = dot(v_tex_coord - 0.5, dir);

        // Add wave distortion perpendicular to direction
        float perpPos = dot(v_tex_coord - 0.5, perp);
        float wave = sin(perpPos * u_wave_freq + time * 2.0) * u_wave_amp;
        pos += wave;

        // Rainbow phase
        float phase = pos * u_frequency * 6.2831 + time;
        vec3 rainbowColor = rbw_rainbow(phase);

        // Blend with original
        vec3 result = mix(origColor.rgb, rainbowColor, u_opacity);

        gl_FragColor = vec4(result, origColor.a);
    """)
