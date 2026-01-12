## shader_glow.rpy - Glow effect shaders
##
## Outer glow, inner glow, and animated pulsing glow effects.
## Ported from Phaser.js glow filter.
##
## Shaders:
##   - shader.glow - Static outer/inner glow
##   - shader.glow_pulse - Animated pulsing glow
##
## Related files: shader_transforms.rpy

init python:

    # Outer/Inner Glow Effect - Simple 8-sample version for compatibility
    renpy.register_shader("shader.glow", variables="""
        uniform float u_outer_strength;
        uniform float u_inner_strength;
        uniform vec4 u_glow_color;
        uniform float u_scale;
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec2 px = (1.0 / u_model_size) * u_scale * 9.0;

        float totalAlpha = 0.0;

        // 8 samples in cardinal + diagonal directions (unrolled for compatibility)
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(0.0, px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(0.0, -px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, 0.0), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, 0.0), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, -px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, -px.y), 0.0, 1.0)).a;

        vec4 color = texture2D(tex0, v_tex_coord);
        float alphaRatio = totalAlpha / 8.0;

        // Inner glow
        float innerGlowStrength = min(1.0, (1.0 - alphaRatio) * u_inner_strength * color.a);
        vec4 innerColor = mix(color, u_glow_color, innerGlowStrength);

        // Outer glow
        float outerGlowAlpha = alphaRatio * u_outer_strength * (1.0 - color.a);
        vec4 outerGlowColor = u_glow_color * min(1.0 - innerColor.a, outerGlowAlpha);

        gl_FragColor = innerColor + outerGlowColor;
    """)

    # Pulsing glow (animated) - Simple 8-sample version for compatibility
    renpy.register_shader("shader.glow_pulse", variables="""
        uniform float u_strength;
        uniform float u_speed;
        uniform vec4 u_glow_color;
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Wrap time to avoid float precision issues with large values
        float wrapped_time = mod(u_time, 628.318); // ~100 cycles of 2*PI
        float pulse = (sin(wrapped_time * u_speed) + 1.0) * 0.5;
        float strength = u_strength * (0.5 + pulse * 0.5);

        vec2 px = (1.0 / u_model_size) * (6.0 + pulse * 6.0);

        float totalAlpha = 0.0;

        // 8 samples unrolled for compatibility
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(0.0, px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(0.0, -px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, 0.0), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, 0.0), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, -px.y), 0.0, 1.0)).a;
        totalAlpha += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, -px.y), 0.0, 1.0)).a;

        vec4 color = texture2D(tex0, v_tex_coord);
        float alphaRatio = totalAlpha / 8.0;

        float outerGlowAlpha = alphaRatio * strength * (1.0 - color.a);
        vec4 glowColor = u_glow_color * outerGlowAlpha;

        gl_FragColor = color + glowColor;
    """)
