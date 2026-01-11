## fonts.rpy - Font definitions
##
## Central font configuration for consistent typography.
## All font paths and sizes defined here.
##
## Font files should be placed in the game/ directory:
##   - CalSans-Regular.ttf (for character names and UI)
##   - Jua-Regular.ttf (for dialogue text)
##
## Related files: gui.rpy, styles.rpy

################################################################################
## Font Files
################################################################################

## Main dialogue text font
define gui.text_font = "Jua-Regular.ttf"

## Character name font
define gui.name_text_font = "CalSans-Regular.ttf"

## Interface/button font
define gui.interface_text_font = "CalSans-Regular.ttf"

## System font (for notifications, etc.)
define gui.system_font = "CalSans-Regular.ttf"

## Glyph font (for special characters/icons)
define gui.glyph_font = "DejaVuSans.ttf"

## Monospace font (for typewriter preset)
define gui.mono_font = "DejaVuSansMono.ttf"


################################################################################
## Font Sizes - Desktop
################################################################################

## Normal text size
define gui.text_size = 28

## Character name size
define gui.name_text_size = 36

## Button text size
define gui.button_text_size = 28

## Label text size
define gui.label_text_size = 32

## Prompt text size
define gui.prompt_text_size = 28

## Notify text size
define gui.notify_text_size = 22

## Title text size
define gui.title_text_size = 60


################################################################################
## Font Sizes - Mobile Override
################################################################################

## Mobile sizes can be set using renpy.variant() for screen variants
## or renpy.mobile for runtime platform detection:

# init python:
#     if renpy.mobile:
#         gui.text_size = 32
#         gui.name_text_size = 40
#         gui.button_text_size = 32
