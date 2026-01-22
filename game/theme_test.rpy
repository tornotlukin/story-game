## theme_test.rpy - Theme Parameter Test Script
##
## Comprehensive test script showcasing ALL visual elements and parameters.
## Each element displays: code property name, editor label, and visual demo.
##
## Generated: 2026-01-22

################################################################################
## Custom Styles (to override defaults completely)
################################################################################

style tt_text is default:
    color "#dddddd"
    size 18

style tt_title is default:
    color "#ffffff"
    size 36

style tt_button is default:
    background None

style tt_button_text is default:
    color "#cccccc"
    hover_color "#ffffff"
    size 20

################################################################################
## Centered Menu Screen - Using fixed positioning, NO frame
################################################################################

screen centered_menu(title, items):
    modal True

    # Full screen black background
    add Solid("#000000")

    # Dark gray box background - centered manually
    add Solid("#222222"):
        xsize 700
        ysize 600
        align (0.5, 0.5)

    # Content container - centered
    fixed:
        align (0.5, 0.5)
        xsize 600
        yfit True

        vbox:
            spacing 15
            xalign 0.5

            text title style "tt_title":
                xalign 0.5

            null height 20

            for label, value in items:
                textbutton label action Return(value) style "tt_button":
                    xalign 0.5
                    xminimum 500
                    text_style "tt_button_text"


screen centered_info(title, lines):
    modal True

    # Full screen black background
    add Solid("#000000")

    # Dark gray box background
    add Solid("#222222"):
        xsize 800
        ysize 500
        align (0.5, 0.5)

    # Content container
    fixed:
        align (0.5, 0.5)
        xsize 700
        yfit True

        vbox:
            spacing 12
            xalign 0.5

            text title style "tt_title":
                color "#88ccff"
                size 28
                xalign 0.5

            null height 15

            for line in lines:
                text line style "tt_text":
                    xalign 0.5

            null height 25

            textbutton "Continue" action Return() style "tt_button":
                xalign 0.5
                text_style "tt_button_text"


################################################################################
## Start - Introduction
################################################################################

label theme_test_start:
    scene black with fade

    call screen centered_info("THEME PARAMETER TEST", [
        "Welcome to the Theme Parameter Test Script.",
        "",
        "This script demonstrates ALL visual elements",
        "configurable in the Game Config editor.",
        "",
        "Each element shows:",
        "- The code property name",
        "- The editor label",
        "- A visual demonstration"
    ])

    jump theme_test_main_menu


################################################################################
## Main Section Menu
################################################################################

label theme_test_main_menu:
    scene black with dissolve

    $ menu_items = [
        ("1. Project Info", "project"),
        ("2. Screen Dimensions", "screen"),
        ("3. Colors", "colors"),
        ("4. Fonts", "fonts"),
        ("5. Font Sizes", "font_sizes"),
        ("6. Dialogue Box Layout", "dialogue"),
        ("7. Name Box Layout", "namebox"),
        ("8. Menu Backgrounds", "menu_bg"),
        ("9. Text Speed", "text_speed"),
        ("10. Window Behavior", "window"),
        ("11. UI Details", "ui_details"),
        ("12. Choice Buttons", "choice_buttons"),
        ("13. Buttons & Frames (Not in Editor)", "buttons_frames"),
        ("14. NVL Mode (Not in Editor)", "nvl"),
        ("15. History Screen (Not in Editor)", "history"),
        ("16. Miscellaneous (Not in Editor)", "misc"),
        ("Exit Test", "exit")
    ]

    call screen centered_menu("THEME PARAMETER TEST", menu_items)

    if _return == "project":
        jump theme_section_project
    elif _return == "screen":
        jump theme_section_screen
    elif _return == "colors":
        jump theme_section_colors
    elif _return == "fonts":
        jump theme_section_fonts
    elif _return == "font_sizes":
        jump theme_section_font_sizes
    elif _return == "dialogue":
        jump theme_section_dialogue
    elif _return == "namebox":
        jump theme_section_namebox
    elif _return == "menu_bg":
        jump theme_section_menu_backgrounds
    elif _return == "text_speed":
        jump theme_section_text_speed
    elif _return == "window":
        jump theme_section_window_behavior
    elif _return == "ui_details":
        jump theme_section_ui_details
    elif _return == "choice_buttons":
        jump theme_section_choice_buttons
    elif _return == "buttons_frames":
        jump theme_section_buttons_frames
    elif _return == "nvl":
        jump theme_section_nvl
    elif _return == "history":
        jump theme_section_history
    elif _return == "misc":
        jump theme_section_misc
    elif _return == "exit":
        return

    jump theme_test_main_menu


