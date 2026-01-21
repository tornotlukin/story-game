"""
textshader_tab.py - Text shader presets tab UI

Handles all UI and callbacks for the Text Shaders tab:
- Manager mode: List with multi-select, move, duplicate, delete
- Builder mode: Edit text shader + text styling params
- JSON mode: Read-only JSON view

Text shader presets combine:
- Shader effect (wave, jitter, typewriter, etc.) or none
- Text styling (font, size, color, outlines, etc.)
"""

import dearpygui.dearpygui as dpg
import os
import time
from pathlib import Path
from typing import Any, List

from modules.ui_components import (
    apply_selection_theme, hex_to_rgb, rgba_to_hex,
    show_confirm_dialog, add_color_edit_with_hex
)


# =============================================================================
# Constants
# =============================================================================

# Built-in Ren'Py text shaders
BUILTIN_TEXT_SHADERS = [
    "dissolve",
    "flip",
    "jitter",
    "linetexture",
    "offset",
    "slowalpha",
    "texture",
    "typewriter",
    "wave",
    "zoom"
]


# =============================================================================
# Module State
# =============================================================================

_app = None
_EditorMode = None
_update_status_bar = None


def init_textshader_tab(app_state, editor_mode_enum, status_callback):
    """Initialize module with app state reference."""
    global _app, _EditorMode, _update_status_bar
    _app = app_state
    _EditorMode = editor_mode_enum
    _update_status_bar = status_callback


# =============================================================================
# Helper
# =============================================================================

def _clean_float(value: Any) -> Any:
    """Round floats to 2 decimal places."""
    if isinstance(value, float):
        return round(value, 2)
    return value


def get_all_text_shaders() -> List[str]:
    """Get all available text shaders: built-in + custom from parsed files."""
    shaders = ["(none)"]  # Always start with no shader option
    shaders.extend(BUILTIN_TEXT_SHADERS)

    # Add custom text shaders from parsed files
    if _app and _app.text_shader_parser:
        custom = _app.text_shader_parser.list_available_text_shaders()
        for name in custom:
            if name not in shaders:
                shaders.append(name)

    return shaders


def get_available_fonts() -> List[str]:
    """Get list of fonts from the preset editor's game/fonts folder."""
    fonts = ["DejaVuSans.ttf"]  # Always include Ren'Py default

    # Look for fonts in the preset editor's game folder
    fonts_dir = Path(__file__).parent.parent / "game" / "fonts"
    if fonts_dir.exists():
        for f in fonts_dir.iterdir():
            if f.suffix.lower() in ('.ttf', '.otf'):
                font_name = f.name
                if font_name not in fonts:
                    fonts.append(font_name)

    return sorted(fonts)


# =============================================================================
# UI Setup
# =============================================================================

def setup_textshader_tab(parent):
    """Build the Text Shaders tab UI structure."""
    with dpg.tab(label="TEXT SHADERS", parent=parent):
        with dpg.group(horizontal=True):
            dpg.add_text("Mode:")
            dpg.add_radio_button(
                items=["Builder", "Manager", "JSON"],
                default_value="Builder",
                horizontal=True,
                callback=lambda s, a: switch_textshader_mode(_EditorMode[a.upper()])
            )
            dpg.add_spacer(width=30)
            dpg.add_button(label="+ New Text Preset", callback=add_new_textshader)

        dpg.add_separator()

        # Builder panel
        with dpg.group(tag="textshader_builder_panel", show=True):
            # Top: Create new preset from text shader
            with dpg.group(horizontal=True):
                dpg.add_text("Create from shader:")
                dpg.add_combo(
                    tag="textshader_builder_source_combo",
                    items=[],
                    default_value="(none)",
                    width=200
                )
                dpg.add_button(
                    label="Create New Preset",
                    callback=textshader_builder_create_new
                )
            dpg.add_separator()

            # Main content
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text("Preset List")
                    dpg.add_separator()
                    with dpg.child_window(tag="textshader_builder_list", width=250, height=500):
                        pass
                dpg.add_spacer(width=10)
                with dpg.child_window(width=-1, height=500, tag="textshader_builder_content"):
                    dpg.add_text("Select a preset to edit")

        # Manager panel
        with dpg.group(tag="textshader_manager_panel", show=False):
            with dpg.child_window(height=-30, tag="textshader_manager_list"):
                pass

        # JSON panel
        with dpg.group(tag="textshader_json_panel", show=False):
            dpg.add_input_text(
                tag="textshader_json_text",
                multiline=True,
                width=-1,
                height=-30,
                readonly=True
            )


