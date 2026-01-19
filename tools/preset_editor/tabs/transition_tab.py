"""
transition_tab.py - Transition presets tab UI

Handles all UI and callbacks for the Transitions tab:
- Manager mode: List with multi-select, move, duplicate, delete
- Builder mode: Edit individual preset fields
- JSON mode: Read-only JSON view
"""

import dearpygui.dearpygui as dpg
from typing import Any

from modules.ui_components import apply_selection_theme


# =============================================================================
# Module State (set by init_transition_tab)
# =============================================================================

_app = None  # Reference to AppState
_EditorMode = None  # Reference to EditorMode enum
_update_status_bar = None  # Callback to update status bar


def init_transition_tab(app_state, editor_mode_enum, status_callback):
    """Initialize module with app state reference."""
    global _app, _EditorMode, _update_status_bar
    _app = app_state
    _EditorMode = editor_mode_enum
    _update_status_bar = status_callback


# =============================================================================
# Helper
# =============================================================================

def _clean_float(value: Any) -> Any:
    """Round floats to 2 decimal places to avoid floating point noise."""
    if isinstance(value, float):
        return round(value, 2)
    return value


# =============================================================================
# UI Setup
# =============================================================================

def setup_transition_tab(parent):
    """Build the Transitions tab UI structure."""
    with dpg.tab(label="TRANSITIONS", parent=parent):
        # Mode selector and actions
        with dpg.group(horizontal=True):
            dpg.add_text("Mode:")
            dpg.add_radio_button(
                items=["Builder", "Manager", "JSON"],
                default_value="Manager",
                horizontal=True,
                callback=lambda s, a: switch_transition_mode(_EditorMode[a.upper()])
            )
            dpg.add_spacer(width=30)
            dpg.add_button(label="+ New Preset", callback=add_new_transition)

        dpg.add_separator()

        # Builder panel
        with dpg.group(horizontal=True, tag="trans_builder_panel", show=False):
            with dpg.group():
                dpg.add_text("Preset List")
                dpg.add_separator()
                with dpg.child_window(tag="trans_builder_list", width=250, height=500):
                    pass
            dpg.add_spacer(width=10)
            with dpg.child_window(width=-1, height=500, tag="trans_builder_content"):
                dpg.add_text("Select a preset to edit")

        # Manager panel
        with dpg.group(tag="trans_manager_panel", show=True):
            with dpg.child_window(height=-30, tag="trans_manager_list"):
                pass

        # JSON panel
        with dpg.group(tag="trans_json_panel", show=False):
            dpg.add_input_text(
                tag="trans_json_text",
                multiline=True,
                width=-1,
                height=-30,
                readonly=True
            )


# =============================================================================
# Mode Switching
# =============================================================================

def switch_transition_mode(mode):
    """Switch between Builder, Manager, and JSON modes."""
    _app.transition_mode = mode

    # Show/hide panels
    if dpg.does_item_exist("trans_builder_panel"):
        dpg.configure_item("trans_builder_panel", show=(mode == _EditorMode.BUILDER))
    if dpg.does_item_exist("trans_manager_panel"):
        dpg.configure_item("trans_manager_panel", show=(mode == _EditorMode.MANAGER))
    if dpg.does_item_exist("trans_json_panel"):
        dpg.configure_item("trans_json_panel", show=(mode == _EditorMode.JSON))

    refresh_transition_ui()


# =============================================================================
# Refresh Functions
# =============================================================================

def refresh_transition_ui():
    """Refresh transition tab content based on current mode."""
    if _app.transition_mode == _EditorMode.MANAGER:
        refresh_transition_manager()
    elif _app.transition_mode == _EditorMode.BUILDER:
        refresh_transition_builder()
    elif _app.transition_mode == _EditorMode.JSON:
        refresh_transition_json()


