## shader_transforms.rpy - Pre-configured shader transforms
##
## Ready-to-use transforms that apply shader effects.
## Use these directly or as examples for custom configurations.
##
## Usage:
##     show eileen at glow_gold
##     show bg at blur_heavy
##     show portrait at grayscale
##
## Related files: shader_library.rpy

################################################################################
## Glow Transforms
## mesh_pad allows glow to extend beyond image bounds
################################################################################

# Basic glow colors
transform glow_white:
    mesh_pad 50
    shader "shader.glow"
    u_outer_strength 0.6
    u_inner_strength 0.0
    u_glow_color (1.0, 1.0, 1.0, 1.0)
    u_scale 1.0

transform glow_gold:
    mesh_pad 50
    shader "shader.glow"
    u_outer_strength 0.8
    u_inner_strength 0.2
    u_glow_color (1.0, 0.85, 0.3, 1.0)
    u_scale 1.0

transform glow_red:
    mesh_pad 50
    shader "shader.glow"
    u_outer_strength 0.7
    u_inner_strength 0.1
    u_glow_color (1.0, 0.2, 0.2, 1.0)
    u_scale 1.0

transform glow_blue:
    mesh_pad 50
    shader "shader.glow"
    u_outer_strength 0.7
    u_inner_strength 0.1
    u_glow_color (0.3, 0.5, 1.0, 1.0)
    u_scale 1.0

transform glow_green:
    mesh_pad 50
    shader "shader.glow"
    u_outer_strength 0.7
    u_inner_strength 0.1
    u_glow_color (0.2, 1.0, 0.4, 1.0)
    u_scale 1.0

transform glow_purple:
    mesh_pad 50
    shader "shader.glow"
    u_outer_strength 0.7
    u_inner_strength 0.1
    u_glow_color (0.7, 0.3, 1.0, 1.0)
    u_scale 1.0

transform glow_pink:
    mesh_pad 50
    shader "shader.glow"
    u_outer_strength 0.7
    u_inner_strength 0.1
    u_glow_color (1.0, 0.4, 0.7, 1.0)
    u_scale 1.0

# Pulsing glow (animated) - pause 0 + repeat forces continuous redraw
transform glow_pulse_white:
    mesh_pad 60
    shader "shader.glow_pulse"
    u_strength 0.8
    u_speed 2.0
    u_glow_color (1.0, 1.0, 1.0, 1.0)
    pause 0
    repeat

transform glow_pulse_gold:
    mesh_pad 60
    shader "shader.glow_pulse"
    u_strength 1.0
    u_speed 1.5
    u_glow_color (1.0, 0.85, 0.3, 1.0)
    pause 0
    repeat

transform glow_pulse_red:
    mesh_pad 60
    shader "shader.glow_pulse"
    u_strength 1.0
    u_speed 3.0
    u_glow_color (1.0, 0.2, 0.2, 1.0)
    pause 0
    repeat

# Parameterized glow (use with At)
transform glow_custom(color=(1.0, 1.0, 1.0, 1.0), outer=0.6, inner=0.0, scale=1.0, pad=50):
    mesh_pad pad
    shader "shader.glow"
    u_outer_strength outer
    u_inner_strength inner
    u_glow_color color
    u_scale scale


################################################################################
## Blur Transforms
## mesh_pad allows blur to bleed beyond image bounds
################################################################################

# Preset blur levels
transform blur_light:
    mesh_pad 10
    shader "shader.blur_box"
    u_radius 1.0

transform blur_medium:
    mesh_pad 20
    shader "shader.blur_box"
    u_radius 2.0

transform blur_heavy:
    mesh_pad 40
    shader "shader.blur_box"
    u_radius 4.0

# Radial blur (motion from center)
transform blur_radial_light:
    mesh_pad 20
    shader "shader.blur_radial"
    u_strength 0.02
    u_center (0.5, 0.5)

transform blur_radial_heavy:
    mesh_pad 50
    shader "shader.blur_radial"
    u_strength 0.08
    u_center (0.5, 0.5)

# Parameterized blur
transform blur_custom(radius=2.0, pad=20):
    mesh_pad pad
    shader "shader.blur_box"
    u_radius radius


################################################################################
## Distortion Transforms
## mesh_pad allows distorted pixels to extend beyond image bounds
################################################################################

# Barrel/Fisheye
transform fisheye_light:
    mesh_pad 20
    shader "shader.distort_barrel"
    u_amount 1.2

transform fisheye_heavy:
    mesh_pad 40
    shader "shader.distort_barrel"
    u_amount 1.8

transform pincushion:
    mesh_pad 20
    shader "shader.distort_barrel"
    u_amount 0.7

