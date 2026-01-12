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

        "Test scene presets":
            jump test_presets

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
##
## Demo organized by shader file:
##   - shader_glow.rpy    -> Glow Effects
##   - shader_blur.rpy    -> Blur Effects
##   - shader_distort.rpy -> Distortion Effects
##   - shader_color.rpy   -> Color Adjustments
##   - shader_retro.rpy   -> Retro/Stylized Effects
##   - shader_fx.rpy      -> Special FX (outline, light rays, threshold)
##   - shader_transforms.rpy -> All transform presets
##
################################################################################

## Center-screen transform for shader demo (character in middle of screen)
transform shader_demo_center:
    xalign 0.5
    yalign 0.5

label test_shaders:

    scene bg_street with dissolve

    "Welcome to the Shader Effects Demo!"
    "Shaders are organized into category files for easy maintenance."

    show novy front at shader_demo_center with dissolve
    novy "Hi! I'll demonstrate each shader category!"

    jump shader_menu

label shader_menu:

    menu:
        "Which shader category would you like to see?"

        "Glow Effects (shader_glow.rpy)":
            jump shader_glow

        "Blur Effects (shader_blur.rpy)":
            jump shader_blur

        "Distortion Effects (shader_distort.rpy)":
            jump shader_distort

        "Color Adjustments (shader_color.rpy)":
            jump shader_color

        "Retro/Stylized (shader_retro.rpy)":
            jump shader_retro

        "Special FX (shader_fx.rpy)":
            jump shader_fx

        "Mood Presets (combined effects)":
            jump shader_mood

        "Animation Demos":
            jump shader_animated

        "Return to Main Menu":
            hide novy front with dissolve
            scene black with fade
            jump start


################################################################################
## Glow Effects (shader_glow.rpy)
## Shaders: shader.glow, shader.glow_pulse
################################################################################

label shader_glow:

    "=== GLOW EFFECTS (shader_glow.rpy) ==="

    show novy front at shader_demo_center
    novy "Here I am without any effects."

    "Static glow colors..."

    show novy front at shader_demo_center, glow_white
    novy "White glow - clean and bright!"

    show novy front at shader_demo_center, glow_gold
    novy "Gold glow - magical and warm!"

    show novy front at shader_demo_center, glow_red
    novy "Red glow - intense and fiery!"

    show novy front at shader_demo_center, glow_blue
    novy "Blue glow - cool and mystical!"

    show novy front at shader_demo_center, glow_green
    novy "Green glow - nature magic!"

    show novy front at shader_demo_center, glow_purple
    novy "Purple glow - mysterious power!"

    show novy front at shader_demo_center, glow_pink
    novy "Pink glow - kawaii energy!"

    "Now the ANIMATED pulsing glows..."

    show novy front at shader_demo_center, glow_pulse_white
    novy "Pulsing white - ethereal breathing!"

    show novy front at shader_demo_center, glow_pulse_gold
    novy "Pulsing gold - magical heartbeat!"

    show novy front at shader_demo_center, glow_pulse_red
    novy "Pulsing red - danger pulse!"

    show novy front at shader_demo_center
    "Glow effects complete!"

    jump shader_menu


################################################################################
## Blur Effects (shader_blur.rpy)
## Shaders: shader.blur_gaussian, shader.blur_gaussian_high, shader.blur_box,
##          shader.blur_bokeh, shader.blur_radial
################################################################################

