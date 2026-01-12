## shader_blend.rpy - Blend mode shaders
##
## Photoshop-style blend modes for compositing two textures.
## Uses #define macros instead of inline functions for GPU compatibility.
## Ported from Phaser.js blend filters.
##
## Shaders:
##   - shader.blend_multiply - Multiply blend
##   - shader.blend_screen - Screen blend
##   - shader.blend_overlay - Overlay blend
##   - shader.blend_soft_light - Soft light blend
##   - shader.blend_hard_light - Hard light blend
##   - shader.blend_color_dodge - Color dodge blend
##   - shader.blend_color_burn - Color burn blend
##   - shader.blend_difference - Difference blend
##   - shader.blend_exclusion - Exclusion blend
##
## Related files: shader_transforms.rpy

init python:

    # Multiply Blend
    renpy.register_shader("shader.blend_multiply", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);
        vec4 result = base * blend;
        gl_FragColor = mix(base, result, u_amount);
    """)

    # Screen Blend
    renpy.register_shader("shader.blend_screen", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);
        vec4 result = 1.0 - (1.0 - base) * (1.0 - blend);
        gl_FragColor = mix(base, result, u_amount);
    """)

    # Overlay Blend - inline expressions for GPU compatibility
    renpy.register_shader("shader.blend_overlay", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser overlay blend - inlined for compatibility
        #define OVERLAY(b, l) ((b) < 0.5 ? 2.0 * (b) * (l) : 1.0 - 2.0 * (1.0 - (b)) * (1.0 - (l)))

        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);

        vec4 result = vec4(
            OVERLAY(base.r, blend.r),
            OVERLAY(base.g, blend.g),
            OVERLAY(base.b, blend.b),
            OVERLAY(base.a, blend.a)
        );

        gl_FragColor = mix(base, result, u_amount);
    """)

    # Soft Light Blend - inline expressions for GPU compatibility
    renpy.register_shader("shader.blend_soft_light", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser soft light blend - inlined for compatibility
        #define SOFTLIGHT(b, l) ((l) < 0.5 ? (2.0 * (b) * (l) + (b) * (b) * (1.0 - 2.0 * (l))) : (sqrt(b) * (2.0 * (l) - 1.0) + 2.0 * (b) * (1.0 - (l))))

        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);

        vec4 result = vec4(
            SOFTLIGHT(base.r, blend.r),
            SOFTLIGHT(base.g, blend.g),
            SOFTLIGHT(base.b, blend.b),
            SOFTLIGHT(base.a, blend.a)
        );

        gl_FragColor = mix(base, result, u_amount);
    """)

    # Hard Light Blend - inline expressions for GPU compatibility
    renpy.register_shader("shader.blend_hard_light", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser hard light blend - inlined for compatibility
        #define HARDLIGHT(b, l) ((l) < 0.5 ? 2.0 * (b) * (l) : 1.0 - 2.0 * (1.0 - (b)) * (1.0 - (l)))

        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);

        vec4 result = vec4(
            HARDLIGHT(base.r, blend.r),
            HARDLIGHT(base.g, blend.g),
            HARDLIGHT(base.b, blend.b),
            HARDLIGHT(base.a, blend.a)
        );

        gl_FragColor = mix(base, result, u_amount);
    """)

    # Color Dodge Blend - inline expressions for GPU compatibility
    renpy.register_shader("shader.blend_color_dodge", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser color dodge blend - inlined for compatibility
        #define DODGE(b, l) ((l) >= 1.0 ? (l) : min(1.0, (b) / (1.0 - (l))))

        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);

        vec4 result = vec4(
            DODGE(base.r, blend.r),
            DODGE(base.g, blend.g),
            DODGE(base.b, blend.b),
            DODGE(base.a, blend.a)
        );

        gl_FragColor = mix(base, result, u_amount);
    """)

    # Color Burn Blend - inline expressions for GPU compatibility
    renpy.register_shader("shader.blend_color_burn", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser color burn blend - inlined for compatibility
        #define BURN(b, l) ((l) <= 0.0 ? (l) : 1.0 - min(1.0, (1.0 - (b)) / (l)))

        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);

        vec4 result = vec4(
            BURN(base.r, blend.r),
            BURN(base.g, blend.g),
            BURN(base.b, blend.b),
            BURN(base.a, blend.a)
        );

        gl_FragColor = mix(base, result, u_amount);
    """)

    # Difference Blend
    renpy.register_shader("shader.blend_difference", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);
        vec4 result = abs(base - blend);
        gl_FragColor = mix(base, result, u_amount);
    """)

    # Exclusion Blend
    renpy.register_shader("shader.blend_exclusion", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_blend_texture;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 base = texture2D(tex0, v_tex_coord);
        vec4 blend = texture2D(u_blend_texture, v_tex_coord);
        vec4 result = base + blend - 2.0 * base * blend;
        gl_FragColor = mix(base, result, u_amount);
    """)
