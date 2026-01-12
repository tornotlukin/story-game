## shader_fx.rpy - Special effects and utility shaders
##
## Miscellaneous effects including light rays, threshold, masking,
## outlines, and transition effects.
## Ported from Phaser.js special effects filters.
##
## Shaders:
##   - shader.light_rays - Volumetric light rays
##   - shader.threshold - Threshold/posterize effect
##   - shader.alpha_mask - Alpha masking with texture
##   - shader.outline - Edge outline effect
##   - shader.transition_dissolve - Noise-based dissolve
##   - shader.transition_wipe - Directional wipe
##
## Related files: shader_transforms.rpy

init python:

    # Light rays - use float instead of int for better GPU compatibility
    renpy.register_shader("shader.light_rays", variables="""
        uniform vec2 u_light_position;
        uniform vec4 u_color;
        uniform float u_decay;
        uniform float u_power;
        uniform float u_intensity;
        uniform float u_samples;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser shadow/light rays filter
        const int MAX = 12;

        vec4 texColor = texture2D(tex0, clamp(v_tex_coord, 0.0, 1.0));
        vec2 pc = (u_light_position - v_tex_coord) * u_intensity;
        float shadow = 0.0;
        int sampleCount = int(clamp(u_samples, 1.0, float(MAX)));
        float limit = max(float(MAX), u_samples);

        for (int i = 0; i < MAX; ++i) {
            if (i >= sampleCount) {
                break;
            }
            vec2 sampleCoord = clamp(v_tex_coord + float(i) * u_decay / limit * pc, 0.0, 1.0);
            shadow += texture2D(tex0, sampleCoord).a * u_power;
        }

        float mask = 1.0 - texColor.a;
        gl_FragColor = mix(texColor, u_color, clamp(shadow * mask, 0.0, 1.0));
    """)

    # Threshold - Ported from Phaser threshold.js
    renpy.register_shader("shader.threshold", variables="""
        uniform vec4 u_edge1;
        uniform vec4 u_edge2;
        uniform vec4 u_invert;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser threshold filter
        vec4 color = texture2D(tex0, v_tex_coord);
        color = clamp((color - u_edge1) / (u_edge2 - u_edge1), 0.0, 1.0);
        color = mix(color, 1.0 - color, u_invert);
        gl_FragColor = color;
    """)

    # Alpha mask - use float instead of bool for better GPU compatibility
    # u_invert: 0.0 = normal mask, 1.0 = inverted mask
    renpy.register_shader("shader.alpha_mask", variables="""
        uniform sampler2D tex0;
        uniform sampler2D u_mask_texture;
        uniform float u_invert;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        // Ported from Phaser mask filter
        vec4 color = texture2D(tex0, v_tex_coord);
        vec4 mask = texture2D(u_mask_texture, v_tex_coord);
        float a = mask.a;
        // u_invert >= 0.5 means inverted
        float maskValue = u_invert >= 0.5 ? (1.0 - a) : a;
        color *= maskValue;
        gl_FragColor = color;
    """)

    # Simple Outline
    renpy.register_shader("shader.outline", variables="""
        uniform float u_width;
        uniform vec4 u_outline_color;
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec2 px = u_width / u_model_size;
        vec4 color = texture2D(tex0, v_tex_coord);

        float outline = 0.0;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, 0.0), 0.0, 1.0)).a;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, 0.0), 0.0, 1.0)).a;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(0.0, -px.y), 0.0, 1.0)).a;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(0.0, px.y), 0.0, 1.0)).a;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, -px.y), 0.0, 1.0)).a;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, -px.y), 0.0, 1.0)).a;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(-px.x, px.y), 0.0, 1.0)).a;
        outline += texture2D(tex0, clamp(v_tex_coord + vec2(px.x, px.y), 0.0, 1.0)).a;

        outline = min(1.0, outline);
        float outlineAlpha = outline * (1.0 - color.a);

        vec4 result = mix(u_outline_color * outlineAlpha, color, color.a);
        result.a = max(color.a, outlineAlpha);

        gl_FragColor = result;
    """)

    # Dissolve with pattern
    renpy.register_shader("shader.transition_dissolve", variables="""
        uniform float u_progress;
        uniform float u_smoothness;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);

        // Generate noise pattern
        float noise = fract(sin(dot(v_tex_coord, vec2(12.9898, 78.233))) * 43758.5453);

        float alpha = smoothstep(u_progress - u_smoothness, u_progress + u_smoothness, noise);
        color.a *= alpha;

        gl_FragColor = color;
    """)

    # Wipe transition (directional)
    renpy.register_shader("shader.transition_wipe", variables="""
        uniform float u_progress;
        uniform float u_angle;
        uniform float u_smoothness;
        uniform sampler2D tex0;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);

        vec2 center = v_tex_coord - 0.5;
        float angle = u_angle * 3.14159 / 180.0;
        float proj = dot(center, vec2(cos(angle), sin(angle))) + 0.5;

        float alpha = smoothstep(u_progress - u_smoothness, u_progress + u_smoothness, proj);
        color.a *= alpha;

        gl_FragColor = color;
    """)