################################################################################
## Section 1: Project Info
################################################################################

label theme_section_project:
    scene black with dissolve

    $ lines = [
        "{color=#88ccff}config.name{/color}",
        "Editor: \"Game Name\"",
        "Current: " + str(config.name),
        "",
        "{color=#88ccff}config.version{/color}",
        "Editor: \"Version\"",
        "Current: " + str(config.version),
        "",
        "{color=#88ccff}build.name{/color}",
        "Editor: \"Build Name\"",
        "Current: " + str(build.name),
        "",
        "{color=#88ccff}config.save_directory{/color}",
        "Editor: \"Save Directory\"",
        "Current: " + str(config.save_directory)
    ]

    call screen centered_info("PROJECT INFO", lines)

    jump theme_test_main_menu


################################################################################
## Section 2: Screen Dimensions
################################################################################

label theme_section_screen:
    scene black with dissolve

    $ phys_w = config.physical_width if config.physical_width else "None (uses virtual)"
    $ phys_h = config.physical_height if config.physical_height else "None (uses virtual)"

    $ lines = [
        "{color=#88ccff}config.screen_width{/color}",
        "Editor: \"Virtual Width\"",
        "Current: " + str(config.screen_width),
        "",
        "{color=#88ccff}config.screen_height{/color}",
        "Editor: \"Virtual Height\"",
        "Current: " + str(config.screen_height),
        "",
        "{color=#88ccff}config.physical_width{/color}",
        "Editor: \"Physical Width\"",
        "Current: " + str(phys_w),
        "",
        "{color=#88ccff}config.physical_height{/color}",
        "Editor: \"Physical Height\"",
        "Current: " + str(phys_h)
    ]

    call screen centered_info("SCREEN DIMENSIONS", lines)

    jump theme_test_main_menu


################################################################################
## Section 3: Colors
################################################################################

label theme_section_colors:
    scene black with dissolve

    $ color_items = [
        ("View All Colors (Visual Grid)", "grid"),
        ("gui.accent_color (Accent Color)", "accent"),
        ("gui.hover_color (Hover Color)", "hover"),
        ("gui.idle_color (Idle Color)", "idle"),
        ("gui.idle_small_color (Idle Small Color)", "idle_small"),
        ("gui.selected_color (Selected Color)", "selected"),
        ("gui.insensitive_color (Insensitive Color)", "insensitive"),
        ("gui.text_color (Text Color)", "text"),
        ("gui.interface_text_color (Interface Text Color)", "interface"),
        ("gui.muted_color (Muted Color)", "muted"),
        ("gui.hover_muted_color (Hover Muted Color)", "hover_muted"),
        ("Back to Main Menu", "back")
    ]

    call screen centered_menu("COLORS", color_items)

    if _return == "grid":
        call screen colors_demo_screen
        jump theme_section_colors
    elif _return == "accent":
        call screen color_detail_screen("gui.accent_color", "Accent Color", gui.accent_color, "Used for labels, highlights, and emphasis.")
    elif _return == "hover":
        call screen color_detail_screen("gui.hover_color", "Hover Color", gui.hover_color, "Applied to buttons and bars when hovered.")
    elif _return == "idle":
        call screen color_detail_screen("gui.idle_color", "Idle Color", gui.idle_color, "Default color for text buttons.")
    elif _return == "idle_small":
        call screen color_detail_screen("gui.idle_small_color", "Idle Small Color", gui.idle_small_color, "Variant for small text readability.")
    elif _return == "selected":
        call screen color_detail_screen("gui.selected_color", "Selected Color", gui.selected_color, "Applied to selected/active items.")
    elif _return == "insensitive":
        call screen color_detail_screen("gui.insensitive_color", "Insensitive Color", gui.insensitive_color, "Applied to disabled items.")
    elif _return == "text":
        call screen color_detail_screen("gui.text_color", "Text Color", gui.text_color, "Primary dialogue and narrative text.")
    elif _return == "interface":
        call screen color_detail_screen("gui.interface_text_color", "Interface Text Color", gui.interface_text_color, "Menu and UI text elements.")
    elif _return == "muted":
        call screen color_detail_screen("gui.muted_color", "Muted Color", gui.muted_color, "Unfilled portions of progress bars.")
    elif _return == "hover_muted":
        call screen color_detail_screen("gui.hover_muted_color", "Hover Muted Color", gui.hover_muted_color, "Unfilled bar portions when hovered.")
    elif _return == "back":
        jump theme_test_main_menu

    jump theme_section_colors


