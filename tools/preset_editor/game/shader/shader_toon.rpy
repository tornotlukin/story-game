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
    """, fragment_300="""
        // HSV conversion functions
        vec3 rgb2hsv(vec3 c) {
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

        vec3 hsv2rgb(vec3 hsv) {
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

        // Quantize a value to discrete levels
        float quantize(float val, float levels) {
            return floor(val * levels + 0.5) / levels;
        }

        // Get average pixel intensity
        float avgIntensity(vec4 pix) {
            return (pix.r + pix.g + pix.b) / 3.0;
        }

        // Edge detection using neighbor sampling
        float detectEdge(vec2 uv) {
            vec2 px = 1.0 / u_model_size;
            float pix[9];
            int k = 0;

            // Sample 3x3 neighborhood
            for (int i = -1; i <= 1; i++) {
                for (int j = -1; j <= 1; j++) {
                    vec2 offset = vec2(float(i), float(j)) * px;
                    pix[k] = avgIntensity(texture2D(tex0, uv + offset));
                    k++;
                }
            }

            // Sobel-like edge detection
            float delta = (abs(pix[1] - pix[7]) +
                          abs(pix[5] - pix[3]) +
                          abs(pix[0] - pix[8]) +
                          abs(pix[2] - pix[6])) / 4.0;

            return clamp(u_edge_strength * delta, 0.0, 1.0);
        }

        void main() {
            vec4 color = texture2D(tex0, v_tex_coord);

            // Skip fully transparent pixels
            if (color.a < 0.01) {
                gl_FragColor = color;
                return;
            }

            // Convert to HSV and quantize
            vec3 hsv = rgb2hsv(color.rgb);
            hsv.x = quantize(hsv.x / 360.0, u_hue_levels) * 360.0;
            hsv.y = quantize(hsv.y, u_sat_levels);
            hsv.z = quantize(hsv.z, u_val_levels);

            // Detect edges
            float edge = detectEdge(v_tex_coord);

            // Apply edge as black outline
            vec3 result;
            if (edge >= u_edge_threshold) {
                result = vec3(0.0);  // Black edge
            } else {
                result = hsv2rgb(hsv);
            }

            // Preserve alpha
            gl_FragColor = vec4(result, color.a);
        }
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
    """, fragment_300="""
        // HSV conversion functions
        vec3 rgb2hsv(vec3 c) {
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

        vec3 hsv2rgb(vec3 hsv) {
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

        float quantize(float val, float levels) {
            return floor(val * levels + 0.5) / levels;
        }

        void main() {
            vec4 color = texture2D(tex0, v_tex_coord);

            if (color.a < 0.01) {
                gl_FragColor = color;
                return;
            }

            vec3 hsv = rgb2hsv(color.rgb);
            hsv.x = quantize(hsv.x / 360.0, u_hue_levels) * 360.0;
            hsv.y = quantize(hsv.y, u_sat_levels);
            hsv.z = quantize(hsv.z, u_val_levels);

            vec3 result = hsv2rgb(hsv);
            gl_FragColor = vec4(result, color.a);
        }
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
    """, fragment_300="""
        float avgIntensity(vec4 pix) {
            return (pix.r + pix.g + pix.b) / 3.0;
        }

        float detectEdge(vec2 uv) {
            vec2 px = 1.0 / u_model_size;
            float pix[9];
            int k = 0;

            for (int i = -1; i <= 1; i++) {
                for (int j = -1; j <= 1; j++) {
                    vec2 offset = vec2(float(i), float(j)) * px;
                    pix[k] = avgIntensity(texture2D(tex0, uv + offset));
                    k++;
                }
            }

            float delta = (abs(pix[1] - pix[7]) +
                          abs(pix[5] - pix[3]) +
                          abs(pix[0] - pix[8]) +
                          abs(pix[2] - pix[6])) / 4.0;

            return clamp(u_edge_strength * delta, 0.0, 1.0);
        }

        void main() {
            vec4 color = texture2D(tex0, v_tex_coord);

            if (color.a < 0.01) {
                gl_FragColor = color;
                return;
            }

            float edge = detectEdge(v_tex_coord);
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
