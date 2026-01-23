## game_config_test.rpy - Game Config Visual Demo
##
## Visual showcase of all Game Config properties.
## Click property → see it → click back.

## =============================================================================
## Demo Screens
## =============================================================================

## Generic display screen with back button
screen demo_display(content_screen):
    modal True
    add Solid("#1a1a1a")

    use expression content_screen

    textbutton "Back" action Hide("demo_display"):
        xalign 0.5
        yalign 0.95
        text_size 32


## -----------------------------------------------------------------------------
## Color Display Screens
## -----------------------------------------------------------------------------

## Accent Color - Used for labels and emphasized text
screen color_accent:
    vbox:
        xalign 0.5 ypos 50
        spacing 10
        text "Accent Color" size 36 xalign 0.5
        text "gui.accent_color" size 24 color "#888888" xalign 0.5
        null height 10
        text "[gui.accent_color]" size 28 xalign 0.5

    ## Show in dialogue context with emphasized word
    window:
        style "say_window"
        yalign gui.textbox_yalign
        hbox:
            style_prefix "say"
            window:
                style "namebox"
                text "Character" style "say_label"
        text "The quick brown fox {color=[gui.accent_color]}jumps over{/color} the lazy dog." style "say_dialogue"

## Idle Color - Button/link text in idle state
screen color_idle:
    vbox:
        xalign 0.5 yalign 0.08
        text "Idle Color" size 36 xalign 0.5
        text "gui.idle_color" size 24 color "#888888" xalign 0.5

    ## Show as navigation buttons in idle state
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 15
            text "Navigation Buttons (idle state):" size 24 color "#888888" xalign 0.5
            null height 10
            textbutton "Start Game" action NullAction() text_color gui.idle_color text_size 32
            textbutton "Load Game" action NullAction() text_color gui.idle_color text_size 32
            textbutton "Preferences" action NullAction() text_color gui.idle_color text_size 32

    text "[gui.idle_color]" size 28 xalign 0.5 yalign 0.78

## Idle Small Color - Small button/text in idle state
screen color_idle_small:
    vbox:
        xalign 0.5 yalign 0.08
        text "Idle Small Color" size 36 xalign 0.5
        text "gui.idle_small_color" size 24 color "#888888" xalign 0.5

    ## Show as smaller UI elements
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 15
            text "Small UI Elements (idle state):" size 24 color "#888888" xalign 0.5
            null height 10
            hbox:
                spacing 30
                xalign 0.5
                textbutton "Skip" action NullAction() text_color gui.idle_small_color text_size 22
                textbutton "Auto" action NullAction() text_color gui.idle_small_color text_size 22
                textbutton "Save" action NullAction() text_color gui.idle_small_color text_size 22
                textbutton "Q.Save" action NullAction() text_color gui.idle_small_color text_size 22

    text "[gui.idle_small_color]" size 28 xalign 0.5 yalign 0.78

## Hover Color - Button/link text when hovered
screen color_hover:
    vbox:
        xalign 0.5 yalign 0.08
        text "Hover Color" size 36 xalign 0.5
        text "gui.hover_color" size 24 color "#888888" xalign 0.5

    ## Show button comparison: idle vs hover
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 20
            text "Button hover state comparison:" size 24 color "#888888" xalign 0.5
            null height 10
            hbox:
                spacing 60
                xalign 0.5
                vbox:
                    text "Idle" size 20 color "#666666" xalign 0.5
                    textbutton "Button" action NullAction() text_color gui.idle_color text_size 32
                vbox:
                    text "Hovered" size 20 color "#666666" xalign 0.5
                    textbutton "Button" action NullAction() text_color gui.hover_color text_size 32

    text "[gui.hover_color]" size 28 xalign 0.5 yalign 0.78

