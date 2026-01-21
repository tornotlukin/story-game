"""
gameconfig_tab.py - Game Configuration tab UI

Provides a scrollable form for configuring baseline Ren'Py game settings.
Exports theme.rpy files for non-destructive game customization.

Sections:
- Project Info
- Screen Dimensions
- Colors
- Fonts
- Font Sizes
- Dialogue Box Layout
- Name Box Layout
- Menu Backgrounds
- Text Speed
- Window Behavior
- UI Details
- Choice Buttons
"""

import dearpygui.dearpygui as dpg
from pathlib import Path
from typing import Optional
import sys

# Add modules to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "modules"))
from gameconfig_manager import GameConfigManager
from ui_components import rgba_to_hex, hex_to_rgb, hex_to_rgba, is_valid_hex


# =============================================================================
# Module State
# =============================================================================

_app = None  # Reference to AppState
_refresh_callback = None
_config_mgr: Optional[GameConfigManager] = None


def init_gameconfig_tab(app_state, refresh_callback):
    """Initialize module with app state reference."""
    global _app, _refresh_callback, _config_mgr
    _app = app_state
    _refresh_callback = refresh_callback

    # Initialize config manager and load
    _config_mgr = GameConfigManager()
    _config_mgr.load()


# =============================================================================
# UI Setup
# =============================================================================

def setup_gameconfig_tab(parent):
    """Build the Game Config tab UI structure."""
    with dpg.tab(label="GAME CONFIG", parent=parent):
        # Top toolbar
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Export theme.rpy",
                callback=_on_export,
                width=140
            )
            dpg.add_spacer(width=20)
            dpg.add_text("Target Folder:")
            dpg.add_input_text(
                tag="gameconfig_target_folder",
                width=400,
                hint="Path to game folder (e.g., C:/MyGame/game)"
            )
            dpg.add_button(
                label="Browse...",
                callback=_on_browse_folder,
                width=80
            )

        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)

        # Scrollable form
        with dpg.child_window(tag="gameconfig_scroll", height=-1, border=False):
            _build_project_section()
            _build_screen_section()
            _build_colors_section()
            _build_fonts_section()
            _build_font_sizes_section()
            _build_dialogue_section()
            _build_namebox_section()
            _build_menu_backgrounds_section()
            _build_text_speed_section()
            _build_window_behavior_section()
            _build_ui_details_section()
            _build_choice_buttons_section()

            dpg.add_spacer(height=20)


# =============================================================================
# Section Builders
# =============================================================================

def _section_header(title: str):
    """Add a section header with separator."""
    dpg.add_spacer(height=10)
    dpg.add_separator()
    dpg.add_spacer(height=5)
    dpg.add_text(title, color=(100, 200, 255))
    dpg.add_spacer(height=5)


def _build_project_section():
    """Build the Project section."""
    _section_header("PROJECT")

    data = _config_mgr.get_project()

    with dpg.group(horizontal=True):
        dpg.add_text("Game Name:", indent=20)
        dpg.add_input_text(
            tag="gc_project_name",
            default_value=data.get("name", ""),
            width=300,
            callback=_on_value_change,
            user_data=("project", "name")
        )

    with dpg.group(horizontal=True):
        dpg.add_text("Version:", indent=20)
        dpg.add_input_text(
            tag="gc_project_version",
            default_value=data.get("version", ""),
            width=150,
            callback=_make_callback("project", "version")
        )

    with dpg.group(horizontal=True):
        dpg.add_text("Build Name:", indent=20)
        dpg.add_input_text(
            tag="gc_project_build_name",
            default_value=data.get("build_name", ""),
            width=200,
            callback=_make_callback("project", "build_name")
        )

    with dpg.group(horizontal=True):
        dpg.add_text("Save Directory:", indent=20)
        dpg.add_input_text(
            tag="gc_project_save_directory",
            default_value=data.get("save_directory", ""),
            width=250,
            callback=_make_callback("project", "save_directory")
        )


