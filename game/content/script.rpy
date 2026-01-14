## script.rpy - Shader & Preset Demo
##
## REVISION: 2026-01-13 @ 16:15
## - Using preset system properly (no manual transform creation)
## - Transitions now accept shader parameter directly
## - Edge transitions with 1200px offset for true off-screen entrances
##
## Related files: characters.rpy, shader_transforms.rpy, presets/presets.json

################################################################################
## Helper transform for plain center positioning
################################################################################

transform center_screen:
    xalign 0.5
    yalign 0.5

################################################################################
## Pure ATL entrance transforms (no function transforms, no preset system)
## These are simple, reliable, and bypass all the complex systems
################################################################################

# Slide in from left with fade
transform atl_slide_left:
    xalign 0.5
    yalign 0.5
    xoffset -300
    alpha 0.0
    easein 0.5 xoffset 0 alpha 1.0

# Slide in from right with fade
transform atl_slide_right:
    xalign 0.5
    yalign 0.5
    xoffset 300
    alpha 0.0
    easein 0.5 xoffset 0 alpha 1.0

# Rise up from bottom with fade
transform atl_rise_up:
    xalign 0.5
    yalign 0.5
    yoffset 200
    alpha 0.0
    easein 0.5 yoffset 0 alpha 1.0

# Pop in with scale
transform atl_pop_in:
    xalign 0.5
    yalign 0.5
    alpha 0.0
    zoom 0.8
    easein 0.3 alpha 1.0 zoom 1.0

# Edge entrance from off-screen left
transform atl_edge_left:
    xalign 0.5
    yalign 0.5
    xoffset -1200
    alpha 0.0
    easein 0.6 xoffset 0 alpha 1.0

# Edge entrance from off-screen right
transform atl_edge_right:
    xalign 0.5
    yalign 0.5
    xoffset 1200
    alpha 0.0
    easein 0.6 xoffset 0 alpha 1.0


################################################################################
## Main Menu
################################################################################

label start:

    scene black with dissolve

    "Welcome to the Shader & Preset Demo!"
    "Testing the PRESET SYSTEM - shaders configured via JSON, not hardcoded."

    jump demo_menu


################################################################################
## TEST: Layered Presets (New JSON-based system)
################################################################################

label test_layered_presets:

    scene bg_street with dissolve

    "=== LAYERED PRESET TEST ==="
    "Testing the new simplified preset system."
    "Presets loaded from transition_presets.json"

    "TEST 1: preset_slide_left_enter (basic slide)"
    show novy front at preset_slide_left_enter()
    novy "Sliding in from left using preset_slide_left_enter()"
    hide novy with dissolve

    "TEST 2: preset_slide_right_enter"
    show novy front at preset_slide_right_enter()
    novy "Sliding in from right using preset_slide_right_enter()"
    hide novy with dissolve

    "TEST 3: preset_edge_left_enter (far off-screen)"
    show novy front at preset_edge_left_enter()
    novy "Coming from way off-screen left!"
    hide novy with dissolve

    "TEST 4: preset_pop_in_enter (scale animation)"
    show novy front at preset_pop_in_enter()
    novy "Popping in with scale animation!"
    hide novy with dissolve

    "TEST 5: preset_rise_up_enter"
    show novy front at preset_rise_up_enter()
    novy "Rising up from below!"
    hide novy with dissolve

    "TEST 6: preset with position override"
    show novy front at preset_slide_left_enter(xalign=0.3)
    novy "Using xalign=0.3 to position me on the left side!"
    hide novy with dissolve

    "Now testing with SHADER CHAINING..."

    "TEST 7: preset_slide_left_enter + glow_blue"
    show novy front at preset_slide_left_enter(), glow_blue
    novy "Preset entrance with blue glow chained!"
    hide novy with dissolve

    "TEST 8: preset_pop_in_enter + sepia"
    show novy front at preset_pop_in_enter(), sepia
    novy "Pop in with sepia shader!"
    hide novy with dissolve

    "TEST 9: preset_edge_left_enter + grayscale"
    show novy front at preset_edge_left_enter(), grayscale
    novy "Edge entrance with grayscale!"
    hide novy with dissolve

    "TEST 10: Exit preset"
    show novy front at preset_slide_left_enter()
    novy "Now I'll exit..."
    show novy front at preset_slide_left_exit()
    pause 0.5
    hide novy

    "Layered preset test complete!"
    "If tests 1-6 worked, the basic preset system is functional."
    "If tests 7-9 worked, shader chaining with presets works!"

    jump demo_menu


