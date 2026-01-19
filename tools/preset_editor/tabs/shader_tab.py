"""
shader_tab.py - Shader presets tab UI

Handles all UI and callbacks for the Shaders tab:
- Manager mode: List with multi-select, move, duplicate, delete
- Builder mode: Edit shader params, create from shader definitions
- JSON mode: Read-only JSON view
"""

import dearpygui.dearpygui as dpg
from typing import Any

from modules.ui_components import (
    apply_selection_theme, hex_to_rgb, rgba_to_hex,
    show_confirm_dialog
)


# =============================================================================
# Module State
# =============================================================================

_app = None
_EditorMode = None
_update_status_bar = None


def init_shader_tab(app_state, editor_mode_enum, status_callback):
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


# =============================================================================
# UI Setup
# =============================================================================

def setup_shader_tab(parent):
    """Build the Shaders tab UI structure."""
    with dpg.tab(label="SHADERS", parent=parent):
        with dpg.group(horizontal=True):
            dpg.add_text("Mode:")
            dpg.add_radio_button(
                items=["Builder", "Manager", "JSON"],
                default_value="Manager",
                horizontal=True,
                callback=lambda s, a: switch_shader_mode(_EditorMode[a.upper()])
            )
            dpg.add_spacer(width=30)
            dpg.add_button(label="+ New Shader", callback=add_new_shader)

        dpg.add_separator()

        # Builder panel
        with dpg.group(tag="shader_builder_panel", show=False):
            # Top: Create new preset from shader
            with dpg.group(horizontal=True):
                dpg.add_text("Create from shader:")
                dpg.add_combo(
                    tag="shader_builder_source_combo",
                    items=[],
                    width=300,
                    callback=shader_builder_source_changed
                )
                dpg.add_button(
                    label="Create New Preset",
                    callback=shader_builder_create_new
                )
            dpg.add_separator()

            # Main content: preset list + editor
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text("Preset List")
                    dpg.add_separator()
                    with dpg.child_window(tag="shader_builder_list", width=250, height=450):
                        pass
                dpg.add_spacer(width=10)
                with dpg.child_window(width=-1, height=450, tag="shader_builder_content"):
                    dpg.add_text("Select a preset to edit")

        # Manager panel
        with dpg.group(tag="shader_manager_panel", show=True):
            with dpg.child_window(height=-30, tag="shader_manager_list"):
                pass

        # JSON panel
        with dpg.group(tag="shader_json_panel", show=False):
            dpg.add_input_text(
                tag="shader_json_text",
                multiline=True,
                width=-1,
                height=-30,
                readonly=True
            )


# =============================================================================
# Mode Switching
# =============================================================================

def switch_shader_mode(mode):
    """Switch between Builder, Manager, and JSON modes."""
    _app.shader_mode = mode

    if dpg.does_item_exist("shader_builder_panel"):
        dpg.configure_item("shader_builder_panel", show=(mode == _EditorMode.BUILDER))
    if dpg.does_item_exist("shader_manager_panel"):
        dpg.configure_item("shader_manager_panel", show=(mode == _EditorMode.MANAGER))
    if dpg.does_item_exist("shader_json_panel"):
        dpg.configure_item("shader_json_panel", show=(mode == _EditorMode.JSON))

    refresh_shader_ui()


# =============================================================================
# Refresh Functions
# =============================================================================

def refresh_shader_ui():
    """Refresh shader tab content based on current mode."""
    if _app.shader_mode == _EditorMode.MANAGER:
        refresh_shader_manager()
    elif _app.shader_mode == _EditorMode.BUILDER:
        refresh_shader_builder()
    elif _app.shader_mode == _EditorMode.JSON:
        refresh_shader_json()


