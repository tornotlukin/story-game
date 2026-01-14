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
    show_rename_dialog, show_confirm_dialog, show_color_picker_dialog
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
            "renpy_exe": self.renpy_exe
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

    # Selection count
    with dpg.group(horizontal=True, parent="trans_manager_list"):
        dpg.add_text(f"Selected: {len(selected)} of {len(names)}")
        dpg.add_spacer(width=20)
        dpg.add_button(label="Select All", callback=trans_select_all, width=80)
        dpg.add_button(label="Select None", callback=trans_select_none, width=85)
        dpg.add_button(label="Invert", callback=trans_invert_selection, width=60)

    dpg.add_separator(parent="trans_manager_list")
    dpg.add_text("Tip: Ctrl+Click to toggle, Shift+Click for range",
                 color=(150, 150, 150), parent="trans_manager_list")
    dpg.add_spacer(height=5, parent="trans_manager_list")

    # List items
    for name in names:
        is_selected = name in selected
        with dpg.group(horizontal=True, parent="trans_manager_list"):
            dpg.add_checkbox(
                default_value=is_selected,
                callback=lambda s, a, n=name: trans_checkbox_click(n, a)
            )
            dpg.add_text(f"preset_{name}", color=(200, 200, 200))
            dpg.add_spacer(width=20)

            # Move buttons
            dpg.add_button(label="^^", width=25,
                          callback=lambda s, a, n=name: trans_move(n, "top"))
            dpg.add_button(label="^", width=25,
                          callback=lambda s, a, n=name: trans_move(n, "up"))
            dpg.add_button(label="v", width=25,
                          callback=lambda s, a, n=name: trans_move(n, "down"))
            dpg.add_button(label="vv", width=25,
                          callback=lambda s, a, n=name: trans_move(n, "bottom"))
            dpg.add_spacer(width=10)

            # Action buttons
            dpg.add_button(label="Edit", width=40,
                          callback=lambda s, a, n=name: trans_edit(n))
            dpg.add_button(label="Rename", width=55,
                          callback=lambda s, a, n=name: trans_rename(n))
            dpg.add_button(label="Dupe", width=40,
                          callback=lambda s, a, n=name: trans_duplicate(n))
            dpg.add_button(label="Del", width=35,
                          callback=lambda s, a, n=name: trans_delete(n))

    # Bulk actions
    dpg.add_separator(parent="trans_manager_list")
    with dpg.group(horizontal=True, parent="trans_manager_list"):
        dpg.add_text("Bulk Actions:")
        dpg.add_button(label="Delete Selected", callback=trans_delete_selected)
        dpg.add_button(label="Duplicate Selected", callback=trans_duplicate_selected)


def refresh_transition_builder():
    """Refresh the transition builder panel (list + content)."""
    refresh_transition_builder_list()
    refresh_transition_builder_content()


