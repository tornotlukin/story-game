# Ren'Py Interactive Fiction - Development Guide

## Project Overview
This is a Ren'Py 8.5.2 interactive fiction project focused on **technical implementation**, not story content. The codebase emphasizes clean separation of concerns, modularity, and maintainability.

## Core Philosophy

### Separation of Concerns
1. **Systems** - Game mechanics and state management (no story)
2. **UI/Chrome** - Visual presentation and styling (no logic)
3. **Screens** - Interactive displays and menus (minimal logic)
4. **Transitions** - Visual effects library (pure presentation)
5. **Content** - Story scripts (separate from all technical systems)

### File Size Principle
- **Maximum ~300 lines per file** - keep files digestible
- **Single responsibility** - one system per file
- **Clear boundaries** - minimal cross-file dependencies
- **Easy scanning** - humans and LLMs should quickly understand any file

### Documentation Reference
- **`docs/renpy_file_org.md`** - **CRITICAL: Read this before creating/modifying .rpy files**
  - Standard Ren'Py project structure
  - What each file does (gui.rpy, options.rpy, screens.rpy, etc.)
  - Style system and inheritance rules
  - Positioning/layout syntax (avoid common mistakes)
  - Common gotchas and solutions
- **`docs/original_renpy_project/`** - **Fresh Ren'Py project from launcher (DO NOT MODIFY)**
  - Use as comparison baseline when debugging or modifying .rpy files
  - Contains unmodified: gui.rpy, screens.rpy, options.rpy, script.rpy, gui/ assets
  - Compare your changes against original to spot issues
- **`docs/game_config_targets.md`** - **Preset Editor File Targets**
  - Maps every configurable property to its target file
  - Line patterns for parsing/modifying properties
  - Data types, default values, editor labels
  - Used by preset_editor Game Config tab
- **`docs/renpy/`** - Full Ren'Py 8.x HTML documentation
- **`docs/CLAUDE.md`** - HTML doc search methodology

### IMPORTANT: Preset Editor Parity

When making **mechanical/functional changes** to:
- **Shaders** (`game/shader/*.rpy`)
- **Presets** (`game/presets/*.rpy`, `game/presets/*.json`)
- **Transitions** or visual tooling code

**You MUST also update `tools/preset_editor/game/`** with the same changes.

The preset editor has its own copy of shader and preset files for testing. These must stay in sync with the main game folder. Failure to maintain parity will cause the preset editor demo to break or behave differently than the actual game.

**Files that require parity:**
- `game/shader/*.rpy` ↔ `tools/preset_editor/game/shader/*.rpy`
- `game/presets/*.rpy` ↔ `tools/preset_editor/game/presets/*.rpy`
- `game/presets/*.json` ↔ `tools/preset_editor/game/presets/*.json`

## Directory Structure

