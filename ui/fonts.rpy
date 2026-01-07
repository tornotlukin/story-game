## fonts.rpy - Font definitions
##
## Central font configuration for consistent typography.
## All font paths and sizes defined here.
##
## Related files: gui.rpy, styles.rpy

################################################################################
## Font Files
################################################################################

## Main text font
define gui.text_font = "DejaVuSans.ttf"

## Character name font
define gui.name_text_font = "DejaVuSans.ttf"

## Interface/button font
define gui.interface_text_font = "DejaVuSans.ttf"

## System font (for notifications, etc.)
define gui.system_font = "DejaVuSans.ttf"

## Glyph font (for special characters/icons)
define gui.glyph_font = "DejaVuSans.ttf"


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

## Mobile sizes are set in gui.rpy based on platform detection
## Override those values here if needed:

# init python:
#     if gui.is_mobile:
#         gui.text_size = 32
#         gui.name_text_size = 40
#         gui.button_text_size = 32
