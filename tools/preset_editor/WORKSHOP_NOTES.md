# Preset Editor Workshop Notes

**Last Updated:** Text Shaders tab implemented
**Status:** TEXT SHADERS TAB COMPLETE - Ready for testing

---

## Current State of Preset Editor

### What's Working
- **Transition presets**: movement (xoffset/yoffset, xalign/yalign), alpha, scale, rotation, duration, easing
- **Shader presets**: All image shaders with params (colors, floats, ints)
- **Real-time JSON editing**: Changes save immediately to loaded JSON files
- **Proper DearPyGui callbacks**: All using `user_data=` pattern (not lambda defaults)
- **Float precision**: Values rounded to 2 decimal places

### Key Files
- `tools/preset_editor/preset_editor.py` - Main DearPyGui application
- `tools/preset_editor/modules/json_manager.py` - JSON load/save with undo/redo
- `tools/preset_editor/modules/shader_parser.py` - Parses @param annotations from .rpy files
- `tools/preset_editor/config.json` - Points to JSON files being edited
- `game/presets/transition_presets.json` - Transition preset data
- `game/presets/shader_presets.json` - Shader preset data

### Recent Bug Fixes (This Session)
1. **Shader params not saving**: Lambda callbacks had `lambda s, a, k=key, n=name:` pattern where `user_data` (3rd arg) overwrote default `k`. Fixed by using explicit `user_data=(name, key)` and callback functions.
2. **Only save relevant file**: `save("shader")` or `save("transition")` instead of saving both
3. **Float precision noise**: Added `_clean_float()` to round to 2 decimal places

---

## Workshop Topic: Text Box & Text Shading System

### Part 1: Text Boxes - RESOLVED

#### Research Questions & Answers

**Q: Can we apply existing transition/shader presets to text boxes?**
**A: YES.** Text boxes support transforms via the `at` property in screen language.

**Q: Are text boxes special objects in Ren'Py?**
**A: NO.** They are standard displayables. The `window` in the say screen is just a displayable container with a background.

#### Key Decision
**No preset editor changes needed for text boxes.** Existing presets work - implementation is purely on Ren'Py side.

#### Implementation (Ren'Py side only)
```python
# In screens.rpy
default textbox_preset = None
default namebox_preset = None

screen say(who, what):
    window at textbox_preset:
        # existing content...
```

```python
# Usage in scripts
$ textbox_preset = shader_glow_blue
"This text box glows."

$ textbox_preset = preset_slide_left_enter
"This box slides in."

$ textbox_preset = None
"Back to default."
```

#### Note: Shaders on screen elements need `mesh True`
```python
transform shader_textbox_glow:
    mesh True  # Required for shaders on screen elements
    shader "shader.glow"
    u_glow_color (1.0, 0.8, 0.0)
```

---

### Part 2: Text Shaders (Per-Character Effects) - RESEARCHED

**This is fundamentally different from image shaders.**

Text shaders use `renpy.register_textshader()` which operates per-glyph (per character), not per-image.

#### Built-in Text Shaders (Ren'Py provides these)
| Shader | Effect |
|--------|--------|
| `dissolve` | Fade in character by character |
| `flip` | Flip characters as they appear |
| `jitter` | Shake/vibrate characters |
| `linetexture` | Apply texture to text |
| `offset` | Offset text position |
| `slowalpha` | Slow alpha fade during text display |
| `texture` | Apply texture overlay |
| `typewriter` | Classic typewriter reveal |
| `wave` | Sine wave displacement |
| `zoom` | Zoom in characters as they appear |

**Shaders can be combined**: `"typewriter|wave"` applies both effects.

#### How Text Shaders Are Applied (3 methods)
```python
# Method 1: Style property (global or per-style)
style say_dialogue:
    textshader "typewriter"

# Method 2: Text tags (inline, per-string)
"Normal text {shader=wave}wavy text{/shader} normal again."

# Method 3: Config default
define config.default_textshader = "typewriter"
```

#### Text Shader API (from docs)
```python
renpy.register_textshader("custom_effect",
    # Which built-in shaders to include
    include_default=True,  # Include default glyph rendering

    # GLSL variable declarations
    variables="""
        uniform float u_time;
        uniform float u_custom_param;
    """,

    # Shader code sections
    vertex_functions="...",
    vertex_200="...",    # GLES 2.0 vertex
    vertex_300="...",    # GLES 3.0 vertex
    fragment_functions="...",
    fragment_200="...",  # GLES 2.0 fragment
    fragment_300="...",  # GLES 3.0 fragment

    # The key difference: adjust_function
    adjust_function="""
        // Runs per-glyph, can modify:
        // gl_Position - glyph position
        // a_text_* attributes - glyph properties
    """,

    # Default parameter values
    u_custom_param=1.0
)
```

#### Special Text Shader Uniforms/Attributes
| Name | Type | Description |
|------|------|-------------|
| `u_text_slow_time` | float | Time since text started displaying |
| `u_text_slow_duration` | float | How long text has been displaying |
| `u_text_to_drawable` | mat4 | Transform from text to drawable coords |
| `u_text_to_virtual` | mat4 | Transform from text to virtual coords |
| `a_text_index` | float | Character index (0, 1, 2, ...) |
| `a_text_pos` | vec2 | Character position in text |
| `a_text_center` | vec2 | Center of current character |
| `a_text_min_time` | float | When character starts appearing |