```
story-game/                         # Project root
├── .gitignore
├── claude.md                       # Development guide (this file)
├── README.md                       # User-facing documentation
├── docs/                           # Reference documentation
│   ├── renpy/                      # Ren'Py 8.x HTML documentation
│   ├── renpy_file_org.md           # Ren'Py project structure guide
│   └── original_renpy_project/     # Fresh Ren'Py project (DO NOT MODIFY)
│       ├── gui.rpy                 # Original GUI variables
│       ├── screens.rpy             # Original screen definitions
│       ├── options.rpy             # Original config
│       ├── script.rpy              # Original entry point
│       └── gui/                    # Original GUI assets
│
└── game/                           # Ren'Py game folder (all game code)
    │
    ├── options.rpy                 # Game configuration (resolution, etc.)
    ├── gui.rpy                     # Ren'Py default GUI config
    ├── screens.rpy                 # Ren'Py default screens
    ├── script.rpy                  # Ren'Py default script (unused)
    │
    ├── systems/                    # Game mechanics & logic
    │   ├── state_manager.rpy       # Core state/variable management
    │   └── dice_system.rpy         # Dice rolling mechanics
    │
    ├── ui/                         # Visual styling & chrome
    │   ├── gui.rpy                 # Main GUI configuration
    │   ├── fonts.rpy               # Font definitions
    │   ├── colors.rpy              # Color scheme
    │   ├── styles.rpy              # Style definitions
    │   └── touch_config.rpy        # Touch/mobile settings
    │
    ├── screens/                    # Interactive UI screens
    │   └── screens_base.rpy        # Core screens (say, choice, menu)
    │
    ├── transitions/                # Scene & character transitions
    │   ├── transitions.json        # JSON config for all transitions
    │   ├── transition_loader.rpy   # JSON loader & defaults
    │   ├── character_animations.rpy # Character entrance/exit factory
    │   ├── basic_transitions.rpy   # Dissolve, fade, wipe, etc.
    │   └── special_fx.rpy          # Flashes, shakes, effects
    │
    ├── presets/                    # JSON preset configurations
    │   ├── shader_presets.json     # Elemental shader configurations
    │   └── presets.json            # Scene choreography presets
    │
    ├── shader/                     # GLSL shader effects
    │   ├── shader_glow.rpy         # Glow/pulse shaders
    │   ├── shader_blur.rpy         # Blur effect shaders
    │   ├── shader_distort.rpy      # Distortion/wave shaders
    │   ├── shader_color.rpy        # Color adjustment shaders
    │   ├── shader_retro.rpy        # Retro effect shaders
    │   ├── shader_fx.rpy           # Special FX shaders
    │   ├── shader_blend.rpy        # Blend mode shaders
    │   └── shader_transforms.rpy   # Transform presets for shaders
    │
    ├── content/                    # Story scripts (user creates)
    │   ├── script.rpy              # Main story entry point
    │   └── characters.rpy          # Character & image definitions
    │
    ├── audio/                      # Sound effects & music
    │
    ├── images/                     # Ren'Py auto-detected images
    │
    ├── gui/                        # GUI assets (Ren'Py generated)
    │   ├── bar/                    # Progress bar images
    │   ├── button/                 # Button backgrounds
    │   ├── overlay/                # Screen overlays
    │   ├── scrollbar/              # Scrollbar images
    │   ├── slider/                 # Slider images
    │   └── phone/                  # Mobile-specific variants
    │
    ├── libs/                       # External libraries\
    │
    ├── fonts/                      # custom font location
    │
    └── tl/                         # Translations
```

## File Organization Rules

### System Files (`systems/`)
**Purpose**: Pure logic, no UI, no story content
**Contains**:
- Python classes and functions
- State management
- Game mechanics calculations
- Data structures

**Example Structure**:
```python
## filename.rpy - Brief description of system

init python:
    class SystemName:
        """
        Clear docstring explaining purpose
        """
        def __init__(self):
            # Initialize state
            pass
        
        def method_name(self, params):
            """What this does and why"""
            # Implementation
            pass

# Global instance
default system_instance = SystemName()

# Helper functions if needed
define helper_func = system_instance.method
```

**Rules**:
- Use `init python:` blocks for classes
- Use `default` for runtime variables
- Use `define` for constants and shortcuts
- No story content, no UI code
- Document all public methods

### UI Files (`ui/`)
**Purpose**: Visual styling only, no logic
**Contains**:
- GUI configuration variables
- Style definitions
- Color schemes
- Font declarations

**Example Structure**:
```python
## filename.rpy - Brief description of UI elements

## Color Definitions
define gui.accent_color = '#cc6699'
define gui.hover_color = '#ff99cc'

## Font Definitions
define gui.text_font = "DejaVuSans.ttf"
define gui.text_size = 28

## Style Properties
style my_element:
    color gui.text_color
    size gui.text_size
    # ... other properties
```

**Rules**:
- Only `define` statements and `style` blocks
- No Python logic
- No story content
- Group related definitions together
- Comment sections clearly

### Screen Files (`screens/`)
**Purpose**: Interactive UI displays
**Contains**:
- Screen definitions
- User interaction handlers (touch, mouse, keyboard)
- Display logic (but complex logic goes in systems/)