################################################################################
## TEST B: Slide In + Wavy Shader
################################################################################

label test_slide_wavy:

    scene bg_street with dissolve

    "=== SLIDE IN + WAVY SHADER TEST ==="
    "Novy will slide in from the left with a wavy distortion effect."

    show novy front at preset_slide_left_enter(), wave_gentle

    novy "I'm sliding in with a gentle wave effect!"

    hide novy with dissolve

    "Now with a stronger wave..."

    show novy front at preset_slide_right_enter(), wave_strong

    novy "This is the strong wave - more distortion!"

    hide novy with dissolve

    "And finally the dreamy wave..."

    show novy front at preset_slide_left_enter(), wave_dreamy

    novy "The dreamy wave has a slower, more ethereal feel."

    hide novy with dissolve

    "Wavy shader test complete!"

    jump demo_menu


label demo_menu:

    scene bg_street with dissolve

    menu:
        "SHADER DEMO - Select a test:"

        "NEW: Layered Presets (JSON-based system)":
            jump test_layered_presets

        "A. PURE ATL: Transitions + Manual Shaders (bypasses preset system)":
            jump test_pure_atl

        "B. Slide In + Wavy Shader":
            jump test_slide_wavy

        "0. DIAGNOSTIC: ATL Transforms (test shaders work)":
            jump test_atl_shaders

        "1. Direct Shaders (via transition shader param)":
            jump test_direct_shaders

        "2. Shaders on Background":
            jump test_bg_shaders

        "3. Dual Shaders (Character + Background)":
            jump test_dual_shaders

        "4. Edge Transitions with Shaders":
            jump test_edge_transitions

        "5. Mood Presets (Full System)":
            jump test_mood_presets

        "Quit":
            return


################################################################################
## A. PURE ATL: Bypasses preset system entirely
## Uses simple ATL transforms for movement + chains shader transforms manually
################################################################################

label test_pure_atl:

    scene bg_street with dissolve

    "=== PURE ATL TEST ==="
    "This bypasses the preset system completely."
    "Uses ATL transforms for movement, then chains shader transforms on top."

    "TEST A1: ATL slide from left (no shader)"
    show novy front at atl_slide_left
    novy "Sliding in from left! (Pure ATL, no shader)"
    hide novy with dissolve

    "TEST A2: ATL slide from right (no shader)"
    show novy front at atl_slide_right
    novy "Sliding in from right! (Pure ATL, no shader)"
    hide novy with dissolve

    "TEST A3: ATL pop in (no shader)"
    show novy front at atl_pop_in
    novy "Popping in with scale! (Pure ATL, no shader)"
    hide novy with dissolve

    "TEST A4: ATL edge entrance from off-screen (no shader)"
    show novy front at atl_edge_left
    novy "Coming from way off screen! (Pure ATL, no shader)"
    hide novy with dissolve

    "Now testing ATL transitions WITH shaders chained..."

    "TEST A5: ATL slide left + sepia shader"
    show novy front at atl_slide_left, sepia
    novy "Sliding in with SEPIA! (ATL + shader chain)"
    hide novy with dissolve

    "TEST A6: ATL pop in + grayscale shader"
    show novy front at atl_pop_in, grayscale
    novy "Popping in with GRAYSCALE! (ATL + shader chain)"
    hide novy with dissolve

    "TEST A7a: ATL edge left + tint_blue shader (KNOWN WORKING)"
    show novy front at atl_edge_left, tint_blue
    novy "Edge entrance with BLUE TINT! (Using shader.color_tint - should work)"
    hide novy with dissolve

    "TEST A7b: ATL edge left + glow_blue (mesh_pad removed)"
    show novy front at atl_edge_left, glow_blue
    novy "Edge entrance with BLUE GLOW! (mesh_pad removed from transform)"
    hide novy with dissolve

    "TEST A8: ATL slide right + horror shader"
    show novy front at atl_slide_right, horror
    novy "Sliding in with HORROR effect! (ATL + shader chain)"
    hide novy with dissolve

    "TEST A9: ATL rise up + vignette_heavy shader"
    show novy front at atl_rise_up, vignette_heavy
    novy "Rising up with VIGNETTE! (ATL + shader chain)"
    hide novy with dissolve

    "Pure ATL test complete!"
    "If A1-A4 work but A5+ don't, the issue is shader chaining."
    "If A5-A6 work, A7a works, but A7b doesn't - shader.glow is broken."
    "If A7a doesn't work - something wrong with blue tint shader."
    jump demo_menu


################################################################################
## 0. DIAGNOSTIC: ATL Transforms
## Tests that shaders work at all using hardcoded ATL transforms
################################################################################