# Wave distortion (animated) - pause 0 + repeat forces continuous redraw
transform wave_gentle:
    mesh_pad 30
    shader "shader.distort_wave"
    u_amplitude 0.01
    u_frequency 10.0
    u_speed 2.0
    pause 0
    repeat

transform wave_strong:
    mesh_pad 50
    shader "shader.distort_wave"
    u_amplitude 0.03
    u_frequency 8.0
    u_speed 3.0
    pause 0
    repeat

transform wave_dreamy:
    mesh_pad 40
    shader "shader.distort_wave"
    u_amplitude 0.015
    u_frequency 5.0
    u_speed 1.0
    pause 0
    repeat

# Ripple (animated, from center) - pause 0 + repeat forces continuous redraw
transform ripple_calm:
    mesh_pad 30
    shader "shader.distort_ripple"
    u_amplitude 0.01
    u_frequency 20.0
    u_speed 3.0
    u_center (0.5, 0.5)
    pause 0
    repeat

transform ripple_intense:
    mesh_pad 50
    shader "shader.distort_ripple"
    u_amplitude 0.03
    u_frequency 30.0
    u_speed 5.0
    u_center (0.5, 0.5)
    pause 0
    repeat

# Shake/Jitter (animated) - pause 0 + repeat forces continuous redraw
transform shake_light:
    mesh_pad 10
    shader "shader.distort_shake"
    u_intensity 2.0
    u_speed 20.0
    pause 0
    repeat

transform shake_heavy:
    mesh_pad 20
    shader "shader.distort_shake"
    u_intensity 8.0
    u_speed 30.0
    pause 0
    repeat

transform shake_panic:
    mesh_pad 30
    shader "shader.distort_shake"
    u_intensity 15.0
    u_speed 50.0
    pause 0
    repeat


################################################################################
## Color Adjustment Transforms
################################################################################

# Grayscale
transform grayscale:
    shader "shader.color_grayscale"
    u_amount 1.0

transform grayscale_partial:
    shader "shader.color_grayscale"
    u_amount 0.5

# Sepia
transform sepia:
    shader "shader.color_sepia"
    u_amount 1.0

transform sepia_light:
    shader "shader.color_sepia"
    u_amount 0.5

# Invert
transform invert:
    shader "shader.color_invert"
    u_amount 1.0

transform invert_partial:
    shader "shader.color_invert"
    u_amount 0.5

# Brightness/Contrast adjustments
transform brighten:
    shader "shader.color_adjust"
    u_brightness 0.15
    u_contrast 1.0
    u_saturation 1.0

transform darken:
    shader "shader.color_adjust"
    u_brightness -0.2
    u_contrast 1.0
    u_saturation 1.0

transform high_contrast:
    shader "shader.color_adjust"
    u_brightness 0.0
    u_contrast 1.5
    u_saturation 1.0

transform low_contrast:
    shader "shader.color_adjust"
    u_brightness 0.0
    u_contrast 0.7
    u_saturation 1.0

transform saturate:
    shader "shader.color_adjust"
    u_brightness 0.0
    u_contrast 1.0
    u_saturation 1.5

transform desaturate:
    shader "shader.color_adjust"
    u_brightness 0.0
    u_contrast 1.0
    u_saturation 0.5

# Tint colors
transform tint_red:
    shader "shader.color_tint"
    u_tint_color (1.0, 0.7, 0.7, 1.0)
    u_amount 0.5

transform tint_blue:
    shader "shader.color_tint"
    u_tint_color (0.7, 0.7, 1.0, 1.0)
    u_amount 0.5

transform tint_green:
    shader "shader.color_tint"
    u_tint_color (0.7, 1.0, 0.7, 1.0)
    u_amount 0.5

transform tint_warm:
    shader "shader.color_tint"
    u_tint_color (1.0, 0.9, 0.8, 1.0)
    u_amount 0.4

transform tint_cool:
    shader "shader.color_tint"
    u_tint_color (0.8, 0.9, 1.0, 1.0)
    u_amount 0.4

# Hue shift (0.0 to 1.0 = full color wheel)
transform hue_shift_small:
    shader "shader.color_hue"
    u_shift 0.1

transform hue_shift_opposite:
    shader "shader.color_hue"
    u_shift 0.5

# Parameterized color adjust
transform color_adjust(brightness=0.0, contrast=1.0, saturation=1.0):
    shader "shader.color_adjust"
    u_brightness brightness
    u_contrast contrast
    u_saturation saturation


################################################################################
## Retro/Stylized Transforms
################################################################################

# Pixelate
transform pixelate_light:
    shader "shader.retro_pixelate"
    u_pixel_size 4.0

transform pixelate_medium:
    shader "shader.retro_pixelate"
    u_pixel_size 8.0

