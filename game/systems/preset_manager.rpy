## preset_manager.rpy - Preset loading and application system
##
## Loads shader_presets.json and presets.json to control visual effects,
## character choreography, audio, and transitions.
##
## Usage:
##   $ mood.set("dream_sequence")
##   $ mood.character_enter("novy", "dream_sequence")
##   $ mood.chain("battle_intense", "clash")
##
## Related files: presets/shader_presets.json, presets/presets.json
## Documentation: docs/PRESET_SYSTEM.md

init -10 python:
    import json
    import os

    # Register ambient channel for mood audio
    if "ambient" not in renpy.audio.audio.channels:
        renpy.music.register_channel("ambient", mixer="sfx", loop=True)

    class PresetManager:
        """
        Manages loading and applying visual/audio presets.

        Two-tier system:
        - shader_presets: Elemental shader configurations
        - presets: Full scene choreography (references shader_presets)
        """

        def __init__(self):
            self.shader_presets = {}
            self.scene_presets = {}
            self.current_preset = None
            self.active_shaders = []
            self._loaded = False

        def load(self):
            """Load preset JSON files."""
            if self._loaded:
                return

            # Load shader presets
            shader_path = os.path.join(config.gamedir, "presets", "shader_presets.json")
            if os.path.exists(shader_path):
                with open(shader_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._parse_shader_presets(data.get("shader_presets", {}))

            # Load scene presets
            preset_path = os.path.join(config.gamedir, "presets", "presets.json")
            if os.path.exists(preset_path):
                with open(preset_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._parse_scene_presets(data.get("presets", {}))

            self._loaded = True

        def _parse_shader_presets(self, data):
            """Parse shader presets from JSON (flat structure with _comment keys)."""
            count = 0
            for name, config in data.items():
                # Skip comment keys and non-dict values
                if name.startswith("_"):
                    continue
                if not isinstance(config, dict):
                    continue
                self.shader_presets[name] = config
                count += 1
            print(f"PresetManager: Loaded {count} shader presets")

        def _parse_scene_presets(self, data):
            """Parse scene presets, resolving inheritance."""
            # First pass: store raw presets
            raw_presets = {}
            for name, config in data.items():
                if not name.startswith("_"):
                    raw_presets[name] = config

            # Second pass: resolve inheritance
            for name in raw_presets:
                self.scene_presets[name] = self._resolve_inheritance(name, raw_presets)

        def _resolve_inheritance(self, name, raw_presets, visited=None):
            """Resolve inheritance chain for a preset."""
            if visited is None:
                visited = set()

            if name in visited:
                return raw_presets.get(name, {})
            visited.add(name)

            preset = raw_presets.get(name, {})
            extends = preset.get("extends")

            if not extends:
                return dict(preset)

            # Handle single or multiple inheritance
            parents = [extends] if isinstance(extends, str) else extends

            # Start with first parent as base
            result = {}
            for parent_name in parents:
                parent = self._resolve_inheritance(parent_name, raw_presets, visited.copy())
                result = self._deep_merge(result, parent)

            # Override with current preset
            result = self._deep_merge(result, preset)
            return result

        def _deep_merge(self, base, override):
            """Deep merge two dictionaries."""
            result = dict(base)
            for key, value in override.items():
                if key.startswith("_"):
                    continue
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        def get_shader_preset(self, name):
            """Get a shader preset by name."""
            self.load()
            return self.shader_presets.get(name)

        def get_scene_preset(self, name):
            """Get a scene preset by name (with inheritance resolved)."""
            self.load()
            return self.scene_presets.get(name)

        def hex_to_color(self, hex_str):
            """Convert hex color string to Ren'Py color tuple."""
            if not hex_str or not isinstance(hex_str, str):
                return (1.0, 1.0, 1.0, 1.0)
            hex_str = hex_str.lstrip('#')
            if len(hex_str) == 6:
                r = int(hex_str[0:2], 16) / 255.0
                g = int(hex_str[2:4], 16) / 255.0
                b = int(hex_str[4:6], 16) / 255.0
                return (r, g, b, 1.0)
            return (1.0, 1.0, 1.0, 1.0)

        def hex_to_vec4(self, hex_str):
            """Convert hex color string to vec4 tuple for shaders."""
            color = self.hex_to_color(hex_str)
            return color  # Return tuple, not list - Ren'Py requires tuples for vec4

        def build_shader_transform(self, preset_name, params_override=None):
            """
            Build a transform that applies a shader preset.

            Args:
                preset_name: Name of shader preset
                params_override: Optional dict of param overrides

            Returns:
                Transform function or None
            """
            preset = self.get_shader_preset(preset_name)
            if not preset:
                return None

            # Handle combined/stacked presets
            if "stack" in preset:
                return self._build_stacked_transform(preset, params_override)

            shader_name = preset.get("shader")
            if not shader_name:
                return None

            params = dict(preset.get("params", {}))
            if params_override:
                params.update(params_override)

            mesh_pad = preset.get("mesh_pad", 0)

            # Convert hex colors in params
            for key, value in params.items():
                if isinstance(value, str) and value.startswith("#"):
                    params[key] = self.hex_to_vec4(value)

            return self._create_transform(shader_name, params, mesh_pad)

        def _build_stacked_transform(self, preset, params_override=None):
            """Build transform for stacked/combined shader presets."""
            stack = preset.get("stack", [])
            if not stack:
                return None

            # Build transforms for each shader in stack
            transforms = []
            for shader_name in stack:
                t = self.build_shader_transform(shader_name, params_override)
                if t:
                    transforms.append(t)

            if not transforms:
                return None

            # Combine transforms
            mesh_pad = preset.get("mesh_pad", 0)
            return self._combine_transforms(transforms, mesh_pad)

        def _create_transform(self, shader_name, params, mesh_pad):
            """Create a Ren'Py transform with shader and params."""
            def transform_func(trans, st, at):
                # CRITICAL: mesh=True is required for shaders to work
                # It renders the child to a texture that the shader can sample
                trans.mesh = True
                trans.shader = shader_name
                for key, value in params.items():
                    setattr(trans, key, value)
                if mesh_pad:
                    if isinstance(mesh_pad, list):
                        trans.mesh_pad = tuple(mesh_pad)
                    else:
                        trans.mesh_pad = (mesh_pad, mesh_pad, mesh_pad, mesh_pad)
                return None
            return Transform(function=transform_func)

        def _combine_transforms(self, transforms, mesh_pad):
            """Combine multiple transforms into one."""
            # For now, return first transform
            # TODO: Implement proper shader stacking
            if transforms:
                return transforms[0]
            return None

# Global instance
default preset_manager = PresetManager()