def refresh_shader_manager():
    """Refresh the shader manager list."""
    if not dpg.does_item_exist("shader_manager_list"):
        return

    dpg.delete_item("shader_manager_list", children_only=True)

    names = _app.json_mgr.get_shader_names()
    selected = _app.shader_selection.selected

    # Top toolbar
    with dpg.group(horizontal=True, parent="shader_manager_list"):
        dpg.add_text(f"Selected: {len(selected)} of {len(names)}")
        dpg.add_spacer(width=10)
        dpg.add_button(label="All", callback=shader_select_all, width=40)
        dpg.add_button(label="None", callback=shader_select_none, width=45)
        dpg.add_button(label="Invert", callback=shader_invert_selection, width=50)
        dpg.add_spacer(width=20)
        dpg.add_button(label="^^", width=25, callback=shader_move_selected_top)
        dpg.add_button(label="^", width=25, callback=shader_move_selected_up)
        dpg.add_button(label="v", width=25, callback=shader_move_selected_down)
        dpg.add_button(label="vv", width=25, callback=shader_move_selected_bottom)
        dpg.add_spacer(width=10)
        dpg.add_button(label="Dupe", width=45, callback=shader_duplicate_selected)
        dpg.add_button(label="Del", width=40, callback=shader_delete_selected)

    dpg.add_separator(parent="shader_manager_list")

    # Selectable list
    for name in names:
        is_selected = name in selected
        prefix = "[*] " if is_selected else "    "
        item_id = dpg.add_selectable(
            label=f"{prefix}shader_{name}",
            default_value=is_selected,
            callback=shader_manager_select_callback,
            user_data=name,
            width=800,
            parent="shader_manager_list"
        )
        apply_selection_theme(item_id, is_selected)


def refresh_shader_builder():
    """Refresh the shader builder panel."""
    # Update the available shaders combo
    if dpg.does_item_exist("shader_builder_source_combo"):
        available = _app.shader_parser.list_available_shaders()
        dpg.configure_item("shader_builder_source_combo", items=available)
        if available and not dpg.get_value("shader_builder_source_combo"):
            dpg.set_value("shader_builder_source_combo", available[0])

    refresh_shader_builder_list()
    refresh_shader_builder_content()


def refresh_shader_builder_list():
    """Refresh the shader builder list panel."""
    if not dpg.does_item_exist("shader_builder_list"):
        return

    dpg.delete_item("shader_builder_list", children_only=True)

    presets = _app.json_mgr.get_shader_names()
    for name in presets:
        is_selected = name in _app.shader_selection.selected
        prefix = "[*] " if is_selected else "    "
        item_id = dpg.add_selectable(
            label=f"{prefix}{name}",
            default_value=is_selected,
            callback=shader_builder_select_callback,
            user_data=name,
            width=230,
            parent="shader_builder_list"
        )
        apply_selection_theme(item_id, is_selected)


def refresh_shader_builder_content():
    """Refresh the shader builder content/editor panel."""
    if not dpg.does_item_exist("shader_builder_content"):
        return

    dpg.delete_item("shader_builder_content", children_only=True)

    selected = _app.shader_selection.selected
    if len(selected) != 1:
        dpg.add_text("Select a single preset to edit",
                    parent="shader_builder_content")
        return

    name = selected[0]
    preset = _app.json_mgr.get_shader(name)
    if not preset:
        dpg.add_text(f"Preset '{name}' not found",
                    parent="shader_builder_content")
        return

    parent = "shader_builder_content"

    # Editable preset name
    with dpg.group(horizontal=True, parent=parent):
        dpg.add_text("Preset Name:")
        name_input = dpg.add_input_text(
            default_value=name,
            callback=shader_rename_callback,
            user_data=name,
            on_enter=True,
            width=150
        )
        dpg.add_button(
            label="Update Name",
            callback=shader_update_name_button_callback,
            user_data=(name, name_input)
        )
    dpg.add_separator(parent=parent)

    # Shader name (read-only)
    shader_name = preset.get("shader", "")
    dpg.add_input_text(
        label="Shader",
        default_value=shader_name,
        readonly=True,
        parent=parent
    )

    # Shader description from parsed shader file
    shader_def = _app.shader_parser.get_shader(shader_name)
    if shader_def:
        desc = shader_def.file_description
        if desc:
            dpg.add_text(desc, parent=parent, wrap=400, color=(200, 200, 200))
        if shader_def.is_animated:
            dpg.add_text("(Animated shader - uses u_time)", parent=parent, color=(150, 200, 255))

    # Parameters
    dpg.add_separator(parent=parent)
    dpg.add_text("Parameters", parent=parent)

    preset_params = preset.get("params", {})

    # Get param definitions from shader
    shader_param_defs = {}
    if shader_def:
        for p in shader_def.params:
            shader_param_defs[p.name] = p

    # Merge preset values with shader defaults
    all_param_keys = set(preset_params.keys()) | set(shader_param_defs.keys())

    for key in sorted(all_param_keys):
        if not key or key == "null":
            continue

        # Get value
        if key in preset_params:
            value = preset_params[key]
        elif key in shader_param_defs:
            value = shader_param_defs[key].default
            if value is None:
                ptype = shader_param_defs[key].param_type
                if ptype == "color":
                    value = "#FFFFFF"
                elif ptype == "float":
                    value = 0.0
                elif ptype == "int":
                    value = 0
                else:
                    value = 0.0
        else:
            continue

        # Determine type
        param_type = None
        if key in shader_param_defs:
            param_type = shader_param_defs[key].param_type

        if param_type == "color" or (isinstance(value, str) and value.startswith("#")):
            rgb = hex_to_rgb(value) if isinstance(value, str) else (255, 255, 255)
            dpg.add_color_edit(
                label=key,
                default_value=[rgb[0], rgb[1], rgb[2], 255],
                callback=shader_param_color_callback,
                user_data=(name, key),
                no_alpha=True,
                parent=parent,
                width=150
            )
        elif isinstance(value, float) or param_type == "float":
            dpg.add_input_float(
                label=key,
                default_value=float(value) if value is not None else 0.0,
                callback=shader_param_callback,
                user_data=(name, key),
                step=0.1,
                parent=parent,
                width=150
            )
        elif isinstance(value, int) or param_type == "int":
            dpg.add_input_int(
                label=key,
                default_value=int(value) if value is not None else 0,
                callback=shader_param_callback,
                user_data=(name, key),
                parent=parent,
                width=150
            )


