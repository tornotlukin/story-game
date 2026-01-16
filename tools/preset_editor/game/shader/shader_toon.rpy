## shader_toon.rpy - Toon/cel-shading effects
##
## Cartoon-style rendering with color quantization and edge detection.
## Creates a hand-drawn/comic book appearance by reducing color levels
## and adding black outlines around edges.
##
## Shaders:
##   - shader.toon_cel - Full cel-shading with edge detection
##   - shader.toon_posterize - Color posterization only (no edges)
##   - shader.toon_edges - Edge detection only (no color change)
##   - shader.toon_simple - Fast RGB-based posterization
##
## @tool-category: Toon
## @tool-description: Cartoon/cel-shading effects with edge detection

init python:

    # =========================================================================
    # shader.toon_cel - Full cel-shading with edges
    # =========================================================================

    # @shader: shader.toon_cel
    # @description: Full cartoon/cel-shading with color quantization and black edges
    # @param u_hue_levels: float, range=2.0-12.0, default=6.0, description=Number of hue levels
    # @param u_sat_levels: float, range=2.0-10.0, default=7.0, description=Number of saturation levels
    # @param u_val_levels: float, range=2.0-8.0, default=4.0, description=Number of value/brightness levels
    # @param u_edge_threshold: float, range=0.05-0.5, default=0.2, description=Edge detection sensitivity
    # @param u_edge_strength: float, range=1.0-10.0, default=5.0, description=Edge darkness multiplier
    renpy.register_shader("shader.toon_cel", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_hue_levels;
        uniform float u_sat_levels;
        uniform float u_val_levels;
        uniform float u_edge_threshold;
        uniform float u_edge_strength;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_functions="""
        vec3 toon_rgb2hsv(vec3 c) {
            float minC = min(min(c.r, c.g), c.b);
            float maxC = max(max(c.r, c.g), c.b);
            float delta = maxC - minC;
            vec3 hsv;
            hsv.z = maxC;
            if (maxC == 0.0) { hsv.x = 0.0; hsv.y = 0.0; return hsv; }
            hsv.y = delta / maxC;
            if (delta == 0.0) { hsv.x = 0.0; return hsv; }
            if (c.r == maxC) { hsv.x = (c.g - c.b) / delta; }
            else if (c.g == maxC) { hsv.x = 2.0 + (c.b - c.r) / delta; }
            else { hsv.x = 4.0 + (c.r - c.g) / delta; }
            hsv.x *= 60.0;
            if (hsv.x < 0.0) hsv.x += 360.0;
            return hsv;
        }

        vec3 toon_hsv2rgb(vec3 hsv) {
            if (hsv.y == 0.0) { return vec3(hsv.z); }
            float h = hsv.x / 60.0;
            int i = int(floor(h));
            float f = h - float(i);
            float p = hsv.z * (1.0 - hsv.y);
            float q = hsv.z * (1.0 - hsv.y * f);
            float t = hsv.z * (1.0 - hsv.y * (1.0 - f));
            vec3 rgb;
            if (i == 0) { rgb = vec3(hsv.z, t, p); }
            else if (i == 1) { rgb = vec3(q, hsv.z, p); }
            else if (i == 2) { rgb = vec3(p, hsv.z, t); }
            else if (i == 3) { rgb = vec3(p, q, hsv.z); }
            else if (i == 4) { rgb = vec3(t, p, hsv.z); }
            else { rgb = vec3(hsv.z, p, q); }
            return rgb;
        }

        float toon_quantize(float val, float levels) {
            return floor(val * levels + 0.5) / levels;
        }

        float toon_avgIntensity(vec4 pix) {
            return (pix.r + pix.g + pix.b) / 3.0;
        }
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);

        // Skip fully transparent pixels
        if (color.a < 0.01) {
            gl_FragColor = color;
            return;
        }

        // Edge detection using neighbor sampling
        vec2 px = 1.0 / u_model_size;
        float pix0 = toon_avgIntensity(texture2D(tex0, v_tex_coord + vec2(-1.0, -1.0) * px));
        float pix1 = toon_avgIntensity(texture2D(tex0, v_tex_coord + vec2(0.0, -1.0) * px));
        float pix2 = toon_avgIntensity(texture2D(tex0, v_tex_coord + vec2(1.0, -1.0) * px));
        float pix3 = toon_avgIntensity(texture2D(tex0, v_tex_coord + vec2(-1.0, 0.0) * px));
        float pix5 = toon_avgIntensity(texture2D(tex0, v_tex_coord + vec2(1.0, 0.0) * px));
        float pix6 = toon_avgIntensity(texture2D(tex0, v_tex_coord + vec2(-1.0, 1.0) * px));
        float pix7 = toon_avgIntensity(texture2D(tex0, v_tex_coord + vec2(0.0, 1.0) * px));
        float pix8 = toon_avgIntensity(texture2D(tex0, v_tex_coord + vec2(1.0, 1.0) * px));

        float delta = (abs(pix1 - pix7) + abs(pix5 - pix3) + abs(pix0 - pix8) + abs(pix2 - pix6)) / 4.0;
        float edge = clamp(u_edge_strength * delta, 0.0, 1.0);

        // Convert to HSV and quantize
        vec3 hsv = toon_rgb2hsv(color.rgb);
        hsv.x = toon_quantize(hsv.x / 360.0, u_hue_levels) * 360.0;
        hsv.y = toon_quantize(hsv.y, u_sat_levels);
        hsv.z = toon_quantize(hsv.z, u_val_levels);

        // Apply edge as black outline
        vec3 result;
        if (edge >= u_edge_threshold) {
            result = vec3(0.0);  // Black edge
        } else {
            result = toon_hsv2rgb(hsv);
        }

        gl_FragColor = vec4(result, color.a);
    """)

    # =========================================================================
    # shader.toon_posterize - Color quantization only
    # =========================================================================

    # @shader: shader.toon_posterize
    # @description: Posterization effect - reduces colors to discrete levels
    # @param u_hue_levels: float, range=2.0-12.0, default=6.0, description=Number of hue levels
    # @param u_sat_levels: float, range=2.0-10.0, default=5.0, description=Number of saturation levels
    # @param u_val_levels: float, range=2.0-8.0, default=4.0, description=Number of value/brightness levels
    renpy.register_shader("shader.toon_posterize", variables="""
        uniform sampler2D tex0;
        uniform float u_hue_levels;
        uniform float u_sat_levels;
        uniform float u_val_levels;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_functions="""
        vec3 post_rgb2hsv(vec3 c) {
            float minC = min(min(c.r, c.g), c.b);
            float maxC = max(max(c.r, c.g), c.b);
            float delta = maxC - minC;
            vec3 hsv;
            hsv.z = maxC;
            if (maxC == 0.0) { hsv.x = 0.0; hsv.y = 0.0; return hsv; }
            hsv.y = delta / maxC;
            if (delta == 0.0) { hsv.x = 0.0; return hsv; }
            if (c.r == maxC) { hsv.x = (c.g - c.b) / delta; }
            else if (c.g == maxC) { hsv.x = 2.0 + (c.b - c.r) / delta; }
            else { hsv.x = 4.0 + (c.r - c.g) / delta; }
            hsv.x *= 60.0;
            if (hsv.x < 0.0) hsv.x += 360.0;
            return hsv;
        }

        vec3 post_hsv2rgb(vec3 hsv) {
            if (hsv.y == 0.0) { return vec3(hsv.z); }
            float h = hsv.x / 60.0;
            int i = int(floor(h));
            float f = h - float(i);
            float p = hsv.z * (1.0 - hsv.y);
            float q = hsv.z * (1.0 - hsv.y * f);
            float t = hsv.z * (1.0 - hsv.y * (1.0 - f));
            vec3 rgb;
            if (i == 0) { rgb = vec3(hsv.z, t, p); }
            else if (i == 1) { rgb = vec3(q, hsv.z, p); }
            else if (i == 2) { rgb = vec3(p, hsv.z, t); }
            else if (i == 3) { rgb = vec3(p, q, hsv.z); }
            else if (i == 4) { rgb = vec3(t, p, hsv.z); }
            else { rgb = vec3(hsv.z, p, q); }
            return rgb;
        }

        float post_quantize(float val, float levels) {
            return floor(val * levels + 0.5) / levels;
        }
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);

        if (color.a < 0.01) {
            gl_FragColor = color;
            return;
        }

        vec3 hsv = post_rgb2hsv(color.rgb);
        hsv.x = post_quantize(hsv.x / 360.0, u_hue_levels) * 360.0;
        hsv.y = post_quantize(hsv.y, u_sat_levels);
        hsv.z = post_quantize(hsv.z, u_val_levels);

        vec3 result = post_hsv2rgb(hsv);
        gl_FragColor = vec4(result, color.a);
    """)

    # =========================================================================
    # shader.toon_edges - Edge detection only
    # =========================================================================

    # @shader: shader.toon_edges
    # @description: Edge detection with customizable outline color
    # @param u_edge_threshold: float, range=0.05-0.5, default=0.15, description=Edge detection sensitivity
    # @param u_edge_strength: float, range=1.0-10.0, default=5.0, description=Edge detection multiplier
    # @param u_edge_color: color, default=#000000, description=Edge/outline color
    # @param u_edge_only: float, range=0.0-1.0, default=0.0, description=1.0 shows only edges
    renpy.register_shader("shader.toon_edges", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_edge_threshold;
        uniform float u_edge_strength;
        uniform vec3 u_edge_color;
        uniform float u_edge_only;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_functions="""
        float edge_avgIntensity(vec4 pix) {
            return (pix.r + pix.g + pix.b) / 3.0;
        }
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);

        if (color.a < 0.01) {
            gl_FragColor = color;
            return;
        }

        vec2 px = 1.0 / u_model_size;
        float pix0 = edge_avgIntensity(texture2D(tex0, v_tex_coord + vec2(-1.0, -1.0) * px));
        float pix1 = edge_avgIntensity(texture2D(tex0, v_tex_coord + vec2(0.0, -1.0) * px));
        float pix2 = edge_avgIntensity(texture2D(tex0, v_tex_coord + vec2(1.0, -1.0) * px));
        float pix3 = edge_avgIntensity(texture2D(tex0, v_tex_coord + vec2(-1.0, 0.0) * px));
        float pix5 = edge_avgIntensity(texture2D(tex0, v_tex_coord + vec2(1.0, 0.0) * px));
        float pix6 = edge_avgIntensity(texture2D(tex0, v_tex_coord + vec2(-1.0, 1.0) * px));
        float pix7 = edge_avgIntensity(texture2D(tex0, v_tex_coord + vec2(0.0, 1.0) * px));
        float pix8 = edge_avgIntensity(texture2D(tex0, v_tex_coord + vec2(1.0, 1.0) * px));

        float delta = (abs(pix1 - pix7) + abs(pix5 - pix3) + abs(pix0 - pix8) + abs(pix2 - pix6)) / 4.0;
        float edge = clamp(u_edge_strength * delta, 0.0, 1.0);
        float isEdge = step(u_edge_threshold, edge);

        vec3 result;
        if (u_edge_only > 0.5) {
            // Edge-only mode: show edges as colored lines on transparent
            result = u_edge_color;
            float alpha = isEdge * color.a;
            gl_FragColor = vec4(result, alpha);
        } else {
            // Normal mode: overlay edges on original
            result = mix(color.rgb, u_edge_color, isEdge);
            gl_FragColor = vec4(result, color.a);
        }
    """)

    # =========================================================================
    # shader.toon_simple - Simplified cel-shading for performance
    # =========================================================================

    # @shader: shader.toon_simple
    # @description: Simple posterization using RGB levels (faster than HSV)
    # @param u_levels: float, range=2.0-16.0, default=4.0, description=Color levels per channel
    renpy.register_shader("shader.toon_simple", variables="""
        uniform sampler2D tex0;
        uniform float u_levels;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);

        if (color.a < 0.01) {
            gl_FragColor = color;
            return;
        }

        // Simple RGB quantization
        vec3 result = floor(color.rgb * u_levels + 0.5) / u_levels;
        gl_FragColor = vec4(result, color.a);
    """)
