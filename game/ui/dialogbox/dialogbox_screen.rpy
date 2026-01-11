## dialogbox_screen.rpy - Custom say screen using dialogbox presets
##
## Replaces the default say screen with preset-aware version.
## Supports dynamic styling, transitions, sounds, and effects.
##
## Related files: dialogbox_manager.rpy, dialogbox.json

################################################################################
## Say Screen Override
################################################################################

## Override the default say screen with our preset-aware version
screen say(who, what):

    # Get current preset configuration
    $ preset = dialogbox_manager.get_current_preset()
    $ pos = dialogbox_manager.get_position()
    $ bg_config = dialogbox_manager.get_background()
    $ namebox_config = dialogbox_manager.get_namebox()
    $ name_style = dialogbox_manager.get_name_style()
    $ text_style = dialogbox_manager.get_text_style()
    $ box_effect_name = dialogbox_manager.get_box_effect()

    # Build background displayable
    $ bg_displayable = None
    if bg_config and bg_config.get("image"):
        $ borders = bg_config.get("borders", [30, 25, 30, 35])
        $ tile = bg_config.get("tile", False)
        $ bg_displayable = Frame(bg_config["image"], borders[0], borders[1], borders[2], borders[3], tile=tile)

    # Build namebox background displayable
    $ namebox_displayable = None
    if namebox_config and namebox_config.get("image"):
        $ nb_borders = namebox_config.get("borders", [5, 5, 5, 5])
        $ nb_tile = namebox_config.get("tile", False)
        $ namebox_displayable = Frame(namebox_config["image"], nb_borders[0], nb_borders[1], nb_borders[2], nb_borders[3], tile=nb_tile)

    # Get textshader
    $ textshader = text_style.get("textshader") if text_style else None

    # Main window container with optional box effect
    if box_effect_name:
        $ box_transform = get_box_effect_transform(box_effect_name)
        window at box_transform:
            id "window"
            style "dialogbox_window"

            xalign pos.get("xalign", 0.5)
            yalign pos.get("yalign", 1.0)
            xoffset pos.get("xoffset", 0)
            yoffset pos.get("yoffset", -30)

            if bg_displayable:
                background bg_displayable

            if who is not None:
                window:
                    id "namebox"
                    style "dialogbox_namebox"
                    if namebox_displayable:
                        background namebox_displayable

                    text who id "who" style "dialogbox_name":
                        if name_style.get("font"):
                            font name_style["font"]
                        if name_style.get("size"):
                            size name_style["size"]
                        if name_style.get("color"):
                            color name_style["color"]
                        if name_style.get("outlines"):
                            outlines name_style["outlines"]

            text what id "what" style "dialogbox_dialogue":
                if text_style.get("font"):
                    font text_style["font"]
                if text_style.get("size"):
                    size text_style["size"]
                if text_style.get("color"):
                    color text_style["color"]
                if text_style.get("outlines"):
                    outlines text_style["outlines"]
                if text_style.get("line_spacing"):
                    line_spacing text_style["line_spacing"]
                if textshader:
                    textshader textshader

    else:
        window:
            id "window"
            style "dialogbox_window"

            xalign pos.get("xalign", 0.5)
            yalign pos.get("yalign", 1.0)
            xoffset pos.get("xoffset", 0)
            yoffset pos.get("yoffset", -30)

            if bg_displayable:
                background bg_displayable

            if who is not None:
                window:
                    id "namebox"
                    style "dialogbox_namebox"
                    if namebox_displayable:
                        background namebox_displayable

                    text who id "who" style "dialogbox_name":
                        if name_style.get("font"):
                            font name_style["font"]
                        if name_style.get("size"):
                            size name_style["size"]
                        if name_style.get("color"):
                            color name_style["color"]
                        if name_style.get("outlines"):
                            outlines name_style["outlines"]

            text what id "what" style "dialogbox_dialogue":
                if text_style.get("font"):
                    font text_style["font"]
                if text_style.get("size"):
                    size text_style["size"]
                if text_style.get("color"):
                    color text_style["color"]
                if text_style.get("outlines"):
                    outlines text_style["outlines"]
                if text_style.get("line_spacing"):
                    line_spacing text_style["line_spacing"]
                if textshader:
                    textshader textshader

    # Side image (if not on small/phone variant)
    if not renpy.variant("small"):
        add SideImage() xalign 0.0 yalign 1.0


################################################################################
## Dialogbox Styles
################################################################################

style dialogbox_window is window:
    xfill True
    ysize gui.textbox_height

style dialogbox_namebox is namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height
    padding gui.namebox_borders.padding

style dialogbox_name is say_label:
    xalign gui.name_xalign
    yalign 0.5

style dialogbox_dialogue is say_dialogue:
    xpos gui.dialogue_xpos
    xsize gui.dialogue_width
    ypos gui.dialogue_ypos
    adjust_spacing False


################################################################################
## Dialogue Callbacks for Sound Integration
################################################################################

init python:

    # Track dialogue state for sounds
    _dialogbox_dialogue_active = False

    def dialogbox_dialogue_callback(event, interact=True, **kwargs):
        """
        Callback for dialogue events to handle sounds.

        Called by Ren'Py at various dialogue events:
        - "begin": Dialogue is starting
        - "show": Text is about to be shown
        - "slow_done": Slow text finished displaying
        - "end": Dialogue is ending
        """
        global _dialogbox_dialogue_active

        if event == "begin":
            # Dialogue starting - play appear sound
            dialogbox_manager.play_appear_sound()
            _dialogbox_dialogue_active = True

        elif event == "show":
            # Text starting to display - start typing loop if configured
            dialogbox_manager.start_typing_loop()

        elif event == "slow_done":
            # Slow text finished - stop typing loop
            dialogbox_manager.stop_typing_loop()

        elif event == "end":
            # Dialogue ending - ensure typing stopped, play dismiss
            dialogbox_manager.stop_typing_loop()
            if _dialogbox_dialogue_active:
                dialogbox_manager.play_dismiss_sound()
                _dialogbox_dialogue_active = False

    # Register the callback
    config.all_character_callbacks.append(dialogbox_dialogue_callback)


################################################################################
## Character Integration
################################################################################

init python:

    def create_dialogbox_character(name, preset="standard", **kwargs):
        """
        Create a Character with dialogbox preset support.

        Args:
            name: Character name
            preset: Dialogbox preset name
            **kwargs: Additional Character parameters

        Returns:
            Character object

        Usage:
            define novy = create_dialogbox_character("Novy", preset="standard")
        """
        # Create callback that sets preset before dialogue
        def set_preset_callback(event, **cb_kwargs):
            if event == "begin":
                dialogbox_manager.set_preset(preset)

        # Add to existing callbacks or create new list
        callbacks = kwargs.get("callback", [])
        if not isinstance(callbacks, list):
            callbacks = [callbacks]
        callbacks.insert(0, set_preset_callback)
        kwargs["callback"] = callbacks

        return Character(name, **kwargs)
