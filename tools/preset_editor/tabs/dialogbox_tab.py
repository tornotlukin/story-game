"""
dialogbox_tab.py - Dialog Box Maker tab UI

Allows users to configure Frame-based dialog boxes with:
- PNG image selection
- 9-slice border configuration
- Positioning and sizing properties
- Live preview with border overlay
- Code output in multiple formats
"""

import dearpygui.dearpygui as dpg
from pathlib import Path
import subprocess
import sys

# Add modules to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "modules"))
from dialogbox_generator import DialogBoxGenerator, DialogBoxConfig


# =============================================================================
# Module State
# =============================================================================

_app = None
_refresh_callback = None
_generator: DialogBoxGenerator = None
_config: DialogBoxConfig = None
_loaded_texture_tag = None
_loaded_image_width = 0
_loaded_image_height = 0

# =============================================================================
# UI Constants (matching gameconfig_tab.py)
# =============================================================================

NUMBER_INPUT_WIDTH = 100
TEXT_INPUT_WIDTH = 300
PREVIEW_SIZE = 300


# =============================================================================
# Initialization
# =============================================================================

def init_dialogbox_tab(app_state, refresh_callback):
    """Initialize module with app state reference."""
    global _app, _refresh_callback, _generator, _config
    _app = app_state
    _refresh_callback = refresh_callback
    _generator = DialogBoxGenerator()
    _config = DialogBoxConfig()


# =============================================================================
# UI Setup
# =============================================================================

