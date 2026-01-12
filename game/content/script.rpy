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

        "Test shader effects":
            jump test_shaders

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


################################################################################
## Shader Effects Test
################################################################################

label test_shaders:

    scene bg_street with dissolve

    "Welcome to the Shader Effects Demo!"
    "I'll showcase various shader effects using Novy-chan."

    show novy front at center with dissolve
    novy "Hi! I'm going to be your shader demo model today!"

    jump shader_menu

label shader_menu:

    menu:
        "Which shader category would you like to see?"

        "Glow Effects":
            jump shader_glow

        "Color Adjustments":
            jump shader_color

        "Distortion Effects":
            jump shader_distort

        "Retro/Stylized Effects":
            jump shader_retro

        "Outline Effects":
            jump shader_outline

        "Blur Effects":
            jump shader_blur

        "Mood/Combined Effects":
            jump shader_mood

        "Animated Effects":
            jump shader_animated

        "Return to Main Menu":
            hide novy front with dissolve
            scene black with fade
            jump start


################################################################################
## Glow Effects
################################################################################

label shader_glow:

    "=== GLOW EFFECTS ==="

    show novy front at center
    novy "Here I am without any effects."

    show novy front at glow_white
    novy "White glow - clean and bright!"

    show novy front at glow_gold
    novy "Gold glow - magical and warm!"

    show novy front at glow_red
    novy "Red glow - intense and fiery!"

    show novy front at glow_blue
    novy "Blue glow - cool and mystical!"

    show novy front at glow_green
    novy "Green glow - nature magic!"

    show novy front at glow_purple
    novy "Purple glow - mysterious power!"

    show novy front at glow_pink
    novy "Pink glow - kawaii energy!"

    show novy front at center
    "Glow effects complete!"

    jump shader_menu


################################################################################
## Color Adjustments
################################################################################

label shader_color:

    "=== COLOR ADJUSTMENT EFFECTS ==="

    show novy front at center
    novy "Normal colors first."

    show novy front at grayscale
    novy "Grayscale - classic black and white."

    show novy front at grayscale_partial
    novy "Partial grayscale - slightly desaturated."

    show novy front at sepia
    novy "Sepia - vintage photograph look."

    show novy front at sepia_light
    novy "Light sepia - subtle vintage tone."

    show novy front at invert
    novy "Inverted colors - negative effect!"

    show novy front at brighten
    novy "Brightened - more light!"

    show novy front at darken
    novy "Darkened - shadowy."

    show novy front at high_contrast
    novy "High contrast - bold and punchy!"

    show novy front at saturate
    novy "Saturated - vivid colors!"

    show novy front at desaturate
    novy "Desaturated - muted tones."

    show novy front at tint_red
    novy "Red tint - warm and alert."

    show novy front at tint_blue
    novy "Blue tint - cold and calm."

    show novy front at tint_warm
    novy "Warm tint - cozy feeling."

    show novy front at tint_cool
    novy "Cool tint - fresh and clean."

    show novy front at hue_shift_small
    novy "Small hue shift - subtle color change."

    show novy front at hue_shift_opposite
    novy "Opposite hue - completely different palette!"

    show novy front at center
    "Color adjustment effects complete!"

    jump shader_menu


################################################################################
## Distortion Effects
################################################################################

label shader_distort:

    "=== DISTORTION EFFECTS ==="

    show novy front at center
    novy "Starting with no distortion."

    show novy front at fisheye_light
    novy "Light fisheye - subtle bulge."

    show novy front at fisheye_heavy
    novy "Heavy fisheye - big bubble effect!"

    show novy front at pincushion
    novy "Pincushion - inward curve."

    show novy front at wave_gentle
    novy "Gentle wave - soft underwater feel."

    show novy front at wave_strong
    novy "Strong wave - really wavy!"

    show novy front at wave_dreamy
    novy "Dreamy wave - slow and hypnotic."

    show novy front at ripple_calm
    novy "Calm ripple - like a pond."

    show novy front at ripple_intense
    novy "Intense ripple - splashy!"

    show novy front at shake_light
    novy "Light shake - a bit nervous."

    show novy front at shake_heavy
    novy "Heavy shake - very unstable!"

    show novy front at shake_panic
    novy "Panic shake - AAAHHH!"

    show novy front at center
    "Distortion effects complete!"

    jump shader_menu


################################################################################
## Retro/Stylized Effects
################################################################################

