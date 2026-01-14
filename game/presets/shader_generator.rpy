## shader_generator.rpy - Generate shader transforms from JSON presets
##
## Reads shader_presets.json at init and creates ATL transforms.
## Each preset becomes a global transform: shader_glow_blue, shader_wave_gentle
##
## NOTE: mesh_pad is intentionally ignored to allow chaining with transition presets.
## Shaders work with mesh True only.
##
## Usage:
##     show character at shader_glow_blue
##     show character at preset_slide_left_enter(), shader_wave_gentle
##
## Related files: shader_presets.json, preset_generator.rpy

init -5 python:
    import json
    import os
    import re

    class ShaderGenerator:
        """
        Loads shader presets from JSON and registers them as ATL transforms.
        """

        def __init__(self):
            self.presets = {}
            self._loaded = False

        def load(self):
            """Load presets from JSON file."""
            if self._loaded:
                return True

            filepath = os.path.join(config.gamedir, "presets", "shader_presets.json")
            if not os.path.exists(filepath):
                print(f"ShaderGenerator: File not found: {filepath}")
                return False

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._parse_presets(data.get("shader_presets", {}))
                self._loaded = True
                print(f"ShaderGenerator: Loaded {len(self.presets)} shader presets")
                return True
            except Exception as e:
                print(f"ShaderGenerator: Error loading presets: {e}")
                import traceback
                traceback.print_exc()
                return False

        def _parse_presets(self, data):
            """Parse shader preset definitions from JSON data."""
            for name, config in data.items():
                # Skip comment keys
                if name.startswith("_"):
                    continue
                # Use duck typing
                if not hasattr(config, 'keys'):
                    continue
                self.presets[name] = config

        def _hex_to_tuple(self, hex_color):
            """Convert hex color string to RGBA tuple (0.0-1.0)."""
            if not isinstance(hex_color, str):
                return hex_color

            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                return (r, g, b, 1.0)
            elif len(hex_color) == 8:
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                a = int(hex_color[6:8], 16) / 255.0
                return (r, g, b, a)
            return hex_color

        def _convert_param(self, value):
            """Convert JSON param values to Ren'Py compatible types."""
            # Handle hex colors
            if isinstance(value, str) and value.startswith('#'):
                return self._hex_to_tuple(value)
            # Handle arrays -> tuples
            if isinstance(value, list):
                return tuple(value)
            return value

        def get_preset(self, name):
            """Get a preset by name."""
            self.load()
            return self.presets.get(name)

        def list_presets(self):
            """Get list of all preset names."""
            self.load()
            return list(self.presets.keys())

        def create_transform(self, name):
            """
            Create an ATL transform for a shader preset.
            Returns a Transform object.
            """
            config = self.get_preset(name)
            if not config:
                return None

            shader_name = config.get("shader")
            params = config.get("params", {})
            animated = config.get("animated", False)
            # mesh_pad intentionally ignored for chaining compatibility

            # Convert params
            converted_params = {}
            for key, value in params.items():
                converted_params[key] = self._convert_param(value)

            if animated:
                # Animated shader - needs continuous updates
                def anim_func(trans, st, at):
                    trans.mesh = True
                    trans.shader = shader_name
                    for key, value in converted_params.items():
                        setattr(trans, key, value)
                    return 0  # Always redraw

                return Transform(function=anim_func)
            else:
                # Static shader
                def static_func(trans, st, at):
                    trans.mesh = True
                    trans.shader = shader_name
                    for key, value in converted_params.items():
                        setattr(trans, key, value)
                    return None  # Done after first frame

                return Transform(function=static_func)

        def create_transform_factory(self, name):
            """
            Create a callable that returns a new Transform each time.
            This is needed for proper chaining.
            """
            config = self.get_preset(name)
            if not config:
                return None

            shader_name = config.get("shader")
            params = config.get("params", {})
            animated = config.get("animated", False)

            # Convert params once
            converted_params = {}
            for key, value in params.items():
                converted_params[key] = self._convert_param(value)

            def factory():
                if animated:
                    def anim_func(trans, st, at):
                        trans.mesh = True
                        trans.shader = shader_name
                        for key, value in converted_params.items():
                            setattr(trans, key, value)
                        return 0
                    return Transform(function=anim_func)
                else:
                    def static_func(trans, st, at):
                        trans.mesh = True
                        trans.shader = shader_name
                        for key, value in converted_params.items():
                            setattr(trans, key, value)
                        return None
                    return Transform(function=static_func)

            return factory

        def register_all(self):
            """
            Register all presets as global transforms.
            Creates transforms named 'shader_<name>' for each preset.
            """
            self.load()
            count = 0
            for name in self.presets:
                # Create a static transform instance for simple usage
                transform = self.create_transform(name)
                if transform:
                    global_name = f"shader_{name}"
                    setattr(store, global_name, transform)
                    count += 1

            print(f"ShaderGenerator: Registered {count} shader transforms")
            return count


# Global instance
init -4 python:
    shader_gen = ShaderGenerator()


# Register all shaders at init 1
init 1 python:
    shader_gen.register_all()
