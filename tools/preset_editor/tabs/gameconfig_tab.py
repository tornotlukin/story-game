"""
gameconfig_tab.py - Game Configuration tab UI (Schema-Driven)

Dynamically generates UI from game_config_schema.json.
Supports all property types: string, int, float, bool, color, font, image_path, int_or_none, borders.
"""

import dearpygui.dearpygui as dpg
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys

# Add modules to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "modules"))
from gameconfig_manager import GameConfigManager
from schema_loader import SchemaLoader
from file_modifier import GameFileModifier
from ui_components import rgba_to_hex, hex_to_rgb, hex_to_rgba, is_valid_hex


# =============================================================================
# Module State
# =============================================================================

_app = None  # Reference to AppState
_refresh_callback = None
_config_mgr: Optional[GameConfigManager] = None
_schema: Optional[SchemaLoader] = None
_file_modifier: Optional[GameFileModifier] = None
_output_messages: List[str] = []

# =============================================================================
# UI Constants
# =============================================================================

NUMBER_INPUT_WIDTH = 100  # Standard width for all number inputs


def init_gameconfig_tab(app_state, refresh_callback):
    """Initialize module with app state reference."""
    global _app, _refresh_callback, _config_mgr, _schema, _file_modifier
    _app = app_state
    _refresh_callback = refresh_callback

    # Initialize schema loader
    _schema = SchemaLoader()
    _schema.load()

    # Initialize config manager and load
    _config_mgr = GameConfigManager(_schema)
    _config_mgr.load()

    # Initialize file modifier
    _file_modifier = GameFileModifier(_schema)


# =============================================================================
# UI Setup
# =============================================================================

def setup_gameconfig_tab(parent):
    """Build the Game Config tab UI structure."""
    with dpg.tab(label="GAME CONFIG", parent=parent):
        # Top toolbar
        with dpg.group(horizontal=True):
            dpg.add_text("Target Game Folder:")
            dpg.add_input_text(
                tag="gameconfig_target_folder",
                width=450,
                hint="Path to game folder (e.g., C:/MyGame/game)"
            )
            dpg.add_button(
                label="Browse...",
                callback=_on_browse_folder,
                width=80
            )
            dpg.add_spacer(width=20)
            dpg.add_button(
                label="Edit Project",
                callback=_on_edit_project_click,
                width=120
            )

        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)

        # Scrollable form - dynamically generated from schema
        with dpg.child_window(tag="gameconfig_scroll", height=-1, border=False):
            _build_schema_sections()
            dpg.add_spacer(height=20)


def _build_schema_sections():
    """Build all category sections from schema."""
    if not _schema:
        dpg.add_text("Schema not loaded", color=(255, 100, 100))
        return

    # Get categories that have at least one property (enabled or disabled)
    for category in _schema.get_categories():
        cat_id = category["id"]
        props = _schema.get_properties_for_category(cat_id, enabled_only=False)
        if props:
            _build_category_section(category, props)


def _build_category_section(category: Dict, properties: list):
    """Build a single category section with its properties."""
    _section_header(category["label"].upper())

    for prop in properties:
        _build_property_widget(prop)


# =============================================================================
# Section Header
# =============================================================================

def _section_header(title: str):
    """Add a section header with separator."""
    dpg.add_spacer(height=10)
    dpg.add_separator()
    dpg.add_spacer(height=5)
    dpg.add_text(title, color=(100, 200, 255))
    dpg.add_spacer(height=5)


# =============================================================================
# Widget Builders by Type
# =============================================================================

def _build_property_widget(prop: Dict):
    """Build the appropriate widget for a property based on its type."""
    prop_id = prop["id"]
    prop_type = prop.get("type", "string")
    enabled = prop.get("enabled", True)
    label = prop.get("label", prop_id)
    description = prop.get("description", "")

    # Get current value from config
    value = _get_value(prop_id)
    if value is None:
        value = prop.get("default")

    # Widget tag for referencing later
    tag = f"gc_{prop_id.replace('.', '_')}"

    # Build based on type
    if prop_type == "string":
        _build_string_widget(prop, tag, value, enabled)
    elif prop_type == "int":
        _build_int_widget(prop, tag, value, enabled)
    elif prop_type == "float":
        _build_float_widget(prop, tag, value, enabled)
    elif prop_type == "bool":
        _build_bool_widget(prop, tag, value, enabled)
    elif prop_type == "color":
        _build_color_widget(prop, tag, value, enabled)
    elif prop_type == "font":
        _build_font_widget(prop, tag, value, enabled)
    elif prop_type == "image_path":
        _build_image_path_widget(prop, tag, value, enabled)
    elif prop_type == "int_or_none":
        _build_int_or_none_widget(prop, tag, value, enabled)
    elif prop_type == "borders":
        _build_borders_widget(prop, tag, value, enabled)
    elif prop_type == "color_or_ref":
        _build_color_or_ref_widget(prop, tag, value, enabled)
    elif prop_type == "multiline_string":
        _build_multiline_string_widget(prop, tag, value, enabled)
    elif prop_type == "transition":
        _build_string_widget(prop, tag, value, enabled)  # Treat as string for now
    else:
        # Fallback to string
        _build_string_widget(prop, tag, value, enabled)