transform pixelate_heavy:
    shader "shader.retro_pixelate"
    u_pixel_size 16.0

transform pixelate_extreme:
    shader "shader.retro_pixelate"
    u_pixel_size 32.0

# Scanlines
transform scanlines_subtle:
    shader "shader.retro_scanlines"
    u_intensity 0.15
    u_count 300.0

transform scanlines_crt:
    shader "shader.retro_scanlines"
    u_intensity 0.3
    u_count 400.0

transform scanlines_heavy:
    shader "shader.retro_scanlines"
    u_intensity 0.5
    u_count 500.0

# Vignette
transform vignette_light:
    shader "shader.retro_vignette"
    u_intensity 0.3
    u_radius 0.8

transform vignette_medium:
    shader "shader.retro_vignette"
    u_intensity 0.5
    u_radius 0.6

transform vignette_heavy:
    shader "shader.retro_vignette"
    u_intensity 0.7
    u_radius 0.5

transform vignette_dramatic:
    shader "shader.retro_vignette"
    u_intensity 0.9
    u_radius 0.4

# Chromatic Aberration
transform chromatic_subtle:
    shader "shader.retro_chromatic"
    u_amount 0.005

transform chromatic_medium:
    shader "shader.retro_chromatic"
    u_amount 0.015

transform chromatic_heavy:
    shader "shader.retro_chromatic"
    u_amount 0.03

# Glitch (animated) - pause 0 + repeat forces continuous redraw
transform glitch_light:
    shader "shader.retro_glitch"
    u_intensity 0.3
    u_speed 1.0
    pause 0
    repeat

transform glitch_medium:
    shader "shader.retro_glitch"
    u_intensity 0.6
    u_speed 2.0
    pause 0
    repeat

transform glitch_heavy:
    shader "shader.retro_glitch"
    u_intensity 1.0
    u_speed 3.0
    pause 0
    repeat

# Parameterized pixelate
transform pixelate_custom(size=8.0):
    shader "shader.retro_pixelate"
    u_pixel_size size


################################################################################
## Outline Transforms
## mesh_pad allows outline to extend beyond image bounds
################################################################################

transform outline_black:
    mesh_pad 10
    shader "shader.outline"
    u_width 2.0
    u_outline_color (0.0, 0.0, 0.0, 1.0)

transform outline_white:
    mesh_pad 10
    shader "shader.outline"
    u_width 2.0
    u_outline_color (1.0, 1.0, 1.0, 1.0)

transform outline_gold:
    mesh_pad 15
    shader "shader.outline"
    u_width 3.0
    u_outline_color (1.0, 0.85, 0.3, 1.0)

transform outline_custom(width=2.0, color=(0.0, 0.0, 0.0, 1.0), pad=10):
    mesh_pad pad
    shader "shader.outline"
    u_width width
    u_outline_color color


################################################################################
## Combined Effect Transforms
################################################################################

# Flashback look (sepia + vignette)
transform flashback:
    shader "shader.color_sepia"
    u_amount 0.7

transform flashback_full:
    shader "shader.color_sepia"
    u_amount 1.0

# Dream sequence (blur + wave + desaturate) - animated, needs pause 0 + repeat
transform dream:
    mesh_pad 30
    shader "shader.distort_wave"
    u_amplitude 0.008
    u_frequency 5.0
    u_speed 1.0
    pause 0
    repeat

# Horror effect (desaturate + vignette + chromatic)
transform horror:
    shader "shader.color_adjust"
    u_brightness -0.1
    u_contrast 1.2
    u_saturation 0.4

# Damaged/hurt effect (red tint + shake)
transform hurt:
    shader "shader.color_tint"
    u_tint_color (1.0, 0.3, 0.3, 1.0)
    u_amount 0.4

# Power up effect (glow + saturate) - animated
transform power_up:
    mesh_pad 60
    shader "shader.glow_pulse"
    u_strength 1.2
    u_speed 4.0
    u_glow_color (1.0, 1.0, 0.5, 1.0)
    pause 0
    repeat

# Freeze/Ice effect (blue tint + slight desaturate)
transform frozen:
    shader "shader.color_tint"
    u_tint_color (0.6, 0.8, 1.0, 1.0)
    u_amount 0.6

# Poison effect (green tint)
transform poisoned:
    shader "shader.color_tint"
    u_tint_color (0.5, 1.0, 0.5, 1.0)
    u_amount 0.4

# Old TV effect (scanlines + slight noise via glitch)
transform old_tv:
    shader "shader.retro_scanlines"
    u_intensity 0.25
    u_count 350.0


################################################################################
## Animation Helpers
################################################################################