label shader_blur:

    "=== BLUR EFFECTS (shader_blur.rpy) ==="

    show novy front at shader_demo_center
    novy "Sharp and clear to start."

    "Box blur (fast)..."

    show novy front at shader_demo_center, blur_light
    novy "Light box blur - slightly soft."

    show novy front at shader_demo_center, blur_medium
    novy "Medium box blur - out of focus."

    show novy front at shader_demo_center, blur_heavy
    novy "Heavy box blur - very fuzzy!"

    "Gaussian blur (smooth quality)..."

    show novy front at shader_demo_center, blur_gaussian_light
    novy "Light gaussian - smooth softness."

    show novy front at shader_demo_center, blur_gaussian_medium
    novy "Medium gaussian - dreamy."

    show novy front at shader_demo_center, blur_gaussian_heavy
    novy "Heavy gaussian - very soft!"

    show novy front at shader_demo_center, blur_gaussian_hq
    novy "HQ gaussian (13-tap) - highest quality!"

    "Bokeh blur (depth-of-field)..."

    show novy front at shader_demo_center, bokeh_light
    novy "Light bokeh - photography style."

    show novy front at shader_demo_center, bokeh_medium
    novy "Medium bokeh - dreamy DOF."

    show novy front at shader_demo_center, bokeh_heavy
    novy "Heavy bokeh - artistic blur!"

    "Radial blur (motion)..."

    show novy front at shader_demo_center, blur_radial_light
    novy "Light radial - subtle zoom."

    show novy front at shader_demo_center, blur_radial_heavy
    novy "Heavy radial - speed effect!"

    show novy front at shader_demo_center
    "Blur effects complete!"

    jump shader_menu


################################################################################
## Distortion Effects (shader_distort.rpy)
## Shaders: shader.distort_barrel, shader.distort_displacement,
##          shader.distort_wave, shader.distort_ripple, shader.distort_shake
################################################################################

label shader_distort:

    "=== DISTORTION EFFECTS (shader_distort.rpy) ==="

    show novy front at shader_demo_center
    novy "Starting with no distortion."

    "Barrel/Fisheye distortion..."

    show novy front at shader_demo_center, fisheye_light
    novy "Light fisheye - subtle bulge."

    show novy front at shader_demo_center, fisheye_heavy
    novy "Heavy fisheye - bubble effect!"

    show novy front at shader_demo_center, pincushion
    novy "Pincushion - inward curve."

    "Wave distortion (animated)..."

    show novy front at shader_demo_center, wave_gentle
    novy "Gentle wave - underwater feel."

    show novy front at shader_demo_center, wave_strong
    novy "Strong wave - really wavy!"

    show novy front at shader_demo_center, wave_dreamy
    novy "Dreamy wave - slow and hypnotic."

    "Ripple distortion (animated)..."

    show novy front at shader_demo_center, ripple_calm
    novy "Calm ripple - like a pond."

    show novy front at shader_demo_center, ripple_intense
    novy "Intense ripple - splashy!"

    "Shake distortion (animated)..."

    show novy front at shader_demo_center, shake_light
    novy "Light shake - a bit nervous."

    show novy front at shader_demo_center, shake_heavy
    novy "Heavy shake - very unstable!"

    show novy front at shader_demo_center, shake_panic
    novy "Panic shake - AAAHHH!"

    show novy front at shader_demo_center
    "Distortion effects complete!"

    jump shader_menu


################################################################################
## Color Adjustments (shader_color.rpy)
## Shaders: shader.color_matrix, shader.color_grayscale, shader.color_sepia,
##          shader.color_invert, shader.color_adjust, shader.color_hue,
##          shader.color_tint
################################################################################