def refresh_transition_manager():
    """Refresh the transition manager list."""
    if not dpg.does_item_exist("trans_manager_list"):
        return

    dpg.delete_item("trans_manager_list", children_only=True)

    names = _app.json_mgr.get_transition_names()
    selected = _app.trans_selection.selected

    # Top toolbar: selection + actions
    with dpg.group(horizontal=True, parent="trans_manager_list"):
        dpg.add_text(f"Selected: {len(selected)} of {len(names)}")
        dpg.add_spacer(width=10)
        dpg.add_button(label="All", callback=trans_select_all, width=40)
        dpg.add_button(label="None", callback=trans_select_none, width=45)
        dpg.add_button(label="Invert", callback=trans_invert_selection, width=50)
        dpg.add_spacer(width=20)
        dpg.add_button(label="^^", width=25, callback=trans_move_selected_top)
        dpg.add_button(label="^", width=25, callback=trans_move_selected_up)
        dpg.add_button(label="v", width=25, callback=trans_move_selected_down)
        dpg.add_button(label="vv", width=25, callback=trans_move_selected_bottom)
        dpg.add_spacer(width=10)
        dpg.add_button(label="Dupe", width=45, callback=trans_duplicate_selected)
        dpg.add_button(label="Del", width=40, callback=trans_delete_selected)

    dpg.add_separator(parent="trans_manager_list")

    # Selectable list
    for name in names:
        is_selected = name in selected
        prefix = "[*] " if is_selected else "    "
        item_id = dpg.add_selectable(
            label=f"{prefix}preset_{name}",
            default_value=is_selected,
            callback=trans_manager_select_callback,
            user_data=name,
            width=800,
            parent="trans_manager_list"
        )
        apply_selection_theme(item_id, is_selected)


def refresh_transition_builder():
    """Refresh the transition builder panel (list + content)."""
    refresh_transition_builder_list()
    refresh_transition_builder_content()


def refresh_transition_builder_list():
    """Refresh the transition builder list panel."""
    if not dpg.does_item_exist("trans_builder_list"):
        return

    dpg.delete_item("trans_builder_list", children_only=True)

    presets = _app.json_mgr.get_transition_names()
    for name in presets:
        is_selected = name in _app.trans_selection.selected
        prefix = "[*] " if is_selected else "    "
        item_id = dpg.add_selectable(
            label=f"{prefix}{name}",
            default_value=is_selected,
            callback=trans_builder_select_callback,
            user_data=name,
            width=230,
            parent="trans_builder_list"
        )
        apply_selection_theme(item_id, is_selected)