## Selected Color - Currently selected/active item
screen color_selected:
    vbox:
        xalign 0.5 yalign 0.08
        text "Selected Color" size 36 xalign 0.5
        text "gui.selected_color" size 24 color "#888888" xalign 0.5

    ## Show as selected menu item
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 15
            text "Menu with selected item:" size 24 color "#888888" xalign 0.5
            null height 10
            textbutton "Chapter 1" action NullAction() text_color gui.idle_color text_size 28
            textbutton "Chapter 2" action NullAction() text_color gui.selected_color text_size 28  ## Selected
            textbutton "Chapter 3" action NullAction() text_color gui.idle_color text_size 28

    text "[gui.selected_color]" size 28 xalign 0.5 yalign 0.78

## Insensitive Color - Disabled/unavailable items
screen color_insensitive:
    vbox:
        xalign 0.5 yalign 0.08
        text "Insensitive Color" size 36 xalign 0.5
        text "gui.insensitive_color" size 24 color "#888888" xalign 0.5

    ## Show as disabled buttons
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 15
            text "Enabled vs Disabled buttons:" size 24 color "#888888" xalign 0.5
            null height 10
            hbox:
                spacing 40
                xalign 0.5
                vbox:
                    text "Enabled" size 20 color "#666666" xalign 0.5
                    textbutton "Continue" action NullAction() text_color gui.idle_color text_size 28
                vbox:
                    text "Disabled" size 20 color "#666666" xalign 0.5
                    textbutton "Continue" action NullAction() text_color gui.insensitive_color text_size 28

    text "[gui.insensitive_color]" size 28 xalign 0.5 yalign 0.78

## Muted Color - De-emphasized/secondary text
screen color_muted:
    vbox:
        xalign 0.5 ypos 50
        spacing 10
        text "Muted Color" size 36 xalign 0.5
        text "gui.muted_color" size 24 color "#888888" xalign 0.5
        null height 10
        text "[gui.muted_color]" size 28 xalign 0.5

    ## Show in dialogue with muted aside
    window:
        style "say_window"
        yalign gui.textbox_yalign
        vbox:
            text "The door creaked open slowly." style "say_dialogue"
            text "{color=[gui.muted_color]}(You hear footsteps in the distance.){/color}" size gui.text_size

## Hover Muted Color - Muted elements when hovered
screen color_hover_muted:
    vbox:
        xalign 0.5 yalign 0.08
        text "Hover Muted Color" size 36 xalign 0.5
        text "gui.hover_muted_color" size 24 color "#888888" xalign 0.5

    ## Show muted button hover comparison
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 20
            text "Muted button hover state:" size 24 color "#888888" xalign 0.5
            null height 10
            hbox:
                spacing 60
                xalign 0.5
                vbox:
                    text "Muted Idle" size 20 color "#666666" xalign 0.5
                    textbutton "Return" action NullAction() text_color gui.muted_color text_size 28
                vbox:
                    text "Muted Hover" size 20 color "#666666" xalign 0.5
                    textbutton "Return" action NullAction() text_color gui.hover_muted_color text_size 28

    text "[gui.hover_muted_color]" size 28 xalign 0.5 yalign 0.78

## Text Color - Main dialogue/narration text
screen color_text:
    vbox:
        xalign 0.5 ypos 50
        spacing 10
        text "Text Color" size 36 xalign 0.5
        text "gui.text_color" size 24 color "#888888" xalign 0.5
        null height 10
        text "[gui.text_color]" size 28 xalign 0.5

    ## Show as dialogue text
    window:
        style "say_window"
        yalign gui.textbox_yalign
        text "The quick brown fox jumps over the lazy dog. This is the main dialogue text color used throughout the game." color gui.text_color size gui.text_size

## Interface Text Color - Menu and UI text
screen color_interface:
    vbox:
        xalign 0.5 yalign 0.08
        text "Interface Text Color" size 36 xalign 0.5
        text "gui.interface_text_color" size 24 color "#888888" xalign 0.5

    ## Show as interface/menu text
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 15
            text "Interface Elements:" size 24 color "#888888" xalign 0.5
            null height 10
            text "PREFERENCES" size 32 color gui.interface_text_color xalign 0.5
            null height 5
            hbox:
                spacing 20
                xalign 0.5
                text "Display" size 24 color gui.interface_text_color
                text "|" size 24 color "#444444"
                text "Sound" size 24 color gui.interface_text_color
                text "|" size 24 color "#444444"
                text "Skip" size 24 color gui.interface_text_color

    text "[gui.interface_text_color]" size 28 xalign 0.5 yalign 0.78

