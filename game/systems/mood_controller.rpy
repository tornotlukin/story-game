## mood_controller.rpy - High-level mood/preset controller
##
## Provides the main API for applying presets to scenes, characters,
## dialog boxes, and backgrounds.
##
## Usage:
##   $ mood.set("dream_sequence")
##   show novy at mood_enter("novy")
##   hide novy at mood_exit("novy")
##   $ mood.reset()
##
## Related files: preset_manager.rpy, presets/presets.json

init python:

    class MoodController:
        """
        High-level controller for applying scene presets.

        Manages the current mood state and provides methods for
        character choreography, transitions, and effects.
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

            # Apply ambient audio
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

        def build_enter_transform(self, character_name, override=None):
            """
            Build transform for character entrance with shader and sound.

            Args:
                character_name: Character identifier
                override: Optional dict to override lead_in properties

            Returns:
                ATL transform for entrance animation
            """
            lead_in = dict(self.get_lead_in(character_name))
            if override:
                lead_in.update(override)

            start = lead_in.get("start", [-0.3, 1.0])
            end = lead_in.get("end", [0.5, 1.0])
            speed = lead_in.get("speed", 0.5)
            delay = lead_in.get("delay", 0.0)
            easing = lead_in.get("easing", "ease_out")
            alpha_config = lead_in.get("alpha", {"start": 0.0, "end": 1.0})
            sound = lead_in.get("sound")
            shader_config = lead_in.get("shader")

            # Store final position
            self._character_positions[character_name] = end

            # Get shader transform if specified
            shader_preset = None
            shader_fade = 0.0
            if shader_config:
                shader_preset = shader_config.get("preset")
                shader_fade = shader_config.get("fade_duration", speed)

            return self._build_full_transform(
                start, end, speed, delay, easing,
                alpha_config.get("start", 0.0),
                alpha_config.get("end", 1.0),
                sound,
                shader_preset,
                shader_fade,
                is_enter=True
            )

        def build_exit_transform(self, character_name, override=None):
            """
            Build transform for character exit with shader and sound.
            """
            lead_out = dict(self.get_lead_out(character_name))
            if override:
                lead_out.update(override)

            # Start from current position if not specified
            start = lead_out.get("start")
            if start is None:
                start = self._character_positions.get(character_name, [0.5, 1.0])

            end = lead_out.get("end", [1.3, 1.0])
            speed = lead_out.get("speed", 0.5)
            delay = lead_out.get("delay", 0.0)
            easing = lead_out.get("easing", "ease_in")
            alpha_config = lead_out.get("alpha", {"start": 1.0, "end": 0.0})
            sound = lead_out.get("sound")
            shader_config = lead_out.get("shader")

            # Clear position on exit
            if character_name in self._character_positions:
                del self._character_positions[character_name]

            # Get shader transform if specified
            shader_preset = None
            shader_fade = 0.0
            if shader_config:
                shader_preset = shader_config.get("preset")
                shader_fade = shader_config.get("fade_duration", speed)

            return self._build_full_transform(
                start, end, speed, delay, easing,
                alpha_config.get("start", 1.0),
                alpha_config.get("end", 0.0),
                sound,
                shader_preset,
                shader_fade,
                is_enter=False
            )

        def _build_full_transform(self, start, end, speed, delay, easing,
                                   alpha_start, alpha_end, sound,
                                   shader_preset, shader_fade, is_enter):
            """Build ATL transform with movement, alpha, sound, and shader."""
            easing_func = self._get_easing(easing)

            # Get shader transform if we have a preset
            shader_transform = None
            if shader_preset:
                shader_transform = preset_manager.build_shader_transform(shader_preset)

            # Track state across calls
            state = {"sound_played": False, "started": False}

            def transform_func(trans, st, at):
                # Play sound on first frame (after delay)
                if not state["sound_played"] and sound and st >= delay:
                    if renpy.loadable(sound):
                        renpy.play(sound, channel="sound")
                    state["sound_played"] = True

                # Handle delay
                if st < delay:
                    trans.xalign = start[0]
                    trans.yalign = start[1]
                    trans.alpha = alpha_start
                    return 0

                # Calculate progress
                effective_st = st - delay
                progress = min(1.0, effective_st / speed) if speed > 0 else 1.0
                eased = easing_func(progress)

                # Movement
                trans.xalign = start[0] + (end[0] - start[0]) * eased
                trans.yalign = start[1] + (end[1] - start[1]) * eased

                # Alpha
                trans.alpha = alpha_start + (alpha_end - alpha_start) * eased

                # Shader effect (fades out for enter, fades in for exit)
                if shader_transform and shader_fade > 0:
                    shader_progress = min(1.0, effective_st / shader_fade) if shader_fade > 0 else 1.0
                    # For enter: shader starts strong, fades out
                    # For exit: shader starts weak, gets stronger
                    if is_enter:
                        shader_intensity = 1.0 - shader_progress
                    else:
                        shader_intensity = shader_progress

                    # Apply shader with intensity (modulate via alpha-like effect)
                    if shader_intensity > 0.01:
                        # Apply the shader transform
                        if hasattr(shader_transform, 'function'):
                            shader_transform.function(trans, st, at)

                # Continue or finish
                if progress >= 1.0:
                    return None
                return 0

            return Transform(function=transform_func)

        def _get_easing(self, name):
            """Get easing function by name."""
            if name == "linear":
                return lambda t: t
            elif name == "ease_in":
                return lambda t: t * t
            elif name == "ease_out":
                return lambda t: 1 - (1 - t) * (1 - t)
            elif name == "ease_in_out":
                return lambda t: t * t * (3 - 2 * t)
            elif name == "bounce":
                def bounce(t):
                    if t < 0.5:
                        return 2 * t * t
                    else:
                        t = t - 0.75
                        return 1 - 2 * t * t
                return bounce
            elif name == "elastic":
                import math
                def elastic(t):
                    if t == 0 or t == 1:
                        return t
                    return pow(2, -10 * t) * math.sin((t - 0.1) * 5 * math.pi) + 1
                return elastic
            else:
                return lambda t: t

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


# Callable transform functions for use in show/hide statements
init python:

    def mood_enter_func(character_name="default"):
        """
        Returns a transform for mood-aware character entrance.

        Usage:
            show novy at mood_enter_func("novy")
            show novy at mood_enter_func()  # uses "default"
        """
        return mood.build_enter_transform(character_name)

    def mood_exit_func(character_name="default"):
        """
        Returns a transform for mood-aware character exit.

        Usage:
            hide novy at mood_exit_func("novy")
            hide novy at mood_exit_func()  # uses "default"
        """
        return mood.build_exit_transform(character_name)


# ATL transforms that call the functions
transform mood_enter(char="default"):
    function renpy.curry(lambda trans, st, at, c=char: mood.build_enter_transform(c).function(trans, st, at))

transform mood_exit(char="default"):
    function renpy.curry(lambda trans, st, at, c=char: mood.build_exit_transform(c).function(trans, st, at))
