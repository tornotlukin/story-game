## transition_loader.rpy - JSON config loader for transitions
##
## Loads transition configurations from transitions.json and provides
## access to transition parameters with default fallbacks.
##
## Related files: transitions.json, character_animations.rpy

init -10 python:
    import json

    class TransitionLoader:
        """
        Loads and manages transition configurations from JSON.
        Provides default fallbacks for missing parameters.
        """

        def __init__(self):
            self.settings = {}
            self.transitions = {}
            self._loaded = False

        def load(self, filepath="transitions/transitions.json"):
            """
            Load transition configurations from JSON file.

            Args:
                filepath: Path to JSON file relative to game directory

            Returns:
                True if loaded successfully, False otherwise
            """
            try:
                with renpy.open_file(filepath) as f:
                    data = json.load(f)

                self.settings = data.get("settings", {})
                self.transitions = data.get("transitions", {})
                self._loaded = True

                return True

            except Exception as e:
                print(f"TransitionLoader: Failed to load {filepath}: {e}")
                self._loaded = False
                return False

        def get_default(self, key):
            """
            Get a default value from settings.

            Args:
                key: Setting key (without 'default_' prefix)

            Returns:
                Default value or None if not found
            """
            return self.settings.get(f"default_{key}")

        def get_transition(self, name):
            """
            Get a transition config by name, with defaults applied.

            Args:
                name: Transition name as defined in JSON

            Returns:
                Dict with all parameters, or None if not found
            """
            if name not in self.transitions:
                print(f"TransitionLoader: Transition '{name}' not found")
                return None

            # Skip comment keys and non-dict values
            value = self.transitions[name]
            if name.startswith("_") or not isinstance(value, dict):
                return None

            config = value.copy()

            # Apply defaults for missing keys
            defaults = {
                "duration": self.get_default("duration") or 0.4,
                "easing": self.get_default("easing") or "ease_out",
                "offset": self.get_default("offset") or 200,
                "fade": self.get_default("fade") if self.get_default("fade") is not None else True,
                "sound_volume": self.get_default("sound_volume") or 0.8,
                "delay": 0,
                "start_alpha": 0.0 if config.get("type") == "entrance" else 1.0,
                "end_alpha": 1.0 if config.get("type") == "entrance" else 0.0,
                "scale": False,
                "start_scale": 1.0,
                "end_scale": 1.0,
                "rotate": 0,
                "sound": None,
                "sound_delay": 0
            }

            for key, default_value in defaults.items():
                if key not in config:
                    config[key] = default_value

            return config

        def get_all_transitions(self):
            """
            Get all transition names (excludes comment keys starting with _).

            Returns:
                List of transition names
            """
            return [name for name in self.transitions.keys()
                    if not name.startswith("_") and isinstance(self.transitions[name], dict)]

        def get_transitions_by_type(self, transition_type):
            """
            Get all transitions of a specific type.

            Args:
                transition_type: 'entrance', 'exit', or 'effect'

            Returns:
                Dict of matching transitions
            """
            return {
                name: config
                for name, config in self.transitions.items()
                if not name.startswith("_")
                and isinstance(config, dict)
                and config.get("type") == transition_type
            }

        def is_loaded(self):
            """Check if config has been loaded."""
            return self._loaded


# Global loader instance (created and loaded at init time)
init -6 python:
    transition_loader = TransitionLoader()
    transition_loader.load()
