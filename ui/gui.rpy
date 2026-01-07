## gui.rpy - Main GUI configuration
##
## Core GUI settings and layout configuration.
## This file sets up the fundamental visual parameters.
##
## Related files: colors.rpy, fonts.rpy, styles.rpy, touch_config.rpy

init python:
    # Platform detection
    gui.is_mobile = renpy.mobile
    gui.is_android = renpy.android
    gui.is_ios = renpy.ios
    gui.is_desktop = not renpy.mobile


## GUI Initialization
init offset = -2

## GUI Directory
define gui.about = _("")


################################################################################
## Layout Configuration
################################################################################

## Game Resolution
define gui.default_width = 1920
define gui.default_height = 1080

## Dialogue Box
define gui.textbox_height = 278
define gui.textbox_yalign = 1.0

## Character Name Placement
define gui.name_xpos = 360
define gui.name_ypos = 0
define gui.name_xalign = 0.0
define gui.namebox_width = None
define gui.namebox_height = None
define gui.namebox_borders = Borders(5, 5, 5, 5)
define gui.namebox_tile = False

## Dialogue Text Placement
define gui.dialogue_xpos = 402
define gui.dialogue_ypos = 75
define gui.dialogue_width = 1116
define gui.dialogue_text_xalign = 0.0


################################################################################
## Buttons
################################################################################

## Button dimensions
define gui.button_width = None
define gui.button_height = None
define gui.button_borders = Borders(6, 6, 6, 6)
define gui.button_tile = False

## Button text
define gui.button_text_xalign = 0.0


################################################################################
## Choice Buttons
################################################################################

define gui.choice_button_width = 1185
define gui.choice_button_height = None
define gui.choice_button_tile = False
define gui.choice_button_borders = Borders(150, 8, 150, 8)
define gui.choice_button_text_xalign = 0.5


################################################################################
## Slot Buttons (Save/Load)
################################################################################

define gui.slot_button_width = 414
define gui.slot_button_height = 309
define gui.slot_button_borders = Borders(15, 15, 15, 15)
define gui.slot_button_text_xalign = 0.5


################################################################################
## Positioning
################################################################################

## Navigation
define gui.navigation_xpos = 60

## Skip Indicator
define gui.skip_ypos = 15

## Notify
define gui.notify_ypos = 68

## NVL Mode
define gui.nvl_borders = Borders(0, 15, 0, 30)
define gui.nvl_list_length = 6
define gui.nvl_height = 173
define gui.nvl_spacing = 15
define gui.nvl_name_xpos = 645
define gui.nvl_name_ypos = 0
define gui.nvl_name_width = 225
define gui.nvl_name_xalign = 1.0
define gui.nvl_text_xpos = 675
define gui.nvl_text_ypos = 12
define gui.nvl_text_width = 885
define gui.nvl_text_xalign = 0.0
define gui.nvl_thought_xpos = 360
define gui.nvl_thought_width = 1170
define gui.nvl_thought_xalign = 0.0
define gui.nvl_button_xpos = 675
define gui.nvl_button_xalign = 0.0


################################################################################
## Mobile Adjustments
################################################################################

init python:
    if gui.is_mobile:
        # Increase sizes for touch
        gui.text_size = 32
        gui.name_text_size = 40
        gui.button_text_size = 32
        gui.label_text_size = 36