screen color_detail_screen(code_name, editor_label, color_value, description):
    modal True

    add Solid("#000000")

    add Solid("#222222"):
        xsize 500
        ysize 400
        align (0.5, 0.5)

    fixed:
        align (0.5, 0.5)
        xsize 450
        yfit True

        vbox:
            spacing 15
            xalign 0.5

            text code_name size 28 xalign 0.5 color "#88ccff"
            text "Editor: \"[editor_label]\"" size 20 xalign 0.5 color "#dddddd"
            text "Current: [color_value]" size 18 xalign 0.5 color "#dddddd"

            null height 10

            add Solid(color_value):
                xsize 200
                ysize 60
                xalign 0.5

            null height 10

            text "{color=[color_value]}Sample text in this color.{/color}" size 24 xalign 0.5

            null height 5

            text description size 16 xalign 0.5 color "#aaaaaa"

            null height 20

            textbutton "Back" action Return() style "tt_button":
                xalign 0.5
                text_style "tt_button_text"


################################################################################
## Section 4: Fonts
################################################################################

label theme_section_fonts:
    scene black with dissolve

    $ lines = [
        "{color=#88ccff}gui.text_font{/color}",
        "Editor: \"Text Font\"",
        "Current: " + str(gui.text_font),
        "Used for dialogue and narrative.",
        "",
        "{color=#88ccff}gui.name_text_font{/color}",
        "Editor: \"Name Font\"",
        "Current: " + str(gui.name_text_font),
        "Used for character names.",
        "",
        "{color=#88ccff}gui.interface_text_font{/color}",
        "Editor: \"Interface Font\"",
        "Current: " + str(gui.interface_text_font),
        "Used for menus and UI."
    ]

    call screen centered_info("FONTS", lines)

    jump theme_test_main_menu


################################################################################
## Section 5: Font Sizes
################################################################################

label theme_section_font_sizes:
    scene black with dissolve

    call screen font_sizes_demo_screen

    jump theme_test_main_menu


screen font_sizes_demo_screen():
    modal True

    add Solid("#000000")

    add Solid("#222222"):
        xsize 700
        ysize 600
        align (0.5, 0.5)

    fixed:
        align (0.5, 0.5)
        xsize 650
        yfit True

        vbox:
            spacing 12
            xalign 0.5

            text "FONT SIZES" size 30 xalign 0.5 color "#ffffff"

            null height 15

            hbox:
                spacing 30
                xalign 0.5

                vbox:
                    spacing 8
                    text "{color=#88ccff}gui.text_size{/color}" size 16
                    text "Editor: \"Text Size\"" size 14 color "#dddddd"
                    text "Value: [gui.text_size]" size 14 color "#dddddd"
                    text "Sample" size gui.text_size color "#ffffff"

                vbox:
                    spacing 8
                    text "{color=#88ccff}gui.name_text_size{/color}" size 16
                    text "Editor: \"Name Size\"" size 14 color "#dddddd"
                    text "Value: [gui.name_text_size]" size 14 color "#dddddd"
                    text "Sample" size gui.name_text_size color "#ffffff"

            null height 10

            hbox:
                spacing 30
                xalign 0.5

                vbox:
                    spacing 8
                    text "{color=#88ccff}gui.interface_text_size{/color}" size 16
                    text "Editor: \"Interface Size\"" size 14 color "#dddddd"
                    text "Value: [gui.interface_text_size]" size 14 color "#dddddd"
                    text "Sample" size gui.interface_text_size color "#ffffff"

                vbox:
                    spacing 8
                    text "{color=#88ccff}gui.label_text_size{/color}" size 16
                    text "Editor: \"Label Size\"" size 14 color "#dddddd"
                    text "Value: [gui.label_text_size]" size 14 color "#dddddd"
                    text "Sample" size gui.label_text_size color "#ffffff"

            null height 10

            hbox:
                spacing 30
                xalign 0.5

                vbox:
                    spacing 8
                    text "{color=#88ccff}gui.notify_text_size{/color}" size 16
                    text "Editor: \"Notify Size\"" size 14 color "#dddddd"
                    text "Value: [gui.notify_text_size]" size 14 color "#dddddd"
                    text "Sample" size gui.notify_text_size color "#ffffff"

                vbox:
                    spacing 8
                    text "{color=#88ccff}gui.title_text_size{/color}" size 16
                    text "Editor: \"Title Size\"" size 14 color "#dddddd"
                    text "Value: [gui.title_text_size]" size 14 color "#dddddd"
                    text "TITLE" size gui.title_text_size color "#ffffff"

            null height 20

            textbutton "Back" action Return() style "tt_button":
                xalign 0.5
                text_style "tt_button_text"