def refresh_transition_builder_list():
    """Refresh the transition builder list panel."""
    if not dpg.does_item_exist("trans_builder_list"):
        return

    dpg.delete_item("trans_builder_list", children_only=True)

    presets = app.json_mgr.get_transition_names()
    for name in presets:
        is_selected = name in app.trans_selection.selected
        dpg.add_selectable(
            label=name,
            default_value=is_selected,
            callback=lambda s, a, n=name: trans_builder_select(n),
            width=230,
            parent="trans_builder_list"
        )


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

    dpg.add_text(f"Editing: preset_{name}", parent=parent)
    dpg.add_separator(parent=parent)

    # Duration
    dpg.add_input_float(
        label="Duration",
        default_value=preset.get("duration", 0.4),
        callback=lambda s, a: trans_update_field(name, "duration", a),
        min_value=0.0, max_value=5.0, step=0.1,
        parent=parent
    )

    # Easing
    easing_options = ["linear", "easein", "easeout", "ease"]
    dpg.add_combo(
        label="Easing",
        items=easing_options,
        default_value=preset.get("easing", "easeout"),
        callback=lambda s, a: trans_update_field(name, "easing", a),
        parent=parent
    )

    # Start Position
    dpg.add_separator(parent=parent)
    dpg.add_text("Start Position", parent=parent)
    start_pos = preset.get("start_position", {})
    for key in ["xoffset", "yoffset", "xalign", "yalign"]:
        default = start_pos.get(key, 0.0 if "offset" in key else None)
        if default is not None or key in ["xoffset", "yoffset"]:
            dpg.add_input_float(
                label=f"Start {key}",
                default_value=default if default is not None else 0.0,
                callback=lambda s, a, k=key: trans_update_position(name, "start_position", k, a),
                step=0.1 if "align" in key else 10.0,
                parent=parent
            )

    # End Position
    dpg.add_separator(parent=parent)
    dpg.add_text("End Position", parent=parent)
    end_pos = preset.get("end_position", {})
    for key in ["xoffset", "yoffset", "xalign", "yalign"]:
        default = end_pos.get(key, 0.0 if "offset" in key else None)
        if default is not None or key in ["xoffset", "yoffset"]:
            dpg.add_input_float(
                label=f"End {key}",
                default_value=default if default is not None else 0.0,
                callback=lambda s, a, k=key: trans_update_position(name, "end_position", k, a),
                step=0.1 if "align" in key else 10.0,
                parent=parent
            )

    # Alpha
    dpg.add_separator(parent=parent)
    dpg.add_text("Alpha", parent=parent)
    alpha = preset.get("alpha", {"start": 1.0, "end": 1.0})
    dpg.add_input_float(
        label="Alpha Start",
        default_value=alpha.get("start", 1.0),
        callback=lambda s, a: trans_update_nested(name, "alpha", "start", a),
        min_value=0.0, max_value=1.0, step=0.1,
        parent=parent
    )
    dpg.add_input_float(
        label="Alpha End",
        default_value=alpha.get("end", 1.0),
        callback=lambda s, a: trans_update_nested(name, "alpha", "end", a),
        min_value=0.0, max_value=1.0, step=0.1,
        parent=parent
    )

    # Scale
    dpg.add_separator(parent=parent)
    dpg.add_text("Scale", parent=parent)
    scale = preset.get("scale", {"start": 1.0, "end": 1.0})
    dpg.add_input_float(
        label="Scale Start",
        default_value=scale.get("start", 1.0),
        callback=lambda s, a: trans_update_nested(name, "scale", "start", a),
        min_value=0.0, max_value=3.0, step=0.1,
        parent=parent
    )
    dpg.add_input_float(
        label="Scale End",
        default_value=scale.get("end", 1.0),
        callback=lambda s, a: trans_update_nested(name, "scale", "end", a),
        min_value=0.0, max_value=3.0, step=0.1,
        parent=parent
    )

    # Rotation
    dpg.add_separator(parent=parent)
    dpg.add_text("Rotation", parent=parent)
    rotation = preset.get("rotation", {"start": 0, "end": 0})
    dpg.add_input_int(
        label="Rotation Start",
        default_value=int(rotation.get("start", 0)),
        callback=lambda s, a: trans_update_nested(name, "rotation", "start", a),
        min_value=-360, max_value=360, step=15,
        parent=parent
    )
    dpg.add_input_int(
        label="Rotation End",
        default_value=int(rotation.get("end", 0)),
        callback=lambda s, a: trans_update_nested(name, "rotation", "end", a),
        min_value=-360, max_value=360, step=15,
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

    # Selection count
    with dpg.group(horizontal=True, parent="shader_manager_list"):
        dpg.add_text(f"Selected: {len(selected)} of {len(names)}")
        dpg.add_spacer(width=20)
        dpg.add_button(label="Select All", callback=shader_select_all, width=80)
        dpg.add_button(label="Select None", callback=shader_select_none, width=85)
        dpg.add_button(label="Invert", callback=shader_invert_selection, width=60)

    dpg.add_separator(parent="shader_manager_list")
    dpg.add_text("Tip: Ctrl+Click to toggle, Shift+Click for range",
                 color=(150, 150, 150), parent="shader_manager_list")
    dpg.add_spacer(height=5, parent="shader_manager_list")

    # List items
    for name in names:
        is_selected = name in selected
        preset = app.json_mgr.get_shader(name) or {}
        params = preset.get("params", {})

        # Get color if present
        color_hex = None
        for key in ["u_glow_color", "u_tint_color"]:
            if key in params:
                color_hex = params[key]
                break

        with dpg.group(horizontal=True, parent="shader_manager_list"):
            dpg.add_checkbox(
                default_value=is_selected,
                callback=lambda s, a, n=name: shader_checkbox_click(n, a)
            )

            # Color swatch
            if color_hex:
                rgb = hex_to_rgb(color_hex)
                dpg.add_color_button(
                    default_value=[rgb[0], rgb[1], rgb[2], 255],
                    width=20, height=20,
                    no_border=True,
                    callback=lambda s, a, n=name: shader_color_click(n)
                )

            dpg.add_text(f"shader_{name}", color=(200, 200, 200))
            dpg.add_spacer(width=20)

            # Move buttons
            dpg.add_button(label="^^", width=25,
                          callback=lambda s, a, n=name: shader_move(n, "top"))
            dpg.add_button(label="^", width=25,
                          callback=lambda s, a, n=name: shader_move(n, "up"))
            dpg.add_button(label="v", width=25,
                          callback=lambda s, a, n=name: shader_move(n, "down"))
            dpg.add_button(label="vv", width=25,
                          callback=lambda s, a, n=name: shader_move(n, "bottom"))
            dpg.add_spacer(width=10)

            # Action buttons
            dpg.add_button(label="Edit", width=40,
                          callback=lambda s, a, n=name: shader_edit(n))
            dpg.add_button(label="Rename", width=55,
                          callback=lambda s, a, n=name: shader_rename(n))
            dpg.add_button(label="Dupe", width=40,
                          callback=lambda s, a, n=name: shader_duplicate(n))
            dpg.add_button(label="Del", width=35,
                          callback=lambda s, a, n=name: shader_delete(n))

    # Bulk actions
    dpg.add_separator(parent="shader_manager_list")
    with dpg.group(horizontal=True, parent="shader_manager_list"):
        dpg.add_text("Bulk Actions:")
        dpg.add_button(label="Delete Selected", callback=shader_delete_selected)
        dpg.add_button(label="Duplicate Selected", callback=shader_duplicate_selected)


def refresh_shader_builder():
    """Refresh the shader builder panel (list + content)."""
    refresh_shader_builder_list()
    refresh_shader_builder_content()


def refresh_shader_builder_list():
    """Refresh the shader builder list panel."""
    if not dpg.does_item_exist("shader_builder_list"):
        return

    dpg.delete_item("shader_builder_list", children_only=True)

    presets = app.json_mgr.get_shader_names()
    for name in presets:
        is_selected = name in app.shader_selection.selected
        dpg.add_selectable(
            label=name,
            default_value=is_selected,
            callback=lambda s, a, n=name: shader_builder_select(n),
            width=230,
            parent="shader_builder_list"
        )


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

    dpg.add_text(f"Editing: shader_{name}", parent=parent)
    dpg.add_separator(parent=parent)

    # Shader name (read-only)
    dpg.add_input_text(
        label="Shader",
        default_value=preset.get("shader", ""),
        readonly=True,
        parent=parent
    )

    # Available shaders dropdown
    available = app.shader_parser.list_available_shaders()
    if available:
        dpg.add_combo(
            label="Change Shader",
            items=available,
            default_value=preset.get("shader", ""),
            callback=lambda s, a: shader_update_field(name, "shader", a),
            parent=parent
        )

    # Animated flag
    dpg.add_checkbox(
        label="Animated",
        default_value=preset.get("animated", False),
        callback=lambda s, a: shader_update_field(name, "animated", a),
        parent=parent
    )

    # Parameters
    dpg.add_separator(parent=parent)
    dpg.add_text("Parameters", parent=parent)

    params = preset.get("params", {})
    for key, value in params.items():
        if isinstance(value, str) and value.startswith("#"):
            # Color parameter
            rgb = hex_to_rgb(value)
            dpg.add_color_edit(
                label=key,
                default_value=[rgb[0], rgb[1], rgb[2], 255],
                callback=lambda s, a, k=key: shader_update_param_color(name, k, a),
                no_alpha=True,
                parent=parent
            )
        elif isinstance(value, float):
            dpg.add_input_float(
                label=key,
                default_value=value,
                callback=lambda s, a, k=key: shader_update_param(name, k, a),
                step=0.1,
                parent=parent
            )
        elif isinstance(value, int):
            dpg.add_input_int(
                label=key,
                default_value=value,
                callback=lambda s, a, k=key: shader_update_param(name, k, a),
                parent=parent
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


def shader_update_param(name: str, param: str, value: Any):
    preset = app.json_mgr.get_shader(name) or {}
    if "params" not in preset:
        preset["params"] = {}
    preset["params"][param] = value
    app.json_mgr.set_shader(name, preset)
    update_status_bar()


def shader_update_param_color(name: str, param: str, rgba: list):
    hex_color = rgba_to_hex(rgba)
    shader_update_param(name, param, hex_color)


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
        height=600,
        pos=[150, 100],
        tag="export_demo_window",
        on_close=lambda: dpg.delete_item("export_demo_window")
    ):
        dpg.add_text("Build demo combinations (max 10). Select one from each column and click Add.")
        dpg.add_separator()

        with dpg.group(horizontal=True):
            # Column 1: Transitions
            with dpg.child_window(width=290, height=420):
                dpg.add_text("Transition Presets", color=(150, 200, 255))
                dpg.add_separator()
                with dpg.child_window(tag="demo_trans_list", height=-1):
                    for name in app.json_mgr.get_transition_names():
                        dpg.add_selectable(
                            label=f"preset_{name}",
                            callback=lambda s, a, n=name: demo_select_transition(n)
                        )

            # Column 2: Shaders
            with dpg.child_window(width=290, height=420):
                dpg.add_text("Shader Presets", color=(255, 200, 150))
                dpg.add_separator()
                with dpg.child_window(tag="demo_shader_list", height=-1):
                    for name in app.json_mgr.get_shader_names():
                        dpg.add_selectable(
                            label=f"shader_{name}",
                            callback=lambda s, a, n=name: demo_select_shader(n)
                        )

            # Column 3: Demo Items
            with dpg.child_window(width=320, height=420):
                dpg.add_text(f"Demo Items ({len(app.demo_gen.items)}/10)", color=(150, 255, 150))
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Add Selected", callback=demo_add_item)
                    dpg.add_button(label="Clear All", callback=demo_clear_items)
                dpg.add_separator()
                with dpg.child_window(tag="demo_items_list", height=-1):
                    refresh_demo_items_list()

        dpg.add_separator()
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
                label="Cancel",
                callback=lambda: dpg.delete_item("export_demo_window"),
                width=80
            )