label shader_color:

    "=== COLOR ADJUSTMENTS (shader_color.rpy) ==="

    show novy front at shader_demo_center
    novy "Normal colors first."

    "Grayscale..."

    show novy front at shader_demo_center, grayscale
    novy "Full grayscale - black and white."

    show novy front at shader_demo_center, grayscale_partial
    novy "Partial grayscale - desaturated."

    "Sepia tone..."

    show novy front at shader_demo_center, sepia
    novy "Sepia - vintage photograph."

    show novy front at shader_demo_center, sepia_light
    novy "Light sepia - subtle vintage."

    "Color inversion..."

    show novy front at shader_demo_center, invert
    novy "Inverted - negative effect!"

    show novy front at shader_demo_center, invert_partial
    novy "Partial invert - ghostly."

    "Brightness and contrast..."

    show novy front at shader_demo_center, brighten
    novy "Brightened - more light!"

    show novy front at shader_demo_center, darken
    novy "Darkened - shadowy."

    show novy front at shader_demo_center, high_contrast
    novy "High contrast - bold!"

    show novy front at shader_demo_center, low_contrast
    novy "Low contrast - flat."

    "Saturation..."

    show novy front at shader_demo_center, saturate
    novy "Saturated - vivid colors!"

    show novy front at shader_demo_center, desaturate
    novy "Desaturated - muted tones."

    "Color tinting..."

    show novy front at shader_demo_center, tint_red
    novy "Red tint - warm and alert."

    show novy front at shader_demo_center, tint_blue
    novy "Blue tint - cold and calm."

    show novy front at shader_demo_center, tint_green
    novy "Green tint - nature or sickness."

    show novy front at shader_demo_center, tint_warm
    novy "Warm tint - cozy feeling."

    show novy front at shader_demo_center, tint_cool
    novy "Cool tint - fresh and clean."

    "Hue shifting..."

    show novy front at shader_demo_center, hue_shift_small
    novy "Small hue shift - subtle change."

    show novy front at shader_demo_center, hue_shift_opposite
    novy "Opposite hue - completely different!"

    show novy front at shader_demo_center
    "Color adjustment effects complete!"

    jump shader_menu


################################################################################
## Retro/Stylized Effects (shader_retro.rpy)
## Shaders: shader.retro_pixelate, shader.retro_scanlines,
##          shader.retro_vignette, shader.retro_chromatic, shader.retro_glitch
################################################################################

label shader_retro:

    "=== RETRO/STYLIZED (shader_retro.rpy) ==="

    show novy front at shader_demo_center
    novy "Normal appearance first."

    "Pixelation..."

    show novy front at shader_demo_center, pixelate_light
    novy "Light pixelate - subtle retro."

    show novy front at shader_demo_center, pixelate_medium
    novy "Medium pixelate - 8-bit style!"

    show novy front at shader_demo_center, pixelate_heavy
    novy "Heavy pixelate - very blocky!"

    show novy front at shader_demo_center, pixelate_extreme
    novy "Extreme pixelate - abstract!"

    "CRT scanlines..."

    show novy front at shader_demo_center, scanlines_subtle
    novy "Subtle scanlines - hint of CRT."

    show novy front at shader_demo_center, scanlines_crt
    novy "CRT scanlines - old TV feel."

    show novy front at shader_demo_center, scanlines_heavy
    novy "Heavy scanlines - very retro!"

    "Vignette..."

    show novy front at shader_demo_center, vignette_light
    novy "Light vignette - subtle frame."

    show novy front at shader_demo_center, vignette_medium
    novy "Medium vignette - cinematic!"

    show novy front at shader_demo_center, vignette_heavy
    novy "Heavy vignette - spotlight!"

    show novy front at shader_demo_center, vignette_dramatic
    novy "Dramatic vignette - intense!"

    "Chromatic aberration..."

    show novy front at shader_demo_center, chromatic_subtle
    novy "Subtle chromatic - slight RGB split."

    show novy front at shader_demo_center, chromatic_medium
    novy "Medium chromatic - noticeable."

    show novy front at shader_demo_center, chromatic_heavy
    novy "Heavy chromatic - trippy!"

    "Glitch effect (animated)..."

    show novy front at shader_demo_center, glitch_light
    novy "Light glitch - minor corruption."

    show novy front at shader_demo_center, glitch_medium
    novy "Medium glitch - unstable!"

    show novy front at shader_demo_center, glitch_heavy
    novy "Heavy glitch - SYSTEM ERROR!"

    show novy front at shader_demo_center
    "Retro effects complete!"

    jump shader_menu


################################################################################
## Special FX (shader_fx.rpy)
## Shaders: shader.light_rays, shader.threshold, shader.alpha_mask,
##          shader.outline, shader.transition_dissolve, shader.transition_wipe
################################################################################

