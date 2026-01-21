## options.rpy - Game configuration
##
## Ren'Py configuration options. Controls game metadata,
## build settings, and engine behavior.
##
## Related files: ui/gui.rpy

################################################################################
## Game Metadata
################################################################################

## Game title shown in window title bar
define config.name = _("My Story Game")

## Short name for save directories (no spaces or special characters)
define build.name = "MyStoryGame"

## Version number
define config.version = "0.1.0"

## Credits text shown on About screen
define gui.about = _("")

## GUI flag - indicates custom GUI is in use
define gui.show_name = True


################################################################################
## Sound & Music
################################################################################

## Main volume mixer
define config.has_sound = True
define config.has_music = True
define config.has_voice = True

## Sample sounds for preferences screen
define config.sample_sound = None
define config.sample_voice = None

## Music to play on main menu
define config.main_menu_music = None


################################################################################
## Screen Dimensions
################################################################################

## Base resolution (vertical/portrait mode)
define config.screen_width = 1080
define config.screen_height = 1920

## Window size (for windowed mode)
define config.physical_width = 540
define config.physical_height = 960


################################################################################
## Save/Load Configuration
################################################################################

## Directory for saves (relative to Ren'Py save location)
define config.save_directory = "mystorygame-saves"



################################################################################
## Transitions
################################################################################

## Default transitions
define config.enter_transition = dissolve
define config.exit_transition = dissolve

## Transition between main/game menu and game
define config.intra_transition = dissolve


## After load transition
define config.after_load_transition = dissolve

## End game transition
define config.end_game_transition = fade


################################################################################
## Window Behavior
################################################################################

## Show dialogue window before dialogue
define config.window_show_transition = Dissolve(0.2)
define config.window_hide_transition = Dissolve(0.2)

## Window icon
define config.window_icon = None

## Quit behavior - show confirm dialog when clicking X button
define config.quit_action = Quit(confirm=True)

## Custom quit confirmation message (overrides default "Are you sure you want to quit?")
define gui.QUIT = _("Are you sure you want to quit?\n\nAny unsaved progress will be lost.")

## FIX: Disable transitions for confirm dialogs
## Workaround for GitHub issue #972 - window close button can cause flash/miss
## when transitions are enabled on confirm screens
define config.enter_yesno_transition = None
define config.exit_yesno_transition = None


################################################################################
## Dialogue Settings
################################################################################

## Default text speed (characters per second, 0 for instant)
default preferences.text_cps = 40

## Auto-forward time
default preferences.afm_time = 15


################################################################################
## Layers
################################################################################

## Image layers (bottom to top)
define config.layers = ['master', 'transient', 'screens', 'overlay']


################################################################################
## Graphics / Renderer
################################################################################

## Prefer ANGLE2 renderer on Windows (more stable with window events)
## Users can override with Shift+G during gameplay
## Options: "auto", "gl", "angle", "gles", "gl2", "angle2", "gles2"
default preferences.renderer = "auto"

## Mouse focus clickthrough - if true, clicks that focus the window are also
## processed as game clicks. Set to False to prevent X button click from
## advancing dialogue.
define config.mouse_focus_clickthrough = False


################################################################################
## Developer Tools
################################################################################

## Enable developer console (Shift+O)
## Set to False to avoid director screen issues
define config.developer = False

## Console access
define config.console = False


################################################################################
## Build Configuration
################################################################################

init python:

    ## File patterns to include in distributions
    build.classify('**~', None)
    build.classify('**.bak', None)
    build.classify('**/.**', None)
    build.classify('**/#**', None)
    build.classify('**/thumbs.db', None)
    build.classify('**.rpy', None)
    build.classify('**.rpyc', 'archive')
    build.classify('**.png', 'archive')
    build.classify('**.jpg', 'archive')
    build.classify('**.webp', 'archive')
    build.classify('**.ogg', 'archive')
    build.classify('**.opus', 'archive')
    build.classify('**.mp3', 'archive')

    ## Documentation to include
    build.documentation('*.html')
    build.documentation('*.txt')


################################################################################
## Mobile Configuration
################################################################################

## Enable mobile variants
define config.variants = ['touch', 'small', 'medium', 'large', 'tablet', 'phone']

## Mobile gestures (maps gesture patterns to events)
## Example: "n_s_w_e_w_e" maps to "progress_screen"
define config.gestures = {}
