## state_manager.rpy - Core state and variable management
##
## Handles game state, flags, and persistent data tracking.
## This is the central hub for all game state operations.
##
## Related files: None (core system)

init python:
    class GameState:
        """
        Central state management for the game.
        Tracks flags, variables, and game progress.
        """

        def __init__(self):
            self.flags = {}
            self.stats = {
                'strength': 10,
                'dexterity': 10,
                'constitution': 10,
                'intelligence': 10,
                'wisdom': 10,
                'charisma': 10
            }
            self.variables = {}

        def set_flag(self, flag_name, value=True):
            """
            Set a boolean flag.

            Args:
                flag_name: Name of the flag to set
                value: Boolean value (default True)

            Example:
                game_state.set_flag("met_merchant")
                game_state.set_flag("door_locked", False)
            """
            self.flags[flag_name] = value

        def has_flag(self, flag_name):
            """
            Check if a flag is set and True.

            Args:
                flag_name: Name of the flag to check

            Returns:
                Boolean - True if flag exists and is True

            Example:
                if game_state.has_flag("met_merchant"):
                    jump merchant_greeting
            """
            return self.flags.get(flag_name, False)

        def get_flag(self, flag_name, default=False):
            """
            Get a flag's value with optional default.

            Args:
                flag_name: Name of the flag
                default: Value to return if flag doesn't exist

            Returns:
                The flag's value or default
            """
            return self.flags.get(flag_name, default)

        def set_variable(self, var_name, value):
            """
            Set a named variable to any value.

            Args:
                var_name: Name of the variable
                value: Any value to store

            Example:
                game_state.set_variable("gold", 100)
                game_state.set_variable("player_name", "Hero")
            """
            self.variables[var_name] = value

        def get_variable(self, var_name, default=None):
            """
            Get a variable's value with optional default.

            Args:
                var_name: Name of the variable
                default: Value to return if variable doesn't exist

            Returns:
                The variable's value or default
            """
            return self.variables.get(var_name, default)

        def modify_stat(self, stat_name, amount):
            """
            Modify a stat by a given amount (can be negative).

            Args:
                stat_name: Name of the stat to modify
                amount: Amount to add (negative to subtract)

            Returns:
                New stat value, or None if stat doesn't exist

            Example:
                game_state.modify_stat("strength", 2)
                game_state.modify_stat("charisma", -1)
            """
            if stat_name in self.stats:
                self.stats[stat_name] += amount
                return self.stats[stat_name]
            return None

        def get_stat(self, stat_name):
            """
            Get a stat's current value.

            Args:
                stat_name: Name of the stat

            Returns:
                Stat value or 0 if not found
            """
            return self.stats.get(stat_name, 0)

# Global instance - saved with game saves
default game_state = GameState()