def _build_screen_section():
    """Build the Screen Dimensions section."""
    _section_header("SCREEN DIMENSIONS")

    data = _config_mgr.get_screen()

    with dpg.group(horizontal=True):
        dpg.add_text("Virtual Width:", indent=20)
        dpg.add_input_int(
            tag="gc_screen_width",
            default_value=data.get("width", 1920),
            width=100,
            min_value=320,
            max_value=7680,
            callback=_make_callback("screen", "width")
        )
        dpg.add_spacer(width=30)
        dpg.add_text("Virtual Height:")
        dpg.add_input_int(
            tag="gc_screen_height",
            default_value=data.get("height", 1080),
            width=100,
            min_value=240,
            max_value=4320,
            callback=_make_callback("screen", "height")
        )

    with dpg.group(horizontal=True):
        dpg.add_text("Physical Width:", indent=20)
        dpg.add_input_int(
            tag="gc_screen_physical_width",
            default_value=data.get("physical_width") or 0,
            width=100,
            min_value=0,
            max_value=7680,
            callback=_make_callback_nullable("screen", "physical_width")
        )
        dpg.add_spacer(width=30)
        dpg.add_text("Physical Height:")
        dpg.add_input_int(
            tag="gc_screen_physical_height",
            default_value=data.get("physical_height") or 0,
            width=100,
            min_value=0,
            max_value=4320,
            callback=_make_callback_nullable("screen", "physical_height")
        )

    dpg.add_text("(Physical = 0 means use virtual size)", indent=20, color=(128, 128, 128))


def _build_colors_section():
    """Build the Colors section with color pickers and hex inputs."""
    _section_header("COLORS")

    data = _config_mgr.get_colors()

    color_fields = [
        ("accent", "Accent Color"),
        ("hover", "Hover Color"),
        ("idle", "Idle Color"),
        ("idle_small", "Idle Small Color"),
        ("selected", "Selected Color"),
        ("insensitive", "Insensitive Color"),
        ("text", "Text Color"),
        ("interface_text", "Interface Text Color"),
        ("muted", "Muted Color"),
        ("hover_muted", "Hover Muted Color"),
    ]

    for i, (key, label) in enumerate(color_fields):
        hex_val = data.get(key, "#ffffffff")
        rgba = _hex_to_rgba_list(hex_val)

        with dpg.group(horizontal=True):
            dpg.add_text(f"{label}:", indent=20)
            dpg.add_color_edit(
                tag=f"gc_color_{key}",
                default_value=rgba,
                no_alpha=False,
                alpha_bar=True,
                width=200,
                callback=_make_color_picker_callback("colors", key)
            )
            dpg.add_input_text(
                tag=f"gc_color_{key}_hex",
                default_value=hex_val,
                width=90,
                hint="#RRGGBBAA",
                callback=_make_hex_input_callback("colors", key)
            )


def _build_fonts_section():
    """Build the Fonts section with dropdowns populated from game fonts folder."""
    _section_header("FONTS")

    data = _config_mgr.get_fonts()

    font_fields = [
        ("text", "Text Font"),
        ("name", "Name Font"),
        ("interface", "Interface Font"),
    ]

    for key, label in font_fields:
        current_val = data.get(key, "")
        # Get a fresh copy of the font list for each combo
        available_fonts = _get_available_fonts()
        with dpg.group(horizontal=True):
            dpg.add_text(f"{label}:", indent=20)
            dpg.add_combo(
                tag=f"gc_font_{key}",
                items=available_fonts,
                default_value=current_val if current_val in available_fonts else "",
                width=300,
                callback=_make_callback("fonts", key)
            )

    # Refresh button to rescan fonts folder
    with dpg.group(horizontal=True):
        dpg.add_spacer(width=20)
        dpg.add_button(
            label="Refresh Font List",
            callback=_refresh_font_dropdowns,
            width=120
        )
        dpg.add_text("(Scans game/fonts folder)", color=(128, 128, 128))


