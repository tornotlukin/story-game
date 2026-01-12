## dialogbox_screen.rpy - Custom dialogbox preset system
##
## Uses Ren'Py's Character parameter system to inject styles dynamically.
## Based on how the bubble system works in Ren'Py 8.x.
##
## Related files: dialogbox_manager.rpy, dialogbox.json

################################################################################
## Say Arguments Callback - Injects preset properties into dialogue
################################################################################

init python:

    def dialogbox_say_arguments_callback(char, *args, **kwargs):
        """
        Callback that injects dialogbox preset properties into Character parameters.
        This is called before every line of dialogue.

        Properties with window_, what_, who_ prefixes are automatically
        applied to displayables with matching IDs in the say screen.

        Must return a tuple: (args, kwargs)
        """

        # Get current preset
        preset = dialogbox_manager.get_current_preset()
        if preset is None:
            return args, kwargs

        # Get position
        pos = dialogbox_manager.get_position()

        # Inject window properties (applied to id "window")
        if "window_yalign" not in kwargs:
            kwargs["window_yalign"] = pos.get("yalign", 1.0)
        if "window_xalign" not in kwargs:
            kwargs["window_xalign"] = pos.get("xalign", 0.5)
        if "window_xoffset" not in kwargs:
            kwargs["window_xoffset"] = pos.get("xoffset", 0)
        if "window_yoffset" not in kwargs:
            kwargs["window_yoffset"] = pos.get("yoffset", -30)

        # Get and inject background
        bg = dialogbox_manager.get_background()
        if bg and bg.get("image") and "window_background" not in kwargs:
            borders = bg.get("borders", [30, 25, 30, 35])
            tile = bg.get("tile", False)
            kwargs["window_background"] = Frame(
                bg["image"],
                borders[0], borders[1], borders[2], borders[3],
                tile=tile
            )

        # Inject window padding
        if bg and bg.get("padding") and "window_padding" not in kwargs:
            padding = bg["padding"]
            kwargs["window_padding"] = (padding[0], padding[1], padding[2], padding[3])

        # Get and inject text style (applied to id "what")
        text_style = dialogbox_manager.get_text_style()
        if text_style:
            if text_style.get("size") and "what_size" not in kwargs:
                kwargs["what_size"] = text_style["size"]
            if text_style.get("color") and "what_color" not in kwargs:
                kwargs["what_color"] = text_style["color"]
            if text_style.get("font") and "what_font" not in kwargs:
                kwargs["what_font"] = text_style["font"]
            if text_style.get("outlines") and "what_outlines" not in kwargs:
                kwargs["what_outlines"] = text_style["outlines"]
            # Inject textshader for text effects
            if text_style.get("textshader") and "what_textshader" not in kwargs:
                kwargs["what_textshader"] = text_style["textshader"]
            # Inject line spacing
            if text_style.get("line_spacing") is not None and "what_line_spacing" not in kwargs:
                kwargs["what_line_spacing"] = text_style["line_spacing"]
            # Inject text alignment (0.0=left, 0.5=center, 1.0=right)
            if text_style.get("text_align") is not None and "what_text_align" not in kwargs:
                kwargs["what_text_align"] = text_style["text_align"]
            # Inject text position within the window
            if text_style.get("xpos") is not None and "what_xpos" not in kwargs:
                kwargs["what_xpos"] = text_style["xpos"]
            if text_style.get("ypos") is not None and "what_ypos" not in kwargs:
                kwargs["what_ypos"] = text_style["ypos"]

        # Get and inject name style (applied to id "who")
        name_style = dialogbox_manager.get_name_style()
        if name_style:
            if name_style.get("size") and "who_size" not in kwargs:
                kwargs["who_size"] = name_style["size"]
            if name_style.get("color") and "who_color" not in kwargs:
                kwargs["who_color"] = name_style["color"]
            if name_style.get("font") and "who_font" not in kwargs:
                kwargs["who_font"] = name_style["font"]
            if name_style.get("outlines") and "who_outlines" not in kwargs:
                kwargs["who_outlines"] = name_style["outlines"]

        # Get and inject namebox position (applied to id "namebox" container)
        # Note: screens.rpy registers 'namebox' as a character_id_prefix
        # Namebox is now outside the window in a fixed container
        namebox = dialogbox_manager.get_namebox()
        if namebox:
            # Position properties for the namebox container
            if namebox.get("xpos") is not None and "namebox_xpos" not in kwargs:
                kwargs["namebox_xpos"] = namebox["xpos"]
            if namebox.get("ypos") is not None and "namebox_ypos" not in kwargs:
                kwargs["namebox_ypos"] = namebox["ypos"]
            if namebox.get("xoffset") is not None and "namebox_xoffset" not in kwargs:
                kwargs["namebox_xoffset"] = namebox["xoffset"]
            if namebox.get("yoffset") is not None and "namebox_yoffset" not in kwargs:
                kwargs["namebox_yoffset"] = namebox["yoffset"]
            # Alignment properties
            if namebox.get("xalign") is not None and "namebox_xalign" not in kwargs:
                kwargs["namebox_xalign"] = namebox["xalign"]
            if namebox.get("yalign") is not None and "namebox_yalign" not in kwargs:
                kwargs["namebox_yalign"] = namebox["yalign"]

        # Return tuple of (args, kwargs) as required
        return args, kwargs

    # Register the callback
    config.say_arguments_callback = dialogbox_say_arguments_callback


################################################################################
## Dialogue Callbacks for Sound Integration
################################################################################

init python:

    # Track dialogue state for sounds
    _dialogbox_dialogue_active = False

    def dialogbox_dialogue_callback(event, interact=True, **kwargs):
        """
        Callback for dialogue events to handle sounds.
        """
        global _dialogbox_dialogue_active

        if event == "begin":
            dialogbox_manager.play_appear_sound()
            _dialogbox_dialogue_active = True

        elif event == "show":
            dialogbox_manager.start_typing_loop()

        elif event == "slow_done":
            dialogbox_manager.stop_typing_loop()

        elif event == "end":
            dialogbox_manager.stop_typing_loop()
            if _dialogbox_dialogue_active:
                dialogbox_manager.play_dismiss_sound()
                _dialogbox_dialogue_active = False

    # Register the callback
    config.all_character_callbacks.append(dialogbox_dialogue_callback)
