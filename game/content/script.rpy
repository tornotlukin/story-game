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

    "Welcome to the Transition and Dialogbox Demo!"

    menu:
        "What would you like to do?"

        "Test character transitions":
            jump test_transitions

        "Test dialogbox presets":
            jump test_dialogbox

        "Test text effects":
            jump test_text_effects

        "Test sounds":
            jump test_sounds

        "Exit to Main Menu":
            return

        "Quit Game":
            $ renpy.quit()


################################################################################
## Transition Test - Positioned Transitions
################################################################################

label test_transitions:

    scene bg_street with dissolve

    "Let's test the character entrance and exit animations."
    "Now with POSITION support - characters land where you want them!"

    ## === CENTER POSITION (default) ===
    "SLIDE LEFT ENTER - Landing at CENTER (xalign=0.5)"
    show novy front at slide_left_enter(xalign=0.5, yalign=1.0)
    novy "I slid in from the left and landed at center!"
    hide novy front with dissolve

    ## === LEFT POSITION ===
    "SLIDE LEFT ENTER - Landing at LEFT SIDE (xalign=0.2)"
    show novy front at slide_left_enter(xalign=0.2, yalign=1.0)
    novy "This time I landed on the left side of the screen!"
    hide novy front with dissolve

    ## === RIGHT POSITION ===
    "SLIDE RIGHT ENTER - Landing at RIGHT SIDE (xalign=0.8)"
    show novy front at slide_right_enter(xalign=0.8, yalign=1.0)
    novy "Now I'm on the right side!"
    hide novy front with dissolve

    ## === RISE UP TO CENTER ===
    "RISE UP ENTER - Landing at CENTER"
    show novy front at rise_up_enter(xalign=0.5, yalign=1.0)
    novy "Rising up to center!"
    hide novy front with dissolve

    ## === DROP DOWN TO LEFT ===
    "DROP DOWN ENTER - Landing at LEFT (xalign=0.3)"
    show novy front at drop_down_enter(xalign=0.3, yalign=1.0)
    novy "Dropped in on the left!"
    hide novy front with dissolve

    ## === DRAMATIC EMERGE TO RIGHT ===
    "DRAMATIC EMERGE - Landing at RIGHT (xalign=0.7)"
    show novy front at dramatic_emerge_enter(xalign=0.7, yalign=1.0)
    novy "A dramatic entrance on the right!"
    hide novy front with dissolve

    ## === POP IN AT CENTER ===
    "POP IN - Quick entrance at CENTER"
    show novy front at pop_in_enter(xalign=0.5, yalign=1.0)
    novy "Pop!"
    hide novy front with dissolve

    ## === CORNER ENTRANCE ===
    "CORNER TOP LEFT - Landing slightly left of center"
    show novy front at corner_top_left_enter(xalign=0.4, yalign=1.0)
    novy "Came in from the corner!"
    hide novy front with dissolve

    ## === EXIT ANIMATIONS ===
    "Now let's test EXIT animations from different positions..."

    ## Exit from center
    show novy front at slide_left_enter(xalign=0.5, yalign=1.0)
    novy "I'm at center. Watch me exit left!"
    show novy front at fade_left_exit(xalign=0.5, yalign=1.0)
    $ renpy.pause(0.4)
    hide novy front

    $ renpy.pause(0.3)

    ## Exit from right side
    show novy front at slide_right_enter(xalign=0.8, yalign=1.0)
    novy "I'm on the right. Sinking down!"
    show novy front at sink_down_exit(xalign=0.8, yalign=1.0)
    $ renpy.pause(0.4)
    hide novy front

    $ renpy.pause(0.3)

    ## Exit from left side
    show novy front at slide_left_enter(xalign=0.2, yalign=1.0)
    novy "On the left. Quick vanish!"
    show novy front at vanish_quick_exit(xalign=0.2, yalign=1.0)
    $ renpy.pause(0.2)
    hide novy front

    $ renpy.pause(0.3)

    ## Spin out from center
    show novy front at rise_up_enter(xalign=0.5, yalign=1.0)
    novy "Center again. Spinning out!"
    show novy front at spin_out_exit(xalign=0.5, yalign=1.0)
    $ renpy.pause(0.5)
    hide novy front

    scene black with fade
    "Transition test complete!"
    "You can position characters anywhere using xalign (0.0-1.0)!"

    jump start


################################################################################
## Dialogbox Preset Test
################################################################################

