## preset_generator.rpy - Generate transforms from JSON presets
##
## Reads transition_presets.json at init and creates transform functions.
## Each preset becomes a callable: preset_slide_left_enter(xalign=0.5)
##
## Position types supported in JSON:
##   - xalign/yalign: Decimal positions (0.0-1.0)
##   - xoffset/yoffset: Pixel offsets from alignment
##   - x/y: Absolute pixel positions (converted to xpos/ypos)
##
## Usage:
##     show character at preset_slide_left_enter()
##     show character at preset_slide_left_enter(xalign=0.3)
##     show character at preset_pop_in_enter(), glow_blue
##
## Related files: transition_presets.json, shader_transforms.rpy

init -5 python:
    import json
    import os

    print(">>> preset_generator.rpy: init -5 starting")

    class PresetGenerator:
        """
        Loads transition presets from JSON and registers them as transform functions.
        Supports position-based animations with automatic delta calculation.
        """

        def __init__(self):
            self.presets = {}
            self.defaults = {}
            self._loaded = False

        def load(self):
            """Load presets from JSON file."""
            if self._loaded:
                return True

            filepath = os.path.join(config.gamedir, "presets", "transition_presets.json")
            if not os.path.exists(filepath):
                print(f"PresetGenerator: File not found: {filepath}")
                return False

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.defaults = data.get("defaults", {})
                self._parse_presets(data.get("presets", {}))
                self._loaded = True
                print(f"PresetGenerator: Loaded {len(self.presets)} presets")
                return True
            except Exception as e:
                print(f"PresetGenerator: Error loading presets: {e}")
                import traceback
                traceback.print_exc()
                return False

        def _parse_presets(self, data):
            """Parse preset definitions from JSON data."""
            for name, config in data.items():
                # Skip comment keys
                if name.startswith("_"):
                    continue
                # Use duck typing - check if it has keys() method (dict-like)
                if not hasattr(config, 'keys'):
                    continue
                self.presets[name] = self._normalize(config)

        def _normalize(self, config):
            """Apply defaults to a preset configuration."""
            result = {
                "start_position": {},
                "end_position": {},
                "alpha": {
                    "start": 1.0,
                    "end": 1.0
                },
                "rotation": {
                    "start": 0,
                    "end": 0
                },
                "scale": {
                    "start": 1.0,
                    "end": 1.0
                },
                "duration": self.defaults.get("duration", 0.4),
                "easing": self.defaults.get("easing", "easeout")
            }

            # Merge config into result (use duck typing - isinstance fails in Ren'Py)
            for key, val in config.items():
                # Check if both are dict-like using duck typing
                if hasattr(val, 'keys') and key in result and hasattr(result[key], 'update'):
                    result[key].update(val)
                else:
                    result[key] = val

            return result

        def _parse_position(self, pos_dict):
            """
            Parse a position dictionary and return structured position data.

            Returns dict with keys for each property type:
              - xalign, yalign: alignment values (0.0-1.0)
              - xoffset, yoffset: pixel offsets
              - xpos, ypos: absolute pixel positions
            """
            result = {
                "xalign": None,
                "yalign": None,
                "xoffset": None,
                "yoffset": None,
                "xpos": None,
                "ypos": None
            }

            if not pos_dict:
                return result

            # Parse each possible key
            if "xalign" in pos_dict:
                result["xalign"] = float(pos_dict["xalign"])
            if "yalign" in pos_dict:
                result["yalign"] = float(pos_dict["yalign"])
            if "xoffset" in pos_dict:
                result["xoffset"] = float(pos_dict["xoffset"])
            if "yoffset" in pos_dict:
                result["yoffset"] = float(pos_dict["yoffset"])
            if "x" in pos_dict:
                result["xpos"] = float(pos_dict["x"])
            if "y" in pos_dict:
                result["ypos"] = float(pos_dict["y"])

            return result

        def get_preset(self, name):
            """Get a preset by name."""
            self.load()
            return self.presets.get(name)

        def list_presets(self):
            """Get list of all preset names."""
            self.load()
            return list(self.presets.keys())

        def create_transform_func(self, name):
            """
            Create a callable transform function for a preset.

            Returns a function that takes optional position overrides
            and returns a Transform.
            """
            config = self.get_preset(name)
            if not config:
                print(f"PresetGenerator: Preset '{name}' not found")
                return None

            # Parse positions
            start_pos = self._parse_position(config.get("start_position", {}))
            end_pos = self._parse_position(config.get("end_position", {}))

            # Extract other properties
            alp = config["alpha"]
            rot = config["rotation"]
            scl = config["scale"]
            dur = config["duration"]
            ease = config["easing"]

            # Pre-calculate deltas
            da = alp["end"] - alp["start"]
            dr = rot["end"] - rot["start"]
            ds = scl["end"] - scl["start"]

            # Calculate position deltas (only for properties that exist in both)
            dx_align = None
            dy_align = None
            dx_offset = None
            dy_offset = None
            dx_pos = None
            dy_pos = None

            if start_pos["xalign"] is not None and end_pos["xalign"] is not None:
                dx_align = end_pos["xalign"] - start_pos["xalign"]
            if start_pos["yalign"] is not None and end_pos["yalign"] is not None:
                dy_align = end_pos["yalign"] - start_pos["yalign"]
            if start_pos["xoffset"] is not None and end_pos["xoffset"] is not None:
                dx_offset = end_pos["xoffset"] - start_pos["xoffset"]
            if start_pos["yoffset"] is not None and end_pos["yoffset"] is not None:
                dy_offset = end_pos["yoffset"] - start_pos["yoffset"]
            if start_pos["xpos"] is not None and end_pos["xpos"] is not None:
                dx_pos = end_pos["xpos"] - start_pos["xpos"]
            if start_pos["ypos"] is not None and end_pos["ypos"] is not None:
                dy_pos = end_pos["ypos"] - start_pos["ypos"]

            def preset_transform(xalign=None, yalign=None, xanchor=0.5, yanchor=1.0):
                """
                Returns a Transform that animates this preset.

                Args:
                    xalign: Override final horizontal alignment (0.0-1.0)
                    yalign: Override final vertical alignment (0.0-1.0)
                    xanchor: Horizontal anchor point
                    yanchor: Vertical anchor point
                """
                # Use defaults if not overridden
                final_xalign = xalign if xalign is not None else 0.5
                final_yalign = yalign if yalign is not None else 1.0

                def animation(trans, st, at):
                    # Calculate progress (0.0 to 1.0)
                    progress = min(1.0, st / dur) if dur > 0 else 1.0

                    # Apply easing
                    if ease == "easeout":
                        t = 1.0 - (1.0 - progress) ** 2
                    elif ease == "easein":
                        t = progress ** 2
                    elif ease == "ease":
                        t = progress * progress * (3.0 - 2.0 * progress)
                    else:  # linear
                        t = progress

                    # Set anchor points
                    trans.xanchor = xanchor
                    trans.yanchor = yanchor

                    # Apply position animations based on what's defined
                    if dx_align is not None:
                        trans.xalign = start_pos["xalign"] + dx_align * t
                    elif xalign is not None:
                        trans.xalign = xalign
                    else:
                        trans.xalign = final_xalign

                    if dy_align is not None:
                        trans.yalign = start_pos["yalign"] + dy_align * t
                    elif yalign is not None:
                        trans.yalign = yalign
                    else:
                        trans.yalign = final_yalign

                    if dx_offset is not None:
                        trans.xoffset = start_pos["xoffset"] + dx_offset * t
                    if dy_offset is not None:
                        trans.yoffset = start_pos["yoffset"] + dy_offset * t

                    if dx_pos is not None:
                        trans.xpos = start_pos["xpos"] + dx_pos * t
                    if dy_pos is not None:
                        trans.ypos = start_pos["ypos"] + dy_pos * t

                    # Interpolate other properties
                    trans.alpha = alp["start"] + da * t
                    trans.rotate = rot["start"] + dr * t
                    trans.zoom = scl["start"] + ds * t

                    # Done when progress reaches 1.0
                    if progress >= 1.0:
                        return None
                    return 0

                return Transform(function=animation)

            return preset_transform

        def register_all(self):
            """
            Register all presets as global transform functions.

            Creates functions named 'preset_<name>' for each preset.
            """
            self.load()
            count = 0
            for name in self.presets:
                func = self.create_transform_func(name)
                if func:
                    global_name = f"preset_{name}"
                    setattr(store, global_name, func)
                    count += 1

            print(f"PresetGenerator: Registered {count} transform functions")
            return count


# Global instance - created at init -4 (after class defined at -5)
init -4 python:
    preset_gen = PresetGenerator()


# Register all presets at init 1
init 1 python:
    preset_gen.register_all()
