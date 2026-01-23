## touch_config.rpy - Touch and mobile settings reference
##
## NOTE: Base touch configuration has been moved to gui.rpy for editor compatibility.
## Use the Preset Editor's Game Config tab to edit touch settings.
##
## This file contains mobile-specific overrides that run at init time.
##
## Related files: gui.rpy, styles.rpy

################################################################################
## Touch settings defined in gui.rpy (editable via Game Config):
################################################################################
##
## Touch Target Sizes:
##   gui.minimum_touch_size - Minimum touch target (Apple HIG: 44px)
##   gui.comfortable_touch_size - Comfortable touch target for games
##   gui.button_minimum_height - Button minimum height for touch
##   gui.button_minimum_width - Button minimum width for touch
##   gui.touch_spacing - Spacing between interactive elements
##   gui.quick_button_spacing - Quick menu button spacing
##
## Input Configuration:
##   config.gestures - Enable gesture support
##   gui.scrollbar_touch_draggable - Enable touch drag scrolling
##   gui.scrollbar_mousewheel - Enable mousewheel/touchpad scrolling


################################################################################
## Platform-Specific Overrides
################################################################################

## Mobile devices get larger touch targets. These values override the base
## values from gui.rpy when running on mobile platforms.

init python:
    if renpy.mobile:
        # Larger touch targets on mobile
        gui.button_minimum_height = 70
        gui.button_minimum_width = 140
        gui.touch_spacing = 16
        gui.choice_spacing = 28
        gui.quick_button_spacing = 25

        # Don't hide cursor on mobile (there isn't one)
        config.mouse_hide_time = None