label test_atl_shaders:

    scene bg_street with dissolve

    "=== DIAGNOSTIC: ATL SHADER TEST ==="
    "This tests shaders using ATL transforms (hardcoded, not presets)."
    "If these work but preset shaders don't, the issue is in the preset system."

    "TEST 1: Show character without any transform"
    show novy front at center_screen
    novy "Can you see me? (No shader)"
    hide novy with dissolve

    "TEST 2: Show character with ATL glow_blue transform"
    show novy front at center_screen, glow_blue
    novy "Can you see me with BLUE GLOW? (ATL transform)"
    hide novy with dissolve

    "TEST 3: Show character with ATL sepia transform"
    show novy front at center_screen, sepia
    novy "Can you see me with SEPIA? (ATL transform)"
    hide novy with dissolve

    "TEST 4: Show character with ATL grayscale transform"
    show novy front at center_screen, grayscale
    novy "Can you see me in GRAYSCALE? (ATL transform)"
    hide novy with dissolve

    "TEST 5: Show character using simple_test_transform (basic function)"
    show novy front at simple_test_transform
    novy "Can you see me? (Simple function transform)"
    hide novy with dissolve

    "TEST 6: Show character using pop_in_enter (no shader)"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5)
    novy "Can you see me? (pop_in_enter, no shader)"
    hide novy with dissolve

    "TEST 7: Show character using pop_in_enter WITH shader param"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="glow_blue", shader_fade=0)
    novy "Can you see me with BLUE GLOW? (pop_in_enter with shader)"
    hide novy with dissolve

    "Diagnostic complete. Check log.txt for these messages:"
    "- 'CharacterAnimationFactory: Found X transitions'"
    "- 'CharacterAnimationFactory: Registered entrance pop_in_enter'"
    "- 'PresetManager: Loaded X shader presets'"
    jump demo_menu


################################################################################
## 1. Direct Shaders on Character
## Using transition's shader parameter - no transform chaining needed
################################################################################

label test_direct_shaders:

    scene bg_street with dissolve

    "=== TEST 1: DIRECT SHADERS ON CHARACTER ==="
    "Using pop_in_enter with shader parameter."
    "Shaders come from shader_presets.json"

    ## GLOW TESTS
    "--- GLOW EFFECTS ---"

    "BLUE GLOW (glow_blue preset)"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="glow_blue", shader_fade=0)
    novy "I have a BLUE glow! Shader loads from JSON preset."
    hide novy with dissolve

    "RED GLOW (glow_red preset)"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="glow_red", shader_fade=0)
    novy "I have a RED glow!"
    hide novy with dissolve

    "GOLD GLOW (glow_gold preset)"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="glow_gold", shader_fade=0)
    novy "I have a GOLD glow!"
    hide novy with dissolve

    "PULSING GLOW (glow_pulse_white preset - animated)"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="glow_pulse_white", shader_fade=0)
    novy "Pulsing glow! Animated shader from JSON."
    novy "Click to continue."
    hide novy with dissolve

    ## COLOR TESTS
    "--- COLOR EFFECTS ---"

    "SEPIA (sepia preset)"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="sepia", shader_fade=0)
    novy "Sepia tint - old photo look."
    hide novy with dissolve

    "GRAYSCALE (grayscale preset)"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="grayscale", shader_fade=0)
    novy "Grayscale - no color."
    hide novy with dissolve

    "HORROR (horror preset)"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="horror", shader_fade=0)
    novy "Horror look - dark and creepy."
    hide novy with dissolve

    ## DISTORTION TESTS
    "--- DISTORTION EFFECTS ---"

    "WAVE (wave_gentle preset - animated)"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="wave_gentle", shader_fade=0)
    novy "Wave distortion - dreamlike wobble!"
    novy "Click to continue."
    hide novy with dissolve

    "GLITCH (glitch_medium preset - animated)"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="glitch_medium", shader_fade=0)
    novy "Glitch effect - reality breaking!"
    hide novy with dissolve

    ## RETRO TESTS
    "--- RETRO EFFECTS ---"

    "PIXELATE (pixelate_medium preset)"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="pixelate_medium", shader_fade=0)
    novy "Pixelated - 8-bit retro style!"
    hide novy with dissolve

    "SCANLINES (scanlines_crt preset)"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="scanlines_crt", shader_fade=0)
    novy "CRT scanlines - old TV look!"
    hide novy with dissolve

    "VIGNETTE (vignette_heavy preset)"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="vignette_heavy", shader_fade=0)
    novy "Heavy vignette - dark edges!"
    hide novy with dissolve

    "Direct shader test complete!"
    jump demo_menu


