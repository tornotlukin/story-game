## styles.rpy - Style definitions
##
## Defines visual styles for UI elements.
## Uses colors and fonts from colors.rpy and fonts.rpy.
##
## Related files: gui.rpy, colors.rpy, fonts.rpy

################################################################################
## Base Styles
################################################################################

style default:
    font gui.text_font
    size gui.text_size
    color gui.text_color

style input:
    color gui.accent_color
    adjust_spacing False

style hyperlink_text:
    color gui.accent_color
    hover_underline True


################################################################################
## Button Styles
################################################################################

style button:
    padding gui.button_borders.padding
    background Frame("gui/button/idle_background.png", gui.button_borders, tile=gui.button_tile)
    hover_background Frame("gui/button/hover_background.png", gui.button_borders, tile=gui.button_tile)

style button_text:
    font gui.interface_text_font
    size gui.button_text_size
    color gui.idle_color
    hover_color gui.hover_color
    selected_color gui.selected_color
    insensitive_color gui.insensitive_color
    xalign gui.button_text_xalign
    yalign 0.5


################################################################################
## Choice Button Styles
################################################################################

style choice_vbox:
    xalign 0.5
    ypos 405
    yanchor 0.5
    spacing gui.choice_spacing

style choice_button:
    xsize gui.choice_button_width
    padding gui.choice_button_borders.padding
    background Frame("gui/button/choice_idle_background.png", gui.choice_button_borders, tile=gui.choice_button_tile)
    hover_background Frame("gui/button/choice_hover_background.png", gui.choice_button_borders, tile=gui.choice_button_tile)

style choice_button_text:
    font gui.text_font
    size gui.text_size
    color gui.idle_color
    hover_color gui.hover_color
    xalign gui.choice_button_text_xalign


################################################################################
## Label Styles
################################################################################

style label:
    padding (0, 0, 0, 0)

style label_text:
    font gui.interface_text_font
    size gui.label_text_size
    color gui.accent_color


################################################################################
## Prompt Styles
################################################################################

style prompt_text:
    font gui.interface_text_font
    size gui.prompt_text_size
    color gui.text_color


################################################################################
## Frame Styles
################################################################################

style frame:
    background Frame("gui/frame.png", gui.frame_borders, tile=False)
    padding gui.frame_borders.padding


################################################################################
## Scrollbar Styles
################################################################################

style scrollbar:
    base_bar Frame("gui/scrollbar/horizontal_idle_bar.png", gui.scrollbar_borders, tile=False)
    thumb Frame("gui/scrollbar/horizontal_idle_thumb.png", gui.scrollbar_borders, tile=False)

style vscrollbar:
    base_bar Frame("gui/scrollbar/vertical_idle_bar.png", gui.vscrollbar_borders, tile=False)
    thumb Frame("gui/scrollbar/vertical_idle_thumb.png", gui.vscrollbar_borders, tile=False)


################################################################################
## Slider Styles
################################################################################

style slider:
    base_bar Frame("gui/slider/horizontal_idle_bar.png", gui.slider_borders, tile=False)
    thumb "gui/slider/horizontal_idle_thumb.png"

style vslider:
    base_bar Frame("gui/slider/vertical_idle_bar.png", gui.vslider_borders, tile=False)
    thumb "gui/slider/vertical_idle_thumb.png"
