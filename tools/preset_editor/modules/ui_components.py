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


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple (0-255) to hex color string."""
    return "#{:02X}{:02X}{:02X}".format(
        int(min(255, max(0, rgb[0]))),
        int(min(255, max(0, rgb[1]))),
        int(min(255, max(0, rgb[2])))
    )


def rgba_to_hex(rgba: List[float]) -> str:
    """Convert RGBA list (0-255) to hex color string."""
    return rgb_to_hex((int(rgba[0]), int(rgba[1]), int(rgba[2])))


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
