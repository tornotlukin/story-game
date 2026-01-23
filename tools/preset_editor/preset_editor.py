#!/usr/bin/env python3
"""
Preset Editor - Dear PyGui tool for managing Ren'Py preset JSON files

Features:
- Five tabs: Transitions, Shaders, Text Shaders, Demo, Game Config
- Three modes per preset tab: Builder, Manager, JSON
- Demo tab for testing preset combinations
- Game Config tab for baseline Ren'Py settings (exports theme.rpy)
- Shader .rpy file parsing
- Live JSON updates with undo/redo
- Multi-select (Ctrl+click, Shift+click)

Usage:
    python preset_editor.py
"""

import dearpygui.dearpygui as dpg
import json
import os
from pathlib import Path
from enum import Enum
from typing import Optional

# Import our core modules
from modules.json_manager import JsonManager
from modules.shader_parser import ShaderParser, TextShaderParser
from modules.demo_generator import DemoGenerator
from modules.ui_components import (
    create_dark_theme, StatusBar, SelectionManager,
    init_selection_themes
)

# Import tab modules
from tabs import (
    init_transition_tab, setup_transition_tab,
    refresh_transition_ui,
    init_shader_tab, setup_shader_tab,
    refresh_shader_ui,
    init_textshader_tab, setup_textshader_tab,
    refresh_textshader_ui,
    init_demo_tab, setup_demo_tab,
    refresh_demo_tab,
    init_gameconfig_tab, setup_gameconfig_tab,
    refresh_gameconfig_tab, show_output_window,
)

# Import modal modules
from modals import (
    init_settings_modal, show_settings_modal,
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
        self.textshader_presets_path = ""
        self.shader_folder = ""
        self.text_shader_folder = ""
        self.game_folder = ""
        self.renpy_exe = ""

        # Demo settings
        self.demo_width = 1080
        self.demo_height = 1920

        # Managers
        self.json_mgr = JsonManager()
        self.shader_parser = ShaderParser()
        self.text_shader_parser = TextShaderParser()
        self.demo_gen = DemoGenerator()

        # UI state
        self.transition_mode = EditorMode.BUILDER
        self.shader_mode = EditorMode.BUILDER
        self.textshader_mode = EditorMode.BUILDER

        # Selection managers
        self.trans_selection = SelectionManager([])
        self.shader_selection = SelectionManager([])
        self.textshader_selection = SelectionManager([])

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
                self.textshader_presets_path = self._resolve_path(
                    config.get("textshader_presets", "")
                )
                self.shader_folder = self._resolve_path(
                    config.get("shader_folder", "")
                )
                self.text_shader_folder = self._resolve_path(
                    config.get("text_shader_folder", "")
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
        self.textshader_presets_path = str(
            (base / "../../game/presets/textshader_presets.json").resolve()
        )
        self.shader_folder = str(
            (base / "../../game/shader").resolve()
        )
        self.text_shader_folder = str(
            (base / "../../game/text_shader").resolve()
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
            "textshader_presets": self.textshader_presets_path,
            "shader_folder": self.shader_folder,
            "text_shader_folder": self.text_shader_folder,
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
            self.shader_presets_path,
            self.textshader_presets_path
        )
        self.json_mgr.load()

        # Update selection managers
        self.trans_selection.update_items(self.json_mgr.get_transition_names())
        self.shader_selection.update_items(self.json_mgr.get_shader_names())
        self.textshader_selection.update_items(self.json_mgr.get_textshader_names())

        # Set presets path for demo generator (for text shader lookup)
        if self.textshader_presets_path:
            presets_folder = str(Path(self.textshader_presets_path).parent)
            self.demo_gen.set_presets_path(presets_folder)

        # Parse shader .rpy files
        if self.shader_folder and Path(self.shader_folder).exists():
            self.shader_parser.parse_directory(self.shader_folder)

        # Parse text shader .rpy files
        if self.text_shader_folder and Path(self.text_shader_folder).exists():
            self.text_shader_parser.parse_directory(self.text_shader_folder)


# Global state
app = AppState()


# =============================================================================
# UI Refresh Functions
# =============================================================================

def refresh_all():
    """Refresh all UI elements."""
    app.trans_selection.update_items(app.json_mgr.get_transition_names())
    app.shader_selection.update_items(app.json_mgr.get_shader_names())
    app.textshader_selection.update_items(app.json_mgr.get_textshader_names())

    refresh_transition_ui()
    refresh_shader_ui()
    refresh_textshader_ui()
    refresh_demo_tab()
    update_status_bar()


def update_status_bar():
    """Update the status bar."""
    if app.status_bar:
        app.status_bar.update(
            auto_save=True,
            undo_count=app.json_mgr.undo_count,
            redo_count=app.json_mgr.redo_count
        )


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
            dpg.add_menu_item(label="Output", callback=show_output_window)
            dpg.add_separator()
            dpg.add_menu_item(label="Exit", callback=dpg.stop_dearpygui)

        with dpg.menu(label="Edit"):
            dpg.add_menu_item(label="Undo", callback=lambda: (app.json_mgr.undo(), refresh_all()),
                            shortcut="Ctrl+Z")
            dpg.add_menu_item(label="Redo", callback=lambda: (app.json_mgr.redo(), refresh_all()),
                            shortcut="Ctrl+Y")

    # Main window
    with dpg.window(tag="primary_window"):
        # Add spacing below menu bar
        dpg.add_spacer(height=10)

        # Tab bar - each tab is built by its module
        with dpg.tab_bar() as tab_bar:
            setup_transition_tab(tab_bar)
            setup_shader_tab(tab_bar)
            setup_textshader_tab(tab_bar)
            setup_demo_tab(tab_bar)
            setup_gameconfig_tab(tab_bar)

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

    # Initialize tab modules (must be before setup_ui)
    init_transition_tab(app, EditorMode, update_status_bar)
    init_shader_tab(app, EditorMode, update_status_bar)
    init_textshader_tab(app, EditorMode, update_status_bar)
    init_demo_tab(app, refresh_all)
    init_gameconfig_tab(app, refresh_all)

    # Initialize modal modules
    init_settings_modal(app, refresh_all)

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
