# Shader Development Guide for Ren'Py

This guide covers creating GLSL shaders for Ren'Py 8.x that work with the preset editor tool.

## Documentation References

For detailed Ren'Py shader documentation, refer to:
- **`docs/renpy/model.html`** - Ren'Py shader system, `renpy.register_shader()`, built-in uniforms
- **`docs/renpy/transforms.html`** - Transform properties for applying shaders
- **`docs/SHADER_PORTING_GUIDE.md`** - Guide for porting shaders from other engines

When in doubt, check these docs first.

---

## File Structure

Each shader category gets its own file: `shader_<category>.rpy`

```python
## shader_example.rpy - Brief description
##
## Detailed explanation of shaders in this file.
##
## @tool-category: Example
## @tool-description: Example effects for demonstration

init python:

    # @shader: shader.example_effect
    # @param u_amount: float, range=0.0-1.0, default=0.5, description=Effect intensity
    renpy.register_shader("shader.example_effect", variables="""
        uniform sampler2D tex0;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        // Effect code here
        gl_FragColor = color;
    """)
```

---

## renpy.register_shader() API

```python
renpy.register_shader("shader.name",
    variables="...",      # Uniform/attribute/varying declarations
    vertex_300="...",     # Vertex shader code (GLSL ES 3.0)
    fragment_300="..."    # Fragment shader code (GLSL ES 3.0)
)
```

**Naming Convention:** `shader.<category>_<effect>` (e.g., `shader.blur_gaussian`, `shader.glow_pulse`)

---

## Built-in Ren'Py Uniforms

Always available - do NOT declare these in variables:

| Uniform | Type | Description |
|---------|------|-------------|
| `tex0` | sampler2D | Primary texture (the image being rendered) |
| `tex1`, `tex2` | sampler2D | Additional textures (if needed) |
| `u_model_size` | vec2 | Width and height of the image in pixels |
| `u_time` | float | Time in seconds (for animations, resets daily) |
| `u_random` | vec4 | 4 random floats per frame |
| `u_lod_bias` | float | Level-of-detail bias |

**Required Attributes** (declare in variables):
```glsl
attribute vec2 a_tex_coord;  // Texture coordinates (0-1)
varying vec2 v_tex_coord;    // Pass to fragment shader
```

---

## Shader Template

### Basic Effect (No Animation)

```python
# @shader: shader.category_name
# @param u_amount: float, range=0.0-1.0, default=0.5, description=Effect strength
renpy.register_shader("shader.category_name", variables="""
    uniform sampler2D tex0;
    uniform vec2 u_model_size;
    uniform float u_amount;
    attribute vec2 a_tex_coord;
    varying vec2 v_tex_coord;
""", vertex_300="""
    v_tex_coord = a_tex_coord;
""", fragment_300="""
    vec4 color = texture2D(tex0, v_tex_coord);

    // Your effect code here
    // Modify color.rgb and/or color.a

    gl_FragColor = color;
""")
```

### Animated Effect

```python
# @shader: shader.category_animated
# @animated
# @param u_speed: float, range=0.5-5.0, default=1.0, description=Animation speed
renpy.register_shader("shader.category_animated", variables="""
    uniform sampler2D tex0;
    uniform float u_time;
    uniform float u_speed;
    attribute vec2 a_tex_coord;
    varying vec2 v_tex_coord;
""", vertex_300="""
    v_tex_coord = a_tex_coord;
""", fragment_300="""
    vec4 color = texture2D(tex0, v_tex_coord);

    // Use u_time for animation
    float wave = sin(u_time * u_speed) * 0.5 + 0.5;

    gl_FragColor = color;
""")
```

---

## CRITICAL: Alpha Preservation

Character sprites have transparency. **Always preserve alpha** or you'll get black edges.

### Wrong (destroys transparency):
```glsl
vec3 result = someEffect(color.rgb);
gl_FragColor = vec4(result, 1.0);  // BAD: forces alpha to 1
```

### Correct (preserves transparency):
```glsl
vec3 result = someEffect(color.rgb);
gl_FragColor = vec4(result, color.a);  // GOOD: keeps original alpha
```

### For Multi-Sample Effects (blur, glow):
Weight samples by alpha to avoid dark edges:

```glsl
// Accumulate weighted by alpha
vec3 colorSum = vec3(0.0);
float weightSum = 0.0;
float alphaSum = 0.0;

for (int i = 0; i < SAMPLES; i++) {
    vec4 samp = texture2D(tex0, sampleCoord);
    colorSum += samp.rgb * samp.a;  // Weight color by alpha
    weightSum += samp.a;
    alphaSum += samp.a;
}

vec3 finalColor = weightSum > 0.0 ? colorSum / weightSum : vec3(0.0);
float finalAlpha = alphaSum / float(SAMPLES);
gl_FragColor = vec4(finalColor, finalAlpha);
```

---

## Common Effect Patterns

### Color Tint
```glsl
uniform vec3 u_tint_color;  // Use hex in preset: "#FF5500"
uniform float u_amount;

vec4 color = texture2D(tex0, v_tex_coord);
color.rgb = mix(color.rgb, color.rgb * u_tint_color, u_amount);
gl_FragColor = color;
```

