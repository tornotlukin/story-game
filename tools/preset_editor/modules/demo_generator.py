"""
demo_generator.py - Generate Ren'Py test scripts for presets

Creates menu-based demo scripts that test preset combinations.
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class DemoItem:
    """A single demo item (transition + shader + text_shader combination)."""
    transition: Optional[str] = None
    shader: Optional[str] = None
    text_shader: Optional[str] = None
    # Store resolved shader info for text shader tag generation
    _text_shader_info: Dict[str, Any] = field(default_factory=dict)

    @property
    def display_name(self) -> str:
        """Get display name for the demo item."""
        parts = []
        if self.transition:
            parts.append(f"T:{self.transition}")
        if self.shader:
            parts.append(f"S:{self.shader}")
        if self.text_shader:
            parts.append(f"TS:{self.text_shader}")
        return " + ".join(parts) if parts else "(empty)"

    @property
    def at_clause(self) -> str:
        """Get the 'at' clause for Ren'Py show statement."""
        parts = []
        if self.transition:
            parts.append(f"preset_{self.transition}()")
        if self.shader:
            parts.append(f"shader_{self.shader}")
        return ", ".join(parts) if parts else "center"

    def get_text_shader_tag(self) -> Optional[str]:
        """Get the text shader tag string for Ren'Py.

        Uses {shader=name:param=value} syntax.
        If _text_shader_info is populated, uses the resolved shader name and params.
        Otherwise falls back to using the preset name directly.
        """
        if not self.text_shader:
            return None

        # Check if we have resolved shader info
        if self._text_shader_info:
            shader_name = self._text_shader_info.get("shader")
            if not shader_name:
                return None

            params = self._text_shader_info.get("shader_params", {})
            if params:
                # Build parameter string: "wave:u__amplitude=5.0:u__frequency=2.0"
                # IMPORTANT: Keep u__ prefix for shader local variables!
                # Ren'Py only auto-adds single u_, so u__vars must be explicit
                param_parts = []
                for key, value in params.items():
                    param_parts.append(f"{key}={value}")
                return f"{{shader={shader_name}:{':'.join(param_parts)}}}"
            else:
                return f"{{shader={shader_name}}}"

        # Fallback: use preset name directly (might work if registered as textshader)
        return f"{{shader={self.text_shader}}}"

    @property
    def text_tag_close(self) -> Optional[str]:
        """Get the closing text shader tag."""
        if self.text_shader:
            return "{/shader}"
        return None

    def get_text_style_open_tags(self) -> str:
        """Get opening text style tags for color, font, size from the preset.

        Returns Ren'Py text tags like {color=#000000}{font=...}{size=37}
        """
        if not self._text_shader_info:
            return ""

        text_props = self._text_shader_info.get("text", {})
        if not text_props:
            return ""

        tags = []

        # Color tag
        color = text_props.get("color")
        if color:
            tags.append(f"{{color={color}}}")

        # Font tag
        font = text_props.get("font")
        if font and font != "DejaVuSans.ttf":  # Only if not default
            tags.append(f"{{font={font}}}")

        # Size tag
        size = text_props.get("size")
        if size and size != 28:  # Only if not default
            tags.append(f"{{size={size}}}")

        return "".join(tags)

    def get_text_style_close_tags(self) -> str:
        """Get closing text style tags (in reverse order of opening)."""
        if not self._text_shader_info:
            return ""

        text_props = self._text_shader_info.get("text", {})
        if not text_props:
            return ""

        tags = []

        # Close in reverse order: size, font, color
        size = text_props.get("size")
        if size and size != 28:
            tags.append("{/size}")

        font = text_props.get("font")
        if font and font != "DejaVuSans.ttf":
            tags.append("{/font}")

        color = text_props.get("color")
        if color:
            tags.append("{/color}")

        return "".join(tags)

    def is_empty(self) -> bool:
        """Check if the item has no presets."""
        return not self.transition and not self.shader and not self.text_shader


