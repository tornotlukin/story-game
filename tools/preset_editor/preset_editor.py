#!/usr/bin/env python3
"""
Preset Editor - Dear PyGui tool for managing Ren'Py preset JSON files

Features:
- Two tabs: Transitions and Shaders
- Three modes per tab: Builder, Manager, JSON
- Export Demo modal for testing presets
- Shader .rpy file parsing
- Live JSON updates with undo/redo
- Multi-select (Ctrl+click, Shift+click)

Usage:
    python preset_editor.py
"""

import dearpygui.dearpygui as dpg
import json
import os
import subprocess
import sys
from pathlib import Path
from enum import Enum
from typing import Optional, List, Dict, Any

# Import our modules
from modules.json_manager import JsonManager
from modules.shader_parser import ShaderParser
from modules.demo_generator import DemoGenerator, DemoItem
from modules.ui_components import (
    create_dark_theme, StatusBar, SelectionManager,
    hex_to_rgb, rgb_to_hex, rgba_to_hex,
    show_rename_dialog, show_confirm_dialog, show_color_picker_dialog,
    init_selection_themes, apply_selection_theme
)


# =============================================================================
# Constants
# =============================================================================

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
CONFIG_FILE = "config.json"


class EditorMode(Enum):
    BUILDER = "Builder"
    MANAGER = "Manager"
    JSON = "JSON"


# =============================================================================
# Application State
# =============================================================================

class AppState:
    """Global application state."""

    def __init__(self):
        # Paths from config
        self.transition_presets_path = ""
        self.shader_presets_path = ""
        self.shader_folder = ""
        self.game_folder = ""
        self.renpy_exe = ""

        # Demo settings
        self.demo_width = 1080
        self.demo_height = 1920

        # Managers
        self.json_mgr = JsonManager()
        self.shader_parser = ShaderParser()
        self.demo_gen = DemoGenerator()

        # UI state
        self.transition_mode = EditorMode.MANAGER
        self.shader_mode = EditorMode.MANAGER

        # Selection managers
        self.trans_selection = SelectionManager([])
        self.shader_selection = SelectionManager([])

        # Status bar reference
        self.status_bar: Optional[StatusBar] = None

    def load_config(self):
        """Load configuration from config.json."""
        config_path = Path(__file__).parent / CONFIG_FILE
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                self.transition_presets_path = self._resolve_path(
                    config.get("transition_presets", "")
                )
                self.shader_presets_path = self._resolve_path(
                    config.get("shader_presets", "")
                )
                self.shader_folder = self._resolve_path(
                    config.get("shader_folder", "")
                )
                self.game_folder = self._resolve_path(
                    config.get("game_folder", "")
                )
                self.renpy_exe = config.get("renpy_exe", "")

                # Demo dimensions
                self.demo_width = config.get("demo_width", 1080)
                self.demo_height = config.get("demo_height", 1920)

            except Exception as e:
                print(f"Error loading config: {e}")
                self._use_defaults()
        else:
            self._use_defaults()

    def _use_defaults(self):
        """Use default paths relative to this script."""
        base = Path(__file__).parent
        self.transition_presets_path = str(
            (base / "../../game/presets/transition_presets.json").resolve()
        )
        self.shader_presets_path = str(
            (base / "../../game/presets/shader_presets.json").resolve()
        )
        self.shader_folder = str(
            (base / "../../game/shader").resolve()
        )
        self.game_folder = str(
            (base / "../../game").resolve()
        )

    def _resolve_path(self, path: str) -> str:
        """Resolve a path relative to this script."""
        if not path:
            return ""
        p = Path(path)
        if not p.is_absolute():
            p = Path(__file__).parent / path
        return str(p.resolve())

    def save_config(self):
        """Save configuration to config.json."""
        config = {
            "transition_presets": self.transition_presets_path,
            "shader_presets": self.shader_presets_path,
            "shader_folder": self.shader_folder,
            "game_folder": self.game_folder,
            "renpy_exe": self.renpy_exe,
            "demo_width": self.demo_width,
            "demo_height": self.demo_height
        }
        config_path = Path(__file__).parent / CONFIG_FILE
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            print(f"Config saved to: {config_path}")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def load_data(self):
        """Load all data (JSON presets and shader definitions)."""
        self.json_mgr.set_paths(
            self.transition_presets_path,
            self.shader_presets_path
        )
        self.json_mgr.load()

        # Update selection managers
        self.trans_selection.update_items(self.json_mgr.get_transition_names())
        self.shader_selection.update_items(self.json_mgr.get_shader_names())

        # Parse shader .rpy files
        if self.shader_folder and Path(self.shader_folder).exists():
            self.shader_parser.parse_directory(self.shader_folder)


# Global state
app = AppState()


# =============================================================================
# UI Refresh Functions
# =============================================================================

def refresh_all():
    """Refresh all UI elements."""
    app.trans_selection.update_items(app.json_mgr.get_transition_names())
    app.shader_selection.update_items(app.json_mgr.get_shader_names())

    refresh_transition_ui()
    refresh_shader_ui()
    update_status_bar()


def update_status_bar():
    """Update the status bar."""
    if app.status_bar:
        app.status_bar.update(
            auto_save=True,
            undo_count=app.json_mgr.undo_count,
            redo_count=app.json_mgr.redo_count
        )


def refresh_transition_ui():
    """Refresh transition tab content based on current mode."""
    if app.transition_mode == EditorMode.MANAGER:
        refresh_transition_manager()
    elif app.transition_mode == EditorMode.BUILDER:
        refresh_transition_builder()
    elif app.transition_mode == EditorMode.JSON:
        refresh_transition_json()


def refresh_shader_ui():
    """Refresh shader tab content based on current mode."""
    if app.shader_mode == EditorMode.MANAGER:
        refresh_shader_manager()
    elif app.shader_mode == EditorMode.BUILDER:
        refresh_shader_builder()
    elif app.shader_mode == EditorMode.JSON:
        refresh_shader_json()


# =============================================================================
# Transition UI
# =============================================================================

def refresh_transition_manager():
    """Refresh the transition manager list."""
    if not dpg.does_item_exist("trans_manager_list"):
        return

    dpg.delete_item("trans_manager_list", children_only=True)

    names = app.json_mgr.get_transition_names()
    selected = app.trans_selection.selected

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

    # Selectable list with proper visual selection
    for name in names:
        is_selected = name in selected
        # Add visual prefix for selected items
        prefix = "[*] " if is_selected else "    "
        item_id = dpg.add_selectable(
            label=f"{prefix}preset_{name}",
            default_value=is_selected,
            callback=trans_manager_select_callback,
            user_data=name,
            width=800,
            parent="trans_manager_list"
        )
        # Apply selection theme for visual feedback
        apply_selection_theme(item_id, is_selected)


