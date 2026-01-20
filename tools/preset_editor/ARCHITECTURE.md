# Preset Editor Architecture Documentation

**Purpose:** This document provides a complete breakdown of the Preset Editor application structure, components, and dependencies. Use this as a reference when making changes to ensure separation of concerns is maintained.

---

## File Structure Overview

```
tools/preset_editor/
├── preset_editor.py          # Main application (UI + callbacks)
├── config.json               # Configuration paths
├── ARCHITECTURE.md           # This documentation
├── WORKSHOP_NOTES.md         # Session notes and decisions
│
├── modules/                  # Reusable components (separation of concerns)
│   ├── json_manager.py       # JSON data management + undo/redo
│   ├── shader_parser.py      # .rpy file parsing for shader definitions
│   ├── ui_components.py      # Reusable DearPyGui widgets
│   └── demo_generator.py     # Ren'Py demo script generation
│
└── game/                     # Test game folder for demos
    ├── presets/
    │   ├── transition_presets.json
    │   ├── shader_presets.json
    │   └── textshader_presets.json
    └── ...
```

---

## Module Responsibilities

### 1. `preset_editor.py` (Main Application)
**Lines:** ~3020
**Responsibility:** UI construction, user interaction, callbacks

**DOES:**
- Creates DearPyGui windows, tabs, panels
- Handles user input and callbacks
- Calls module methods for data operations
- Manages UI refresh cycles

**DOES NOT:**
- Directly manipulate JSON files (uses JsonManager)
- Parse shader files (uses ShaderParser)
- Generate demo scripts (uses DemoGenerator)

---

### 2. `modules/json_manager.py` (Data Layer)
**Lines:** ~726
**Responsibility:** JSON data management with undo/redo

**DOES:**
- Load/save JSON files
- CRUD operations on presets
- Undo/redo stack management
- Change notification callbacks
- Auto-save on changes

**DOES NOT:**
- Know about UI
- Handle user input

---

### 3. `modules/shader_parser.py` (Parser Layer)
**Lines:** ~535
**Responsibility:** Parse .rpy files for shader definitions

**DOES:**
- Read .rpy files from shader directories
- Extract shader names, params, categories from annotations
- Provide shader definitions with param metadata

**DOES NOT:**
- Know about UI
- Modify any files

---

### 4. `modules/ui_components.py` (UI Components)
**Lines:** ~498
**Responsibility:** Reusable DearPyGui widgets

**DOES:**
- Color conversion utilities
- Selection management (multi-select)
- Dialog helpers (rename, confirm, color picker)
- Status bar widget
- Theme creation

**DOES NOT:**
- Handle data persistence
- Know about preset structure

---

### 5. `modules/demo_generator.py` (Demo Generation)
**Lines:** ~264
**Responsibility:** Generate Ren'Py test scripts

**DOES:**
- Build demo item lists
- Generate .rpy script content
- Save scripts to files

**DOES NOT:**
- Know about UI
- Manage preset data

---

## Class Reference

### AppState (preset_editor.py:57-206)
Global application state container.

```python
class AppState:
    # Paths from config
    transition_presets_path: str
    shader_presets_path: str
    textshader_presets_path: str
    shader_folder: str
    text_shader_folder: str
    game_folder: str
    renpy_exe: str

    # Demo settings
    demo_width: int
    demo_height: int

    # Managers (dependency injection)
    json_mgr: JsonManager
    shader_parser: ShaderParser
    text_shader_parser: TextShaderParser
    demo_gen: DemoGenerator

    # UI state
    transition_mode: EditorMode
    shader_mode: EditorMode
    textshader_mode: EditorMode

    # Selection managers
    trans_selection: SelectionManager
    shader_selection: SelectionManager
    textshader_selection: SelectionManager

    # Status bar reference
    status_bar: StatusBar

    # Methods
    def load_config()      # Load config.json
    def save_config()      # Save config.json
    def load_data()        # Load all JSON + parse shaders
```

### JsonManager (json_manager.py:24-725)
Manages preset JSON files with undo/redo.