# =============================================================================
# Mode Switching
# =============================================================================

def switch_textshader_mode(mode):
    """Switch between Builder, Manager, and JSON modes."""
    _app.textshader_mode = mode

    if dpg.does_item_exist("textshader_builder_panel"):
        dpg.configure_item("textshader_builder_panel", show=(mode == _EditorMode.BUILDER))
    if dpg.does_item_exist("textshader_manager_panel"):
        dpg.configure_item("textshader_manager_panel", show=(mode == _EditorMode.MANAGER))
    if dpg.does_item_exist("textshader_json_panel"):
        dpg.configure_item("textshader_json_panel", show=(mode == _EditorMode.JSON))

    refresh_textshader_ui()


# =============================================================================
# Refresh Functions
# =============================================================================

def refresh_textshader_ui():
    """Refresh text shader tab content based on current mode."""
    if _app.textshader_mode == _EditorMode.MANAGER:
        refresh_textshader_manager()
    elif _app.textshader_mode == _EditorMode.BUILDER:
        refresh_textshader_builder()
    elif _app.textshader_mode == _EditorMode.JSON:
        refresh_textshader_json()


def refresh_textshader_manager():
    """Refresh the text shader manager list."""
    if not dpg.does_item_exist("textshader_manager_list"):
        return

    dpg.delete_item("textshader_manager_list", children_only=True)

    names = _app.json_mgr.get_textshader_names()
    selected = _app.textshader_selection.selected

    # Top toolbar
    with dpg.group(horizontal=True, parent="textshader_manager_list"):
        dpg.add_text(f"Selected: {len(selected)} of {len(names)}")
        dpg.add_spacer(width=10)
        dpg.add_button(label="All", callback=textshader_select_all, width=40)
        dpg.add_button(label="None", callback=textshader_select_none, width=45)
        dpg.add_button(label="Invert", callback=textshader_invert_selection, width=50)
        dpg.add_spacer(width=20)
        dpg.add_button(label="^^", width=25, callback=textshader_move_selected_top)
        dpg.add_button(label="^", width=25, callback=textshader_move_selected_up)
        dpg.add_button(label="v", width=25, callback=textshader_move_selected_down)
        dpg.add_button(label="vv", width=25, callback=textshader_move_selected_bottom)
        dpg.add_spacer(width=10)
        dpg.add_button(label="Dupe", width=45, callback=textshader_duplicate_selected)
        dpg.add_button(label="Del", width=40, callback=textshader_delete_selected)

    dpg.add_separator(parent="textshader_manager_list")

    # Selectable list
    for name in names:
        is_selected = name in selected
        prefix = "[*] " if is_selected else "    "
        item_id = dpg.add_selectable(
            label=f"{prefix}text_{name}",
            default_value=is_selected,
            callback=textshader_manager_select_callback,
            user_data=name,
            width=800,
            parent="textshader_manager_list"
        )
        apply_selection_theme(item_id, is_selected)


def refresh_textshader_builder():
    """Refresh the text shader builder panel."""
    # Update the available text shaders combo
    if dpg.does_item_exist("textshader_builder_source_combo"):
        available = get_all_text_shaders()
        dpg.configure_item("textshader_builder_source_combo", items=available)
        current = dpg.get_value("textshader_builder_source_combo")
        if not current or current not in available:
            dpg.set_value("textshader_builder_source_combo", "(none)")

    refresh_textshader_builder_list()
    refresh_textshader_builder_content()