class DemoGenerator:
    """
    Generates Ren'Py demo scripts for testing presets.

    IMPORTANT: Generated code must match real Ren'Py game patterns.
    See CLAUDE.md "Real Game Parity" section.

    Features:
    - Menu-based navigation (max 10 items)
    - Tests transition + shader + text_shader combinations
    - Configurable character and background
    - Configurable screen dimensions
    - Apply to dialog mode:
      - Shaders applied to say screen window via demo_dialog_transform
      - Text shaders applied via {shader=...} tags in dialogue
    """

    MAX_ITEMS = 10

    def __init__(self):
        self.items: List[DemoItem] = []
        self.character_name = "test"
        self.character_image = "char_demo"
        self.background = "bg_demo"
        self.label_name = "preset_demo"
        self.screen_width = 1080
        self.screen_height = 1920
        self.sample_text = "Sample dialogue text for testing presets."
        # Mode flags (mutually exclusive: both off, or one on)
        # apply_to_text: shader on black rect say window + text shader on text
        # apply_to_dialog: shader on dialog_demo artwork + text shader on text
        self.apply_to_text = False
        self.apply_to_dialog = False
        self._textshader_presets: Dict[str, Any] = {}
        self._presets_path: Optional[str] = None

    def set_presets_path(self, path: str):
        """Set the path to the presets folder for loading textshader presets."""
        self._presets_path = path
        self._load_textshader_presets()

    def _load_textshader_presets(self):
        """Load textshader presets from JSON file."""
        if not self._presets_path:
            return

        json_path = Path(self._presets_path) / "textshader_presets.json"
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._textshader_presets = data.get("presets", {})
            except Exception as e:
                print(f"DemoGenerator: Error loading textshader presets: {e}")

    def _resolve_text_shader_info(self, preset_name: str) -> Dict[str, Any]:
        """Look up a textshader preset and return its shader info AND text styling."""
        if preset_name in self._textshader_presets:
            preset = self._textshader_presets[preset_name]
            return {
                "shader": preset.get("shader"),
                "shader_params": preset.get("shader_params", {}),
                "text": preset.get("text", {})  # Include text styling
            }
        return {}

    def add_item(
        self,
        transition: Optional[str] = None,
        shader: Optional[str] = None,
        text_shader: Optional[str] = None
    ) -> bool:
        """
        Add a demo item.

        Returns False if max items reached.
        """
        if len(self.items) >= self.MAX_ITEMS:
            return False

        item = DemoItem(transition=transition, shader=shader, text_shader=text_shader)
        if not item.is_empty():
            self.items.append(item)
            return True
        return False

    def remove_item(self, index: int) -> bool:
        """Remove a demo item by index."""
        if 0 <= index < len(self.items):
            self.items.pop(index)
            return True
        return False

    def clear_items(self):
        """Clear all demo items."""
        self.items.clear()

    def move_item(self, index: int, direction: str) -> bool:
        """Move an item up or down."""
        if direction == "up" and index > 0:
            self.items[index], self.items[index - 1] = self.items[index - 1], self.items[index]
            return True
        elif direction == "down" and index < len(self.items) - 1:
            self.items[index], self.items[index + 1] = self.items[index + 1], self.items[index]
            return True
        return False

    def get_item(self, index: int) -> Optional[DemoItem]:
        """Get a demo item by index."""
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def generate_script(self) -> str:
        """
        Generate the Ren'Py demo script.

        IMPORTANT: Generated code must match real Ren'Py game patterns.
        - Characters: show at transition(), shader_transform
        - Dialog shaders: set demo_dialog_transform variable
        - Dialog background: set demo_dialog_background variable
        - Text shaders: {shader=...} tags in dialogue string

        Three modes (mutually exclusive):
        - Both OFF: Character/Image testing
        - apply_to_text ON: Shader on black rect + text shader
        - apply_to_dialog ON: Shader on dialog artwork + text shader

        Returns the script content as a string.
        """
        # Reload presets to pick up any changes made in the editor
        self._load_textshader_presets()

        # Clear cached shader info on items so they get re-resolved
        for item in self.items:
            item._text_shader_info = {}

        if not self.items:
            return self._generate_empty_script()

        # Determine mode for header comment
        if self.apply_to_text:
            mode_str = "Text Testing (shader on black rect + text shader)"
        elif self.apply_to_dialog:
            mode_str = "Dialog Testing (shader on dialog artwork + text shader)"
        else:
            mode_str = "Character/Image Testing"

        lines = [
            "## preset_demo.rpy - Auto-generated preset demo",
            "## Generated by Preset Editor",
            "##",
            f"## Testing {len(self.items)} preset combinations",
            f"## Mode: {mode_str}",
            "",
        ]

        # Main label
        lines.extend([
            f"label {self.label_name}:",
            f"    scene {self.background} with dissolve",
            "",
            '    "Preset Demo - Select a preset to test"',
            "",
        ])

        # Generate menu
        lines.append("    menu preset_demo_menu:")
        lines.append('        "Select a preset to demo:"')
        lines.append("")

        for i, item in enumerate(self.items):
            menu_label = item.display_name.replace('"', '\\"')
            at_clause = item.at_clause

            # Resolve text shader info from presets if available
            if item.text_shader and not item._text_shader_info:
                item._text_shader_info = self._resolve_text_shader_info(item.text_shader)

            # Build dialogue text with text styling AND shader tags
            # Order: {color}{font}{size}{shader}text{/shader}{/size}{/font}{/color}
            style_open = item.get_text_style_open_tags()
            style_close = item.get_text_style_close_tags()
            text_tag = item.get_text_shader_tag()

            if text_tag:
                # Has shader effect + styling
                dialogue_text = f"{style_open}{text_tag}{self.sample_text}{item.text_tag_close}{style_close}"
            elif style_open:
                # Has styling only (no shader)
                dialogue_text = f"{style_open}{self.sample_text}{style_close}"
            else:
                dialogue_text = self.sample_text

            lines.append(f'        "{i+1}. {menu_label}":')

            if self.apply_to_text:
                # Apply to Text Mode
                # - Shaders applied to say screen window (black rect) via demo_dialog_transform
                # - Text shaders applied via {shader=...} tags in dialogue

                # Set dialog box shader if specified
                if item.shader:
                    lines.append(f"            $ demo_dialog_transform = shader_{item.shader}")

                # Show dialogue with text shader tags
                lines.append(f'            "{dialogue_text}"')

                # Reset dialog transform
                if item.shader:
                    lines.append(f"            $ demo_dialog_transform = None")

            elif self.apply_to_dialog:
                # Apply to Dialog Mode
                # - Dialog artwork as window background via demo_dialog_background
                # - Shaders applied to dialog artwork via demo_dialog_transform
                # - Text shaders applied via {shader=...} tags in dialogue

                # Set dialog background to artwork
                lines.append(f'            $ demo_dialog_background = "images/dialog_demo.png"')

                # Set dialog box shader if specified
                if item.shader:
                    lines.append(f"            $ demo_dialog_transform = shader_{item.shader}")

                # Show dialogue with text shader tags
                lines.append(f'            "{dialogue_text}"')

                # Reset dialog transform and background
                if item.shader:
                    lines.append(f"            $ demo_dialog_transform = None")
                lines.append(f"            $ demo_dialog_background = None")

            else:
                # Character/Image Testing Mode
                # - Transitions and shaders applied to character image
                # - No text shaders (they're disabled in this mode)

                lines.append(f"            show {self.character_image} at {at_clause}")
                lines.append(f'            {self.character_name} "{dialogue_text}"')
                lines.append(f"            hide {self.character_image} with dissolve")

            lines.append(f"            jump {self.label_name}")
            lines.append("")

        # Exit option
        lines.append('        "Exit Demo":')
        lines.append('            "Demo complete!"')
        lines.append("            return")
        lines.append("")

        return "\n".join(lines)

    def _generate_empty_script(self) -> str:
        """Generate a placeholder script when no items."""
        return f'''## preset_demo.rpy - Auto-generated preset demo
## Generated by Preset Editor
##
## No preset combinations selected.

label {self.label_name}:
    scene {self.background} with dissolve

    "No presets selected for demo."
    "Use the Preset Editor to add demo items."

    return
'''

    def save_script(self, output_path: str) -> bool:
        """
        Save the demo script to a file.

        Args:
            output_path: Path to save the script

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)

            script = self.generate_script()
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script)
            return True
        except Exception as e:
            print(f"DemoGenerator: Error saving script: {e}")
            return False

    def generate_test_game_script(self) -> str:
        """
        Generate a complete test game script.rpy.

        This is for the standalone test game folder.
        Uses bg_demo.png (stretched to fit) and char_demo.png.

        IMPORTANT: This generates real Ren'Py game code patterns.
        No fake overlay images - uses actual say screen for dialog.
        """
        lines = [
            "## script.rpy - Test game for Preset Editor",
            "##",
            "## This is a minimal Ren'Py game for testing presets.",
            "## Generated code matches real game patterns.",
            "## Generated by Preset Editor.",
            "",
            "# Character definition",
            f'define {self.character_name} = Character("{self.character_name.title()}")',
            "",
            f"# Background - stretched to fit {self.screen_width}x{self.screen_height}",
            f'image {self.background} = im.Scale("images/bg_demo.png", {self.screen_width}, {self.screen_height})',
            "",
            "# Character image",
            f'image {self.character_image} = "images/char_demo.png"',
            "",
            "label start:",
            '    "Welcome to the Preset Editor Test Game!"',
            '    "Use this to test your preset combinations."',
            "",
            f"    jump {self.label_name}",
            "",
        ]

        # Add the demo script content
        lines.append(self.generate_script())

        return "\n".join(lines)

    def save_test_game(self, game_folder: str) -> bool:
        """
        Save a complete test game to a folder.

        Creates script.rpy and options.rpy.
        """
        try:
            game_path = Path(game_folder)
            game_path.mkdir(parents=True, exist_ok=True)

            # script.rpy
            script_path = game_path / "script.rpy"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(self.generate_test_game_script())

            # options.rpy with configured dimensions
            options_path = game_path / "options.rpy"
            with open(options_path, 'w', encoding='utf-8') as f:
                f.write(f'''## options.rpy - Test game configuration

define config.name = "Preset Editor Test"
define build.name = "PresetTest"
define config.version = "1.0"

define config.screen_width = {self.screen_width}
define config.screen_height = {self.screen_height}

define config.save_directory = "preset_editor_test"
''')

            return True
        except Exception as e:
            print(f"DemoGenerator: Error saving test game: {e}")
            return False
