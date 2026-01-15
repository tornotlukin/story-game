## shader_retro.rpy - Retro and stylized effect shaders
##
## Visual effects for retro/vintage aesthetics including pixelation,
## scanlines, vignette, chromatic aberration, and glitch effects.
## Ported from Phaser.js retro filters.
##
## Shaders:
##   - shader.retro_pixelate - Pixelation/mosaic effect (square or rectangular)
##   - shader.retro_scanlines - CRT scanline effect
##   - shader.retro_vignette - Darkened edges
##   - shader.retro_chromatic - RGB channel split
##   - shader.retro_glitch - Digital glitch effect (animated)
##
## @tool-category: Retro
## @tool-description: Retro/vintage effects (pixelate, scanlines, CRT, glitch)

init python:

    # =========================================================================
    # shader.retro_pixelate - Robust pixelation effect
    # =========================================================================

    # @shader: shader.retro_pixelate
    # @description: Pixelation/mosaic effect with optional smoothing and rectangular pixels
    # @param u_pixel_w: float, range=2.0-64.0, default=8.0, description=Pixel width in screen pixels
    # @param u_pixel_h: float, range=2.0-64.0, default=8.0, description=Pixel height in screen pixels (0 = same as width)
    # @param u_smooth: float, range=0.0-1.0, default=0.0, description=Smoothing (0 = crisp/aliased, 1 = anti-aliased)
    renpy.register_shader("shader.retro_pixelate", variables="""
        uniform float u_pixel_w;
        uniform float u_pixel_h;
        uniform float u_smooth;
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Get pixel dimensions (use width for height if height is 0 or not set)
        float pixelW = max(2.0, u_pixel_w);
        float pixelH = u_pixel_h > 0.0 ? max(2.0, u_pixel_h) : pixelW;
        vec2 pixelSize = vec2(pixelW, pixelH);

        vec2 resolution = u_model_size;

        // Find cell center in pixel coordinates
        vec2 cell = floor(v_tex_coord * resolution / pixelSize);
        vec2 cellCenter = (cell + 0.5) * pixelSize;

        // Sample center
        vec2 centerUV = cellCenter / resolution;
        vec4 centerColor = texture2D(tex0, centerUV);

        vec4 pixel;
        if (u_smooth > 0.5) {
            // Anti-aliased mode: 5-tap weighted sampling
            vec2 corner1 = cellCenter + pixelSize * vec2(-0.5, -0.5);
            vec2 corner2 = cellCenter + pixelSize * vec2(0.5, -0.5);
            vec2 corner3 = cellCenter + pixelSize * vec2(0.5, 0.5);
            vec2 corner4 = cellCenter + pixelSize * vec2(-0.5, 0.5);

            pixel = 0.4 * centerColor;
            pixel += 0.15 * texture2D(tex0, corner1 / resolution);
            pixel += 0.15 * texture2D(tex0, corner2 / resolution);
            pixel += 0.15 * texture2D(tex0, corner3 / resolution);
            pixel += 0.15 * texture2D(tex0, corner4 / resolution);
        } else {
            // Crisp mode: single sample from cell center
            pixel = centerColor;
        }

        // Preserve alpha from original position for proper sprite edges
        vec4 origColor = texture2D(tex0, v_tex_coord);
        if (origColor.a < 0.01) {
            pixel.a = 0.0;
        }

        gl_FragColor = pixel;
    """)

    # =========================================================================
    # shader.retro_scanlines - CRT scanline effect
    # =========================================================================

    # @shader: shader.retro_scanlines
    # @description: CRT-style horizontal scanlines
    # @param u_intensity: float, range=0.0-1.0, default=0.3, description=Scanline darkness
    # @param u_count: float, range=100.0-800.0, default=400.0, description=Number of scanlines
    renpy.register_shader("shader.retro_scanlines", variables="""
        uniform float u_intensity;
        uniform float u_count;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        float scanline = sin(v_tex_coord.y * u_count * 3.14159) * 0.5 + 0.5;
        scanline = pow(scanline, 1.5);
        color.rgb *= 1.0 - (u_intensity * (1.0 - scanline));
        gl_FragColor = color;
    """)

    # =========================================================================
    # shader.retro_vignette - Darkened edges
    # =========================================================================

    # @shader: shader.retro_vignette
    # @description: Darkens edges of image (spotlight/tunnel effect)
    # @param u_intensity: float, range=0.0-1.0, default=0.5, description=Edge darkness amount
    # @param u_radius: float, range=0.2-1.0, default=0.6, description=Vignette radius (smaller = more visible)
    renpy.register_shader("shader.retro_vignette", variables="""
        uniform float u_intensity;
        uniform float u_radius;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        vec2 center = v_tex_coord - 0.5;
        float dist = length(center);
        float vignette = smoothstep(u_radius, u_radius - 0.3, dist);
        color.rgb *= mix(1.0 - u_intensity, 1.0, vignette);
        gl_FragColor = color;
    """)

    # =========================================================================
    # shader.retro_chromatic - RGB channel split
    # =========================================================================

    # @shader: shader.retro_chromatic
    # @description: Chromatic aberration (RGB color fringing from center)
    # @param u_amount: float, range=0.0-0.1, default=0.015, description=Separation amount
    renpy.register_shader("shader.retro_chromatic", variables="""
        uniform float u_amount;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec2 dir = v_tex_coord - 0.5;
        float dist = length(dir);
        vec2 offset = dir * dist * u_amount;

        float r = texture2D(tex0, clamp(v_tex_coord + offset, 0.0, 1.0)).r;
        float g = texture2D(tex0, v_tex_coord).g;
        float b = texture2D(tex0, clamp(v_tex_coord - offset, 0.0, 1.0)).b;
        float a = texture2D(tex0, v_tex_coord).a;

        gl_FragColor = vec4(r, g, b, a);
    """)

    # =========================================================================
    # shader.retro_glitch - Digital glitch effect
    # =========================================================================

    # @shader: shader.retro_glitch
    # @description: Animated digital glitch with horizontal tearing and color split
    # @animated
    # @param u_intensity: float, range=0.0-2.0, default=0.6, description=Glitch strength
    # @param u_speed: float, range=0.5-5.0, default=2.0, description=Animation speed
    renpy.register_shader("shader.retro_glitch", variables="""
        uniform float u_intensity;
        uniform float u_speed;
        uniform sampler2D tex0;
        uniform float u_time;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Wrap time to avoid float precision issues
        float t = mod(u_time * u_speed, 628.318);

        // Random-ish function
        float rand = fract(sin(dot(vec2(floor(v_tex_coord.y * 20.0), floor(t * 10.0)), vec2(12.9898, 78.233))) * 43758.5453);

        // Horizontal offset glitch
        float glitchOffset = 0.0;
        if (rand > 0.9) {
            glitchOffset = (rand - 0.9) * 10.0 * u_intensity;
        }

        vec2 uv = v_tex_coord;
        uv.x += glitchOffset * sin(t * 100.0);
        uv = clamp(uv, 0.0, 1.0);

        // Color channel split
        float r = texture2D(tex0, clamp(uv + vec2(u_intensity * 0.01, 0.0), 0.0, 1.0)).r;
        float g = texture2D(tex0, uv).g;
        float b = texture2D(tex0, clamp(uv - vec2(u_intensity * 0.01, 0.0), 0.0, 1.0)).b;
        float a = texture2D(tex0, uv).a;

        gl_FragColor = vec4(r, g, b, a);
    """)