def _build_string_widget(prop: Dict, tag: str, value: Any, enabled: bool):
    """Build a string input widget."""
    with dpg.group(horizontal=True):
        _add_label(prop, enabled)
        dpg.add_input_text(
            tag=tag,
            default_value=str(value) if value else "",
            width=300,
            enabled=enabled,
            callback=_make_callback(prop["id"])
        )
        _add_disabled_indicator(enabled)


def _build_multiline_string_widget(prop: Dict, tag: str, value: Any, enabled: bool):
    """Build a multiline string input widget."""
    with dpg.group(horizontal=True):
        _add_label(prop, enabled)

    dpg.add_input_text(
        tag=tag,
        default_value=str(value) if value else "",
        width=500,
        height=80,
        multiline=True,
        enabled=enabled,
        indent=20,
        callback=_make_callback(prop["id"])
    )
    _add_disabled_indicator(enabled)


def _build_int_widget(prop: Dict, tag: str, value: Any, enabled: bool):
    """Build an integer input widget."""
    validation = prop.get("validation", {})
    min_val = validation.get("min", -999999)
    max_val = validation.get("max", 999999)

    with dpg.group(horizontal=True):
        _add_label(prop, enabled)
        dpg.add_input_int(
            tag=tag,
            default_value=int(value) if value is not None else 0,
            width=NUMBER_INPUT_WIDTH,
            min_value=min_val,
            max_value=max_val,
            enabled=enabled,
            callback=_make_callback(prop["id"])
        )
        _add_disabled_indicator(enabled)


def _build_float_widget(prop: Dict, tag: str, value: Any, enabled: bool):
    """Build a float input widget."""
    validation = prop.get("validation", {})
    min_val = validation.get("min", -999999.0)
    max_val = validation.get("max", 999999.0)

    with dpg.group(horizontal=True):
        _add_label(prop, enabled)
        dpg.add_input_float(
            tag=tag,
            default_value=float(value) if value is not None else 0.0,
            width=NUMBER_INPUT_WIDTH,
            min_value=min_val,
            max_value=max_val,
            format="%.2f",
            enabled=enabled,
            callback=_make_callback(prop["id"])
        )
        _add_disabled_indicator(enabled)


def _build_bool_widget(prop: Dict, tag: str, value: Any, enabled: bool):
    """Build a boolean checkbox widget."""
    with dpg.group(horizontal=True):
        _add_label(prop, enabled)
        dpg.add_checkbox(
            tag=tag,
            default_value=bool(value) if value is not None else False,
            enabled=enabled,
            callback=_make_callback(prop["id"])
        )
        _add_disabled_indicator(enabled)


def _build_color_widget(prop: Dict, tag: str, value: Any, enabled: bool):
    """Build a color picker with hex input."""
    hex_val = str(value) if value else "#ffffffff"
    # Ensure we have a valid hex
    if not hex_val.startswith("#"):
        hex_val = "#" + hex_val
    rgba = _hex_to_rgba_list(hex_val)

    with dpg.group(horizontal=True):
        _add_label(prop, enabled)
        dpg.add_color_edit(
            tag=tag,
            default_value=rgba,
            no_alpha=not prop.get("supports_alpha", True),
            alpha_bar=prop.get("supports_alpha", True),
            width=200,
            enabled=enabled,
            callback=_make_color_picker_callback(prop["id"])
        )
        dpg.add_input_text(
            tag=f"{tag}_hex",
            default_value=hex_val,
            width=90,
            hint="#RRGGBBAA",
            enabled=enabled,
            callback=_make_hex_input_callback(prop["id"])
        )
        _add_disabled_indicator(enabled)


