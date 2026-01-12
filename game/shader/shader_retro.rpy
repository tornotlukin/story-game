## shader_retro.rpy - Retro and stylized effect shaders
##
## Visual effects for retro/vintage aesthetics including pixelation,
## scanlines, vignette, chromatic aberration, and glitch effects.
## Ported from Phaser.js retro filters.
##
## Shaders:
##   - shader.retro_pixelate - Pixelation/mosaic effect
##   - shader.retro_scanlines - CRT scanline effect
##   - shader.retro_vignette - Darkened edges
##   - shader.retro_chromatic - RGB channel split
##   - shader.retro_glitch - Digital glitch effect (animated)
##
## Related files: shader_transforms.rpy

init python:

    # Pixelate - Ported from Phaser pixelate.js
    renpy.register_shader("shader.retro_pixelate", variables="""
        uniform float u_pixel_size;
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser pixelate filter
        float pixelSize = max(2.0, u_pixel_size);
        vec2 resolution = u_model_size;
        vec2 center = pixelSize * floor(v_tex_coord * resolution / pixelSize) + pixelSize * vec2(0.5, 0.5);
        vec2 corner1 = center + pixelSize * vec2(-0.5, -0.5);
        vec2 corner2 = center + pixelSize * vec2(0.5, -0.5);
        vec2 corner3 = center + pixelSize * vec2(0.5, 0.5);
        vec2 corner4 = center + pixelSize * vec2(-0.5, 0.5);

        vec4 pixel = 0.4 * texture2D(tex0, center / resolution);
        pixel += 0.15 * texture2D(tex0, corner1 / resolution);
        pixel += 0.15 * texture2D(tex0, corner2 / resolution);
        pixel += 0.15 * texture2D(tex0, corner3 / resolution);
        pixel += 0.15 * texture2D(tex0, corner4 / resolution);

        gl_FragColor = pixel;
    """)

    # CRT Scanlines
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

    # Vignette (darkened edges)
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

    # Chromatic Aberration (RGB split)
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

    # Glitch Effect
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