def trans_manager_select_callback(sender, app_data, user_data):
    """Callback for manager mode selection (receives user_data=name)."""
    trans_manager_select(user_data)


def trans_manager_select(name: str):
    """Handle selection in manager mode."""
    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)
    shift = dpg.is_key_down(dpg.mvKey_LShift) or dpg.is_key_down(dpg.mvKey_RShift)
    app.trans_selection.handle_click(name, ctrl, shift)
    refresh_transition_manager()


def trans_move_selected_top():
    """Move selected items to top."""
    for name in reversed(app.trans_selection.selected):
        app.json_mgr.move_transition(name, "top")
    refresh_transition_manager()


def trans_move_selected_up():
    """Move selected items up."""
    for name in app.trans_selection.selected:
        app.json_mgr.move_transition(name, "up")
    refresh_transition_manager()


def trans_move_selected_down():
    """Move selected items down."""
    for name in reversed(app.trans_selection.selected):
        app.json_mgr.move_transition(name, "down")
    refresh_transition_manager()


def trans_move_selected_bottom():
    """Move selected items to bottom."""
    for name in app.trans_selection.selected:
        app.json_mgr.move_transition(name, "bottom")
    refresh_transition_manager()


def refresh_transition_builder():
    """Refresh the transition builder panel (list + content)."""
    refresh_transition_builder_list()
    refresh_transition_builder_content()


def trans_builder_select_callback(sender, app_data, user_data):
    """Callback for builder mode selection."""
    trans_builder_select(user_data)


def refresh_transition_builder_list():
    """Refresh the transition builder list panel."""
    if not dpg.does_item_exist("trans_builder_list"):
        return

    dpg.delete_item("trans_builder_list", children_only=True)

    presets = app.json_mgr.get_transition_names()
    for name in presets:
        is_selected = name in app.trans_selection.selected
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


def trans_builder_select(name: str):
    """Select a preset in builder mode."""
    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)
    if ctrl:
        # Toggle selection
        if name in app.trans_selection.selected:
            app.trans_selection.selected.remove(name)
        else:
            app.trans_selection.selected.append(name)
    else:
        # Single selection
        app.trans_selection.selected = [name]
    refresh_transition_builder_list()
    refresh_transition_builder_content()


def trans_update_name_button_callback(sender, app_data, user_data):
    """Callback for Update Name button in transition builder."""
    old_name, input_tag = user_data
    new_name = dpg.get_value(input_tag)
    trans_rename_preset(old_name, new_name)


def refresh_transition_builder_content():
    """Refresh the transition builder content/editor panel."""
    if not dpg.does_item_exist("trans_builder_content"):
        return

    dpg.delete_item("trans_builder_content", children_only=True)

    selected = app.trans_selection.selected
    if len(selected) != 1:
        dpg.add_text("Select a single preset to edit",
                    parent="trans_builder_content")
        return

    name = selected[0]
    preset = app.json_mgr.get_transition(name)
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

    # X input - label changes based on mode
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

    # Y input - label changes based on mode
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

    # X input
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

    # Y input
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
    if dpg.does_item_exist("trans_json_text"):
        text = json.dumps(app.json_mgr.transition_data, indent=2)
        dpg.set_value("trans_json_text", text)


# Transition callbacks
def trans_checkbox_click(name: str, checked: bool):
    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)
    shift = dpg.is_key_down(dpg.mvKey_LShift) or dpg.is_key_down(dpg.mvKey_RShift)
    app.trans_selection.handle_click(name, ctrl, shift)
    refresh_transition_manager()


def trans_select_all():
    app.trans_selection.select_all()
    refresh_transition_manager()


def trans_select_none():
    app.trans_selection.select_none()
    refresh_transition_manager()


def trans_invert_selection():
    app.trans_selection.invert_selection()
    refresh_transition_manager()


def trans_move(name: str, direction: str):
    app.json_mgr.move_transition(name, direction)
    refresh_all()


def trans_edit(name: str):
    app.trans_selection.selected = [name]
    app.transition_mode = EditorMode.BUILDER
    switch_transition_mode(EditorMode.BUILDER)


def trans_rename(name: str):
    def do_rename(new_name: str):
        app.json_mgr.rename_transition(name, new_name)
        refresh_all()

    show_rename_dialog("Rename Transition", name, do_rename)


def trans_duplicate(name: str):
    new_name = app.json_mgr.get_unique_transition_name(f"{name}_copy")
    app.json_mgr.duplicate_transition(name, new_name)
    refresh_all()


def trans_delete(name: str):
    def do_delete():
        app.json_mgr.delete_transition(name)
        app.trans_selection.selected = []
        refresh_all()

    show_confirm_dialog(
        "Delete Transition",
        f"Delete preset_{name}?",
        do_delete
    )


def trans_delete_selected():
    selected = app.trans_selection.selected.copy()
    if not selected:
        return

    def do_delete():
        app.json_mgr.delete_transitions(selected)
        app.trans_selection.selected = []
        refresh_all()

    show_confirm_dialog(
        "Delete Selected",
        f"Delete {len(selected)} transition(s)?",
        do_delete
    )


def trans_duplicate_selected():
    selected = app.trans_selection.selected.copy()
    for name in selected:
        new_name = app.json_mgr.get_unique_transition_name(f"{name}_copy")
        app.json_mgr.duplicate_transition(name, new_name)
    refresh_all()


def trans_field_callback(sender, app_data, user_data):
    """DearPyGui callback for transition field inputs."""
    if user_data:
        name, field = user_data
        trans_update_field(name, field, app_data)


def trans_nested_callback(sender, app_data, user_data):
    """DearPyGui callback for nested transition field inputs (alpha, scale, rotation)."""
    if user_data:
        name, category, key = user_data
        trans_update_nested(name, category, key, app_data)


def trans_rename_callback(sender, app_data, user_data):
    """DearPyGui callback for transition rename input."""
    if user_data:
        trans_rename_preset(user_data, app_data)


def trans_update_field(name: str, field: str, value: Any):
    preset = app.json_mgr.get_transition(name) or {}
    preset[field] = value
    app.json_mgr.set_transition(name, preset)
    update_status_bar()


def trans_update_position(name: str, pos_type: str, key: str, value: float):
    preset = app.json_mgr.get_transition(name) or {}
    if pos_type not in preset:
        preset[pos_type] = {}
    preset[pos_type][key] = value
    app.json_mgr.set_transition(name, preset)
    update_status_bar()