def refresh_textshader_builder_list():
    """Refresh the text shader builder list panel."""
    if not dpg.does_item_exist("textshader_builder_list"):
        return

    dpg.delete_item("textshader_builder_list", children_only=True)

    presets = _app.json_mgr.get_textshader_names()
    for name in presets:
        is_selected = name in _app.textshader_selection.selected
        prefix = "[*] " if is_selected else "    "
        item_id = dpg.add_selectable(
            label=f"{prefix}{name}",
            default_value=is_selected,
            callback=textshader_builder_select_callback,
            user_data=name,
            width=230,
            parent="textshader_builder_list"
        )
        apply_selection_theme(item_id, is_selected)


def refresh_textshader_builder_content():
    """Refresh the text shader builder content/editor panel."""
    if not dpg.does_item_exist("textshader_builder_content"):
        return

    dpg.delete_item("textshader_builder_content", children_only=True)

    selected = _app.textshader_selection.selected
    if len(selected) != 1:
        dpg.add_text("Select a single preset to edit",
                    parent="textshader_builder_content")
        return

    name = selected[0]
    preset = _app.json_mgr.get_textshader(name)
    if not preset:
        dpg.add_text(f"Preset '{name}' not found",
                    parent="textshader_builder_content")
        return

    parent = "textshader_builder_content"

    # Editable preset name
    with dpg.group(horizontal=True, parent=parent):
        dpg.add_text("Preset Name:")
        name_input = dpg.add_input_text(
            default_value=name,
            callback=textshader_rename_callback,
            user_data=name,
            on_enter=True,
            width=150
        )
        dpg.add_button(
            label="Update Name",
            callback=textshader_update_name_button_callback,
            user_data=(name, name_input)
        )
    dpg.add_separator(parent=parent)

    # Shader info (read-only display, use "Create from shader" to change)
    current_shader = preset.get("shader")
    shader_params = preset.get("shader_params", {})
    if current_shader:
        dpg.add_text(f"Shader: {current_shader}", parent=parent, color=(150, 200, 255))
        if shader_params:
            dpg.add_text("Shader Parameters", parent=parent, color=(150, 150, 150))
            for param_name, param_value in shader_params.items():
                if isinstance(param_value, float):
                    dpg.add_input_float(
                        label=param_name,
                        default_value=param_value,
                        callback=textshader_shader_param_callback,
                        user_data=(name, param_name),
                        step=0.1,
                        width=150,
                        parent=parent
                    )
                elif isinstance(param_value, str):
                    dpg.add_input_text(
                        label=param_name,
                        default_value=param_value,
                        callback=textshader_shader_param_str_callback,
                        user_data=(name, param_name),
                        width=150,
                        parent=parent
                    )
    else:
        dpg.add_text("Shader: (none)", parent=parent, color=(150, 150, 150))

    # Text styling section
    dpg.add_separator(parent=parent)
    dpg.add_text("Text Styling", parent=parent, color=(255, 200, 150))

    text_props = preset.get("text", {})

    # Font dropdown
    available_fonts = get_available_fonts()
    current_font = text_props.get("font", "DejaVuSans.ttf")
    # Ensure current font is in list even if not found in folder
    if current_font not in available_fonts:
        available_fonts.append(current_font)
    dpg.add_combo(
        label="Font",
        items=available_fonts,
        default_value=current_font,
        callback=textshader_text_callback,
        user_data=(name, "font"),
        width=250,
        parent=parent
    )

    # Size
    dpg.add_input_int(
        label="Size",
        default_value=text_props.get("size", 28),
        callback=textshader_text_callback,
        user_data=(name, "size"),
        min_value=8, max_value=100,
        width=150,
        parent=parent
    )

    # Color (with hex input and alpha)
    color_hex = text_props.get("color", "#FFFFFFFF")
    add_color_edit_with_hex(
        label="Color",
        default_value=color_hex,
        callback=textshader_text_color_callback,
        user_data=(name, "color"),
        parent=parent,
        color_width=150,
        include_alpha=True
    )

    # Kerning
    dpg.add_input_float(
        label="Kerning",
        default_value=text_props.get("kerning", 0.0),
        callback=textshader_text_callback,
        user_data=(name, "kerning"),
        step=0.5,
        width=150,
        parent=parent
    )

    # Line spacing
    dpg.add_input_int(
        label="Line Spacing",
        default_value=text_props.get("line_spacing", 0),
        callback=textshader_text_callback,
        user_data=(name, "line_spacing"),
        width=150,
        parent=parent
    )

    # Text alignment (0.0=left, 0.5=center, 1.0=right)
    dpg.add_combo(
        label="Text Align",
        items=["Left (0.0)", "Center (0.5)", "Right (1.0)"],
        default_value=_align_to_label(text_props.get("text_align", 0.0)),
        callback=_on_text_align_change,
        user_data=(name, "text_align"),
        width=150,
        parent=parent
    )

    # Horizontal position of text block
    dpg.add_combo(
        label="X Align",
        items=["Left (0.0)", "Center (0.5)", "Right (1.0)"],
        default_value=_align_to_label(text_props.get("xalign", 0.0)),
        callback=_on_text_align_change,
        user_data=(name, "xalign"),
        width=150,
        parent=parent
    )

    # CPS
    dpg.add_input_int(
        label="Slow CPS",
        default_value=text_props.get("slow_cps", 0),
        callback=textshader_text_callback,
        user_data=(name, "slow_cps"),
        min_value=0, max_value=200,
        width=150,
        parent=parent
    )

    # Bold/Italic
    with dpg.group(horizontal=True, parent=parent):
        dpg.add_checkbox(
            label="Bold",
            default_value=text_props.get("bold", False),
            callback=textshader_text_bool_callback,
            user_data=(name, "bold")
        )
        dpg.add_checkbox(
            label="Italic",
            default_value=text_props.get("italic", False),
            callback=textshader_text_bool_callback,
            user_data=(name, "italic")
        )

    # Outlines section
    dpg.add_separator(parent=parent)
    dpg.add_text("Outlines", parent=parent, color=(150, 255, 150))
    outlines = text_props.get("outlines", [])
    print(f"[DEBUG] Creating outline widgets for '{name}': {len(outlines)} outlines")

    for i, outline in enumerate(outlines):
        outline_val = outline[0] if len(outline) > 0 else 1
        print(f"[DEBUG] Creating outline[{i}] widget with value={outline_val}")
        try:
            # Define callback inline, capturing user_data
            def make_outline_size_callback(preset_name, outline_idx):
                def callback(sender, app_data, user_data):
                    print(f"[OUTLINE SIZE CALLBACK] sender={sender}, value={app_data}, preset={preset_name}, idx={outline_idx}")
                    preset = _app.json_mgr.get_textshader(preset_name) or {}
                    if "text" not in preset:
                        preset["text"] = {}
                    if "outlines" not in preset["text"]:
                        preset["text"]["outlines"] = []
                    while len(preset["text"]["outlines"]) <= outline_idx:
                        preset["text"]["outlines"].append([1, "#000000", 0, 0])
                    preset["text"]["outlines"][outline_idx][0] = app_data
                    _app.json_mgr.set_textshader(preset_name, preset)
                    print(f"[OUTLINE SIZE CALLBACK] Saved! New outlines: {preset['text']['outlines']}")
                return callback

            # TEST: Put size widget DIRECTLY in parent, not in a group
            outline_size_widget = dpg.add_input_int(
                label=f"Outline {i} Size",
                default_value=outline_val,
                callback=make_outline_size_callback(name, i),
                width=100,
                min_value=0,
                max_value=20,
                parent=parent  # Direct parent, not group!
            )
            print(f"[DEBUG] Created outline size widget (in parent): {outline_size_widget}")

            # Group for color (with hex input and alpha) and delete button
            outline_group = dpg.add_group(horizontal=True, parent=parent)
            # Color (with hex input and alpha)
            outline_color = outline[1] if len(outline) > 1 else "#000000FF"
            add_color_edit_with_hex(
                label=f"##outline_color_{name}_{i}",
                default_value=outline_color,
                callback=textshader_outline_color_callback,
                user_data=(name, i),
                parent=outline_group,
                color_width=100,
                include_alpha=True
            )
            dpg.add_button(
                label="X",
                callback=textshader_remove_outline_callback,
                user_data=(name, i),
                width=25,
                parent=outline_group
            )
        except Exception as e:
            print(f"[DEBUG] ERROR creating outline widget: {e}")
            import traceback
            traceback.print_exc()

    dpg.add_button(
        label="+ Add Outline",
        callback=textshader_add_outline_callback,
        user_data=name,
        parent=parent
    )


