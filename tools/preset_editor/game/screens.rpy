## screens.rpy - Minimal screens for Preset Editor Test Game

# Disable quit confirmation - just quit directly
define config.quit_action = Quit(confirm=False)

# Enable text shaders with a default
define config.default_textshader = "dissolve"

# Null transform - does nothing, used as default when no shader is active
transform null_transform:
    pass

# Dialog shader transform - set this to apply shaders to the dialog window
# Usage in script:
#     $ dialog_shader = shader_glow_blue
#     "This text has a glowing dialog box"
#     $ dialog_shader = null_transform
default dialog_shader = null_transform

# Dialog background - set to use custom artwork instead of default style
# Usage in script:
#     $ dialog_background = "images/dialog_art.png"
#     "This text has custom dialog artwork"
#     $ dialog_background = None
default dialog_background = None

# Say screen with optional dialog shader and background support
screen say(who, what):
    style_prefix "say"

    window:
        id "window"
        at dialog_shader

        if dialog_background:
            background dialog_background

        vbox:
            spacing 10

            if who is not None:
                text who id "who"

            text what id "what"


# Basic choice screen
screen choice(items):
    style_prefix "choice"

    vbox:
        for i in items:
            textbutton i.caption action i.action


# Basic input screen
screen input(prompt):
    style_prefix "input"

    window:
        vbox:
            text prompt
            input id "input"


# Confirm screen (for quit, etc)
screen confirm(message, yes_action, no_action):
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 40
        ypadding 40

        vbox:
            spacing 20
            text message xalign 0.5

            hbox:
                spacing 40
                xalign 0.5
                textbutton "Yes" action yes_action
                textbutton "No" action no_action


# Skip indicator
screen skip_indicator():
    pass

# Fast forward indicator
screen ctc():
    pass


################################################################################
## Styles
################################################################################

# Say window
style say_window:
    xalign 0.5
    xfill True
    yalign 1.0
    ysize 280
    background "#000000cc"
    padding (40, 30, 40, 30)

# Say text (dialogue)
style say_what:
    color "#ffffff"
    size 28
    outlines [(2, "#000000", 0, 0)]

# Say who (character name)
style say_who:
    color "#ffcc00"
    size 32
    bold True

# Namebox style
style namebox:
    xpos 40
    ypos -40
    background "#333333"
    padding (10, 5, 10, 5)

# Choice styles
style choice_vbox:
    xalign 0.5
    yalign 0.5
    spacing 20

style choice_button:
    xsize 600
    background "#444444"
    hover_background "#666666"
    padding (20, 10, 20, 10)

style choice_button_text:
    xalign 0.5
    color "#ffffff"