## Dialogue Text Color - Dialogue box specific text
screen color_dialogue:
    vbox:
        xalign 0.5 ypos 50
        spacing 10
        text "Dialogue Text Color" size 36 xalign 0.5
        text "gui.dialogue_text_color" size 24 color "#888888" xalign 0.5
        null height 10
        text "[gui.dialogue_text_color]" size 28 xalign 0.5

    ## Show in dialogue box
    window:
        style "say_window"
        yalign gui.textbox_yalign
        text "This text uses the dialogue text color, which can be different from the main text color for special styling." color gui.dialogue_text_color size gui.text_size

## Name Text Color - Character name color
screen color_name:
    vbox:
        xalign 0.5 ypos 50
        spacing 10
        text "Name Text Color" size 36 xalign 0.5
        text "gui.name_text_color" size 24 color "#888888" xalign 0.5
        null height 10
        text "[gui.name_text_color]" size 28 xalign 0.5

    ## Show with character name
    window:
        style "say_window"
        yalign gui.textbox_yalign
        vbox:
            text "Character Name" color gui.name_text_color size gui.name_text_size
            null height 10
            text "This is the default color used for character names in dialogue." style "say_dialogue"

## Frame Color - Frame background color
screen color_frame:
    vbox:
        xalign 0.5 yalign 0.08
        text "Frame Color" size 36 xalign 0.5
        text "gui.frame_color" size 24 color "#888888" xalign 0.5

    ## Show as frame background
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        background Solid(gui.frame_color)
        vbox:
            spacing 15
            text "Frame Background" size 32 xalign 0.5
            text "This frame uses gui.frame_color" size 24 color "#888888" xalign 0.5

    text "[gui.frame_color]" size 28 xalign 0.5 yalign 0.78


## -----------------------------------------------------------------------------
## Font Display Screens
## -----------------------------------------------------------------------------

screen font_text:
    vbox:
        xalign 0.5 yalign 0.08
        text "Text Font" size 36 xalign 0.5
        text "gui.text_font" size 24 color "#888888" xalign 0.5
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 20
            text "The quick brown fox jumps over the lazy dog" size gui.text_size font gui.text_font xalign 0.5
    text "[gui.text_font]" size 28 xalign 0.5 yalign 0.75

screen font_name:
    vbox:
        xalign 0.5 yalign 0.08
        text "Name Font" size 36 xalign 0.5
        text "gui.name_text_font" size 24 color "#888888" xalign 0.5
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 20
            text "Character Name" size gui.name_text_size font gui.name_text_font xalign 0.5
    text "[gui.name_text_font]" size 28 xalign 0.5 yalign 0.75

screen font_interface:
    vbox:
        xalign 0.5 yalign 0.08
        text "Interface Font" size 36 xalign 0.5
        text "gui.interface_text_font" size 24 color "#888888" xalign 0.5
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 20
            text "Menu Item Text" size gui.interface_text_size font gui.interface_text_font xalign 0.5
    text "[gui.interface_text_font]" size 28 xalign 0.5 yalign 0.75

screen size_text:
    vbox:
        xalign 0.5 yalign 0.08
        text "Text Size" size 36 xalign 0.5
        text "gui.text_size" size 24 color "#888888" xalign 0.5
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        text "Sample dialogue text at this size" size gui.text_size xalign 0.5
    text "[gui.text_size]px" size 28 xalign 0.5 yalign 0.75

screen size_name:
    vbox:
        xalign 0.5 yalign 0.08
        text "Name Size" size 36 xalign 0.5
        text "gui.name_text_size" size 24 color "#888888" xalign 0.5
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        text "Character Name" size gui.name_text_size xalign 0.5
    text "[gui.name_text_size]px" size 28 xalign 0.5 yalign 0.75

