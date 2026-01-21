"""
ui_components.py - Reusable Dear PyGui UI components

Provides consistent UI widgets for the preset editor.
"""

import dearpygui.dearpygui as dpg
from typing import Callable, List, Optional, Any, Tuple


# =============================================================================
# Color Utilities
# =============================================================================

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color (#RRGGBB) to RGB tuple (0-255)."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) >= 6:
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )
    return (255, 255, 255)


def hex_to_rgba(hex_color: str) -> Tuple[int, int, int, int]:
    """Convert hex color (#RRGGBB or #RRGGBBAA) to RGBA tuple (0-255).

    If no alpha is provided, defaults to 255 (fully opaque).
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) >= 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        a = int(hex_color[6:8], 16) if len(hex_color) >= 8 else 255
        return (r, g, b, a)
    return (255, 255, 255, 255)


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple (0-255) to hex color string."""
    return "#{:02X}{:02X}{:02X}".format(
        int(min(255, max(0, rgb[0]))),
        int(min(255, max(0, rgb[1]))),
        int(min(255, max(0, rgb[2])))
    )


def rgba_to_hex_with_alpha(rgba: Tuple[int, int, int, int]) -> str:
    """Convert RGBA tuple (0-255) to 8-digit hex color string (#RRGGBBAA)."""
    return "#{:02X}{:02X}{:02X}{:02X}".format(
        int(min(255, max(0, rgba[0]))),
        int(min(255, max(0, rgba[1]))),
        int(min(255, max(0, rgba[2]))),
        int(min(255, max(0, rgba[3])))
    )


def rgba_to_hex(rgba: List[float], include_alpha: bool = False) -> str:
    """Convert RGBA list to hex color string.

    DearPyGui color_edit returns values as 0.0-1.0 floats (or 0-255 ints).
    This function handles both cases by detecting the range.

    Args:
        rgba: List of [r, g, b] or [r, g, b, a] values
        include_alpha: If True, output 8-digit hex (#RRGGBBAA)

    Returns:
        Hex color string (#RRGGBB or #RRGGBBAA)
    """
    r, g, b = rgba[0], rgba[1], rgba[2]
    a = rgba[3] if len(rgba) > 3 else 1.0

    # If all RGB values are <= 1.0, assume 0.0-1.0 range and scale to 0-255
    if all(v <= 1.0 for v in [r, g, b]):
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        a = int(a * 255) if a <= 1.0 else int(a)
    else:
        r = int(r)
        g = int(g)
        b = int(b)
        a = int(a)

    if include_alpha:
        return rgba_to_hex_with_alpha((r, g, b, a))
    else:
        return rgb_to_hex((r, g, b))