def trans_update_nested(name: str, category: str, key: str, value: Any):
    preset = app.json_mgr.get_transition(name) or {}
    if category not in preset:
        preset[category] = {}
    preset[category][key] = value
    app.json_mgr.set_transition(name, preset)
    update_status_bar()


def trans_toggle_start_callback(sender, app_data, user_data):
    """Callback for start position toggle."""
    trans_toggle_section_mode(user_data, "start_position", app_data)


def trans_toggle_end_callback(sender, app_data, user_data):
    """Callback for end position toggle."""
    trans_toggle_section_mode(user_data, "end_position", app_data)


def trans_update_start_x_callback(sender, app_data, user_data):
    """Callback for start X position input."""
    trans_update_position_smart(user_data, "start_position", "x", app_data)


def trans_update_start_y_callback(sender, app_data, user_data):
    """Callback for start Y position input."""
    trans_update_position_smart(user_data, "start_position", "y", app_data)


def trans_update_end_x_callback(sender, app_data, user_data):
    """Callback for end X position input."""
    trans_update_position_smart(user_data, "end_position", "x", app_data)


def trans_update_end_y_callback(sender, app_data, user_data):
    """Callback for end Y position input."""
    trans_update_position_smart(user_data, "end_position", "y", app_data)


def trans_toggle_section_mode(name: str, pos_type: str, use_align: bool):
    """Toggle between align (0-1) and offset (pixels) mode for a position section (both X and Y)."""
    preset = app.json_mgr.get_transition(name)
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
            y_value = 1.0  # Default to bottom for Y align
        pos["yalign"] = y_value
    else:
        if 0.0 < y_value <= 1.0:
            y_value = 0.0
        pos["yoffset"] = y_value

    app.json_mgr.set_transition(name, preset)
    update_status_bar()

    # Update UI - refresh the builder to reflect changes
    refresh_transition_builder()


def trans_update_position_smart(name: str, pos_type: str, axis: str, value: float):
    """Update position value, using the current mode (align or offset)."""
    preset = app.json_mgr.get_transition(name) or {}
    if pos_type not in preset:
        preset[pos_type] = {}

    pos = preset[pos_type]
    offset_key = f"{axis}offset"
    align_key = f"{axis}align"

    # Determine which mode we're in based on which key exists
    if align_key in pos:
        pos[align_key] = value
    else:
        pos[offset_key] = value

    app.json_mgr.set_transition(name, preset)
    update_status_bar()


def trans_rename_preset(old_name: str, new_name: str):
    """Rename a transition preset."""
    new_name = new_name.strip()
    if not new_name or new_name == old_name:
        return
    # Check if new name already exists
    if app.json_mgr.get_transition(new_name):
        return
    # Copy data to new name, delete old
    preset = app.json_mgr.get_transition(old_name)
    if preset:
        app.json_mgr.set_transition(new_name, preset)
        app.json_mgr.delete_transition(old_name)
        # Update selection
        app.trans_selection.clear()
        app.trans_selection.toggle(new_name)
        refresh_all()
        update_status_bar()


# =============================================================================
# Shader UI
# =============================================================================

def refresh_shader_manager():
    """Refresh the shader manager list."""
    if not dpg.does_item_exist("shader_manager_list"):
        return

    dpg.delete_item("shader_manager_list", children_only=True)

    names = app.json_mgr.get_shader_names()
    selected = app.shader_selection.selected

    # Top toolbar: selection + actions
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

    # Selectable list with proper visual selection
    for name in names:
        is_selected = name in selected
        # Add visual prefix for selected items
        prefix = "[*] " if is_selected else "    "
        item_id = dpg.add_selectable(
            label=f"{prefix}shader_{name}",
            default_value=is_selected,
            callback=shader_manager_select_callback,
            user_data=name,
            width=800,
            parent="shader_manager_list"
        )
        # Apply selection theme for visual feedback
        apply_selection_theme(item_id, is_selected)


def shader_manager_select_callback(sender, app_data, user_data):
    """Callback for shader manager mode selection (receives user_data=name)."""
    shader_manager_select(user_data)


def shader_manager_select(name: str):
    """Handle selection in manager mode."""
    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)
    shift = dpg.is_key_down(dpg.mvKey_LShift) or dpg.is_key_down(dpg.mvKey_RShift)
    app.shader_selection.handle_click(name, ctrl, shift)
    refresh_shader_manager()


def shader_move_selected_top():
    """Move selected items to top."""
    for name in reversed(app.shader_selection.selected):
        app.json_mgr.move_shader(name, "top")
    refresh_shader_manager()


def shader_move_selected_up():
    """Move selected items up."""
    for name in app.shader_selection.selected:
        app.json_mgr.move_shader(name, "up")
    refresh_shader_manager()


def shader_move_selected_down():
    """Move selected items down."""
    for name in reversed(app.shader_selection.selected):
        app.json_mgr.move_shader(name, "down")
    refresh_shader_manager()


def shader_move_selected_bottom():
    """Move selected items to bottom."""
    for name in app.shader_selection.selected:
        app.json_mgr.move_shader(name, "bottom")
    refresh_shader_manager()


def refresh_shader_builder():
    """Refresh the shader builder panel (list + content)."""
    # Update the available shaders combo
    if dpg.does_item_exist("shader_builder_source_combo"):
        available = app.shader_parser.list_available_shaders()
        dpg.configure_item("shader_builder_source_combo", items=available)
        if available and not dpg.get_value("shader_builder_source_combo"):
            dpg.set_value("shader_builder_source_combo", available[0])

    refresh_shader_builder_list()
    refresh_shader_builder_content()


# Global to track selected source shader for new preset creation
shader_builder_selected_source: Optional[str] = None


def shader_builder_source_changed(sender, app_data, user_data):
    """Called when user selects a different source shader."""
    global shader_builder_selected_source
    shader_builder_selected_source = app_data


def shader_builder_create_new():
    """Create a new shader preset based on selected source shader."""
    global shader_builder_selected_source

    # Get selected source shader
    source = dpg.get_value("shader_builder_source_combo") if dpg.does_item_exist("shader_builder_source_combo") else None

    if not source:
        return

    # Get shader definition from parser
    shader_def = app.shader_parser.get_shader(source)

    # Build default params from shader definition
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

    # Generate unique name based on shader name
    base_name = source.replace("shader.", "").replace(".", "_")
    new_name = app.json_mgr.get_unique_shader_name(base_name)

    # Create the preset
    preset_data = {
        "shader": source,
        "animated": shader_def.is_animated if shader_def else False,
        "params": params
    }

    app.json_mgr.add_shader(new_name, preset_data)
    app.shader_selection.selected = [new_name]
    refresh_shader_builder()