def _build_font_sizes_section():
    """Build the Font Sizes section."""
    _section_header("FONT SIZES")

    data = _config_mgr.get_font_sizes()

    size_fields = [
        ("text", "Text Size"),
        ("name", "Name Size"),
        ("interface", "Interface Size"),
        ("label", "Label Size"),
        ("notify", "Notify Size"),
        ("title", "Title Size"),
    ]

    for key, label in size_fields:
        with dpg.group(horizontal=True):
            dpg.add_text(f"{label}:", indent=20)
            dpg.add_input_int(
                tag=f"gc_fontsize_{key}",
                default_value=data.get(key, 28),
                width=80,
                min_value=8,
                max_value=200,
                callback=_on_value_change,
                user_data=("font_sizes", key)
            )


def _build_dialogue_section():
    """Build the Dialogue Box Layout section."""
    _section_header("DIALOGUE BOX LAYOUT")

    data = _config_mgr.get_dialogue()

    with dpg.group(horizontal=True):
        dpg.add_text("Textbox Height:", indent=20)
        dpg.add_input_int(
            tag="gc_dialogue_textbox_height",
            default_value=data.get("textbox_height", 278),
            width=80,
            callback=_make_callback("dialogue", "textbox_height")
        )
        dpg.add_spacer(width=30)
        dpg.add_text("Textbox Y Align:")
        dpg.add_input_float(
            tag="gc_dialogue_textbox_yalign",
            default_value=data.get("textbox_yalign", 1.0),
            width=80,
            min_value=0.0,
            max_value=1.0,
            format="%.2f",
            callback=_make_callback("dialogue", "textbox_yalign")
        )

    with dpg.group(horizontal=True):
        dpg.add_text("Text X Position:", indent=20)
        dpg.add_input_int(
            tag="gc_dialogue_text_xpos",
            default_value=data.get("text_xpos", 402),
            width=80,
            callback=_make_callback("dialogue", "text_xpos")
        )
        dpg.add_spacer(width=30)
        dpg.add_text("Text Y Position:")
        dpg.add_input_int(
            tag="gc_dialogue_text_ypos",
            default_value=data.get("text_ypos", 75),
            width=80,
            callback=_make_callback("dialogue", "text_ypos")
        )

    with dpg.group(horizontal=True):
        dpg.add_text("Text Width:", indent=20)
        dpg.add_input_int(
            tag="gc_dialogue_text_width",
            default_value=data.get("text_width", 1116),
            width=80,
            callback=_make_callback("dialogue", "text_width")
        )
        dpg.add_spacer(width=30)
        dpg.add_text("Text X Align:")
        dpg.add_input_float(
            tag="gc_dialogue_text_xalign",
            default_value=data.get("text_xalign", 0.0),
            width=80,
            min_value=0.0,
            max_value=1.0,
            format="%.2f",
            callback=_make_callback("dialogue", "text_xalign")
        )


def _build_namebox_section():
    """Build the Name Box Layout section."""
    _section_header("NAME BOX LAYOUT")

    data = _config_mgr.get_namebox()

    with dpg.group(horizontal=True):
        dpg.add_text("Name X Position:", indent=20)
        dpg.add_input_int(
            tag="gc_namebox_xpos",
            default_value=data.get("xpos", 360),
            width=80,
            callback=_make_callback("namebox", "xpos")
        )
        dpg.add_spacer(width=30)
        dpg.add_text("Name Y Position:")
        dpg.add_input_int(
            tag="gc_namebox_ypos",
            default_value=data.get("ypos", 0),
            width=80,
            callback=_make_callback("namebox", "ypos")
        )

    with dpg.group(horizontal=True):
        dpg.add_text("Name X Align:", indent=20)
        dpg.add_input_float(
            tag="gc_namebox_xalign",
            default_value=data.get("xalign", 0.0),
            width=80,
            min_value=0.0,
            max_value=1.0,
            format="%.2f",
            callback=_make_callback("namebox", "xalign")
        )

    with dpg.group(horizontal=True):
        dpg.add_text("Namebox Width:", indent=20)
        dpg.add_input_int(
            tag="gc_namebox_width",
            default_value=data.get("width") or 0,
            width=80,
            min_value=0,
            callback=_make_callback_nullable("namebox", "width")
        )
        dpg.add_spacer(width=30)
        dpg.add_text("Namebox Height:")
        dpg.add_input_int(
            tag="gc_namebox_height",
            default_value=data.get("height") or 0,
            width=80,
            min_value=0,
            callback=_make_callback_nullable("namebox", "height")
        )

    dpg.add_text("(Width/Height = 0 means None/auto)", indent=20, color=(128, 128, 128))


