"""
schema_loader.py - Load and query game config schema

Provides access to property definitions, categories, and validation
for the schema-driven Game Config tab.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class SchemaLoader:
    """Loads and queries game_config_schema.json."""

    def __init__(self, schema_path: Optional[str] = None):
        self._schema: Dict[str, Any] = {}
        self._categories: List[Dict] = []
        self._properties: List[Dict] = []
        self._props_by_id: Dict[str, Dict] = {}
        self._props_by_category: Dict[str, List[Dict]] = {}

        # Default path is next to this module
        if schema_path is None:
            module_dir = Path(__file__).parent
            schema_path = str(module_dir / "game_config_schema.json")
        self._schema_path = schema_path

    def load(self) -> bool:
        """Load schema from JSON file."""
        if not Path(self._schema_path).exists():
            print(f"Schema file not found: {self._schema_path}")
            return False

        try:
            with open(self._schema_path, 'r', encoding='utf-8') as f:
                self._schema = json.load(f)

            self._categories = self._schema.get("categories", [])
            self._properties = self._schema.get("properties", [])

            # Build lookup indexes
            self._props_by_id = {p["id"]: p for p in self._properties}
            self._props_by_category = {}
            for prop in self._properties:
                cat = prop.get("category", "misc")
                if cat not in self._props_by_category:
                    self._props_by_category[cat] = []
                self._props_by_category[cat].append(prop)

            print(f"Loaded schema: {len(self._categories)} categories, {len(self._properties)} properties")
            return True
        except Exception as e:
            print(f"Error loading schema: {e}")
            return False

    def get_meta(self) -> Dict[str, Any]:
        """Get schema metadata."""
        return self._schema.get("_meta", {})

    def get_target_files(self) -> Dict[str, str]:
        """Get target file mappings (e.g., {'gui': 'game/gui.rpy'})."""
        meta = self.get_meta()
        return meta.get("target_files", {})

    # =========================================================================
    # Categories
    # =========================================================================

    def get_categories(self) -> List[Dict]:
        """Get all categories in order."""
        return self._categories

    def get_category(self, cat_id: str) -> Optional[Dict]:
        """Get a specific category by ID."""
        for cat in self._categories:
            if cat["id"] == cat_id:
                return cat
        return None

    def get_categories_with_enabled_props(self) -> List[Dict]:
        """Get categories that have at least one enabled property."""
        result = []
        for cat in self._categories:
            props = self.get_properties_for_category(cat["id"], enabled_only=True)
            if props:
                result.append(cat)
        return result

    # =========================================================================
    # Properties
    # =========================================================================

    def get_all_properties(self) -> List[Dict]:
        """Get all properties."""
        return self._properties

    def get_property(self, prop_id: str) -> Optional[Dict]:
        """Get a property by its ID (e.g., 'gui.accent_color')."""
        return self._props_by_id.get(prop_id)

    def get_properties_for_category(self, cat_id: str, enabled_only: bool = False) -> List[Dict]:
        """Get all properties for a category."""
        props = self._props_by_category.get(cat_id, [])
        if enabled_only:
            return [p for p in props if p.get("enabled", True)]
        return props

    def get_enabled_properties(self) -> List[Dict]:
        """Get all enabled properties."""
        return [p for p in self._properties if p.get("enabled", True)]

    def get_disabled_properties(self) -> List[Dict]:
        """Get all disabled properties."""
        return [p for p in self._properties if not p.get("enabled", True)]

    # =========================================================================
    # Validation
    # =========================================================================

    def validate_value(self, prop_id: str, value: Any) -> Tuple[bool, str]:
        """Validate a value against property constraints.

        Returns (is_valid, error_message).
        """
        prop = self.get_property(prop_id)
        if not prop:
            return False, f"Unknown property: {prop_id}"

        prop_type = prop.get("type", "string")
        validation = prop.get("validation", {})

        # Type checking
        if prop_type == "int":
            if not isinstance(value, int):
                return False, f"Expected integer, got {type(value).__name__}"
            if "min" in validation and value < validation["min"]:
                return False, f"Value must be >= {validation['min']}"
            if "max" in validation and value > validation["max"]:
                return False, f"Value must be <= {validation['max']}"

        elif prop_type == "float":
            if not isinstance(value, (int, float)):
                return False, f"Expected number, got {type(value).__name__}"
            if "min" in validation and value < validation["min"]:
                return False, f"Value must be >= {validation['min']}"
            if "max" in validation and value > validation["max"]:
                return False, f"Value must be <= {validation['max']}"

        elif prop_type == "string":
            if not isinstance(value, str):
                return False, f"Expected string, got {type(value).__name__}"
            if "pattern" in validation:
                import re
                if not re.match(validation["pattern"], value):
                    return False, validation.get("message", "Invalid format")

        elif prop_type == "color":
            if not isinstance(value, str):
                return False, "Color must be a hex string"
            if not value.startswith("#"):
                return False, "Color must start with #"
            hex_part = value[1:]
            if len(hex_part) not in [6, 8]:
                return False, "Color must be #RRGGBB or #RRGGBBAA"
            try:
                int(hex_part, 16)
            except ValueError:
                return False, "Invalid hex color"

        elif prop_type == "bool":
            if not isinstance(value, bool):
                return False, f"Expected boolean, got {type(value).__name__}"

        elif prop_type == "int_or_none":
            if value is not None and not isinstance(value, int):
                return False, f"Expected integer or None, got {type(value).__name__}"

        elif prop_type == "borders":
            if not isinstance(value, list) or len(value) != 4:
                return False, "Borders must be a list of 4 integers"
            if not all(isinstance(v, int) for v in value):
                return False, "All border values must be integers"

        return True, ""

    def get_default_value(self, prop_id: str) -> Any:
        """Get the default value for a property."""
        prop = self.get_property(prop_id)
        if prop:
            return prop.get("default")
        return None

    # =========================================================================
    # Code Generation Helpers
    # =========================================================================

    def get_rpy_pattern(self, prop_id: str) -> Optional[str]:
        """Get the Ren'Py line pattern for a property."""
        prop = self.get_property(prop_id)
        if prop:
            return prop.get("pattern")
        return None

    def get_target_file(self, prop_id: str) -> Optional[str]:
        """Get which file a property belongs to ('gui' or 'options')."""
        prop = self.get_property(prop_id)
        if prop:
            return prop.get("file")
        return None

    def format_rpy_value(self, prop_id: str, value: Any) -> str:
        """Format a value for Ren'Py code output."""
        prop = self.get_property(prop_id)
        if not prop:
            return str(value)

        prop_type = prop.get("type", "string")

        if value is None:
            return "None"
        elif prop_type == "color":
            return f"'{value}'"
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
            return f"Borders({value[0]}, {value[1]}, {value[2]}, {value[3]})"
        elif prop_type in ["int", "float", "int_or_none"]:
            return str(value) if value is not None else "None"
        elif prop_type == "color_or_ref":
            # Could be a color or a reference like gui.idle_color
            if value.startswith("#"):
                return f"'{value}'"
            else:
                return value  # It's a reference
        else:
            return str(value)

    def format_rpy_line(self, prop_id: str, value: Any) -> Optional[str]:
        """Generate a complete Ren'Py line for a property."""
        prop = self.get_property(prop_id)
        if not prop or value is None:
            return None

        pattern = prop.get("pattern", "")
        formatted_value = self.format_rpy_value(prop_id, value)

        return f"{pattern}{formatted_value}"