def refresh_transition_builder_content():
    """Refresh the transition builder content/editor panel."""
    if not dpg.does_item_exist("trans_builder_content"):
        return

    dpg.delete_item("trans_builder_content", children_only=True)

    selected = _app.trans_selection.selected
    if len(selected) != 1:
        dpg.add_text("Select a single preset to edit",
                    parent="trans_builder_content")
        return

    name = selected[0]
    preset = _app.json_mgr.get_transition(name)
    if not preset:
        dpg.add_text(f"Preset '{name}' not found",
                    parent="trans_builder_content")
        return

    parent = "trans_builder_content"

    # Editable preset name with Update button
    with dpg.group(horizontal=True, parent=parent):
        dpg.add_text("Preset Name:")
        name_input = dpg.add_input_text(
            default_value=name,
            callback=trans_rename_callback,
            user_data=name,
            on_enter=True,
            width=150
        )
        dpg.add_button(
            label="Update Name",
            callback=trans_update_name_button_callback,
            user_data=(name, name_input)
        )
    dpg.add_separator(parent=parent)

    # Duration
    dpg.add_input_float(
        label="Duration",
        default_value=preset.get("duration", 0.4),
        callback=trans_field_callback,
        user_data=(name, "duration"),
        min_value=0.0, max_value=5.0, step=0.1,
        width=150,
        parent=parent
    )

    # Easing
    easing_options = ["linear", "easein", "easeout", "ease"]
    dpg.add_combo(
        label="Easing",
        items=easing_options,
        default_value=preset.get("easing", "easeout"),
        callback=trans_field_callback,
        user_data=(name, "easing"),
        width=150,
        parent=parent
    )

    # Start Position
    dpg.add_separator(parent=parent)
    start_pos = preset.get("start_position", {})
    start_is_align = "xalign" in start_pos or "yalign" in start_pos

    with dpg.group(horizontal=True, parent=parent):
        dpg.add_text("Start Position")
        dpg.add_spacer(width=10)
        dpg.add_text("Offset", color=(150, 255, 150) if not start_is_align else (150, 150, 150))
        dpg.add_checkbox(
            label="",
            default_value=start_is_align,
            callback=trans_toggle_start_callback,
            user_data=name,
        )
        dpg.add_text("Align", color=(150, 255, 150) if start_is_align else (150, 150, 150))

    x_key = "xalign" if start_is_align else "xoffset"
    x_value = start_pos.get("xalign", start_pos.get("xoffset", 0.0))
    dpg.add_input_float(
        label=x_key,
        default_value=x_value,
        callback=trans_update_start_x_callback,
        user_data=name,
        step=0.1 if start_is_align else 10.0,
        width=150,
        parent=parent
    )

    y_key = "yalign" if start_is_align else "yoffset"
    y_value = start_pos.get("yalign", start_pos.get("yoffset", 0.0))
    dpg.add_input_float(
        label=y_key,
        default_value=y_value,
        callback=trans_update_start_y_callback,
        user_data=name,
        step=0.1 if start_is_align else 10.0,
        width=150,
        parent=parent
    )

    # End Position
    dpg.add_separator(parent=parent)
    end_pos = preset.get("end_position", {})
    end_is_align = "xalign" in end_pos or "yalign" in end_pos

    with dpg.group(horizontal=True, parent=parent):
        dpg.add_text("End Position")
        dpg.add_spacer(width=10)
        dpg.add_text("Offset", color=(150, 255, 150) if not end_is_align else (150, 150, 150))
        dpg.add_checkbox(
            label="",
            default_value=end_is_align,
            callback=trans_toggle_end_callback,
            user_data=name,
        )
        dpg.add_text("Align", color=(150, 255, 150) if end_is_align else (150, 150, 150))

    x_key = "xalign" if end_is_align else "xoffset"
    x_value = end_pos.get("xalign", end_pos.get("xoffset", 0.0))
    dpg.add_input_float(
        label=x_key,
        default_value=x_value,
        callback=trans_update_end_x_callback,
        user_data=name,
        step=0.1 if end_is_align else 10.0,
        width=150,
        parent=parent
    )

    y_key = "yalign" if end_is_align else "yoffset"
    y_value = end_pos.get("yalign", end_pos.get("yoffset", 0.0))
    dpg.add_input_float(
        label=y_key,
        default_value=y_value,
        callback=trans_update_end_y_callback,
        user_data=name,
        step=0.1 if end_is_align else 10.0,
        width=150,
        parent=parent
    )

    # Alpha
    dpg.add_separator(parent=parent)
    dpg.add_text("Alpha", parent=parent)
    alpha = preset.get("alpha", {"start": 1.0, "end": 1.0})
    dpg.add_input_float(
        label="Alpha Start",
        default_value=alpha.get("start", 1.0),
        callback=trans_nested_callback,
        user_data=(name, "alpha", "start"),
        min_value=0.0, max_value=1.0, step=0.1,
        width=150,
        parent=parent
    )
    dpg.add_input_float(
        label="Alpha End",
        default_value=alpha.get("end", 1.0),
        callback=trans_nested_callback,
        user_data=(name, "alpha", "end"),
        min_value=0.0, max_value=1.0, step=0.1,
        width=150,
        parent=parent
    )

    # Scale
    dpg.add_separator(parent=parent)
    dpg.add_text("Scale", parent=parent)
    scale = preset.get("scale", {"start": 1.0, "end": 1.0})
    dpg.add_input_float(
        label="Scale Start",
        default_value=scale.get("start", 1.0),
        callback=trans_nested_callback,
        user_data=(name, "scale", "start"),
        min_value=0.0, max_value=3.0, step=0.1,
        width=150,
        parent=parent
    )
    dpg.add_input_float(
        label="Scale End",
        default_value=scale.get("end", 1.0),
        callback=trans_nested_callback,
        user_data=(name, "scale", "end"),
        min_value=0.0, max_value=3.0, step=0.1,
        width=150,
        parent=parent
    )

    # Rotation
    dpg.add_separator(parent=parent)
    dpg.add_text("Rotation", parent=parent)
    rotation = preset.get("rotation", {"start": 0, "end": 0})
    dpg.add_input_int(
        label="Rotation Start",
        default_value=int(rotation.get("start", 0)),
        callback=trans_nested_callback,
        user_data=(name, "rotation", "start"),
        min_value=-360, max_value=360, step=15,
        width=150,
        parent=parent
    )
    dpg.add_input_int(
        label="Rotation End",
        default_value=int(rotation.get("end", 0)),
        callback=trans_nested_callback,
        user_data=(name, "rotation", "end"),
        min_value=-360, max_value=360, step=15,
        width=150,
        parent=parent
    )


def refresh_transition_json():
    """Refresh the transition JSON view."""
    import json
    if dpg.does_item_exist("trans_json_text"):
        text = json.dumps(_app.json_mgr.transition_data, indent=2)
        dpg.set_value("trans_json_text", text)