def refresh_textshader_json():
    """Refresh the text shader JSON view."""
    import json
    if dpg.does_item_exist("textshader_json_text"):
        text = json.dumps(_app.json_mgr.textshader_data, indent=2)
        dpg.set_value("textshader_json_text", text)


# =============================================================================
# Selection Callbacks
# =============================================================================

def textshader_manager_select_callback(sender, app_data, user_data):
    textshader_manager_select(user_data)


def textshader_manager_select(name: str):
    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)
    shift = dpg.is_key_down(dpg.mvKey_LShift) or dpg.is_key_down(dpg.mvKey_RShift)
    _app.textshader_selection.handle_click(name, ctrl, shift)
    refresh_textshader_manager()


def textshader_builder_select_callback(sender, app_data, user_data):
    textshader_builder_select(user_data)


def textshader_builder_select(name: str):
    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)
    old_selection = list(_app.textshader_selection.selected)

    if ctrl:
        if name in _app.textshader_selection.selected:
            _app.textshader_selection.selected.remove(name)
        else:
            _app.textshader_selection.selected.append(name)
    else:
        _app.textshader_selection.selected = [name]

    refresh_textshader_builder_list()

    # Only refresh content if selection actually changed
    # This prevents destroying widgets before their callbacks fire
    if _app.textshader_selection.selected != old_selection:
        refresh_textshader_builder_content()