def _build_menu_backgrounds_section():
    """Build the Menu Backgrounds section."""
    _section_header("MENU BACKGROUNDS")

    data = _config_mgr.get_menu_backgrounds()

    with dpg.group(horizontal=True):
        dpg.add_text("Main Menu:", indent=20)
        dpg.add_input_text(
            tag="gc_menu_main_menu",
            default_value=data.get("main_menu", ""),
            width=350,
            callback=_make_callback("menu_backgrounds", "main_menu")
        )

    with dpg.group(horizontal=True):
        dpg.add_text("Game Menu:", indent=20)
        dpg.add_input_text(
            tag="gc_menu_game_menu",
            default_value=data.get("game_menu", ""),
            width=350,
            callback=_make_callback("menu_backgrounds", "game_menu")
        )


def _build_text_speed_section():
    """Build the Text Speed section."""
    _section_header("TEXT SPEED")

    data = _config_mgr.get_text_speed()

    with dpg.group(horizontal=True):
        dpg.add_text("Characters Per Second:", indent=20)
        dpg.add_input_int(
            tag="gc_textspeed_cps",
            default_value=data.get("cps", 0),
            width=80,
            min_value=0,
            max_value=500,
            callback=_make_callback("text_speed", "cps")
        )
        dpg.add_text("(0 = instant)", color=(128, 128, 128))

    with dpg.group(horizontal=True):
        dpg.add_text("Auto-Forward Time:", indent=20)
        dpg.add_input_int(
            tag="gc_textspeed_afm_time",
            default_value=data.get("afm_time", 15),
            width=80,
            min_value=0,
            max_value=60,
            callback=_make_callback("text_speed", "afm_time")
        )
        dpg.add_text("seconds", color=(128, 128, 128))


def _build_window_behavior_section():
    """Build the Window Behavior section."""
    _section_header("WINDOW BEHAVIOR")

    data = _config_mgr.get_window_behavior()

    with dpg.group(horizontal=True):
        dpg.add_text("Confirm on Quit:", indent=20)
        dpg.add_checkbox(
            tag="gc_window_quit_confirm",
            default_value=data.get("quit_confirm", True),
            callback=_make_callback("window_behavior", "quit_confirm")
        )

    with dpg.group(horizontal=True):
        dpg.add_text("Quit Message:", indent=20)

    dpg.add_input_text(
        tag="gc_window_quit_message",
        default_value=data.get("quit_message", ""),
        width=500,
        height=60,
        multiline=True,
        indent=20,
        callback=_make_callback("window_behavior", "quit_message")
    )


