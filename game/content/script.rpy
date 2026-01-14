## script.rpy - Integrated Preset System Demo
##
## Demonstrates the JSON-based preset system:
## - Transition presets from transition_presets.json (movement, position, alpha, scale, rotation)
## - Shader presets from shader_presets.json (visual effects)
## - Chaining: preset_slide_left_enter(), shader_wave_gentle
##
## Related files:
##   - presets/transition_presets.json
##   - presets/shader_presets.json
##   - presets/preset_generator.rpy
##   - presets/shader_generator.rpy

################################################################################
## GAME START
################################################################################

label start:
    scene bg_street with dissolve

    "Welcome to the Integrated Preset System Demo!"
    "This demo showcases the JSON-based preset system."

    jump demo_menu


################################################################################
## DEMO MENU
################################################################################

label demo_menu:
    scene bg_street with dissolve

    menu:
        "SELECT A DEMO:"

        "1. Transition Presets (movement/position)":
            jump demo_transitions

        "2. Shader Presets (visual effects)":
            jump demo_shaders

        "3. Combined: Transitions + Shaders":
            jump demo_combined

        "4. Position Override Demo":
            jump demo_positions

        "Exit Demo":
            "Thanks for testing!"
            return


################################################################################
## DEMO 1: TRANSITION PRESETS
################################################################################

label demo_transitions:
    scene bg_street with dissolve

    "=== TRANSITION PRESETS ==="
    "These are loaded from transition_presets.json"

    "Slide in from left..."
    show novy front at preset_slide_left_enter()
    novy "preset_slide_left_enter()"
    hide novy with dissolve

    "Slide in from right..."
    show novy front at preset_slide_right_enter()
    novy "preset_slide_right_enter()"
    hide novy with dissolve

    "Edge enter (from off-screen left)..."
    show novy front at preset_edge_left_enter()
    novy "preset_edge_left_enter() - uses xalign animation"
    hide novy with dissolve

    "Rise up from bottom..."
    show novy front at preset_rise_up_enter()
    novy "preset_rise_up_enter()"
    hide novy with dissolve

    "Pop in with scale..."
    show novy front at preset_pop_in_enter()
    novy "preset_pop_in_enter()"
    hide novy with dissolve

    "Spin enter..."
    show novy front at preset_spin_enter()
    novy "preset_spin_enter() - rotation + scale"
    hide novy with dissolve

    "Transition presets demo complete!"
    jump demo_menu


################################################################################
## DEMO 2: SHADER PRESETS
################################################################################

label demo_shaders:
    scene bg_street with dissolve

    "=== SHADER PRESETS ==="
    "These are loaded from shader_presets.json"

    show novy front at center
    novy "Normal appearance (no shader)"

    "Glow effects..."
    show novy front at center, shader_glow_blue
    novy "shader_glow_blue"

    show novy front at center, shader_glow_gold
    novy "shader_glow_gold"

    show novy front at center, shader_glow_purple
    novy "shader_glow_purple"

    "Color adjustments..."
    show novy front at center, shader_sepia
    novy "shader_sepia"

    show novy front at center, shader_grayscale
    novy "shader_grayscale"

    show novy front at center, shader_invert
    novy "shader_invert"

    "Animated effects..."
    show novy front at center, shader_wave_gentle
    novy "shader_wave_gentle (animated)"
    pause 2.0

    show novy front at center, shader_glitch_light
    novy "shader_glitch_light (animated)"
    pause 2.0

    hide novy with dissolve

    "Shader presets demo complete!"
    jump demo_menu


################################################################################
## DEMO 3: COMBINED TRANSITIONS + SHADERS
################################################################################

label demo_combined:
    scene bg_street with dissolve

    "=== COMBINED: TRANSITIONS + SHADERS ==="
    "Chain presets with comma: preset_xxx(), shader_xxx"

    "Slide left + glow blue..."
    show novy front at preset_slide_left_enter(), shader_glow_blue
    novy "preset_slide_left_enter(), shader_glow_blue"
    hide novy with dissolve

    "Slide right + wave..."
    show novy front at preset_slide_right_enter(), shader_wave_gentle
    novy "preset_slide_right_enter(), shader_wave_gentle"
    pause 1.5
    hide novy with dissolve

    "Pop in + sepia..."
    show novy front at preset_pop_in_enter(), shader_sepia
    novy "preset_pop_in_enter(), shader_sepia"
    hide novy with dissolve

    "Edge enter + glow gold..."
    show novy front at preset_edge_left_enter(), shader_glow_gold
    novy "preset_edge_left_enter(), shader_glow_gold"
    hide novy with dissolve

    "Rise up + grayscale..."
    show novy front at preset_rise_up_enter(), shader_grayscale
    novy "preset_rise_up_enter(), shader_grayscale"
    hide novy with dissolve

    "Spin enter + glitch..."
    show novy front at preset_spin_enter(), shader_glitch_light
    novy "preset_spin_enter(), shader_glitch_light"
    pause 2.0
    hide novy with dissolve

    "Combined demo complete!"
    jump demo_menu


################################################################################
## DEMO 4: POSITION OVERRIDES
################################################################################

label demo_positions:
    scene bg_street with dissolve

    "=== POSITION OVERRIDES ==="
    "Override final position with xalign parameter"

    "Slide left to LEFT position (xalign=0.25)..."
    show novy front at preset_slide_left_enter(xalign=0.25)
    novy "preset_slide_left_enter(xalign=0.25)"
    hide novy with dissolve

    "Slide right to RIGHT position (xalign=0.75)..."
    show novy front at preset_slide_right_enter(xalign=0.75)
    novy "preset_slide_right_enter(xalign=0.75)"
    hide novy with dissolve

    "Pop in at CENTER (xalign=0.5)..."
    show novy front at preset_pop_in_enter(xalign=0.5)
    novy "preset_pop_in_enter(xalign=0.5)"
    hide novy with dissolve

    "Multiple characters with different positions..."
    show novy front at preset_slide_left_enter(xalign=0.25), shader_glow_blue
    show novy front at preset_slide_right_enter(xalign=0.75), shader_glow_gold as novy2
    novy "Two characters, different positions and shaders!"
    hide novy
    hide novy2
    with dissolve

    "Position overrides demo complete!"
    jump demo_menu