################################################################################
## Section 6: Dialogue Box Layout
################################################################################

label theme_section_dialogue:
    scene black with dissolve

    $ lines = [
        "{color=#88ccff}gui.textbox_height{/color}",
        "Editor: \"Textbox Height\" | Value: " + str(gui.textbox_height),
        "",
        "{color=#88ccff}gui.textbox_yalign{/color}",
        "Editor: \"Textbox Y Align\" | Value: " + str(gui.textbox_yalign),
        "",
        "{color=#88ccff}gui.dialogue_xpos{/color}",
        "Editor: \"Text X Position\" | Value: " + str(gui.dialogue_xpos),
        "",
        "{color=#88ccff}gui.dialogue_ypos{/color}",
        "Editor: \"Text Y Position\" | Value: " + str(gui.dialogue_ypos),
        "",
        "{color=#88ccff}gui.dialogue_width{/color}",
        "Editor: \"Text Width\" | Value: " + str(gui.dialogue_width),
        "",
        "{color=#88ccff}gui.dialogue_text_xalign{/color}",
        "Editor: \"Text X Align\" | Value: " + str(gui.dialogue_text_xalign)
    ]

    call screen centered_info("DIALOGUE BOX LAYOUT", lines)

    jump theme_test_main_menu


################################################################################
## Section 7: Name Box Layout
################################################################################

label theme_section_namebox:
    scene black with dissolve

    $ nb_w = gui.namebox_width if hasattr(gui, 'namebox_width') and gui.namebox_width else "None (auto)"
    $ nb_h = gui.namebox_height if hasattr(gui, 'namebox_height') and gui.namebox_height else "None (auto)"

    $ lines = [
        "{color=#88ccff}gui.name_xpos{/color}",
        "Editor: \"Name X Position\" | Value: " + str(gui.name_xpos),
        "",
        "{color=#88ccff}gui.name_ypos{/color}",
        "Editor: \"Name Y Position\" | Value: " + str(gui.name_ypos),
        "",
        "{color=#88ccff}gui.name_xalign{/color}",
        "Editor: \"Name X Align\" | Value: " + str(gui.name_xalign),
        "",
        "{color=#88ccff}gui.namebox_width{/color}",
        "Editor: \"Namebox Width\" | Value: " + str(nb_w),
        "",
        "{color=#88ccff}gui.namebox_height{/color}",
        "Editor: \"Namebox Height\" | Value: " + str(nb_h)
    ]

    call screen centered_info("NAME BOX LAYOUT", lines)

    jump theme_test_main_menu


################################################################################
## Section 8: Menu Backgrounds
################################################################################

label theme_section_menu_backgrounds:
    scene black with dissolve

    $ lines = [
        "{color=#88ccff}gui.main_menu_background{/color}",
        "Editor: \"Main Menu\"",
        "Value: " + str(gui.main_menu_background),
        "",
        "{color=#88ccff}gui.game_menu_background{/color}",
        "Editor: \"Game Menu\"",
        "Value: " + str(gui.game_menu_background),
        "",
        "Press Escape to see the game menu background."
    ]

    call screen centered_info("MENU BACKGROUNDS", lines)

    jump theme_test_main_menu


################################################################################
## Section 9: Text Speed
################################################################################

label theme_section_text_speed:
    scene black with dissolve

    $ lines = [
        "{color=#88ccff}preferences.text_cps{/color}",
        "Editor: \"Characters Per Second\"",
        "Value: " + str(preferences.text_cps),
        "Speed of text reveal. 0 = instant.",
        "",
        "{color=#88ccff}preferences.afm_time{/color}",
        "Editor: \"Auto-Forward Time\"",
        "Value: " + str(preferences.afm_time),
        "Seconds before auto-advance."
    ]

    call screen centered_info("TEXT SPEED", lines)

    jump theme_test_main_menu


################################################################################
## Section 10: Window Behavior
################################################################################

label theme_section_window_behavior:
    scene black with dissolve

    $ quit_confirm = "True" if config.quit_action else "False"
    $ quit_msg = gui.QUIT if hasattr(gui, 'QUIT') else "(not set)"

    $ lines = [
        "{color=#88ccff}config.quit_action{/color}",
        "Editor: \"Confirm on Quit\"",
        "Enabled: " + quit_confirm,
        "",
        "{color=#88ccff}gui.QUIT{/color}",
        "Editor: \"Quit Message\"",
        "Message:",
        str(quit_msg)
    ]

    call screen centered_info("WINDOW BEHAVIOR", lines)

    jump theme_test_main_menu


################################################################################
## Section 11: UI Details
################################################################################

