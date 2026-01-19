## textshader_generator.rpy - Generate text styles from JSON presets
##
## Reads textshader_presets.json at init and creates styles for each preset.
## Use with: style say_what (for dialogue text)
## Or with Character definition: what_style="ts_preset_name"

init -5 python:
    import json
    import os

    class TextShaderGenerator:
        """Generates Ren'Py styles from textshader_presets.json"""

        def __init__(self):
            self.presets = {}
            self.defaults = {}
            self._loaded = False

        def load(self):
            if self._loaded:
                return

            path = os.path.join(config.gamedir, "presets", "textshader_presets.json")
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.defaults = data.get("defaults", {})
                    self._parse_presets(data.get("presets", {}))
                    print(f"TextShaderGenerator: Loaded {len(self.presets)} presets")
                except Exception as e:
                    print(f"TextShaderGenerator: Error loading presets: {e}")
            else:
                print(f"TextShaderGenerator: No presets file at {path}")
            self._loaded = True

        def _parse_presets(self, data):
            for name, config in data.items():
                if name.startswith("_"):
                    continue
                self.presets[name] = config

        def _hex_to_color(self, hex_str):
            """Convert hex color to Ren'Py color string."""
            if hex_str.startswith("#"):
                return hex_str
            return "#" + hex_str

        def _build_textshader_string(self, preset):
            """Build the textshader string from shader name and params."""
            shader = preset.get("shader")
            if not shader:
                return None

            params = preset.get("shader_params", {})
            if not params:
                return shader

            # Build parameter string: "wave:u_amplitude=5.0:u_frequency=2.0"
            param_parts = []
            for key, value in params.items():
                # Remove u_ prefix if present for cleaner syntax
                clean_key = key[2:] if key.startswith("u_") else key
                param_parts.append(f"{clean_key}={value}")

            if param_parts:
                return f"{shader}:{':'.join(param_parts)}"
            return shader

        def get_preset(self, name):
            """Get a preset by name."""
            self.load()
            return self.presets.get(name)

        def get_textshader_string(self, name):
            """Get the textshader string for a preset."""
            preset = self.get_preset(name)
            if preset:
                return self._build_textshader_string(preset)
            return None

        def get_style_properties(self, name):
            """Get style properties dict for a preset."""
            preset = self.get_preset(name)
            if not preset:
                return {}

            text_config = preset.get("text", {})
            props = {}

            # Font
            if "font" in text_config:
                props["font"] = text_config["font"]

            # Size
            if "size" in text_config:
                props["size"] = text_config["size"]

            # Color
            if "color" in text_config:
                props["color"] = self._hex_to_color(text_config["color"])

            # Outlines - convert to Ren'Py format
            if "outlines" in text_config and text_config["outlines"]:
                outlines = []
                for outline in text_config["outlines"]:
                    if len(outline) >= 2:
                        size = outline[0]
                        color = self._hex_to_color(outline[1])
                        x_off = outline[2] if len(outline) > 2 else 0
                        y_off = outline[3] if len(outline) > 3 else 0
                        outlines.append((size, color, x_off, y_off))
                props["outlines"] = outlines

            # Kerning
            if "kerning" in text_config:
                props["kerning"] = text_config["kerning"]

            # Line spacing
            if "line_spacing" in text_config:
                props["line_spacing"] = text_config["line_spacing"]

            # Slow CPS (for slow_cps style property)
            if "slow_cps" in text_config and text_config["slow_cps"] > 0:
                props["slow_cps"] = text_config["slow_cps"]

            # Bold/Italic
            if text_config.get("bold"):
                props["bold"] = True
            if text_config.get("italic"):
                props["italic"] = True

            # Text shader
            textshader = self._build_textshader_string(preset)
            if textshader:
                props["textshader"] = textshader

            return props

        def register_all_styles(self):
            """Register styles for all presets as ts_<name>."""
            self.load()
            count = 0
            for name in self.presets:
                style_name = f"ts_{name}"
                props = self.get_style_properties(name)

                # Create the style dynamically
                if props:
                    try:
                        # Create style inheriting from default
                        s = Style(style.default)
                        for prop, value in props.items():
                            setattr(s, prop, value)
                        setattr(store.style, style_name, s)
                        count += 1
                    except Exception as e:
                        print(f"TextShaderGenerator: Error creating style {style_name}: {e}")

            print(f"TextShaderGenerator: Registered {count} text styles")


# Register all styles at init 1 (after styles are available)
init 1 python:
    # Create instance and register styles
    # Instance created here because it needs to be in same scope as register call
    _ts_gen = TextShaderGenerator()
    _ts_gen.register_all_styles()