**Example Structure**:
```python
## filename.rpy - Brief description of screen

screen screen_name(param1, param2):
    """
    What this screen displays and when to use it
    
    Input support: Touch, Mouse, Keyboard
    """
    
    modal True  # If screen blocks interaction
    
    frame:
        # Layout and structure
        vbox:
            spacing gui.touch_spacing  # Touch-friendly spacing
            
            text "Display Text"
            
            # Cross-platform button
            textbutton "Action":
                action Return(value)
                # Touch-friendly minimum size
                minimum (gui.button_minimum_width, gui.button_minimum_height)
    
    # Input bindings (keyboard, gestures)
    key "K_ESCAPE" action Return()
    key "android_back" action Return()  # Android back button
    key "swipe_down" action Return()    # Touch gesture
```

**Rules**:
- One primary screen per file (related helper screens OK)
- Keep logic minimal - call system methods instead
- **Support all input methods** - touch, mouse, keyboard
- Document parameters, usage, and input methods
- Include example usage in comments
- Ensure touch-friendly sizing (44+ pixel targets)

### Transition Files (`transitions/`)
**Purpose**: Visual transition definitions
**Contains**:
- Transition definitions
- Custom transition combinations

**Example Structure**:
```python
## filename.rpy - Brief description of transitions

# Basic transition
define my_transition = Dissolve(0.5)

# Complex transition
define special_transition = ComposeTransition(
    Dissolve(1.0),
    before=Fade(0.3, 0.0, 0.3),
    after=Dissolve(0.5)
)

## Usage Examples:
# scene new_location with my_transition
# show character with special_transition
```

**Rules**:
- Use `define` for all transitions
- Group related transitions together
- Include usage examples in comments
- Keep files under 200 lines

### Preset Files (`presets/`)
**Purpose**: JSON configuration for visual effects and scene choreography
**Contains**:
- Shader preset definitions
- Scene preset definitions with inheritance
- Character movement choreography
- Dialog box and background configurations

**Two-Tier System**:
```
shader_presets.json (elemental)
└─ Simple, single-purpose shader configurations
└─ No inheritance - create new presets for variations
└─ Referenced by presets.json

presets.json (composite)
└─ Full scene choreography
└─ Supports inheritance via "extends"
└─ References shader presets
└─ Defines character lead_in/lead_out
└─ Configures dialog box, background, transitions
```

**Rules**:
- Shader presets are elemental - no inheritance
- Scene presets use CSS-like inheritance
- All colors in 6-digit hex format (`"#FF5500"`)
- See `docs/PRESET_SYSTEM.md` for complete documentation

### Shader Files (`shader/`)
**Purpose**: GLSL shader definitions for visual effects
**Contains**:
- `renpy.register_shader()` calls
- Transform definitions for shader application
- Ported from Phaser.js color filters

**Example Structure**:
```python
## shader_effect.rpy - Effect description

init python:
    renpy.register_shader("shader.effect_name", variables="""
        uniform sampler2D tex0;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        // Effect implementation
        gl_FragColor = color;
    """)

# Transform to apply shader
transform effect_name:
    shader "shader.effect_name"
    u_amount 1.0
    mesh_pad 50  # For effects extending beyond bounds
```

**Rules**:
- One category per file (glow, blur, distort, etc.)
- Preserve transparency in all shaders
- Use `mesh_pad` for effects that extend beyond image bounds
- Mark animated shaders in documentation
- Keep files under 300 lines

### Content Files (`content/`)
**Purpose**: Story script - user creates this
**Contains**:
- Labels and narrative
- Character dialogue
- Story choices
- Calls to systems for mechanics

**Example Structure**:
```python
## filename.rpy - Chapter/scene description

label chapter_start:
    scene location with dissolve
    
    "Narration text."
    
    character "Dialogue text."
    
    # Use systems for mechanics
    $ result = dice.roll("1d20")
    
    menu:
        "Choice 1":
            $ game_state.set_flag("choice1_taken")
            jump choice1_path
        
        "Choice 2":
            jump choice2_path
```

**Rules**:
- This is where story goes
- Call system methods, don't implement logic here
- Keep labels focused and not too long
- Use meaningful label names

## Naming Conventions