screen size_interface:
    vbox:
        xalign 0.5 yalign 0.08
        text "Interface Size" size 36 xalign 0.5
        text "gui.interface_text_size" size 24 color "#888888" xalign 0.5
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        text "Menu Button Text" size gui.interface_text_size xalign 0.5
    text "[gui.interface_text_size]px" size 28 xalign 0.5 yalign 0.75

screen size_label:
    vbox:
        xalign 0.5 yalign 0.08
        text "Label Size" size 36 xalign 0.5
        text "gui.label_text_size" size 24 color "#888888" xalign 0.5
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        text "Section Label" size gui.label_text_size xalign 0.5
    text "[gui.label_text_size]px" size 28 xalign 0.5 yalign 0.75

screen size_notify:
    vbox:
        xalign 0.5 yalign 0.08
        text "Notify Size" size 36 xalign 0.5
        text "gui.notify_text_size" size 24 color "#888888" xalign 0.5
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        text "Notification message" size gui.notify_text_size xalign 0.5
    text "[gui.notify_text_size]px" size 28 xalign 0.5 yalign 0.75

screen size_title:
    vbox:
        xalign 0.5 yalign 0.08
        text "Title Size" size 36 xalign 0.5
        text "gui.title_text_size" size 24 color "#888888" xalign 0.5
    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        text "Title" size gui.title_text_size xalign 0.5
    text "[gui.title_text_size]px" size 28 xalign 0.5 yalign 0.75


## -----------------------------------------------------------------------------
## Dialogue Box Display Screens
## -----------------------------------------------------------------------------

screen dialogue_textbox:
    vbox:
        xalign 0.5 yalign 0.08
        text "Textbox Height & Position" size 36 xalign 0.5
        text "gui.textbox_height, gui.textbox_yalign" size 24 color "#888888" xalign 0.5

    window:
        style "say_window"
        yalign gui.textbox_yalign
        text "Sample dialogue text shown in the textbox at the configured position and size." style "say_dialogue"

    text "Height: [gui.textbox_height]px | Y-Align: [gui.textbox_yalign]" size 28 xalign 0.5 yalign 0.25

screen dialogue_position:
    vbox:
        xalign 0.5 yalign 0.08
        text "Dialogue Text Position" size 36 xalign 0.5
        text "gui.dialogue_xpos, gui.dialogue_ypos, gui.dialogue_width" size 24 color "#888888" xalign 0.5

    window:
        style "say_window"
        yalign gui.textbox_yalign
        text "Dialogue positioned at the configured coordinates." style "say_dialogue"

    text "X: [gui.dialogue_xpos] | Y: [gui.dialogue_ypos] | Width: [gui.dialogue_width]" size 28 xalign 0.5 yalign 0.25

screen dialogue_align:
    vbox:
        xalign 0.5 yalign 0.08
        text "Text Alignment" size 36 xalign 0.5
        text "gui.dialogue_text_xalign" size 24 color "#888888" xalign 0.5

    window:
        style "say_window"
        yalign gui.textbox_yalign
        text "Text alignment: 0=left, 0.5=center, 1=right" style "say_dialogue"

    text "[gui.dialogue_text_xalign]" size 28 xalign 0.5 yalign 0.25


## -----------------------------------------------------------------------------
## Namebox Display Screens
## -----------------------------------------------------------------------------

screen namebox_display:
    vbox:
        xalign 0.5 yalign 0.08
        text "Namebox Display" size 36 xalign 0.5
        text "gui.name_xpos, gui.name_ypos, gui.name_xalign" size 24 color "#888888" xalign 0.5

    window:
        style "say_window"
        yalign gui.textbox_yalign

        window:
            style "namebox"
            text "Character" style "say_label"

        text "Dialogue text with character name shown above." style "say_dialogue"

    text "X: [gui.name_xpos] | Y: [gui.name_ypos] | Align: [gui.name_xalign]" size 28 xalign 0.5 yalign 0.25


## -----------------------------------------------------------------------------
## Choice Button Display Screens
## -----------------------------------------------------------------------------