label theme_section_ui_details:
    scene black with dissolve

    $ ui_items = [
        ("Bar/Slider/Scrollbar Sizes", "sizes"),
        ("Button Dimensions", "dimensions"),
        ("Button Text Colors", "colors"),
        ("Interactive Demo", "demo"),
        ("Back to Main Menu", "back")
    ]

    call screen centered_menu("UI DETAILS", ui_items)

    if _return == "sizes":
        call screen ui_sizes_screen
    elif _return == "dimensions":
        call screen ui_dimensions_screen
    elif _return == "colors":
        call screen ui_button_colors_screen
    elif _return == "demo":
        call screen ui_details_demo_screen
    elif _return == "back":
        jump theme_test_main_menu

    jump theme_section_ui_details


screen ui_sizes_screen():
    modal True

    add Solid("#000000")

    add Solid("#222222"):
        xsize 600
        ysize 400
        align (0.5, 0.5)

    fixed:
        align (0.5, 0.5)
        xsize 550
        yfit True

        vbox:
            spacing 15
            xalign 0.5

            text "BAR/SLIDER/SCROLLBAR SIZES" size 28 xalign 0.5 color "#ffffff"

            null height 15

            text "{color=#88ccff}gui.bar_size{/color}" xalign 0.5
            text "Editor: \"Bar Size\" | Value: [gui.bar_size]" xalign 0.5 color "#dddddd"

            null height 10

            text "{color=#88ccff}gui.scrollbar_size{/color}" xalign 0.5
            text "Editor: \"Scrollbar Size\" | Value: [gui.scrollbar_size]" xalign 0.5 color "#dddddd"

            null height 10

            text "{color=#88ccff}gui.slider_size{/color}" xalign 0.5
            text "Editor: \"Slider Size\" | Value: [gui.slider_size]" xalign 0.5 color "#dddddd"

            null height 25

            textbutton "Back" action Return() style "tt_button":
                xalign 0.5
                text_style "tt_button_text"


screen ui_dimensions_screen():
    modal True

    add Solid("#000000")

    $ btn_w = gui.button_width if hasattr(gui, 'button_width') and gui.button_width else "None (auto)"
    $ btn_h = gui.button_height if hasattr(gui, 'button_height') and gui.button_height else "None (auto)"

    add Solid("#222222"):
        xsize 600
        ysize 350
        align (0.5, 0.5)

    fixed:
        align (0.5, 0.5)
        xsize 550
        yfit True

        vbox:
            spacing 15
            xalign 0.5

            text "BUTTON DIMENSIONS" size 28 xalign 0.5 color "#ffffff"

            null height 15

            text "{color=#88ccff}gui.button_width{/color}" xalign 0.5
            text "Editor: \"Button Width\" | Value: [btn_w]" xalign 0.5 color "#dddddd"

            null height 10

            text "{color=#88ccff}gui.button_height{/color}" xalign 0.5
            text "Editor: \"Button Height\" | Value: [btn_h]" xalign 0.5 color "#dddddd"

            null height 25

            textbutton "Back" action Return() style "tt_button":
                xalign 0.5
                text_style "tt_button_text"


screen ui_button_colors_screen():
    modal True

    add Solid("#000000")

    $ c1 = gui.button_text_idle_color if hasattr(gui, 'button_text_idle_color') and gui.button_text_idle_color else "(not set)"
    $ c2 = gui.button_text_hover_color if hasattr(gui, 'button_text_hover_color') and gui.button_text_hover_color else "(not set)"
    $ c3 = gui.button_text_selected_color if hasattr(gui, 'button_text_selected_color') and gui.button_text_selected_color else "(not set)"
    $ c4 = gui.button_text_insensitive_color if hasattr(gui, 'button_text_insensitive_color') and gui.button_text_insensitive_color else "(not set)"

    add Solid("#222222"):
        xsize 650
        ysize 450
        align (0.5, 0.5)

    fixed:
        align (0.5, 0.5)
        xsize 600
        yfit True

        vbox:
            spacing 12
            xalign 0.5

            text "BUTTON TEXT COLORS" size 28 xalign 0.5 color "#ffffff"

            null height 15

            text "{color=#88ccff}gui.button_text_idle_color{/color}" xalign 0.5
            text "Editor: \"Button Idle\" | Value: [c1]" xalign 0.5 color "#dddddd"

            text "{color=#88ccff}gui.button_text_hover_color{/color}" xalign 0.5
            text "Editor: \"Button Hover\" | Value: [c2]" xalign 0.5 color "#dddddd"

            text "{color=#88ccff}gui.button_text_selected_color{/color}" xalign 0.5
            text "Editor: \"Button Selected\" | Value: [c3]" xalign 0.5 color "#dddddd"

            text "{color=#88ccff}gui.button_text_insensitive_color{/color}" xalign 0.5
            text "Editor: \"Button Insensitive\" | Value: [c4]" xalign 0.5 color "#dddddd"

            null height 20

            textbutton "Back" action Return() style "tt_button":
                xalign 0.5
                text_style "tt_button_text"