def _build_color_or_ref_widget(prop: Dict, tag: str, value: Any, enabled: bool):
    """Build a color widget that can also accept variable references."""
    str_val = str(value) if value else ""

    # If it's a reference (doesn't start with #), show as text input
    if str_val and not str_val.startswith("#"):
        with dpg.group(horizontal=True):
            _add_label(prop, enabled)
            dpg.add_input_text(
                tag=tag,
                default_value=str_val,
                width=200,
                enabled=enabled,
                callback=_make_callback(prop["id"])
            )
            dpg.add_text("(reference)", color=(128, 128, 128))
            _add_disabled_indicator(enabled)
    else:
        # It's a color, use color widget
        _build_color_widget(prop, tag, value, enabled)


def _build_font_widget(prop: Dict, tag: str, value: Any, enabled: bool):
    """Build a font dropdown widget."""
    available_fonts = _get_available_fonts()
    current_val = str(value) if value else ""

    with dpg.group(horizontal=True):
        _add_label(prop, enabled)
        dpg.add_combo(
            tag=tag,
            items=available_fonts,
            default_value=current_val if current_val in available_fonts else "",
            width=300,
            enabled=enabled,
            callback=_make_callback(prop["id"])
        )
        _add_disabled_indicator(enabled)


def _build_image_path_widget(prop: Dict, tag: str, value: Any, enabled: bool):
    """Build an image path input widget."""
    with dpg.group(horizontal=True):
        _add_label(prop, enabled)
        dpg.add_input_text(
            tag=tag,
            default_value=str(value) if value else "",
            width=350,
            enabled=enabled,
            callback=_make_callback(prop["id"])
        )
        _add_disabled_indicator(enabled)


def _build_int_or_none_widget(prop: Dict, tag: str, value: Any, enabled: bool):
    """Build an integer widget where 0 means None/null."""
    display_val = int(value) if value is not None else 0

    with dpg.group(horizontal=True):
        _add_label(prop, enabled)
        dpg.add_input_int(
            tag=tag,
            default_value=display_val,
            width=NUMBER_INPUT_WIDTH,
            min_value=0,
            enabled=enabled,
            callback=_make_callback_nullable(prop["id"])
        )
        dpg.add_text("(0 = auto/None)", color=(128, 128, 128))
        _add_disabled_indicator(enabled)


def _build_borders_widget(prop: Dict, tag: str, value: Any, enabled: bool):
    """Build a borders widget (4 integer inputs)."""
    borders = value if isinstance(value, list) and len(value) == 4 else [0, 0, 0, 0]

    with dpg.group(horizontal=True):
        _add_label(prop, enabled)
        dpg.add_text("L:")
        dpg.add_input_int(
            tag=f"{tag}_0",
            default_value=borders[0],
            width=NUMBER_INPUT_WIDTH,
            enabled=enabled,
            callback=_make_borders_callback(prop["id"], 0)
        )
        dpg.add_text("T:")
        dpg.add_input_int(
            tag=f"{tag}_1",
            default_value=borders[1],
            width=NUMBER_INPUT_WIDTH,
            enabled=enabled,
            callback=_make_borders_callback(prop["id"], 1)
        )
        dpg.add_text("R:")
        dpg.add_input_int(
            tag=f"{tag}_2",
            default_value=borders[2],
            width=NUMBER_INPUT_WIDTH,
            enabled=enabled,
            callback=_make_borders_callback(prop["id"], 2)
        )
        dpg.add_text("B:")
        dpg.add_input_int(
            tag=f"{tag}_3",
            default_value=borders[3],
            width=NUMBER_INPUT_WIDTH,
            enabled=enabled,
            callback=_make_borders_callback(prop["id"], 3)
        )
        _add_disabled_indicator(enabled)


# =============================================================================
# UI Helpers
# =============================================================================

def _add_label(prop: Dict, enabled: bool):
    """Add a property label with appropriate styling."""
    label = prop.get("label", prop["id"])
    color = (200, 200, 200) if enabled else (128, 128, 128)
    dpg.add_text(f"{label}:", indent=20, color=color)


def _add_disabled_indicator(enabled: bool):
    """Add 'coming soon' indicator for disabled properties."""
    if not enabled:
        dpg.add_text("(coming soon)", color=(100, 100, 100))


# =============================================================================
# Value Getters/Setters
# =============================================================================

def _get_value(prop_id: str) -> Any:
    """Get value from config manager by property ID."""
    if _config_mgr:
        return _config_mgr.get_value_by_id(prop_id)
    return None


def _set_value(prop_id: str, value: Any):
    """Set value in config manager by property ID."""
    if _config_mgr:
        _config_mgr.set_value_by_id(prop_id, value)


# =============================================================================
# Callbacks - Factory Functions
# =============================================================================

def _make_callback(prop_id: str):
    """Create a callback function for a property."""
    def callback(sender, app_data, user_data):
        _set_value(prop_id, app_data)
    return callback