def _build_ui_details_section():
    """Build the UI Details section."""
    _section_header("UI DETAILS")

    data = _config_mgr.get_ui_details()

    with dpg.group(horizontal=True):
        dpg.add_text("Bar Size:", indent=20)
        dpg.add_input_int(
            tag="gc_ui_bar_size",
            default_value=data.get("bar_size", 38),
            width=80,
            min_value=1,
            callback=_make_callback("ui_details", "bar_size")
        )
        dpg.add_spacer(width=30)
        dpg.add_text("Scrollbar Size:")
        dpg.add_input_int(
            tag="gc_ui_scrollbar_size",
            default_value=data.get("scrollbar_size", 18),
            width=80,
            min_value=1,
            callback=_make_callback("ui_details", "scrollbar_size")
        )
        dpg.add_spacer(width=30)
        dpg.add_text("Slider Size:")
        dpg.add_input_int(
            tag="gc_ui_slider_size",
            default_value=data.get("slider_size", 38),
            width=80,
            min_value=1,
            callback=_make_callback("ui_details", "slider_size")
        )

    with dpg.group(horizontal=True):
        dpg.add_text("Button Width:", indent=20)
        dpg.add_input_int(
            tag="gc_ui_button_width",
            default_value=data.get("button_width") or 0,
            width=80,
            min_value=0,
            callback=_make_callback_nullable("ui_details", "button_width")
        )
        dpg.add_spacer(width=30)
        dpg.add_text("Button Height:")
        dpg.add_input_int(
            tag="gc_ui_button_height",
            default_value=data.get("button_height") or 0,
            width=80,
            min_value=0,
            callback=_make_callback_nullable("ui_details", "button_height")
        )

    dpg.add_text("(Button Width/Height = 0 means None/auto)", indent=20, color=(128, 128, 128))

    # Button colors
    dpg.add_spacer(height=5)
    dpg.add_text("Button Text Colors (optional):", indent=20)

    btn_color_fields = [
        ("button_text_idle_color", "Idle"),
        ("button_text_hover_color", "Hover"),
        ("button_text_selected_color", "Selected"),
        ("button_text_insensitive_color", "Insensitive"),
    ]

    for key, label in btn_color_fields:
        hex_val = data.get(key) or "#888888ff"
        rgba = _hex_to_rgba_list(hex_val)
        with dpg.group(horizontal=True, indent=20):
            dpg.add_text(f"{label}:")
            dpg.add_color_edit(
                tag=f"gc_ui_{key}",
                default_value=rgba,
                no_alpha=False,
                alpha_bar=True,
                width=100,
                callback=_make_color_picker_callback("ui_details", key)
            )
            dpg.add_input_text(
                tag=f"gc_ui_{key}_hex",
                default_value=hex_val,
                width=90,
                hint="#RRGGBBAA",
                callback=_make_hex_input_callback("ui_details", key)
            )


def _build_choice_buttons_section():
    """Build the Choice Buttons section."""
    _section_header("CHOICE BUTTONS")

    data = _config_mgr.get_choice_buttons()

    with dpg.group(horizontal=True):
        dpg.add_text("Choice Button Width:", indent=20)
        dpg.add_input_int(
            tag="gc_choice_width",
            default_value=data.get("width", 1185),
            width=80,
            min_value=0,
            callback=_make_callback("choice_buttons", "width")
        )
        dpg.add_spacer(width=30)
        dpg.add_text("Choice Button Height:")
        dpg.add_input_int(
            tag="gc_choice_height",
            default_value=data.get("height") or 0,
            width=80,
            min_value=0,
            callback=_make_callback_nullable("choice_buttons", "height")
        )

    with dpg.group(horizontal=True):
        dpg.add_text("Choice Spacing:", indent=20)
        dpg.add_input_int(
            tag="gc_choice_spacing",
            default_value=data.get("spacing", 33),
            width=80,
            min_value=0,
            callback=_make_callback("choice_buttons", "spacing")
        )

    dpg.add_spacer(height=5)
    dpg.add_text("Choice Button Text Colors:", indent=20)

    choice_color_fields = [
        ("text_idle_color", "Idle"),
        ("text_hover_color", "Hover"),
        ("text_insensitive_color", "Insensitive"),
    ]

    for key, label in choice_color_fields:
        hex_val = data.get(key) or "#888888ff"
        rgba = _hex_to_rgba_list(hex_val)
        with dpg.group(horizontal=True, indent=20):
            dpg.add_text(f"{label}:")
            dpg.add_color_edit(
                tag=f"gc_choice_{key}",
                default_value=rgba,
                no_alpha=False,
                alpha_bar=True,
                width=100,
                callback=_make_color_picker_callback("choice_buttons", key)
            )
            dpg.add_input_text(
                tag=f"gc_choice_{key}_hex",
                default_value=hex_val,
                width=90,
                hint="#RRGGBBAA",
                callback=_make_hex_input_callback("choice_buttons", key)
            )


# =============================================================================
# Refresh Functions
# =============================================================================

def refresh_gameconfig_tab():
    """Refresh all game config tab content from the config manager."""
    if not _config_mgr:
        return

    # Reload config from file
    _config_mgr.load()

    # Update all UI fields (would need to iterate through all tags)
    # For now, this is a placeholder - full refresh would rebuild UI
    pass