################################################################################
## Section 12: Choice Buttons
################################################################################

label theme_section_choice_buttons:
    scene black with dissolve

    call screen choice_buttons_screen

    jump theme_test_main_menu


screen choice_buttons_screen():
    modal True

    add Solid("#000000")

    $ ch_h = gui.choice_button_height if hasattr(gui, 'choice_button_height') and gui.choice_button_height else "None (auto)"
    $ c1 = gui.choice_button_text_idle_color if hasattr(gui, 'choice_button_text_idle_color') else "(not set)"
    $ c2 = gui.choice_button_text_hover_color if hasattr(gui, 'choice_button_text_hover_color') else "(not set)"
    $ c3 = gui.choice_button_text_insensitive_color if hasattr(gui, 'choice_button_text_insensitive_color') else "(not set)"

    add Solid("#222222"):
        xsize 700
        ysize 450
        align (0.5, 0.5)

    fixed:
        align (0.5, 0.5)
        xsize 650
        yfit True

        vbox:
            spacing 10
            xalign 0.5

            text "CHOICE BUTTONS" size 28 xalign 0.5 color "#ffffff"

            null height 10

            text "{color=#88ccff}gui.choice_button_width{/color}" xalign 0.5
            text "Editor: \"Choice Button Width\" | Value: [gui.choice_button_width]" xalign 0.5 color "#dddddd"

            text "{color=#88ccff}gui.choice_button_height{/color}" xalign 0.5
            text "Editor: \"Choice Button Height\" | Value: [ch_h]" xalign 0.5 color "#dddddd"

            text "{color=#88ccff}gui.choice_spacing{/color}" xalign 0.5
            text "Editor: \"Choice Spacing\" | Value: [gui.choice_spacing]" xalign 0.5 color "#dddddd"

            null height 10

            text "Choice Text Colors:" size 20 xalign 0.5 color "#aaaaaa"

            text "Idle: [c1] | Hover: [c2]" xalign 0.5 size 16 color "#dddddd"
            text "Insensitive: [c3]" xalign 0.5 size 16 color "#dddddd"

            null height 15

            textbutton "Back" action Return() style "tt_button":
                xalign 0.5
                text_style "tt_button_text"


################################################################################
## Section 13: Buttons & Frames (NOT IN EDITOR)
################################################################################

label theme_section_buttons_frames:
    scene black with dissolve

    $ bb = gui.button_borders if hasattr(gui, 'button_borders') else "(not set)"
    $ bt = gui.button_tile if hasattr(gui, 'button_tile') else "(not set)"
    $ fb = gui.frame_borders if hasattr(gui, 'frame_borders') else "(not set)"
    $ ft = gui.frame_tile if hasattr(gui, 'frame_tile') else "(not set)"
    $ cfb = gui.confirm_frame_borders if hasattr(gui, 'confirm_frame_borders') else "(not set)"
    $ sfb = gui.skip_frame_borders if hasattr(gui, 'skip_frame_borders') else "(not set)"
    $ nfb = gui.notify_frame_borders if hasattr(gui, 'notify_frame_borders') else "(not set)"

    $ lines = [
        "{color=#ffcc00}NOT IN EDITOR{/color}",
        "",
        "{color=#88ccff}gui.button_borders{/color}: " + str(bb),
        "{color=#88ccff}gui.button_tile{/color}: " + str(bt),
        "{color=#88ccff}gui.frame_borders{/color}: " + str(fb),
        "{color=#88ccff}gui.frame_tile{/color}: " + str(ft),
        "{color=#88ccff}gui.confirm_frame_borders{/color}: " + str(cfb),
        "{color=#88ccff}gui.skip_frame_borders{/color}: " + str(sfb),
        "{color=#88ccff}gui.notify_frame_borders{/color}: " + str(nfb)
    ]

    call screen centered_info("BUTTONS & FRAMES", lines)

    jump theme_test_main_menu


################################################################################
## Section 14: NVL Mode (NOT IN EDITOR)
################################################################################