#### Key Differences from Image Shaders

| Aspect | Image Shaders | Text Shaders |
|--------|---------------|--------------|
| Registration | `renpy.register_shader()` | `renpy.register_textshader()` |
| Operates on | Whole image | Per-glyph (character) |
| Application | Transform `at shader_name` | Style, text tag, or config |
| Special code | Just vertex/fragment | Has `adjust_function` |
| Timing | `u_time` | `u_text_slow_time`, `a_text_min_time` |
| Coordinates | Image coords | Glyph-relative coords |

#### Decision Point: Do We Need Editor Support?

**Arguments FOR editor support:**
- Could create presets for custom text shaders with tunable params
- Parser could potentially extract params from `register_textshader()`
- Consistent with image shader workflow

**Arguments AGAINST editor support:**
- Built-in shaders cover most use cases (wave, jitter, typewriter, etc.)
- Text shaders are more code-heavy (adjust_function)
- Applied via text tags/styles, not transforms
- Fewer tunable parameters typically
- Could just write .rpy files directly

#### Decision: ADD TEXT SHADERS TAB WITH FULL TEXT STYLING

User decided to add a third tab: `Transitions | Shaders | Text Shaders`

**Key Insight:** Text Shaders tab manages BOTH:
1. **Text shader effects** (wave, jitter, rainbow GLSL effects)
2. **Text styling parameters** (font, size, color, speed, outlines)

**"No Shader" Preset:** A preset with `shader: null` that only manages text styling.
Use case: Different character "feels" without fancy effects.

**Single Self-Contained JSON:** `textshader_presets.json` has everything needed:
```json
{
    "presets": {
        "narrator": {
            "shader": null,
            "text": { "font": "DejaVuSans.ttf", "size": 28, "color": "#FFFFFF", "cps": 30 }
        },
        "villain_whisper": {
            "shader": "wave",
            "shader_params": { "u_amplitude": 2.0, "u_speed": 0.5 },
            "text": { "font": "creepy.ttf", "size": 24, "color": "#880000", "cps": 15 }
        }
    }
}
```

**Generator:** `textshader_generator.rpy` reads this file and creates complete text styles.

**Implementation Plan:**
1. Create `textshader_presets.json` with schema
2. Update `json_manager.py` to handle text shader presets
3. Update `config.json` with text shader preset path
4. Add "Text Shaders" tab to `preset_editor.py` with:
   - Shader selection (none, wave, jitter, etc.)
   - Shader params (when applicable)
   - Text styling params (font, size, color, cps, outlines, etc.)
5. Create `textshader_generator.rpy` to digest the JSON

---

## Summary: Text System Decisions

| Component | Needs Editor Changes? | Implementation |
|-----------|----------------------|----------------|
| **Text Boxes** | NO | Ren'Py side - use `at` with existing presets |
| **Text Shaders** | YES - DONE | New "Text Shaders" tab in preset editor |

---

## Implementation Complete

### Files Created/Modified
- `game/presets/textshader_presets.json` - Text shader preset data (both locations)
- `tools/preset_editor/modules/json_manager.py` - Added text shader methods
- `tools/preset_editor/config.json` - Added textshader_presets path
- `tools/preset_editor/preset_editor.py` - Added Text Shaders tab

### Features Added
- **Text Shaders tab** with Builder, Manager, and JSON modes
- **Shader selection** from built-in Ren'Py text shaders (wave, jitter, typewriter, etc.)
- **"No shader" option** for pure text styling
- **Full text styling**: font, size, color, kerning, line_spacing, slow_cps, bold, italic
- **Outlines management**: Add/remove/edit multiple outlines

---

## Next Actions

### Testing
- [ ] Test the preset editor Text Shaders tab
- [ ] Verify JSON saves correctly
- [ ] Test all text property inputs

### Ren'Py Side
- [ ] Create `textshader_generator.rpy` to consume the JSON
- [ ] Modify `game/screens/screens_base.rpy` to support `textbox_preset`/`namebox_preset`
- [ ] Test applying text presets to characters

### Completed
- [x] Document current preset editor state
- [x] Research text box implementation
- [x] Research text shader API
- [x] Create textshader_presets.json schema
- [x] Update json_manager.py for text shaders
- [x] Add Text Shaders tab to preset_editor.py

---

## Reference: Ren'Py Say Screen Structure

```
Screen (say)
└── window displayable (the text box)
    └── vbox
        ├── text displayable (who - character name)
        └── text displayable (what - dialogue)
```

The `window` and `text` elements are standard displayables that can have transforms/shaders applied.

---

## How to Resume This Session

1. Read this file for context
2. **Text Shaders tab implemented** - Ready for testing
3. **Next step**: Test the editor, then create `textshader_generator.rpy`
4. The preset editor now has three tabs: Transitions | Shaders | Text Shaders