def shader_builder_select_callback(sender, app_data, user_data):
    """Callback for shader builder mode selection."""
    shader_builder_select(user_data)


def refresh_shader_builder_list():
    """Refresh the shader builder list panel."""
    if not dpg.does_item_exist("shader_builder_list"):
        return

    dpg.delete_item("shader_builder_list", children_only=True)

    presets = app.json_mgr.get_shader_names()
    for name in presets:
        is_selected = name in app.shader_selection.selected
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


def shader_builder_select(name: str):
    """Select a shader preset in builder mode."""
    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)
    if ctrl:
        # Toggle selection
        if name in app.shader_selection.selected:
            app.shader_selection.selected.remove(name)
        else:
            app.shader_selection.selected.append(name)
    else:
        # Single selection
        app.shader_selection.selected = [name]
    refresh_shader_builder_list()
    refresh_shader_builder_content()


def shader_update_name_button_callback(sender, app_data, user_data):
    """Callback for Update Name button in shader builder."""
    old_name, input_tag = user_data
    new_name = dpg.get_value(input_tag)
    shader_rename_preset(old_name, new_name)


def shader_rename_callback(sender, app_data, user_data):
    """DearPyGui callback for shader rename input."""
    if user_data:
        shader_rename_preset(user_data, app_data)


def refresh_shader_builder_content():
    """Refresh the shader builder content/editor panel."""
    if not dpg.does_item_exist("shader_builder_content"):
        return

    dpg.delete_item("shader_builder_content", children_only=True)

    selected = app.shader_selection.selected
    if len(selected) != 1:
        dpg.add_text("Select a single preset to edit",
                    parent="shader_builder_content")
        return

    name = selected[0]
    preset = app.json_mgr.get_shader(name)
    if not preset:
        dpg.add_text(f"Preset '{name}' not found",
                    parent="shader_builder_content")
        return

    parent = "shader_builder_content"

    # Editable preset name with Update button
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

    # Shader description from parsed shader file (natural language from lines 3-5)
    shader_def = app.shader_parser.get_shader(shader_name)
    if shader_def:
        desc = shader_def.file_description
        if desc:
            dpg.add_text(desc, parent=parent, wrap=400, color=(200, 200, 200))
        # Show animated status as info text
        if shader_def.is_animated:
            dpg.add_text("(Animated shader - uses u_time)", parent=parent, color=(150, 200, 255))

    # Parameters
    dpg.add_separator(parent=parent)
    dpg.add_text("Parameters", parent=parent)

    # Get params from preset
    preset_params = preset.get("params", {})

    # Also get param definitions from shader (for defaults and types)
    shader_def = app.shader_parser.get_shader(shader_name)
    shader_param_defs = {}
    if shader_def:
        for p in shader_def.params:
            shader_param_defs[p.name] = p

    # Merge: use preset values, fall back to shader defaults
    all_param_keys = set(preset_params.keys()) | set(shader_param_defs.keys())

    for key in sorted(all_param_keys):
        # Skip invalid keys
        if not key or key == "null":
            continue

        # Get value from preset, or default from shader def
        if key in preset_params:
            value = preset_params[key]
        elif key in shader_param_defs:
            value = shader_param_defs[key].default
            if value is None:
                # Use type-based defaults
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

        # Determine type from value or shader def
        param_type = None
        if key in shader_param_defs:
            param_type = shader_param_defs[key].param_type

        if param_type == "color" or (isinstance(value, str) and value.startswith("#")):
            # Color parameter
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
    if dpg.does_item_exist("shader_json_text"):
        text = json.dumps(app.json_mgr.shader_data, indent=2)
        dpg.set_value("shader_json_text", text)


# Shader callbacks
def shader_checkbox_click(name: str, checked: bool):
    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)
    shift = dpg.is_key_down(dpg.mvKey_LShift) or dpg.is_key_down(dpg.mvKey_RShift)
    app.shader_selection.handle_click(name, ctrl, shift)
    refresh_shader_manager()


def shader_select_all():
    app.shader_selection.select_all()
    refresh_shader_manager()


def shader_select_none():
    app.shader_selection.select_none()
    refresh_shader_manager()


def shader_invert_selection():
    app.shader_selection.invert_selection()
    refresh_shader_manager()


def shader_move(name: str, direction: str):
    app.json_mgr.move_shader(name, direction)
    refresh_all()


def shader_edit(name: str):
    app.shader_selection.selected = [name]
    app.shader_mode = EditorMode.BUILDER
    switch_shader_mode(EditorMode.BUILDER)


def shader_rename(name: str):
    def do_rename(new_name: str):
        app.json_mgr.rename_shader(name, new_name)
        refresh_all()

    show_rename_dialog("Rename Shader", name, do_rename)


def shader_duplicate(name: str):
    new_name = app.json_mgr.get_unique_shader_name(f"{name}_copy")
    app.json_mgr.duplicate_shader(name, new_name)
    refresh_all()


def shader_delete(name: str):
    def do_delete():
        app.json_mgr.delete_shader(name)
        app.shader_selection.selected = []
        refresh_all()

    show_confirm_dialog(
        "Delete Shader",
        f"Delete shader_{name}?",
        do_delete
    )


def shader_delete_selected():
    selected = app.shader_selection.selected.copy()
    if not selected:
        return

    def do_delete():
        app.json_mgr.delete_shaders(selected)
        app.shader_selection.selected = []
        refresh_all()

    show_confirm_dialog(
        "Delete Selected",
        f"Delete {len(selected)} shader(s)?",
        do_delete
    )


def shader_duplicate_selected():
    selected = app.shader_selection.selected.copy()
    for name in selected:
        new_name = app.json_mgr.get_unique_shader_name(f"{name}_copy")
        app.json_mgr.duplicate_shader(name, new_name)
    refresh_all()


def shader_color_click(name: str):
    preset = app.json_mgr.get_shader(name) or {}
    params = preset.get("params", {})

    color_param = None
    color_value = "#FFFFFF"
    for key in ["u_glow_color", "u_tint_color"]:
        if key in params:
            color_param = key
            color_value = params[key]
            break

    if color_param:
        def on_change(hex_color: str):
            shader_update_param(name, color_param, hex_color)

        show_color_picker_dialog(f"Color: {name}", color_value, on_change)


def shader_update_field(name: str, field: str, value: Any):
    preset = app.json_mgr.get_shader(name) or {}
    preset[field] = value
    app.json_mgr.set_shader(name, preset)
    update_status_bar()


def shader_param_callback(sender, app_data, user_data):
    """DearPyGui callback for shader parameter inputs."""
    if user_data:
        name, param = user_data
        shader_update_param(name, param, app_data)


