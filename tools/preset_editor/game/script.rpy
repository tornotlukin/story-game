## script.rpy - Preset Editor Test Game
##
## Minimal Ren'Py game for testing preset combinations.
## Generated demos are saved to content/preset_demo.rpy

# Test character
define test = Character("Test")

# Placeholder images
image bg_test = Solid("#2a2a3a")
image test_char = Solid("#666688", xsize=400, ysize=700)

label start:
    scene bg_test with dissolve

    "Welcome to the Preset Editor Test Game!"
    "This environment tests your preset transitions and shaders."

    menu:
        "Run Preset Demo" if renpy.loadable("content/preset_demo.rpy"):
            jump preset_demo

        "No demo found - export one from the Preset Editor":
            "Use Tools > Export Demo in the Preset Editor."
            "Then reload this game to test your presets."
            jump start

        "Exit":
            return