screen choice_buttons:
    vbox:
        xalign 0.5 yalign 0.08
        text "Choice Button Layout" size 36 xalign 0.5
        text "gui.choice_button_width, gui.choice_spacing" size 24 color "#888888" xalign 0.5

    vbox:
        xalign 0.5 yalign 0.45
        spacing gui.choice_spacing

        textbutton "Choice Option 1" action NullAction():
            style "choice_button"
        textbutton "Choice Option 2" action NullAction():
            style "choice_button"
        textbutton "Choice Option 3" action NullAction():
            style "choice_button"

    text "Width: [gui.choice_button_width] | Spacing: [gui.choice_spacing]" size 28 xalign 0.5 yalign 0.85

screen choice_colors:
    vbox:
        xalign 0.5 yalign 0.08
        text "Choice Colors" size 36 xalign 0.5
        text "gui.choice_button_text_*_color" size 24 color "#888888" xalign 0.5

    vbox:
        xalign 0.5 yalign 0.45
        spacing 30

        hbox:
            spacing 20
            add Solid(gui.choice_button_text_idle_color) size (100, 100)
            vbox:
                yalign 0.5
                text "Idle" size 32
                text "[gui.choice_button_text_idle_color]" size 24 color "#888888"

        hbox:
            spacing 20
            add Solid(gui.choice_button_text_hover_color) size (100, 100)
            vbox:
                yalign 0.5
                text "Hover" size 32
                text "[gui.choice_button_text_hover_color]" size 24 color "#888888"

        hbox:
            spacing 20
            add Solid(gui.choice_button_text_insensitive_color) size (100, 100)
            vbox:
                yalign 0.5
                text "Insensitive" size 32
                text "[gui.choice_button_text_insensitive_color]" size 24 color "#888888"


## -----------------------------------------------------------------------------
## Button Display Screens
## -----------------------------------------------------------------------------

screen button_colors:
    vbox:
        xalign 0.5 yalign 0.08
        text "Button States" size 36 xalign 0.5
        text "gui.idle_color, gui.hover_color, etc." size 24 color "#888888" xalign 0.5

    vbox:
        xalign 0.5 yalign 0.45
        spacing 30

        hbox:
            spacing 40
            textbutton "Idle" action NullAction() style "navigation_button"
            textbutton "Hover (mouse over)" action NullAction() style "navigation_button"

        hbox:
            spacing 40
            textbutton "Selected" action NullAction() selected True style "navigation_button"
            textbutton "Insensitive" action NullAction() sensitive False style "navigation_button"


## -----------------------------------------------------------------------------
## UI Element Display Screens
## -----------------------------------------------------------------------------

screen ui_bar:
    vbox:
        xalign 0.5 yalign 0.08
        text "Bar Size" size 36 xalign 0.5
        text "gui.bar_size" size 24 color "#888888" xalign 0.5

    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 20
            bar value StaticValue(0.6, 1.0) xsize 400 xalign 0.5

    text "[gui.bar_size]px" size 28 xalign 0.5 yalign 0.75

screen ui_slider:
    vbox:
        xalign 0.5 yalign 0.08
        text "Slider Size" size 36 xalign 0.5
        text "gui.slider_size" size 24 color "#888888" xalign 0.5

    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 20
            bar value ScreenVariableValue("demo_slider_val", 1.0) xsize 400 xalign 0.5

    text "[gui.slider_size]px" size 28 xalign 0.5 yalign 0.75

    default demo_slider_val = 0.5

screen ui_scrollbar:
    vbox:
        xalign 0.5 yalign 0.08
        text "Scrollbar Size" size 36 xalign 0.5
        text "gui.scrollbar_size" size 24 color "#888888" xalign 0.5

    frame:
        xalign 0.5 yalign 0.45
        padding (30, 20)
        viewport:
            xsize 400 ysize 200
            scrollbars "vertical"
            mousewheel True
            vbox:
                for i in range(20):
                    text "Scrollable item [i + 1]" size 24

    text "[gui.scrollbar_size]px" size 28 xalign 0.5 yalign 0.75