def shader_param_color_callback(sender, app_data, user_data):
    """DearPyGui callback for shader color parameter inputs."""
    if user_data:
        name, param = user_data
        shader_update_param_color(name, param, app_data)


def shader_update_param(name: str, param: str, value: Any):
    """Update a shader parameter value."""
    # Skip invalid param names
    if not param or param == "null":
        return

    preset = app.json_mgr.get_shader(name) or {}
    if "params" not in preset:
        preset["params"] = {}
    preset["params"][param] = value
    app.json_mgr.set_shader(name, preset)
    update_status_bar()


def shader_update_param_color(name: str, param: str, rgba: list):
    """Update a shader color parameter from RGBA list."""
    hex_color = rgba_to_hex(rgba)
    shader_update_param(name, param, hex_color)


def shader_rename_preset(old_name: str, new_name: str):
    """Rename a shader preset."""
    new_name = new_name.strip()
    if not new_name or new_name == old_name:
        return
    # Check if new name already exists
    if app.json_mgr.get_shader(new_name):
        return
    # Copy data to new name, delete old
    preset = app.json_mgr.get_shader(old_name)
    if preset:
        app.json_mgr.set_shader(new_name, preset)
        app.json_mgr.delete_shader(old_name)
        # Update selection
        app.shader_selection.clear()
        app.shader_selection.toggle(new_name)
        refresh_all()
        update_status_bar()


# =============================================================================
# Mode Switching
# =============================================================================

def switch_transition_mode(mode: EditorMode):
    app.transition_mode = mode

    # Update radio buttons
    if dpg.does_item_exist("trans_mode_builder"):
        dpg.set_value("trans_mode_builder", mode == EditorMode.BUILDER)
    if dpg.does_item_exist("trans_mode_manager"):
        dpg.set_value("trans_mode_manager", mode == EditorMode.MANAGER)
    if dpg.does_item_exist("trans_mode_json"):
        dpg.set_value("trans_mode_json", mode == EditorMode.JSON)

    # Show/hide panels
    if dpg.does_item_exist("trans_builder_panel"):
        dpg.configure_item("trans_builder_panel", show=(mode == EditorMode.BUILDER))
    if dpg.does_item_exist("trans_manager_panel"):
        dpg.configure_item("trans_manager_panel", show=(mode == EditorMode.MANAGER))
    if dpg.does_item_exist("trans_json_panel"):
        dpg.configure_item("trans_json_panel", show=(mode == EditorMode.JSON))

    refresh_transition_ui()


def switch_shader_mode(mode: EditorMode):
    app.shader_mode = mode

    if dpg.does_item_exist("shader_mode_builder"):
        dpg.set_value("shader_mode_builder", mode == EditorMode.BUILDER)
    if dpg.does_item_exist("shader_mode_manager"):
        dpg.set_value("shader_mode_manager", mode == EditorMode.MANAGER)
    if dpg.does_item_exist("shader_mode_json"):
        dpg.set_value("shader_mode_json", mode == EditorMode.JSON)

    if dpg.does_item_exist("shader_builder_panel"):
        dpg.configure_item("shader_builder_panel", show=(mode == EditorMode.BUILDER))
    if dpg.does_item_exist("shader_manager_panel"):
        dpg.configure_item("shader_manager_panel", show=(mode == EditorMode.MANAGER))
    if dpg.does_item_exist("shader_json_panel"):
        dpg.configure_item("shader_json_panel", show=(mode == EditorMode.JSON))

    refresh_shader_ui()


# =============================================================================
# Add New Presets
# =============================================================================

def add_new_transition():
    name = app.json_mgr.get_unique_transition_name("new_preset")
    app.json_mgr.add_transition(name, {
        "start_position": {"xoffset": 0},
        "end_position": {"xoffset": 0},
        "alpha": {"start": 1.0, "end": 1.0},
        "duration": 0.4,
        "easing": "easeout"
    })
    app.trans_selection.selected = [name]
    refresh_all()


def add_new_shader():
    name = app.json_mgr.get_unique_shader_name("new_shader")
    app.json_mgr.add_shader(name, {
        "shader": "shader.color_tint",
        "params": {
            "u_tint_color": "#FFFFFF",
            "u_amount": 0.5
        }
    })
    app.shader_selection.selected = [name]
    refresh_all()


# =============================================================================
# Export Demo Modal
# =============================================================================

demo_trans_selection: Optional[str] = None
demo_shader_selection: Optional[str] = None


def show_export_demo_modal():
    global demo_trans_selection, demo_shader_selection
    demo_trans_selection = None
    demo_shader_selection = None

    if dpg.does_item_exist("export_demo_window"):
        dpg.delete_item("export_demo_window")

    with dpg.window(
        label="Export Demo",
        modal=True,
        width=950,
        height=680,
        pos=[150, 80],
        tag="export_demo_window",
        on_close=lambda: dpg.delete_item("export_demo_window")
    ):
        # Demo window dimensions (use saved values)
        dpg.add_text("Demo Window Dimensions", color=(200, 200, 100))
        with dpg.group(horizontal=True):
            dpg.add_text("Width:")
            dpg.add_input_int(
                tag="demo_width",
                default_value=app.demo_width,
                min_value=100,
                min_clamped=True,
                width=100
            )
            dpg.add_spacer(width=20)
            dpg.add_text("Height:")
            dpg.add_input_int(
                tag="demo_height",
                default_value=app.demo_height,
                min_value=100,
                min_clamped=True,
                width=100
            )
        dpg.add_separator()

        dpg.add_text("Build demo combinations (max 10). Select one from each column and click Add.")
        dpg.add_text("Current selection shown below:", color=(150, 150, 150))

        # Show current selection status
        with dpg.group(horizontal=True):
            dpg.add_text("Trans:", color=(150, 200, 255))
            dpg.add_text("(none)", tag="demo_trans_status", color=(100, 100, 100))
            dpg.add_spacer(width=20)
            dpg.add_text("Shader:", color=(255, 200, 150))
            dpg.add_text("(none)", tag="demo_shader_status", color=(100, 100, 100))

        dpg.add_separator()

        with dpg.group(horizontal=True):
            # Column 1: Transitions
            with dpg.child_window(width=290, height=380):
                dpg.add_text("Transition Presets", color=(150, 200, 255))
                dpg.add_separator()
                with dpg.child_window(tag="demo_trans_list", height=-1):
                    refresh_demo_trans_list()

            # Column 2: Shaders
            with dpg.child_window(width=290, height=380):
                dpg.add_text("Shader Presets", color=(255, 200, 150))
                dpg.add_separator()
                with dpg.child_window(tag="demo_shader_list", height=-1):
                    refresh_demo_shader_list()

            # Column 3: Demo Items
            with dpg.child_window(width=320, height=380):
                dpg.add_text("Demo Items", tag="demo_items_header", color=(150, 255, 150))
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Add Selected", callback=demo_add_item)
                    dpg.add_button(label="Clear All", callback=demo_clear_items)
                dpg.add_separator()
                with dpg.child_window(tag="demo_items_list", height=-1):
                    refresh_demo_items_list()

        dpg.add_separator()

        # Status feedback area
        dpg.add_text("", tag="demo_status_text", color=(150, 150, 150))

        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Generate Demo Script",
                callback=demo_generate,
                width=150
            )
            dpg.add_button(
                label="Run in Ren'Py",
                callback=demo_run,
                width=120
            )
            dpg.add_spacer(width=20)
            dpg.add_button(
                label="Close",
                callback=lambda: dpg.delete_item("export_demo_window"),
                width=80
            )