label shader_fx:

    "=== SPECIAL FX (shader_fx.rpy) ==="

    show novy front at shader_demo_center
    novy "These are special effect shaders."

    "Outline effects..."

    show novy front at shader_demo_center, outline_black
    novy "Black outline - comic style!"

    show novy front at shader_demo_center, outline_white
    novy "White outline - glowing edge!"

    show novy front at shader_demo_center, outline_gold
    novy "Gold outline - premium feel!"

    "Light rays effect..."

    show novy front at shader_demo_center, light_rays
    novy "Light rays - volumetric lighting!"

    show novy front at shader_demo_center, light_rays_strong
    novy "Strong light rays - dramatic!"

    "Threshold/posterize effect..."

    show novy front at shader_demo_center, threshold_medium
    novy "Medium threshold - poster art."

    show novy front at shader_demo_center, threshold_high
    novy "High threshold - stark contrast."

    show novy front at shader_demo_center, threshold_inverted
    novy "Inverted threshold - negative poster!"

    show novy front at shader_demo_center
    "Special FX complete!"

    jump shader_menu


################################################################################
## Mood Presets (combined effects from shader_transforms.rpy)
################################################################################

label shader_mood:

    "=== MOOD PRESETS ==="
    "These combine shaders for common scenarios."

    show novy front at shader_demo_center
    novy "Normal mood first."

    show novy front at shader_demo_center, flashback
    novy "Flashback - remembering the past..."

    show novy front at shader_demo_center, flashback_full
    novy "Full flashback - deep memory..."

    show novy front at shader_demo_center, dream
    novy "Dream - floating in imagination..."

    show novy front at shader_demo_center, horror
    novy "Horror - something isn't right..."

    show novy front at shader_demo_center, hurt
    novy "Hurt - ouch, that stings!"

    show novy front at shader_demo_center, power_up
    novy "Power up - energy surging!"

    show novy front at shader_demo_center, frozen
    novy "Frozen - so... c-cold..."

    show novy front at shader_demo_center, poisoned
    novy "Poisoned - feeling sick..."

    show novy front at shader_demo_center, old_tv
    novy "Old TV - broadcast from the past."

    show novy front at shader_demo_center
    "Mood presets complete!"

    jump shader_menu


################################################################################
## Animation Demos
################################################################################

label shader_animated:

    "=== ANIMATION DEMOS ==="
    "Watch these animated effects for a few seconds each."

    show novy front at shader_demo_center
    novy "Let's see some animations!"

    show novy front at shader_demo_center, glow_pulse_gold
    "Pulsing gold glow..."
    $ renpy.pause(3.0)

    show novy front at shader_demo_center, power_up
    "Power up effect!"
    $ renpy.pause(3.0)

    show novy front at shader_demo_center, wave_dreamy
    "Dreamy wave..."
    $ renpy.pause(3.0)

    show novy front at shader_demo_center, ripple_calm
    "Calm ripple..."
    $ renpy.pause(3.0)

    show novy front at shader_demo_center, shake_heavy
    "Heavy shake!"
    $ renpy.pause(2.0)

    show novy front at shader_demo_center, glitch_medium
    "Glitch effect..."
    $ renpy.pause(3.0)

    show novy front at shader_demo_center, dream
    "Dream sequence..."
    $ renpy.pause(3.0)

    "Now testing animation transitions..."

    show novy front at shader_demo_center
    "Starting blur-in animation..."

    show novy front at shader_demo_center, blur_in(duration=1.0)
    $ renpy.pause(1.5)

    show novy front at shader_demo_center, blur_out(duration=1.0)
    "Blur-out..."
    $ renpy.pause(1.5)

    show novy front at shader_demo_center
    "Pixelate-in animation..."

    show novy front at shader_demo_center, pixelate_in(duration=1.0)
    $ renpy.pause(1.5)

    show novy front at shader_demo_center, pixelate_out(duration=1.0)
    "Pixelate-out..."
    $ renpy.pause(1.5)

    show novy front at shader_demo_center
    "Animation demos complete!"

    jump shader_menu


