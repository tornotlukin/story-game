## touch_config.rpy - Touch and mobile settings
##
## Configuration for touch-friendly UI and mobile platforms.
## Ensures all interactive elements meet minimum touch target sizes.
##
## Related files: gui.rpy, styles.rpy

################################################################################
## Touch Target Sizes
################################################################################

## Minimum touch target size (Apple HIG recommends 44px)
define gui.minimum_touch_size = 44

## Comfortable touch size (recommended for games)
define gui.comfortable_touch_size = 60

## Button minimum dimensions for touch
define gui.button_minimum_height = 60
define gui.button_minimum_width = 120

## Spacing between interactive elements
define gui.touch_spacing = 12


################################################################################
## Choice Button Spacing
################################################################################

## Space between choice options
define gui.choice_spacing = 22


################################################################################
## Platform-Specific Configuration
################################################################################

init python:
    if renpy.mobile:
        # Larger touch targets on mobile
        gui.button_minimum_height = 70
        gui.button_minimum_width = 140
        gui.touch_spacing = 16
        gui.choice_spacing = 28

        # Don't hide cursor on mobile (there isn't one)
        config.mouse_hide_time = None


################################################################################
## Gesture Configuration
################################################################################

## Enable gesture support
define config.gestures = True


################################################################################
## Quick Menu Touch Adjustments
################################################################################

## Quick menu button spacing for touch
define gui.quick_button_spacing = 15

init python:
    if renpy.mobile:
        gui.quick_button_spacing = 25


################################################################################
## Scrolling Configuration
################################################################################

## Enable touch drag scrolling in viewports
define gui.scrollbar_touch_draggable = True

## Mousewheel support (works with touchpad too)
define gui.scrollbar_mousewheel = True
