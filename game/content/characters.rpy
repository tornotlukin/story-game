## characters.rpy - Character definitions
##
## Define all speaking characters here. Each character can have
## custom colors, name styles, and other properties.
##
## Related files: script.rpy, ui/colors.rpy

################################################################################
## Narrator
################################################################################

## The narrator (no name shown)
define narrator = Character(None, kind=adv)


################################################################################
## Example Characters
################################################################################

## Example character with colored name
# define e = Character("Eileen", color="#c8ffc8")

## Example character with custom who_color
# define m = Character("Me", who_color="#c8c8ff")

## Example character with image tag (for automatic sprite changes)
# define s = Character("Sylvie", image="sylvie", who_color="#c8ffc8")


################################################################################
## Project Characters
################################################################################

## Novy-chan - main character
define novy = Character("Novy-chan", image="novy")


################################################################################
## Image Definitions
################################################################################

## Backgrounds
image bg_street = "images/bg_street.png"

## Character sprites
image novy front = "images/novy_front.png"


################################################################################
## Character Template
################################################################################

## Copy this template to create new characters:
##
## define short_name = Character(
##     "Display Name",
##     who_color="#hexcolor",           # Name color
##     what_color="#hexcolor",          # Dialogue color (optional)
##     image="image_tag",               # For say with image attributes
##     voice_tag="voice_channel",       # For voice acting
## )
##
## Example usage in script:
##     short_name "Hello, this is my dialogue."
##     short_name happy "This shows 'happy' expression if image tag is set."


################################################################################
## Special Characters
################################################################################

## Centered text (for titles, chapter headers)
define centered = Character(None, what_style="centered_text")

## Thought text (for internal monologue)
# define thought = Character(None, what_style="thought_text", what_prefix="(", what_suffix=")")


################################################################################
## Dynamic Name Characters
################################################################################

## Character whose name comes from a variable
# default player_name = "Player"
# define player = Character("[player_name]", dynamic=True)

## Usage:
##     $ player_name = renpy.input("What is your name?")
##     player "My name is [player_name]!"
