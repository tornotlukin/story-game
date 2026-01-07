## dice_system.rpy - Dice rolling mechanics
##
## Provides dice rolling functionality for RPG-style mechanics.
## Supports standard dice notation (1d20, 2d6+3, etc.)
##
## Related files: state_manager.rpy (for stat-based checks)

init python:
    import random

    class DiceRoller:
        """
        Handles all dice rolling mechanics.
        Supports standard RPG dice notation.
        """

        def __init__(self):
            pass

        def roll(self, dice_string):
            """
            Roll dice using standard notation.

            Args:
                dice_string: Dice notation like "1d20", "2d6+3", "1d8-1"

            Returns:
                Tuple of (total, list of individual rolls)

            Example:
                total, rolls = dice.roll("2d6")
                total, rolls = dice.roll("1d20+5")
            """
            # Parse the dice string
            dice_string = dice_string.lower().replace(" ", "")

            # Handle modifier
            modifier = 0
            if '+' in dice_string:
                parts = dice_string.split('+')
                dice_string = parts[0]
                modifier = int(parts[1])
            elif '-' in dice_string:
                parts = dice_string.split('-')
                dice_string = parts[0]
                modifier = -int(parts[1])

            # Parse XdY
            if 'd' in dice_string:
                num_dice, die_size = dice_string.split('d')
                num_dice = int(num_dice) if num_dice else 1
                die_size = int(die_size)
            else:
                # Just a number, return it
                return (int(dice_string) + modifier, [int(dice_string)])

            # Roll the dice
            rolls = [random.randint(1, die_size) for _ in range(num_dice)]
            total = sum(rolls) + modifier

            return (total, rolls)

        def roll_with_advantage(self, dice_string):
            """
            Roll twice and take the higher result.

            Args:
                dice_string: Dice notation

            Returns:
                Tuple of (best_total, all_rolls)

            Example:
                total, rolls = dice.roll_with_advantage("1d20")
            """
            roll1 = self.roll(dice_string)
            roll2 = self.roll(dice_string)

            if roll1[0] >= roll2[0]:
                return (roll1[0], [roll1[1], roll2[1]])
            else:
                return (roll2[0], [roll1[1], roll2[1]])

        def roll_with_disadvantage(self, dice_string):
            """
            Roll twice and take the lower result.

            Args:
                dice_string: Dice notation

            Returns:
                Tuple of (worst_total, all_rolls)

            Example:
                total, rolls = dice.roll_with_disadvantage("1d20")
            """
            roll1 = self.roll(dice_string)
            roll2 = self.roll(dice_string)

            if roll1[0] <= roll2[0]:
                return (roll1[0], [roll1[1], roll2[1]])
            else:
                return (roll2[0], [roll1[1], roll2[1]])

        def skill_check(self, stat_value, difficulty, dice="1d20"):
            """
            Perform a skill check against a difficulty.

            Args:
                stat_value: The stat/skill modifier to add
                difficulty: The target number to meet or beat
                dice: The dice to roll (default "1d20")

            Returns:
                Tuple of (success, roll_total, final_total)

            Example:
                success, roll, total = dice.skill_check(
                    game_state.get_stat("charisma"),
                    difficulty=15
                )
            """
            roll_total, rolls = self.roll(dice)
            final_total = roll_total + stat_value
            success = final_total >= difficulty

            return (success, roll_total, final_total)

# Global instance
default dice = DiceRoller()
