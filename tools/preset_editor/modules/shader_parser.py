"""
shader_parser.py - Parse shader .rpy files for shader definitions

Reads structured comments in shader .rpy files to extract:
- Shader names
- Parameter definitions (type, range, default, description)
- Category and description metadata

Comment Syntax:
    ## @tool-category: Glow
    ## @tool-description: Adds glowing aura effects

    # @shader: shader.glow
    # @param u_glow_color: color, default=#FFFFFF, description=Glow color
    # @param u_outer_strength: float, range=0.0-2.0, default=0.6
    # @param u_scale: float, range=0.5-2.0, default=1.0
    renpy.register_shader("shader.glow", ...)
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class ShaderParam:
    """Definition of a shader parameter."""
    name: str
    param_type: str  # color, float, int, vec2, vec3, vec4
    default: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""


@dataclass
class ShaderDefinition:
    """Complete shader definition parsed from .rpy file."""
    name: str  # e.g., "shader.glow"
    category: str = "Uncategorized"
    description: str = ""
    file_description: str = ""  # Natural language description from lines 3-5 of file
    params: List[ShaderParam] = field(default_factory=list)
    source_file: str = ""
    line_number: int = 0
    is_animated: bool = False


class ShaderParser:
    """
    Parses shader .rpy files to extract shader definitions.

    Usage:
        parser = ShaderParser()
        shaders = parser.parse_directory("game/shader")
        for shader in shaders:
            print(f"{shader.name}: {shader.description}")
    """

    def __init__(self):
        self.shaders: Dict[str, ShaderDefinition] = {}

    def parse_directory(self, shader_dir: str) -> List[ShaderDefinition]:
        """
        Parse all .rpy files in a directory for shader definitions.

        Args:
            shader_dir: Path to shader directory

        Returns:
            List of ShaderDefinition objects
        """
        self.shaders = {}
        shader_path = Path(shader_dir)

        if not shader_path.exists():
            print(f"ShaderParser: Directory not found: {shader_dir}")
            return []

        for rpy_file in shader_path.glob("*.rpy"):
            self._parse_file(str(rpy_file))

        return list(self.shaders.values())

    def parse_file(self, filepath: str) -> List[ShaderDefinition]:
        """Parse a single .rpy file."""
        self.shaders = {}
        self._parse_file(filepath)
        return list(self.shaders.values())

    def _parse_file(self, filepath: str):
        """Internal method to parse a single file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            print(f"ShaderParser: Error reading {filepath}: {e}")
            return

        filename = os.path.basename(filepath)

        # File-level metadata
        file_category = "Uncategorized"
        file_description = ""
        file_natural_description = ""

        # Extract natural language description from lines 3-5
        # These are the human-readable description lines before @tool annotations
        desc_lines = []
        for i in range(2, min(5, len(lines))):  # Lines 3-5 (0-indexed: 2-4)
            line = lines[i].strip()
            # Stop if we hit an empty comment line, annotation, or non-comment
            if line == "##" or line.startswith("## @") or not line.startswith("##"):
                break
            # Extract text after ##
            text = line[2:].strip()
            if text:
                desc_lines.append(text)
        file_natural_description = " ".join(desc_lines)

        # Parse file-level annotations (## @tool-xxx)
        for line in lines[:20]:  # Check first 20 lines for file metadata
            line = line.strip()
            if line.startswith("## @tool-category:"):
                file_category = line.split(":", 1)[1].strip()
            elif line.startswith("## @tool-description:"):
                file_description = line.split(":", 1)[1].strip()

        # Find shader definitions
        current_shader = None
        current_params = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Check for @shader annotation
            if stripped.startswith("# @shader:"):
                # Save previous shader if exists
                if current_shader:
                    current_shader.params = current_params
                    self.shaders[current_shader.name] = current_shader

                shader_name = stripped.split(":", 1)[1].strip()
                current_shader = ShaderDefinition(
                    name=shader_name,
                    category=file_category,
                    description=file_description,
                    file_description=file_natural_description,
                    source_file=filename,
                    line_number=i + 1
                )
                current_params = []

            # Check for @param annotation
            elif stripped.startswith("# @param") and current_shader:
                param = self._parse_param_line(stripped)
                if param:
                    current_params.append(param)

            # Check for @animated annotation
            elif stripped.startswith("# @animated") and current_shader:
                current_shader.is_animated = True

            # Check for @description (shader-level)
            elif stripped.startswith("# @description:") and current_shader:
                current_shader.description = stripped.split(":", 1)[1].strip()

            # Also detect renpy.register_shader() calls directly
            elif 'renpy.register_shader(' in stripped:
                shader_name = self._extract_shader_name(stripped)
                if shader_name and shader_name not in self.shaders:
                    # Create basic definition from register_shader call
                    shader_def = ShaderDefinition(
                        name=shader_name,
                        category=file_category,
                        description="",
                        file_description=file_natural_description,
                        source_file=filename,
                        line_number=i + 1
                    )
                    self.shaders[shader_name] = shader_def

        # Save last annotated shader
        if current_shader:
            current_shader.params = current_params
            self.shaders[current_shader.name] = current_shader

    def _extract_shader_name(self, line: str) -> Optional[str]:
        """Extract shader name from renpy.register_shader() call."""
        # Match patterns like: renpy.register_shader("shader.name", ...)
        match = re.search(r'renpy\.register_shader\s*\(\s*["\']([^"\']+)["\']', line)
        if match:
            return match.group(1)
        return None

    def _parse_param_line(self, line: str) -> Optional[ShaderParam]:
        """
        Parse a @param annotation line.

        Format: # @param name: type, range=min-max, default=value, description=text

        Examples:
            # @param u_glow_color: color, default=#FFFFFF, description=Glow color
            # @param u_strength: float, range=0.0-2.0, default=0.6
            # @param u_count: int, range=1-100, default=10
        """
        # Remove "# @param " prefix
        content = line.replace("# @param", "").strip()

        # Split name from rest
        if ":" not in content:
            return None

        name_part, attrs_part = content.split(":", 1)
        name = name_part.strip()

        # Parse attributes
        attrs = {}
        param_type = "float"  # default

        for attr in attrs_part.split(","):
            attr = attr.strip()
            if "=" in attr:
                key, value = attr.split("=", 1)
                attrs[key.strip()] = value.strip()
            else:
                # First non-key=value is the type
                param_type = attr.strip()

        # Build param object
        param = ShaderParam(name=name, param_type=param_type)

        # Parse default value
        if "default" in attrs:
            default_str = attrs["default"]
            if param_type == "color":
                param.default = default_str
            elif param_type == "float":
                try:
                    param.default = float(default_str)
                except:
                    param.default = 0.0
            elif param_type == "int":
                try:
                    param.default = int(default_str)
                except:
                    param.default = 0
            else:
                param.default = default_str

        # Parse range
        if "range" in attrs:
            range_str = attrs["range"]
            if "-" in range_str:
                parts = range_str.split("-")
                if len(parts) == 2:
                    try:
                        param.min_value = float(parts[0])
                        param.max_value = float(parts[1])
                    except:
                        pass

        # Parse description
        if "description" in attrs:
            param.description = attrs["description"]

        return param

    def get_shader(self, name: str) -> Optional[ShaderDefinition]:
        """Get a shader definition by name."""
        return self.shaders.get(name)

    def get_shaders_by_category(self) -> Dict[str, List[ShaderDefinition]]:
        """Group shaders by category."""
        by_category = {}
        for shader in self.shaders.values():
            cat = shader.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(shader)
        return by_category

    def list_available_shaders(self) -> List[str]:
        """Get list of all available shader names."""
        return list(self.shaders.keys())


# Convenience function
def parse_shaders(shader_dir: str) -> List[ShaderDefinition]:
    """Parse all shaders in a directory."""
    parser = ShaderParser()
    return parser.parse_directory(shader_dir)