def setup_dialogbox_tab(parent):
    """Build the Dialog Box Maker tab UI structure."""
    with dpg.tab(label="DIALOG BOX", parent=parent):

        # Style Name
        _section_header("STYLE NAME")
        with dpg.group(horizontal=True):
            dpg.add_text("Style:", indent=20)
            dpg.add_input_text(
                tag="dialogbox_style_name",
                default_value="window",
                width=TEXT_INPUT_WIDTH,
                callback=_on_style_name_changed
            )
            dpg.add_text('(use "window" to override default)', color=(128, 128, 128))

        dpg.add_spacer(height=10)

        # Image Source
        _section_header("IMAGE SOURCE")
        with dpg.group(horizontal=True):
            dpg.add_text("Path:", indent=20)
            dpg.add_input_text(
                tag="dialogbox_image_path",
                width=TEXT_INPUT_WIDTH,
                hint="gui/textbox.png",
                callback=_on_image_path_changed
            )
            dpg.add_button(
                label="Browse...",
                callback=_on_browse_image,
                width=80
            )

        dpg.add_spacer(height=10)

        # Two-column layout: Controls | Preview
        with dpg.group(horizontal=True):

            # Left column: Controls
            with dpg.child_window(width=320, height=400, border=False):

                # Frame Borders
                _section_header("FRAME BORDERS (9-SLICE)")

                with dpg.group(horizontal=True):
                    dpg.add_text("Left:", indent=20)
                    dpg.add_input_int(
                        tag="dialogbox_border_left",
                        default_value=0,
                        width=NUMBER_INPUT_WIDTH,
                        min_value=0,
                        callback=_on_border_changed
                    )

                with dpg.group(horizontal=True):
                    dpg.add_text("Top:", indent=20)
                    dpg.add_input_int(
                        tag="dialogbox_border_top",
                        default_value=0,
                        width=NUMBER_INPUT_WIDTH,
                        min_value=0,
                        callback=_on_border_changed
                    )

                with dpg.group(horizontal=True):
                    dpg.add_text("Right:", indent=20)
                    dpg.add_input_int(
                        tag="dialogbox_border_right",
                        default_value=0,
                        width=NUMBER_INPUT_WIDTH,
                        min_value=0,
                        callback=_on_border_changed
                    )

                with dpg.group(horizontal=True):
                    dpg.add_text("Bottom:", indent=20)
                    dpg.add_input_int(
                        tag="dialogbox_border_bottom",
                        default_value=0,
                        width=NUMBER_INPUT_WIDTH,
                        min_value=0,
                        callback=_on_border_changed
                    )

                with dpg.group(horizontal=True):
                    dpg.add_text("", indent=20)
                    dpg.add_checkbox(
                        tag="dialogbox_tile",
                        label="Tile instead of stretch",
                        default_value=False,
                        callback=_on_tile_changed
                    )

                dpg.add_spacer(height=10)

                # Positioning
                _section_header("POSITIONING")

                with dpg.group(horizontal=True):
                    dpg.add_text("X Align:", indent=20)
                    dpg.add_input_float(
                        tag="dialogbox_xalign",
                        default_value=0.5,
                        width=NUMBER_INPUT_WIDTH,
                        min_value=0.0,
                        max_value=1.0,
                        format="%.2f",
                        callback=_on_position_changed
                    )
                    dpg.add_text("(0=left, 0.5=center, 1=right)", color=(128, 128, 128))

                with dpg.group(horizontal=True):
                    dpg.add_text("Y Align:", indent=20)
                    dpg.add_input_float(
                        tag="dialogbox_yalign",
                        default_value=1.0,
                        width=NUMBER_INPUT_WIDTH,
                        min_value=0.0,
                        max_value=1.0,
                        format="%.2f",
                        callback=_on_position_changed
                    )
                    dpg.add_text("(0=top, 0.5=center, 1=bottom)", color=(128, 128, 128))

                dpg.add_spacer(height=10)

                # Sizing
                _section_header("SIZING")

                with dpg.group(horizontal=True):
                    dpg.add_text("Width:", indent=20)
                    dpg.add_input_int(
                        tag="dialogbox_xsize",
                        default_value=0,
                        width=NUMBER_INPUT_WIDTH,
                        min_value=0,
                        callback=_on_size_changed
                    )
                    dpg.add_text("(0 = auto)", color=(128, 128, 128))

                with dpg.group(horizontal=True):
                    dpg.add_text("Height:", indent=20)
                    dpg.add_input_int(
                        tag="dialogbox_ysize",
                        default_value=185,
                        width=NUMBER_INPUT_WIDTH,
                        min_value=0,
                        callback=_on_size_changed
                    )

                with dpg.group(horizontal=True):
                    dpg.add_text("", indent=20)
                    dpg.add_checkbox(
                        tag="dialogbox_xfill",
                        label="Fill horizontal (xfill)",
                        default_value=True,
                        callback=_on_size_changed
                    )

            # Right column: Preview
            with dpg.child_window(width=-1, height=400, border=False):
                dpg.add_text("9-SLICE PREVIEW", color=(100, 200, 255))
                dpg.add_separator()
                dpg.add_spacer(height=5)

                # Preview area with drawlist - extra space for measurement labels
                with dpg.drawlist(
                    tag="dialogbox_preview_drawlist",
                    width=PREVIEW_SIZE + 60,
                    height=PREVIEW_SIZE + 40
                ):
                    pass  # Will draw dynamically

                dpg.add_spacer(height=10)
                dpg.add_button(
                    label="Preview in Ren'Py",
                    callback=_on_preview_renpy,
                    width=150
                )

        dpg.add_spacer(height=10)
        dpg.add_separator()
        dpg.add_spacer(height=10)

        # Code Output
        with dpg.group(horizontal=True):
            dpg.add_text("CODE OUTPUT", color=(100, 200, 255))
            dpg.add_spacer(width=200)
            dpg.add_text("Format:")
            dpg.add_combo(
                tag="dialogbox_output_format",
                items=["Inline (Frame only)", "Style Block (background)", "Full Style (all properties)"],
                default_value="Full Style (all properties)",
                width=200,
                callback=_on_format_changed
            )

        dpg.add_spacer(height=5)

        dpg.add_input_text(
            tag="dialogbox_code_output",
            multiline=True,
            readonly=True,
            width=-1,
            height=120
        )

        dpg.add_spacer(height=5)

        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Copy to Clipboard",
                callback=_on_copy_code,
                width=130
            )

        # Initial code generation
        _update_code_output()
        _update_preview()


# =============================================================================
# UI Helpers
# =============================================================================

def _section_header(title: str):
    """Add a section header."""
    dpg.add_spacer(height=5)
    dpg.add_text(title, color=(100, 200, 255))
    dpg.add_spacer(height=5)


# =============================================================================
# Callbacks
# =============================================================================

def _on_style_name_changed(sender, app_data, user_data):
    """Handle style name change."""
    _config.style_name = app_data
    _update_code_output()


def _on_image_path_changed(sender, app_data, user_data):
    """Handle image path change."""
    _config.image_path = app_data
    _update_code_output()
    _update_preview()