label theme_section_nvl:
    scene black with dissolve

    $ v1 = gui.nvl_borders if hasattr(gui, 'nvl_borders') else "(not set)"
    $ v2 = gui.nvl_height if hasattr(gui, 'nvl_height') else "(not set)"
    $ v3 = gui.nvl_spacing if hasattr(gui, 'nvl_spacing') else "(not set)"
    $ v4 = gui.nvl_name_xpos if hasattr(gui, 'nvl_name_xpos') else "(not set)"
    $ v5 = gui.nvl_name_width if hasattr(gui, 'nvl_name_width') else "(not set)"
    $ v6 = gui.nvl_text_xpos if hasattr(gui, 'nvl_text_xpos') else "(not set)"
    $ v7 = gui.nvl_text_width if hasattr(gui, 'nvl_text_width') else "(not set)"

    $ lines = [
        "{color=#ffcc00}NOT IN EDITOR{/color}",
        "",
        "{color=#88ccff}gui.nvl_borders{/color}: " + str(v1),
        "{color=#88ccff}gui.nvl_height{/color}: " + str(v2),
        "{color=#88ccff}gui.nvl_spacing{/color}: " + str(v3),
        "{color=#88ccff}gui.nvl_name_xpos{/color}: " + str(v4),
        "{color=#88ccff}gui.nvl_name_width{/color}: " + str(v5),
        "{color=#88ccff}gui.nvl_text_xpos{/color}: " + str(v6),
        "{color=#88ccff}gui.nvl_text_width{/color}: " + str(v7)
    ]

    call screen centered_info("NVL MODE", lines)

    jump theme_test_main_menu


################################################################################
## Section 15: History Screen (NOT IN EDITOR)
################################################################################

label theme_section_history:
    scene black with dissolve

    $ v1 = gui.history_height if hasattr(gui, 'history_height') else "(not set)"
    $ v2 = gui.history_name_xpos if hasattr(gui, 'history_name_xpos') else "(not set)"
    $ v3 = gui.history_name_width if hasattr(gui, 'history_name_width') else "(not set)"
    $ v4 = gui.history_text_xpos if hasattr(gui, 'history_text_xpos') else "(not set)"
    $ v5 = gui.history_text_width if hasattr(gui, 'history_text_width') else "(not set)"
    $ v6 = gui.history_spacing if hasattr(gui, 'history_spacing') else "(not set)"

    $ lines = [
        "{color=#ffcc00}NOT IN EDITOR{/color}",
        "",
        "{color=#88ccff}gui.history_height{/color}: " + str(v1),
        "{color=#88ccff}gui.history_name_xpos{/color}: " + str(v2),
        "{color=#88ccff}gui.history_name_width{/color}: " + str(v3),
        "{color=#88ccff}gui.history_text_xpos{/color}: " + str(v4),
        "{color=#88ccff}gui.history_text_width{/color}: " + str(v5),
        "{color=#88ccff}gui.history_spacing{/color}: " + str(v6),
        "",
        "Press 'H' to see the History screen."
    ]

    call screen centered_info("HISTORY SCREEN", lines)

    jump theme_test_main_menu


################################################################################
## Section 16: Miscellaneous (NOT IN EDITOR)
################################################################################

label theme_section_misc:
    scene black with dissolve

    $ v1 = gui.navigation_xpos if hasattr(gui, 'navigation_xpos') else "(not set)"
    $ v2 = gui.page_spacing if hasattr(gui, 'page_spacing') else "(not set)"
    $ v3 = gui.slot_spacing if hasattr(gui, 'slot_spacing') else "(not set)"
    $ v4 = gui.pref_button_spacing if hasattr(gui, 'pref_button_spacing') else "(not set)"
    $ v5 = gui.pref_spacing if hasattr(gui, 'pref_spacing') else "(not set)"
    $ v6 = gui.quick_button_text_size if hasattr(gui, 'quick_button_text_size') else "(not set)"
    $ v7 = gui.file_slot_cols if hasattr(gui, 'file_slot_cols') else "(not set)"
    $ v8 = gui.file_slot_rows if hasattr(gui, 'file_slot_rows') else "(not set)"

    $ lines = [
        "{color=#ffcc00}NOT IN EDITOR{/color}",
        "",
        "{color=#88ccff}gui.navigation_xpos{/color}: " + str(v1),
        "{color=#88ccff}gui.page_spacing{/color}: " + str(v2),
        "{color=#88ccff}gui.slot_spacing{/color}: " + str(v3),
        "{color=#88ccff}gui.pref_button_spacing{/color}: " + str(v4),
        "{color=#88ccff}gui.pref_spacing{/color}: " + str(v5),
        "{color=#88ccff}gui.quick_button_text_size{/color}: " + str(v6),
        "{color=#88ccff}gui.file_slot_cols{/color}: " + str(v7),
        "{color=#88ccff}gui.file_slot_rows{/color}: " + str(v8)
    ]

    call screen centered_info("MISCELLANEOUS", lines)

    jump theme_test_main_menu


