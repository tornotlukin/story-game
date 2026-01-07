## screens_base.rpy - Base screen definitions
##
## Core screens required by Ren'Py: say, choice, input, etc.
## These are the fundamental screens that make the game work.
##
## Related files: All other screen files build on these

################################################################################
## Say Screen
################################################################################

screen say(who, what):
    """
    Displays dialogue to the player.

    Input support: Touch (tap to advance), Mouse (click), Keyboard (Enter/Space)
    """

    style_prefix "say"

    window:
        id "window"

        if who is not None:
            window:
                id "namebox"
                style "namebox"
                text who id "who"

        text what id "what"

    ## Quick menu at bottom
    if not renpy.variant("small"):
        use quick_menu


################################################################################
## Input Screen
################################################################################

screen input(prompt):
    """
    Displays text input to get information from the player.

    Input support: Touch (keyboard), Mouse, Keyboard
    """

    style_prefix "input"

    window:
        vbox:
            xalign 0.5
            yalign 0.5
            spacing 30

            text prompt style "input_prompt"
            input id "input"


################################################################################
## Choice Screen
################################################################################

screen choice(items):
    """
    Displays in-game choices to the player.

    Input support: Touch (tap), Mouse (click), Keyboard (arrows + Enter)
    """

    style_prefix "choice"

    vbox:
        for i in items:
            textbutton i.caption:
                action i.action
                minimum (gui.button_minimum_width, gui.button_minimum_height)


################################################################################
## Quick Menu Screen
################################################################################

screen quick_menu():
    """
    Quick access menu shown during dialogue.

    Input support: Touch (tap), Mouse (click)
    """

    zorder 100

    if quick_menu:
        hbox:
            style_prefix "quick"
            xalign 0.5
            yalign 1.0
            spacing gui.quick_button_spacing

            textbutton _("Back") action Rollback()
            textbutton _("History") action ShowMenu('history')
            textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("Auto") action Preference("auto-forward", "toggle")
            textbutton _("Save") action ShowMenu('save')
            textbutton _("Q.Save") action QuickSave()
            textbutton _("Q.Load") action QuickLoad()
            textbutton _("Prefs") action ShowMenu('preferences')

default quick_menu = True


################################################################################
## Navigation Screen
################################################################################

screen navigation():
    """
    Main menu navigation buttons.

    Input support: Touch (tap), Mouse (click), Keyboard
    """

    vbox:
        style_prefix "navigation"
        xpos gui.navigation_xpos
        yalign 0.5
        spacing gui.navigation_spacing

        if main_menu:
            textbutton _("Start") action Start()
        else:
            textbutton _("History") action ShowMenu("history")
            textbutton _("Save") action ShowMenu("save")

        textbutton _("Load") action ShowMenu("load")
        textbutton _("Preferences") action ShowMenu("preferences")

        if _in_replay:
            textbutton _("End Replay") action EndReplay(confirm=True)
        elif not main_menu:
            textbutton _("Main Menu") action MainMenu()

        textbutton _("About") action ShowMenu("about")

        if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):
            textbutton _("Help") action ShowMenu("help")

        if renpy.variant("pc"):
            textbutton _("Quit") action Quit(confirm=not main_menu)


################################################################################
## Main Menu Screen
################################################################################

screen main_menu():
    """
    Main menu displayed when game launches.

    Input support: Touch (tap), Mouse (click), Keyboard
    """

    tag menu

    add gui.main_menu_background

    frame:
        style "main_menu_frame"

    use navigation

    if gui.show_name:
        vbox:
            style "main_menu_vbox"
            text "[config.name!t]":
                style "main_menu_title"
            text "[config.version]":
                style "main_menu_version"


################################################################################
## Confirm Screen
################################################################################

screen confirm(message, yes_action, no_action):
    """
    Confirmation dialog for important actions.

    Input support: Touch (tap), Mouse (click), Keyboard (Y/N, Enter/Escape)
    """

    modal True
    zorder 200

    style_prefix "confirm"

    add "gui/overlay/confirm.png"

    frame:
        vbox:
            xalign 0.5
            yalign 0.5
            spacing 45

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 150

                textbutton _("Yes"):
                    action yes_action
                    minimum (gui.button_minimum_width, gui.button_minimum_height)

                textbutton _("No"):
                    action no_action
                    minimum (gui.button_minimum_width, gui.button_minimum_height)

    ## Keyboard shortcuts
    key "K_RETURN" action yes_action
    key "K_ESCAPE" action no_action
    key "K_y" action yes_action
    key "K_n" action no_action

    ## Android back button
    key "game_menu" action no_action
