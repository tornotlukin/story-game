# Workshop: Game Base Styling

**Started:** 2026-01-21
**Status:** In Progress - Baseline Test Game Created

---

## The Idea

Replace Ren'Py's default visual styling with a custom look for the story game. Primary focus: replace the default transparent black "say" dialog box with a custom dialog box image. Secondary: establish a cohesive base visual style.

---

## Open Questions

- What style/aesthetic is the target? (modern, retro, fantasy, minimalist, etc.)
- What screen resolution/aspect ratio? (mobile portrait 1080x1920, landscape, etc.)
- Do you have dialog box artwork ready, or need placeholder dimensions?
- Should the character name plate also be customized?
- What about the choice menu styling?
- Any specific fonts in mind?

---

## Answers & Decisions

**Q: Target aesthetic?**
> A: Manual control - user wants to target each Ren'Py default and modify individually

**Q: Screen setup?**
> A: 1080x1920 primary, but edits should work across dimensions

**Q: Dialog box artwork?**
> A: Default dialog box art + ability to swap per-character

**Q: Scope?**
> A: EVERYTHING. JSON-driven system that controls all visual properties in the game.

**Q: Text positioning?**
> A: Fully customizable at any point

**Q: JSON structure?**
> A: One big theme.json - will figure out what gets applied

**Q: Per-character dialog trigger?**
> A: Character definition includes dialog box reference. Emotional states = shaders applied to dialog boxes.

**Q: Priority order?**
> A: Say screen → Choice menus → Quick menu → Main menu → Game menu → NVL. ALSO fix quit functionality (X button) and settings.

**Q: Runtime vs init?**
> A: JSON used as a TOOL to set up main game files for ANY project. Template/generator system.

**Q: Audit first?**
> A: Yes - audit gui.rpy, screens.rpy, and docs for every default parameter

---

## Conversation Log

> **User:** I want to clean up the game's base styling. We set up the preset system and an editor so that's set. I want to create a base layout and "look" for the story game that replaces some of the Ren'Py defaults. I would like to replace the transparent black "say" dialog box with a dialog box image.

> **User:** The defaults are hard to replace, we must find a way that works.

> **Claude:** Created workshop file, asking clarifying questions...

> **User:** Clarifications:
> - Building a PARADIGM PROJECT - template foundation for all future story games
> - Per-character dialog boxes - need to add this capability to base files
> - Quit (X button) bug - clicking X resets to start instead of quitting. Need proper "Are you sure?" modal with warning about losing progress
> - Tool modifies base game files to set up the game's look and behavior

> **Claude:** Audited gui.rpy (~100+ properties) and screens.rpy (20+ screens). Investigating quit issue...

> **User:** Also include a "system message" dialog box artwork for any system dialogs

> **Claude:** Proposed dialog box architecture with default, per-character, and system types.

> **User:** Answers to finalize:
> 1. Character tag directly (simple: "novy" → dialog_novy.png)
> 2. Namebox should be uniform across all characters
> 3. Ready to implement

---

## Implementation Plan

### Phase 1: Quit Functionality Fix
1. Add `config.quit_action` to options.rpy
2. Customize confirm screen message for quit
3. Use system dialog artwork for confirm screen

### Phase 2: Dialog Box System
1. Create `gui/dialog/` folder structure
2. Modify say screen to load per-character dialog boxes
3. Character tag → `gui/dialog/{tag}.png`, fallback to `default.png`
4. Namebox remains uniform

### Phase 3: System Dialogs
1. Modify confirm screen to use `gui/dialog/system.png`
2. Modify notify screen if needed
3. Consistent system dialog styling

---

## Completed Implementation