```python
class JsonManager:
    # Data storage
    transition_data: Dict
    shader_data: Dict
    textshader_data: Dict

    # Undo/Redo
    undo_stack: List[UndoState]
    redo_stack: List[UndoState]

    # Core methods
    def set_paths(transition_path, shader_path, textshader_path)
    def load() -> bool
    def save(which: str = "all") -> bool  # "transition", "shader", "textshader", "all"

    # Undo/Redo
    def push_undo(description: str)
    def undo() -> bool
    def redo() -> bool

    # Transition presets
    def get_transition_names() -> List[str]
    def get_transition(name) -> Optional[Dict]
    def set_transition(name, data, push_undo=True)
    def add_transition(name, data)
    def delete_transition(name)
    def delete_transitions(names: List[str])
    def rename_transition(old_name, new_name) -> bool
    def duplicate_transition(name, new_name) -> bool
    def move_transition(name, direction) -> bool
    def get_unique_transition_name(base) -> str

    # Shader presets (same pattern as transitions)
    def get_shader_names() -> List[str]
    def get_shader(name) -> Optional[Dict]
    def set_shader(name, data, push_undo=True)
    def add_shader(name, data)
    def delete_shader(name)
    def delete_shaders(names: List[str])
    def rename_shader(old_name, new_name) -> bool
    def duplicate_shader(name, new_name) -> bool
    def move_shader(name, direction) -> bool
    def get_unique_shader_name(base) -> str

    # Text shader presets (same pattern)
    def get_textshader_names() -> List[str]
    def get_textshader(name) -> Optional[Dict]
    def set_textshader(name, data, push_undo=True)
    def add_textshader(name, data)
    def delete_textshader(name)
    def delete_textshaders(names: List[str])
    def rename_textshader(old_name, new_name) -> bool
    def duplicate_textshader(name, new_name) -> bool
    def move_textshader(name, direction) -> bool
    def get_unique_textshader_name(base) -> str

    # Change notifications
    def on_change(callback: Callable)
```

### ShaderParser (shader_parser.py:59-296)
Parses image shader .rpy files.

```python
@dataclass
class ShaderParam:
    name: str
    param_type: str  # "color", "float", "int", "vec2", "vec3", "vec4"
    default: Any
    min_value: Optional[float]
    max_value: Optional[float]
    description: str

@dataclass
class ShaderDefinition:
    name: str           # e.g., "shader.glow"
    category: str       # from @tool-category
    description: str    # from @tool-description
    file_description: str  # from lines 3-5 of file
    params: List[ShaderParam]
    source_file: str
    line_number: int
    is_animated: bool   # from @animated annotation

class ShaderParser:
    shaders: Dict[str, ShaderDefinition]

    def parse_directory(shader_dir: str) -> List[ShaderDefinition]
    def parse_file(filepath: str) -> List[ShaderDefinition]
    def get_shader(name: str) -> Optional[ShaderDefinition]
    def get_shaders_by_category() -> Dict[str, List[ShaderDefinition]]
    def list_available_shaders() -> List[str]
```

### TextShaderParser (shader_parser.py:310-534)
Parses text shader .rpy files (same structure as ShaderParser).

```python
@dataclass
class TextShaderDefinition:
    name: str           # e.g., "rainbow"
    category: str
    description: str
    file_description: str
    params: List[ShaderParam]
    source_file: str
    line_number: int
    is_animated: bool

class TextShaderParser:
    text_shaders: Dict[str, TextShaderDefinition]

    def parse_directory(shader_dir: str) -> List[TextShaderDefinition]
    def parse_file(filepath: str) -> List[TextShaderDefinition]
    def get_text_shader(name: str) -> Optional[TextShaderDefinition]
    def list_available_text_shaders() -> List[str]
```

### SelectionManager (ui_components.py:147-210)
Handles multi-selection with Ctrl+click and Shift+click.

```python
class SelectionManager:
    items: List[str]
    selected: List[str]
    last_selected: Optional[str]

    def update_items(items: List[str])
    def handle_click(name, ctrl=False, shift=False) -> List[str]
    def select_all() -> List[str]
    def select_none() -> List[str]
    def invert_selection() -> List[str]
    def is_selected(name) -> bool
    def clear()  # Alias for select_none
    def toggle(name)  # Toggle single item
```

### StatusBar (ui_components.py:339-384)
Status bar widget.