################################################################################
## 2. Shaders on Background
## Using ATL transforms from shader_transforms.rpy
################################################################################

label test_bg_shaders:

    "=== TEST 2: SHADERS ON BACKGROUND ==="
    "Using ATL transforms from shader_transforms.rpy"

    "NORMAL (no shader)"
    scene bg_street with dissolve
    "Normal background - no shader applied."

    "SEPIA"
    scene bg_street at sepia with dissolve
    "Sepia shader on background."

    "BLUR"
    scene bg_street at blur_medium with dissolve
    "Blur shader on background."

    "HORROR"
    scene bg_street at horror with dissolve
    "Horror shader - dark and desaturated."

    "WAVE (animated)"
    scene bg_street at wave_gentle with dissolve
    "Wave distortion on background. Watch it move!"
    $ renpy.pause(2.0)

    "VIGNETTE"
    scene bg_street at vignette_heavy with dissolve
    "Vignette shader - dark edges."

    "SCANLINES"
    scene bg_street at scanlines_crt with dissolve
    "CRT scanlines on background."

    "PIXELATE"
    scene bg_street at pixelate_heavy with dissolve
    "Pixelate shader on background."

    "GLITCH (animated)"
    scene bg_street at glitch_medium with dissolve
    "Glitch shader on background!"
    $ renpy.pause(2.0)

    "Background shader test complete!"
    scene bg_street with dissolve
    jump demo_menu


################################################################################
## 3. Dual Shaders - Character AND Background
################################################################################

label test_dual_shaders:

    "=== TEST 3: DUAL SHADERS ==="
    "Both character AND background have shaders simultaneously!"

    "FLASHBACK: Sepia BG + Sepia Character"
    scene bg_street at sepia with dissolve
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="sepia", shader_fade=0)
    novy "Both background and I have sepia tint!"
    novy "Cohesive flashback look."
    hide novy with dissolve

    "HORROR: Dark BG + Red Glowing Character"
    scene bg_street at horror with dissolve
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="glow_red", shader_fade=0)
    novy "Dark background, red glow on me..."
    novy "Very ominous!"
    hide novy with dissolve

    "DREAM: Wavy BG + Blurred Character"
    scene bg_street at wave_gentle with dissolve
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="blur_medium", shader_fade=0)
    novy "Wavy background, blurry me..."
    novy "Dream sequence effect!"
    hide novy with dissolve

    "DIVINE: Normal BG + Gold Glowing Character"
    scene bg_street with dissolve
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="glow_gold", shader_fade=0)
    novy "Normal background but I'm glowing gold!"
    novy "Divine presence!"
    hide novy with dissolve

    "RETRO TV: Scanlines BG + Pixelated Character"
    scene bg_street at scanlines_crt with dissolve
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="pixelate_medium", shader_fade=0)
    novy "Scanlines on BG, pixelated character!"
    novy "Old TV broadcast!"
    hide novy with dissolve

    "NIGHTMARE: Glitch BG + Glitch Character"
    scene bg_street at glitch_light with dissolve
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="glitch_heavy", shader_fade=0)
    novy "Everything is glitching!"
    novy "Reality breaking down!"
    hide novy with dissolve

    "Dual shader test complete!"
    scene bg_street with dissolve
    jump demo_menu


################################################################################
## 4. Edge Transitions with Shaders
## Characters come from OFF-SCREEN (1200px offset) with shader integrated
################################################################################

label test_edge_transitions:

    scene bg_street with dissolve

    "=== TEST 4: EDGE TRANSITIONS WITH SHADERS ==="
    "Character enters from OFF-SCREEN edge (1200px offset)."
    "Shader is built into the transition - not chained."

    "EDGE LEFT + BLUE GLOW (fades out over 0.8s)"
    show novy front at edge_left_enter(xalign=0.5, yalign=0.5, shader="glow_blue", shader_fade=0.8)
    novy "Came from left edge with blue glow that faded out!"
    hide novy with dissolve

    "EDGE RIGHT + RED GLOW (persistent, no fade)"
    show novy front at edge_right_enter(xalign=0.5, yalign=0.5, shader="glow_red", shader_fade=0)
    novy "Came from right edge with persistent red glow!"
    hide novy with dissolve

    "EDGE BOTTOM + WAVE (animated, persistent)"
    show novy front at edge_bottom_enter(xalign=0.5, yalign=0.5, shader="wave_gentle", shader_fade=0)
    novy "Rose up from bottom with wave effect!"
    novy "Wave keeps animating..."
    hide novy with dissolve

    "EDGE TOP + GOLD GLOW (fades out)"
    show novy front at edge_top_enter(xalign=0.5, yalign=0.5, shader="glow_gold", shader_fade=0.6)
    novy "Dropped from top with gold glow that fades!"
    hide novy with dissolve

    "DRAMATIC EMERGE + PULSING GLOW (animated)"
    show novy front at dramatic_emerge_enter(xalign=0.5, yalign=0.5, shader="glow_pulse_white", shader_fade=0)
    novy "Dramatic entrance with pulsing glow!"
    novy "Pulse keeps going..."
    hide novy with dissolve

    "POP IN + GLITCH (fades out quickly)"
    show novy front at pop_in_enter(xalign=0.5, yalign=0.5, shader="glitch_heavy", shader_fade=0.25)
    novy "Quick pop with glitch that fades!"
    hide novy with dissolve

    "Edge transitions test complete!"
    jump demo_menu


