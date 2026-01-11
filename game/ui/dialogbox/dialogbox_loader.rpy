## dialogbox_loader.rpy - Dialogbox JSON configuration loader
##
## Loads dialogbox presets from JSON configuration file.
## Provides access to preset definitions for the dialogbox manager.
##
## Related files: dialogbox.json, dialogbox_manager.rpy

init -10 python:
    import json
    import os

    class DialogboxLoader:
        """
        Loads and provides access to dialogbox configuration from JSON.
        """

        def __init__(self):
            self._config = None
            self._settings = {}
            self._presets = {}
            self._box_effects = {}
            self._loaded = False

        def load(self, config_path="ui/dialogbox/dialogbox.json"):
            """
            Load dialogbox configuration from JSON file.

            Args:
                config_path: Path to JSON file relative to game directory
            """
            try:
                full_path = os.path.join(config.gamedir, config_path)

                with open(full_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)

                self._settings = self._config.get("settings", {})
                self._presets = self._config.get("presets", {})
                self._box_effects = self._config.get("box_effects", {})
                self._loaded = True

                print(f"DialogboxLoader: Loaded {len(self._presets)} presets")
                return True

            except FileNotFoundError:
                print(f"DialogboxLoader: Config file not found: {config_path}")
                return False
            except json.JSONDecodeError as e:
                print(f"DialogboxLoader: JSON parse error: {e}")
                return False
            except Exception as e:
                print(f"DialogboxLoader: Error loading config: {e}")
                return False

        def is_loaded(self):
            """Check if configuration has been loaded."""
            return self._loaded

        def get_settings(self):
            """Get global settings."""
            return self._settings

        def get_default_preset_name(self):
            """Get the name of the default preset."""
            return self._settings.get("default_preset", "standard")

        def get_fonts(self):
            """Get font configuration."""
            return self._settings.get("fonts", {})

        def get_preset(self, name):
            """
            Get a specific preset by name.

            Args:
                name: Preset name

            Returns:
                Preset dict or None if not found
            """
            return self._presets.get(name)

        def get_all_presets(self):
            """Get all preset names."""
            return list(self._presets.keys())

        def get_box_effect(self, name):
            """
            Get a box effect configuration.

            Args:
                name: Effect name

            Returns:
                Effect dict or None if not found
            """
            return self._box_effects.get(name)

        def get_all_box_effects(self):
            """Get all box effect names."""
            return list(self._box_effects.keys())

        def get_typing_channel(self):
            """Get the audio channel name for typing sounds."""
            return self._settings.get("typing_channel", "typing")

        def get_typing_channel_mixer(self):
            """Get the mixer for the typing channel."""
            return self._settings.get("typing_channel_mixer", "sfx")


# Create global loader instance
init -9 python:
    dialogbox_loader = DialogboxLoader()
    dialogbox_loader.load()
