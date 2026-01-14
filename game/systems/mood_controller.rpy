## mood_controller.rpy - High-level mood/preset controller
##
## Provides the main API for applying presets to scenes, characters,
## dialog boxes, and backgrounds. Combines transitions from
## character_animations.rpy with shader effects from preset_manager.
##
## Usage:
##   $ mood.set("dream_sequence")
##   show novy at mood_enter("novy")
##   hide novy at mood_exit("novy")
##   $ mood.reset()
##
## Related files: preset_manager.rpy, presets/presets.json,
##                character_animations.rpy, transitions/transitions.json

init python:

    class MoodController:
        """
        High-level controller for applying scene presets.

        Manages the current mood state and provides methods for
        character choreography by combining transitions with shaders.
        """

        def __init__(self):
            self.current = None
            self.current_name = "default"
            self._character_positions = {}

        def set(self, preset_name, apply_transition=True):
            """
            Set the current scene mood.

            Args:
                preset_name: Name of preset from presets.json
                apply_transition: Whether to apply enter transition
            """
            preset = preset_manager.get_scene_preset(preset_name)
            if not preset:
                renpy.log("Mood: Preset '{}' not found".format(preset_name))
                return False

            self.current = preset
            self.current_name = preset_name

            # Apply ambient audio if specified
            self._apply_ambient(preset.get("active", {}).get("ambient"))

            return True

        def reset(self):
            """Reset to default preset."""
            self.set("default")
            self._character_positions.clear()

        def get_active_shader(self):
            """Get the current active shader preset name."""
            if not self.current:
                return None
            active = self.current.get("active", {})
            shader = active.get("shader")
            if shader:
                return shader.get("preset")
            return None

        def get_active_alpha(self):
            """Get the current active alpha value."""
            if not self.current:
                return 1.0
            return self.current.get("active", {}).get("alpha", 1.0)

        def _apply_ambient(self, ambient_config):
            """Apply ambient audio from preset."""
            if not ambient_config:
                renpy.music.stop(channel="ambient", fadeout=1.0)
                return

            sound = ambient_config.get("sound")
            if not sound:
                return

            volume = ambient_config.get("volume", 0.5)
            fadein = ambient_config.get("fadein", 1.0)
            loop = ambient_config.get("loop", True)

            if renpy.loadable(sound):
                renpy.music.play(sound, channel="ambient", fadein=fadein, loop=loop)
                renpy.music.set_volume(volume, channel="ambient")

        def get_character_config(self, character_name):
            """
            Get character-specific config or default.
            """
            if not self.current:
                return {}

            chars = self.current.get("characters", {})
            return chars.get(character_name, chars.get("default", {}))

        def get_lead_in(self, character_name):
            """Get lead_in animation config for a character."""
            config = self.get_character_config(character_name)
            return config.get("lead_in", {})

        def get_lead_out(self, character_name):
            """Get lead_out animation config for a character."""
            config = self.get_character_config(character_name)
            return config.get("lead_out", {})

        def build_enter_transform(self, character_name, xalign=0.5, yalign=1.0):
            """
            Build transform for character entrance.

            Combines transition from character_animations with shader effects.

            Args:
                character_name: Character identifier
                xalign: Final horizontal position (0.0=left, 1.0=right)
                yalign: Final vertical position (0.0=top, 1.0=bottom)

            Returns:
                Transform for entrance animation with shader
            """
            lead_in = self.get_lead_in(character_name)

            # Get transition name and shader config
            transition_name = lead_in.get("transition", "slide_left_enter")
            shader_config = lead_in.get("shader")

            # Get the base transition function from char_anim_factory
            base_transform_func = char_anim_factory.get_transform(transition_name)
            if not base_transform_func:
                renpy.log("Mood: Transition '{}' not found".format(transition_name))
                # Fallback to default
                base_transform_func = char_anim_factory.get_transform("slide_left_enter")

            # Store position for exit
            self._character_positions[character_name] = (xalign, yalign)

            # If no shader, just return the base transition
            if not shader_config:
                return base_transform_func(xalign=xalign, yalign=yalign)

            # Get shader preset and fade duration
            shader_preset = shader_config.get("preset")
            shader_fade = shader_config.get("fade_duration", 0.5)

            # Build combined transform with transition + fading shader
            return self._build_combined_enter_transform(
                base_transform_func, xalign, yalign,
                shader_preset, shader_fade
            )

        def build_exit_transform(self, character_name, xalign=None, yalign=None):
            """
            Build transform for character exit.

            Combines transition from character_animations with shader effects.

            Args:
                character_name: Character identifier
                xalign: Starting horizontal position (uses stored if None)
                yalign: Starting vertical position (uses stored if None)

            Returns:
                Transform for exit animation with shader
            """
            lead_out = self.get_lead_out(character_name)

            # Get stored position or defaults
            stored = self._character_positions.get(character_name, (0.5, 1.0))
            if xalign is None:
                xalign = stored[0]
            if yalign is None:
                yalign = stored[1]

            # Clear stored position
            if character_name in self._character_positions:
                del self._character_positions[character_name]

            # Get transition name and shader config
            transition_name = lead_out.get("transition", "fade_left_exit")
            shader_config = lead_out.get("shader")

            # Get the base transition function from char_anim_factory
            base_transform_func = char_anim_factory.get_transform(transition_name)
            if not base_transform_func:
                renpy.log("Mood: Transition '{}' not found".format(transition_name))
                base_transform_func = char_anim_factory.get_transform("fade_left_exit")

            # If no shader, just return the base transition
            if not shader_config:
                return base_transform_func(xalign=xalign, yalign=yalign)

            # Get shader preset and fade duration
            shader_preset = shader_config.get("preset")
            shader_fade = shader_config.get("fade_duration", 0.5)

            # Build combined transform with transition + fading shader
            return self._build_combined_exit_transform(
                base_transform_func, xalign, yalign,
                shader_preset, shader_fade
            )

        def _build_combined_enter_transform(self, base_func, xalign, yalign,
                                            shader_preset, shader_fade):
            """
            Build a transform that combines base transition with shader fade-out.

            For entrances, shader starts strong and fades out.
            """
            # Get shader params from preset_manager
            shader_params = self._get_shader_params(shader_preset)

            # Get the base transform
            base_transform = base_func(xalign=xalign, yalign=yalign)

            # Check if shader is animated (needs continuous updates)
            is_animated = shader_params.get("animated", False) if shader_params else False

            def combined_func(trans, st, at):
                # Apply base transform first
                if hasattr(base_transform, 'function') and base_transform.function:
                    base_result = base_transform.function(trans, st, at)
                else:
                    base_result = None

                # Apply shader with fade-out effect
                if shader_params:
                    if shader_fade > 0:
                        # Calculate shader intensity (starts at 1, fades to 0)
                        shader_progress = min(1.0, st / shader_fade)
                        shader_intensity = 1.0 - shader_progress
                    else:
                        # No fade, full intensity
                        shader_intensity = 1.0

                    # Apply shader if still visible
                    if shader_intensity > 0.01:
                        self._apply_shader_to_transform(
                            trans, shader_params, shader_intensity
                        )
                        # Keep updating if shader is still active AND (animated OR still fading)
                        if is_animated or shader_intensity > 0.01:
                            return 0  # Request next frame

                # Return base result if shader done, or 0 if shader still needs updates
                return base_result

            return Transform(function=combined_func)

        def _build_combined_exit_transform(self, base_func, xalign, yalign,
                                           shader_preset, shader_fade):
            """
            Build a transform that combines base transition with shader fade-in.

            For exits, shader starts weak and gets stronger.
            """
            shader_params = self._get_shader_params(shader_preset)

            base_transform = base_func(xalign=xalign, yalign=yalign)

            # Check if shader is animated (needs continuous updates)
            is_animated = shader_params.get("animated", False) if shader_params else False

            def combined_func(trans, st, at):
                # Apply base transform first
                if hasattr(base_transform, 'function') and base_transform.function:
                    base_result = base_transform.function(trans, st, at)
                else:
                    base_result = None

                # Apply shader with fade-in effect
                if shader_params:
                    if shader_fade > 0:
                        # Calculate shader intensity (starts at 0, fades to 1)
                        shader_progress = min(1.0, st / shader_fade)
                        shader_intensity = shader_progress
                    else:
                        # No fade, full intensity
                        shader_intensity = 1.0

                    # Apply shader
                    if shader_intensity > 0.01:
                        self._apply_shader_to_transform(
                            trans, shader_params, shader_intensity
                        )
                        # Keep updating if animated
                        if is_animated:
                            return 0

                return base_result

            return Transform(function=combined_func)

        def _get_shader_params(self, shader_preset):
            """Get shader parameters from preset_manager."""
            if not shader_preset:
                return None

            preset = preset_manager.get_shader_preset(shader_preset)
            if not preset:
                return None

            shader_name = preset.get("shader")
            params = dict(preset.get("params", {}))
            mesh_pad = preset.get("mesh_pad", 0)
            animated = preset.get("animated", False)

            # Convert hex colors
            for key, value in params.items():
                if isinstance(value, str) and value.startswith("#"):
                    params[key] = preset_manager.hex_to_vec4(value)

            return {
                "shader": shader_name,
                "params": params,
                "mesh_pad": mesh_pad,
                "animated": animated
            }

        def _apply_shader_to_transform(self, trans, shader_params, intensity):
            """Apply shader parameters to transform with intensity scaling."""
            if not shader_params:
                return

            shader_name = shader_params.get("shader")
            params = shader_params.get("params", {})
            mesh_pad = shader_params.get("mesh_pad", 0)

            if shader_name:
                # CRITICAL: mesh=True is required for shaders to work
                # Without it, the child isn't rendered to texture and shader can't sample
                trans.mesh = True
                trans.shader = shader_name

            # Apply mesh_pad for effects that render outside bounds (glow, blur, etc)
            if mesh_pad:
                if isinstance(mesh_pad, list):
                    trans.mesh_pad = tuple(mesh_pad)
                elif isinstance(mesh_pad, (int, float)):
                    pad = int(mesh_pad)
                    trans.mesh_pad = (pad, pad, pad, pad)

            # Params that should scale with intensity (for fade in/out effects)
            intensity_params = [
                "u_amount", "u_strength", "u_intensity", "u_blur_amount", "u_radius",
                "u_outer_strength", "u_inner_strength"  # Glow params
            ]

            # Apply params, scaling intensity-based ones
            for key, value in params.items():
                # Convert lists to tuples (Ren'Py requires tuples for vec types)
                if isinstance(value, list):
                    value = tuple(value)

                if key in intensity_params:
                    # Scale by intensity
                    if isinstance(value, (int, float)):
                        setattr(trans, key, value * intensity)
                    else:
                        setattr(trans, key, value)
                else:
                    setattr(trans, key, value)

        def get_transition(self, direction="enter"):
            """
            Get Ren'Py transition for scene enter/exit.
            """
            if not self.current:
                return Dissolve(0.5)

            trans_config = self.current.get("transition", {}).get(direction, {})
            trans_type = trans_config.get("type", "dissolve")
            duration = trans_config.get("duration", 0.5)

            if trans_type == "dissolve":
                return Dissolve(duration)
            elif trans_type == "fade":
                color = trans_config.get("color", "#000000")
                return Fade(duration / 2, 0, duration / 2, color=color)
            else:
                return Dissolve(duration)

        def get_dialogbox_config(self):
            """Get dialog box configuration from current preset."""
            if not self.current:
                return {}
            return self.current.get("dialogbox", {})


# Global instance
default mood = MoodController()


# Callable functions for use in show/hide statements
init python:

    def mood_enter_func(character_name="default", xalign=0.5, yalign=1.0):
        """
        Returns a transform for mood-aware character entrance.

        Usage:
            show novy at mood_enter_func("novy")
            show novy at mood_enter_func("novy", xalign=0.3)
        """
        return mood.build_enter_transform(character_name, xalign, yalign)

    def mood_exit_func(character_name="default", xalign=None, yalign=None):
        """
        Returns a transform for mood-aware character exit.

        Usage:
            hide novy at mood_exit_func("novy")
        """
        return mood.build_exit_transform(character_name, xalign, yalign)


# ATL transform wrappers for cleaner syntax
transform mood_enter(char="default", xalign=0.5, yalign=1.0):
    function renpy.curry(lambda trans, st, at, c=char, x=xalign, y=yalign: mood.build_enter_transform(c, x, y).function(trans, st, at))

transform mood_exit(char="default"):
    function renpy.curry(lambda trans, st, at, c=char: mood.build_exit_transform(c).function(trans, st, at))
