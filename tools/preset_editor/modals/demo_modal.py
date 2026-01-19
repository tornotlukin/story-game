"""
demo_modal.py - Export Demo modal window

Allows users to build demo combinations of transitions and shaders,
then generate and run Ren'Py test scripts.
"""

import os
import subprocess
import dearpygui.dearpygui as dpg
from typing import Optional

from modules.ui_components import apply_selection_theme


# =============================================================================
# Module State
# =============================================================================

_app = None
_refresh_all = None

# Selection state for demo modal
_demo_trans_selection: Optional[str] = None
_demo_shader_selection: Optional[str] = None


def init_demo_modal(app_state, refresh_callback):
    """Initialize module with app state reference."""
    global _app, _refresh_all
    _app = app_state
    _refresh_all = refresh_callback


# =============================================================================
# Main Modal
# =============================================================================

def show_export_demo_modal():
    """Show the Export Demo modal window."""
    global _demo_trans_selection, _demo_shader_selection
    _demo_trans_selection = None
    _demo_shader_selection = None

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
        # Demo window dimensions
        dpg.add_text("Demo Window Dimensions", color=(200, 200, 100))
        with dpg.group(horizontal=True):
            dpg.add_text("Width:")
            dpg.add_input_int(
                tag="demo_width",
                default_value=_app.demo_width,
                min_value=100,
                min_clamped=True,
                width=100
            )
            dpg.add_spacer(width=20)
            dpg.add_text("Height:")
            dpg.add_input_int(
                tag="demo_height",
                default_value=_app.demo_height,
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
                    _refresh_demo_trans_list()

            # Column 2: Shaders
            with dpg.child_window(width=290, height=380):
                dpg.add_text("Shader Presets", color=(255, 200, 150))
                dpg.add_separator()
                with dpg.child_window(tag="demo_shader_list", height=-1):
                    _refresh_demo_shader_list()

            # Column 3: Demo Items
            with dpg.child_window(width=320, height=380):
                dpg.add_text("Demo Items", tag="demo_items_header", color=(150, 255, 150))
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Add Selected", callback=_demo_add_item)
                    dpg.add_button(label="Clear All", callback=_demo_clear_items)
                dpg.add_separator()
                with dpg.child_window(tag="demo_items_list", height=-1):
                    _refresh_demo_items_list()

        dpg.add_separator()

        # Status feedback area
        dpg.add_text("", tag="demo_status_text", color=(150, 150, 150))

        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Generate Demo Script",
                callback=_demo_generate,
                width=150
            )
            dpg.add_button(
                label="Run in Ren'Py",
                callback=_demo_run,
                width=120
            )
            dpg.add_spacer(width=20)
            dpg.add_button(
                label="Close",
                callback=lambda: dpg.delete_item("export_demo_window"),
                width=80
            )


# =============================================================================
# Refresh Functions
# =============================================================================

def _refresh_demo_trans_list():
    """Refresh the demo transition list."""
    if not dpg.does_item_exist("demo_trans_list"):
        return

    dpg.delete_item("demo_trans_list", children_only=True)

    for name in _app.json_mgr.get_transition_names():
        is_selected = (name == _demo_trans_selection)
        prefix = "[*] " if is_selected else "    "
        item_id = dpg.add_selectable(
            label=f"{prefix}preset_{name}",
            default_value=is_selected,
            callback=_demo_trans_select_callback,
            user_data=name,
            parent="demo_trans_list"
        )
        apply_selection_theme(item_id, is_selected)


def _refresh_demo_shader_list():
    """Refresh the demo shader list."""
    if not dpg.does_item_exist("demo_shader_list"):
        return

    dpg.delete_item("demo_shader_list", children_only=True)

    for name in _app.json_mgr.get_shader_names():
        is_selected = (name == _demo_shader_selection)
        prefix = "[*] " if is_selected else "    "
        item_id = dpg.add_selectable(
            label=f"{prefix}shader_{name}",
            default_value=is_selected,
            callback=_demo_shader_select_callback,
            user_data=name,
            parent="demo_shader_list"
        )
        apply_selection_theme(item_id, is_selected)


def _refresh_demo_items_list():
    """Refresh the demo items list."""
    if not dpg.does_item_exist("demo_items_list"):
        return

    dpg.delete_item("demo_items_list", children_only=True)

    for i, item in enumerate(_app.demo_gen.items):
        with dpg.group(horizontal=True, parent="demo_items_list"):
            dpg.add_text(f"{i+1}.", color=(100, 100, 100))
            dpg.add_text(item.display_name, color=(200, 200, 200))
            dpg.add_button(
                label="X",
                callback=_demo_remove_item_callback,
                user_data=i,
                width=25
            )


