## dialogbox_manager.rpy - Dialogbox preset manager
##
## Manages dialogbox presets, applies styles, handles sounds and transitions.
## Provides runtime API for switching presets and customizing dialogbox.
##
## Related files: dialogbox_loader.rpy, dialogbox.json

init -5 python:
    import math

    class DialogboxManager:
        """
        Manages dialogbox presets and provides runtime API.
        """

        def __init__(self):
            self._current_preset_name = None
            self._current_preset = None
            self._typing_channel_registered = False
            self._typing_playing = False
            self._position_override = None

        def initialize(self):
            """
            Initialize manager after loader is ready.
            Must be called after dialogbox_loader.load().
            """
            if not dialogbox_loader.is_loaded():
                print("DialogboxManager: Loader not ready")
                return False

            # Register typing audio channel
            self._register_typing_channel()

            # Set default preset
            default_name = dialogbox_loader.get_default_preset_name()
            self.set_preset(default_name)

            print(f"DialogboxManager: Initialized with preset '{default_name}'")
            return True

        def _register_typing_channel(self):
            """Register the typing sound audio channel."""
            if self._typing_channel_registered:
                return

            channel = dialogbox_loader.get_typing_channel()
            mixer = dialogbox_loader.get_typing_channel_mixer()

            try:
                renpy.music.register_channel(channel, mixer=mixer, loop=True)
                self._typing_channel_registered = True
                print(f"DialogboxManager: Registered audio channel '{channel}'")
            except Exception as e:
                print(f"DialogboxManager: Channel registration failed: {e}")

        def set_preset(self, name):
            """
            Set the current dialogbox preset.

            Args:
                name: Preset name from dialogbox.json

            Returns:
                True if preset was set, False if not found
            """
            preset = dialogbox_loader.get_preset(name)
            if preset is None:
                print(f"DialogboxManager: Preset '{name}' not found")
                return False

            self._current_preset_name = name
            self._current_preset = preset
            return True

        def get_current_preset_name(self):
            """Get the name of the current preset."""
            return self._current_preset_name

        def get_current_preset(self):
            """Get the current preset configuration dict."""
            return self._current_preset

        def set_position_override(self, xalign=None, yalign=None, xoffset=None, yoffset=None):
            """
            Set temporary position override for next dialogue.

            Args:
                xalign: Horizontal alignment (0.0-1.0)
                yalign: Vertical alignment (0.0-1.0)
                xoffset: Horizontal offset in pixels
                yoffset: Vertical offset in pixels
            """
            self._position_override = {
                "xalign": xalign,
                "yalign": yalign,
                "xoffset": xoffset,
                "yoffset": yoffset
            }

        def clear_position_override(self):
            """Clear any position override."""
            self._position_override = None

        def get_position(self):
            """
            Get current position settings (with override applied).

            Returns:
                Dict with xalign, yalign, xoffset, yoffset
            """
            if self._current_preset is None:
                return {"xalign": 0.5, "yalign": 1.0, "xoffset": 0, "yoffset": -30}

            pos = self._current_preset.get("position", {}).copy()

            # Apply overrides if set
            if self._position_override:
                for key, value in self._position_override.items():
                    if value is not None:
                        pos[key] = value

            return pos

        def get_background(self):
            """Get background configuration."""
            if self._current_preset is None:
                return None
            return self._current_preset.get("background")

        def get_namebox(self):
            """Get namebox configuration."""
            if self._current_preset is None:
                return None
            return self._current_preset.get("namebox")

        def get_name_style(self):
            """Get name text style configuration."""
            if self._current_preset is None:
                return {}
            return self._current_preset.get("name_style", {})

        def get_text_style(self):
            """Get dialogue text style configuration."""
            if self._current_preset is None:
                return {}
            return self._current_preset.get("text_style", {})

        def get_textshader(self):
            """Get textshader string for current preset."""
            if self._current_preset is None:
                return None
            text_style = self._current_preset.get("text_style", {})
            return text_style.get("textshader")

        def get_transitions(self):
            """Get transition names for enter/exit."""
            if self._current_preset is None:
                return {"enter": None, "exit": None}
            return self._current_preset.get("transitions", {"enter": None, "exit": None})

        def get_sounds(self):
            """Get sound configuration."""
            if self._current_preset is None:
                return {}
            return self._current_preset.get("sounds", {})

        def get_box_effect(self):
            """Get box effect name for current preset."""
            if self._current_preset is None:
                return None
            return self._current_preset.get("box_effect")

        def get_box_effect_config(self, effect_name=None):
            """
            Get box effect configuration.

            Args:
                effect_name: Effect name, or None to use current preset's effect

            Returns:
                Effect config dict or None
            """
            if effect_name is None:
                effect_name = self.get_box_effect()
            if effect_name is None:
                return None
            return dialogbox_loader.get_box_effect(effect_name)

        # Sound management

        def play_appear_sound(self):
            """Play the appear sound for current preset."""
            sounds = self.get_sounds()
            sound_file = sounds.get("appear")
            if sound_file:
                renpy.music.play(sound_file, channel='sound', loop=False)

        def play_dismiss_sound(self):
            """Play the dismiss sound for current preset."""
            sounds = self.get_sounds()
            sound_file = sounds.get("dismiss")
            if sound_file:
                renpy.music.play(sound_file, channel='sound', loop=False)

        def start_typing_loop(self):
            """Start the typing loop sound."""
            sounds = self.get_sounds()
            sound_file = sounds.get("typing_loop")
            if sound_file and not self._typing_playing:
                channel = dialogbox_loader.get_typing_channel()
                renpy.music.play(sound_file, channel=channel, loop=True, fadein=0.1)
                self._typing_playing = True

        def stop_typing_loop(self, fadeout=0.2):
            """Stop the typing loop sound."""
            if self._typing_playing:
                channel = dialogbox_loader.get_typing_channel()
                renpy.music.stop(channel=channel, fadeout=fadeout)
                self._typing_playing = False

        def play_text_blip(self):
            """Play a single text blip sound."""
            sounds = self.get_sounds()
            sound_file = sounds.get("text_blip")
            if sound_file:
                renpy.music.play(sound_file, channel='sound', loop=False)