################################################################################
## Demo Screens
################################################################################

screen colors_demo_screen():
    modal True

    add Solid("#000000")

    add Solid("#222222"):
        xsize 450
        ysize 650
        align (0.5, 0.5)

    fixed:
        align (0.5, 0.5)
        xsize 400
        yfit True

        vbox:
            spacing 10
            xalign 0.5

            text "COLOR PALETTE" size 30 xalign 0.5 color "#ffffff"

            null height 15

            grid 2 5:
                spacing 20
                xalign 0.5

                vbox:
                    spacing 5
                    text "gui.accent_color" size 14 xalign 0.5 color "#dddddd"
                    add Solid(gui.accent_color) xsize 140 ysize 35

                vbox:
                    spacing 5
                    text "gui.hover_color" size 14 xalign 0.5 color "#dddddd"
                    add Solid(gui.hover_color) xsize 140 ysize 35

                vbox:
                    spacing 5
                    text "gui.idle_color" size 14 xalign 0.5 color "#dddddd"
                    add Solid(gui.idle_color) xsize 140 ysize 35

                vbox:
                    spacing 5
                    text "gui.idle_small_color" size 14 xalign 0.5 color "#dddddd"
                    add Solid(gui.idle_small_color) xsize 140 ysize 35

                vbox:
                    spacing 5
                    text "gui.selected_color" size 14 xalign 0.5 color "#dddddd"
                    add Solid(gui.selected_color) xsize 140 ysize 35

                vbox:
                    spacing 5
                    text "gui.insensitive_color" size 14 xalign 0.5 color "#dddddd"
                    add Solid(gui.insensitive_color) xsize 140 ysize 35

                vbox:
                    spacing 5
                    text "gui.text_color" size 14 xalign 0.5 color "#dddddd"
                    add Solid(gui.text_color) xsize 140 ysize 35

                vbox:
                    spacing 5
                    text "gui.interface_text_color" size 14 xalign 0.5 color "#dddddd"
                    add Solid(gui.interface_text_color) xsize 140 ysize 35

                vbox:
                    spacing 5
                    text "gui.muted_color" size 14 xalign 0.5 color "#dddddd"
                    add Solid(gui.muted_color) xsize 140 ysize 35

                vbox:
                    spacing 5
                    text "gui.hover_muted_color" size 14 xalign 0.5 color "#dddddd"
                    add Solid(gui.hover_muted_color) xsize 140 ysize 35

            null height 20

            textbutton "Close" action Return() style "tt_button":
                xalign 0.5
                text_style "tt_button_text"


screen ui_details_demo_screen():
    modal True

    add Solid("#000000")

    add Solid("#222222"):
        xsize 500
        ysize 550
        align (0.5, 0.5)

    fixed:
        align (0.5, 0.5)
        xsize 450
        yfit True

        vbox:
            spacing 15
            xalign 0.5

            text "UI INTERACTIVE DEMO" size 28 xalign 0.5 color "#ffffff"

            null height 10

            # Bar demo
            hbox:
                spacing 20
                xalign 0.5
                text "Progress Bar:" yalign 0.5 xsize 150 color "#dddddd"
                bar value 0.6 xsize 250

            # Slider demo
            hbox:
                spacing 20
                xalign 0.5
                text "Slider:" yalign 0.5 xsize 150 color "#dddddd"
                bar value FieldValue(persistent, "_demo_slider", 1.0, offset=0) xsize 250

            null height 5

            # Scrollable content
            text "Scrollable Content:" size 18 xalign 0.5 color "#dddddd"

            viewport:
                xsize 350
                ysize 80
                xalign 0.5
                scrollbars "vertical"
                mousewheel True

                vbox:
                    for i in range(15):
                        text "Scrollable item [i+1]" size 14 color "#cccccc"

            null height 10

            # Button states demo
            text "Button States:" size 18 xalign 0.5 color "#dddddd"

            hbox:
                spacing 10
                xalign 0.5
                textbutton "Normal" action NullAction() text_color "#cccccc" text_hover_color "#ffffff"
                textbutton "Selected" action NullAction() selected True text_color "#cccccc" text_hover_color "#ffffff"
                textbutton "Disabled" action NullAction() sensitive False text_color "#666666"

            null height 15

            textbutton "Close" action Return() style "tt_button":
                xalign 0.5
                text_style "tt_button_text"


default persistent._demo_slider = 0.5
