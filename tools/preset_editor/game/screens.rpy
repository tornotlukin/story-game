## screens.rpy - Minimal screens for Preset Editor Test Game

# Disable quit confirmation - just quit directly
define config.quit_action = Quit(confirm=False)

# Basic say screen
screen say(who, what):
    style_prefix "say"

    window:
        id "window"

        if who is not None:
            window:
                id "namebox"
                style "namebox"
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

## Styles

style window:
    xalign 0.5
    xfill True
    yalign 1.0
    ysize 280
    background "#000000aa"
    padding (40, 20, 40, 20)

style namebox:
    xpos 40
    ypos -40
    background "#333333"
    padding (10, 5, 10, 5)

style say_dialogue:
    color "#ffffff"
    size 28

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