# Create global manager instance
init -4 python:
    dialogbox_manager = DialogboxManager()


# Initialize manager after loader
init -3 python:
    dialogbox_manager.initialize()


# Helper functions for scripts

init python:

    def dialogbox_set(preset_name):
        """
        Set the dialogbox preset.

        Usage in script:
            $ dialogbox_set("dramatic")
            novy "This is important!"
        """
        return dialogbox_manager.set_preset(preset_name)

    def dialogbox_position(xalign=None, yalign=None, xoffset=None, yoffset=None):
        """
        Override dialogbox position for next dialogue.

        Usage in script:
            $ dialogbox_position(yalign=0.3)
            novy "I'm at the top of the screen!"
            $ dialogbox_manager.clear_position_override()
        """
        dialogbox_manager.set_position_override(xalign, yalign, xoffset, yoffset)

    def dialogbox_reset():
        """Reset dialogbox to default preset and clear overrides."""
        dialogbox_manager.clear_position_override()
        default = dialogbox_loader.get_default_preset_name()
        dialogbox_manager.set_preset(default)


# Box effect transforms

init -2 python:

    def create_shake_transform(intensity=3, speed=15):
        """
        Create a shake/jitter transform for the dialogbox.

        Args:
            intensity: Pixel range for shake
            speed: Speed of shake (updates per second)

        Returns:
            Transform function
        """
        def shake_func(trans, st, at):
            import random
            trans.xoffset = random.uniform(-intensity, intensity)
            trans.yoffset = random.uniform(-intensity, intensity)
            return 1.0 / speed

        return Transform(function=shake_func)

    def create_pulse_transform(min_scale=0.98, max_scale=1.02, speed=2.0):
        """
        Create a pulse transform for the dialogbox.

        Args:
            min_scale: Minimum scale
            max_scale: Maximum scale
            speed: Pulse frequency

        Returns:
            Transform function
        """
        def pulse_func(trans, st, at):
            # Use sine wave for smooth pulsing
            t = st * speed
            scale_range = max_scale - min_scale
            trans.zoom = min_scale + (math.sin(t * 2 * math.pi) + 1) / 2 * scale_range
            return 0

        return Transform(function=pulse_func)

    def create_glow_transform(intensity=0.2, speed=1.5, color="#FFFFFF"):
        """
        Create a glow/brightness pulse transform.
        Uses matrixcolor for brightness effect.

        Args:
            intensity: Brightness variation (0.0-1.0)
            speed: Pulse frequency
            color: Glow color (currently unused, brightness only)

        Returns:
            Transform function
        """
        def glow_func(trans, st, at):
            t = st * speed
            # Brightness ranges from 1.0 - intensity to 1.0 + intensity
            brightness = 1.0 + math.sin(t * 2 * math.pi) * intensity
            trans.matrixcolor = BrightnessMatrix(brightness - 1.0)
            return 0

        return Transform(function=glow_func)

    def get_box_effect_transform(effect_name):
        """
        Get the transform for a box effect by name.

        Args:
            effect_name: Effect name from dialogbox.json

        Returns:
            Transform or None
        """
        config = dialogbox_manager.get_box_effect_config(effect_name)
        if config is None:
            return None

        if effect_name == "shake":
            return create_shake_transform(
                intensity=config.get("intensity", 3),
                speed=config.get("speed", 15)
            )
        elif effect_name == "pulse":
            return create_pulse_transform(
                min_scale=config.get("min_scale", 0.98),
                max_scale=config.get("max_scale", 1.02),
                speed=config.get("speed", 2.0)
            )
        elif effect_name == "glow":
            return create_glow_transform(
                intensity=config.get("intensity", 0.2),
                speed=config.get("speed", 1.5),
                color=config.get("color", "#FFFFFF")
            )

        return None