# =============================================================================
# Callbacks
# =============================================================================

def _on_value_change(sender, app_data, user_data):
    """Handle value change in any field.

    DearPyGui callback signature: (sender, app_data, user_data)
    user_data should be a tuple of (section, key)
    """
    if _config_mgr and user_data:
        section, key = user_data
        _config_mgr.set_value(section, key, app_data)


def _on_value_change_nullable(sender, app_data, user_data):
    """Handle value change where 0 means None/null.

    DearPyGui callback signature: (sender, app_data, user_data)
    user_data should be a tuple of (section, key)
    """
    if _config_mgr and user_data:
        section, key = user_data
        value = app_data if app_data > 0 else None
        _config_mgr.set_value(section, key, value)


def _make_callback(section: str, key: str):
    """Create a callback function for a specific section/key pair."""
    def callback(sender, app_data, user_data):
        if _config_mgr:
            _config_mgr.set_value(section, key, app_data)
    return callback


def _make_callback_nullable(section: str, key: str):
    """Create a callback for nullable fields (0 = None)."""
    def callback(sender, app_data, user_data):
        if _config_mgr:
            value = app_data if app_data > 0 else None
            _config_mgr.set_value(section, key, value)
    return callback


def _make_color_picker_callback(section: str, key: str):
    """Create a callback for color picker changes (with alpha support)."""
    def callback(sender, app_data, user_data):
        # Use rgba_to_hex with alpha support
        hex_color = rgba_to_hex(app_data, include_alpha=True).lower()

        # Update the corresponding hex input field
        hex_tag = _get_hex_tag_for_color(section, key)
        if hex_tag and dpg.does_item_exist(hex_tag):
            dpg.set_value(hex_tag, hex_color)

        if _config_mgr:
            _config_mgr.set_value(section, key, hex_color)
    return callback


def _make_hex_input_callback(section: str, key: str):
    """Create a callback for hex input changes."""
    def callback(sender, app_data, user_data):
        hex_value = app_data.strip()
        if not hex_value.startswith('#'):
            hex_value = '#' + hex_value

        # Only process valid hex codes
        if is_valid_hex(hex_value):
            rgb = _hex_to_rgba_list(hex_value)

            # Update the corresponding color picker
            picker_tag = _get_picker_tag_for_color(section, key)
            if picker_tag and dpg.does_item_exist(picker_tag):
                dpg.set_value(picker_tag, rgb)

            if _config_mgr:
                _config_mgr.set_value(section, key, hex_value.lower())
    return callback


def _on_color_picker_change(section: str, key: str, rgba):
    """Handle color picker change - update hex input and save (with alpha)."""
    # Use rgba_to_hex with alpha support
    hex_color = rgba_to_hex(rgba, include_alpha=True).lower()

    # Update the corresponding hex input field
    hex_tag = _get_hex_tag_for_color(section, key)
    if hex_tag and dpg.does_item_exist(hex_tag):
        dpg.set_value(hex_tag, hex_color)

    if _config_mgr:
        _config_mgr.set_value(section, key, hex_color)


def _on_hex_input_change(section: str, key: str, hex_value: str):
    """Handle hex input change - update color picker and save."""
    # Validate and normalize hex input
    hex_value = hex_value.strip()
    if not hex_value.startswith('#'):
        hex_value = '#' + hex_value

    # Only process valid hex codes
    if is_valid_hex(hex_value):
        rgb = _hex_to_rgba_list(hex_value)

        # Update the corresponding color picker
        picker_tag = _get_picker_tag_for_color(section, key)
        if picker_tag and dpg.does_item_exist(picker_tag):
            dpg.set_value(picker_tag, rgb)

        if _config_mgr:
            _config_mgr.set_value(section, key, hex_value.lower())


def _get_hex_tag_for_color(section: str, key: str) -> str:
    """Get the hex input tag for a given section and key."""
    if section == "colors":
        return f"gc_color_{key}_hex"
    elif section == "ui_details":
        return f"gc_ui_{key}_hex"
    elif section == "choice_buttons":
        return f"gc_choice_{key}_hex"
    return ""


