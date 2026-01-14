## shader_color.rpy - Color adjustment shaders
##
## Color manipulation effects including grayscale, sepia, tint, and more.
## All shaders preserve transparency by not modifying transparent pixels.
## Ported from Phaser.js color filters.
##
## Shaders:
##   - shader.color_matrix - Full 4x5 color matrix transformation
##   - shader.color_grayscale - Desaturation to grayscale
##   - shader.color_sepia - Sepia tone effect
##   - shader.color_invert - Color inversion
##   - shader.color_adjust - Brightness/contrast/saturation
##   - shader.color_hue - Hue rotation
##   - shader.color_tint - Color tinting/overlay
##
## Related files: shader_transforms.rpy
##
## @tool-category: Color
## @tool-description: Color adjustment effects (grayscale, sepia, tint, etc.)

init python:

    # @shader: shader.color_matrix
    # @description: Full 4x5 color matrix transformation
    # @param u_alpha: float, range=0.0-1.0, default=1.0, description=Effect intensity
    renpy.register_shader("shader.color_matrix", variables="""
        uniform float u_matrix[20];
        uniform float u_alpha;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser color matrix filter
        vec4 c = texture2D(tex0, v_tex_coord);

        if (u_alpha == 0.0) {
            gl_FragColor = c;
            return;
        }

        if (c.a > 0.0) {
            c.rgb /= c.a;
        }

        vec4 result;
        result.r = (u_matrix[0] * c.r) + (u_matrix[1] * c.g) + (u_matrix[2] * c.b) + (u_matrix[3] * c.a) + u_matrix[4];
        result.g = (u_matrix[5] * c.r) + (u_matrix[6] * c.g) + (u_matrix[7] * c.b) + (u_matrix[8] * c.a) + u_matrix[9];
        result.b = (u_matrix[10] * c.r) + (u_matrix[11] * c.g) + (u_matrix[12] * c.b) + (u_matrix[13] * c.a) + u_matrix[14];
        result.a = (u_matrix[15] * c.r) + (u_matrix[16] * c.g) + (u_matrix[17] * c.b) + (u_matrix[18] * c.a) + u_matrix[19];

        vec3 rgb = mix(c.rgb, result.rgb, u_alpha);
        rgb *= result.a;

        gl_FragColor = vec4(rgb, result.a);
    """)

    # @shader: shader.color_grayscale
    # @description: Desaturation to grayscale
    # @param u_amount: float, range=0.0-1.0, default=1.0, description=Grayscale amount
    renpy.register_shader("shader.color_grayscale", variables="""
        uniform float u_amount;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
        vec3 grayColor = vec3(gray);
        vec3 result = mix(color.rgb, grayColor, u_amount);
        // Preserve original RGB for transparent pixels
        result = mix(color.rgb, result, color.a);
        gl_FragColor = vec4(result, color.a);
    """)

    # @shader: shader.color_sepia
    # @description: Sepia tone vintage effect
    # @param u_amount: float, range=0.0-1.0, default=1.0, description=Sepia intensity
    renpy.register_shader("shader.color_sepia", variables="""
        uniform float u_amount;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        vec3 sepia;
        sepia.r = dot(color.rgb, vec3(0.393, 0.769, 0.189));
        sepia.g = dot(color.rgb, vec3(0.349, 0.686, 0.168));
        sepia.b = dot(color.rgb, vec3(0.272, 0.534, 0.131));
        vec3 result = mix(color.rgb, sepia, u_amount);
        // Preserve original RGB for transparent pixels
        result = mix(color.rgb, result, color.a);
        gl_FragColor = vec4(result, color.a);
    """)

    # Invert Colors - preserves transparency and contrast
    # Uses curved blend to skip the gray zone at 0.5
    renpy.register_shader("shader.color_invert", variables="""
        uniform float u_amount;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        vec3 inverted = 1.0 - color.rgb;

        // Problem: mix(color, inverted, 0.5) = gray for all colors
        // Solution: remap u_amount to skip the problematic 0.5 blend zone
        // Maps: 0->0, 0.5->0.3, 1->1 (first half compressed, second half expanded)
        float t;
        if (u_amount < 0.5) {
            t = u_amount * 0.6;  // 0-0.5 input -> 0-0.3 blend
        } else {
            t = 0.3 + (u_amount - 0.5) * 1.4;  // 0.5-1 input -> 0.3-1 blend
        }

        vec3 result = mix(color.rgb, inverted, t);

        // Preserve original RGB for fully transparent pixels
        result = mix(color.rgb, result, color.a);
        gl_FragColor = vec4(result, color.a);
    """)

    # Brightness/Contrast/Saturation - preserves transparency
    renpy.register_shader("shader.color_adjust", variables="""
        uniform float u_brightness;
        uniform float u_contrast;
        uniform float u_saturation;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);

        // Brightness
        vec3 result = color.rgb + u_brightness;

        // Contrast
        result = (result - 0.5) * u_contrast + 0.5;

        // Saturation
        float gray = dot(result, vec3(0.299, 0.587, 0.114));
        result = mix(vec3(gray), result, u_saturation);

        // Preserve original RGB for transparent pixels to avoid colored edges
        result = clamp(result, 0.0, 1.0);
        result = mix(color.rgb, result, color.a);
        gl_FragColor = vec4(result, color.a);
    """)

    # Hue Shift - preserves transparency
    renpy.register_shader("shader.color_hue", variables="""
        uniform float u_shift;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);

        // RGB to HSV
        float maxC = max(max(color.r, color.g), color.b);
        float minC = min(min(color.r, color.g), color.b);
        float delta = maxC - minC;

        float h = 0.0;
        if (delta > 0.0) {
            if (maxC == color.r) {
                h = mod((color.g - color.b) / delta, 6.0);
            } else if (maxC == color.g) {
                h = (color.b - color.r) / delta + 2.0;
            } else {
                h = (color.r - color.g) / delta + 4.0;
            }
            h /= 6.0;
        }
        float s = maxC > 0.0 ? delta / maxC : 0.0;
        float v = maxC;

        // Shift hue
        h = mod(h + u_shift, 1.0);

        // HSV to RGB
        float c = v * s;
        float x = c * (1.0 - abs(mod(h * 6.0, 2.0) - 1.0));
        float m = v - c;

        vec3 rgb;
        if (h < 1.0/6.0) rgb = vec3(c, x, 0.0);
        else if (h < 2.0/6.0) rgb = vec3(x, c, 0.0);
        else if (h < 3.0/6.0) rgb = vec3(0.0, c, x);
        else if (h < 4.0/6.0) rgb = vec3(0.0, x, c);
        else if (h < 5.0/6.0) rgb = vec3(x, 0.0, c);
        else rgb = vec3(c, 0.0, x);

        vec3 result = rgb + m;
        // Preserve original RGB for transparent pixels
        result = mix(color.rgb, result, color.a);
        gl_FragColor = vec4(result, color.a);
    """)

    # @shader: shader.color_tint
    # @description: Color tint overlay effect
    # @param u_tint_color: color, default=#FFFFFF, description=Tint color
    # @param u_amount: float, range=0.0-1.0, default=0.5, description=Tint intensity
    renpy.register_shader("shader.color_tint", variables="""
        uniform vec4 u_tint_color;
        uniform float u_amount;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        vec3 tinted = color.rgb * u_tint_color.rgb;
        vec3 result = mix(color.rgb, tinted, u_amount);
        // Preserve original RGB for transparent pixels
        result = mix(color.rgb, result, color.a);
        gl_FragColor = vec4(result, color.a);
    """)