def demo_select_transition(name: str):
    global demo_trans_selection
    demo_trans_selection = name


def demo_select_shader(name: str):
    global demo_shader_selection
    demo_shader_selection = name


def demo_add_item():
    global demo_trans_selection, demo_shader_selection

    if len(app.demo_gen.items) >= 10:
        return

    if demo_trans_selection or demo_shader_selection:
        app.demo_gen.add_item(demo_trans_selection, demo_shader_selection)
        demo_trans_selection = None
        demo_shader_selection = None
        refresh_demo_items_list()


def demo_clear_items():
    app.demo_gen.clear_items()
    refresh_demo_items_list()


def demo_remove_item(index: int):
    app.demo_gen.remove_item(index)
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
                callback=lambda s, a, idx=i: demo_remove_item(idx),
                width=25
            )


def demo_generate():
    output_path = os.path.join(app.game_folder, "content", "preset_demo.rpy")
    if app.demo_gen.save_script(output_path):
        print(f"Demo script saved to: {output_path}")
        dpg.delete_item("export_demo_window")
    else:
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
                with dpg.group(horizontal=True, tag="shader_builder_panel", show=False):
                    with dpg.group():
                        dpg.add_text("Preset List")
                        dpg.add_separator()
                        with dpg.child_window(tag="shader_builder_list", width=250, height=500):
                            pass
                    dpg.add_spacer(width=10)
                    with dpg.child_window(width=-1, height=500, tag="shader_builder_content"):
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