# =============================================================================
# Selection Actions
# =============================================================================

def textshader_select_all():
    _app.textshader_selection.select_all()
    refresh_textshader_manager()


def textshader_select_none():
    _app.textshader_selection.select_none()
    refresh_textshader_manager()


def textshader_invert_selection():
    _app.textshader_selection.invert_selection()
    refresh_textshader_manager()


# =============================================================================
# Move Actions
# =============================================================================

def textshader_move_selected_top():
    for name in reversed(_app.textshader_selection.selected):
        _app.json_mgr.move_textshader(name, "top")
    refresh_textshader_manager()


def textshader_move_selected_up():
    for name in _app.textshader_selection.selected:
        _app.json_mgr.move_textshader(name, "up")
    refresh_textshader_manager()


def textshader_move_selected_down():
    for name in reversed(_app.textshader_selection.selected):
        _app.json_mgr.move_textshader(name, "down")
    refresh_textshader_manager()


def textshader_move_selected_bottom():
    for name in _app.textshader_selection.selected:
        _app.json_mgr.move_textshader(name, "bottom")
    refresh_textshader_manager()


# =============================================================================
# Duplicate/Delete Actions
# =============================================================================

def textshader_duplicate_selected():
    selected = _app.textshader_selection.selected.copy()
    for name in selected:
        new_name = _app.json_mgr.get_unique_textshader_name(f"{name}_copy")
        _app.json_mgr.duplicate_textshader(name, new_name)
    _app.textshader_selection.update_items(_app.json_mgr.get_textshader_names())
    refresh_textshader_manager()
    if _update_status_bar:
        _update_status_bar()


