## shader_glow.rpy - Glow effect shaders
##
## Outer glow, inner glow, and animated pulsing glow effects.
## Ported from Phaser.js glow filter.
##
## Shaders:
##   - shader.glow - Static outer/inner glow (color tint + brightness boost)
##   - shader.glow_pulse - Animated pulsing glow
##
## Related files: shader_transforms.rpy

init python:

    # Glow effect - follows exact same pattern as working color_sepia shader
    # Adds glow color tint and brightness boost
    renpy.register_shader("shader.glow", variables="""
        uniform float u_outer_strength;
        uniform float u_inner_strength;
        uniform vec4 u_glow_color;
        uniform float u_scale;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);

        // Combine inner and outer strength for overall effect
        float strength = u_inner_strength + u_outer_strength;

        // Mix original color with glow color (like sepia does)
        vec3 glowTint;
        glowTint.r = color.r * (1.0 + u_glow_color.r * strength);
        glowTint.g = color.g * (1.0 + u_glow_color.g * strength);
        glowTint.b = color.b * (1.0 + u_glow_color.b * strength);

        // Blend based on strength
        vec3 result = mix(color.rgb, glowTint, strength * 0.5);

        // Preserve original RGB for transparent pixels (CRITICAL - matches working shaders)
        result = mix(color.rgb, result, color.a);

        gl_FragColor = vec4(result, color.a);
    """)

    # Pulsing glow (animated) - Simple color tint that pulses
    # Uses same pattern as working color shaders
    renpy.register_shader("shader.glow_pulse", variables="""
        uniform float u_strength;
        uniform float u_speed;
        uniform vec4 u_glow_color;
        uniform sampler2D tex0;
        uniform float u_time;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);

        // Wrap time to avoid float precision issues
        float wrapped_time = mod(u_time, 628.318);
        float pulse = (sin(wrapped_time * u_speed) + 1.0) * 0.5;
        float strength = u_strength * (0.3 + pulse * 0.7);

        // Apply pulsing glow tint (like static glow but animated)
        vec3 glowTint;
        glowTint.r = color.r * (1.0 + u_glow_color.r * strength);
        glowTint.g = color.g * (1.0 + u_glow_color.g * strength);
        glowTint.b = color.b * (1.0 + u_glow_color.b * strength);

        vec3 result = mix(color.rgb, glowTint, strength * 0.5);

        // Preserve original RGB for transparent pixels
        result = mix(color.rgb, result, color.a);

        gl_FragColor = vec4(result, color.a);
    """)