def _on_browse_image(sender, app_data, user_data):
    """Open file browser for image selection."""
    def _on_file_selected(sender, app_data):
        if app_data and "file_path_name" in app_data:
            file_path = app_data["file_path_name"]
            dpg.set_value("dialogbox_image_path", file_path)
            _config.image_path = file_path
            _update_code_output()
            _update_preview()

    if dpg.does_item_exist("dialogbox_file_dialog"):
        dpg.delete_item("dialogbox_file_dialog")

    with dpg.file_dialog(
        tag="dialogbox_file_dialog",
        directory_selector=False,
        show=True,
        callback=_on_file_selected,
        width=600,
        height=400,
        default_path=str(Path(_app.game_folder) / "gui") if _app and _app.game_folder else ""
    ):
        # Ren'Py compatible image formats
        dpg.add_file_extension(".png", color=(0, 255, 0, 255))
        dpg.add_file_extension(".PNG", color=(0, 255, 0, 255))
        dpg.add_file_extension(".jpg", color=(0, 200, 255, 255))
        dpg.add_file_extension(".JPG", color=(0, 200, 255, 255))
        dpg.add_file_extension(".jpeg", color=(0, 200, 255, 255))
        dpg.add_file_extension(".JPEG", color=(0, 200, 255, 255))
        dpg.add_file_extension(".webp", color=(255, 200, 0, 255))
        dpg.add_file_extension(".WEBP", color=(255, 200, 0, 255))
        dpg.add_file_extension(".gif", color=(255, 100, 255, 255))
        dpg.add_file_extension(".GIF", color=(255, 100, 255, 255))
        dpg.add_file_extension(".bmp", color=(200, 200, 200, 255))
        dpg.add_file_extension(".BMP", color=(200, 200, 200, 255))
        dpg.add_file_extension(".avif", color=(255, 150, 100, 255))
        dpg.add_file_extension(".AVIF", color=(255, 150, 100, 255))
        dpg.add_file_extension(".*", color=(150, 150, 150, 255))  # All files


def _on_border_changed(sender, app_data, user_data):
    """Handle border value change."""
    _config.border_left = dpg.get_value("dialogbox_border_left")
    _config.border_top = dpg.get_value("dialogbox_border_top")
    _config.border_right = dpg.get_value("dialogbox_border_right")
    _config.border_bottom = dpg.get_value("dialogbox_border_bottom")
    _update_code_output()
    _update_preview()


def _on_tile_changed(sender, app_data, user_data):
    """Handle tile checkbox change."""
    _config.tile = app_data
    _update_code_output()


def _on_position_changed(sender, app_data, user_data):
    """Handle positioning change."""
    _config.xalign = dpg.get_value("dialogbox_xalign")
    _config.yalign = dpg.get_value("dialogbox_yalign")
    _update_code_output()


def _on_size_changed(sender, app_data, user_data):
    """Handle sizing change."""
    _config.xsize = dpg.get_value("dialogbox_xsize")
    _config.ysize = dpg.get_value("dialogbox_ysize")
    _config.xfill = dpg.get_value("dialogbox_xfill")
    _update_code_output()


def _on_format_changed(sender, app_data, user_data):
    """Handle output format change."""
    _update_code_output()


def _on_copy_code(sender, app_data, user_data):
    """Copy code to clipboard."""
    code = dpg.get_value("dialogbox_code_output")
    dpg.set_clipboard_text(code)
    _show_status("Code copied to clipboard", (100, 200, 100))


def _on_preview_renpy(sender, app_data, user_data):
    """Launch Ren'Py preview."""
    if not _app or not _app.game_folder:
        _show_status("No game folder configured", (255, 200, 100))
        return

    # Write demo script
    game_folder = str(Path(__file__).parent.parent / "game")
    if _generator.write_demo_script(_config, game_folder):
        _launch_renpy_demo()
    else:
        _show_status("Failed to write demo script", (255, 100, 100))