```python
class StatusBar:
    def __init__(parent: int)
    def update(auto_save: bool, undo_count: int, redo_count: int)
    def set_status(message: str, color: tuple)
```

### DemoGenerator (demo_generator.py:44-263)
Generates Ren'Py demo scripts.

```python
@dataclass
class DemoItem:
    transition: Optional[str]
    shader: Optional[str]

    @property
    def display_name() -> str
    @property
    def at_clause() -> str
    def is_empty() -> bool

class DemoGenerator:
    items: List[DemoItem]
    character_name: str
    character_image: str
    background: str
    label_name: str
    screen_width: int
    screen_height: int

    def add_item(transition, shader) -> bool
    def remove_item(index) -> bool
    def clear_items()
    def move_item(index, direction) -> bool
    def get_item(index) -> Optional[DemoItem]
    def generate_script() -> str
    def save_script(output_path) -> bool
    def generate_test_game_script() -> str
    def save_test_game(game_folder) -> bool
```

---

## Function Reference by Section

### preset_editor.py - Global Functions

#### UI Refresh Functions (lines 216-255)
```python
def refresh_all()                    # Refresh all UI elements
def update_status_bar()              # Update status bar display
def refresh_transition_ui()          # Refresh based on transition mode
def refresh_shader_ui()              # Refresh based on shader mode
def refresh_textshader_ui()          # Refresh based on text shader mode
```

#### Transition UI Functions (lines 262-878)
```python
# Manager mode
def refresh_transition_manager()     # Rebuild manager list
def trans_manager_select_callback()  # DPG callback wrapper
def trans_manager_select(name)       # Handle selection
def trans_select_all()
def trans_select_none()
def trans_invert_selection()
def trans_move_selected_top()
def trans_move_selected_up()
def trans_move_selected_down()
def trans_move_selected_bottom()
def trans_delete_selected()
def trans_duplicate_selected()

# Builder mode
def refresh_transition_builder()     # Refresh list + content
def refresh_transition_builder_list()
def refresh_transition_builder_content()
def trans_builder_select_callback()
def trans_builder_select(name)

# Field callbacks (DPG pattern: sender, app_data, user_data)
def trans_field_callback()           # Simple field changes
def trans_nested_callback()          # Nested dict changes (alpha, scale, rotation)
def trans_rename_callback()
def trans_update_name_button_callback()
def trans_toggle_start_callback()
def trans_toggle_end_callback()
def trans_update_start_x_callback()
def trans_update_start_y_callback()
def trans_update_end_x_callback()
def trans_update_end_y_callback()

# Data operations
def trans_update_field(name, field, value)
def trans_update_position(name, pos_type, key, value)
def trans_update_nested(name, category, key, value)
def trans_toggle_section_mode(name, pos_type, use_align)
def trans_update_position_smart(name, pos_type, axis, value)
def trans_rename_preset(old_name, new_name)

# JSON view
def refresh_transition_json()

# Helper
def _clean_float(value)              # Round to 2 decimal places
```

#### Shader UI Functions (lines 885-1399)
```python
# Manager mode (same pattern as transitions)
def refresh_shader_manager()
def shader_manager_select_callback()
def shader_manager_select(name)
def shader_select_all()
def shader_select_none()
def shader_invert_selection()
def shader_move_selected_top()
def shader_move_selected_up()
def shader_move_selected_down()
def shader_move_selected_bottom()
def shader_delete_selected()
def shader_duplicate_selected()

# Builder mode
def refresh_shader_builder()
def refresh_shader_builder_list()
def refresh_shader_builder_content()
def shader_builder_select_callback()
def shader_builder_select(name)
def shader_builder_source_changed()
def shader_builder_create_new()      # Create preset from shader

# Field callbacks
def shader_param_callback()
def shader_param_color_callback()
def shader_rename_callback()
def shader_update_name_button_callback()

# Data operations
def shader_update_field(name, field, value)
def shader_update_param(name, param, value)
def shader_update_param_color(name, param, rgba)
def shader_rename_preset(old_name, new_name)

# JSON view
def refresh_shader_json()
```