################################################################################
## Scene Preset Test
################################################################################
##
## Demo of all scene presets from presets/presets.json
## Presets control: shaders, character transitions, dialogbox styling,
## background effects, and scene transitions.
##
## Uses mood_enter_func() and mood_exit_func() to get preset-defined
## entrance/exit animations with sounds and shader effects.
##
################################################################################

label test_presets:

    scene bg_street with dissolve

    "Welcome to the Scene Preset Demo!"
    "Presets control the overall mood and choreography of scenes."
    "They combine shaders, transitions, sounds, and styling into cohesive themes."

    menu preset_menu:
        "Which preset category would you like to see?"

        "Mood Presets (dream, nightmare, flashback)":
            jump preset_mood

        "Action Presets (battle, horror, hurt)":
            jump preset_action

        "Effect Presets (underwater, divine, dramatic, quick)":
            jump preset_effects

        "Retro Presets (old_tv, glitch, pixelated)":
            jump preset_retro

        "View All Presets (quick tour)":
            jump preset_all

        "Return to Main Menu":
            $ mood.reset()
            scene black with fade
            jump start


################################################################################
## Mood Presets
################################################################################

label preset_mood:

    scene bg_street with dissolve

    "=== MOOD PRESETS ==="
    "These presets create distinct emotional atmospheres."
    "Watch for: sounds, movement, and shader effects on characters!"

    ## --- DEFAULT ---
    "First, the DEFAULT preset (normal state)..."
    $ mood.set("default")
    show novy front at mood_enter_func()
    novy "This is the default preset - clean and normal."
    novy "You should hear a footstep sound on entrance!"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.5)

    ## --- DREAM SEQUENCE ---
    "Now the DREAM_SEQUENCE preset..."
    $ mood.set("dream_sequence")
    scene bg_street with Dissolve(1.5)
    show novy front at mood_enter_func()
    novy "The dream sequence preset..."
    novy "Soft blur effect fades out as I appear."
    novy "Characters float up from below slowly."
    hide novy front at mood_exit_func()
    $ renpy.pause(1.0)

    ## --- NIGHTMARE ---
    "The NIGHTMARE preset..."
    $ mood.set("nightmare")
    scene bg_street with Dissolve(0.6)
    show novy front at mood_enter_func()
    novy "The nightmare preset..."
    novy "Glitchy shader during entrance!"
    novy "Something feels very wrong here..."
    hide novy front at mood_exit_func()
    $ renpy.pause(0.2)

    ## --- FLASHBACK ---
    "The FLASHBACK preset..."
    $ mood.set("flashback")
    scene bg_street with Fade(0.75, 0, 0.75, color="#FFFFFF")
    show novy front at mood_enter_func()
    novy "The flashback preset..."
    novy "Blur effect fades in, sepia tones."
    novy "Like a faded memory..."
    hide novy front at mood_exit_func()
    $ renpy.pause(0.6)

    $ mood.reset()
    scene bg_street with dissolve
    "Mood presets complete!"

    jump preset_menu


################################################################################
## Action Presets
################################################################################

label preset_action:

    scene bg_street with dissolve

    "=== ACTION PRESETS ==="
    "High-energy presets for intense scenes."

    ## --- BATTLE INTENSE ---
    "The BATTLE_INTENSE preset..."
    $ mood.set("battle_intense")
    scene bg_street with Dissolve(0.3)

    "Fast entrance with radial blur effect!"
    show novy front at mood_enter_func()
    novy "I enter fast with blur effects!"
    novy "High contrast, high energy!"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.3)

    ## --- HORROR TENSION ---
    "The HORROR_TENSION preset..."
    $ mood.set("horror_tension")
    scene bg_street with Fade(0.5, 0, 0.5, color="#000000")
    show novy front at mood_enter_func()
    novy "The horror tension preset..."
    novy "Slow emergence with vignette shader."
    novy "Characters creep up from below..."
    hide novy front at mood_exit_func()
    $ renpy.pause(0.5)

    ## --- HURT ---
    "The HURT preset..."
    $ mood.set("hurt")
    scene bg_street with dissolve
    show novy front at mood_enter_func()
    novy "The hurt preset - ouch!"
    novy "Shake shader during entrance!"
    novy "Used when taking damage or in pain."
    hide novy front at mood_exit_func()
    $ renpy.pause(0.4)

    $ mood.reset()
    scene bg_street with dissolve
    "Action presets complete!"

    jump preset_menu