### Files
- `snake_case.rpy` - lowercase with underscores
- Descriptive names: `dice_system.rpy` not `dice.rpy`
- Grouped by purpose: `character_stats.rpy`, `character_sheet.rpy`

### Variables
- `snake_case` - Python convention
- Prefix for scope clarity:
  - No prefix: local variables
  - `gui.` prefix: GUI configuration
  - `game_state.` prefix: persistent game state
  
### Classes
- `PascalCase` - Python convention
- Descriptive: `DiceRoller`, `GameState`, `InventoryManager`

### Labels
- `snake_case` - Ren'Py convention
- Descriptive: `merchant_encounter`, `chapter_01_start`
- No generic names: use `town_entrance` not `scene1`

### Screens
- `snake_case` - Ren'Py convention
- Noun phrases: `character_sheet`, `dice_display`
- Purpose-driven: `skill_check_screen` not `screen1`

### Transitions
- `snake_case` - consistent with rest
- Descriptive: `slow_dissolve`, `combat_flash`
- Context hints: `dream_transition`, `flashback_fade`

## Code Documentation Standards

### File Headers
Every .rpy file should start with:
```python
## filename.rpy - One line description
##
## Detailed explanation of what this file contains and when to use it.
## Include dependencies on other files if relevant.
##
## Related files: other_file.rpy, another_file.rpy
```

### Function/Method Documentation
```python
def function_name(param1, param2):
    """
    Brief description of what function does.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
    
    Returns:
        Description of return value
    
    Example:
        result = function_name(10, "test")
    """
    pass
```

### Inline Comments
- Explain **why**, not what (code shows what)
- Complex logic needs comments
- Mark TODOs clearly: `# TODO: Implement X`
- Mark temporary code: `# TEMP: Replace with Y`

## When to Create New Files

### Create a new file when:
1. A system/screen has **distinct responsibility** from existing files
2. A file exceeds **~300 lines**
3. Code would be **reused across multiple scripts**
4. Separation improves **clarity and maintainability**

### Don't create a new file when:
1. Adding 10-20 lines to an existing file makes more sense
2. The code is **tightly coupled** to existing system
3. File would be **< 50 lines** with no growth expected

## Development Workflow

### For New Features:
1. **Identify category** - Which directory does this belong in?
2. **Check existing files** - Can this extend an existing system?
3. **Create/modify file** - Follow structure for that category
4. **Document** - Add header, docstrings, comments
5. **Test in isolation** - Ensure system works standalone
6. **Integrate** - Connect to other systems minimally

### For Bug Fixes:
1. **Locate file** - Directory structure should make this easy
2. **Understand context** - Read file header and related files
3. **Fix issue** - Keep changes minimal and focused
4. **Update comments** - If behavior changes, update docs

### For Refactoring:
1. **Identify scope** - What needs to change?
2. **Plan new structure** - Which files affected?
3. **Update incrementally** - One system at a time
4. **Test each change** - Don't break working code
5. **Update documentation** - Keep CLAUDE.MD and comments current

## Version Control Best Practices

### Commit Messages:
```
[Category] Brief description

Detailed explanation if needed.

Files changed: file1.rpy, file2.rpy
```

Examples:
- `[Systems] Add dice rolling with advantage/disadvantage`
- `[UI] Update color scheme for better contrast`
- `[Screens] Create character sheet display`

### What to Commit:
- `.rpy` source files
- `CLAUDE.MD` and `README.md`
- Custom assets in `game/` directory

### What NOT to Commit:
- `.rpyc` compiled files
- `saves/` directory
- `tmp/` directory
- IDE-specific files

## Testing Guidelines

### Manual Testing:
- **Test in isolation** - Launch Ren'Py, test just this system
- **Test integration** - Ensure systems work together
- **Test edge cases** - What if variable is None? Empty? Negative?

### Test Labels:
Create test labels for systems:
```python
label test_dice_system:
    "Testing dice system..."
    
    $ result, rolls = dice.roll("2d6")
    "Rolled 2d6: [result] (individual: [rolls])"
    
    return
```

## Common Patterns