screen ui_bar_colors:
    vbox:
        xalign 0.5 yalign 0.08
        text "Bar Colors" size 36 xalign 0.5
        text "gui.bar_color, gui.bar_full_color" size 24 color "#888888" xalign 0.5

    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 30
            hbox:
                spacing 20
                add Solid(gui.bar_color) size (100, 60)
                vbox:
                    yalign 0.5
                    text "Unfilled" size 28
                    text "[gui.bar_color]" size 20 color "#888888"
            hbox:
                spacing 20
                add Solid(gui.bar_full_color) size (100, 60)
                vbox:
                    yalign 0.5
                    text "Filled" size 28
                    text "[gui.bar_full_color]" size 20 color "#888888"

screen ui_scrollbar_colors:
    vbox:
        xalign 0.5 yalign 0.08
        text "Scrollbar Colors" size 36 xalign 0.5
        text "gui.scrollbar_color, gui.scrollbar_hover_color" size 24 color "#888888" xalign 0.5

    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 30
            hbox:
                spacing 20
                add Solid(gui.scrollbar_color) size (100, 60)
                vbox:
                    yalign 0.5
                    text "Idle" size 28
                    text "[gui.scrollbar_color]" size 20 color "#888888"
            hbox:
                spacing 20
                add Solid(gui.scrollbar_hover_color) size (100, 60)
                vbox:
                    yalign 0.5
                    text "Hover" size 28
                    text "[gui.scrollbar_hover_color]" size 20 color "#888888"

screen ui_slider_colors:
    vbox:
        xalign 0.5 yalign 0.08
        text "Slider Colors" size 36 xalign 0.5
        text "gui.slider_color, gui.slider_hover_color" size 24 color "#888888" xalign 0.5

    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 30
            hbox:
                spacing 20
                add Solid(gui.slider_color) size (100, 60)
                vbox:
                    yalign 0.5
                    text "Idle" size 28
                    text "[gui.slider_color]" size 20 color "#888888"
            hbox:
                spacing 20
                add Solid(gui.slider_hover_color) size (100, 60)
                vbox:
                    yalign 0.5
                    text "Hover" size 28
                    text "[gui.slider_hover_color]" size 20 color "#888888"


## -----------------------------------------------------------------------------
## Background Display Screens
## -----------------------------------------------------------------------------

screen bg_main_menu:
    vbox:
        xalign 0.5 yalign 0.08
        frame:
            background "#000000cc"
            padding (20, 10)
            vbox:
                text "Main Menu Background" size 36 xalign 0.5
                text "gui.main_menu_background" size 24 color "#888888" xalign 0.5

    add gui.main_menu_background

    frame:
        xalign 0.5 yalign 0.85
        background "#000000cc"
        padding (20, 10)
        text "[gui.main_menu_background]" size 28

screen bg_game_menu:
    vbox:
        xalign 0.5 yalign 0.08
        frame:
            background "#000000cc"
            padding (20, 10)
            vbox:
                text "Game Menu Background" size 36 xalign 0.5
                text "gui.game_menu_background" size 24 color "#888888" xalign 0.5

    add gui.game_menu_background

    frame:
        xalign 0.5 yalign 0.85
        background "#000000cc"
        padding (20, 10)
        text "[gui.game_menu_background]" size 28


## -----------------------------------------------------------------------------
## Text Speed Display Screens
## -----------------------------------------------------------------------------

screen text_cps:
    vbox:
        xalign 0.5 yalign 0.08
        text "Text CPS" size 36 xalign 0.5
        text "preferences.text_cps" size 24 color "#888888" xalign 0.5

    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 20
            text "Characters per second" size 28 xalign 0.5
            text "(0 = instant)" size 24 color "#888888" xalign 0.5

    text "[preferences.text_cps]" size 48 xalign 0.5 yalign 0.75

screen text_afm:
    vbox:
        xalign 0.5 yalign 0.08
        text "Auto-Forward Time" size 36 xalign 0.5
        text "preferences.afm_time" size 24 color "#888888" xalign 0.5

    frame:
        xalign 0.5 yalign 0.45
        padding (60, 40)
        vbox:
            spacing 20
            text "Delay before auto-advance" size 28 xalign 0.5
            text "(0-30 range)" size 24 color "#888888" xalign 0.5

    text "[preferences.afm_time]" size 48 xalign 0.5 yalign 0.75