def textshader_delete_selected():
    selected = _app.textshader_selection.selected.copy()
    if not selected:
        return

    def do_delete():
        _app.json_mgr.delete_textshaders(selected)
        _app.textshader_selection.selected = []
        _app.textshader_selection.update_items(_app.json_mgr.get_textshader_names())
        refresh_textshader_manager()
        if _update_status_bar:
            _update_status_bar()

    show_confirm_dialog(
        "Delete Selected",
        f"Delete {len(selected)} text shader(s)?",
        do_delete
    )


# =============================================================================
# Create New
# =============================================================================

def textshader_builder_create_new():
    """Create a new text shader preset based on selected source shader."""
    source = dpg.get_value("textshader_builder_source_combo") if dpg.does_item_exist("textshader_builder_source_combo") else "(none)"

    shader_value = source if source != "(none)" else None

    if shader_value:
        base_name = shader_value
    else:
        base_name = "text_style"
    new_name = _app.json_mgr.get_unique_textshader_name(base_name)

    # Build shader params from parsed text shader definition (if custom)
    shader_params = {}
    if shader_value and shader_value not in BUILTIN_TEXT_SHADERS:
        shader_def = _app.text_shader_parser.get_text_shader(shader_value)
        if shader_def:
            for param in shader_def.params:
                if param.default is not None:
                    shader_params[param.name] = param.default
                elif param.param_type == "color":
                    shader_params[param.name] = "#FFFFFF"
                elif param.param_type == "float":
                    shader_params[param.name] = param.min_value if param.min_value is not None else 0.0
                elif param.param_type == "int":
                    shader_params[param.name] = int(param.min_value) if param.min_value is not None else 0

    preset_data = {
        "shader": shader_value,
        "shader_params": shader_params,
        "text": {
            "font": "DejaVuSans.ttf",
            "size": 28,
            "color": "#FFFFFF",
            "outlines": [[2, "#000000", 0, 0]],
            "kerning": 0.0,
            "line_spacing": 0,
            "text_align": 0.0,
            "xalign": 0.0,
            "slow_cps": 30,
            "bold": False,
            "italic": False
        }
    }

    _app.json_mgr.add_textshader(new_name, preset_data)
    _app.textshader_selection.update_items(_app.json_mgr.get_textshader_names())
    _app.textshader_selection.selected = [new_name]
    refresh_textshader_builder()
    if _update_status_bar:
        _update_status_bar()


def add_new_textshader():
    """Add a new text shader preset with defaults."""
    name = _app.json_mgr.get_unique_textshader_name("new_text_preset")
    _app.json_mgr.add_textshader(name, {
        "shader": None,
        "shader_params": {},
        "text": {
            "font": "DejaVuSans.ttf",
            "size": 28,
            "color": "#FFFFFF",
            "outlines": [[2, "#000000", 0, 0]],
            "kerning": 0.0,
            "line_spacing": 0,
            "text_align": 0.0,
            "xalign": 0.0,
            "slow_cps": 30,
            "bold": False,
            "italic": False
        }
    })
    _app.textshader_selection.update_items(_app.json_mgr.get_textshader_names())
    _app.textshader_selection.selected = [name]
    refresh_textshader_ui()
    if _update_status_bar:
        _update_status_bar()


# =============================================================================
# Field Callbacks
# =============================================================================

def textshader_shader_callback(sender, app_data, user_data):
    name = user_data
    shader_value = app_data if app_data != "(none)" else None
    preset = _app.json_mgr.get_textshader(name) or {}
    preset["shader"] = shader_value
    _app.json_mgr.set_textshader(name, preset)
    refresh_textshader_builder_content()
    if _update_status_bar:
        _update_status_bar()


def textshader_shader_param_callback(sender, app_data, user_data):
    if user_data:
        name, param = user_data
        preset = _app.json_mgr.get_textshader(name) or {}
        if "shader_params" not in preset:
            preset["shader_params"] = {}
        preset["shader_params"][param] = _clean_float(app_data)
        _app.json_mgr.set_textshader(name, preset)
        if _update_status_bar:
            _update_status_bar()