# =============================================================================
# Selection Callbacks
# =============================================================================

def trans_manager_select_callback(sender, app_data, user_data):
    """Callback for manager mode selection."""
    trans_manager_select(user_data)


def trans_manager_select(name: str):
    """Handle selection in manager mode."""
    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)
    shift = dpg.is_key_down(dpg.mvKey_LShift) or dpg.is_key_down(dpg.mvKey_RShift)
    _app.trans_selection.handle_click(name, ctrl, shift)
    refresh_transition_manager()


def trans_builder_select_callback(sender, app_data, user_data):
    """Callback for builder mode selection."""
    trans_builder_select(user_data)


def trans_builder_select(name: str):
    """Select a preset in builder mode."""
    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)
    if ctrl:
        if name in _app.trans_selection.selected:
            _app.trans_selection.selected.remove(name)
        else:
            _app.trans_selection.selected.append(name)
    else:
        _app.trans_selection.selected = [name]
    refresh_transition_builder_list()
    refresh_transition_builder_content()


# =============================================================================
# Selection Actions
# =============================================================================

def trans_select_all():
    _app.trans_selection.select_all()
    refresh_transition_manager()


def trans_select_none():
    _app.trans_selection.select_none()
    refresh_transition_manager()


def trans_invert_selection():
    _app.trans_selection.invert_selection()
    refresh_transition_manager()


# =============================================================================
# Move Actions
# =============================================================================

def trans_move_selected_top():
    for name in reversed(_app.trans_selection.selected):
        _app.json_mgr.move_transition(name, "top")
    refresh_transition_manager()


def trans_move_selected_up():
    for name in _app.trans_selection.selected:
        _app.json_mgr.move_transition(name, "up")
    refresh_transition_manager()


def trans_move_selected_down():
    for name in reversed(_app.trans_selection.selected):
        _app.json_mgr.move_transition(name, "down")
    refresh_transition_manager()


def trans_move_selected_bottom():
    for name in _app.trans_selection.selected:
        _app.json_mgr.move_transition(name, "bottom")
    refresh_transition_manager()


# =============================================================================
# Duplicate/Delete Actions
# =============================================================================

def trans_duplicate_selected():
    from modules.ui_components import show_confirm_dialog
    selected = _app.trans_selection.selected.copy()
    for name in selected:
        new_name = _app.json_mgr.get_unique_transition_name(f"{name}_copy")
        _app.json_mgr.duplicate_transition(name, new_name)
    _app.trans_selection.update_items(_app.json_mgr.get_transition_names())
    refresh_transition_manager()
    if _update_status_bar:
        _update_status_bar()


def trans_delete_selected():
    from modules.ui_components import show_confirm_dialog
    selected = _app.trans_selection.selected.copy()
    if not selected:
        return

    def do_delete():
        _app.json_mgr.delete_transitions(selected)
        _app.trans_selection.selected = []
        _app.trans_selection.update_items(_app.json_mgr.get_transition_names())
        refresh_transition_manager()
        if _update_status_bar:
            _update_status_bar()

    show_confirm_dialog(
        "Delete Selected",
        f"Delete {len(selected)} transition(s)?",
        do_delete
    )


# =============================================================================
# Add New Preset
# =============================================================================

def add_new_transition():
    """Add a new transition preset with defaults."""
    name = _app.json_mgr.get_unique_transition_name("new_preset")
    _app.json_mgr.add_transition(name, {
        "start_position": {"xoffset": 0},
        "end_position": {"xoffset": 0},
        "alpha": {"start": 1.0, "end": 1.0},
        "duration": 0.4,
        "easing": "easeout"
    })
    _app.trans_selection.update_items(_app.json_mgr.get_transition_names())
    _app.trans_selection.selected = [name]
    refresh_transition_ui()
    if _update_status_bar:
        _update_status_bar()


# =============================================================================
# Field Callbacks
# =============================================================================

def trans_field_callback(sender, app_data, user_data):
    """Callback for simple field inputs."""
    if user_data:
        name, field = user_data
        trans_update_field(name, field, _clean_float(app_data))


def trans_nested_callback(sender, app_data, user_data):
    """Callback for nested field inputs (alpha, scale, rotation)."""
    if user_data:
        name, category, key = user_data
        trans_update_nested(name, category, key, _clean_float(app_data))


def trans_rename_callback(sender, app_data, user_data):
    """Callback for rename input on enter."""
    if user_data:
        trans_rename_preset(user_data, app_data)


