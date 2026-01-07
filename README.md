# Story Game - Ren'Py Project

A modular Ren'Py interactive fiction framework.

## Quick Start

1. Open this project in Ren'Py Launcher
2. Click "Launch Project" to test
3. Edit files in `content/` to write your story

## Directory Structure

```
game/
├── systems/        # Game mechanics (dice, state, etc.)
├── ui/             # Visual styling (colors, fonts, GUI)
├── screens/        # Interactive UI screens
├── transitions/    # Visual effects
├── content/        # YOUR STORY GOES HERE
└── options.rpy     # Game configuration
```

## Writing Your Story

### 1. Define Characters

Edit `content/characters.rpy`:

```renpy
define e = Character("Elena", who_color="#c8ffc8")
define m = Character("Marcus", who_color="#c8c8ff")
```

### 2. Write Scenes

Create files in `content/`:

```renpy
label chapter_01:
    scene bg forest with fade

    e "Welcome to the forest."

    menu:
        "Go left":
            jump path_left
        "Go right":
            jump path_right
```

### 3. Use Game Systems

```renpy
# Roll dice
$ result, rolls = dice.roll("1d20+5")
"You rolled [result]!"

# Set flags
$ game_state.set_flag("found_key")

# Check flags
if game_state.has_flag("found_key"):
    "You use the key to unlock the door."

# Skill checks
$ success, roll, total = dice.skill_check(
    game_state.get_stat("charisma"),
    difficulty=15
)
if success:
    "You convince the guard."
```

## Platform Support

This template supports:
- **Desktop**: Windows, Mac, Linux
- **Mobile**: Android, iOS
- **Web**: HTML5

All UI elements are touch-friendly (60px+ touch targets).

## Files You'll Edit

| File | Purpose |
|------|---------|
| `content/script.rpy` | Main story |
| `content/characters.rpy` | Character definitions |
| `options.rpy` | Game title, version |
| `ui/colors.rpy` | Color scheme |

## Files You Probably Won't Edit

| File | Purpose |
|------|---------|
| `systems/*.rpy` | Game mechanics |
| `screens/*.rpy` | UI screens |
| `transitions/*.rpy` | Visual effects |
| `ui/gui.rpy` | Layout settings |

## Resources

- [Ren'Py Documentation](https://www.renpy.org/doc/html/)
- [Lemma Soft Forums](https://lemmasoft.renai.us/forums/)
- See `docs/renpy/` for offline documentation

## Development

See `claude.md` in the project root for detailed development guidelines.
