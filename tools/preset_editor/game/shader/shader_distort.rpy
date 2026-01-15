## shader_distort.rpy - Distortion effect shaders
##
## Spatial distortion effects including barrel, wave, ripple, and shake.
## Animated shaders use time wrapping to avoid float precision issues.
## Ported from Phaser.js distortion filters.
##
## Shaders:
##   - shader.distort_barrel - Fisheye/barrel distortion
##   - shader.distort_displacement - Displacement map
##   - shader.distort_wave - Horizontal wave (animated)
##   - shader.distort_ripple - Circular ripple (animated)
##   - shader.distort_shake - Screen shake/jitter (animated)
##
## Related files: shader_transforms.rpy

init python:

    # Barrel/Fisheye Distortion - Ported from Phaser barrel.js
    renpy.register_shader("shader.distort_barrel", variables="""
        uniform float u_amount;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser barrel distortion
        vec2 xy = 2.0 * v_tex_coord - 1.0;
        vec2 texCoord = v_tex_coord;

        if (length(xy) < 1.0) {
            float theta = atan(xy.y, xy.x);
            float radius = pow(length(xy), u_amount);
            texCoord = 0.5 * (vec2(radius * cos(theta), radius * sin(theta)) + 1.0);
        }

        gl_FragColor = texture2D(tex0, clamp(texCoord, 0.0, 1.0));
    """)

    # Displacement Map - Ported from Phaser displacement.js
    renpy.register_shader("shader.distort_displacement", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_displacement_map;
        uniform vec2 u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser displacement filter
        vec2 disp = (-vec2(0.5, 0.5) + texture2D(u_displacement_map, v_tex_coord).rg) * u_amount;
        gl_FragColor = texture2D(tex0, clamp(v_tex_coord + disp, 0.0, 1.0));
    """)

    # Wave Distortion (horizontal waves)
    renpy.register_shader("shader.distort_wave", variables="""
        uniform float u_amplitude;
        uniform float u_frequency;
        uniform float u_speed;
        uniform sampler2D tex0;
        uniform float u_time;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Wrap time to avoid float precision issues
        float wrapped_time = mod(u_time, 628.318);
        float wave = sin(v_tex_coord.y * u_frequency + wrapped_time * u_speed) * u_amplitude;
        vec2 texCoord = clamp(v_tex_coord + vec2(wave, 0.0), 0.0, 1.0);
        gl_FragColor = texture2D(tex0, texCoord);
    """)

    # Ripple Distortion (circular waves from center)
    renpy.register_shader("shader.distort_ripple", variables="""
        uniform float u_amplitude;
        uniform float u_frequency;
        uniform float u_speed;
        uniform vec2 u_center;
        uniform sampler2D tex0;
        uniform float u_time;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Wrap time to avoid float precision issues
        float wrapped_time = mod(u_time, 628.318);
        vec2 delta = v_tex_coord - u_center;
        float dist = length(delta);
        float wave = sin(dist * u_frequency - wrapped_time * u_speed) * u_amplitude;
        vec2 dir = normalize(delta + 0.0001);
        vec2 texCoord = clamp(v_tex_coord + dir * wave, 0.0, 1.0);
        gl_FragColor = texture2D(tex0, texCoord);
    """)

    # Screen shake/jitter
    renpy.register_shader("shader.distort_shake", variables="""
        uniform float u_intensity;
        uniform float u_speed;
        uniform sampler2D tex0;
        uniform float u_time;
        uniform vec2 u_model_size;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Wrap time to avoid float precision issues
        float t = mod(u_time * u_speed, 628.318);
        vec2 offset = vec2(
            sin(t * 17.0) * cos(t * 23.0),
            sin(t * 19.0) * cos(t * 29.0)
        ) * u_intensity / u_model_size;
        gl_FragColor = texture2D(tex0, clamp(v_tex_coord + offset, 0.0, 1.0));
    """)
