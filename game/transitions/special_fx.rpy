## special_fx.rpy - Special visual effects
##
## Screen shakes, flashes, and other dramatic effects.
## Use sparingly for impact.
##
## Related files: basic_transitions.rpy, character_animations.rpy
##
## Note: For character entrance/exit animations, see character_animations.rpy
## which loads transforms from transitions.json

################################################################################
## Screen Shake Effects
################################################################################

## Horizontal shake - impact, explosion
define hpunch = hpunch

## Vertical shake - earthquake, stomping
define vpunch = vpunch

## Custom shake - adjustable intensity
init python:
    def shake(duration=0.5, intensity=10):
        """
        Create a custom screen shake.

        Args:
            duration: How long the shake lasts
            intensity: How far the screen moves

        Example:
            $ renpy.with_statement(shake(0.3, 5))
        """
        return Move((0, 0), (intensity, intensity), duration, repeat=True, bounce=True)


################################################################################
## Flash Effects
################################################################################

## White flash - lightning, magic, revelation
define flash_white = Fade(0.1, 0.0, 0.3, color="#ffffff")

## Quick white flash
define flash_quick = Fade(0.05, 0.0, 0.1, color="#ffffff")

## Red flash - damage, danger
define flash_red = Fade(0.1, 0.0, 0.2, color="#ff0000")

## Blue flash - magic, cold
define flash_blue = Fade(0.1, 0.0, 0.2, color="#0066ff")


################################################################################
## Combined Effects
################################################################################

## Impact flash with shake
define impact = ComposeTransition(
    vpunch,
    after=flash_white
)

## Explosion effect
define explosion = ComposeTransition(
    hpunch,
    after=flash_red
)


################################################################################
## Blinds/Squares
################################################################################

## Blinds effect
define blinds_horizontal = ImageDissolve("images/transitions/blinds_h.png", 0.5, 0)
define blinds_vertical = ImageDissolve("images/transitions/blinds_v.png", 0.5, 0)

## Note: blinds effects require transition images in images/transitions/


################################################################################
## Dream/Memory Effects
################################################################################

## Dream sequence transition
define dream_in = Fade(1.0, 0.5, 1.0, color="#ffffff")
define dream_out = Fade(1.0, 0.5, 1.0, color="#ffffff")

## Flashback effect
define flashback_in = Fade(0.5, 0.3, 0.5, color="#000000")
define flashback_out = Fade(0.5, 0.3, 0.5, color="#000000")


################################################################################
## Usage Examples
################################################################################

## "Lightning strikes!" with flash_white
## "The ground shakes." with vpunch
## "An explosion rocks the building!" with explosion
## scene memory_location with flashback_in