def demo_trans_select_callback(sender, app_data, user_data):
    """Callback for demo transition selection."""
    demo_select_transition(user_data)


def refresh_demo_trans_list():
    """Refresh the demo transition list with selection highlighting."""
    if not dpg.does_item_exist("demo_trans_list"):
        return

    dpg.delete_item("demo_trans_list", children_only=True)

    for name in app.json_mgr.get_transition_names():
        is_selected = (name == demo_trans_selection)
        prefix = "[*] " if is_selected else "    "
        item_id = dpg.add_selectable(
            label=f"{prefix}preset_{name}",
            default_value=is_selected,
            callback=demo_trans_select_callback,
            user_data=name,
            parent="demo_trans_list"
        )
        apply_selection_theme(item_id, is_selected)


def demo_shader_select_callback(sender, app_data, user_data):
    """Callback for demo shader selection."""
    demo_select_shader(user_data)


def refresh_demo_shader_list():
    """Refresh the demo shader list with selection highlighting."""
    if not dpg.does_item_exist("demo_shader_list"):
        return

    dpg.delete_item("demo_shader_list", children_only=True)

    for name in app.json_mgr.get_shader_names():
        is_selected = (name == demo_shader_selection)
        prefix = "[*] " if is_selected else "    "
        item_id = dpg.add_selectable(
            label=f"{prefix}shader_{name}",
            default_value=is_selected,
            callback=demo_shader_select_callback,
            user_data=name,
            parent="demo_shader_list"
        )
        apply_selection_theme(item_id, is_selected)


def demo_select_transition(name: str):
    global demo_trans_selection
    demo_trans_selection = name
    # Update status display
    if dpg.does_item_exist("demo_trans_status"):
        dpg.set_value("demo_trans_status", f"preset_{name}")
        dpg.configure_item("demo_trans_status", color=(150, 200, 255))
    # Refresh list to show selection
    refresh_demo_trans_list()


def demo_select_shader(name: str):
    global demo_shader_selection
    demo_shader_selection = name
    # Update status display
    if dpg.does_item_exist("demo_shader_status"):
        dpg.set_value("demo_shader_status", f"shader_{name}")
        dpg.configure_item("demo_shader_status", color=(255, 200, 150))
    # Refresh list to show selection
    refresh_demo_shader_list()


def demo_add_item():
    global demo_trans_selection, demo_shader_selection

    if len(app.demo_gen.items) >= 10:
        return

    if demo_trans_selection or demo_shader_selection:
        app.demo_gen.add_item(demo_trans_selection, demo_shader_selection)
        demo_trans_selection = None
        demo_shader_selection = None
        # Reset status displays
        if dpg.does_item_exist("demo_trans_status"):
            dpg.set_value("demo_trans_status", "(none)")
            dpg.configure_item("demo_trans_status", color=(100, 100, 100))
        if dpg.does_item_exist("demo_shader_status"):
            dpg.set_value("demo_shader_status", "(none)")
            dpg.configure_item("demo_shader_status", color=(100, 100, 100))
        # Update header with count
        if dpg.does_item_exist("demo_items_header"):
            dpg.set_value("demo_items_header", f"Demo Items ({len(app.demo_gen.items)}/10)")
        # Refresh all lists
        refresh_demo_trans_list()
        refresh_demo_shader_list()
        refresh_demo_items_list()


def demo_clear_items():
    app.demo_gen.clear_items()
    if dpg.does_item_exist("demo_items_header"):
        dpg.set_value("demo_items_header", "Demo Items (0/10)")
    refresh_demo_items_list()


def demo_remove_item_callback(sender, app_data, user_data):
    """DearPyGui callback for demo item remove button."""
    if user_data is not None:
        demo_remove_item(user_data)


def demo_remove_item(index: int):
    app.demo_gen.remove_item(index)
    if dpg.does_item_exist("demo_items_header"):
        dpg.set_value("demo_items_header", f"Demo Items ({len(app.demo_gen.items)}/10)")
    refresh_demo_items_list()


def refresh_demo_items_list():
    if not dpg.does_item_exist("demo_items_list"):
        return

    dpg.delete_item("demo_items_list", children_only=True)

    for i, item in enumerate(app.demo_gen.items):
        with dpg.group(horizontal=True, parent="demo_items_list"):
            dpg.add_text(f"{i+1}.", color=(100, 100, 100))
            dpg.add_text(item.display_name, color=(200, 200, 200))
            dpg.add_button(
                label="X",
                callback=demo_remove_item_callback,
                user_data=i,
                width=25
            )


def demo_generate():
    # Get dimensions from inputs
    width = app.demo_width
    height = app.demo_height
    if dpg.does_item_exist("demo_width"):
        width = max(100, dpg.get_value("demo_width"))
    if dpg.does_item_exist("demo_height"):
        height = max(100, dpg.get_value("demo_height"))

    # Save dimensions to app state
    app.demo_width = width
    app.demo_height = height

    # Set dimensions on demo generator
    app.demo_gen.screen_width = width
    app.demo_gen.screen_height = height

    # Generate options.rpy with screen dimensions
    options_path = os.path.join(app.game_folder, "options.rpy")
    try:
        with open(options_path, 'w', encoding='utf-8') as f:
            f.write(f'''## options.rpy - Generated by Preset Editor
##
## Screen dimensions for demo testing

define config.screen_width = {width}
define config.screen_height = {height}

define config.name = "Preset Editor Demo"
define config.save_directory = "preset_editor_demo"
''')
    except Exception as e:
        print(f"Error writing options.rpy: {e}")

    # Generate script.rpy with image definitions
    script_path = os.path.join(app.game_folder, "script.rpy")
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(f'''## script.rpy - Generated by Preset Editor
##
## Demo game setup

define test = Character("Test")

# Background stretched to fit screen dimensions
image bg_demo = im.Scale("images/bg_demo.png", {width}, {height})

# Character image
image char_demo = "images/char_demo.png"

label start:
    jump preset_demo
''')
    except Exception as e:
        print(f"Error writing script.rpy: {e}")

    output_path = os.path.join(app.game_folder, "content", "preset_demo.rpy")
    if app.demo_gen.save_script(output_path):
        # Save config to persist dimensions
        app.save_config()
        # Show success feedback
        if dpg.does_item_exist("demo_status_text"):
            dpg.set_value("demo_status_text", f"Success! Demo generated ({width}x{height})")
            dpg.configure_item("demo_status_text", color=(100, 255, 100))
        print(f"Demo script saved to: {output_path}")
        # Window stays open - user can close manually
    else:
        # Show error feedback
        if dpg.does_item_exist("demo_status_text"):
            dpg.set_value("demo_status_text", "Error: Failed to save demo script")
            dpg.configure_item("demo_status_text", color=(255, 100, 100))
        print("Failed to save demo script")


