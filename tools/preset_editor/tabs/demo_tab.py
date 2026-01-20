"""
demo_tab.py - Demo export tab UI

Handles the Demo tab for testing preset combinations:
- Three preset columns: Transitions, Shaders, Text Shaders
- Demo Items column for queued combinations
- Generate and Run in Ren'Py functionality

Three testing modes (mutually exclusive checkboxes):
- Both OFF: Character/Image testing (transitions + shaders on character)
- Apply to text ON: Shader on black rect dialog + text shader on text
- Apply to dialog ON: Shader on dialog artwork + text shader on text
"""

import dearpygui.dearpygui as dpg
import subprocess
import os
from pathlib import Path
from typing import List, Optional

from modules.ui_components import apply_selection_theme
from modules.demo_generator import DemoItem


# =============================================================================
# Module State (set by init_demo_tab)
# =============================================================================

_app = None  # Reference to AppState
_refresh_all = None  # Callback to refresh all UI
_initialized = False  # Track if already initialized

# Local selection state for the three columns
_trans_selected: List[str] = []
_shader_selected: List[str] = []
_textshader_selected: List[str] = []


def init_demo_tab(app_state, refresh_callback):
    """Initialize module with app state reference."""
    global _app, _refresh_all, _initialized
    _app = app_state
    _refresh_all = refresh_callback

    # Register for data change notifications to refresh demo lists
    # when presets are edited in other tabs (only register once)
    if not _initialized:
        _app.json_mgr.on_change(_on_data_change)
        _initialized = True


def _on_data_change():
    """Callback when JSON data changes - refresh demo preset lists."""
    _refresh_trans_list()
    _refresh_shader_list()
    _refresh_textshader_list()


# =============================================================================
# UI Setup
# =============================================================================

