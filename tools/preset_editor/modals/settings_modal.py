"""
settings_modal.py - Settings modal window

Allows users to configure file paths for the preset editor.
"""

import os
import dearpygui.dearpygui as dpg


# =============================================================================
# Module State
# =============================================================================

_app = None
_refresh_all = None


def init_settings_modal(app_state, refresh_callback):
    """Initialize module with app state reference."""
    global _app, _refresh_all
    _app = app_state
    _refresh_all = refresh_callback


# =============================================================================
# Main Modal
# =============================================================================

def show_settings_modal():
    """Show settings modal with current app values."""
    _show_settings_modal_with_values(
        _app.transition_presets_path,
        _app.shader_presets_path,
        _app.shader_folder,
        _app.game_folder,
        _app.renpy_exe
    )


def _show_settings_modal_with_values(trans_path, shader_path, shader_folder, game_folder, renpy_exe):
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
            dpg.add_button(
                label="Browse...",
                callback=lambda: _settings_browse_file("settings_trans_path"),
                width=80
            )
        dpg.add_spacer(height=5)

        dpg.add_text("Shader Presets JSON:")
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                default_value=shader_path,
                tag="settings_shader_path",
                width=500
            )
            dpg.add_button(
                label="Browse...",
                callback=lambda: _settings_browse_file("settings_shader_path"),
                width=80
            )
        dpg.add_spacer(height=5)

        dpg.add_text("Shader .rpy Folder:")
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                default_value=shader_folder,
                tag="settings_shader_folder",
                width=500
            )
            dpg.add_button(
                label="Browse...",
                callback=lambda: _settings_browse_folder("settings_shader_folder"),
                width=80
            )
        dpg.add_spacer(height=5)

        dpg.add_text("Game Folder:")
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                default_value=game_folder,
                tag="settings_game_folder",
                width=500
            )
            dpg.add_button(
                label="Browse...",
                callback=lambda: _settings_browse_folder("settings_game_folder"),
                width=80
            )
        dpg.add_spacer(height=5)

        dpg.add_text("Ren'Py Executable:")
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                default_value=renpy_exe,
                tag="settings_renpy_exe",
                width=500
            )
            dpg.add_button(
                label="Browse...",
                callback=lambda: _settings_browse_exe("settings_renpy_exe"),
                width=80
            )

        dpg.add_spacer(height=10)
        dpg.add_separator()
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Apply", callback=_settings_apply, width=100)
            dpg.add_button(
                label="Cancel",
                callback=lambda: dpg.delete_item("settings_window"),
                width=100
            )


# =============================================================================
# File/Folder Browsers
# =============================================================================

def _settings_browse_file(target_tag: str):
    """Open file browser and set result to target input."""
    current_values = _get_current_values(target_tag)

    def callback(sender, app_data):
        selected_path = None
        if app_data and "file_path_name" in app_data:
            selected_path = app_data["file_path_name"]
        dpg.delete_item("file_dialog")
        _reopen_settings_with_values(current_values, selected_path)

    def cancel_callback(sender, app_data):
        dpg.delete_item("file_dialog")
        _reopen_settings_with_values(current_values, None)

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


def _settings_browse_exe(target_tag: str):
    """Open executable browser."""
    current_values = _get_current_values(target_tag)

    def callback(sender, app_data):
        selected_path = None
        if app_data and "file_path_name" in app_data:
            selected_path = app_data["file_path_name"]
        dpg.delete_item("exe_dialog")
        _reopen_settings_with_values(current_values, selected_path)

    def cancel_callback(sender, app_data):
        dpg.delete_item("exe_dialog")
        _reopen_settings_with_values(current_values, None)

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


def _settings_browse_folder(target_tag: str):
    """Open folder browser."""
    current_values = _get_current_values(target_tag)

    def callback(sender, app_data):
        selected_path = None
        if app_data and "file_path_name" in app_data:
            selected_path = app_data["file_path_name"]
        dpg.delete_item("folder_dialog")
        _reopen_settings_with_values(current_values, selected_path)

    def cancel_callback(sender, app_data):
        dpg.delete_item("folder_dialog")
        _reopen_settings_with_values(current_values, None)

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


# =============================================================================
# Helpers
# =============================================================================

def _get_current_values(target_tag: str) -> dict:
    """Get current values from settings inputs."""
    return {
        "trans": dpg.get_value("settings_trans_path"),
        "shader": dpg.get_value("settings_shader_path"),
        "shader_folder": dpg.get_value("settings_shader_folder"),
        "game_folder": dpg.get_value("settings_game_folder"),
        "renpy_exe": dpg.get_value("settings_renpy_exe"),
        "target": target_tag
    }


def _reopen_settings_with_values(values: dict, new_path: str):
    """Reopen settings modal with preserved values."""
    target = values["target"]

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

    _show_settings_modal_with_values(
        values["trans"],
        values["shader"],
        values["shader_folder"],
        values["game_folder"],
        values["renpy_exe"]
    )


def _settings_apply():
    """Apply settings and reload data."""
    _app.transition_presets_path = dpg.get_value("settings_trans_path")
    _app.shader_presets_path = dpg.get_value("settings_shader_path")
    _app.shader_folder = dpg.get_value("settings_shader_folder")
    _app.game_folder = dpg.get_value("settings_game_folder")
    _app.renpy_exe = dpg.get_value("settings_renpy_exe")

    if _app.save_config():
        if _app.status_bar:
            _app.status_bar.set_status("Settings saved successfully", (100, 200, 100))
    else:
        if _app.status_bar:
            _app.status_bar.set_status("Error saving settings!", (255, 100, 100))

    _app.load_data()
    if _refresh_all:
        _refresh_all()

    dpg.delete_item("settings_window")