### Grayscale
```glsl
vec4 color = texture2D(tex0, v_tex_coord);
float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
color.rgb = mix(color.rgb, vec3(gray), u_amount);
gl_FragColor = color;
```

### Wave Distortion
```glsl
uniform float u_time;
uniform float u_amplitude;
uniform float u_frequency;

vec2 uv = v_tex_coord;
uv.x += sin(uv.y * u_frequency + u_time) * u_amplitude;
vec4 color = texture2D(tex0, clamp(uv, 0.0, 1.0));
gl_FragColor = color;
```

### Outline/Glow (samples neighbors)
```glsl
vec2 px = 1.0 / u_model_size;  // Pixel size
vec4 center = texture2D(tex0, v_tex_coord);

// Sample in 4 directions
float outline = 0.0;
outline += texture2D(tex0, v_tex_coord + vec2(px.x, 0.0) * u_radius).a;
outline += texture2D(tex0, v_tex_coord - vec2(px.x, 0.0) * u_radius).a;
outline += texture2D(tex0, v_tex_coord + vec2(0.0, px.y) * u_radius).a;
outline += texture2D(tex0, v_tex_coord - vec2(0.0, px.y) * u_radius).a;

// Glow where neighbors have alpha but center doesn't
float glow = clamp(outline - center.a * 4.0, 0.0, 1.0);
```

---

## Transform Definition

After creating a shader, define a transform to apply it:

```python
# In shader_transforms.rpy or same file

transform effect_name:
    shader "shader.category_name"
    u_amount 0.5

# With mesh_pad for effects extending beyond image bounds (glow, blur)
transform glow_effect:
    mesh_pad 50  # Pixels of padding
    shader "shader.glow"
    u_glow_color (1.0, 0.5, 0.0)  # RGB 0-1 format in transforms
    u_strength 0.8
```

**Note:** In transforms, colors are `(r, g, b)` floats 0-1, not hex strings.

---

## Preset Editor Annotations

### File-Level (top of file, first 20 lines)
```python
## @tool-category: CategoryName
## @tool-description: What these shaders do
```

### Shader-Level (before renpy.register_shader)
```python
# @shader: shader.exact_name
# @description: What this specific shader does
# @animated
```

### Parameter Annotations
```python
# @param u_name: type, range=min-max, default=value, description=text
```

**Types:**
| Type | Preset JSON | Transform | Editor Widget |
|------|-------------|-----------|---------------|
| `color` | `"#FF5500"` | `(1.0, 0.33, 0.0)` | Color picker |
| `float` | `0.5` | `0.5` | Slider |
| `int` | `10` | `10` | Number input |

---

## Complete Example: New Glow Shader

```python
## shader_glow.rpy - Glow and aura effects
##
## @tool-category: Glow
## @tool-description: Adds glowing aura effects to sprites

init python:

    # @shader: shader.glow_soft
    # @description: Soft outer glow with customizable color
    # @param u_glow_color: color, default=#FFFFFF, description=Glow color
    # @param u_strength: float, range=0.0-2.0, default=0.6, description=Glow intensity
    # @param u_radius: float, range=1.0-10.0, default=3.0, description=Glow size
    renpy.register_shader("shader.glow_soft", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform vec3 u_glow_color;
        uniform float u_strength;
        uniform float u_radius;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec2 px = 1.0 / u_model_size;
        vec4 center = texture2D(tex0, v_tex_coord);

        // Sample neighbors for glow
        float glowAlpha = 0.0;
        for (float x = -2.0; x <= 2.0; x += 1.0) {
            for (float y = -2.0; y <= 2.0; y += 1.0) {
                vec2 offset = vec2(x, y) * px * u_radius;
                glowAlpha += texture2D(tex0, v_tex_coord + offset).a;
            }
        }
        glowAlpha = glowAlpha / 25.0 * u_strength;

        // Glow behind sprite
        vec3 glow = u_glow_color * glowAlpha * (1.0 - center.a);
        vec3 finalColor = center.rgb + glow;
        float finalAlpha = max(center.a, glowAlpha * 0.5);

        gl_FragColor = vec4(finalColor, finalAlpha);
    """)


# Transform to use this shader
transform glow_soft:
    mesh_pad 30
    shader "shader.glow_soft"
    u_glow_color (1.0, 1.0, 1.0)
    u_strength 0.6
    u_radius 3.0
```

---

## Checklist for New Shaders

- [ ] File named `shader_<category>.rpy`
- [ ] `## @tool-category:` at top of file
- [ ] `# @shader:` annotation before each shader
- [ ] `# @param` annotations for all custom uniforms
- [ ] `# @animated` if shader uses `u_time`
- [ ] Shader name matches: `shader.<category>_<name>`
- [ ] Alpha preservation in fragment shader
- [ ] `clamp(uv, 0.0, 1.0)` for any UV manipulation
- [ ] Transform definition with `mesh_pad` if effect extends bounds
- [ ] Tested in Ren'Py with character sprite

---

## Testing

1. Place .rpy file in `game/shader/`
2. Open preset editor, go to Shaders → Builder
3. Select your shader from dropdown
4. Click "Create New Preset"
5. Adjust parameters and test in demo