### Accessing Systems:
```python
# In content files, access systems via global instances
$ result = dice.roll("1d20")
$ game_state.set_flag("flag_name", True)
$ inventory.add_item("sword")
```

### Conditional Checks:
```python
# Check flags
if game_state.has_flag("met_merchant"):
    jump merchant_dialogue_2
else:
    jump merchant_dialogue_1

# Check stats
$ charisma = game_state.stats['charisma']
if charisma >= 15:
    "Your charm wins them over."
```

### Menu Integration:
```python
menu:
    "Persuade (Charisma 15)":
        $ success, roll, total = dice.skill_check(
            game_state.stats['charisma'], 
            difficulty=15
        )
        if success:
            "Success!"
        else:
            "Failure..."
```

### Platform-Specific Adjustments:
```python
# Adjust UI based on platform
init python:
    if renpy.mobile:
        # Mobile-specific settings
        gui.text_size = 32
        gui.button_height = 60
        config.mouse_hide_time = 0  # Don't hide cursor on mobile
    else:
        # Desktop settings
        gui.text_size = 28
        gui.button_height = 40

# In screens, adapt to platform
screen adaptive_ui():
    if renpy.mobile:
        # Larger, simplified mobile layout
        vbox:
            spacing 20
            textbutton "Big Touch Button" minimum (200, 80)
    else:
        # Compact desktop layout
        hbox:
            spacing 10
            textbutton "Button 1" minimum (120, 40)
            textbutton "Button 2" minimum (120, 40)
```

## Mobile & Touch Support

### Target Platforms:
- **Desktop**: Windows, Mac, Linux (mouse + keyboard)
- **Mobile**: Android, iOS (touch)
- **Hybrid**: Tablets, touch-enabled laptops (touch + keyboard/mouse)

### Input Method Support:

**All interactive elements MUST support:**
1. **Touch** - Single tap, long press, swipe gestures
2. **Mouse** - Click, hover, drag
3. **Keyboard** - Shortcuts, navigation

### Touch-Friendly UI Guidelines:

**Minimum Touch Target Sizes:**
```python
# In ui/gui.rpy or ui/touch_config.rpy
define gui.minimum_touch_size = 44  # pixels (Apple HIG recommendation)
define gui.comfortable_touch_size = 60  # pixels (better for games)

# Button sizing
define gui.button_minimum_height = 60
define gui.button_minimum_width = 120

# Spacing between interactive elements
define gui.touch_spacing = 12  # minimum space between buttons
```

**Screen Design Principles:**
- Buttons: **60+ pixels** high/wide (44px absolute minimum)
- Spacing: **12+ pixels** between interactive elements
- Hit boxes: Larger than visual button (generous touch areas)
- No hover-only features (use tap or long-press alternatives)

### Input Handling Patterns:

**In Screens - Multiple Input Methods:**
```python
screen example_screen():
    """
    Example of cross-platform input handling
    """
    
    # Button with keyboard, mouse, and touch support
    textbutton "Continue":
        # Touch/Mouse - primary action
        action Return()
        
        # Keyboard shortcut
        keysym "K_RETURN"
        
        # Ensure touch-friendly size
        minimum (gui.button_minimum_width, gui.button_minimum_height)
    
    # Add keyboard navigation
    key "K_ESCAPE" action Return("cancel")
    key "K_SPACE" action Return("continue")
```

**Touch Gestures Support:**
```python
# Ren'Py supports these touch gestures:
# - Single tap
# - Long press
# - Swipe (left, right, up, down)
# - Pinch (zoom in/out)
# - Rotate

# Example gesture handling:
screen gesture_example():
    
    # Swipe to dismiss
    on "swipe_left" action Return("dismiss")
    on "swipe_right" action Return("open_menu")
    
    # Long press for context menu
    on "long_press" action Show("context_menu")
```

**Drag and Drop (Cross-Platform):**
```python
screen inventory_touch():
    """
    Inventory with touch and mouse drag support
    """
    
    drag:
        draggable True
        droppable True
        
        # Works with both touch and mouse
        drag_name "item_sword"
        
        # Visual feedback
        drag_raise True
```

### Mobile-Specific Considerations:

**Screen Resolutions:**
```python
# Support multiple aspect ratios
# Common mobile: 16:9, 18:9, 19.5:9, 20:9
# Tablets: 4:3, 16:10

# In options.rpy:
define config.screen_width = 1920   # Base width
define config.screen_height = 1080  # Base height

# UI scales automatically, but test on:
# - Phone portrait (9:16)
# - Phone landscape (16:9)
# - Tablet (4:3, 16:10)
```

**Performance Optimization:**
```python
# Mobile devices have limited resources

# Limit concurrent transitions
define config.gl_test_image = "white"  # Test GL support

# Optimize image sizes
# - Use appropriate resolutions
# - Compress images for mobile
# - Use .webp format when possible

# Limit particle effects
# - Reduce for mobile
# - Provide quality settings
```

**Text Readability:**
```python
# Minimum font sizes for mobile
define gui.mobile_text_size = 32      # Readable on phones
define gui.mobile_name_text_size = 40
define gui.mobile_button_text_size = 36

# Auto-adjust based on platform
init python:
    if renpy.mobile:
        gui.text_size = gui.mobile_text_size
        gui.name_text_size = gui.mobile_name_text_size
```

**Platform Detection:**
```python
init python:
    # Check platform
    is_mobile = renpy.mobile
    is_android = renpy.android
    is_ios = renpy.ios
    is_desktop = not renpy.mobile
    
    # Adjust UI based on platform
    if is_mobile:
        # Larger touch targets
        gui.button_minimum_height = 60
        # Simplified layouts
        # Fewer on-screen elements
    else:
        # Desktop optimizations
        gui.button_minimum_height = 40
```

### Best Practices:

**1. Test All Input Methods:**
```python
# Every interactive element should work with:
- Touch tap (mobile)
- Mouse click (desktop)
- Keyboard shortcut (desktop)
- Gamepad button (if supported)
```

**2. Provide Visual Feedback:**
```python
style button:
    # Hover for mouse (desktop)
    hover_color gui.hover_color
    
    # Selected state for keyboard navigation
    selected_color gui.selected_color
    
    # Insensitive for disabled state
    insensitive_color gui.insensitive_color

# Active feedback for touch
style button:
    activate_sound "audio/click.ogg"
```

**3. No Hover-Dependent Features:**
```python
# BAD - requires hover (doesn't work on touch)
screen bad_example():
    imagebutton:
        idle "button_idle.png"
        hover "button_hover.png"  # User can't see without hover
        action Return()

# GOOD - clear visual state always
screen good_example():
    imagebutton:
        idle "button_clear_idle.png"  # Shows what it does
        hover "button_highlighted.png"
        selected "button_selected.png"
        action Return()
```

**4. Scrolling on Mobile:**
```python
screen scrollable_content():
    """
    Works with touch scroll and mouse wheel
    """
    
    viewport:
        scrollbars "vertical"  # Shows scrollbar
        mousewheel True       # Mouse wheel support
        draggable True        # Touch drag to scroll
        
        vbox:
            # Content here
            pass
```

**5. Context Menus:**
```python
# Desktop: Right-click
# Mobile: Long-press

screen item_display(item):
    
    button:
        # Regular action (left-click/tap)
        action Show("item_details", item=item)
        
        # Alternative action (right-click/long-press)
        alternate Return("use_item")
```

### Ren'Py Mobile Features:

**Gesture Support:**
```python
# Documentation: https://www.renpy.org/doc/html/gesture.html

# Enable gestures
define config.gestures = True

screen gesture_nav():
    # Swipe navigation
    key "swipe_left" action Return("next")
    key "swipe_right" action Return("previous")
    key "swipe_up" action Return("menu")
    key "swipe_down" action Return("back")
```

**Back Button (Android):**
```python
# Handle Android back button
screen game_menu_custom():
    
    # Standard escape key
    key "K_ESCAPE" action Return()
    
    # Android back button
    key "android_back" action Return()
```

