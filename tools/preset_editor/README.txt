Preset Editor v2.0
==================

A Dear PyGui desktop application for managing Ren'Py preset JSON files.

Manages:
- transition_presets.json (movement, position, alpha, scale, rotation)
- shader_presets.json (visual effects)


INSTALLATION
------------

1. Install Python 3.8+ if not already installed

2. Install dependencies:
   pip install -r requirements.txt

3. Run the tool:
   python preset_editor.py


FEATURES
--------

Two Main Tabs:
- TRANSITIONS - Manage transition presets (movement animations)
- SHADERS - Manage shader presets (visual effects)

Three Modes per Tab:
- Builder - Visual editor for preset properties
- Manager - List view with reordering and bulk actions
- JSON - Raw JSON view (read-only)

Manager Mode Features:
- Select All / Select None / Invert selection
- Multi-select: Ctrl+Click to toggle, Shift+Click for range
- Move to Top (^^) / Up (^) / Down (v) / Bottom (vv)
- Edit / Rename / Duplicate / Delete per item
- Bulk actions for selected items

Export Demo:
- Tools > Export Demo
- Three columns: Transitions | Shaders | Demo Items
- Select one from each column (or just one), click Add
- Build up to 10 demo combinations
- Generate creates a Ren'Py test script
- Run in Ren'Py launches the game (requires renpy_exe in settings)


KEYBOARD SHORTCUTS
------------------

Ctrl+Z       - Undo
Ctrl+Y       - Redo
Ctrl+Click   - Toggle selection
Shift+Click  - Range selection


SETTINGS
--------

File > Settings to configure:
- Path to transition_presets.json
- Path to shader_presets.json
- Path to shader .rpy folder (for available shaders)
- Game folder for demo export
- Ren'Py executable path (optional, for Run in Ren'Py)


SHADER .RPY ANNOTATIONS
-----------------------

The tool can parse shader .rpy files to discover available shaders.
Add these comments to your shader files:

At file level:
    ## @tool-category: Glow
    ## @tool-description: Adds glowing aura effects

Before each renpy.register_shader():
    # @shader: shader.glow
    # @param u_glow_color: color, default=#FFFFFF, description=Glow color
    # @param u_outer_strength: float, range=0.0-2.0, default=0.6
    # @param u_inner_strength: float, range=0.0-1.0, default=0.0
    # @animated
    renpy.register_shader("shader.glow", ...)

Supported param types: color, float, int


USAGE IN REN'PY
---------------

Transitions are called as functions:
    show character at preset_slide_left_enter()
    show character at preset_slide_left_enter(xalign=0.3)

Shaders are static transforms:
    show character at shader_glow_blue
    show character at shader_wave_gentle

Chain them together:
    show character at preset_slide_left_enter(), shader_glow_blue


FILE STRUCTURE
--------------

tools/preset_editor/
├── preset_editor.py      # Main application
├── config.json           # User settings (auto-generated)
├── requirements.txt      # Python dependencies
├── README.txt            # This file
├── modules/
│   ├── __init__.py
│   ├── shader_parser.py  # Parses .rpy files for shader defs
│   ├── json_manager.py   # JSON load/save with undo/redo
│   ├── ui_components.py  # Reusable UI widgets
│   └── demo_generator.py # Generates Ren'Py test scripts
└── game/                 # (Optional) Test game folder
    └── ...