label test_dialogbox:

    scene bg_street with dissolve

    show novy front at slide_left_enter(xalign=0.5, yalign=1.0)

    "Let's test the dialogbox preset system!"
    "Each preset has different styling, sounds, and effects."

    ## === STANDARD PRESET ===
    $ dialogbox_set("standard")
    novy "This is the STANDARD preset."
    novy "Default styling with clean text display."

    ## === DRAMATIC PRESET ===
    $ dialogbox_set("dramatic")
    novy "This is the DRAMATIC preset!"
    novy "Notice the different colors and text animation."

    ## === WHISPER PRESET ===
    $ dialogbox_set("whisper")
    novy "...and this is the whisper preset..."
    novy "...softer colors, smaller text..."

    ## === FRIGHTENED PRESET ===
    $ dialogbox_set("frightened")
    novy "T-this is the frightened preset!"
    novy "The text should be shaky and the box might jitter!"

    ## === TYPEWRITER PRESET ===
    $ dialogbox_set("typewriter")
    novy "This is the typewriter preset."
    novy "Monospace font with typing sounds."

    ## === ANNOUNCEMENT PRESET ===
    $ dialogbox_set("announcement")
    "This is the announcement preset."
    "Centered on screen for important messages."

    ## === RESET TO STANDARD ===
    $ dialogbox_reset()
    novy "And we're back to normal!"

    ## === POSITION OVERRIDE ===
    "You can also override the dialogbox position..."

    $ dialogbox_position(yalign=0.3)
    novy "Now the dialogbox is at the top of the screen!"

    $ dialogbox_position(yalign=0.5)
    novy "And now it's in the center!"

    $ dialogbox_manager.clear_position_override()
    novy "Back to the normal bottom position."

    hide novy front with dissolve
    scene black with fade

    "Dialogbox preset test complete!"

    jump start


################################################################################
## Text Effects Test
################################################################################

label test_text_effects:

    scene bg_street with dissolve
    show novy front at slide_left_enter(xalign=0.5, yalign=1.0)

    "Let's test the custom text tags!"

    ## === SIZE TAGS ===
    novy "This is {big=2}BIG{/big} text and {small}small{/small} text!"

    ## === STYLE TAGS ===
    novy "This is {sc}small caps{/sc} text."
    novy "This is {highlight}highlighted{/highlight} text!"
    novy "This is {em}emphasized{/em} text."

    ## === MOOD TAGS ===
    novy "{alert}WARNING: This is an alert!{/alert}"
    novy "{quiet}...this is very quiet...{/quiet}"
    novy "{thought}I wonder what's going to happen next...{/thought}"
    novy "{shout}HEY! PAY ATTENTION!{/shout}"

    ## === TIMING TAGS ===
    novy "Let me think{beat}... okay, I've got it!"
    novy "And then{pause}... nothing happened."

    ## === SYMBOL TAGS ===
    novy "I {heart} this game!"
    novy "You're a {star} superstar!"

    ## === BUILT-IN TEXTSHADERS ===
    "Now let's test the built-in text shaders..."

    $ dialogbox_set("standard")

    novy "Normal text without any shader."

    # These require textshader support in the preset or direct shader tags
    "Using the {shader=wave}wave shader{/shader} for wavy text!"
    "Using the {shader=jitter:3,3}jitter shader{/shader} for shaky text!"

    ## === FRIGHTENED PRESET (has jitter textshader) ===
    $ dialogbox_set("frightened")
    novy "The frightened preset has built-in jitter!"
    novy "Every line is shaky automatically!"

    $ dialogbox_reset()

    hide novy front with dissolve
    scene black with fade

    "Text effects test complete!"

    jump start


################################################################################
## Sound Test
################################################################################

label test_sounds:

    scene bg_street with dissolve

    "Let's test the footstep sounds."

    "Playing sand footstep (left)..."
    play sound "audio/Fantozzi-SandL1.ogg"
    $ renpy.pause(0.5)

    "Playing sand footstep (right)..."
    play sound "audio/Fantozzi-SandR1.ogg"
    $ renpy.pause(0.5)

    "Playing stone footstep (left)..."
    play sound "audio/Fantozzi-StoneL1.ogg"
    $ renpy.pause(0.5)

    "Playing stone footstep (right)..."
    play sound "audio/Fantozzi-StoneR1.ogg"
    $ renpy.pause(0.5)

    "Sound test complete!"

    jump start