# =============================================================================
# Selection Callbacks
# =============================================================================

def _demo_trans_select_callback(sender, app_data, user_data):
    _demo_select_transition(user_data)


def _demo_select_transition(name: str):
    global _demo_trans_selection
    _demo_trans_selection = name
    if dpg.does_item_exist("demo_trans_status"):
        dpg.set_value("demo_trans_status", f"preset_{name}")
        dpg.configure_item("demo_trans_status", color=(150, 200, 255))
    _refresh_demo_trans_list()


def _demo_shader_select_callback(sender, app_data, user_data):
    _demo_select_shader(user_data)


def _demo_select_shader(name: str):
    global _demo_shader_selection
    _demo_shader_selection = name
    if dpg.does_item_exist("demo_shader_status"):
        dpg.set_value("demo_shader_status", f"shader_{name}")
        dpg.configure_item("demo_shader_status", color=(255, 200, 150))
    _refresh_demo_shader_list()


# =============================================================================
# Item Actions
# =============================================================================

def _demo_add_item():
    global _demo_trans_selection, _demo_shader_selection

    if len(_app.demo_gen.items) >= 10:
        return

    if _demo_trans_selection or _demo_shader_selection:
        _app.demo_gen.add_item(_demo_trans_selection, _demo_shader_selection)
        _demo_trans_selection = None
        _demo_shader_selection = None
        # Reset status displays
        if dpg.does_item_exist("demo_trans_status"):
            dpg.set_value("demo_trans_status", "(none)")
            dpg.configure_item("demo_trans_status", color=(100, 100, 100))
        if dpg.does_item_exist("demo_shader_status"):
            dpg.set_value("demo_shader_status", "(none)")
            dpg.configure_item("demo_shader_status", color=(100, 100, 100))
        # Update header with count
        if dpg.does_item_exist("demo_items_header"):
            dpg.set_value("demo_items_header", f"Demo Items ({len(_app.demo_gen.items)}/10)")
        # Refresh all lists
        _refresh_demo_trans_list()
        _refresh_demo_shader_list()
        _refresh_demo_items_list()


def _demo_clear_items():
    _app.demo_gen.clear_items()
    if dpg.does_item_exist("demo_items_header"):
        dpg.set_value("demo_items_header", "Demo Items (0/10)")
    _refresh_demo_items_list()


def _demo_remove_item_callback(sender, app_data, user_data):
    if user_data is not None:
        _demo_remove_item(user_data)


def _demo_remove_item(index: int):
    _app.demo_gen.remove_item(index)
    if dpg.does_item_exist("demo_items_header"):
        dpg.set_value("demo_items_header", f"Demo Items ({len(_app.demo_gen.items)}/10)")
    _refresh_demo_items_list()


# =============================================================================
# Generate/Run
# =============================================================================

def _demo_generate():
    """Generate the demo script."""
    # Get dimensions from inputs
    width = _app.demo_width
    height = _app.demo_height
    if dpg.does_item_exist("demo_width"):
        width = max(100, dpg.get_value("demo_width"))
    if dpg.does_item_exist("demo_height"):
        height = max(100, dpg.get_value("demo_height"))

    # Save dimensions to app state
    _app.demo_width = width
    _app.demo_height = height

    # Set dimensions on demo generator
    _app.demo_gen.screen_width = width
    _app.demo_gen.screen_height = height

    # Generate options.rpy
    options_path = os.path.join(_app.game_folder, "options.rpy")
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

    # Generate script.rpy
    script_path = os.path.join(_app.game_folder, "script.rpy")
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

    output_path = os.path.join(_app.game_folder, "content", "preset_demo.rpy")
    if _app.demo_gen.save_script(output_path):
        # Save config to persist dimensions
        _app.save_config()
        # Show success feedback
        if dpg.does_item_exist("demo_status_text"):
            dpg.set_value("demo_status_text", f"Success! Demo generated ({width}x{height})")
            dpg.configure_item("demo_status_text", color=(100, 255, 100))
        print(f"Demo script saved to: {output_path}")
    else:
        if dpg.does_item_exist("demo_status_text"):
            dpg.set_value("demo_status_text", "Error: Failed to save demo script")
            dpg.configure_item("demo_status_text", color=(255, 100, 100))
        print("Failed to save demo script")


def _demo_run():
    """Generate and run the demo."""
    _demo_generate()

    if _app.renpy_exe and os.path.exists(_app.renpy_exe):
        try:
            subprocess.Popen([_app.renpy_exe, _app.game_folder, "run"])
        except Exception as e:
            print(f"Failed to launch Ren'Py: {e}")
    else:
        print("Ren'Py executable not configured. Set it in Settings.")