**Vibration (Mobile):**
```python
init python:
    def vibrate(duration=0.1):
        """Haptic feedback for touch actions"""
        if renpy.mobile:
            renpy.vibrate(duration)

# Use in screens
screen touch_button():
    textbutton "Action":
        action [
            Function(vibrate, 0.05),
            Return("action")
        ]
```

### Testing Checklist:

**Desktop Testing:**
- [ ] All buttons clickable with mouse
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Hover states show clearly
- [ ] Mouse wheel scrolling works

**Mobile Testing (or emulation):**
- [ ] All buttons tappable (44+ pixel targets)
- [ ] No hover-dependent features
- [ ] Touch scrolling works smoothly
- [ ] Gestures work (if implemented)
- [ ] Text readable on phone screens
- [ ] Android back button handled
- [ ] Performance acceptable (30+ fps)

**Both Platforms:**
- [ ] Save/Load works
- [ ] Settings accessible
- [ ] Quick menu usable
- [ ] History/rollback functional

## Integration with Ren'Py 8.5.2

### Python Version:
- Ren'Py 8.5.2 uses **Python 3.12**
- Use Python 3.12 features freely
- Standard library available

### Key Ren'Py Features Used:
- `init python:` - For class definitions
- `default` - For runtime variables (saved in saves)
- `define` - For constants (not saved)
- `screen` - For UI elements
- Transitions - For visual effects
- Gestures - For mobile touch input
- Platform detection - `renpy.mobile`, `renpy.android`, `renpy.ios`

### Documentation References (Local):

The complete Ren'Py 8.5.2 documentation is available locally at `docs/renpy/`.

**LLM Quick-Access Files** (read these first):
- `docs/renpy/LLM_QUICKREF.md` - Fast topic-to-file lookup, common patterns
- `docs/renpy/LLM_INDEX.json` - Machine-readable index with keywords and file mappings
- `docs/CLAUDE.md` - HTML navigation strategies for efficient doc reading

**Index Files** (for targeted lookups):
| File | Use For |
|------|---------|
| `index.html` | Main table of contents |
| `py-function-class-index.html` | Function/class name → file lookup |
| `std-var-index.html` | Variable name → file lookup |
| `std-style-property-index.html` | Style properties reference |
| `std-transform-property-index.html` | Transform properties reference |
| `genindex.html` | Alphabetical general index |

**Topic Quick Map**:
| Topic | File |
|-------|------|
| Character, dialogue | `dialogue.html` |
| show, hide, scene | `displaying_images.html` |
| Screens, vbox, hbox | `screens.html` |
| Screen actions | `screen_actions.html` |
| Styles | `style.html` + `style_properties.html` |
| Transforms, ATL | `transforms.html` |
| Transitions | `transitions.html` |
| Touch/gestures | `gesture.html` |
| Mobile/Android/iOS | `android.html`, `ios.html` |
| config.* variables | `config.html` |
| renpy.* functions | `statement_equivalents.html`, `other.html` |

**Navigation Strategy**:
1. Check `LLM_QUICKREF.md` for common patterns
2. Use index files for specific lookups
3. Read only the relevant section of HTML files (they can be large)
4. See `docs/CLAUDE.md` for detailed HTML navigation patterns

### Live2D Documentation:

**For Ren'Py Live2D integration** (primary reference):
- `docs/renpy/live2d.html` - Full local documentation for Live2D in Ren'Py

**For Cubism Editor topics** (model creation):
- `docs/live2d/LLM_QUICKREF.md` - Quick reference for Live2D workflows
- `docs/live2d/LLM_INDEX.json` - Index with external doc links

**Live2D Quick Reference**:
```python
# Define Live2D character
image hiyori = Live2D("Resources/Hiyori", base=1.0)

# Show with motion and expression
show hiyori m1 e1
```

**Note**: Most Cubism Editor docs link externally to docs.live2d.com. The Ren'Py integration docs at `docs/renpy/live2d.html` are fully available locally.

### Preset System Documentation:

**Full Documentation**:
- `docs/PRESET_SYSTEM.md` - Complete preset system reference

**Quick Reference**:
| File | Purpose |
|------|---------|
| `game/presets/shader_presets.json` | Elemental shader configurations |
| `game/presets/presets.json` | Scene choreography presets |
| `game/systems/preset_manager.rpy` | Preset loading and application |

