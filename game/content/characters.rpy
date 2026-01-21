## characters.rpy - Character definitions
##
## DIALOG BOX SYSTEM:
## Each character's dialog box is loaded from gui/dialog/{name}.png
## where {name} is the display name (lowercase, spaces to underscores)
## Falls back to gui/dialog/default.png if not found.

################################################################################
## Narrator
################################################################################

## Narrator (no name shown) - uses default.png
define narrator = Character(None, kind=adv)


################################################################################
## Test Characters
################################################################################

## Guide - tutorial/help voice
define guide = Character("Guide", who_color="#88ccff")

## Novy - example character
define novy = Character("Novy", who_color="#ff88cc")


################################################################################
## Images
################################################################################

## Backgrounds
image bg_welcome = Solid("#2a2a4a")
image bg_test = Solid("#3a4a3a")