#### Text Shader UI Functions (lines 1402-2026)
```python
# Constants
BUILTIN_TEXT_SHADERS = [...]         # List of built-in Ren'Py text shaders

# Helpers
def get_all_text_shaders() -> List[str]  # Built-in + custom merged

# Manager mode (same pattern)
def refresh_textshader_manager()
def textshader_manager_select_callback()
def textshader_manager_select(name)
def textshader_select_all()
def textshader_select_none()
def textshader_invert_selection()
def textshader_move_selected_top()
def textshader_move_selected_up()
def textshader_move_selected_down()
def textshader_move_selected_bottom()
def textshader_delete_selected()
def textshader_duplicate_selected()

# Builder mode
def refresh_textshader_builder()
def refresh_textshader_builder_list()
def refresh_textshader_builder_content()
def textshader_builder_select_callback()
def textshader_builder_select(name)
def textshader_builder_create_new()

# Field callbacks
def textshader_shader_callback()
def textshader_shader_param_callback()
def textshader_text_callback()
def textshader_text_bool_callback()
def textshader_text_color_callback()
def textshader_outline_callback()
def textshader_outline_color_callback()
def textshader_add_outline_callback()
def textshader_remove_outline_callback()
def textshader_rename_callback()
def textshader_update_name_button_callback()

# Data operations
def textshader_rename_preset(old_name, new_name)

# JSON view
def refresh_textshader_json()
```

#### Mode Switching (lines 2029-2092)
```python
def switch_transition_mode(mode: EditorMode)
def switch_shader_mode(mode: EditorMode)
def switch_textshader_mode(mode: EditorMode)
```

#### Add New Presets (lines 2095-2143)
```python
def add_new_transition()
def add_new_shader()
def add_new_textshader()
```

#### Export Demo Modal (lines 2146-2475)
```python
# State
demo_trans_selection: Optional[str]
demo_shader_selection: Optional[str]

# Modal
def show_export_demo_modal()
def refresh_demo_trans_list()
def refresh_demo_shader_list()
def refresh_demo_items_list()
def demo_trans_select_callback()
def demo_shader_select_callback()
def demo_select_transition(name)
def demo_select_shader(name)
def demo_add_item()
def demo_clear_items()
def demo_remove_item_callback()
def demo_remove_item(index)
def demo_generate()
def demo_run()
```

#### Settings Modal (lines 2478-2756)
```python
def show_settings_modal()
def show_settings_modal_with_values(...)
def settings_browse_file(target_tag)
def settings_browse_exe(target_tag)
def settings_browse_folder(target_tag)
def reopen_settings_with_values(values, new_path)
def settings_apply()
```

#### Main UI Setup (lines 2759-2973)
```python
def setup_ui()                       # Build complete UI structure
def setup_keyboard_shortcuts()       # Ctrl+Z, Ctrl+Y handlers
```

#### Entry Point (lines 2976-3022)
```python
def main()                           # Application entry point
```

---

## DearPyGui Callback Pattern

All DPG callbacks follow this signature:
```python
def callback(sender, app_data, user_data):
    # sender: widget ID that triggered callback
    # app_data: widget's current value
    # user_data: custom data passed via user_data= parameter
    pass
```

**IMPORTANT:** When using `user_data=`, the value passed replaces the default third argument. This caused bugs when using lambda default captures like `lambda s, a, k=key:` because `user_data` overwrote `k`.

**Solution:** Always use explicit `user_data=(name, key)` tuples and unpack in callback:
```python
def my_callback(sender, app_data, user_data):
    if user_data:
        name, key = user_data
        # Use name and key
```

---

## UI Element Tags

These are the fixed tag names used for UI elements:

### Transition Tab
- `trans_builder_panel` - Builder mode container
- `trans_builder_list` - Preset list in builder
- `trans_builder_content` - Editor panel in builder
- `trans_manager_panel` - Manager mode container
- `trans_manager_list` - List in manager
- `trans_json_panel` - JSON mode container
- `trans_json_text` - JSON text display

### Shader Tab
- `shader_builder_panel`
- `shader_builder_list`
- `shader_builder_content`
- `shader_builder_source_combo` - "Create from shader" dropdown
- `shader_manager_panel`
- `shader_manager_list`
- `shader_json_panel`
- `shader_json_text`