def textshader_shader_param_str_callback(sender, app_data, user_data):
    """Handle string shader parameters (like vec2 values: "1.5, 1.5")."""
    if user_data:
        name, param = user_data
        preset = _app.json_mgr.get_textshader(name) or {}
        if "shader_params" not in preset:
            preset["shader_params"] = {}
        preset["shader_params"][param] = app_data
        _app.json_mgr.set_textshader(name, preset)
        if _update_status_bar:
            _update_status_bar()


def _align_to_label(value: float) -> str:
    """Convert alignment float to combo label."""
    if value <= 0.25:
        return "Left (0.0)"
    elif value <= 0.75:
        return "Center (0.5)"
    else:
        return "Right (1.0)"


def _label_to_align(label: str) -> float:
    """Convert combo label to alignment float."""
    if "0.5" in label or "Center" in label:
        return 0.5
    elif "1.0" in label or "Right" in label:
        return 1.0
    else:
        return 0.0


def _on_text_align_change(sender, app_data, user_data):
    """Handle text alignment combo changes."""
    if user_data:
        name, prop = user_data
        preset = _app.json_mgr.get_textshader(name) or {}
        if "text" not in preset:
            preset["text"] = {}
        preset["text"][prop] = _label_to_align(app_data)
        _app.json_mgr.set_textshader(name, preset)
        if _update_status_bar:
            _update_status_bar()


def textshader_text_callback(sender, app_data, user_data):
    print(f"[DEBUG] textshader_text_callback: sender={sender}, app_data={app_data}, user_data={user_data}")
    if user_data:
        name, prop = user_data
        preset = _app.json_mgr.get_textshader(name) or {}
        if "text" not in preset:
            preset["text"] = {}
        preset["text"][prop] = _clean_float(app_data)
        _app.json_mgr.set_textshader(name, preset)
        if _update_status_bar:
            _update_status_bar()


def textshader_text_bool_callback(sender, app_data, user_data):
    if user_data:
        name, prop = user_data
        preset = _app.json_mgr.get_textshader(name) or {}
        if "text" not in preset:
            preset["text"] = {}
        preset["text"][prop] = app_data
        _app.json_mgr.set_textshader(name, preset)
        if _update_status_bar:
            _update_status_bar()


def textshader_text_color_callback(sender, app_data, user_data):
    """Handle text color changes. app_data is hex string from add_color_edit_with_hex."""
    if user_data:
        name, prop = user_data
        preset = _app.json_mgr.get_textshader(name) or {}
        if "text" not in preset:
            preset["text"] = {}
        # app_data is already a hex string from add_color_edit_with_hex
        preset["text"][prop] = app_data
        _app.json_mgr.set_textshader(name, preset)
        if _update_status_bar:
            _update_status_bar()


def _outline_deactivated_handler(sender, app_data, user_data):
    """Handler for outline input deactivation (backup mechanism via item_handler_registry)."""
    print(f"[DEBUG] _outline_deactivated_handler CALLED! sender={sender}")
    # Get the current value from the widget
    try:
        current_value = dpg.get_value(sender)
        print(f"[DEBUG]   current_value from widget: {current_value}, user_data={user_data}")
        # Call the main callback with the value
        textshader_outline_callback(sender, current_value, user_data)
    except Exception as e:
        print(f"[DEBUG]   ERROR in _outline_deactivated_handler: {e}")