## =============================================================================
## Menu Screens
## =============================================================================

screen demo_main_menu:
    modal True
    add Solid("#1a1a1a")

    text "Game Config Demo" size 48 xalign 0.5 yalign 0.08

    vbox:
        xalign 0.5 yalign 0.5
        spacing 15

        textbutton "Colors" action ShowMenu("demo_colors_menu") xalign 0.5
        textbutton "Fonts" action ShowMenu("demo_fonts_menu") xalign 0.5
        textbutton "Dialogue Box" action ShowMenu("demo_dialogue_menu") xalign 0.5
        textbutton "Name Box" action ShowMenu("demo_namebox_menu") xalign 0.5
        textbutton "Choice Buttons" action ShowMenu("demo_choices_menu") xalign 0.5
        textbutton "Buttons" action ShowMenu("demo_buttons_menu") xalign 0.5
        textbutton "UI Elements" action ShowMenu("demo_ui_menu") xalign 0.5
        textbutton "Backgrounds" action ShowMenu("demo_backgrounds_menu") xalign 0.5
        textbutton "Text Speed" action ShowMenu("demo_textspeed_menu") xalign 0.5

    textbutton "Exit" action Return() xalign 0.5 yalign 0.92


## Category Menus

screen demo_colors_menu:
    modal True
    add Solid("#1a1a1a")

    text "Colors" size 48 xalign 0.5 yalign 0.08

    vbox:
        xalign 0.5 yalign 0.5
        spacing 12

        textbutton "Accent Color" action ShowMenu("demo_display", "color_accent") xalign 0.5
        textbutton "Idle Color" action ShowMenu("demo_display", "color_idle") xalign 0.5
        textbutton "Idle Small Color" action ShowMenu("demo_display", "color_idle_small") xalign 0.5
        textbutton "Hover Color" action ShowMenu("demo_display", "color_hover") xalign 0.5
        textbutton "Selected Color" action ShowMenu("demo_display", "color_selected") xalign 0.5
        textbutton "Insensitive Color" action ShowMenu("demo_display", "color_insensitive") xalign 0.5
        textbutton "Muted Color" action ShowMenu("demo_display", "color_muted") xalign 0.5
        textbutton "Hover Muted Color" action ShowMenu("demo_display", "color_hover_muted") xalign 0.5
        textbutton "Text Color" action ShowMenu("demo_display", "color_text") xalign 0.5
        textbutton "Interface Text Color" action ShowMenu("demo_display", "color_interface") xalign 0.5
        textbutton "Dialogue Text Color" action ShowMenu("demo_display", "color_dialogue") xalign 0.5
        textbutton "Name Text Color" action ShowMenu("demo_display", "color_name") xalign 0.5
        textbutton "Frame Color" action ShowMenu("demo_display", "color_frame") xalign 0.5

    textbutton "Back" action Return() xalign 0.5 yalign 0.92


screen demo_fonts_menu:
    modal True
    add Solid("#1a1a1a")

    text "Fonts & Sizes" size 48 xalign 0.5 yalign 0.08

    vbox:
        xalign 0.5 yalign 0.5
        spacing 12

        textbutton "Text Font" action ShowMenu("demo_display", "font_text") xalign 0.5
        textbutton "Name Font" action ShowMenu("demo_display", "font_name") xalign 0.5
        textbutton "Interface Font" action ShowMenu("demo_display", "font_interface") xalign 0.5
        null height 20
        textbutton "Text Size" action ShowMenu("demo_display", "size_text") xalign 0.5
        textbutton "Name Size" action ShowMenu("demo_display", "size_name") xalign 0.5
        textbutton "Interface Size" action ShowMenu("demo_display", "size_interface") xalign 0.5
        textbutton "Label Size" action ShowMenu("demo_display", "size_label") xalign 0.5
        textbutton "Notify Size" action ShowMenu("demo_display", "size_notify") xalign 0.5
        textbutton "Title Size" action ShowMenu("demo_display", "size_title") xalign 0.5

    textbutton "Back" action Return() xalign 0.5 yalign 0.92