**Usage in Scripts**:
```python
# Set scene mood
$ mood.set("dream_sequence")

# Run character choreography chain
$ mood.chain("dream_sequence", "dramatic_entrance")

# Character entry with preset
$ mood.character_enter("novy", "dream_sequence")
```

### Shader Documentation:

**Custom GLSL Shaders**:
- `docs/SHADER_PORTING_GUIDE.md` - Phaser→Ren'Py shader porting guide with examples
- `docs/PRESET_SYSTEM.md` - Shader preset parameter reference
- `docs/renpy/model.html` - Ren'Py shader registration and built-in uniforms
- `docs/renpy/textshaders.html` - Text-specific shader effects

**Ren'Py Built-in Uniforms**:
| Uniform | Type | Description |
|---------|------|-------------|
| `tex0`, `tex1`, `tex2` | sampler2D | Textures |
| `u_model_size` | vec2 | Width/height of model |
| `u_time` | float | Frame time (resets daily) |
| `u_random` | vec4 | 4 random numbers per frame |
| `u_viewport` | vec4 | Current viewport |
| `u_virtual_size` | vec2 | Game virtual size |
| `u_transform` | mat4 | Transform matrix |

**Quick Shader Example**:
```python
init python:
    renpy.register_shader("my_effect", variables="""
        uniform sampler2D tex0;
        uniform float u_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec4 color = texture2D(tex0, v_tex_coord);
        // Apply effect here
        gl_FragColor = color;
    """)

transform apply_effect:
    shader "my_effect"
    u_amount 1.0
```

## LLM Development Notes

When working with this codebase:

1. **Always check CLAUDE.MD first** - Understand structure before coding
2. **For Ren'Py documentation lookups**:
   - **FIRST**: Check `docs/renpy/LLM_QUICKREF.md` - Has topic-to-file mappings, common patterns
   - **SECOND**: Check `docs/renpy/LLM_INDEX.json` - Keyword search, function lookups
   - **LAST**: Read specific HTML file sections only when needed
   - This order saves tokens and speeds up lookups
3. **Identify the right directory** - Where does this code belong?
4. **Check for existing files** - Don't duplicate functionality
5. **Follow patterns** - Consistency matters more than cleverness
6. **Keep files small** - Split when approaching 300 lines
7. **Document as you go** - Comments and docstrings required
8. **Think modular** - Systems should work independently
9. **Minimize coupling** - Clear interfaces between systems
10. **Ask before major changes** - Discuss structure changes with user
11. **Test on multiple inputs** - Touch, mouse, and keyboard support required

## User Customization Areas

The user will handle:
- **Content creation** - All story scripts in `content/`
- **Character definitions** - Dialogue styles, names
- **Asset integration** - Images, audio, fonts
- **Story-specific systems** - Unique mechanics for their story

The technical framework provides:
- **Game systems** - Reusable mechanics
- **UI/Chrome** - Polished, consistent interface
- **Transitions** - Professional scene changes
- **Architecture** - Clean, maintainable structure
- **Cross-platform support** - Touch, mouse, keyboard ready

## Future Expansion

When adding new systems:
1. Create appropriately named file in `systems/`
2. Define clear class interface
3. Create corresponding screen in `screens/` if needed
4. **Ensure cross-platform input support**
5. Update this CLAUDE.MD with new patterns
6. Add examples in comments

## Questions for Development

Before implementing:
- Which category does this belong to?
- Does a file for this already exist?
- What dependencies does this have?
- How will this be used in content scripts?
- Is the interface clear and simple?
- **Does this support touch, mouse, AND keyboard?**

## Summary

This project prioritizes:
- **Clarity** over cleverness
- **Modularity** over monolithic
- **Documentation** over implicit knowledge
- **Consistency** over individual style
- **Maintainability** over quick hacks
- **Cross-platform support** - Touch, mouse, and keyboard on all screens

Follow these guidelines and the codebase will remain clean, navigable, easy to extend, and functional across desktop and mobile platforms.