def demo_run():
    demo_generate()

    if app.renpy_exe and os.path.exists(app.renpy_exe):
        try:
            subprocess.Popen([app.renpy_exe, app.game_folder, "run"])
        except Exception as e:
            print(f"Failed to launch Ren'Py: {e}")
    else:
        print("Ren'Py executable not configured. Set it in Settings.")


# =============================================================================
# Settings Modal
# =============================================================================

def settings_browse_file(target_tag: str):
    """Open file browser and set result to target input."""
    # Store current values before hiding settings
    current_values = {
        "trans": dpg.get_value("settings_trans_path"),
        "shader": dpg.get_value("settings_shader_path"),
        "shader_folder": dpg.get_value("settings_shader_folder"),
        "game_folder": dpg.get_value("settings_game_folder"),
        "renpy_exe": dpg.get_value("settings_renpy_exe"),
        "target": target_tag
    }

    def callback(sender, app_data):
        selected_path = None
        if app_data and "file_path_name" in app_data:
            selected_path = app_data["file_path_name"]
        dpg.delete_item("file_dialog")
        # Reopen settings with updated value
        reopen_settings_with_values(current_values, selected_path)

    def cancel_callback(sender, app_data):
        dpg.delete_item("file_dialog")
        reopen_settings_with_values(current_values, None)

    # Close settings window
    dpg.delete_item("settings_window")

    if dpg.does_item_exist("file_dialog"):
        dpg.delete_item("file_dialog")

    start_path = current_values.get(target_tag.replace("settings_", ""), "")
    if start_path:
        start_path = os.path.dirname(start_path)

    with dpg.file_dialog(
        callback=callback,
        cancel_callback=cancel_callback,
        tag="file_dialog",
        width=700,
        height=400,
        show=True,
        default_path=start_path or "."
    ):
        dpg.add_file_extension(".json", color=(0, 255, 0, 255))
        dpg.add_file_extension(".exe", color=(0, 255, 255, 255))
        dpg.add_file_extension(".*")


def settings_browse_exe(target_tag: str):
    """Open executable browser and set result to target input."""
    # Store current values before hiding settings
    current_values = {
        "trans": dpg.get_value("settings_trans_path"),
        "shader": dpg.get_value("settings_shader_path"),
        "shader_folder": dpg.get_value("settings_shader_folder"),
        "game_folder": dpg.get_value("settings_game_folder"),
        "renpy_exe": dpg.get_value("settings_renpy_exe"),
        "target": target_tag
    }

    def callback(sender, app_data):
        selected_path = None
        if app_data and "file_path_name" in app_data:
            selected_path = app_data["file_path_name"]
        dpg.delete_item("exe_dialog")
        reopen_settings_with_values(current_values, selected_path)

    def cancel_callback(sender, app_data):
        dpg.delete_item("exe_dialog")
        reopen_settings_with_values(current_values, None)

    # Close settings window
    dpg.delete_item("settings_window")

    if dpg.does_item_exist("exe_dialog"):
        dpg.delete_item("exe_dialog")

    start_path = current_values["renpy_exe"]
    if start_path:
        start_path = os.path.dirname(start_path)

    with dpg.file_dialog(
        callback=callback,
        cancel_callback=cancel_callback,
        tag="exe_dialog",
        width=700,
        height=400,
        show=True,
        default_path=start_path or "."
    ):
        dpg.add_file_extension(".exe", color=(0, 255, 255, 255))
        dpg.add_file_extension(".app", color=(0, 255, 255, 255))
        dpg.add_file_extension(".*")


def settings_browse_folder(target_tag: str):
    """Open folder browser and set result to target input."""
    # Store current values before hiding settings
    current_values = {
        "trans": dpg.get_value("settings_trans_path"),
        "shader": dpg.get_value("settings_shader_path"),
        "shader_folder": dpg.get_value("settings_shader_folder"),
        "game_folder": dpg.get_value("settings_game_folder"),
        "renpy_exe": dpg.get_value("settings_renpy_exe"),
        "target": target_tag
    }

    def callback(sender, app_data):
        selected_path = None
        if app_data and "file_path_name" in app_data:
            selected_path = app_data["file_path_name"]
        dpg.delete_item("folder_dialog")
        reopen_settings_with_values(current_values, selected_path)

    def cancel_callback(sender, app_data):
        dpg.delete_item("folder_dialog")
        reopen_settings_with_values(current_values, None)

    # Close settings window
    dpg.delete_item("settings_window")

    if dpg.does_item_exist("folder_dialog"):
        dpg.delete_item("folder_dialog")

    start_path = ""
    if target_tag == "settings_shader_folder":
        start_path = current_values["shader_folder"]
    elif target_tag == "settings_game_folder":
        start_path = current_values["game_folder"]

    with dpg.file_dialog(
        callback=callback,
        cancel_callback=cancel_callback,
        tag="folder_dialog",
        directory_selector=True,
        width=700,
        height=400,
        show=True,
        default_path=start_path or "."
    ):
        pass


def reopen_settings_with_values(values: dict, new_path: str):
    """Reopen settings modal with preserved values, updating target if new_path provided."""
    target = values["target"]

    # Update the target value if a new path was selected
    if new_path:
        if target == "settings_trans_path":
            values["trans"] = new_path
        elif target == "settings_shader_path":
            values["shader"] = new_path
        elif target == "settings_shader_folder":
            values["shader_folder"] = new_path
        elif target == "settings_game_folder":
            values["game_folder"] = new_path
        elif target == "settings_renpy_exe":
            values["renpy_exe"] = new_path

    # Reopen the settings window
    show_settings_modal_with_values(
        values["trans"],
        values["shader"],
        values["shader_folder"],
        values["game_folder"],
        values["renpy_exe"]
    )