def is_valid_hex(hex_str: str) -> bool:
    """Check if a string is a valid hex color (6 or 8 digit)."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) not in (6, 8):
        return False
    try:
        int(hex_str, 16)
        return True
    except ValueError:
        return False


# Track color widget pairs for syncing (color_edit_id -> hex_input_id and vice versa)
_color_widget_pairs: dict = {}


def add_color_edit_with_hex(
    label: str,
    default_value: str,
    callback: Callable[[Any, Any, Any], None],
    user_data: Any = None,
    parent: int = 0,
    color_width: int = 150,
    hex_width: int = 80,
    include_alpha: bool = False
) -> Tuple[int, int]:
    """
    Add a color edit widget with an adjacent hex input field.

    Both widgets stay in sync - editing one updates the other.

    Args:
        label: Label for the color edit (hex input uses ##hidden label)
        default_value: Initial hex color string (#RRGGBB or #RRGGBBAA)
        callback: Called when color changes. Receives (sender, hex_color_str, user_data)
        user_data: Passed to callback
        parent: Parent widget ID
        color_width: Width of color picker
        hex_width: Width of hex input field (auto-adjusted for alpha if not specified)
        include_alpha: If True, show alpha bar and output 8-digit hex

    Returns:
        Tuple of (color_edit_id, hex_input_id)
    """
    rgba = hex_to_rgba(default_value)
    hex_value = default_value if default_value.startswith('#') else f"#{default_value}"

    # Auto-adjust hex width for alpha if using default
    actual_hex_width = hex_width if hex_width != 80 else (90 if include_alpha else 80)

    # Generate unique tag base for this pair
    import time
    tag_base = f"color_pair_{int(time.time() * 1000000)}"

    group_id = dpg.add_group(horizontal=True, parent=parent)

    # Color edit widget
    color_edit_id = dpg.add_color_edit(
        label=label,
        default_value=[rgba[0], rgba[1], rgba[2], rgba[3]],
        no_alpha=not include_alpha,
        alpha_bar=include_alpha,
        width=color_width,
        parent=group_id,
        tag=f"{tag_base}_color"
    )

    # Hex input widget
    hex_input_id = dpg.add_input_text(
        label=f"##{tag_base}_hex",
        default_value=hex_value.upper(),
        width=actual_hex_width,
        hint="#RRGGBBAA" if include_alpha else "#RRGGBB",
        parent=group_id,
        tag=f"{tag_base}_hex"
    )

    # Store the pair relationship (including alpha setting)
    _color_widget_pairs[color_edit_id] = {
        'hex_input': hex_input_id,
        'callback': callback,
        'user_data': user_data,
        'include_alpha': include_alpha
    }
    _color_widget_pairs[hex_input_id] = {
        'color_edit': color_edit_id,
        'callback': callback,
        'user_data': user_data,
        'include_alpha': include_alpha
    }

    def on_color_change(sender, app_data):
        """Handle color picker change - update hex input and call user callback."""
        pair_info = _color_widget_pairs.get(sender, {})
        use_alpha = pair_info.get('include_alpha', False)
        hex_color = rgba_to_hex(app_data, include_alpha=use_alpha)
        hex_input = pair_info.get('hex_input')

        # Update hex input without triggering its callback
        if hex_input and dpg.does_item_exist(hex_input):
            dpg.set_value(hex_input, hex_color.upper())

        # Call user callback with hex string
        user_callback = pair_info.get('callback')
        if user_callback:
            user_callback(sender, hex_color.upper(), pair_info.get('user_data'))

    def on_hex_change(sender, app_data):
        """Handle hex input change - update color picker and call user callback."""
        hex_str = app_data.strip()

        # Validate and normalize
        if not hex_str.startswith('#'):
            hex_str = f"#{hex_str}"

        if not is_valid_hex(hex_str):
            return  # Invalid hex, don't update

        pair_info = _color_widget_pairs.get(sender, {})
        color_edit = pair_info.get('color_edit')

        # Update color picker (use rgba to handle both 6 and 8 digit hex)
        if color_edit and dpg.does_item_exist(color_edit):
            rgba = hex_to_rgba(hex_str)
            dpg.set_value(color_edit, [rgba[0], rgba[1], rgba[2], rgba[3]])

        # Normalize the hex input to uppercase
        dpg.set_value(sender, hex_str.upper())

        # Call user callback with hex string
        user_callback = pair_info.get('callback')
        if user_callback:
            user_callback(sender, hex_str.upper(), pair_info.get('user_data'))

    # Set callbacks
    dpg.set_item_callback(color_edit_id, on_color_change)
    dpg.set_item_callback(hex_input_id, on_hex_change)

    return color_edit_id, hex_input_id


# =============================================================================
# Preset List Item
# =============================================================================

class PresetListItem:
    """
    A list item with selection, color swatch, and action buttons.

    Layout: [checkbox] [color?] name [Top][Up][Down][Bottom] [Edit][Dupe][Del]
    """

    def __init__(
        self,
        name: str,
        parent: int,
        on_select: Callable[[str, bool], None],
        on_move: Callable[[str, str], None],
        on_edit: Callable[[str], None],
        on_duplicate: Callable[[str], None],
        on_delete: Callable[[str], None],
        color: Optional[str] = None,
        selected: bool = False,
        prefix: str = "preset_"
    ):
        self.name = name
        self.color = color
        self.selected = selected
        self.prefix = prefix

        self._on_select = on_select
        self._on_move = on_move
        self._on_edit = on_edit
        self._on_duplicate = on_duplicate
        self._on_delete = on_delete

        self._build(parent)

    def _build(self, parent: int):
        """Build the list item UI."""
        with dpg.group(horizontal=True, parent=parent):
            # Checkbox
            dpg.add_checkbox(
                default_value=self.selected,
                callback=lambda s, a: self._on_select(self.name, a)
            )

            # Color swatch (if applicable)
            if self.color:
                rgb = hex_to_rgb(self.color)
                dpg.add_color_button(
                    default_value=[rgb[0], rgb[1], rgb[2], 255],
                    width=20, height=20,
                    no_border=True
                )

            # Name
            dpg.add_text(f"{self.prefix}{self.name}", color=(200, 200, 200))

            dpg.add_spacer(width=20)

            # Move buttons
            dpg.add_button(
                label="^^",
                width=25,
                callback=lambda: self._on_move(self.name, "top")
            )
            dpg.add_button(
                label="^",
                width=25,
                callback=lambda: self._on_move(self.name, "up")
            )
            dpg.add_button(
                label="v",
                width=25,
                callback=lambda: self._on_move(self.name, "down")
            )
            dpg.add_button(
                label="vv",
                width=25,
                callback=lambda: self._on_move(self.name, "bottom")
            )

            dpg.add_spacer(width=10)

            # Action buttons
            dpg.add_button(
                label="Edit",
                width=40,
                callback=lambda: self._on_edit(self.name)
            )
            dpg.add_button(
                label="Dupe",
                width=40,
                callback=lambda: self._on_duplicate(self.name)
            )
            dpg.add_button(
                label="Del",
                width=35,
                callback=lambda: self._on_delete(self.name)
            )


# =============================================================================
# Selection Manager
# =============================================================================

class SelectionManager:
    """
    Manages multi-selection with Ctrl+click and Shift+click support.
    """

    def __init__(self, items: List[str]):
        self.items = items
        self.selected: List[str] = []
        self.last_selected: Optional[str] = None

    def update_items(self, items: List[str]):
        """Update the list of items."""
        self.items = items
        # Remove selections that no longer exist
        self.selected = [s for s in self.selected if s in items]

    def handle_click(self, name: str, ctrl: bool = False, shift: bool = False) -> List[str]:
        """
        Handle a click on an item.

        Returns the new selection list.
        """
        if shift and self.last_selected and self.last_selected in self.items:
            # Range select
            try:
                start_idx = self.items.index(self.last_selected)
                end_idx = self.items.index(name)
                if start_idx > end_idx:
                    start_idx, end_idx = end_idx, start_idx
                self.selected = self.items[start_idx:end_idx + 1]
            except ValueError:
                self.selected = [name]
        elif ctrl:
            # Toggle select
            if name in self.selected:
                self.selected.remove(name)
            else:
                self.selected.append(name)
        else:
            # Single select
            self.selected = [name]

        self.last_selected = name
        return self.selected

    def select_all(self) -> List[str]:
        """Select all items."""
        self.selected = self.items.copy()
        return self.selected

    def select_none(self) -> List[str]:
        """Clear selection."""
        self.selected = []
        return self.selected

    def invert_selection(self) -> List[str]:
        """Invert selection."""
        self.selected = [i for i in self.items if i not in self.selected]
        return self.selected

    def is_selected(self, name: str) -> bool:
        """Check if an item is selected."""
        return name in self.selected


# =============================================================================
# Popup Dialogs
# =============================================================================

def show_rename_dialog(
    title: str,
    current_name: str,
    on_confirm: Callable[[str], None],
    parent_tag: str = "primary_window"
):
    """Show a rename dialog."""
    dialog_tag = "rename_dialog"

    if dpg.does_item_exist(dialog_tag):
        dpg.delete_item(dialog_tag)

    def confirm():
        new_name = dpg.get_value("rename_input")
        if new_name and new_name != current_name:
            on_confirm(new_name)
        dpg.delete_item(dialog_tag)

    def cancel():
        dpg.delete_item(dialog_tag)

    with dpg.window(
        label=title,
        modal=True,
        width=400,
        height=120,
        pos=[400, 300],
        tag=dialog_tag,
        on_close=cancel
    ):
        dpg.add_input_text(
            default_value=current_name,
            tag="rename_input",
            width=-1,
            on_enter=True,
            callback=lambda: confirm()
        )
        dpg.add_spacer(height=10)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Rename", callback=confirm, width=100)
            dpg.add_button(label="Cancel", callback=cancel, width=100)


def show_confirm_dialog(
    title: str,
    message: str,
    on_confirm: Callable[[], None],
    on_cancel: Optional[Callable[[], None]] = None
):
    """Show a confirmation dialog."""
    dialog_tag = "confirm_dialog"

    if dpg.does_item_exist(dialog_tag):
        dpg.delete_item(dialog_tag)

    def confirm():
        on_confirm()
        dpg.delete_item(dialog_tag)

    def cancel():
        if on_cancel:
            on_cancel()
        dpg.delete_item(dialog_tag)

    with dpg.window(
        label=title,
        modal=True,
        width=400,
        height=120,
        pos=[400, 300],
        tag=dialog_tag,
        on_close=cancel
    ):
        dpg.add_text(message)
        dpg.add_spacer(height=10)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Yes", callback=confirm, width=100)
            dpg.add_button(label="No", callback=cancel, width=100)


def show_color_picker_dialog(
    title: str,
    current_color: str,
    on_change: Callable[[str], None]
):
    """Show a color picker dialog."""
    dialog_tag = "color_picker_dialog"

    if dpg.does_item_exist(dialog_tag):
        dpg.delete_item(dialog_tag)

    rgb = hex_to_rgb(current_color)

    def on_color_change(sender, app_data):
        hex_color = rgba_to_hex(app_data)
        on_change(hex_color)

    def close():
        dpg.delete_item(dialog_tag)

    with dpg.window(
        label=title,
        modal=True,
        width=320,
        height=380,
        pos=[440, 200],
        tag=dialog_tag,
        on_close=close
    ):
        dpg.add_color_picker(
            default_value=[rgb[0], rgb[1], rgb[2], 255],
            callback=on_color_change,
            no_alpha=True,
            width=300
        )
        dpg.add_spacer(height=10)
        dpg.add_button(label="Close", callback=close, width=-1)


# =============================================================================
# Status Bar
# =============================================================================

class StatusBar:
    """
    Status bar showing auto-save status, undo/redo counts, and hints.

    Layout: [Save Status] | Undo: X | Redo: Y | [Hints]
    """

    def __init__(self, parent: int):
        self.parent = parent
        self.status_text_tag = None
        self.undo_text_tag = None
        self.redo_text_tag = None

        self._build()

    def _build(self):
        """Build the status bar UI."""
        with dpg.group(horizontal=True, parent=self.parent):
            self.status_text_tag = dpg.add_text("Auto-save: ON", color=(100, 200, 100))
            dpg.add_text(" | ")
            self.undo_text_tag = dpg.add_text("Undo: 0")
            dpg.add_text(" | ")
            self.redo_text_tag = dpg.add_text("Redo: 0")
            dpg.add_text(" | ")
            dpg.add_text("Ctrl+Z: Undo | Ctrl+Y: Redo | Ctrl+Click: Multi-select",
                        color=(150, 150, 150))

    def update(self, auto_save: bool, undo_count: int, redo_count: int):
        """Update status bar values."""
        if self.status_text_tag and dpg.does_item_exist(self.status_text_tag):
            status = "Auto-save: ON" if auto_save else "Auto-save: OFF"
            color = (100, 200, 100) if auto_save else (200, 100, 100)
            dpg.set_value(self.status_text_tag, status)
            dpg.configure_item(self.status_text_tag, color=color)

        if self.undo_text_tag and dpg.does_item_exist(self.undo_text_tag):
            dpg.set_value(self.undo_text_tag, f"Undo: {undo_count}")

        if self.redo_text_tag and dpg.does_item_exist(self.redo_text_tag):
            dpg.set_value(self.redo_text_tag, f"Redo: {redo_count}")

    def set_status(self, message: str, color: tuple = (100, 200, 100)):
        """Set a custom status message."""
        if self.status_text_tag and dpg.does_item_exist(self.status_text_tag):
            dpg.set_value(self.status_text_tag, message)
            dpg.configure_item(self.status_text_tag, color=color)


# =============================================================================
# Theme Setup
# =============================================================================

# Global theme references (set after creation)
SELECTED_THEME = None
UNSELECTED_THEME = None


def create_selected_theme() -> int:
    """Create theme for selected items (blue highlight)."""
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvSelectable):
            # Bright blue background for selected items
            dpg.add_theme_color(dpg.mvThemeCol_Header, (51, 102, 204, 255))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (71, 122, 224, 255))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (91, 142, 244, 255))
    return theme


def create_unselected_theme() -> int:
    """Create theme for unselected items (default dark)."""
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvSelectable):
            dpg.add_theme_color(dpg.mvThemeCol_Header, (50, 50, 55))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (70, 70, 80))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (80, 80, 90))
    return theme


def init_selection_themes():
    """Initialize selection themes. Call after dpg.create_context()."""
    global SELECTED_THEME, UNSELECTED_THEME
    SELECTED_THEME = create_selected_theme()
    UNSELECTED_THEME = create_unselected_theme()


def apply_selection_theme(item_id: int, is_selected: bool):
    """Apply appropriate theme to a selectable item."""
    if SELECTED_THEME is None:
        return
    # Only bind selected theme - unselected items use default
    if is_selected:
        dpg.bind_item_theme(item_id, SELECTED_THEME)


def create_dark_theme() -> int:
    """Create and return the dark theme."""
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvAll):
            # Window
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30))
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (35, 35, 35))
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (40, 40, 40))

            # Frame (inputs, etc)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (50, 50, 50))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (60, 60, 60))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (70, 70, 70))

            # Buttons
            dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 60, 60))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (80, 80, 80))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (100, 100, 100))

            # Headers (tabs, collapsing headers)
            dpg.add_theme_color(dpg.mvThemeCol_Header, (60, 60, 70))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (70, 70, 80))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (80, 80, 90))

            # Tab
            dpg.add_theme_color(dpg.mvThemeCol_Tab, (50, 50, 55))
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (70, 70, 80))
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, (65, 65, 75))

            # Title
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (40, 40, 45))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (50, 50, 60))

            # Scrollbar
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (30, 30, 30))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (60, 60, 60))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (80, 80, 80))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (100, 100, 100))

            # Checkbox
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (120, 180, 255))

            # Slider
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (100, 150, 200))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (120, 180, 255))

            # Text
            dpg.add_theme_color(dpg.mvThemeCol_Text, (220, 220, 220))
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (128, 128, 128))

            # Separator
            dpg.add_theme_color(dpg.mvThemeCol_Separator, (60, 60, 60))

            # Rounding
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 4)

            # Padding
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 4)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 4)

    return theme