################################################################################
## Effect Presets
################################################################################

label preset_effects:

    scene bg_street with dissolve

    "=== EFFECT PRESETS ==="
    "Environmental and status effect presets."

    ## --- UNDERWATER ---
    "The UNDERWATER preset..."
    $ mood.set("underwater")
    scene bg_street with Dissolve(1.2)
    show novy front at mood_enter_func()
    novy "The underwater preset..."
    novy "Blur effect during slow rise from below."
    novy "Characters float up slowly..."
    hide novy front at mood_exit_func()
    $ renpy.pause(1.5)

    ## --- DIVINE MOMENT ---
    "The DIVINE_MOMENT preset..."
    $ mood.set("divine_moment")
    scene bg_street with Fade(1.0, 0, 1.0, color="#FFFFFF")
    show novy front at mood_enter_func()
    novy "The divine moment preset..."
    novy "Golden glow shader during descent!"
    novy "Characters descend from above."
    hide novy front at mood_exit_func()
    $ renpy.pause(1.2)

    ## --- POISONED ---
    "The POISONED preset..."
    $ mood.set("poisoned")
    scene bg_street with dissolve
    show novy front at mood_enter_func()
    novy "The poisoned preset..."
    novy "Wave distortion during entrance."
    novy "Sickly feeling..."
    hide novy front at mood_exit_func()
    $ renpy.pause(0.6)

    ## --- DRAMATIC ENTRANCE ---
    "The DRAMATIC_ENTRANCE preset..."
    $ mood.set("dramatic_entrance")
    scene bg_street with dissolve
    show novy front at mood_enter_func()
    novy "The dramatic entrance preset!"
    novy "White glow shader during emergence!"
    novy "Perfect for important reveals."
    hide novy front at mood_exit_func()
    $ renpy.pause(0.6)

    ## --- QUICK ACTION ---
    "The QUICK_ACTION preset..."
    $ mood.set("quick_action")
    scene bg_street with dissolve
    show novy front at mood_enter_func()
    novy "Quick action preset - fast!"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.2)

    show novy front at mood_enter_func()
    novy "Rapid entrances and exits!"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.2)

    $ mood.reset()
    scene bg_street with dissolve
    "Effect presets complete!"

    jump preset_menu


################################################################################
## Retro Presets
################################################################################

label preset_retro:

    scene bg_street with dissolve

    "=== RETRO PRESETS ==="
    "Stylized presets for unique visual aesthetics."

    ## --- OLD TV ---
    "The OLD_TV preset..."
    $ mood.set("old_tv")
    scene bg_street with dissolve
    show novy front at mood_enter_func()
    novy "The old TV preset..."
    novy "CRT scanlines shader during entrance!"
    novy "Like watching an old broadcast!"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.2)

    ## --- GLITCH WORLD ---
    "The GLITCH_WORLD preset..."
    $ mood.set("glitch_world")
    scene bg_street with dissolve
    show novy front at mood_enter_func()
    novy "The glitch world preset..."
    novy "Heavy glitch shader during entrance!"
    novy "Reality is breaking down!"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.3)

    ## --- PIXELATED ---
    "The PIXELATED preset..."
    $ mood.set("pixelated")
    scene bg_street with dissolve
    show novy front at mood_enter_func()
    novy "The pixelated preset..."
    novy "Pixelate shader during entrance!"
    novy "Retro 8-bit style!"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.4)

    $ mood.reset()
    scene bg_street with dissolve
    "Retro presets complete!"

    jump preset_menu