def setup_demo_tab(parent):
    """Build the Demo tab UI structure."""
    with dpg.tab(label="DEMO", parent=parent):
        # Top toolbar
        with dpg.group():
            # Demo size row
            with dpg.group(horizontal=True):
                dpg.add_text("Demo Size:")
                dpg.add_spacer(width=10)
                dpg.add_text("Width")
                dpg.add_input_int(
                    tag="demo_width_input",
                    default_value=1080,
                    width=90,
                    min_value=320,
                    max_value=3840,
                    callback=_on_demo_size_change
                )
                dpg.add_spacer(width=20)
                dpg.add_text("Height")
                dpg.add_input_int(
                    tag="demo_height_input",
                    default_value=1920,
                    width=90,
                    min_value=240,
                    max_value=2160,
                    callback=_on_demo_size_change
                )

            dpg.add_spacer(height=5)

            # Mode checkboxes row (mutually exclusive)
            with dpg.group(horizontal=True):
                dpg.add_checkbox(
                    label="Apply to text",
                    tag="demo_apply_to_text",
                    default_value=False,
                    callback=_on_apply_to_text_change
                )
                dpg.add_spacer(width=20)
                dpg.add_checkbox(
                    label="Apply to dialog",
                    tag="demo_apply_to_dialog",
                    default_value=False,
                    callback=_on_apply_to_dialog_change
                )
                dpg.add_spacer(width=30)
                dpg.add_text("Sample Text:")
                dpg.add_input_text(
                    tag="demo_sample_text",
                    default_value="Sample dialogue text for testing presets.",
                    width=400,
                    callback=_on_sample_text_change
                )

        dpg.add_separator()
        dpg.add_spacer(height=5)

        # Four columns layout
        with dpg.group(horizontal=True):
            # Column 1: Transitions
            with dpg.group():
                dpg.add_text("TRANSITIONS")
                dpg.add_separator()
                with dpg.child_window(tag="demo_trans_list", width=250, height=400):
                    pass

            dpg.add_spacer(width=10)

            # Column 2: Shaders
            with dpg.group():
                dpg.add_text("SHADERS")
                dpg.add_separator()
                with dpg.child_window(tag="demo_shader_list", width=250, height=400):
                    pass

            dpg.add_spacer(width=10)

            # Column 3: Text Shaders
            with dpg.group():
                dpg.add_text("TEXT SHADERS")
                dpg.add_separator()
                with dpg.child_window(tag="demo_textshader_list", width=250, height=400):
                    pass

            dpg.add_spacer(width=10)

            # Column 4: Demo Items
            with dpg.group():
                dpg.add_text("DEMO ITEMS")
                dpg.add_separator()
                with dpg.child_window(tag="demo_items_list", width=300, height=360):
                    pass
                dpg.add_spacer(height=5)
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Add Selected",
                        callback=_add_selected,
                        width=100
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(
                        label="Clear All",
                        callback=_clear_all,
                        width=70
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(
                        label="Create Demo",
                        callback=_create_demo,
                        width=90
                    )


# =============================================================================
# Refresh Functions
# =============================================================================

def refresh_demo_tab():
    """Refresh all demo tab content."""
    _refresh_trans_list()
    _refresh_shader_list()
    _refresh_textshader_list()
    _refresh_demo_items()
    _sync_ui_from_app()


def _sync_ui_from_app():
    """Sync UI elements from app state."""
    if dpg.does_item_exist("demo_width_input"):
        dpg.set_value("demo_width_input", _app.demo_width)
    if dpg.does_item_exist("demo_height_input"):
        dpg.set_value("demo_height_input", _app.demo_height)
    if dpg.does_item_exist("demo_sample_text"):
        dpg.set_value("demo_sample_text", _app.demo_gen.sample_text)
    if dpg.does_item_exist("demo_apply_to_text"):
        dpg.set_value("demo_apply_to_text", _app.demo_gen.apply_to_text)
    if dpg.does_item_exist("demo_apply_to_dialog"):
        dpg.set_value("demo_apply_to_dialog", _app.demo_gen.apply_to_dialog)


def _refresh_trans_list():
    """Refresh the transitions column."""
    global _trans_selected

    if not dpg.does_item_exist("demo_trans_list"):
        return

    dpg.delete_item("demo_trans_list", children_only=True)

    names = _app.json_mgr.get_transition_names()

    for name in names:
        is_selected = name in _trans_selected
        prefix = "[*] " if is_selected else "    "
        item_id = dpg.add_selectable(
            label=f"{prefix}{name}",
            default_value=is_selected,
            callback=_on_trans_select,
            user_data=name,
            width=230,
            parent="demo_trans_list"
        )
        apply_selection_theme(item_id, is_selected)


def _refresh_shader_list():
    """Refresh the shaders column."""
    global _shader_selected

    if not dpg.does_item_exist("demo_shader_list"):
        return

    dpg.delete_item("demo_shader_list", children_only=True)

    names = _app.json_mgr.get_shader_names()

    for name in names:
        is_selected = name in _shader_selected
        prefix = "[*] " if is_selected else "    "
        item_id = dpg.add_selectable(
            label=f"{prefix}{name}",
            default_value=is_selected,
            callback=_on_shader_select,
            user_data=name,
            width=230,
            parent="demo_shader_list"
        )
        apply_selection_theme(item_id, is_selected)


def _refresh_textshader_list():
    """Refresh the text shaders column."""
    global _textshader_selected

    if not dpg.does_item_exist("demo_textshader_list"):
        return

    dpg.delete_item("demo_textshader_list", children_only=True)

    # Text shaders are enabled when EITHER checkbox is checked
    # Both modes support text shaders on dialogue text
    text_shaders_enabled = _app.demo_gen.apply_to_text or _app.demo_gen.apply_to_dialog

    if not text_shaders_enabled:
        # Show disabled message when in character mode
        dpg.add_text("(Enable 'Apply to text'", parent="demo_textshader_list",
                    color=(128, 128, 128))
        dpg.add_text(" or 'Apply to dialog'", parent="demo_textshader_list",
                    color=(128, 128, 128))
        dpg.add_text(" to use text shaders)", parent="demo_textshader_list",
                    color=(128, 128, 128))
        dpg.add_separator(parent="demo_textshader_list")

    names = _app.json_mgr.get_textshader_names()

    for name in names:
        is_selected = name in _textshader_selected
        prefix = "[*] " if is_selected else "    "

        if text_shaders_enabled:
            # Normal interactive mode
            item_id = dpg.add_selectable(
                label=f"{prefix}{name}",
                default_value=is_selected,
                callback=_on_textshader_select,
                user_data=name,
                width=230,
                parent="demo_textshader_list"
            )
            apply_selection_theme(item_id, is_selected)
        else:
            # Grayed out display-only mode
            dpg.add_text(
                f"    {name}",
                parent="demo_textshader_list",
                color=(100, 100, 100)
            )


def _refresh_demo_items():
    """Refresh the demo items column."""
    if not dpg.does_item_exist("demo_items_list"):
        return

    dpg.delete_item("demo_items_list", children_only=True)

    items = _app.demo_gen.items

    if not items:
        dpg.add_text("No demo items yet.", parent="demo_items_list")
        dpg.add_text("Select presets from the", parent="demo_items_list")
        dpg.add_text("columns and click 'Add Selected'", parent="demo_items_list")
        return

    for i, item in enumerate(items):
        with dpg.group(horizontal=True, parent="demo_items_list"):
            dpg.add_text(f"{i+1}.")
            dpg.add_text(item.display_name, wrap=250)
            dpg.add_button(
                label="X",
                callback=_remove_demo_item,
                user_data=i,
                width=20
            )

        if i < len(items) - 1:
            dpg.add_separator(parent="demo_items_list")


# =============================================================================
# Selection Callbacks
# =============================================================================

def _on_trans_select(sender, app_data, user_data):
    """Handle transition selection."""
    global _trans_selected
    name = user_data

    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)

    if ctrl:
        if name in _trans_selected:
            _trans_selected.remove(name)
        else:
            _trans_selected.append(name)
    else:
        if name in _trans_selected:
            _trans_selected = []
        else:
            _trans_selected = [name]

    _refresh_trans_list()