def show_settings_modal_with_values(trans_path, shader_path, shader_folder, game_folder, renpy_exe):
    """Show settings modal with specific values."""
    if dpg.does_item_exist("settings_window"):
        dpg.delete_item("settings_window")

    with dpg.window(
        label="Settings",
        modal=True,
        width=620,
        height=400,
        pos=[280, 160],
        tag="settings_window",
        on_close=lambda: dpg.delete_item("settings_window")
    ):
        dpg.add_text("Configure file paths")
        dpg.add_separator()
        dpg.add_spacer(height=5)

        dpg.add_text("Transition Presets JSON:")
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                default_value=trans_path,
                tag="settings_trans_path",
                width=500
            )
            dpg.add_button(label="Browse...", callback=lambda: settings_browse_file("settings_trans_path"), width=80)
        dpg.add_spacer(height=5)

        dpg.add_text("Shader Presets JSON:")
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                default_value=shader_path,
                tag="settings_shader_path",
                width=500
            )
            dpg.add_button(label="Browse...", callback=lambda: settings_browse_file("settings_shader_path"), width=80)
        dpg.add_spacer(height=5)

        dpg.add_text("Shader .rpy Folder:")
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                default_value=shader_folder,
                tag="settings_shader_folder",
                width=500
            )
            dpg.add_button(label="Browse...", callback=lambda: settings_browse_folder("settings_shader_folder"), width=80)
        dpg.add_spacer(height=5)

        dpg.add_text("Game Folder:")
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                default_value=game_folder,
                tag="settings_game_folder",
                width=500
            )
            dpg.add_button(label="Browse...", callback=lambda: settings_browse_folder("settings_game_folder"), width=80)
        dpg.add_spacer(height=5)

        dpg.add_text("Ren'Py Executable:")
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                default_value=renpy_exe,
                tag="settings_renpy_exe",
                width=500
            )
            dpg.add_button(label="Browse...", callback=lambda: settings_browse_exe("settings_renpy_exe"), width=80)

        dpg.add_spacer(height=10)
        dpg.add_separator()
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Apply", callback=settings_apply, width=100)
            dpg.add_button(label="Cancel",
                          callback=lambda: dpg.delete_item("settings_window"),
                          width=100)


def show_settings_modal():
    """Show settings modal with current app values."""
    show_settings_modal_with_values(
        app.transition_presets_path,
        app.shader_presets_path,
        app.shader_folder,
        app.game_folder,
        app.renpy_exe
    )


def settings_apply():
    app.transition_presets_path = dpg.get_value("settings_trans_path")
    app.shader_presets_path = dpg.get_value("settings_shader_path")
    app.shader_folder = dpg.get_value("settings_shader_folder")
    app.game_folder = dpg.get_value("settings_game_folder")
    app.renpy_exe = dpg.get_value("settings_renpy_exe")

    if app.save_config():
        if app.status_bar:
            app.status_bar.set_status("Settings saved successfully", (100, 200, 100))
    else:
        if app.status_bar:
            app.status_bar.set_status("Error saving settings!", (255, 100, 100))

    app.load_data()
    refresh_all()

    dpg.delete_item("settings_window")


# =============================================================================
# Main UI Setup
# =============================================================================

def setup_ui():
    """Build the main UI."""

    # Menu bar
    with dpg.viewport_menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Reload", callback=lambda: (app.load_data(), refresh_all()))
            dpg.add_menu_item(label="Settings", callback=show_settings_modal)
            dpg.add_separator()
            dpg.add_menu_item(label="Exit", callback=dpg.stop_dearpygui)

        with dpg.menu(label="Edit"):
            dpg.add_menu_item(label="Undo", callback=lambda: (app.json_mgr.undo(), refresh_all()),
                            shortcut="Ctrl+Z")
            dpg.add_menu_item(label="Redo", callback=lambda: (app.json_mgr.redo(), refresh_all()),
                            shortcut="Ctrl+Y")

        with dpg.menu(label="Tools"):
            dpg.add_menu_item(label="Export Demo...", callback=show_export_demo_modal)

    # Main window
    with dpg.window(tag="primary_window"):
        # Add spacing below menu bar
        dpg.add_spacer(height=10)

        # Tab bar
        with dpg.tab_bar():
            # ========== TRANSITIONS TAB ==========
            with dpg.tab(label="TRANSITIONS"):
                # Mode selector and actions
                with dpg.group(horizontal=True):
                    dpg.add_text("Mode:")
                    dpg.add_radio_button(
                        items=["Builder", "Manager", "JSON"],
                        default_value="Manager",
                        horizontal=True,
                        callback=lambda s, a: switch_transition_mode(EditorMode[a.upper()])
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

            # ========== SHADERS TAB ==========
            with dpg.tab(label="SHADERS"):
                with dpg.group(horizontal=True):
                    dpg.add_text("Mode:")
                    dpg.add_radio_button(
                        items=["Builder", "Manager", "JSON"],
                        default_value="Manager",
                        horizontal=True,
                        callback=lambda s, a: switch_shader_mode(EditorMode[a.upper()])
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

        # Status bar at bottom
        dpg.add_separator()
        with dpg.group(tag="status_bar_container"):
            app.status_bar = StatusBar("status_bar_container")

    dpg.set_primary_window("primary_window", True)


def setup_keyboard_shortcuts():
    """Set up global keyboard shortcuts."""
    def ctrl_pressed():
        return dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)

    def undo_callback():
        if ctrl_pressed():
            app.json_mgr.undo()
            refresh_all()

    def redo_callback():
        if ctrl_pressed():
            app.json_mgr.redo()
            refresh_all()

    with dpg.handler_registry():
        dpg.add_key_press_handler(dpg.mvKey_Z, callback=undo_callback)
        dpg.add_key_press_handler(dpg.mvKey_Y, callback=redo_callback)


# =============================================================================
# Main
# =============================================================================

def main():
    # Load configuration
    app.load_config()

    # Create DPG context
    dpg.create_context()

    # Initialize selection themes (must be after context creation)
    init_selection_themes()

    # Apply dark theme
    theme = create_dark_theme()
    dpg.bind_theme(theme)

    # Build UI
    setup_ui()
    setup_keyboard_shortcuts()

    # Load data
    app.load_data()

    # Register change callback
    app.json_mgr.on_change(update_status_bar)

    # Create viewport
    dpg.create_viewport(
        title="Preset Editor v2.0",
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT
    )
    dpg.setup_dearpygui()
    dpg.show_viewport()

    # Initial refresh
    refresh_all()

    # Run
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