label shader_retro:

    "=== RETRO/STYLIZED EFFECTS ==="

    show novy front at center
    novy "Normal appearance first."

    show novy front at pixelate_light
    novy "Light pixelate - subtle retro."

    show novy front at pixelate_medium
    novy "Medium pixelate - 8-bit style!"

    show novy front at pixelate_heavy
    novy "Heavy pixelate - very blocky!"

    show novy front at pixelate_extreme
    novy "Extreme pixelate - can you even see me?"

    show novy front at scanlines_subtle
    novy "Subtle scanlines - hint of CRT."

    show novy front at scanlines_crt
    novy "CRT scanlines - old TV feel."

    show novy front at scanlines_heavy
    novy "Heavy scanlines - very retro!"

    show novy front at vignette_light
    novy "Light vignette - subtle frame."

    show novy front at vignette_medium
    novy "Medium vignette - cinematic!"

    show novy front at vignette_heavy
    novy "Heavy vignette - dramatic spotlight!"

    show novy front at vignette_dramatic
    novy "Dramatic vignette - intense focus!"

    show novy front at chromatic_subtle
    novy "Subtle chromatic aberration - slight RGB split."

    show novy front at chromatic_medium
    novy "Medium chromatic - more noticeable."

    show novy front at chromatic_heavy
    novy "Heavy chromatic - trippy!"

    show novy front at glitch_light
    novy "Light glitch - minor corruption."

    show novy front at glitch_medium
    novy "Medium glitch - getting unstable!"

    show novy front at glitch_heavy
    novy "Heavy glitch - SYSTEM ERROR!"

    show novy front at center
    "Retro effects complete!"

    jump shader_menu


################################################################################
## Outline Effects
################################################################################

label shader_outline:

    "=== OUTLINE EFFECTS ==="

    show novy front at center
    novy "No outline to start."

    show novy front at outline_black
    novy "Black outline - classic comic style!"

    show novy front at outline_white
    novy "White outline - glowing edge!"

    show novy front at outline_gold
    novy "Gold outline - premium feel!"

    show novy front at center
    "Outline effects complete!"

    jump shader_menu


################################################################################
## Blur Effects
################################################################################

label shader_blur:

    "=== BLUR EFFECTS ==="

    show novy front at center
    novy "Sharp and clear."

    show novy front at blur_light
    novy "Light blur - slightly soft."

    show novy front at blur_medium
    novy "Medium blur - out of focus."

    show novy front at blur_heavy
    novy "Heavy blur - very fuzzy!"

    show novy front at blur_radial_light
    novy "Light radial blur - subtle motion."

    show novy front at blur_radial_heavy
    novy "Heavy radial blur - zooming effect!"

    show novy front at blur_gaussian_light
    novy "Light gaussian blur - smooth."

    show novy front at blur_gaussian_heavy
    novy "Heavy gaussian blur - very soft!"

    show novy front at bokeh_light
    novy "Light bokeh - photography style."

    show novy front at bokeh_medium
    novy "Medium bokeh - dreamy depth of field."

    show novy front at bokeh_heavy
    novy "Heavy bokeh - artistic blur!"

    show novy front at center
    "Blur effects complete!"

    jump shader_menu


################################################################################
## Mood/Combined Effects
################################################################################

label shader_mood:

    "=== MOOD/COMBINED EFFECTS ==="
    "These are preset combinations for common scenarios."

    show novy front at center
    novy "Normal mood first."

    show novy front at flashback
    novy "Flashback - remembering the past..."

    show novy front at dream
    novy "Dream - floating in imagination..."

    show novy front at horror
    novy "Horror - something isn't right..."

    show novy front at hurt
    novy "Hurt - ouch, that stings!"

    show novy front at frozen
    novy "Frozen - so... c-cold..."

    show novy front at poisoned
    novy "Poisoned - feeling sick..."

    show novy front at old_tv
    novy "Old TV - broadcast from the past."

    show novy front at center
    "Mood effects complete!"

    jump shader_menu


################################################################################
## Animated Effects
################################################################################

label shader_animated:

    "=== ANIMATED EFFECTS ==="
    "These effects animate over time!"

    show novy front at center
    novy "Watch the animations..."

    show novy front at glow_pulse_white
    "Pulsing white glow..."
    $ renpy.pause(3.0)

    show novy front at glow_pulse_gold
    "Pulsing gold glow..."
    $ renpy.pause(3.0)

    show novy front at glow_pulse_red
    "Pulsing red glow - heartbeat style!"
    $ renpy.pause(3.0)

    show novy front at power_up
    "Power up effect!"
    $ renpy.pause(3.0)

    show novy front at wave_gentle
    "Gentle wave animation..."
    $ renpy.pause(3.0)

    show novy front at ripple_calm
    "Ripple animation..."
    $ renpy.pause(3.0)

    show novy front at glitch_medium
    "Glitch animation..."
    $ renpy.pause(3.0)

    show novy front at center
    "Animated effects complete!"

    jump shader_menu