def refresh_shader_json():
    """Refresh the shader JSON view."""
    import json
    if dpg.does_item_exist("shader_json_text"):
        text = json.dumps(_app.json_mgr.shader_data, indent=2)
        dpg.set_value("shader_json_text", text)


# =============================================================================
# Selection Callbacks
# =============================================================================

def shader_manager_select_callback(sender, app_data, user_data):
    shader_manager_select(user_data)


def shader_manager_select(name: str):
    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)
    shift = dpg.is_key_down(dpg.mvKey_LShift) or dpg.is_key_down(dpg.mvKey_RShift)
    _app.shader_selection.handle_click(name, ctrl, shift)
    refresh_shader_manager()


def shader_builder_select_callback(sender, app_data, user_data):
    shader_builder_select(user_data)


def shader_builder_select(name: str):
    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)
    if ctrl:
        if name in _app.shader_selection.selected:
            _app.shader_selection.selected.remove(name)
        else:
            _app.shader_selection.selected.append(name)
    else:
        _app.shader_selection.selected = [name]
    refresh_shader_builder_list()
    refresh_shader_builder_content()


# =============================================================================
# Selection Actions
# =============================================================================

def shader_select_all():
    _app.shader_selection.select_all()
    refresh_shader_manager()


def shader_select_none():
    _app.shader_selection.select_none()
    refresh_shader_manager()


def shader_invert_selection():
    _app.shader_selection.invert_selection()
    refresh_shader_manager()


# =============================================================================
# Move Actions
# =============================================================================

def shader_move_selected_top():
    for name in reversed(_app.shader_selection.selected):
        _app.json_mgr.move_shader(name, "top")
    refresh_shader_manager()


def shader_move_selected_up():
    for name in _app.shader_selection.selected:
        _app.json_mgr.move_shader(name, "up")
    refresh_shader_manager()


def shader_move_selected_down():
    for name in reversed(_app.shader_selection.selected):
        _app.json_mgr.move_shader(name, "down")
    refresh_shader_manager()


def shader_move_selected_bottom():
    for name in _app.shader_selection.selected:
        _app.json_mgr.move_shader(name, "bottom")
    refresh_shader_manager()


# =============================================================================
# Duplicate/Delete Actions
# =============================================================================

def shader_duplicate_selected():
    selected = _app.shader_selection.selected.copy()
    for name in selected:
        new_name = _app.json_mgr.get_unique_shader_name(f"{name}_copy")
        _app.json_mgr.duplicate_shader(name, new_name)
    _app.shader_selection.update_items(_app.json_mgr.get_shader_names())
    refresh_shader_manager()
    if _update_status_bar:
        _update_status_bar()