def _make_callback_nullable(prop_id: str):
    """Create a callback for nullable fields (0 = None)."""
    def callback(sender, app_data, user_data):
        value = app_data if app_data > 0 else None
        _set_value(prop_id, value)
    return callback


def _make_color_picker_callback(prop_id: str):
    """Create a callback for color picker changes (with alpha support)."""
    def callback(sender, app_data, user_data):
        hex_color = rgba_to_hex(app_data, include_alpha=True).lower()

        # Update the corresponding hex input field
        tag = f"gc_{prop_id.replace('.', '_')}_hex"
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, hex_color)

        _set_value(prop_id, hex_color)
    return callback


def _make_hex_input_callback(prop_id: str):
    """Create a callback for hex input changes."""
    def callback(sender, app_data, user_data):
        hex_value = app_data.strip()
        if not hex_value.startswith('#'):
            hex_value = '#' + hex_value

        if is_valid_hex(hex_value):
            rgb = _hex_to_rgba_list(hex_value)

            # Update the corresponding color picker
            tag = f"gc_{prop_id.replace('.', '_')}"
            if dpg.does_item_exist(tag):
                dpg.set_value(tag, rgb)

            _set_value(prop_id, hex_value.lower())
    return callback


def _make_borders_callback(prop_id: str, index: int):
    """Create a callback for borders input (one of 4 values)."""
    def callback(sender, app_data, user_data):
        # Get current borders value
        current = _get_value(prop_id)
        if not isinstance(current, list) or len(current) != 4:
            current = [0, 0, 0, 0]
        else:
            current = list(current)  # Make a copy

        current[index] = app_data
        _set_value(prop_id, current)
    return callback


# =============================================================================
# Toolbar Callbacks
# =============================================================================

def _on_edit_project_click(sender=None, app_data=None, user_data=None):
    """Handle Edit Project button click - show confirmation modal."""
    target = ""
    if dpg.does_item_exist("gameconfig_target_folder"):
        target = dpg.get_value("gameconfig_target_folder")

    if not target:
        _show_status("Please specify a target game folder", (255, 200, 100))
        return

    # Validate folder
    if _file_modifier:
        is_valid, message = _file_modifier.validate_folder(target)
        if not is_valid:
            _show_status(f"Invalid folder: {message}", (255, 100, 100))
            return

    # Show confirmation modal
    _show_confirm_edit_modal(target)


def _show_confirm_edit_modal(target_folder: str):
    """Show confirmation modal before editing project files."""
    if dpg.does_item_exist("confirm_edit_modal"):
        dpg.delete_item("confirm_edit_modal")

    with dpg.window(
        label="Confirm Edit Project",
        modal=True,
        width=500,
        height=180,
        pos=[300, 200],
        tag="confirm_edit_modal",
        on_close=lambda: dpg.delete_item("confirm_edit_modal")
    ):
        dpg.add_text("Are you sure you want to edit this project?")
        dpg.add_spacer(height=5)
        dpg.add_text(f"Target: {target_folder}", color=(150, 150, 150))
        dpg.add_spacer(height=10)
        dpg.add_text("This will modify gui.rpy and options.rpy directly.", color=(255, 200, 100))
        dpg.add_text("Only properties that exist in the files will be changed.", color=(150, 150, 150))
        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Yes, Edit Project",
                callback=lambda: _do_edit_project(target_folder),
                width=140
            )
            dpg.add_spacer(width=20)
            dpg.add_button(
                label="Cancel",
                callback=lambda: dpg.delete_item("confirm_edit_modal"),
                width=100
            )


def _do_edit_project(target_folder: str):
    """Actually perform the project edit."""
    global _output_messages

    # Close the modal
    if dpg.does_item_exist("confirm_edit_modal"):
        dpg.delete_item("confirm_edit_modal")

    if not _file_modifier or not _config_mgr:
        _show_status("Editor not initialized", (255, 100, 100))
        return

    # Get all values from config
    values = _config_mgr.get_all_values()

    # Apply modifications
    result = _file_modifier.modify_project(target_folder, values)

    # Store messages for output window
    _output_messages = result.messages

    # Show result
    if result.success:
        _show_status(
            f"Project edited: {result.modified_count} modified, {result.skipped_count} skipped",
            (100, 200, 100)
        )
    else:
        _show_status(
            f"Edit failed - check Output window for details",
            (255, 100, 100)
        )

    # Show output window with results
    show_output_window()


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
# Output Window
# =============================================================================