def trans_update_name_button_callback(sender, app_data, user_data):
    """Callback for Update Name button."""
    old_name, input_tag = user_data
    new_name = dpg.get_value(input_tag)
    trans_rename_preset(old_name, new_name)


def trans_toggle_start_callback(sender, app_data, user_data):
    """Callback for start position toggle."""
    trans_toggle_section_mode(user_data, "start_position", app_data)


def trans_toggle_end_callback(sender, app_data, user_data):
    """Callback for end position toggle."""
    trans_toggle_section_mode(user_data, "end_position", app_data)


def trans_update_start_x_callback(sender, app_data, user_data):
    trans_update_position_smart(user_data, "start_position", "x", app_data)


def trans_update_start_y_callback(sender, app_data, user_data):
    trans_update_position_smart(user_data, "start_position", "y", app_data)


def trans_update_end_x_callback(sender, app_data, user_data):
    trans_update_position_smart(user_data, "end_position", "x", app_data)


def trans_update_end_y_callback(sender, app_data, user_data):
    trans_update_position_smart(user_data, "end_position", "y", app_data)


# =============================================================================
# Data Operations
# =============================================================================

def trans_update_field(name: str, field: str, value):
    """Update a simple field on a transition preset."""
    preset = _app.json_mgr.get_transition(name) or {}
    preset[field] = value
    _app.json_mgr.set_transition(name, preset)
    if _update_status_bar:
        _update_status_bar()


def trans_update_nested(name: str, category: str, key: str, value):
    """Update a nested field (alpha.start, scale.end, etc.)."""
    preset = _app.json_mgr.get_transition(name) or {}
    if category not in preset:
        preset[category] = {}
    preset[category][key] = value
    _app.json_mgr.set_transition(name, preset)
    if _update_status_bar:
        _update_status_bar()


def trans_toggle_section_mode(name: str, pos_type: str, use_align: bool):
    """Toggle between align (0-1) and offset (pixels) mode for a position section."""
    preset = _app.json_mgr.get_transition(name)
    if preset is None:
        preset = {}

    if pos_type not in preset:
        preset[pos_type] = {}

    pos = preset[pos_type]

    # Handle X axis
    x_value = pos.get("xalign", pos.get("xoffset", 0.0))
    pos.pop("xoffset", None)
    pos.pop("xalign", None)
    if use_align:
        if x_value > 1.0 or x_value < 0.0:
            x_value = 0.5
        pos["xalign"] = x_value
    else:
        if 0.0 < x_value <= 1.0:
            x_value = 0.0
        pos["xoffset"] = x_value

    # Handle Y axis
    y_value = pos.get("yalign", pos.get("yoffset", 0.0))
    pos.pop("yoffset", None)
    pos.pop("yalign", None)
    if use_align:
        if y_value > 1.0 or y_value < 0.0:
            y_value = 1.0
        pos["yalign"] = y_value
    else:
        if 0.0 < y_value <= 1.0:
            y_value = 0.0
        pos["yoffset"] = y_value

    _app.json_mgr.set_transition(name, preset)
    if _update_status_bar:
        _update_status_bar()
    refresh_transition_builder()


def trans_update_position_smart(name: str, pos_type: str, axis: str, value: float):
    """Update position value, using current mode (align or offset)."""
    preset = _app.json_mgr.get_transition(name) or {}
    if pos_type not in preset:
        preset[pos_type] = {}

    pos = preset[pos_type]
    offset_key = f"{axis}offset"
    align_key = f"{axis}align"

    if align_key in pos:
        pos[align_key] = _clean_float(value)
    else:
        pos[offset_key] = _clean_float(value)

    _app.json_mgr.set_transition(name, preset)
    if _update_status_bar:
        _update_status_bar()


def trans_rename_preset(old_name: str, new_name: str):
    """Rename a transition preset."""
    new_name = new_name.strip()
    if not new_name or new_name == old_name:
        return
    if _app.json_mgr.get_transition(new_name):
        return
    preset = _app.json_mgr.get_transition(old_name)
    if preset:
        _app.json_mgr.set_transition(new_name, preset)
        _app.json_mgr.delete_transition(old_name)
        _app.trans_selection.update_items(_app.json_mgr.get_transition_names())
        _app.trans_selection.selected = [new_name]
        refresh_transition_ui()
        if _update_status_bar:
            _update_status_bar()