# Fade in glow
transform glow_fade_in(color=(1.0, 1.0, 1.0, 1.0), duration=0.5):
    mesh_pad 50
    shader "shader.glow"
    u_outer_strength 0.0
    u_inner_strength 0.0
    u_glow_color color
    u_scale 1.0
    linear duration u_outer_strength 0.8

# Pixelate transition (in)
transform pixelate_in(duration=0.5):
    shader "shader.retro_pixelate"
    u_pixel_size 2.0
    linear duration u_pixel_size 64.0

# Pixelate transition (out)
transform pixelate_out(duration=0.5):
    shader "shader.retro_pixelate"
    u_pixel_size 64.0
    linear duration u_pixel_size 2.0

# Blur in
transform blur_in(duration=0.5):
    mesh_pad 50
    shader "shader.blur_box"
    u_radius 0.0
    linear duration u_radius 5.0

# Blur out
transform blur_out(duration=0.5):
    mesh_pad 50
    shader "shader.blur_box"
    u_radius 5.0
    linear duration u_radius 0.0


################################################################################
## Additional Effects (from Phaser)
################################################################################

# Bokeh blur (depth-of-field style)
transform bokeh_light:
    mesh_pad 20
    shader "shader.blur_bokeh"
    u_radius 2.0
    u_amount 1.0
    u_contrast 0.0

transform bokeh_medium:
    mesh_pad 30
    shader "shader.blur_bokeh"
    u_radius 4.0
    u_amount 1.5
    u_contrast 0.2

transform bokeh_heavy:
    mesh_pad 50
    shader "shader.blur_bokeh"
    u_radius 8.0
    u_amount 2.0
    u_contrast 0.5

transform bokeh_custom(radius=4.0, amount=1.5, contrast=0.2, pad=30):
    mesh_pad pad
    shader "shader.blur_bokeh"
    u_radius radius
    u_amount amount
    u_contrast contrast

# Light rays effect - u_samples is float for GPU compatibility
# mesh_pad adds padding so rays can extend beyond image bounds
transform light_rays:
    mesh_pad (100, 150, 100, 50)  # left, top, right, bottom padding
    shader "shader.light_rays"
    u_light_position (0.5, 0.0)
    u_color (1.0, 0.95, 0.8, 1.0)
    u_decay 0.95
    u_power 0.3
    u_intensity 0.5
    u_samples 8.0

transform light_rays_strong:
    mesh_pad (150, 200, 150, 50)  # more padding for stronger effect
    shader "shader.light_rays"
    u_light_position (0.5, 0.0)
    u_color (1.0, 0.9, 0.7, 1.0)
    u_decay 0.9
    u_power 0.5
    u_intensity 0.8
    u_samples 12.0

transform light_rays_custom(pos=(0.5, 0.0), color=(1.0, 0.95, 0.8, 1.0), intensity=0.5, pad=100):
    mesh_pad (pad, pad * 1.5, pad, pad * 0.5)
    shader "shader.light_rays"
    u_light_position pos
    u_color color
    u_decay 0.95
    u_power 0.3
    u_intensity intensity
    u_samples 8.0

# Threshold effect (posterize/contrast)
transform threshold_high:
    shader "shader.threshold"
    u_edge1 (0.3, 0.3, 0.3, 0.0)
    u_edge2 (0.7, 0.7, 0.7, 1.0)
    u_invert (0.0, 0.0, 0.0, 0.0)

transform threshold_medium:
    shader "shader.threshold"
    u_edge1 (0.2, 0.2, 0.2, 0.0)
    u_edge2 (0.8, 0.8, 0.8, 1.0)
    u_invert (0.0, 0.0, 0.0, 0.0)

transform threshold_inverted:
    shader "shader.threshold"
    u_edge1 (0.3, 0.3, 0.3, 0.0)
    u_edge2 (0.7, 0.7, 0.7, 1.0)
    u_invert (1.0, 1.0, 1.0, 1.0)

# Gaussian blur (higher quality)
transform blur_gaussian_light:
    mesh_pad 15
    shader "shader.blur_gaussian"
    u_offset (1.0, 1.0)
    u_strength 1.0

transform blur_gaussian_medium:
    mesh_pad 25
    shader "shader.blur_gaussian"
    u_offset (1.0, 1.0)
    u_strength 2.0

transform blur_gaussian_heavy:
    mesh_pad 40
    shader "shader.blur_gaussian"
    u_offset (1.0, 1.0)
    u_strength 4.0

transform blur_gaussian_custom(strength=2.0, direction=(1.0, 1.0), pad=25):
    mesh_pad pad
    shader "shader.blur_gaussian"
    u_offset direction
    u_strength strength

# High quality Gaussian blur (13-tap)
transform blur_gaussian_hq:
    mesh_pad 30
    shader "shader.blur_gaussian_high"
    u_offset (1.0, 1.0)
    u_strength 2.0