def _on_shader_select(sender, app_data, user_data):
    """Handle shader selection."""
    global _shader_selected
    name = user_data

    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)

    if ctrl:
        if name in _shader_selected:
            _shader_selected.remove(name)
        else:
            _shader_selected.append(name)
    else:
        if name in _shader_selected:
            _shader_selected = []
        else:
            _shader_selected = [name]

    _refresh_shader_list()


def _on_textshader_select(sender, app_data, user_data):
    """Handle text shader selection."""
    global _textshader_selected
    name = user_data

    ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)

    if ctrl:
        if name in _textshader_selected:
            _textshader_selected.remove(name)
        else:
            _textshader_selected.append(name)
    else:
        if name in _textshader_selected:
            _textshader_selected = []
        else:
            _textshader_selected = [name]

    _refresh_textshader_list()


# =============================================================================
# Demo Item Actions
# =============================================================================

def _add_selected(sender=None, app_data=None, user_data=None):
    """Add selected presets from all columns as a demo item."""
    global _trans_selected, _shader_selected, _textshader_selected

    # Get first selected from each column (or None)
    trans = _trans_selected[0] if _trans_selected else None
    shader = _shader_selected[0] if _shader_selected else None

    # Only include text shader when either text/dialog mode is enabled
    text_shaders_enabled = _app.demo_gen.apply_to_text or _app.demo_gen.apply_to_dialog
    textshader = None
    if text_shaders_enabled and _textshader_selected:
        textshader = _textshader_selected[0]

    if not trans and not shader and not textshader:
        if _app.status_bar:
            _app.status_bar.set_status("No presets selected", (255, 200, 100))
        return

    success = _app.demo_gen.add_item(
        transition=trans,
        shader=shader,
        text_shader=textshader
    )

    if success:
        # Clear selections after adding
        _trans_selected = []
        _shader_selected = []
        _textshader_selected = []

        refresh_demo_tab()

        if _app.status_bar:
            _app.status_bar.set_status("Demo item added", (100, 200, 100))
    else:
        if _app.status_bar:
            _app.status_bar.set_status(
                f"Max {_app.demo_gen.MAX_ITEMS} items reached",
                (255, 100, 100)
            )


def _remove_demo_item(sender, app_data, user_data):
    """Remove a demo item by index."""
    index = user_data
    _app.demo_gen.remove_item(index)
    _refresh_demo_items()


def _clear_all(sender=None, app_data=None, user_data=None):
    """Clear all demo items."""
    _app.demo_gen.clear_items()
    _refresh_demo_items()

    if _app.status_bar:
        _app.status_bar.set_status("Demo items cleared", (100, 200, 100))


# =============================================================================
# Settings Callbacks
# =============================================================================

def _on_demo_size_change(sender, app_data, user_data=None):
    """Handle demo size change."""
    if dpg.does_item_exist("demo_width_input"):
        _app.demo_width = dpg.get_value("demo_width_input")
        _app.demo_gen.screen_width = _app.demo_width

    if dpg.does_item_exist("demo_height_input"):
        _app.demo_height = dpg.get_value("demo_height_input")
        _app.demo_gen.screen_height = _app.demo_height


