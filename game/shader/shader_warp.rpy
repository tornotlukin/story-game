## shader_warp.rpy - Time warp and fractal tunnel effects
##
## Psychedelic fractal patterns that create tunnel, vortex, and
## time-travel style visual effects through iterative coordinate warping.
##
## Shaders:
##   - shader.warp_tunnel - Fractal time-warp tunnel effect
##   - shader.warp_tunnel_overlay - Time warp as overlay on images
##   - shader.warp_vortex - Spinning vortex variation
##   - shader.warp_hyperspace - Star Wars style hyperspace (replaces image)
##   - shader.warp_hyperspace_overlay - Hyperspace blended with image
##   - shader.warp_triangle_tunnel - Triangular fractal tunnel
##   - shader.warp_triangle_colored - Colorful triangular tunnel
##
## @tool-category: Warp
## @tool-description: Time warp, fractal tunnel, and vortex effects

init python:

    # =========================================================================
    # shader.warp_tunnel - Fractal time-warp tunnel
    # =========================================================================

    # @shader: shader.warp_tunnel
    # @description: Psychedelic fractal tunnel effect (time travel style)
    # @animated
    # @param u_speed: float, range=100.0-2000.0, default=888.0, description=Animation speed
    # @param u_rotation: float, range=0.0-1.0, default=0.25, description=Rotation amount per iteration
    # @param u_wave_factor: float, range=0.1-2.0, default=1.0, description=Wave distortion intensity
    # @param u_iterations: float, range=10.0-60.0, default=40.0, description=Fractal iterations (higher = more detail)
    # @param u_zoom: float, range=5.0-30.0, default=15.0, description=Zoom level
    # @param u_color_shift: float, range=0.0-2.0, default=1.0, description=Color variation
    renpy.register_shader("shader.warp_tunnel", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_rotation;
        uniform float u_wave_factor;
        uniform float u_iterations;
        uniform float u_zoom;
        uniform float u_color_shift;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        // Convert UV to centered coordinates
        vec2 uv = v_tex_coord - 0.5;
        float aspect = u_model_size.x / u_model_size.y;
        uv.x *= aspect;
        vec2 v = uv * u_zoom;

        float t = u_time * u_speed;

        // Rotation angle
        float angle = u_rotation * 6.28318530718;
        float c = cos(angle);
        float s = sin(angle);

        // Fractal iteration
        int N = int(u_iterations);
        for (int i = 1; i <= 60; i++) {
            if (i > N) break;

            float d = float(i + 3) / float(N);
            float x = v.x;
            float y = v.y + sin(v.x * d * 3.0 + t) / d * u_wave_factor
                          + cos(v.x * d + t) / d * u_wave_factor;

            // Rotate
            v.x = x * c - y * s;
            v.y = x * s + y * c;
        }

        // Color based on distance from center
        float col = length(v) * 0.25;

        // Trippy color mapping
        vec3 color;
        color.r = cos(col * u_color_shift);
        color.g = cos(col * 2.0 * u_color_shift);
        color.b = cos(col * 4.0 * u_color_shift);

        // Normalize to 0-1 range (cos returns -1 to 1)
        color = color * 0.5 + 0.5;

        gl_FragColor = vec4(color, origColor.a);
    """)

    # =========================================================================
    # shader.warp_tunnel_overlay - Time warp overlay on images
    # =========================================================================

    # @shader: shader.warp_tunnel_overlay
    # @description: Time warp effect blended with original image
    # @animated
    # @param u_speed: float, range=100.0-2000.0, default=500.0, description=Animation speed
    # @param u_rotation: float, range=0.0-1.0, default=0.2, description=Rotation per iteration
    # @param u_wave_factor: float, range=0.1-2.0, default=0.8, description=Wave intensity
    # @param u_iterations: float, range=10.0-60.0, default=30.0, description=Fractal detail
    # @param u_zoom: float, range=5.0-30.0, default=12.0, description=Zoom level
    # @param u_opacity: float, range=0.1-1.0, default=0.5, description=Effect opacity
    # @param u_blend_mode: float, range=0.0-2.0, default=1.0, description=Blend (0=mix, 1=screen, 2=overlay)
    renpy.register_shader("shader.warp_tunnel_overlay", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_rotation;
        uniform float u_wave_factor;
        uniform float u_iterations;
        uniform float u_zoom;
        uniform float u_opacity;
        uniform float u_blend_mode;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        if (origColor.a < 0.01) {
            gl_FragColor = origColor;
            return;
        }

        vec2 uv = v_tex_coord - 0.5;
        float aspect = u_model_size.x / u_model_size.y;
        uv.x *= aspect;
        vec2 v = uv * u_zoom;

        float t = u_time * u_speed;

        float angle = u_rotation * 6.28318530718;
        float c = cos(angle);
        float s = sin(angle);

        int N = int(u_iterations);
        for (int i = 1; i <= 60; i++) {
            if (i > N) break;

            float d = float(i + 3) / float(N);
            float x = v.x;
            float y = v.y + sin(v.x * d * 3.0 + t) / d * u_wave_factor
                          + cos(v.x * d + t) / d * u_wave_factor;

            v.x = x * c - y * s;
            v.y = x * s + y * c;
        }

        float col = length(v) * 0.25;
        vec3 warpColor;
        warpColor.r = cos(col) * 0.5 + 0.5;
        warpColor.g = cos(col * 2.0) * 0.5 + 0.5;
        warpColor.b = cos(col * 4.0) * 0.5 + 0.5;

        // Blend modes
        vec3 result;
        if (u_blend_mode < 0.5) {
            // Simple mix
            result = mix(origColor.rgb, warpColor, u_opacity);
        } else if (u_blend_mode < 1.5) {
            // Screen blend
            vec3 screened = 1.0 - (1.0 - origColor.rgb) * (1.0 - warpColor);
            result = mix(origColor.rgb, screened, u_opacity);
        } else {
            // Additive
            result = origColor.rgb + warpColor * u_opacity;
            result = clamp(result, 0.0, 1.0);
        }

        gl_FragColor = vec4(result, origColor.a);
    """)

    # =========================================================================
    # shader.warp_vortex - Spinning vortex variation
    # =========================================================================

    # @shader: shader.warp_vortex
    # @description: Spinning vortex/portal effect
    # @animated
    # @param u_speed: float, range=0.5-5.0, default=2.0, description=Spin speed
    # @param u_twist: float, range=1.0-20.0, default=8.0, description=Twist intensity
    # @param u_arms: float, range=2.0-12.0, default=5.0, description=Number of spiral arms
    # @param u_zoom: float, range=1.0-10.0, default=3.0, description=Zoom level
    # @param u_color1: color, default=#0066FF, description=Primary color
    # @param u_color2: color, default=#FF00FF, description=Secondary color
    # @param u_color3: color, default=#00FFFF, description=Tertiary color
    renpy.register_shader("shader.warp_vortex", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_twist;
        uniform float u_arms;
        uniform float u_zoom;
        uniform vec3 u_color1;
        uniform vec3 u_color2;
        uniform vec3 u_color3;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        vec2 uv = v_tex_coord - 0.5;
        float aspect = u_model_size.x / u_model_size.y;
        uv.x *= aspect;

        // Polar coordinates
        float dist = length(uv) * u_zoom;
        float angle = atan(uv.y, uv.x);

        // Twist based on distance
        angle += dist * u_twist + u_time * u_speed;

        // Spiral pattern
        float spiral = sin(angle * u_arms + dist * 10.0 - u_time * u_speed * 5.0);
        spiral = spiral * 0.5 + 0.5;

        // Radial pulse
        float pulse = sin(dist * 8.0 - u_time * u_speed * 3.0) * 0.5 + 0.5;

        // Color mixing
        float t = spiral * pulse;
        vec3 color;
        if (t < 0.33) {
            color = mix(u_color1, u_color2, t * 3.0);
        } else if (t < 0.66) {
            color = mix(u_color2, u_color3, (t - 0.33) * 3.0);
        } else {
            color = mix(u_color3, u_color1, (t - 0.66) * 3.0);
        }

        // Center glow
        float glow = 1.0 - smoothstep(0.0, 0.5, dist / u_zoom);
        color += glow * 0.3;

        gl_FragColor = vec4(color, origColor.a);
    """)

    # =========================================================================
    # shader.warp_hyperspace - Hyperspace jump effect
    # =========================================================================

    # @shader: shader.warp_hyperspace
    # @description: Star Wars style hyperspace streaks
    # @animated
    # @param u_speed: float, range=1.0-10.0, default=5.0, description=Travel speed
    # @param u_streak_length: float, range=0.1-1.0, default=0.5, description=Star streak length
    # @param u_density: float, range=0.1-1.0, default=0.5, description=Star density
    # @param u_color_core: color, default=#FFFFFF, description=Streak core color
    # @param u_color_edge: color, default=#6699FF, description=Streak edge color
    renpy.register_shader("shader.warp_hyperspace", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_streak_length;
        uniform float u_density;
        uniform vec3 u_color_core;
        uniform vec3 u_color_edge;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        vec2 uv = v_tex_coord - 0.5;
        float aspect = u_model_size.x / u_model_size.y;
        uv.x *= aspect;

        float time = u_time * u_speed;

        // Polar coordinates
        float dist = length(uv);
        float angle = atan(uv.y, uv.x);

        // Convert angle to grid cell
        float angleSegments = 100.0 * u_density;
        float angleCell = floor(angle / 6.28318 * angleSegments);

        // Radial streaks
        float streak = 0.0;
        for (int layer = 0; layer < 3; layer++) {
            float layerOffset = float(layer) * 0.33;

            // Random per-segment values using simple hash
            float randAngle = fract(sin(dot(vec2(angleCell, float(layer)), vec2(127.1, 311.7))) * 43758.5453);
            float randDist = fract(sin(dot(vec2(angleCell + 100.0, float(layer)), vec2(127.1, 311.7))) * 43758.5453);

            // Streak position (moves outward over time)
            float streakPos = fract(randDist + time * (0.5 + randAngle * 0.5));
            float streakDist = streakPos;

            // Distance from this streak
            float d = abs(dist - streakDist);

            // Streak shape - longer as it goes outward
            float streakWidth = 0.003 + streakPos * 0.01;

            // Check if we're on the streak
            float angleDiff = abs(fract((angle / 6.28318 * angleSegments) - angleCell) - 0.5);
            if (d < streakWidth && angleDiff < 0.5) {
                float brightness = (1.0 - d / streakWidth) * streakPos;
                streak = max(streak, brightness);
            }
        }

        // Color gradient from edge to core based on brightness
        vec3 streakColor = mix(u_color_edge, u_color_core, streak);

        // Background is dark with subtle blue
        vec3 bgColor = vec3(0.0, 0.0, 0.02);

        vec3 result = bgColor + streakColor * streak;

        gl_FragColor = vec4(result, origColor.a);
    """)

    # =========================================================================
    # shader.warp_hyperspace_overlay - Hyperspace blended with image
    # =========================================================================

    # @shader: shader.warp_hyperspace_overlay
    # @description: Hyperspace streaks blended with original image
    # @animated
    # @param u_speed: float, range=1.0-10.0, default=5.0, description=Travel speed
    # @param u_streak_length: float, range=0.1-1.0, default=0.5, description=Star streak length
    # @param u_density: float, range=0.1-1.0, default=0.5, description=Star density
    # @param u_color_core: color, default=#FFFFFF, description=Streak core color
    # @param u_color_edge: color, default=#6699FF, description=Streak edge color
    # @param u_opacity: float, range=0.1-1.0, default=0.6, description=Effect opacity
    # @param u_blend_mode: float, range=0.0-2.0, default=1.0, description=Blend (0=mix, 1=screen, 2=additive)
    renpy.register_shader("shader.warp_hyperspace_overlay", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_streak_length;
        uniform float u_density;
        uniform vec3 u_color_core;
        uniform vec3 u_color_edge;
        uniform float u_opacity;
        uniform float u_blend_mode;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        if (origColor.a < 0.01) {
            gl_FragColor = origColor;
            return;
        }

        vec2 uv = v_tex_coord - 0.5;
        float aspect = u_model_size.x / u_model_size.y;
        uv.x *= aspect;

        float time = u_time * u_speed;

        // Polar coordinates
        float dist = length(uv);
        float angle = atan(uv.y, uv.x);

        // Convert angle to grid cell
        float angleSegments = 100.0 * u_density;
        float angleCell = floor(angle / 6.28318 * angleSegments);

        // Radial streaks
        float streak = 0.0;
        for (int layer = 0; layer < 3; layer++) {
            float layerOffset = float(layer) * 0.33;

            // Random per-segment values using simple hash
            float randAngle = fract(sin(dot(vec2(angleCell, float(layer)), vec2(127.1, 311.7))) * 43758.5453);
            float randDist = fract(sin(dot(vec2(angleCell + 100.0, float(layer)), vec2(127.1, 311.7))) * 43758.5453);

            // Streak position (moves outward over time)
            float streakPos = fract(randDist + time * (0.5 + randAngle * 0.5));
            float streakDist = streakPos;

            // Distance from this streak
            float d = abs(dist - streakDist);

            // Streak shape - longer as it goes outward
            float streakWidth = 0.003 + streakPos * 0.01;

            // Check if we're on the streak
            float angleDiff = abs(fract((angle / 6.28318 * angleSegments) - angleCell) - 0.5);
            if (d < streakWidth && angleDiff < 0.5) {
                float brightness = (1.0 - d / streakWidth) * streakPos;
                streak = max(streak, brightness);
            }
        }

        // Color gradient from edge to core based on brightness
        vec3 streakColor = mix(u_color_edge, u_color_core, streak);
        vec3 hyperColor = streakColor * streak;

        // Blend with original image
        vec3 result;
        if (u_blend_mode < 0.5) {
            // Simple mix
            result = mix(origColor.rgb, hyperColor, u_opacity * streak);
        } else if (u_blend_mode < 1.5) {
            // Screen blend (brightens)
            vec3 screened = 1.0 - (1.0 - origColor.rgb) * (1.0 - hyperColor);
            result = mix(origColor.rgb, screened, u_opacity);
        } else {
            // Additive (glow effect)
            result = origColor.rgb + hyperColor * u_opacity;
            result = clamp(result, 0.0, 1.0);
        }

        gl_FragColor = vec4(result, origColor.a);
    """)

    # =========================================================================
    # shader.warp_triangle_tunnel - Triangular fractal tunnel
    # =========================================================================

    # @shader: shader.warp_triangle_tunnel
    # @description: Hypnotic triangular fractal tunnel effect
    # @animated
    # @param u_speed: float, range=0.5-5.0, default=1.0, description=Animation speed
    # @param u_bands: float, range=4.0-32.0, default=16.0, description=Number of color bands
    # @param u_band_speed: float, range=4.0-32.0, default=16.0, description=Band animation speed
    # @param u_iterations: float, range=5.0-20.0, default=15.0, description=Fractal iterations
    # @param u_zoom: float, range=0.05-0.3, default=0.1, description=Zoom level
    # @param u_color1: color, default=#FFFFFF, description=Primary color
    # @param u_color2: color, default=#000000, description=Secondary color
    renpy.register_shader("shader.warp_triangle_tunnel", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_bands;
        uniform float u_band_speed;
        uniform float u_iterations;
        uniform float u_zoom;
        uniform vec3 u_color1;
        uniform vec3 u_color2;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        // Center and aspect correct
        vec2 position = v_tex_coord * 2.0 - 1.0;
        float aspect = u_model_size.x / u_model_size.y;
        position.x *= aspect;

        // Inline fractal distance calculation
        vec2 p = position / u_zoom;
        float d = 1.0;
        float n = 1.0;
        vec2 s = vec2(1.0, -1.0);

        float t = u_time * u_speed;
        float S = sin(t / 3.14159) * cos(t * 0.125443);
        float C = cos(t / 3.14159) * sin(t * 0.195483);

        int maxIter = int(u_iterations);
        for (int i = 0; i < 20; i++) {
            if (i >= maxIter) break;

            // Triangle distance
            float triDist = max(abs(p.x) * 0.866025 + p.y * 0.5, -p.y) - 55.5;
            d = min(d, triDist);

            // Line distances
            vec2 v1 = vec2(-0.866, -0.5);
            vec2 w1 = vec2(-0.866, -n * C);
            float l2_1 = distance(w1, v1);
            l2_1 *= l2_1;
            float t1 = clamp(dot(p - v1, w1 - v1) / max(l2_1, 0.0001), 0.0, 1.0);
            d = min(d, distance(p, v1 + t1 * (w1 - v1)));

            vec2 v2 = vec2(-0.866, -2.0);
            vec2 w2 = vec2(0.866 * 2.0 * n * S, -2.0);
            float l2_2 = distance(w2, v2);
            l2_2 *= l2_2;
            float t2 = clamp(dot(p - v2, w2 - v2) / max(l2_2, 0.0001), 0.0, 1.0);
            d = min(d, distance(p, v2 + t2 * (w2 - v2)));

            n += 1.0;
            p += s * S;
            p.xy = vec2(p.x * C - p.y * S, p.y * C + p.x * S) + s;
            s = -s;
        }

        // Color banding
        float band = sin(d * u_bands + u_time * u_band_speed) * 0.5 + 0.5;

        // Mix between two colors
        vec3 color = mix(u_color2, u_color1, band);

        gl_FragColor = vec4(color, origColor.a);
    """)

    # =========================================================================
    # shader.warp_triangle_colored - Colorful triangular tunnel
    # =========================================================================

    # @shader: shader.warp_triangle_colored
    # @description: Triangular tunnel with rainbow coloring
    # @animated
    # @param u_speed: float, range=0.5-5.0, default=1.0, description=Animation speed
    # @param u_bands: float, range=4.0-32.0, default=12.0, description=Color bands
    # @param u_iterations: float, range=5.0-20.0, default=15.0, description=Fractal detail
    # @param u_zoom: float, range=0.05-0.3, default=0.1, description=Zoom level
    # @param u_saturation: float, range=0.0-1.0, default=0.8, description=Color saturation
    # @param u_brightness: float, range=0.5-1.0, default=0.9, description=Color brightness
    renpy.register_shader("shader.warp_triangle_colored", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_bands;
        uniform float u_iterations;
        uniform float u_zoom;
        uniform float u_saturation;
        uniform float u_brightness;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        vec2 position = v_tex_coord * 2.0 - 1.0;
        float aspect = u_model_size.x / u_model_size.y;
        position.x *= aspect;

        // Inline fractal distance calculation
        vec2 p = position / u_zoom;
        float d = 1.0;
        float n = 1.0;
        vec2 s = vec2(1.0, -1.0);

        float t = u_time * u_speed;
        float S = sin(t / 3.14159) * cos(t * 0.125443);
        float C = cos(t / 3.14159) * sin(t * 0.195483);

        int maxIter = int(u_iterations);
        for (int i = 0; i < 20; i++) {
            if (i >= maxIter) break;

            // Triangle distance
            float triDist = max(abs(p.x) * 0.866025 + p.y * 0.5, -p.y) - 55.5;
            d = min(d, triDist);

            // Line distances
            vec2 v1 = vec2(-0.866, -0.5);
            vec2 w1 = vec2(-0.866, -n * C);
            float l2_1 = distance(w1, v1);
            l2_1 *= l2_1;
            float t1 = clamp(dot(p - v1, w1 - v1) / max(l2_1, 0.0001), 0.0, 1.0);
            d = min(d, distance(p, v1 + t1 * (w1 - v1)));

            vec2 v2 = vec2(-0.866, -2.0);
            vec2 w2 = vec2(0.866 * 2.0 * n * S, -2.0);
            float l2_2 = distance(w2, v2);
            l2_2 *= l2_2;
            float t2 = clamp(dot(p - v2, w2 - v2) / max(l2_2, 0.0001), 0.0, 1.0);
            d = min(d, distance(p, v2 + t2 * (w2 - v2)));

            n += 1.0;
            p += s * S;
            p.xy = vec2(p.x * C - p.y * S, p.y * C + p.x * S) + s;
            s = -s;
        }

        // HSV to RGB inline
        float hue = fract(d * 0.1 + u_time * 0.1);
        vec3 c = clamp(abs(fract(hue + vec3(0.0, 2.0/3.0, 1.0/3.0)) * 6.0 - 3.0) - 1.0, 0.0, 1.0);
        vec3 color = mix(vec3(1.0), c, u_saturation) * u_brightness;

        // Add banding for extra visual interest
        float band = sin(d * u_bands + u_time * 10.0) * 0.2 + 0.8;
        color *= band;

        gl_FragColor = vec4(color, origColor.a);
    """)