################################################################################
## All Presets Quick Tour
################################################################################

label preset_all:

    scene bg_street with dissolve

    "=== QUICK TOUR OF ALL PRESETS ==="
    "Watch each preset in action with sounds and shaders!"

    ## DEFAULT
    $ mood.set("default")
    show novy front at mood_enter_func()
    "DEFAULT - Standard, clean look"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.5)

    ## DREAM SEQUENCE
    $ mood.set("dream_sequence")
    scene bg_street with Dissolve(1.0)
    show novy front at mood_enter_func()
    "DREAM_SEQUENCE - Ethereal, blur shader"
    hide novy front at mood_exit_func()
    $ renpy.pause(1.0)

    ## NIGHTMARE
    $ mood.set("nightmare")
    scene bg_street with Dissolve(0.5)
    show novy front at mood_enter_func()
    "NIGHTMARE - Dark, glitch shader"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.2)

    ## FLASHBACK
    $ mood.set("flashback")
    scene bg_street with Fade(0.5, 0, 0.5, color="#FFFFFF")
    show novy front at mood_enter_func()
    "FLASHBACK - Sepia, blur shader"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.6)

    ## BATTLE INTENSE
    $ mood.set("battle_intense")
    scene bg_street with Dissolve(0.3)
    show novy front at mood_enter_func()
    "BATTLE_INTENSE - Fast, radial blur"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.3)

    ## HORROR TENSION
    $ mood.set("horror_tension")
    scene bg_street with Fade(0.4, 0, 0.4, color="#000000")
    show novy front at mood_enter_func()
    "HORROR_TENSION - Slow, vignette shader"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.5)

    ## UNDERWATER
    $ mood.set("underwater")
    scene bg_street with Dissolve(0.8)
    show novy front at mood_enter_func()
    "UNDERWATER - Slow rise, blur shader"
    hide novy front at mood_exit_func()
    $ renpy.pause(1.5)

    ## DIVINE MOMENT
    $ mood.set("divine_moment")
    scene bg_street with Fade(0.8, 0, 0.8, color="#FFFFFF")
    show novy front at mood_enter_func()
    "DIVINE_MOMENT - Descent, gold glow"
    hide novy front at mood_exit_func()
    $ renpy.pause(1.2)

    ## DRAMATIC ENTRANCE
    $ mood.set("dramatic_entrance")
    scene bg_street with dissolve
    show novy front at mood_enter_func()
    "DRAMATIC_ENTRANCE - White glow shader"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.6)

    ## QUICK ACTION
    $ mood.set("quick_action")
    show novy front at mood_enter_func()
    "QUICK_ACTION - Fast pace"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.2)

    ## OLD TV
    $ mood.set("old_tv")
    show novy front at mood_enter_func()
    "OLD_TV - CRT scanlines shader"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.2)

    ## GLITCH WORLD
    $ mood.set("glitch_world")
    show novy front at mood_enter_func()
    "GLITCH_WORLD - Glitch shader"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.3)

    ## PIXELATED
    $ mood.set("pixelated")
    show novy front at mood_enter_func()
    "PIXELATED - Pixelate shader"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.4)

    ## POISONED
    $ mood.set("poisoned")
    show novy front at mood_enter_func()
    "POISONED - Wave shader"
    hide novy front at mood_exit_func()
    $ renpy.pause(1.0)

    ## HURT
    $ mood.set("hurt")
    show novy front at mood_enter_func()
    "HURT - Shake shader"
    hide novy front at mood_exit_func()
    $ renpy.pause(0.4)

    ## RESET
    $ mood.reset()
    scene bg_street with dissolve

    "All 14 presets demonstrated!"
    "Each combines movement, sounds, and shader effects."

    jump preset_menu
