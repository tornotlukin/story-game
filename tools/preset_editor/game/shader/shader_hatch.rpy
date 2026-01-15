## shader_hatch.rpy - Crosshatching and sketch effects
##
## Creates pencil sketch and engraving-style rendering using crosshatch
## line patterns. Darker areas get more overlapping lines.
##
## Shaders:
##   - shader.hatch_cross - Crosshatching based on luminance thresholds
##   - shader.hatch_simple - Single-direction hatching
##
## @tool-category: Hatch
## @tool-description: Crosshatching and pencil sketch effects

init python:

    # =========================================================================
    # shader.hatch_cross - Full crosshatching effect
    # =========================================================================

    # @shader: shader.hatch_cross
    # @description: Crosshatching sketch effect with 4 luminance levels
    # @param u_line_spacing: float, range=4.0-20.0, default=10.0, description=Space between hatch lines
    # @param u_line_offset: float, range=0.0-10.0, default=5.0, description=Offset for second line pair
    # @param u_threshold_1: float, range=0.0-2.0, default=1.0, description=Luminance threshold for first hatch layer
    # @param u_threshold_2: float, range=0.0-2.0, default=0.7, description=Luminance threshold for second hatch layer
    # @param u_threshold_3: float, range=0.0-2.0, default=0.5, description=Luminance threshold for third hatch layer
    # @param u_threshold_4: float, range=0.0-2.0, default=0.3, description=Luminance threshold for fourth hatch layer
    # @param u_line_color: color, default=#000000, description=Hatch line color
    # @param u_bg_color: color, default=#FFFFFF, description=Background/paper color
    renpy.register_shader("shader.hatch_cross", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_line_spacing;
        uniform float u_line_offset;
        uniform float u_threshold_1;
        uniform float u_threshold_2;
        uniform float u_threshold_3;
        uniform float u_threshold_4;
        uniform vec3 u_line_color;
        uniform vec3 u_bg_color;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        // Skip transparent pixels
        if (origColor.a < 0.01) {
            gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
            return;
        }

        // Calculate luminance
        float lum = length(origColor.rgb);

        // Start with background color
        vec3 result = u_bg_color;

        // Get pixel coordinates for line pattern
        vec2 pixelCoord = v_tex_coord * u_model_size;
        float spacing = max(2.0, u_line_spacing);

        // Layer 1: diagonal lines (top-left to bottom-right)
        if (lum < u_threshold_1) {
            if (mod(pixelCoord.x + pixelCoord.y, spacing) < 1.0) {
                result = u_line_color;
            }
        }

        // Layer 2: opposite diagonal (top-right to bottom-left)
        if (lum < u_threshold_2) {
            if (mod(pixelCoord.x - pixelCoord.y, spacing) < 1.0) {
                result = u_line_color;
            }
        }

        // Layer 3: offset diagonal (denser shading)
        if (lum < u_threshold_3) {
            if (mod(pixelCoord.x + pixelCoord.y - u_line_offset, spacing) < 1.0) {
                result = u_line_color;
            }
        }

        // Layer 4: offset opposite diagonal (darkest areas)
        if (lum < u_threshold_4) {
            if (mod(pixelCoord.x - pixelCoord.y - u_line_offset, spacing) < 1.0) {
                result = u_line_color;
            }
        }

        gl_FragColor = vec4(result, origColor.a);
    """)

    # =========================================================================
    # shader.hatch_simple - Single-direction hatching
    # =========================================================================

    # @shader: shader.hatch_simple
    # @description: Simple single-direction hatching (faster)
    # @param u_line_spacing: float, range=4.0-20.0, default=8.0, description=Space between hatch lines
    # @param u_angle: float, range=0.0-3.14159, default=0.785, description=Line angle in radians (0.785 = 45 degrees)
    # @param u_threshold: float, range=0.0-2.0, default=0.8, description=Luminance threshold for hatching
    # @param u_line_color: color, default=#000000, description=Hatch line color
    # @param u_bg_color: color, default=#FFFFFF, description=Background color
    renpy.register_shader("shader.hatch_simple", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_line_spacing;
        uniform float u_angle;
        uniform float u_threshold;
        uniform vec3 u_line_color;
        uniform vec3 u_bg_color;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        if (origColor.a < 0.01) {
            gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
            return;
        }

        float lum = length(origColor.rgb);
        vec3 result = u_bg_color;

        vec2 pixelCoord = v_tex_coord * u_model_size;
        float spacing = max(2.0, u_line_spacing);

        // Rotate coordinates by angle
        float c = cos(u_angle);
        float s = sin(u_angle);
        float rotated = pixelCoord.x * c + pixelCoord.y * s;

        if (lum < u_threshold) {
            if (mod(rotated, spacing) < 1.0) {
                result = u_line_color;
            }
        }

        gl_FragColor = vec4(result, origColor.a);
    """)

    # =========================================================================
    # shader.hatch_color - Crosshatching that preserves color tint
    # =========================================================================

    # @shader: shader.hatch_color
    # @description: Crosshatching that blends with original colors
    # @param u_line_spacing: float, range=4.0-20.0, default=10.0, description=Space between hatch lines
    # @param u_line_offset: float, range=0.0-10.0, default=5.0, description=Offset for second line pair
    # @param u_threshold_1: float, range=0.0-2.0, default=1.0, description=First threshold
    # @param u_threshold_2: float, range=0.0-2.0, default=0.7, description=Second threshold
    # @param u_threshold_3: float, range=0.0-2.0, default=0.5, description=Third threshold
    # @param u_threshold_4: float, range=0.0-2.0, default=0.3, description=Fourth threshold
    # @param u_color_mix: float, range=0.0-1.0, default=0.3, description=How much original color to preserve
    renpy.register_shader("shader.hatch_color", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_line_spacing;
        uniform float u_line_offset;
        uniform float u_threshold_1;
        uniform float u_threshold_2;
        uniform float u_threshold_3;
        uniform float u_threshold_4;
        uniform float u_color_mix;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        if (origColor.a < 0.01) {
            gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
            return;
        }

        float lum = length(origColor.rgb);

        // Background is tinted by original color
        vec3 bgColor = mix(vec3(1.0), origColor.rgb, u_color_mix);
        vec3 lineColor = mix(vec3(0.0), origColor.rgb * 0.2, u_color_mix);

        vec3 result = bgColor;

        vec2 pixelCoord = v_tex_coord * u_model_size;
        float spacing = max(2.0, u_line_spacing);

        if (lum < u_threshold_1) {
            if (mod(pixelCoord.x + pixelCoord.y, spacing) < 1.0) {
                result = lineColor;
            }
        }

        if (lum < u_threshold_2) {
            if (mod(pixelCoord.x - pixelCoord.y, spacing) < 1.0) {
                result = lineColor;
            }
        }

        if (lum < u_threshold_3) {
            if (mod(pixelCoord.x + pixelCoord.y - u_line_offset, spacing) < 1.0) {
                result = lineColor;
            }
        }

        if (lum < u_threshold_4) {
            if (mod(pixelCoord.x - pixelCoord.y - u_line_offset, spacing) < 1.0) {
                result = lineColor;
            }
        }

        gl_FragColor = vec4(result, origColor.a);
    """)