def show_output_window():
    """Show the output window with modification results."""
    global _output_messages

    if dpg.does_item_exist("output_window"):
        dpg.delete_item("output_window")

    with dpg.window(
        label="Output",
        width=600,
        height=400,
        pos=[250, 150],
        tag="output_window",
        on_close=lambda: dpg.delete_item("output_window")
    ):
        dpg.add_text("Game Config Edit Results", color=(100, 200, 255))
        dpg.add_separator()
        dpg.add_spacer(height=5)

        # Scrollable output area
        with dpg.child_window(height=-40, border=True):
            if _output_messages:
                for msg in _output_messages:
                    # Color code messages
                    if msg.startswith("ERROR"):
                        color = (255, 100, 100)
                    elif msg.startswith("SKIP"):
                        color = (255, 200, 100)
                    elif "Modified:" in msg:
                        color = (100, 255, 100)
                    elif "Complete:" in msg:
                        color = (100, 200, 255)
                    else:
                        color = (200, 200, 200)
                    dpg.add_text(msg, color=color)
            else:
                dpg.add_text("No output messages.", color=(150, 150, 150))

        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Close",
                callback=lambda: dpg.delete_item("output_window"),
                width=80
            )
            dpg.add_spacer(width=10)
            dpg.add_button(
                label="Copy to Clipboard",
                callback=_copy_output_to_clipboard,
                width=130
            )


def _copy_output_to_clipboard():
    """Copy output messages to clipboard."""
    if _output_messages:
        text = "\n".join(_output_messages)
        dpg.set_clipboard_text(text)
        _show_status("Output copied to clipboard", (100, 200, 100))


def get_output_messages() -> List[str]:
    """Get the current output messages (for external access)."""
    return _output_messages


# =============================================================================
# Refresh Functions
# =============================================================================

def refresh_gameconfig_tab():
    """Refresh all game config tab content from the config manager."""
    if not _config_mgr or not _schema:
        return

    # Reload config from file
    _config_mgr.load()

    # Update all UI fields from schema
    for prop in _schema.get_all_properties():
        _refresh_property_widget(prop)


def _refresh_property_widget(prop: Dict):
    """Refresh a single property widget with current value."""
    prop_id = prop["id"]
    prop_type = prop.get("type", "string")
    tag = f"gc_{prop_id.replace('.', '_')}"

    if not dpg.does_item_exist(tag):
        return

    value = _get_value(prop_id)
    if value is None:
        value = prop.get("default")

    # Update based on type
    if prop_type in ["string", "image_path", "transition", "multiline_string"]:
        dpg.set_value(tag, str(value) if value else "")
    elif prop_type == "int":
        dpg.set_value(tag, int(value) if value is not None else 0)
    elif prop_type == "float":
        dpg.set_value(tag, float(value) if value is not None else 0.0)
    elif prop_type == "bool":
        dpg.set_value(tag, bool(value) if value is not None else False)
    elif prop_type in ["color", "color_or_ref"]:
        if value and str(value).startswith("#"):
            rgba = _hex_to_rgba_list(str(value))
            dpg.set_value(tag, rgba)
            if dpg.does_item_exist(f"{tag}_hex"):
                dpg.set_value(f"{tag}_hex", str(value))
    elif prop_type == "font":
        dpg.set_value(tag, str(value) if value else "")
    elif prop_type == "int_or_none":
        dpg.set_value(tag, int(value) if value is not None else 0)
    elif prop_type == "borders":
        if isinstance(value, list) and len(value) == 4:
            for i in range(4):
                if dpg.does_item_exist(f"{tag}_{i}"):
                    dpg.set_value(f"{tag}_{i}", value[i])


# =============================================================================
# Utilities
# =============================================================================

def _hex_to_rgba_list(hex_str: str) -> list:
    """Convert hex color string to RGBA list for DearPyGui."""
    rgba = hex_to_rgba(hex_str)
    return [rgba[0], rgba[1], rgba[2], rgba[3]]


def _get_available_fonts() -> list:
    """Get list of available fonts from the game's fonts folder."""
    fonts_set = set()

    # Get game folder from app state
    if _app and hasattr(_app, 'game_folder') and _app.game_folder:
        fonts_path = Path(_app.game_folder) / "fonts"
        if fonts_path.exists():
            for font_file in fonts_path.iterdir():
                if font_file.suffix.lower() in ['.ttf', '.otf']:
                    fonts_set.add(font_file.name)

    fonts = sorted(list(fonts_set), key=str.lower)

    # Always include DejaVuSans.ttf at the start
    if "DejaVuSans.ttf" not in fonts:
        fonts.insert(0, "DejaVuSans.ttf")
    else:
        fonts.remove("DejaVuSans.ttf")
        fonts.insert(0, "DejaVuSans.ttf")

    return fonts