def _launch_renpy_demo():
    """Launch Ren'Py with the demo."""
    if not _app or not _app.renpy_exe:
        _show_status("Ren'Py executable not configured", (255, 200, 100))
        return

    try:
        game_folder = str(Path(__file__).parent.parent / "game")
        cmd = [_app.renpy_exe, game_folder, "--lint", "dialogbox_demo"]

        # On Windows, use shell=True to avoid console window
        if sys.platform == "win32":
            subprocess.Popen(
                [_app.renpy_exe, game_folder],
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        else:
            subprocess.Popen([_app.renpy_exe, game_folder])

        _show_status("Launched Ren'Py preview", (100, 200, 100))

    except Exception as e:
        _show_status(f"Failed to launch Ren'Py: {e}", (255, 100, 100))


# =============================================================================
# Code Generation
# =============================================================================

def _update_code_output():
    """Update the code output text based on current config and format."""
    format_value = dpg.get_value("dialogbox_output_format") if dpg.does_item_exist("dialogbox_output_format") else "Full Style (all properties)"

    # Map display name to format type
    if "Inline" in format_value:
        format_type = "inline"
    elif "background" in format_value:
        format_type = "background"
    else:
        format_type = "full"

    code = _generator.generate_code(_config, format_type)

    if dpg.does_item_exist("dialogbox_code_output"):
        dpg.set_value("dialogbox_code_output", code)


# =============================================================================
# Preview Drawing
# =============================================================================

def _update_preview():
    """Update the 9-slice preview with current image and borders."""
    global _loaded_texture_tag

    if not dpg.does_item_exist("dialogbox_preview_drawlist"):
        return

    # Clear previous drawings
    dpg.delete_item("dialogbox_preview_drawlist", children_only=True)

    # Draw background (only for the image area, leave room for labels)
    dpg.draw_rectangle(
        parent="dialogbox_preview_drawlist",
        pmin=[0, 0],
        pmax=[PREVIEW_SIZE, PREVIEW_SIZE],
        fill=[30, 30, 30, 255]
    )

    # Try to load and display the image
    image_path = _config.image_path
    if image_path and Path(image_path).exists():
        try:
            _draw_image_with_borders(image_path)
        except Exception as e:
            print(f"[DialogBox] Error loading image: {e}")
            _draw_placeholder_with_borders()
    else:
        _draw_placeholder_with_borders()


def _draw_placeholder_with_borders():
    """Draw a placeholder rectangle with 9-slice border indicators."""
    # Placeholder box
    margin = 20
    box_size = PREVIEW_SIZE - 2 * margin

    # Draw placeholder background
    dpg.draw_rectangle(
        parent="dialogbox_preview_drawlist",
        pmin=[margin, margin],
        pmax=[margin + box_size, margin + box_size],
        fill=[60, 60, 60, 255],
        color=[100, 100, 100, 255],
        thickness=2
    )

    # Draw 9-slice grid
    _draw_9slice_grid(margin, margin, box_size, box_size)


def _draw_image_with_borders(image_path: str):
    """Draw the actual image with 9-slice border overlay."""
    global _loaded_texture_tag, _loaded_image_width, _loaded_image_height

    margin = 20
    max_size = PREVIEW_SIZE - 2 * margin

    # Clean up old texture
    if _loaded_texture_tag and dpg.does_item_exist(_loaded_texture_tag):
        dpg.delete_item(_loaded_texture_tag)
        _loaded_texture_tag = None

    # Create texture registry if needed
    if not dpg.does_item_exist("dialogbox_texture_registry"):
        dpg.add_texture_registry(tag="dialogbox_texture_registry")

    # Load image
    try:
        width, height, channels, data = dpg.load_image(image_path)
        if width == 0 or height == 0:
            raise ValueError("Failed to load image")

        # Store original dimensions for border scaling
        _loaded_image_width = width
        _loaded_image_height = height

        # Create texture
        _loaded_texture_tag = dpg.add_static_texture(
            width=width,
            height=height,
            default_value=data,
            parent="dialogbox_texture_registry"
        )

        # Calculate scaled dimensions to fit preview (maintain aspect ratio)
        aspect = width / height
        if aspect > 1:  # Wider than tall
            display_width = max_size
            display_height = max_size / aspect
        else:  # Taller than wide
            display_height = max_size
            display_width = max_size * aspect

        # Center the image
        x_offset = margin + (max_size - display_width) / 2
        y_offset = margin + (max_size - display_height) / 2

        # Draw the image
        dpg.draw_image(
            _loaded_texture_tag,
            parent="dialogbox_preview_drawlist",
            pmin=[x_offset, y_offset],
            pmax=[x_offset + display_width, y_offset + display_height]
        )

        # Draw 9-slice grid scaled to the displayed image size
        _draw_9slice_grid(x_offset, y_offset, display_width, display_height,
                         original_width=width, original_height=height)

    except Exception as e:
        print(f"[DialogBox] Error loading image texture: {e}")
        # Fall back to placeholder
        dpg.draw_rectangle(
            parent="dialogbox_preview_drawlist",
            pmin=[margin, margin],
            pmax=[margin + max_size, margin + max_size],
            fill=[80, 60, 60, 255],
            color=[150, 100, 100, 255],
            thickness=2
        )
        dpg.draw_text(
            parent="dialogbox_preview_drawlist",
            pos=[margin + 10, margin + max_size / 2 - 10],
            text=f"Error: {Path(image_path).name}",
            size=14,
            color=[255, 100, 100, 255]
        )
        _draw_9slice_grid(margin, margin, max_size, max_size)


def _draw_9slice_grid(x: float, y: float, width: float, height: float,
                      original_width: int = 0, original_height: int = 0):
    """Draw the 9-slice grid lines with measurements."""
    # Get border values
    left = _config.border_left
    top = _config.border_top
    right = _config.border_right
    bottom = _config.border_bottom

    # Scale borders based on actual image dimensions if available
    if original_width > 0 and original_height > 0:
        scale_x = width / original_width
        scale_y = height / original_height
        scaled_left = min(left * scale_x, width / 3)
        scaled_top = min(top * scale_y, height / 3)
        scaled_right = min(right * scale_x, width / 3)
        scaled_bottom = min(bottom * scale_y, height / 3)
    else:
        # Fallback: assume 200x200 reference size
        scale = min(width / 200, height / 200)
        scaled_left = min(left * scale, width / 3)
        scaled_top = min(top * scale, height / 3)
        scaled_right = min(right * scale, width / 3)
        scaled_bottom = min(bottom * scale, height / 3)

    # Line color
    line_color = [255, 200, 0, 200]
    text_color = [255, 255, 0, 255]

    # Vertical lines (left and right borders)
    if scaled_left > 0:
        dpg.draw_line(
            parent="dialogbox_preview_drawlist",
            p1=[x + scaled_left, y],
            p2=[x + scaled_left, y + height],
            color=line_color,
            thickness=2
        )
        dpg.draw_text(
            parent="dialogbox_preview_drawlist",
            pos=[x + 2, y + height + 5],
            text=f"{left}px",
            size=12,
            color=text_color
        )

    if scaled_right > 0:
        dpg.draw_line(
            parent="dialogbox_preview_drawlist",
            p1=[x + width - scaled_right, y],
            p2=[x + width - scaled_right, y + height],
            color=line_color,
            thickness=2
        )
        dpg.draw_text(
            parent="dialogbox_preview_drawlist",
            pos=[x + width - scaled_right + 2, y + height + 5],
            text=f"{right}px",
            size=12,
            color=text_color
        )

    # Horizontal lines (top and bottom borders)
    if scaled_top > 0:
        dpg.draw_line(
            parent="dialogbox_preview_drawlist",
            p1=[x, y + scaled_top],
            p2=[x + width, y + scaled_top],
            color=line_color,
            thickness=2
        )
        dpg.draw_text(
            parent="dialogbox_preview_drawlist",
            pos=[x + width + 5, y + 2],
            text=f"{top}px",
            size=12,
            color=text_color
        )

    if scaled_bottom > 0:
        dpg.draw_line(
            parent="dialogbox_preview_drawlist",
            p1=[x, y + height - scaled_bottom],
            p2=[x + width, y + height - scaled_bottom],
            color=line_color,
            thickness=2
        )
        dpg.draw_text(
            parent="dialogbox_preview_drawlist",
            pos=[x + width + 5, y + height - scaled_bottom - 12],
            text=f"{bottom}px",
            size=12,
            color=text_color
        )

    # Draw "CENTER" label if there's a center region
    if (scaled_left + scaled_right < width) and (scaled_top + scaled_bottom < height):
        center_x = x + scaled_left + (width - scaled_left - scaled_right) / 2 - 25
        center_y = y + scaled_top + (height - scaled_top - scaled_bottom) / 2 - 8
        dpg.draw_text(
            parent="dialogbox_preview_drawlist",
            pos=[center_x, center_y],
            text="CENTER",
            size=14,
            color=[150, 150, 150, 255]
        )
        dpg.draw_text(
            parent="dialogbox_preview_drawlist",
            pos=[center_x - 5, center_y + 16],
            text="(stretches)",
            size=11,
            color=[100, 100, 100, 255]
        )


# =============================================================================
# Status
# =============================================================================

def _show_status(message: str, color=(200, 200, 200)):
    """Show status message."""
    if _app and hasattr(_app, 'status_bar') and _app.status_bar:
        _app.status_bar.set_status(message, color)
    else:
        print(f"[DialogBox] {message}")


# =============================================================================
# Refresh
# =============================================================================

def refresh_dialogbox_tab():
    """Refresh the dialog box tab (called on app refresh)."""
    _update_code_output()
    _update_preview()