def shader_delete_selected():
    selected = _app.shader_selection.selected.copy()
    if not selected:
        return

    def do_delete():
        _app.json_mgr.delete_shaders(selected)
        _app.shader_selection.selected = []
        _app.shader_selection.update_items(_app.json_mgr.get_shader_names())
        refresh_shader_manager()
        if _update_status_bar:
            _update_status_bar()

    show_confirm_dialog(
        "Delete Selected",
        f"Delete {len(selected)} shader(s)?",
        do_delete
    )


# =============================================================================
# Create New
# =============================================================================

def shader_builder_source_changed(sender, app_data, user_data):
    """Called when user selects a different source shader."""
    pass  # Just tracks selection, used by create_new


def shader_builder_create_new():
    """Create a new shader preset based on selected source shader."""
    source = dpg.get_value("shader_builder_source_combo") if dpg.does_item_exist("shader_builder_source_combo") else None

    if not source:
        return

    shader_def = _app.shader_parser.get_shader(source)

    # Build default params
    params = {}
    if shader_def:
        for param in shader_def.params:
            if param.default is not None:
                params[param.name] = param.default
            elif param.param_type == "color":
                params[param.name] = "#FFFFFF"
            elif param.param_type == "float":
                params[param.name] = param.min_value if param.min_value is not None else 0.0
            elif param.param_type == "int":
                params[param.name] = int(param.min_value) if param.min_value is not None else 0

    base_name = source.replace("shader.", "").replace(".", "_")
    new_name = _app.json_mgr.get_unique_shader_name(base_name)

    preset_data = {
        "shader": source,
        "animated": shader_def.is_animated if shader_def else False,
        "params": params
    }

    _app.json_mgr.add_shader(new_name, preset_data)
    _app.shader_selection.update_items(_app.json_mgr.get_shader_names())
    _app.shader_selection.selected = [new_name]
    refresh_shader_builder()
    if _update_status_bar:
        _update_status_bar()


def add_new_shader():
    """Add a new shader preset with defaults."""
    name = _app.json_mgr.get_unique_shader_name("new_shader")
    _app.json_mgr.add_shader(name, {
        "shader": "shader.color_tint",
        "params": {
            "u_tint_color": "#FFFFFF",
            "u_amount": 0.5
        }
    })
    _app.shader_selection.update_items(_app.json_mgr.get_shader_names())
    _app.shader_selection.selected = [name]
    refresh_shader_ui()
    if _update_status_bar:
        _update_status_bar()


# =============================================================================
# Field Callbacks
# =============================================================================

def shader_param_callback(sender, app_data, user_data):
    if user_data:
        name, param = user_data
        shader_update_param(name, param, _clean_float(app_data))


def shader_param_color_callback(sender, app_data, user_data):
    if user_data:
        name, param = user_data
        hex_color = rgba_to_hex(app_data)
        shader_update_param(name, param, hex_color)


def shader_rename_callback(sender, app_data, user_data):
    if user_data:
        shader_rename_preset(user_data, app_data)


def shader_update_name_button_callback(sender, app_data, user_data):
    old_name, input_tag = user_data
    new_name = dpg.get_value(input_tag)
    shader_rename_preset(old_name, new_name)


# =============================================================================
# Data Operations
# =============================================================================

def shader_update_param(name: str, param: str, value):
    """Update a shader parameter value."""
    if not param or param == "null":
        return

    preset = _app.json_mgr.get_shader(name) or {}
    if "params" not in preset:
        preset["params"] = {}
    preset["params"][param] = value
    _app.json_mgr.set_shader(name, preset)
    if _update_status_bar:
        _update_status_bar()


def shader_rename_preset(old_name: str, new_name: str):
    """Rename a shader preset."""
    new_name = new_name.strip()
    if not new_name or new_name == old_name:
        return
    if _app.json_mgr.get_shader(new_name):
        return
    preset = _app.json_mgr.get_shader(old_name)
    if preset:
        _app.json_mgr.set_shader(new_name, preset)
        _app.json_mgr.delete_shader(old_name)
        _app.shader_selection.update_items(_app.json_mgr.get_shader_names())
        _app.shader_selection.selected = [new_name]
        refresh_shader_ui()
        if _update_status_bar:
            _update_status_bar()
