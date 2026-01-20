# Text Shader System - Technical Notes

## Key Discovery: Two Separate Shader Systems

Ren'Py has **two completely separate shader systems**:

1. **Transform/Image Shaders** - Applied to displayables (images, windows) via `shader` transform property
2. **Text Shaders** - Applied to text rendering via `textshader` style property or `{shader}` tags

These systems do NOT interact. You cannot use an image shader on text or vice versa.

---

## Text Shader Requirements

### Enabling Text Shaders
Text shaders MUST be enabled by setting a default:
```renpy
define config.default_textshader = "typewriter"
```

Without this, using `{shader=...}` tags will cause:
```
Exception: The shader tag was given, but text shaders are not in use.
```

### Built-in Text Shaders
- `dissolve` - Fade in character by character
- `typewriter` - Classic typewriter reveal
- `wave` - Sine wave displacement (params: `u__amplitude`, `u__frequency`, `u__wavelength`)
- `jitter` - Random shake (params: `u__jitter` as vec2)
- `zoom` - Zoom in characters
- `flip` - Flip characters horizontally
- `offset` - Move text by fixed amount
- `slowalpha` - Show unrevealed text at low alpha
- `linetexture` / `texture` - Apply texture to text

### Uniform Naming
- Built-in uniforms use `u__` (double underscore) prefix
- Example: `u__amplitude`, `u__frequency`, `u__jitter`
- When specifying in tags, the `u_` or `u__` can be omitted:
  - `{shader=wave:u__amplitude=5.0}` OR `{shader=wave:amplitude=5.0}` both work

---

## Creating Custom Text Shaders

Use `renpy.register_textshader()`:

```renpy
init python:
    renpy.register_textshader(
        "my_shader",  # Name for {shader=my_shader} tags

        variables = """
        uniform float u__my_param;
        uniform float u_text_slow_time;
        attribute vec2 a_text_center;
        attribute float a_text_min_time;
        """,

        vertex_50 = """
        // Vertex shader code here
        // Modify gl_Position to transform text
        """,

        fragment_50 = """
        // Fragment shader code here (optional)
        // Modify gl_FragColor for color effects
        """,

        # Default values for uniforms
        u__my_param = 1.0,
    )
```

### Available Text Shader Variables

**Uniforms (same for all glyphs):**
- `u_text_slow_time` - Time since slow text started
- `u_text_slow_duration` - Duration per character
- `u_text_depth` - 0.0 for main text, 1.0+ for outlines
- `u_text_main` - 1.0 if main text, 0.0 if outline
- `u_time` - Global time (for continuous animations)
- `tex0` - Rendered text texture
- `res0` - Resolution of tex0

**Attributes (per-glyph):**
- `a_text_center` - Center of glyph baseline
- `a_text_index` - Index of glyph (0, 1, 2...)
- `a_text_min_time` / `a_text_max_time` - When glyph should appear
- `a_text_time` - Time for this vertex
- `a_text_ascent` / `a_text_descent` - Font metrics

### Shader Code Conventions
- Use `l__` prefix for local variables in shader code
- Use `u__` prefix for custom uniforms
- Vertex stages: `vertex_50`, `vertex_100`, etc.
- Fragment stages: `fragment_50`, `fragment_100`, etc.

---

## Preset Editor - Current State

### Demo Tab Behavior
- **"Apply to dialog" UNCHECKED**: Tests transitions + image shaders on character sprite only
- **"Apply to dialog" CHECKED**: Tests transitions + image shaders on dialog + text shaders on text

### Text Shader Presets (textshader_presets.json)
```json
{
    "wave_dreamy": {
        "shader": "wave",
        "shader_params": {
            "u__amplitude": 3.0,
            "u__frequency": 2.0
        },
        "text": {
            "font": "DejaVuSans.ttf",
            "size": 26,
            "color": "#DDAAFF",
            ...
        }
    }
}
```

### Demo Generator Output
When text shader is selected, generates tags like:
```renpy
"{shader=wave:u__amplitude=3.0:u__frequency=2.0}Sample text{/shader}"
```

---

## Current Issues & Solutions

### Issue: Text not appearing in demo
**Root Cause**: The "Apply to dialog" mode was showing a separate `dialog_demo` image overlapping with the say window.

**Solution**:
1. For character testing (unchecked): Use standard show/say without text shaders
2. For dialog testing (checked): Use say screen with text shader tags only - no separate dialog image

### Issue: Unknown uniform errors
**Root Cause**: Using wrong uniform names (e.g., `u_wave_amplitude` instead of `u__amplitude`)

**Solution**: Use exact Ren'Py built-in uniform names with `u__` prefix.

---

## Files Modified

- `tools/preset_editor/tabs/demo_tab.py` - Demo generation and UI
- `tools/preset_editor/tabs/textshader_tab.py` - Text shader preset editing
- `tools/preset_editor/modules/demo_generator.py` - Script generation
- `tools/preset_editor/game/screens.rpy` - Test game screens with `config.default_textshader`
- `tools/preset_editor/game/presets/textshader_presets.json` - Preset definitions
- `game/presets/textshader_presets.json` - Main game preset definitions (keep in sync!)

---

## Next Steps

1. Fix demo to use text shaders properly (say screen only, no overlapping dialog image)
2. Consider creating custom text shader registration system (like image shaders)
3. Text shader presets should map to registered text shaders OR built-in ones

---

## References

- [Ren'Py Text Shaders Documentation](https://www.renpy.org/doc/html/textshaders.html)
- [GitHub Issue #5711 - Text shader error](https://github.com/renpy/renpy/issues/5711)
- Local docs: `docs/renpy/textshaders.html`
