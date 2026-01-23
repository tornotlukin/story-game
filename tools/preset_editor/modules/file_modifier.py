"""
file_modifier.py - Modify gui.rpy and options.rpy in target game projects

Reads schema patterns to find and replace property values in-place.
Skips properties that don't exist in the target files.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ModificationResult:
    """Result of a file modification operation."""
    success: bool
    modified_count: int
    skipped_count: int
    messages: List[str]


class GameFileModifier:
    """Modifies gui.rpy and options.rpy in a target game project."""

    def __init__(self, schema_loader):
        self._schema = schema_loader
        self._messages: List[str] = []

    def _log(self, message: str):
        """Add a message to the log."""
        self._messages.append(message)
        print(f"[FileModifier] {message}")

    def modify_project(self, game_folder: str, values: Dict[str, Any]) -> ModificationResult:
        """
        Modify gui.rpy and options.rpy with the given values.

        Args:
            game_folder: Path to the game folder (containing gui.rpy, options.rpy)
            values: Dict of property_id -> value to apply

        Returns:
            ModificationResult with success status and messages
        """
        self._messages = []
        game_path = Path(game_folder)

        # Validate folder
        if not game_path.exists():
            self._log(f"ERROR: Game folder not found: {game_folder}")
            return ModificationResult(False, 0, 0, self._messages)

        gui_path = game_path / "gui.rpy"
        options_path = game_path / "options.rpy"

        if not gui_path.exists():
            self._log(f"ERROR: gui.rpy not found in {game_folder}")
            return ModificationResult(False, 0, 0, self._messages)

        if not options_path.exists():
            self._log(f"ERROR: options.rpy not found in {game_folder}")
            return ModificationResult(False, 0, 0, self._messages)

        # Group values by target file
        gui_values = {}
        options_values = {}

        for prop_id, value in values.items():
            if value is None:
                continue

            prop = self._schema.get_property(prop_id)
            if not prop:
                self._log(f"SKIP: Unknown property {prop_id}")
                continue

            if not prop.get("enabled", True):
                continue

            target_file = prop.get("file", "gui")
            if target_file == "gui":
                gui_values[prop_id] = value
            elif target_file == "options":
                options_values[prop_id] = value

        # Modify each file
        total_modified = 0
        total_skipped = 0

        if gui_values:
            self._log(f"Processing gui.rpy ({len(gui_values)} properties)...")
            modified, skipped = self._modify_file(gui_path, gui_values)
            total_modified += modified
            total_skipped += skipped

        if options_values:
            self._log(f"Processing options.rpy ({len(options_values)} properties)...")
            modified, skipped = self._modify_file(options_path, options_values)
            total_modified += modified
            total_skipped += skipped

        success = total_modified > 0 or (total_modified == 0 and total_skipped == 0)
        self._log(f"Complete: {total_modified} modified, {total_skipped} skipped")

        return ModificationResult(success, total_modified, total_skipped, self._messages)

    def _modify_file(self, file_path: Path, values: Dict[str, Any]) -> Tuple[int, int]:
        """
        Modify a single .rpy file with the given values.

        Returns:
            Tuple of (modified_count, skipped_count)
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self._log(f"ERROR: Could not read {file_path}: {e}")
            return 0, len(values)

        lines = content.split('\n')
        modified_count = 0
        skipped_props = []

        for prop_id, value in values.items():
            prop = self._schema.get_property(prop_id)
            if not prop:
                continue

            pattern = prop.get("pattern", "")
            if not pattern:
                self._log(f"SKIP: No pattern for {prop_id}")
                skipped_props.append(prop_id)
                continue

            # Handle special pattern types (like gui.init function args)
            pattern_type = prop.get("pattern_type")
            if pattern_type == "function_arg":
                # Skip function arg patterns for now - gui.init() is special
                self._log(f"SKIP: Function arg pattern not supported: {prop_id}")
                skipped_props.append(prop_id)
                continue

            # Find and replace the line
            found = False
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith(pattern):
                    # Found the line - replace it
                    new_value = self._format_value(prop, value)
                    # Preserve leading whitespace
                    leading_ws = line[:len(line) - len(line.lstrip())]
                    lines[i] = f"{leading_ws}{pattern}{new_value}"
                    found = True
                    modified_count += 1
                    self._log(f"  Modified: {prop_id}")
                    break

            if not found:
                self._log(f"  SKIP: Line not found for {prop_id}")
                skipped_props.append(prop_id)

        # Write back if we made changes
        if modified_count > 0:
            try:
                file_path.write_text('\n'.join(lines), encoding='utf-8')
                self._log(f"  Saved: {file_path.name}")
            except Exception as e:
                self._log(f"ERROR: Could not write {file_path}: {e}")
                return 0, len(values)

        return modified_count, len(skipped_props)

    def _format_value(self, prop: Dict, value: Any) -> str:
        """Format a value for Ren'Py code output."""
        prop_type = prop.get("type", "string")

        if value is None:
            return "None"

        if prop_type == "color":
            return f"'{value}'"
        elif prop_type == "color_or_ref":
            if str(value).startswith("#"):
                return f"'{value}'"
            else:
                return str(value)
        elif prop_type == "string":
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
            return "Borders(0, 0, 0, 0)"
        elif prop_type in ["int", "float"]:
            return str(value)
        elif prop_type == "int_or_none":
            return str(value) if value is not None else "None"
        elif prop_type == "transition":
            return str(value)
        elif prop_type == "multiline_string":
            escaped = str(value).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            return f'_("{escaped}")'
        else:
            return str(value)

    def validate_folder(self, game_folder: str) -> Tuple[bool, str]:
        """
        Validate that a folder is a valid Ren'Py game folder.

        Returns:
            Tuple of (is_valid, message)
        """
        game_path = Path(game_folder)

        if not game_path.exists():
            return False, "Folder does not exist"

        if not game_path.is_dir():
            return False, "Path is not a folder"

        gui_path = game_path / "gui.rpy"
        options_path = game_path / "options.rpy"

        missing = []
        if not gui_path.exists():
            missing.append("gui.rpy")
        if not options_path.exists():
            missing.append("options.rpy")

        if missing:
            return False, f"Missing required files: {', '.join(missing)}"

        return True, "Valid Ren'Py game folder"
