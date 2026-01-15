## shader_stitch.rpy - Cross-stitch and embroidery effects
##
## Creates a needlework/embroidery appearance by rendering images as
## cross-stitch patterns on a fabric-like background.
##
## Shaders:
##   - shader.stitch_cross - Cross-stitch embroidery effect
##   - shader.stitch_cross_colored - Cross-stitch with custom background color
##
## @tool-category: Stitch
## @tool-description: Cross-stitch and embroidery effects

init python:

    # =========================================================================
    # shader.stitch_cross - Cross-stitch embroidery effect
    # =========================================================================

    # @shader: shader.stitch_cross
    # @description: Cross-stitch embroidery effect with X-pattern stitches
    # @param u_stitch_size: float, range=4.0-20.0, default=6.0, description=Size of each stitch cell in pixels
    # @param u_invert: float, range=0.0-1.0, default=0.0, description=Invert stitch and background (1.0 = inverted)
    # @param u_brightness: float, range=1.0-2.0, default=1.4, description=Stitch color brightness boost
    renpy.register_shader("shader.stitch_cross", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_stitch_size;
        uniform float u_invert;
        uniform float u_brightness;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        void main() {
            float size = max(2.0, u_stitch_size);

            // Convert UV to pixel coordinates
            vec2 pixelPos = v_tex_coord * u_model_size;

            // Find top-left corner of current stitch cell
            vec2 cellPos = floor(pixelPos / size) * size;

            // Position within the cell
            vec2 localPos = mod(pixelPos, size);
            int remX = int(localPos.x);
            int remY = int(localPos.y);

            // Bottom-left of cell (for anti-diagonal check)
            vec2 blPos = cellPos;
            blPos.y += (size - 1.0);

            // Check if pixel is on a diagonal (the X stitch pattern)
            // Main diagonal: remX == remY
            // Anti-diagonal: distance from bottom-left
            bool onDiagonal = (remX == remY);
            bool onAntiDiag = (int(pixelPos.x) - int(cellPos.x)) == (int(blPos.y) - int(pixelPos.y));
            bool isStitch = onDiagonal || onAntiDiag;

            // Sample color from cell's top-left corner
            vec2 sampleUV = cellPos / u_model_size;
            vec4 stitchColor = texture2D(tex0, sampleUV) * u_brightness;

            // Dark fabric background color
            vec4 fabricColor = vec4(0.2, 0.15, 0.05, 1.0);

            // Determine output based on invert mode
            vec4 result;
            if (u_invert > 0.5) {
                // Inverted: fabric on stitches, color on background
                result = isStitch ? fabricColor : stitchColor;
            } else {
                // Normal: color on stitches, dark on background
                result = isStitch ? stitchColor : vec4(0.0, 0.0, 0.0, 1.0);
            }

            // Preserve alpha from original image
            // Only show effect where original has opacity
            vec4 origColor = texture2D(tex0, v_tex_coord);
            result.a = origColor.a;

            // Fade background in transparent areas
            if (!isStitch && origColor.a < 0.5) {
                result.a = 0.0;
            }

            gl_FragColor = result;
        }
    """)

    # =========================================================================
    # shader.stitch_cross_colored - Cross-stitch with custom colors
    # =========================================================================

    # @shader: shader.stitch_cross_colored
    # @description: Cross-stitch with customizable fabric background color
    # @param u_stitch_size: float, range=4.0-20.0, default=6.0, description=Size of each stitch cell in pixels
    # @param u_fabric_color: color, default=#1A1308, description=Background fabric color
    # @param u_brightness: float, range=1.0-2.0, default=1.4, description=Stitch color brightness boost
    # @param u_show_fabric: float, range=0.0-1.0, default=1.0, description=Show fabric between stitches (0 = transparent)
    renpy.register_shader("shader.stitch_cross_colored", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_stitch_size;
        uniform vec3 u_fabric_color;
        uniform float u_brightness;
        uniform float u_show_fabric;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        void main() {
            float size = max(2.0, u_stitch_size);

            vec2 pixelPos = v_tex_coord * u_model_size;
            vec2 cellPos = floor(pixelPos / size) * size;
            vec2 localPos = mod(pixelPos, size);
            int remX = int(localPos.x);
            int remY = int(localPos.y);

            vec2 blPos = cellPos;
            blPos.y += (size - 1.0);

            bool onDiagonal = (remX == remY);
            bool onAntiDiag = (int(pixelPos.x) - int(cellPos.x)) == (int(blPos.y) - int(pixelPos.y));
            bool isStitch = onDiagonal || onAntiDiag;

            vec2 sampleUV = cellPos / u_model_size;
            vec4 stitchColor = texture2D(tex0, sampleUV) * u_brightness;
            vec4 origColor = texture2D(tex0, v_tex_coord);

            vec4 result;
            if (isStitch) {
                result = vec4(stitchColor.rgb, origColor.a);
            } else {
                if (u_show_fabric > 0.5 && origColor.a > 0.1) {
                    result = vec4(u_fabric_color, origColor.a);
                } else {
                    result = vec4(0.0, 0.0, 0.0, 0.0);
                }
            }

            gl_FragColor = result;
        }
    """)

    # =========================================================================
    # shader.stitch_pixel - Simplified pixelated stitch (no X pattern)
    # =========================================================================

    # @shader: shader.stitch_pixel
    # @description: Pixelated grid effect without X pattern (faster)
    # @param u_stitch_size: float, range=4.0-20.0, default=8.0, description=Size of each cell in pixels
    # @param u_gap: float, range=0.0-4.0, default=1.0, description=Gap between cells (grid lines)
    # @param u_gap_color: color, default=#1A1308, description=Grid line color
    renpy.register_shader("shader.stitch_pixel", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_stitch_size;
        uniform float u_gap;
        uniform vec3 u_gap_color;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        void main() {
            float size = max(2.0, u_stitch_size);

            vec2 pixelPos = v_tex_coord * u_model_size;
            vec2 cellPos = floor(pixelPos / size) * size;
            vec2 localPos = mod(pixelPos, size);

            // Check if in gap area (edges of cell)
            bool inGap = localPos.x < u_gap || localPos.y < u_gap;

            // Sample from cell center
            vec2 sampleUV = (cellPos + size * 0.5) / u_model_size;
            vec4 cellColor = texture2D(tex0, sampleUV);
            vec4 origColor = texture2D(tex0, v_tex_coord);

            vec4 result;
            if (inGap && origColor.a > 0.1) {
                result = vec4(u_gap_color, origColor.a);
            } else {
                result = vec4(cellColor.rgb, origColor.a);
            }

            // Clear fully transparent areas
            if (origColor.a < 0.01) {
                result.a = 0.0;
            }

            gl_FragColor = result;
        }
    """)