### Quit Functionality Fix
- Added `config.quit_action = Quit(confirm=True)` in `options.rpy`
- Custom message via `gui.QUIT`: "Are you sure you want to quit?\n\nAny unsaved progress will be lost."
- **FIX for X button treated as screen click**: Disabled confirm dialog transitions
  - `config.enter_yesno_transition = None`
  - `config.exit_yesno_transition = None`
  - Workaround for [GitHub issue #972](https://github.com/renpy/renpy/issues/972)
- Added `config.mouse_focus_clickthrough = False` to prevent window-focus clicks from advancing dialogue
- Added `preferences.renderer = "auto"` with documentation for switching to ANGLE2 if needed

### Per-Character Dialog Box System
- Created `gui/dialog/` folder structure
- Added `get_dialog_image(who)` helper function in `screens.rpy`
- Modified say screen to use dynamic background based on speaker
- Character name → filename: "Novy" → `gui/dialog/novy.png`
- Falls back to `gui/dialog/default.png` if no character-specific file exists

### System Dialog Artwork
- Modified confirm screen style to use `gui/dialog/system.png`
- All system dialogs (quit, save overwrite, etc.) now use consistent artwork

---

## Image Requirements

### Dialog Box Images (`gui/dialog/`)

| File | Purpose | Dimensions |
|------|---------|------------|
| `default.png` | Fallback dialog box | Match textbox.png |
| `system.png` | System dialogs (quit, confirm) | Can be different size |
| `{character}.png` | Per-character (e.g., `novy.png`) | Match textbox.png |

**Naming Convention:**
- Character display name is converted to filename
- Lowercase, spaces → underscores, apostrophes removed
- Examples:
  - "Novy" → `novy.png`
  - "Dr. Smith" → `dr._smith.png`
  - "Mary Jane" → `mary_jane.png`

**Current Placeholders:**
- `default.png` - Copy of original textbox.png
- `system.png` - Copy of original textbox.png

---

## Key Insights

1. Ren'Py's say screen is defined in `screens.rpy` - can be fully customized
2. The `window` style controls the dialog box appearance
3. Can use `background` property with an image instead of solid color
4. Need to handle nine-patch/Frame for scalable dialog boxes

---

## Technical Notes

### Vision: JSON-Driven Theme System

A single `theme.json` file that:
1. Controls ALL visual properties in the game
2. Supports per-character dialog box images
3. Can be used as a TOOL to generate game files for ANY project
4. Works across different screen dimensions

### JSON Tool: Window Behavior Settings

The JSON tool should include these window/quit behavior settings:

```json
{
  "window_behavior": {
    "quit_action": {
      "confirm": true,
      "message": "Are you sure you want to quit?\n\nAny unsaved progress will be lost."
    },
    "transitions": {
      "enter_yesno": null,
      "exit_yesno": null,
      "_comment": "Set to null to fix X button click issue (GitHub #972)"
    },
    "mouse": {
      "focus_clickthrough": false,
      "_comment": "Prevents window-focus clicks from advancing dialogue"
    },
    "renderer": {
      "default": "auto",
      "options": ["auto", "gl", "angle", "gles", "gl2", "angle2", "gles2"],
      "_comment": "Use angle2 if X button issues persist on Windows"
    }
  }
}
```

**Generated Code:**
```python
## Window Behavior (options.rpy)
define config.quit_action = Quit(confirm=True)
define gui.QUIT = _("Are you sure you want to quit?\n\nAny unsaved progress will be lost.")
define config.enter_yesno_transition = None
define config.exit_yesno_transition = None
define config.mouse_focus_clickthrough = False
default preferences.renderer = "auto"
```

---

## AUDIT: gui.rpy Parameters

### Colors (10 properties)
| Property | Default | Description |
|----------|---------|-------------|
| `gui.accent_color` | `#0099cc` | Highlight/label color |
| `gui.idle_color` | `#888888` | Default button text |
| `gui.idle_small_color` | `#aaaaaa` | Small text (brighter) |
| `gui.hover_color` | `#66c1e0` | Hovered button/bar |
| `gui.selected_color` | `#ffffff` | Selected button |
| `gui.insensitive_color` | `#8888887f` | Disabled button |
| `gui.muted_color` | `#003d51` | Bar unfilled |
| `gui.hover_muted_color` | `#005b7a` | Bar unfilled hover |
| `gui.text_color` | `#ffffff` | Dialogue text |
| `gui.interface_text_color` | `#ffffff` | UI text |

### Fonts (3 properties)
| Property | Default | Description |
|----------|---------|-------------|
| `gui.text_font` | `Jua-Regular.ttf` | Dialogue font |
| `gui.name_text_font` | `CalSans-Regular.ttf` | Character name font |
| `gui.interface_text_font` | `CalSans-Regular.ttf` | Menu/UI font |

### Font Sizes (7 properties)
| Property | Default | Description |
|----------|---------|-------------|
| `gui.text_size` | `19` | Dialogue text |
| `gui.name_text_size` | `26` | Character name |
| `gui.interface_text_size` | `19` | UI text |
| `gui.label_text_size` | `21` | Labels |
| `gui.notify_text_size` | `14` | Notifications |
| `gui.title_text_size` | `43` | Game title |
| `gui.quick_button_text_size` | `12` | Quick menu buttons |

### Menu Backgrounds (2 properties)
| Property | Default | Description |
|----------|---------|-------------|
| `gui.main_menu_background` | `gui/main_menu.png` | Main menu BG |
| `gui.game_menu_background` | `gui/game_menu.png` | In-game menu BG |

### Dialogue/Textbox (11 properties)
| Property | Default | Description |
|----------|---------|-------------|
| `gui.textbox_height` | `157` | Dialog box height |
| `gui.textbox_yalign` | `1.0` | Dialog box vertical position |
| `gui.name_xpos` | `203` | Name X position |
| `gui.name_ypos` | `0` | Name Y position |
| `gui.name_xalign` | `0.0` | Name horizontal alignment |
| `gui.namebox_width` | `None` | Name box width (auto) |
| `gui.namebox_height` | `None` | Name box height (auto) |
| `gui.namebox_borders` | `Borders(5,5,5,5)` | Name box 9-patch borders |
| `gui.namebox_tile` | `False` | Tile vs scale |
| `gui.dialogue_xpos` | `227` | Dialogue text X |
| `gui.dialogue_ypos` | `43` | Dialogue text Y |
| `gui.dialogue_width` | `628` | Dialogue text width |
| `gui.dialogue_text_xalign` | `0.0` | Dialogue alignment |

### Button Base (9 properties)
| Property | Default | Description |
|----------|---------|-------------|
| `gui.button_width` | `None` | Button width (auto) |
| `gui.button_height` | `None` | Button height (auto) |
| `gui.button_borders` | `Borders(4,4,4,4)` | Button 9-patch |
| `gui.button_tile` | `False` | Tile vs scale |
| `gui.button_text_font` | (interface) | Button font |
| `gui.button_text_size` | (interface) | Button text size |
| `gui.button_text_idle_color` | (idle) | Idle text color |
| `gui.button_text_hover_color` | (hover) | Hover text color |
| `gui.button_text_selected_color` | (selected) | Selected color |
| `gui.button_text_insensitive_color` | (insensitive) | Disabled color |
| `gui.button_text_xalign` | `0.0` | Text alignment |

### Choice Buttons (9 properties)
| Property | Default | Description |
|----------|---------|-------------|
| `gui.choice_button_width` | `667` | Choice button width |
| `gui.choice_button_height` | `None` | Choice button height |
| `gui.choice_button_tile` | `False` | Tile vs scale |
| `gui.choice_button_borders` | `Borders(85,5,85,5)` | 9-patch borders |
| `gui.choice_button_text_font` | (text) | Choice font |
| `gui.choice_button_text_size` | (text) | Choice text size |
| `gui.choice_button_text_xalign` | `0.5` | Choice alignment |
| `gui.choice_button_text_idle_color` | `#888888` | Idle color |
| `gui.choice_button_text_hover_color` | `#ffffff` | Hover color |
| `gui.choice_button_text_insensitive_color` | `#8888887f` | Disabled |

### Save/Load Slots (9 properties)
| Property | Default | Description |
|----------|---------|-------------|
| `gui.slot_button_width` | `233` | Slot button width |
| `gui.slot_button_height` | `174` | Slot button height |
| `gui.slot_button_borders` | `Borders(9,9,9,9)` | 9-patch borders |
| `gui.slot_button_text_size` | `12` | Slot text size |
| `gui.slot_button_text_xalign` | `0.5` | Slot alignment |
| `config.thumbnail_width` | `216` | Save thumbnail width |
| `config.thumbnail_height` | `122` | Save thumbnail height |
| `gui.file_slot_cols` | `3` | Grid columns |
| `gui.file_slot_rows` | `2` | Grid rows |

### Positioning/Spacing (10 properties)
| Property | Default | Description |
|----------|---------|-------------|
| `gui.navigation_xpos` | `34` | Nav buttons X |
| `gui.skip_ypos` | `9` | Skip indicator Y |
| `gui.notify_ypos` | `38` | Notification Y |
| `gui.choice_spacing` | `19` | Choice spacing |
| `gui.navigation_spacing` | `4` | Nav button spacing |
| `gui.pref_spacing` | `9` | Preference spacing |
| `gui.pref_button_spacing` | `0` | Pref button spacing |
| `gui.page_spacing` | `0` | Page button spacing |
| `gui.slot_spacing` | `9` | Slot spacing |
| `gui.main_menu_text_xalign` | `1.0` | Main menu text align |

### Frames (5 properties)
| Property | Default | Description |
|----------|---------|-------------|
| `gui.frame_borders` | `Borders(4,4,4,4)` | Generic frame |
| `gui.confirm_frame_borders` | `Borders(34,34,34,34)` | Confirm dialog |
| `gui.skip_frame_borders` | `Borders(14,5,43,5)` | Skip indicator |
| `gui.notify_frame_borders` | `Borders(14,5,34,5)` | Notification |
| `gui.frame_tile` | `False` | Tile vs scale |

### Bars/Scrollbars/Sliders (14 properties)
| Property | Default | Description |
|----------|---------|-------------|
| `gui.bar_size` | `22` | Bar thickness |
| `gui.scrollbar_size` | `11` | Scrollbar thickness |
| `gui.slider_size` | `22` | Slider thickness |
| `gui.bar_tile` | `False` | Tile bars |
| `gui.scrollbar_tile` | `False` | Tile scrollbars |
| `gui.slider_tile` | `False` | Tile sliders |
| `gui.bar_borders` | `Borders(4,4,4,4)` | H-bar borders |
| `gui.scrollbar_borders` | `Borders(4,4,4,4)` | H-scroll borders |
| `gui.slider_borders` | `Borders(4,4,4,4)` | H-slider borders |
| `gui.vbar_borders` | `Borders(4,4,4,4)` | V-bar borders |
| `gui.vscrollbar_borders` | `Borders(4,4,4,4)` | V-scroll borders |
| `gui.vslider_borders` | `Borders(4,4,4,4)` | V-slider borders |
| `gui.unscrollable` | `"hide"` | Hide unneeded scrollbars |

### History (9 properties)
| Property | Default | Description |
|----------|---------|-------------|
| `config.history_length` | `250` | Entries to keep |
| `gui.history_height` | `119` | Entry height |
| `gui.history_spacing` | `0` | Entry spacing |
| `gui.history_name_xpos` | `131` | Name X |
| `gui.history_name_ypos` | `0` | Name Y |
| `gui.history_name_width` | `131` | Name width |
| `gui.history_name_xalign` | `1.0` | Name alignment |
| `gui.history_text_xpos` | `144` | Text X |
| `gui.history_text_ypos` | `2` | Text Y |
| `gui.history_text_width` | `625` | Text width |
| `gui.history_text_xalign` | `0.0` | Text alignment |

### NVL Mode (16 properties)
| Property | Default | Description |
|----------|---------|-------------|
| `gui.nvl_borders` | `Borders(0,9,0,17)` | Window borders |
| `gui.nvl_list_length` | `6` | Max entries |
| `gui.nvl_height` | `98` | Entry height |
| `gui.nvl_spacing` | `9` | Entry spacing |
| `gui.nvl_name_xpos` | `363` | Name X |
| `gui.nvl_name_ypos` | `0` | Name Y |
| `gui.nvl_name_width` | `127` | Name width |
| `gui.nvl_name_xalign` | `1.0` | Name alignment |
| `gui.nvl_text_xpos` | `380` | Text X |
| `gui.nvl_text_ypos` | `7` | Text Y |
| `gui.nvl_text_width` | `498` | Text width |
| `gui.nvl_text_xalign` | `0.0` | Text alignment |
| `gui.nvl_thought_xpos` | `203` | Thought X |
| `gui.nvl_thought_ypos` | `0` | Thought Y |
| `gui.nvl_thought_width` | `659` | Thought width |
| `gui.nvl_thought_xalign` | `0.0` | Thought alignment |
| `gui.nvl_button_xpos` | `380` | Button X |
| `gui.nvl_button_xalign` | `0.0` | Button alignment |

### Other
| Property | Default | Description |
|----------|---------|-------------|
| `gui.language` | `"unicode"` | Line break rules |

---

## AUDIT: screens.rpy

### Core Screens
| Screen | Purpose |
|--------|---------|
| `say` | Displays dialogue + character name |
| `input` | Text input prompts |
| `choice` | In-game choice menus |
| `quick_menu` | Quick access buttons (Save, Load, etc) |

### Menu Screens
| Screen | Purpose |
|--------|---------|
| `navigation` | Main/game menu navigation buttons |
| `main_menu` | Title screen |
| `game_menu` | Base template for save/load/prefs |
| `about` | About/credits |
| `save` | Save game |
| `load` | Load game |
| `file_slots` | Save/load slot grid |
| `preferences` | Settings/options |
| `history` | Dialogue history |
| `help` | Keyboard/mouse/gamepad help |
| `confirm` | Yes/No dialogs |

### Indicator/Utility Screens
| Screen | Purpose |
|--------|---------|
| `skip_indicator` | Shows skipping in progress |
| `notify` | Quick notifications |
| `nvl` | NVL-mode dialogue |
| `bubble` | Speech bubble dialogue |

### Key Image Files Referenced
| File | Used For |
|------|----------|
| `gui/textbox.png` | Say window background |
| `gui/namebox.png` | Character name background |
| `gui/main_menu.png` | Main menu background |
| `gui/game_menu.png` | Game menu background |
| `gui/overlay/main_menu.png` | Main menu overlay |
| `gui/overlay/game_menu.png` | Game menu overlay |
| `gui/overlay/confirm.png` | Confirm dialog overlay |
| `gui/frame.png` | Generic frame |
| `gui/confirm_frame.png` | Confirm frame |
| `gui/skip.png` | Skip indicator |
| `gui/notify.png` | Notification frame |
| `gui/nvl.png` | NVL background |
| `gui/bubble.png` | Speech bubble |
| `gui/thoughtbubble.png` | Thought bubble |
| `gui/bar/*` | Progress bars |
| `gui/scrollbar/*` | Scrollbars |
| `gui/slider/*` | Sliders |
| `gui/button/*` | Button backgrounds |

---

## Next Steps

1. ~~Investigate quit functionality (X button)~~ ⚠️ DEFERRED - SDL-level issue, use Escape→Menu→Quit for now
2. Check Ren'Py docs for `config.*` properties we might have missed
3. Design theme.json schema structure
4. Decide: generate files once, or runtime loading?

## Known Issues

### Quit Button (X) / Alt+F4 Not Working Properly
- **Symptom**: X button and Alt+F4 advance dialogue instead of quitting
- **Cause**: Likely SDL-level event handling issue
- **Workaround**: Use Escape → Game Menu → Quit
- **Status**: Deferred - requires deeper investigation
- **References**:
  - [GitHub SDL Issue #8517](https://github.com/libsdl-org/SDL/issues/8517)
  - [Ren'Py GitHub Issue #972](https://github.com/renpy/renpy/issues/972)

---

## Resources & Links

**Local Files:**
- `game/screens.rpy` - Default Ren'Py screens
- `game/gui.rpy` - GUI configuration
- `game/options.rpy` - Game configuration (quit behavior, renderer)

**Documentation:**
- `docs/renpy/screens.html` - Screen documentation
- `docs/renpy/style.html` - Style documentation
- `docs/renpy/config.html` - Config variables
- `docs/renpy/display_problems.html` - Graphics/renderer troubleshooting

**External References:**
- [GitHub Issue #972](https://github.com/renpy/renpy/issues/972) - Window close button flash/miss with transitions
- [Ren'Py Display Problems](https://www.renpy.org/doc/html/display_problems.html) - Renderer switching guide
- [Lemma Soft Forums - Quit Behavior](https://lemmasoft.renai.us/forums/viewtopic.php?t=50710) - Community discussion
