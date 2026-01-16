## shader_vision.rpy - Night vision and thermal imaging effects
##
## Military/surveillance style vision effects with procedural noise
## and vignette masking. No external textures required.
##
## Shaders:
##   - shader.vision_night - Night vision goggles effect
##   - shader.vision_thermal - Thermal/infrared imaging effect
##   - shader.vision_night_dual - Dual-tube binocular style
##
## @tool-category: Vision
## @tool-description: Night vision and thermal imaging effects

init python:

    # =========================================================================
    # shader.vision_night - Night vision goggles effect
    # =========================================================================

    # @shader: shader.vision_night
    # @description: Night vision goggles with noise, glow, and vignette
    # @animated
    # @param u_lum_threshold: float, range=0.0-0.5, default=0.2, description=Luminance threshold for amplification
    # @param u_amplification: float, range=1.0-8.0, default=4.0, description=Dark area color boost
    # @param u_noise_intensity: float, range=0.0-0.5, default=0.2, description=Grain/noise amount
    # @param u_distortion: float, range=0.0-0.02, default=0.005, description=Noise-based distortion
    # @param u_scan_speed: float, range=10.0-100.0, default=50.0, description=Scanning line speed
    # @param u_vision_color: color, default=#19F233, description=Night vision tint color
    # @param u_vignette: float, range=0.0-1.0, default=0.8, description=Edge darkening (goggles effect)
    # @param u_vignette_softness: float, range=0.1-0.5, default=0.3, description=Vignette edge softness
    renpy.register_shader("shader.vision_night", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_lum_threshold;
        uniform float u_amplification;
        uniform float u_noise_intensity;
        uniform float u_distortion;
        uniform float u_scan_speed;
        uniform vec3 u_vision_color;
        uniform float u_vignette;
        uniform float u_vignette_softness;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_functions="""
        float nv_hash(vec2 p) {
            return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
        }

        float nv_noise(vec2 p) {
            vec2 i = floor(p);
            vec2 f = fract(p);
            f = f * f * (3.0 - 2.0 * f);

            float a = nv_hash(i);
            float b = nv_hash(i + vec2(1.0, 0.0));
            float c = nv_hash(i + vec2(0.0, 1.0));
            float d = nv_hash(i + vec2(1.0, 1.0));

            return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
        }
    """, fragment_300="""
        vec2 uv = v_tex_coord;

        // Animated noise offset for scanning effect
        float time = u_time * u_scan_speed;
        vec2 noiseOffset;
        noiseOffset.x = 0.4 * sin(time);
        noiseOffset.y = 0.4 * cos(time);

        // Sample noise at different scales
        vec2 noiseUV = uv * 3.5 + noiseOffset * 0.1;
        float n1 = nv_noise(noiseUV * 50.0);
        float n2 = nv_noise(noiseUV * 100.0 + 50.0);
        float n3 = nv_noise(noiseUV * 25.0 + 100.0);
        vec3 noiseVec = vec3(n1, n2, n3);

        // Apply noise-based distortion to UV
        vec2 distortedUV = uv + (noiseVec.xy - 0.5) * u_distortion;
        distortedUV = clamp(distortedUV, 0.0, 1.0);

        // Sample the scene
        vec4 origColor = texture2D(tex0, distortedUV);

        // Skip fully transparent pixels
        if (origColor.a < 0.01) {
            gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
            return;
        }

        vec3 c = origColor.rgb;

        // Calculate luminance
        float lum = dot(vec3(0.30, 0.59, 0.11), c);

        // Amplify dark areas
        if (lum < u_lum_threshold) {
            c *= u_amplification;
        }

        // Add noise grain
        c += (noiseVec - 0.5) * u_noise_intensity;

        // Apply night vision color tint
        c *= u_vision_color;

        // Procedural vignette mask (goggles effect)
        vec2 center = uv - 0.5;
        float dist = length(center) * 2.0;
        float mask = 1.0 - smoothstep(1.0 - u_vignette_softness - u_vignette,
                                      1.0 - u_vignette_softness, dist);

        c *= mask;

        // Scanline effect (subtle)
        float scanline = sin(uv.y * u_model_size.y * 2.0 + u_time * 10.0) * 0.02 + 0.98;
        c *= scanline;

        gl_FragColor = vec4(c, origColor.a);
    """)

    # =========================================================================
    # shader.vision_thermal - Thermal/infrared imaging effect
    # =========================================================================

    # @shader: shader.vision_thermal
    # @description: Thermal imaging with heat-based coloring
    # @param u_cold_color: color, default=#000066, description=Color for cold/dark areas
    # @param u_mid_color: color, default=#FF0000, description=Color for medium heat
    # @param u_hot_color: color, default=#FFFF00, description=Color for hot/bright areas
    # @param u_contrast: float, range=0.5-3.0, default=1.5, description=Heat contrast
    # @param u_noise_intensity: float, range=0.0-0.3, default=0.1, description=Sensor noise
    renpy.register_shader("shader.vision_thermal", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform vec3 u_cold_color;
        uniform vec3 u_mid_color;
        uniform vec3 u_hot_color;
        uniform float u_contrast;
        uniform float u_noise_intensity;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_functions="""
        float th_hash(vec2 p) {
            return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
        }
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        if (origColor.a < 0.01) {
            gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
            return;
        }

        // Calculate "heat" from luminance
        float heat = dot(vec3(0.30, 0.59, 0.11), origColor.rgb);

        // Apply contrast
        heat = pow(heat, 1.0 / u_contrast);
        heat = clamp(heat, 0.0, 1.0);

        // Add sensor noise
        float noise = (th_hash(v_tex_coord * u_model_size) - 0.5) * u_noise_intensity;
        heat = clamp(heat + noise, 0.0, 1.0);

        // Three-color gradient (cold -> mid -> hot)
        vec3 thermalColor;
        if (heat < 0.5) {
            thermalColor = mix(u_cold_color, u_mid_color, heat * 2.0);
        } else {
            thermalColor = mix(u_mid_color, u_hot_color, (heat - 0.5) * 2.0);
        }

        gl_FragColor = vec4(thermalColor, origColor.a);
    """)

    # =========================================================================
    # shader.vision_night_dual - Dual-tube night vision (two circles)
    # =========================================================================

    # @shader: shader.vision_night_dual
    # @description: Dual-tube night vision goggles (binocular style)
    # @animated
    # @param u_lum_threshold: float, range=0.0-0.5, default=0.2, description=Luminance threshold
    # @param u_amplification: float, range=1.0-8.0, default=4.0, description=Dark area boost
    # @param u_noise_intensity: float, range=0.0-0.5, default=0.15, description=Grain amount
    # @param u_vision_color: color, default=#19F233, description=Night vision tint
    # @param u_tube_radius: float, range=0.2-0.5, default=0.35, description=Each tube radius
    # @param u_tube_spacing: float, range=0.1-0.4, default=0.25, description=Space between tubes
    renpy.register_shader("shader.vision_night_dual", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_lum_threshold;
        uniform float u_amplification;
        uniform float u_noise_intensity;
        uniform vec3 u_vision_color;
        uniform float u_tube_radius;
        uniform float u_tube_spacing;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_functions="""
        float dual_hash(vec2 p) {
            return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
        }

        float dual_noise(vec2 p) {
            vec2 i = floor(p);
            vec2 f = fract(p);
            f = f * f * (3.0 - 2.0 * f);
            float a = dual_hash(i);
            float b = dual_hash(i + vec2(1.0, 0.0));
            float c = dual_hash(i + vec2(0.0, 1.0));
            float d = dual_hash(i + vec2(1.0, 1.0));
            return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
        }
    """, fragment_300="""
        vec2 uv = v_tex_coord;
        vec4 origColor = texture2D(tex0, uv);

        if (origColor.a < 0.01) {
            gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
            return;
        }

        // Aspect ratio
        float aspect = u_model_size.x / u_model_size.y;

        // Two tube centers
        vec2 leftCenter = vec2(0.5 - u_tube_spacing, 0.5);
        vec2 rightCenter = vec2(0.5 + u_tube_spacing, 0.5);

        // Distance to each tube (aspect corrected)
        vec2 toLeft = uv - leftCenter;
        toLeft.x *= aspect;
        float distLeft = length(toLeft);

        vec2 toRight = uv - rightCenter;
        toRight.x *= aspect;
        float distRight = length(toRight);

        // Check if inside either tube
        float inLeft = 1.0 - smoothstep(u_tube_radius - 0.05, u_tube_radius, distLeft);
        float inRight = 1.0 - smoothstep(u_tube_radius - 0.05, u_tube_radius, distRight);
        float mask = max(inLeft, inRight);

        if (mask < 0.01) {
            // Outside tubes - black
            gl_FragColor = vec4(0.0, 0.0, 0.0, origColor.a);
            return;
        }

        vec3 c = origColor.rgb;

        // Luminance amplification
        float lum = dot(vec3(0.30, 0.59, 0.11), c);
        if (lum < u_lum_threshold) {
            c *= u_amplification;
        }

        // Add noise
        float n = dual_noise(uv * 100.0 + u_time * 10.0);
        c += (n - 0.5) * u_noise_intensity;

        // Apply color tint
        c *= u_vision_color;

        // Edge darkening within tubes
        float edgeDark = min(
            1.0 - smoothstep(u_tube_radius * 0.6, u_tube_radius, distLeft),
            1.0 - smoothstep(u_tube_radius * 0.6, u_tube_radius, distRight)
        );
        edgeDark = max(edgeDark, 0.3);

        c *= mask * edgeDark;

        // Scanlines
        float scanline = sin(uv.y * u_model_size.y * 2.0) * 0.03 + 0.97;
        c *= scanline;

        gl_FragColor = vec4(c, origColor.a);
    """)