### Text Shader Tab
- `textshader_builder_panel`
- `textshader_builder_list`
- `textshader_builder_content`
- `textshader_builder_source_combo` - "Create from shader" dropdown
- `textshader_manager_panel`
- `textshader_manager_list`
- `textshader_json_panel`
- `textshader_json_text`

### Other
- `primary_window` - Main window
- `status_bar_container` - Status bar parent
- `export_demo_window` - Demo modal
- `settings_window` - Settings modal

---

## Data Flow

### Loading Data
```
main()
  -> app.load_config()     # Read config.json
  -> app.load_data()       # JsonManager.load() + ShaderParser.parse_directory()
  -> refresh_all()         # Update UI
```

### User Edits a Field
```
User changes input
  -> DPG callback fires
  -> Callback unpacks user_data
  -> Calls data operation (e.g., trans_update_field)
  -> JsonManager.set_transition()
     -> push_undo()
     -> Update data dict
     -> Auto-save if enabled
     -> Notify change callbacks
  -> update_status_bar()
```

### Mode Switching
```
User clicks mode radio button
  -> switch_*_mode(EditorMode.BUILDER/MANAGER/JSON)
  -> Update app.*_mode
  -> Show/hide panels via dpg.configure_item(tag, show=bool)
  -> refresh_*_ui() for that mode
```

---

## JSON Schema Reference

### transition_presets.json
```json
{
    "presets": {
        "preset_name": {
            "start_position": { "xoffset": 0, "yoffset": 0 }  // or xalign/yalign
            "end_position": { "xoffset": 0, "yoffset": 0 },
            "alpha": { "start": 1.0, "end": 1.0 },
            "scale": { "start": 1.0, "end": 1.0 },
            "rotation": { "start": 0, "end": 0 },
            "duration": 0.4,
            "easing": "easeout"  // linear, easein, easeout, ease
        }
    }
}
```

### shader_presets.json
```json
{
    "shader_presets": {
        "preset_name": {
            "shader": "shader.glow",
            "animated": false,
            "params": {
                "u_glow_color": "#FFFFFF",
                "u_strength": 0.5
            }
        }
    }
}
```

### textshader_presets.json
```json
{
    "presets": {
        "preset_name": {
            "shader": "wave",  // or null for no shader
            "shader_params": {
                "u_amplitude": 2.0
            },
            "text": {
                "font": "DejaVuSans.ttf",
                "size": 28,
                "color": "#FFFFFF",
                "outlines": [[2, "#000000", 0, 0]],
                "kerning": 0.0,
                "line_spacing": 0,
                "slow_cps": 30,
                "bold": false,
                "italic": false
            }
        }
    }
}
```

---

## Annotation Format for Shaders

### Image Shaders (.rpy files)
```python
## @tool-category: CategoryName
## @tool-description: Brief description

# @shader: shader.name
# @param u_param_name: type, range=min-max, default=value, description=text
# @animated
renpy.register_shader("shader.name", ...)
```

### Text Shaders (.rpy files)
```python
## @tool-category: CategoryName
## @tool-description: Brief description

# @textshader: shader_name
# @param u_param_name: type, range=min-max, default=value, description=text
# @animated
renpy.register_textshader("shader_name", ...)
```

---

## Common Patterns

### Adding a New Field to Builder
1. In `refresh_*_builder_content()`, add DPG widget with:
   - `callback=*_field_callback` (or new callback)
   - `user_data=(name, "field_name")`
2. If needed, add callback function following pattern
3. Ensure data operation updates correct JSON structure

### Adding a New Preset Type
1. Add data storage in `JsonManager` (data dict, methods)
2. Add parser in `shader_parser.py` if needed
3. Add UI state in `AppState` (mode, selection)
4. Add tab in `setup_ui()`
5. Add all refresh functions following existing pattern
6. Add mode switching function
7. Update `refresh_all()` to include new refresh

---

## Testing Checklist

When modifying the editor:
- [ ] Preset creation works
- [ ] Preset editing saves changes
- [ ] Undo/redo works
- [ ] Mode switching works (Builder/Manager/JSON)
- [ ] Selection (single, Ctrl+click, Shift+click) works
- [ ] Move/duplicate/delete works
- [ ] JSON view displays current data
- [ ] No exceptions in console