screen demo_dialogue_menu:
    modal True
    add Solid("#1a1a1a")

    text "Dialogue Box" size 48 xalign 0.5 yalign 0.08

    vbox:
        xalign 0.5 yalign 0.5
        spacing 15

        textbutton "Textbox Height & Position" action ShowMenu("demo_display", "dialogue_textbox") xalign 0.5
        textbutton "Dialogue Text Position" action ShowMenu("demo_display", "dialogue_position") xalign 0.5
        textbutton "Text Alignment" action ShowMenu("demo_display", "dialogue_align") xalign 0.5

    textbutton "Back" action Return() xalign 0.5 yalign 0.92


screen demo_namebox_menu:
    modal True
    add Solid("#1a1a1a")

    text "Name Box" size 48 xalign 0.5 yalign 0.08

    vbox:
        xalign 0.5 yalign 0.5
        spacing 15

        textbutton "Namebox Display" action ShowMenu("demo_display", "namebox_display") xalign 0.5

    textbutton "Back" action Return() xalign 0.5 yalign 0.92


screen demo_choices_menu:
    modal True
    add Solid("#1a1a1a")

    text "Choice Buttons" size 48 xalign 0.5 yalign 0.08

    vbox:
        xalign 0.5 yalign 0.5
        spacing 15

        textbutton "Choice Button Layout" action ShowMenu("demo_display", "choice_buttons") xalign 0.5
        textbutton "Choice Colors" action ShowMenu("demo_display", "choice_colors") xalign 0.5

    textbutton "Back" action Return() xalign 0.5 yalign 0.92


screen demo_buttons_menu:
    modal True
    add Solid("#1a1a1a")

    text "Buttons" size 48 xalign 0.5 yalign 0.08

    vbox:
        xalign 0.5 yalign 0.5
        spacing 15

        textbutton "Button States" action ShowMenu("demo_display", "button_colors") xalign 0.5

    textbutton "Back" action Return() xalign 0.5 yalign 0.92


screen demo_ui_menu:
    modal True
    add Solid("#1a1a1a")

    text "UI Elements" size 48 xalign 0.5 yalign 0.08

    vbox:
        xalign 0.5 yalign 0.5
        spacing 15

        textbutton "Bar Size" action ShowMenu("demo_display", "ui_bar") xalign 0.5
        textbutton "Slider Size" action ShowMenu("demo_display", "ui_slider") xalign 0.5
        textbutton "Scrollbar Size" action ShowMenu("demo_display", "ui_scrollbar") xalign 0.5
        null height 15
        textbutton "Bar Colors" action ShowMenu("demo_display", "ui_bar_colors") xalign 0.5
        textbutton "Scrollbar Colors" action ShowMenu("demo_display", "ui_scrollbar_colors") xalign 0.5
        textbutton "Slider Colors" action ShowMenu("demo_display", "ui_slider_colors") xalign 0.5

    textbutton "Back" action Return() xalign 0.5 yalign 0.92


screen demo_backgrounds_menu:
    modal True
    add Solid("#1a1a1a")

    text "Backgrounds" size 48 xalign 0.5 yalign 0.08

    vbox:
        xalign 0.5 yalign 0.5
        spacing 15

        textbutton "Main Menu Background" action ShowMenu("demo_display", "bg_main_menu") xalign 0.5
        textbutton "Game Menu Background" action ShowMenu("demo_display", "bg_game_menu") xalign 0.5

    textbutton "Back" action Return() xalign 0.5 yalign 0.92


screen demo_textspeed_menu:
    modal True
    add Solid("#1a1a1a")

    text "Text Speed" size 48 xalign 0.5 yalign 0.08

    vbox:
        xalign 0.5 yalign 0.5
        spacing 15

        textbutton "Text CPS" action ShowMenu("demo_display", "text_cps") xalign 0.5
        textbutton "Auto-Forward Time" action ShowMenu("demo_display", "text_afm") xalign 0.5

    textbutton "Back" action Return() xalign 0.5 yalign 0.92


## =============================================================================
## Entry Point
## =============================================================================

label game_config_test:
    call screen demo_main_menu
    return
