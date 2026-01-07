## script.rpy - Main story entry point
##
## This is where your story begins. The 'start' label is called
## when the player clicks "Start Game" on the main menu.
##
## Related files: characters.rpy

################################################################################
## Story Start
################################################################################

label start:

    ## Example: Show a scene
    # scene bg room with fade

    ## Example: Show a character
    # show eileen happy with dissolve

    "Welcome to your new Ren'Py project."

    "This template includes systems for:"

    "- State management (flags, variables, stats)"

    "- Dice rolling (skill checks, random events)"

    "- Touch-friendly UI (works on mobile and desktop)"

    ## Example: Using the dice system
    # $ result, rolls = dice.roll("1d20")
    # "You rolled a [result]!"

    ## Example: Setting a flag
    # $ game_state.set_flag("intro_complete")

    ## Example: Checking a flag
    # if game_state.has_flag("intro_complete"):
    #     "You've completed the intro before."

    ## Example: A choice menu
    menu:
        "What would you like to do?"

        "Explore the systems":
            jump explore_systems

        "Start writing my story":
            jump writing_tips

        "Exit for now":
            jump ending


label explore_systems:

    "The systems/ folder contains reusable game logic."

    "State Manager - tracks flags, stats, and variables:"
    $ game_state.set_flag("explored_systems")
    "Flag 'explored_systems' has been set!"

    "Dice System - handles random rolls:"
    $ result, rolls = dice.roll("2d6")
    "You rolled 2d6 and got: [result]"

    jump ending


label writing_tips:

    "To write your story:"

    "1. Define characters in content/characters.rpy"

    "2. Create new .rpy files in content/ for chapters"

    "3. Use 'label' to create story sections"

    "4. Use 'jump' to move between sections"

    "5. Use 'menu' for player choices"

    jump ending


label ending:

    "That's the basic template!"

    "Check the README.md and claude.md for more guidance."

    "Happy creating!"

    return
