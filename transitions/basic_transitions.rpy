## basic_transitions.rpy - Standard transition effects
##
## Common transition definitions for scene changes.
## Use these for consistent visual flow throughout the game.
##
## Related files: special_fx.rpy

################################################################################
## Dissolve Transitions
################################################################################

## Standard dissolve - general purpose
define dissolve = Dissolve(0.5)

## Quick dissolve - for rapid changes
define quick_dissolve = Dissolve(0.2)

## Slow dissolve - for dramatic moments
define slow_dissolve = Dissolve(1.0)

## Very slow dissolve - for contemplative scenes
define very_slow_dissolve = Dissolve(2.0)


################################################################################
## Fade Transitions
################################################################################

## Fade to black and back
define fade = Fade(0.5, 0.0, 0.5)

## Slow fade - more dramatic
define slow_fade = Fade(1.0, 0.0, 1.0)

## Fade with hold - pause on black
define fade_hold = Fade(0.5, 0.5, 0.5)

## Long fade with hold - scene transitions
define long_fade = Fade(1.0, 1.0, 1.0)


################################################################################
## Fade to Color
################################################################################

## Fade to white (flashback, dream, etc.)
define white_fade = Fade(0.5, 0.0, 0.5, color="#ffffff")

## Fade to red (danger, combat)
define red_fade = Fade(0.3, 0.0, 0.3, color="#ff0000")


################################################################################
## Slide/Push Transitions
################################################################################

## Push transitions - new scene pushes old one out
define push_left = PushMove(0.5, "pushright")
define push_right = PushMove(0.5, "pushleft")
define push_up = PushMove(0.5, "pushdown")
define push_down = PushMove(0.5, "pushup")


################################################################################
## Wipe Transitions
################################################################################

## Wipe across screen
define wipe_left = CropMove(0.5, "wiperight")
define wipe_right = CropMove(0.5, "wipeleft")
define wipe_up = CropMove(0.5, "wipedown")
define wipe_down = CropMove(0.5, "wipeup")


################################################################################
## Iris Transitions
################################################################################

## Iris in/out - classic effect
define iris_in = CropMove(0.5, "irisin")
define iris_out = CropMove(0.5, "irisout")


################################################################################
## Pixellate
################################################################################

## Pixellate transition
define pixellate = Pixellate(0.5, 10)


################################################################################
## Usage Examples
################################################################################

## scene kitchen with dissolve
## scene bedroom with fade
## scene dream_sequence with white_fade
## show character happy with quick_dissolve
## scene next_location with push_left