def textshader_outline_callback(sender, app_data, user_data):
    """Callback for outline size changes. Triggers on deactivation (focus loss) or spinner arrows."""
    print(f"[DEBUG] textshader_outline_callback CALLED!")
    print(f"[DEBUG]   sender={sender}, app_data={app_data}, user_data={user_data}")
    if user_data is None:
        print(f"[DEBUG]   user_data is None, returning early")
        return
    if not user_data:
        print(f"[DEBUG]   user_data is falsy: {repr(user_data)}, returning early")
        return
    if user_data:
        name, outline_idx, prop_idx = user_data
        preset = _app.json_mgr.get_textshader(name) or {}
        if "text" not in preset:
            preset["text"] = {}
        if "outlines" not in preset["text"]:
            preset["text"]["outlines"] = []
        # Ensure outline array has enough entries
        while len(preset["text"]["outlines"]) <= outline_idx:
            preset["text"]["outlines"].append([1, "#000000", 0, 0])
        # Ensure this specific outline has enough elements for prop_idx
        outline = preset["text"]["outlines"][outline_idx]
        while len(outline) <= prop_idx:
            # Extend with defaults: [size, color, x_offset, y_offset]
            defaults = [1, "#000000", 0, 0]
            outline.append(defaults[len(outline)] if len(outline) < 4 else 0)
        outline[prop_idx] = app_data
        _app.json_mgr.set_textshader(name, preset)
        if _update_status_bar:
            _update_status_bar()


def textshader_outline_color_callback(sender, app_data, user_data):
    """Handle outline color changes. app_data is hex string from add_color_edit_with_hex."""
    if user_data:
        name, outline_idx = user_data
        preset = _app.json_mgr.get_textshader(name) or {}
        if "text" not in preset:
            preset["text"] = {}
        if "outlines" not in preset["text"]:
            preset["text"]["outlines"] = []
        # Ensure outline array has enough entries
        while len(preset["text"]["outlines"]) <= outline_idx:
            preset["text"]["outlines"].append([1, "#000000", 0, 0])
        # Ensure this specific outline has at least 2 elements for color (index 1)
        outline = preset["text"]["outlines"][outline_idx]
        while len(outline) < 2:
            defaults = [1, "#000000", 0, 0]
            outline.append(defaults[len(outline)])
        # app_data is already a hex string from add_color_edit_with_hex
        outline[1] = app_data
        _app.json_mgr.set_textshader(name, preset)
        if _update_status_bar:
            _update_status_bar()


def textshader_add_outline_callback(sender, app_data, user_data):
    name = user_data
    preset = _app.json_mgr.get_textshader(name) or {}
    if "text" not in preset:
        preset["text"] = {}
    if "outlines" not in preset["text"]:
        preset["text"]["outlines"] = []
    preset["text"]["outlines"].append([1, "#000000", 0, 0])
    _app.json_mgr.set_textshader(name, preset)
    refresh_textshader_builder_content()
    if _update_status_bar:
        _update_status_bar()


def textshader_remove_outline_callback(sender, app_data, user_data):
    if user_data:
        name, outline_idx = user_data
        preset = _app.json_mgr.get_textshader(name) or {}
        if "text" in preset and "outlines" in preset["text"]:
            if 0 <= outline_idx < len(preset["text"]["outlines"]):
                del preset["text"]["outlines"][outline_idx]
                _app.json_mgr.set_textshader(name, preset)
                refresh_textshader_builder_content()
                if _update_status_bar:
                    _update_status_bar()


def textshader_rename_callback(sender, app_data, user_data):
    if user_data:
        textshader_rename_preset(user_data, app_data)


def textshader_update_name_button_callback(sender, app_data, user_data):
    old_name, input_tag = user_data
    new_name = dpg.get_value(input_tag)
    textshader_rename_preset(old_name, new_name)


# =============================================================================
# Data Operations
# =============================================================================

def textshader_rename_preset(old_name: str, new_name: str):
    """Rename a text shader preset."""
    new_name = new_name.strip()
    if not new_name or new_name == old_name:
        return
    if _app.json_mgr.get_textshader(new_name):
        return
    preset = _app.json_mgr.get_textshader(old_name)
    if preset:
        _app.json_mgr.set_textshader(new_name, preset)
        _app.json_mgr.delete_textshader(old_name)
        _app.textshader_selection.update_items(_app.json_mgr.get_textshader_names())
        _app.textshader_selection.selected = [new_name]
        refresh_textshader_ui()
        if _update_status_bar:
            _update_status_bar()