def _on_apply_to_text_change(sender, app_data, user_data=None):
    """Handle apply to text checkbox change.

    Mutually exclusive with apply_to_dialog - only one can be on at a time.
    """
    global _textshader_selected
    _app.demo_gen.apply_to_text = app_data

    # If turning on, turn off the other checkbox
    if app_data and _app.demo_gen.apply_to_dialog:
        _app.demo_gen.apply_to_dialog = False
        if dpg.does_item_exist("demo_apply_to_dialog"):
            dpg.set_value("demo_apply_to_dialog", False)

    # Clear text shader selection when both are off
    if not _app.demo_gen.apply_to_text and not _app.demo_gen.apply_to_dialog:
        _textshader_selected = []

    # Refresh text shader list to show enabled/disabled state
    _refresh_textshader_list()


def _on_apply_to_dialog_change(sender, app_data, user_data=None):
    """Handle apply to dialog checkbox change.

    Mutually exclusive with apply_to_text - only one can be on at a time.
    """
    global _textshader_selected
    _app.demo_gen.apply_to_dialog = app_data

    # If turning on, turn off the other checkbox
    if app_data and _app.demo_gen.apply_to_text:
        _app.demo_gen.apply_to_text = False
        if dpg.does_item_exist("demo_apply_to_text"):
            dpg.set_value("demo_apply_to_text", False)

    # Clear text shader selection when both are off
    if not _app.demo_gen.apply_to_text and not _app.demo_gen.apply_to_dialog:
        _textshader_selected = []

    # Refresh text shader list to show enabled/disabled state
    _refresh_textshader_list()


def _on_sample_text_change(sender, app_data, user_data=None):
    """Handle sample text change."""
    _app.demo_gen.sample_text = app_data


# =============================================================================
# Generate & Run
# =============================================================================

def _generate_demo(sender=None, app_data=None, user_data=None):
    """Generate the demo script."""
    if not _app.demo_gen.items:
        if _app.status_bar:
            _app.status_bar.set_status("No demo items to generate", (255, 200, 100))
        return

    # Generate to game folder
    if not _app.game_folder:
        if _app.status_bar:
            _app.status_bar.set_status("Game folder not configured", (255, 100, 100))
        return

    output_path = Path(_app.game_folder) / "preset_demo.rpy"
    success = _app.demo_gen.save_script(str(output_path))

    if success:
        if _app.status_bar:
            _app.status_bar.set_status(f"Demo saved: {output_path}", (100, 200, 100))
    else:
        if _app.status_bar:
            _app.status_bar.set_status("Error generating demo", (255, 100, 100))


def _clean_compiled_files():
    """Remove all .rpyc files from the game folder for a fresh start."""
    if not _app.game_folder:
        return 0

    game_path = Path(_app.game_folder)
    count = 0

    # Find and delete all .rpyc files recursively
    for rpyc_file in game_path.rglob("*.rpyc"):
        try:
            rpyc_file.unlink()
            count += 1
        except Exception as e:
            print(f"Could not delete {rpyc_file}: {e}")

    # Also clear cache folder if it exists
    cache_path = game_path / "cache"
    if cache_path.exists():
        import shutil
        try:
            shutil.rmtree(cache_path)
        except Exception as e:
            print(f"Could not delete cache folder: {e}")

    return count


def _create_demo(sender=None, app_data=None, user_data=None):
    """Generate the demo script and run it in Ren'Py."""
    # First generate
    _generate_demo()

    if not _app.demo_gen.items:
        return

    # Then run
    if not _app.renpy_exe or not os.path.exists(_app.renpy_exe):
        if _app.status_bar:
            _app.status_bar.set_status("Ren'Py executable not configured", (255, 100, 100))
        return

    if not _app.game_folder:
        if _app.status_bar:
            _app.status_bar.set_status("Game folder not configured", (255, 100, 100))
        return

    # Clean all .rpyc files for fresh compile
    cleaned = _clean_compiled_files()

    # Get parent of game folder (project root)
    project_root = str(Path(_app.game_folder).parent)

    try:
        subprocess.Popen([_app.renpy_exe, project_root])
        if _app.status_bar:
            _app.status_bar.set_status(f"Launching Ren'Py... (cleaned {cleaned} .rpyc files)", (100, 200, 100))
    except Exception as e:
        if _app.status_bar:
            _app.status_bar.set_status(f"Error launching Ren'Py: {e}", (255, 100, 100))