def _get_picker_tag_for_color(section: str, key: str) -> str:
    """Get the color picker tag for a given section and key."""
    if section == "colors":
        return f"gc_color_{key}"
    elif section == "ui_details":
        return f"gc_ui_{key}"
    elif section == "choice_buttons":
        return f"gc_choice_{key}"
    return ""


def _on_export(sender=None, app_data=None, user_data=None):
    """Handle export button click."""
    if not _config_mgr:
        return

    target = ""
    if dpg.does_item_exist("gameconfig_target_folder"):
        target = dpg.get_value("gameconfig_target_folder")

    if not target:
        _show_status("Please specify a target folder", (255, 200, 100))
        return

    success = _config_mgr.export_theme_rpy(target)

    if success:
        _show_status(f"Exported theme.rpy to {target}", (100, 200, 100))
    else:
        _show_status("Export failed - check console for details", (255, 100, 100))


def _on_browse_folder(sender=None, app_data=None, user_data=None):
    """Open folder browser dialog."""
    def _on_folder_selected(sender, app_data):
        if app_data and "file_path_name" in app_data:
            folder = app_data["file_path_name"]
            if dpg.does_item_exist("gameconfig_target_folder"):
                dpg.set_value("gameconfig_target_folder", folder)

    if dpg.does_item_exist("gameconfig_folder_dialog"):
        dpg.delete_item("gameconfig_folder_dialog")

    dpg.add_file_dialog(
        tag="gameconfig_folder_dialog",
        directory_selector=True,
        show=True,
        callback=_on_folder_selected,
        width=600,
        height=400
    )


def _show_status(message: str, color=(200, 200, 200)):
    """Show status message via app status bar if available."""
    if _app and hasattr(_app, 'status_bar') and _app.status_bar:
        _app.status_bar.set_status(message, color)
    else:
        print(f"[GameConfig] {message}")


# =============================================================================
# Utilities
# =============================================================================

def _hex_to_rgba_list(hex_str: str) -> list:
    """Convert hex color string to RGBA list for DearPyGui.

    Handles both 6-digit (#RRGGBB) and 8-digit (#RRGGBBAA) hex.
    DearPyGui color widgets expect [r, g, b, a] format with 0-255 values.
    """
    rgba = hex_to_rgba(hex_str)  # Returns (r, g, b, a) tuple
    return [rgba[0], rgba[1], rgba[2], rgba[3]]


def _get_available_fonts() -> list:
    """Get list of available fonts from the game's fonts folder."""
    fonts_set = set()

    # Get game folder from app state
    if _app and hasattr(_app, 'game_folder') and _app.game_folder:
        fonts_path = Path(_app.game_folder) / "fonts"
        if fonts_path.exists():
            # Find all font files (use set to avoid duplicates on case-insensitive Windows)
            for font_file in fonts_path.iterdir():
                if font_file.suffix.lower() in ['.ttf', '.otf']:
                    fonts_set.add(font_file.name)

    # Convert to list and sort
    fonts = sorted(list(fonts_set), key=str.lower)

    # Always include DejaVuSans.ttf (Ren'Py's built-in default) at the start
    if "DejaVuSans.ttf" not in fonts:
        fonts.insert(0, "DejaVuSans.ttf")
    else:
        # Move it to the front if it exists
        fonts.remove("DejaVuSans.ttf")
        fonts.insert(0, "DejaVuSans.ttf")

    return fonts


def _refresh_font_dropdowns(sender=None, app_data=None, user_data=None):
    """Refresh font dropdown contents by rescanning the fonts folder."""
    available_fonts = _get_available_fonts()

    font_keys = ["text", "name", "interface"]
    for key in font_keys:
        tag = f"gc_font_{key}"
        if dpg.does_item_exist(tag):
            current_val = dpg.get_value(tag)
            dpg.configure_item(tag, items=available_fonts)
            # Restore selection if still valid
            if current_val in available_fonts:
                dpg.set_value(tag, current_val)

    _show_status(f"Found {len(available_fonts)} fonts", (100, 200, 100))
