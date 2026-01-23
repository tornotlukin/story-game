"""
gameconfig_manager.py - Game configuration management (Schema-Driven)

Handles:
- Loading/saving baseline_config.json (ID-based format)
- Generating theme.rpy code using schema definitions
- Configuration validation
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional, Callable, List
from copy import deepcopy


class GameConfigManager:
    """Manages game configuration loading, saving, and code generation."""

    def __init__(self, schema_loader=None):
        self._config: Dict[str, Any] = {}
        self._config_path: Optional[str] = None
        self._change_callbacks: List[Callable] = []
        self._dirty = False
        self._schema = schema_loader

        # Set default path to baseline_config.json next to this module
        module_dir = Path(__file__).parent
        self._config_path = str(module_dir / "baseline_config.json")

    def set_path(self, path: str):
        """Set the config file path."""
        self._config_path = path

    def load(self) -> bool:
        """Load configuration from JSON file."""
        if not self._config_path or not Path(self._config_path).exists():
            print(f"Config file not found: {self._config_path}")
            return False

        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            self._dirty = False
            print(f"Loaded config from: {self._config_path}")
            return True
        except Exception as e:
            print(f"Error loading config: {e}")
            return False

    def save(self) -> bool:
        """Save configuration to JSON file."""
        if not self._config_path:
            print("No config path set")
            return False

        try:
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
            self._dirty = False
            print(f"Saved config to: {self._config_path}")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def on_change(self, callback: Callable):
        """Register a callback for when config changes."""
        if callback not in self._change_callbacks:
            self._change_callbacks.append(callback)

    def _notify_change(self):
        """Notify all registered callbacks of a change."""
        self._dirty = True
        for cb in self._change_callbacks:
            try:
                cb()
            except Exception as e:
                print(f"Change callback error: {e}")

    # =========================================================================
    # ID-Based Value Access (New Format)
    # =========================================================================

    def get_value_by_id(self, prop_id: str) -> Any:
        """Get a value by property ID (e.g., 'gui.accent_color')."""
        values = self._config.get("values", {})
        return values.get(prop_id)

    def set_value_by_id(self, prop_id: str, value: Any):
        """Set a value by property ID."""
        if "values" not in self._config:
            self._config["values"] = {}
        self._config["values"][prop_id] = value
        self._notify_change()
        self.save()  # Auto-save

    def get_all_values(self) -> Dict[str, Any]:
        """Get all values as a dict."""
        return deepcopy(self._config.get("values", {}))

    # =========================================================================
    # Legacy Section-Based Access (Deprecated but kept for compatibility)
    # =========================================================================

    def get_config(self) -> Dict[str, Any]:
        """Get the entire configuration."""
        return deepcopy(self._config)

    def get_section(self, section: str) -> Optional[Dict[str, Any]]:
        """Get a configuration section (legacy)."""
        return deepcopy(self._config.get(section))

    def get_value(self, section: str, key: str) -> Any:
        """Get a specific value from a section (legacy)."""
        sect = self._config.get(section, {})
        return sect.get(key)

    def set_section(self, section: str, data: Dict[str, Any]):
        """Set an entire section (legacy)."""
        self._config[section] = deepcopy(data)
        self._notify_change()
        self.save()

    def set_value(self, section: str, key: str, value: Any):
        """Set a specific value in a section (legacy)."""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        self._notify_change()
        self.save()

    # =========================================================================
    # Code Generation - Generate theme.rpy using Schema
    # =========================================================================

    def generate_theme_rpy(self) -> str:
        """Generate the theme.rpy file content using schema."""
        lines = []

        # Header
        lines.append("## theme.rpy - Generated by Preset Editor Game Configurator")
        lines.append("## This file overrides default gui.rpy and options.rpy settings")
        lines.append("## Delete this file to revert to Ren'Py defaults")
        lines.append("##")
        lines.append(f"## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("init offset = 1  # Load after gui.rpy")
        lines.append("")

        if self._schema:
            # Schema-driven generation
            for category in self._schema.get_categories():
                cat_lines = self._generate_category_lines(category)
                if cat_lines:
                    lines.append("")
                    lines.append("################################################################################")
                    lines.append(f"## {category['label']}")
                    lines.append("################################################################################")
                    lines.append("")
                    lines.extend(cat_lines)
        else:
            # Fallback to legacy generation
            lines.extend(self._generate_legacy_theme())

        lines.append("")
        return "\n".join(lines)

    def _generate_category_lines(self, category: Dict) -> List[str]:
        """Generate Ren'Py lines for all enabled properties in a category."""
        lines = []
        props = self._schema.get_properties_for_category(category["id"], enabled_only=True)

        for prop in props:
            prop_id = prop["id"]
            value = self.get_value_by_id(prop_id)

            # Skip if no value set
            if value is None:
                continue

            # Generate the Ren'Py line using schema
            line = self._format_property_line(prop, value)
            if line:
                lines.append(line)

        return lines

    def _format_property_line(self, prop: Dict, value: Any) -> Optional[str]:
        """Format a single property as a Ren'Py line."""
        pattern = prop.get("pattern", "")
        prop_type = prop.get("type", "string")
        prop_id = prop["id"]

        # Handle special pattern types
        pattern_type = prop.get("pattern_type")
        if pattern_type == "function_arg":
            # Special handling for gui.init() - skip, handled separately
            return None

        # Format value based on type
        formatted_value = self._format_value(prop_type, value, prop)

        if formatted_value is not None:
            return f"{pattern}{formatted_value}"
        return None

    def _format_value(self, prop_type: str, value: Any, prop: Dict) -> Optional[str]:
        """Format a value for Ren'Py code output."""
        if value is None:
            return "None"

        if prop_type == "color":
            return f"'{value}'"
        elif prop_type == "color_or_ref":
            # Could be a color or a reference like gui.idle_color
            if str(value).startswith("#"):
                return f"'{value}'"
            else:
                return str(value)  # It's a reference
        elif prop_type == "string":
            # Check if translatable
            if prop.get("translatable"):
                return f'_("{value}")'
            return f'"{value}"'
        elif prop_type == "font":
            return f'"{value}"'
        elif prop_type == "image_path":
            return f'"{value}"'
        elif prop_type == "bool":
            return "True" if value else "False"
        elif prop_type == "borders":
            if isinstance(value, list) and len(value) == 4:
                return f"Borders({value[0]}, {value[1]}, {value[2]}, {value[3]})"
            return None
        elif prop_type in ["int", "float"]:
            return str(value)
        elif prop_type == "int_or_none":
            return str(value) if value is not None else "None"
        elif prop_type == "transition":
            return str(value)
        elif prop_type == "multiline_string":
            # Escape special characters
            escaped = str(value).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            return f'_("{escaped}")'
        else:
            return str(value)

    def _generate_legacy_theme(self) -> List[str]:
        """Generate theme.rpy using legacy section-based format (fallback)."""
        lines = []
        values = self._config.get("values", {})

        # Group by prefix for organization
        gui_lines = []
        config_lines = []
        pref_lines = []
        build_lines = []

        for prop_id, value in values.items():
            if value is None:
                continue

            # Determine format based on ID
            if prop_id.startswith("gui."):
                line = self._format_legacy_line(prop_id, value)
                if line:
                    gui_lines.append(line)
            elif prop_id.startswith("config."):
                line = self._format_legacy_line(prop_id, value)
                if line:
                    config_lines.append(line)
            elif prop_id.startswith("preferences."):
                line = self._format_legacy_line(prop_id, value, use_default=True)
                if line:
                    pref_lines.append(line)
            elif prop_id.startswith("build."):
                line = self._format_legacy_line(prop_id, value)
                if line:
                    build_lines.append(line)

        if config_lines or build_lines:
            lines.append("## Project")
            lines.extend(config_lines)
            lines.extend(build_lines)
            lines.append("")

        if gui_lines:
            lines.append("## GUI Settings")
            lines.extend(gui_lines)
            lines.append("")

        if pref_lines:
            lines.append("## Preferences")
            lines.extend(pref_lines)
            lines.append("")

        return lines

    def _format_legacy_line(self, prop_id: str, value: Any, use_default: bool = False) -> Optional[str]:
        """Format a line in legacy mode."""
        keyword = "default" if use_default else "define"

        # Determine type from value
        if isinstance(value, bool):
            return f"{keyword} {prop_id} = {value}"
        elif isinstance(value, int):
            return f"{keyword} {prop_id} = {value}"
        elif isinstance(value, float):
            return f"{keyword} {prop_id} = {value}"
        elif isinstance(value, str):
            if value.startswith("#"):
                return f"{keyword} {prop_id} = '{value}'"
            elif prop_id.endswith("_font") or prop_id.endswith("_background"):
                return f'{keyword} {prop_id} = "{value}"'
            elif prop_id in ["config.name"]:
                return f'{keyword} {prop_id} = _("{value}")'
            else:
                return f'{keyword} {prop_id} = "{value}"'
        elif isinstance(value, list):
            if len(value) == 4:
                return f"{keyword} {prop_id} = Borders({value[0]}, {value[1]}, {value[2]}, {value[3]})"

        return None

    def export_theme_rpy(self, target_folder: str) -> bool:
        """Export theme.rpy to the target game folder."""
        if not target_folder:
            print("No target folder specified")
            return False

        target_path = Path(target_folder) / "theme.rpy"

        try:
            content = self.generate_theme_rpy()
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Exported theme.rpy to: {target_path}")

            # Update meta timestamp
            if "_meta" not in self._config:
                self._config["_meta"] = {}
            self._config["_meta"]["generated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.save()

            return True
        except Exception as e:
            print(f"Error exporting theme.rpy: {e}")
            return False

    # =========================================================================
    # Legacy Section-specific getters (Deprecated)
    # =========================================================================

    def get_project(self) -> Dict[str, Any]:
        return self.get_section("project") or {}

    def get_screen(self) -> Dict[str, Any]:
        return self.get_section("screen") or {}

    def get_colors(self) -> Dict[str, Any]:
        return self.get_section("colors") or {}

    def get_fonts(self) -> Dict[str, Any]:
        return self.get_section("fonts") or {}

    def get_font_sizes(self) -> Dict[str, Any]:
        return self.get_section("font_sizes") or {}

    def get_dialogue(self) -> Dict[str, Any]:
        return self.get_section("dialogue") or {}

    def get_namebox(self) -> Dict[str, Any]:
        return self.get_section("namebox") or {}

    def get_menu_backgrounds(self) -> Dict[str, Any]:
        return self.get_section("menu_backgrounds") or {}

    def get_text_speed(self) -> Dict[str, Any]:
        return self.get_section("text_speed") or {}

    def get_window_behavior(self) -> Dict[str, Any]:
        return self.get_section("window_behavior") or {}

    def get_ui_details(self) -> Dict[str, Any]:
        return self.get_section("ui_details") or {}

    def get_choice_buttons(self) -> Dict[str, Any]:
        return self.get_section("choice_buttons") or {}