################################################################################
## 5. Mood Presets (Full System)
## Uses mood.set() + mood_enter_func() - the complete preset pipeline
################################################################################

label test_mood_presets:

    "=== TEST 5: MOOD PRESETS ==="
    "Full preset system: mood.set() + mood_enter_func()"
    "Transitions AND shaders both come from presets.json"

    ## DREAM SEQUENCE
    "DREAM_SEQUENCE preset"
    $ mood.set("dream_sequence")
    scene bg_street at blur_light with Dissolve(1.5)
    show novy front at mood_enter_func("default", xalign=0.5, yalign=0.5)
    novy "Dream sequence mood active!"
    novy "Rise up entrance + blur shader (from preset)."
    hide novy front at mood_exit_func("default")
    $ renpy.pause(0.5)

    ## NIGHTMARE
    "NIGHTMARE preset"
    $ mood.set("nightmare")
    scene bg_street at horror with Dissolve(0.6)
    show novy front at mood_enter_func("default", xalign=0.5, yalign=0.5)
    novy "Nightmare mood active!"
    novy "Dramatic emerge + glitch shader."
    hide novy front at mood_exit_func("default")
    $ renpy.pause(0.3)

    ## FLASHBACK
    "FLASHBACK preset"
    $ mood.set("flashback")
    scene bg_street at sepia with Dissolve(1.5)
    show novy front at mood_enter_func("default", xalign=0.5, yalign=0.5)
    novy "Flashback mood active!"
    novy "Pop in + blur shader."
    hide novy front at mood_exit_func("default")
    $ renpy.pause(0.3)

    ## DIVINE MOMENT
    "DIVINE_MOMENT preset"
    $ mood.set("divine_moment")
    scene bg_street with Dissolve(2.0)
    show novy front at mood_enter_func("default", xalign=0.5, yalign=0.5)
    novy "Divine moment mood active!"
    novy "Drop down + gold glow shader."
    hide novy front at mood_exit_func("default")
    $ renpy.pause(0.5)

    ## BATTLE - HERO
    "BATTLE_INTENSE preset - HERO config"
    $ mood.set("battle_intense")
    scene bg_street with Dissolve(0.3)
    show novy front at mood_enter_func("hero", xalign=0.5, yalign=0.5)
    novy "Hero config - blue glow!"
    hide novy front at mood_exit_func("hero")
    $ renpy.pause(0.3)

    ## BATTLE - VILLAIN
    "BATTLE_INTENSE preset - VILLAIN config"
    show novy front at mood_enter_func("villain", xalign=0.5, yalign=0.5)
    novy "Villain config - red glow!"
    hide novy front at mood_exit_func("villain")
    $ renpy.pause(0.3)

    ## OLD TV
    "OLD_TV preset"
    $ mood.set("old_tv")
    scene bg_street at scanlines_crt with Dissolve(0.3)
    show novy front at mood_enter_func("default", xalign=0.5, yalign=0.5)
    novy "Old TV mood - retro CRT effect!"
    hide novy front at mood_exit_func("default")
    $ renpy.pause(0.3)

    ## GLITCH WORLD
    "GLITCH_WORLD preset"
    $ mood.set("glitch_world")
    scene bg_street at glitch_light with Dissolve(0.3)
    show novy front at mood_enter_func("default", xalign=0.5, yalign=0.5)
    novy "Glitch world - digital corruption!"
    hide novy front at mood_exit_func("default")
    $ renpy.pause(0.3)

    $ mood.reset()
    "Mood preset test complete!"
    scene bg_street with dissolve
    jump demo_menu
