## text_effects.rpy - Custom text tags for dialogue effects
##
## Registers custom text tags that can be used in dialogue.
## These complement Ren'Py's built-in textshaders.
##
## Built-in textshaders (use with {shader=name} or style textshader):
##   - wave, jitter, dissolve, typewriter, flip, zoom, offset, texture
##
## Custom tags defined here (use with {tagname}...{/tagname}):
##   - {big=N} - Scale text by multiplier N
##   - {sc} - Small caps
##   - {highlight} - Highlighted text
##   - {em} - Emphasis (color + italic)
##
## Related files: text_effects.json, dialogbox_manager.rpy

init python:
    import json
    import os

    class TextEffectsLoader:
        """Loads text effect configuration from JSON."""

        def __init__(self):
            self._config = None
            self._effects = {}

        def load(self, config_path="ui/dialogbox/text_effects.json"):
            """Load text effects configuration."""
            try:
                full_path = os.path.join(config.gamedir, config_path)
                with open(full_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                self._effects = self._config.get("effects", {})
                print(f"TextEffectsLoader: Loaded {len(self._effects)} effects")
                return True
            except Exception as e:
                print(f"TextEffectsLoader: Error loading: {e}")
                return False

        def get_effect(self, name):
            """Get effect configuration by name."""
            return self._effects.get(name)

    # Create global loader
    text_effects_loader = TextEffectsLoader()
    text_effects_loader.load()


################################################################################
## Custom Text Tags
################################################################################

init python:

    # {big=N} - Multiplies text size by N
    # Usage: "This is {big=2}BIG{/big} text!"
    def big_tag(tag, argument, contents):
        try:
            multiplier = float(argument) if argument else 2.0
            size = int(gui.text_size * multiplier)
        except:
            size = gui.text_size * 2

        return [
            (renpy.TEXT_TAG, f"size={size}"),
        ] + contents + [
            (renpy.TEXT_TAG, "/size"),
        ]

    config.custom_text_tags["big"] = big_tag


    # {small=N} - Multiplies text size by N (default 0.7)
    # Usage: "This is {small}small{/small} text!"
    def small_tag(tag, argument, contents):
        try:
            multiplier = float(argument) if argument else 0.7
            size = int(gui.text_size * multiplier)
        except:
            size = int(gui.text_size * 0.7)

        return [
            (renpy.TEXT_TAG, f"size={size}"),
        ] + contents + [
            (renpy.TEXT_TAG, "/size"),
        ]

    config.custom_text_tags["small"] = small_tag


    # {sc} - Small caps effect
    # Usage: "This is {sc}important{/sc}!"
    def sc_tag(tag, argument, contents):
        """Small caps - uppercase at smaller size."""
        result = []
        size = int(gui.text_size * 0.85)

        result.append((renpy.TEXT_TAG, f"size={size}"))

        for kind, text in contents:
            if kind == renpy.TEXT_TEXT:
                result.append((renpy.TEXT_TEXT, text.upper()))
            else:
                result.append((kind, text))

        result.append((renpy.TEXT_TAG, "/size"))
        return result

    config.custom_text_tags["sc"] = sc_tag


    # {highlight} - Highlighted text with background color
    # Usage: "This is {highlight}highlighted{/highlight}!"
    def highlight_tag(tag, argument, contents):
        # Default highlight color, or use argument
        color = argument if argument else "#FFFF00"
        # Note: Ren'Py doesn't support background color on text spans directly
        # We'll use a bright color instead as a workaround
        return [
            (renpy.TEXT_TAG, f"color={color}"),
            (renpy.TEXT_TAG, "b"),
        ] + contents + [
            (renpy.TEXT_TAG, "/b"),
            (renpy.TEXT_TAG, "/color"),
        ]

    config.custom_text_tags["highlight"] = highlight_tag


    # {em} or {emphasis} - Emphasis with color and italic
    # Usage: "This is {em}emphasized{/em}!"
    def em_tag(tag, argument, contents):
        color = argument if argument else "#FFD700"  # Gold by default
        return [
            (renpy.TEXT_TAG, f"color={color}"),
            (renpy.TEXT_TAG, "i"),
        ] + contents + [
            (renpy.TEXT_TAG, "/i"),
            (renpy.TEXT_TAG, "/color"),
        ]

    config.custom_text_tags["em"] = em_tag
    config.custom_text_tags["emphasis"] = em_tag


    # {alert} - Alert/warning text style
    # Usage: "This is {alert}dangerous{/alert}!"
    def alert_tag(tag, argument, contents):
        return [
            (renpy.TEXT_TAG, "color=#FF4444"),
            (renpy.TEXT_TAG, "b"),
        ] + contents + [
            (renpy.TEXT_TAG, "/b"),
            (renpy.TEXT_TAG, "/color"),
        ]

    config.custom_text_tags["alert"] = alert_tag


    # {quiet} - Quiet/subdued text style
    # Usage: "This is {quiet}whispered{/quiet}..."
    def quiet_tag(tag, argument, contents):
        size = int(gui.text_size * 0.85)
        return [
            (renpy.TEXT_TAG, "color=#AAAAAA"),
            (renpy.TEXT_TAG, f"size={size}"),
            (renpy.TEXT_TAG, "i"),
        ] + contents + [
            (renpy.TEXT_TAG, "/i"),
            (renpy.TEXT_TAG, "/size"),
            (renpy.TEXT_TAG, "/color"),
        ]

    config.custom_text_tags["quiet"] = quiet_tag


    # {thought} - Internal thought style
    # Usage: "{thought}I wonder what that means...{/thought}"
    def thought_tag(tag, argument, contents):
        return [
            (renpy.TEXT_TAG, "color=#CCCCFF"),
            (renpy.TEXT_TAG, "i"),
        ] + contents + [
            (renpy.TEXT_TAG, "/i"),
            (renpy.TEXT_TAG, "/color"),
        ]

    config.custom_text_tags["thought"] = thought_tag


    # {shout} - Shouting style
    # Usage: "{shout}STOP RIGHT THERE!{/shout}"
    def shout_tag(tag, argument, contents):
        size = int(gui.text_size * 1.3)
        result = []
        result.append((renpy.TEXT_TAG, f"size={size}"))
        result.append((renpy.TEXT_TAG, "b"))

        for kind, text in contents:
            if kind == renpy.TEXT_TEXT:
                result.append((renpy.TEXT_TEXT, text.upper()))
            else:
                result.append((kind, text))

        result.append((renpy.TEXT_TAG, "/b"))
        result.append((renpy.TEXT_TAG, "/size"))
        return result

    config.custom_text_tags["shout"] = shout_tag


################################################################################
## Self-Closing Tags
################################################################################

init python:

    # {beat} - Short pause
    # Usage: "I was thinking{beat} maybe we should go."
    def beat_tag(tag, argument):
        delay = float(argument) if argument else 0.3
        return [(renpy.TEXT_TAG, f"w={delay}")]

    config.self_closing_custom_text_tags["beat"] = beat_tag


    # {pause} - Longer pause
    # Usage: "And then{pause}... it happened."
    def pause_tag(tag, argument):
        delay = float(argument) if argument else 1.0
        return [(renpy.TEXT_TAG, f"w={delay}")]

    config.self_closing_custom_text_tags["pause"] = pause_tag


    # {heart} - Heart emoji/symbol
    # Usage: "I love you{heart}!"
    def heart_tag(tag, argument):
        return [(renpy.TEXT_TEXT, "\u2665")]  # ♥

    config.self_closing_custom_text_tags["heart"] = heart_tag


    # {star} - Star symbol
    # Usage: "You're a {star} star!"
    def star_tag(tag, argument):
        return [(renpy.TEXT_TEXT, "\u2605")]  # ★

    config.self_closing_custom_text_tags["star"] = star_tag


    # {ellipsis} - Animated ellipsis (just dots, animation via textshader)
    # Usage: "Loading{ellipsis}"
    def ellipsis_tag(tag, argument):
        return [(renpy.TEXT_TEXT, "...")]

    config.self_closing_custom_text_tags["ellipsis"] = ellipsis_tag
