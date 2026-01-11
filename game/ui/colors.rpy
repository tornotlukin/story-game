## colors.rpy - Color scheme definitions
##
## Central color definitions for consistent theming.
## Change colors here to restyle the entire game.
##
## Related files: gui.rpy, styles.rpy

################################################################################
## Primary Colors
################################################################################

## Accent color - used for highlights, selections, important elements
define gui.accent_color = '#cc6699'

## Idle color - default state for interactive elements
define gui.idle_color = '#888888'

## Idle small color - for smaller/secondary text
define gui.idle_small_color = '#aaaaaa'

## Hover color - when mouse/touch is over element
define gui.hover_color = '#e6b3cc'

## Selected color - for currently selected items
define gui.selected_color = '#ffffff'

## Insensitive color - for disabled elements
define gui.insensitive_color = '#8888887f'

## Muted color - for de-emphasized text
define gui.muted_color = '#6b4d57'
define gui.hover_muted_color = '#9b6d77'


################################################################################
## Text Colors
################################################################################

## Main text color
define gui.text_color = '#ffffff'

## Interface text color
define gui.interface_text_color = '#ffffff'

## Dialogue text color
define gui.dialogue_text_color = '#ffffff'

## Character name color (default, can be overridden per character)
define gui.name_text_color = '#cc6699'


################################################################################
## Frame Colors
################################################################################

## Frame background color
define gui.frame_color = '#1a1a1a'

## Frame borders
define gui.frame_borders = Borders(6, 6, 6, 6)


################################################################################
## Bar Colors
################################################################################

## Scrollbar colors
define gui.scrollbar_color = '#555555'
define gui.scrollbar_hover_color = '#777777'

## Slider colors
define gui.slider_color = '#555555'
define gui.slider_hover_color = '#777777'

## Progress bar colors
define gui.bar_color = '#404040'
define gui.bar_full_color = '#cc6699'
