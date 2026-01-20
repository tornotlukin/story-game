# Preset Editor - Development Guide

## Overview

The Preset Editor is a DearPyGui-based tool for creating and testing Ren'Py presets:
- **Transitions** - Movement/animation presets for characters and UI elements
- **Shaders** - Visual effect presets (glow, blur, distortion, etc.)
- **Text Shaders** - Text styling and animation presets

## CRITICAL: Real Game Parity

**The demo system MUST generate code identical to how it would work in the actual Ren'Py game.**

### Principles

1. **No Fake Representations** - Never create workaround images or screens to simulate effects. If testing a dialog box shader, apply it to the actual say screen window.

2. **Use Real Ren'Py Patterns** - The generated demo code should be copy-pasteable into a real game script and work identically.

3. **Test What You Ship** - The preset editor exists to preview exactly what the player will see. Any deviation makes the tool unreliable.

### How Effects Are Applied in Real Games

| Element | How It Works |
|---------|--------------|
| **Character image** | `show char at transition(), shader_transform` |
| **Dialog box** | Say screen's `window` with `at dialog_shader` variable |
| **Dialog background** | Say screen checks `dialog_background` variable |
| **Dialog text** | `{shader=name:params}text{/shader}` tags in say statement |
| **Transitions** | Standard `with transition` or `at transition()` |

### Demo Generation Rules

- **Characters**: Use `show character at preset_name(), shader_name`
- **Dialog shaders**: Set `dialog_shader` variable (defaults to `null_transform`)
- **Dialog backgrounds**: Set `dialog_background` variable (defaults to `None`)
- **Text shaders**: Inline `{shader=...}` tags in the dialogue string
- **Never**: Create fake overlay images to represent UI elements

### Required screens.rpy Setup

For dialog shader support, the game's screens.rpy needs:

```renpy
# Null transform - does nothing, used as default
transform null_transform:
    pass

# Dialog shader - set to apply shaders to dialog window
default dialog_shader = null_transform

# Dialog background - set for custom artwork
default dialog_background = None

screen say(who, what):
    style_prefix "say"

    window:
        id "window"
        at dialog_shader

        if dialog_background:
            background dialog_background

        vbox:
            if who is not None:
                text who id "who"
            text what id "what"
```

### Usage in Scripts

```renpy
# Apply shader to dialog box
$ dialog_shader = shader_glow_blue
"This dialog has a glow effect"
$ dialog_shader = null_transform

# Custom dialog artwork with shader
$ dialog_background = "images/fancy_dialog.png"
$ dialog_shader = shader_wave_gentle
"Fancy dialog with wave effect"
$ dialog_shader = null_transform
$ dialog_background = None
```

## IMPORTANT: Game Folder Parity

The preset editor has its own `game/` folder for testing demos. This folder contains copies of shader and preset files from the main game.

### When making mechanical/functional changes to the main game:
- **Shaders** (`game/shader/*.rpy`)
- **Presets** (`game/presets/*.rpy`, `game/presets/*.json`)
- **Transitions** or visual tooling code

### You MUST also update this folder:
- `tools/preset_editor/game/shader/*.rpy`
- `tools/preset_editor/game/presets/*.rpy`
- `tools/preset_editor/game/presets/*.json`

### Files that require parity:

| Main Game | Preset Editor |
|-----------|---------------|
| `game/shader/*.rpy` | `tools/preset_editor/game/shader/*.rpy` |
| `game/presets/*.rpy` | `tools/preset_editor/game/presets/*.rpy` |
| `game/presets/*.json` | `tools/preset_editor/game/presets/*.json` |

**Failure to maintain parity** will cause the preset editor demo to break or behave differently than the actual game.

## Directory Structure

```
tools/preset_editor/
├── preset_editor.py          # Main application entry point
├── config.json               # User configuration (paths, settings)
├── CLAUDE.md                 # This file
│
├── modules/                  # Core modules
│   ├── json_manager.py       # JSON preset loading/saving
│   ├── shader_parser.py      # Parses shader .rpy files for metadata
│   ├── demo_generator.py     # Generates Ren'Py demo scripts
│   └── ui_components.py      # Reusable UI components
│
├── tabs/                     # UI tab modules
│   ├── transition_tab.py     # Transitions tab
│   ├── shader_tab.py         # Shaders tab
│   ├── textshader_tab.py     # Text Shaders tab
│   └── demo_tab.py           # Demo tab for testing presets
│
├── modals/                   # Modal dialogs
│   └── ...
│
└── game/                     # Ren'Py test game (MUST STAY IN SYNC)
    ├── script.rpy            # Test game entry point
    ├── screens.rpy           # Minimal screens for testing
    ├── preset_demo.rpy       # Auto-generated demo script
    │
    ├── shader/               # COPY of game/shader/ - KEEP IN SYNC
    │   └── *.rpy
    │
    ├── presets/              # COPY of game/presets/ - KEEP IN SYNC
    │   ├── *.rpy
    │   └── *.json
    │
    └── images/               # Test images for demos
```

## Key Files

### `demo_generator.py`
Generates Ren'Py scripts to test preset combinations. Supports:
- Transition + Shader + Text Shader combinations
- "Apply to dialog" mode for testing dialog box effects
- Text shader tags using `{shader=name:params}` syntax

### `config.json`
Stores user paths:
- `transition_presets` - Path to transition_presets.json
- `shader_presets` - Path to shader_presets.json
- `textshader_presets` - Path to textshader_presets.json
- `game_folder` - Path to main game folder
- `renpy_exe` - Path to Ren'Py executable

## Running the Editor

```bash
cd tools/preset_editor
python preset_editor.py
```

## Demo Tab Workflow

1. Select presets from Transitions, Shaders, and/or Text Shaders columns
2. Click "Add Selected" to create a demo item
3. Click "Create Demo" to generate script and launch Ren'Py

**Important**: "Apply to dialog" checkbox controls behavior:
- **UNCHECKED**: Tests transitions + shaders on character image only. Text shaders column is disabled.
- **CHECKED**: Tests transitions + shaders on dialog + text shaders on dialogue text.

## Text Shaders vs Image Shaders

These are **completely separate systems** in Ren'Py:
- **Image/Transform Shaders**: Applied via `shader` transform property to displayables
- **Text Shaders**: Applied via `textshader` style property or `{shader=name}` tags

See `TEXT_SHADER_NOTES.md` for detailed technical documentation.
