# Tools Development Guide

Development guidelines for tools in this folder, primarily DearPyGui-based editors.

## DearPyGui Callback Best Practices

### The Callback Signature Problem

DearPyGui callbacks receive three arguments: `(sender, app_data, user_data)`. This causes issues with common Python patterns.

**The signature:**
```python
def callback(sender, app_data, user_data):
    # sender: the widget ID that triggered the callback
    # app_data: the widget's current value
    # user_data: optional data passed via user_data= parameter
```

### Common Mistake: Lambda Closures with Default Parameters

When creating callbacks in loops, this pattern **DOES NOT WORK**:

```python
# BAD - DO NOT USE
for key in ["name", "version", "author"]:
    dpg.add_input_text(
        tag=f"field_{key}",
        callback=lambda s, a, k=key: save_value(k, a)  # BROKEN!
    )
```

**Why it fails:** DearPyGui passes `user_data` (which defaults to `None`) as the third argument. This overwrites the `k=key` default parameter, so `k` becomes `None` instead of the captured key value.

**Result:** All values get saved with key `None` (or `"null"` in JSON).

### Solution: Factory Functions

Use factory functions that properly close over variables:

```python
# GOOD - Use factory functions
def _make_callback(section: str, key: str):
    """Create a callback that properly captures section and key."""
    def callback(sender, app_data, user_data):
        # section and key are captured in the closure
        # user_data is ignored (can be None, doesn't matter)
        save_value(section, key, app_data)
    return callback

# Usage in loops
for key in ["name", "version", "author"]:
    dpg.add_input_text(
        tag=f"field_{key}",
        callback=_make_callback("project", key)  # Works correctly!
    )
```

### Alternative: Use user_data Properly

If you need to pass data, use the `user_data` parameter explicitly:

```python
# ALSO GOOD - Use user_data parameter
def _on_value_change(sender, app_data, user_data):
    """Handle value change. user_data should be (section, key) tuple."""
    if user_data:
        section, key = user_data
        save_value(section, key, app_data)

# Usage
for key in ["name", "version", "author"]:
    dpg.add_input_text(
        tag=f"field_{key}",
        callback=_on_value_change,
        user_data=("project", key)  # Pass data via user_data
    )
```

### Factory Function Examples

Here are common factory function patterns:

```python
def _make_callback(section: str, key: str):
    """Basic callback for saving values."""
    def callback(sender, app_data, user_data):
        if config_manager:
            config_manager.set_value(section, key, app_data)
    return callback


def _make_callback_nullable(section: str, key: str):
    """Callback where 0 means None/null."""
    def callback(sender, app_data, user_data):
        if config_manager:
            value = app_data if app_data > 0 else None
            config_manager.set_value(section, key, value)
    return callback


def _make_color_picker_callback(section: str, key: str):
    """Callback for color picker that converts RGBA to hex."""
    def callback(sender, app_data, user_data):
        rgba = app_data
        r, g, b = int(rgba[0]), int(rgba[1]), int(rgba[2])
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        if config_manager:
            config_manager.set_value(section, key, hex_color)
    return callback


def _make_combo_callback(section: str, key: str, transform=None):
    """Callback for combo boxes with optional value transform."""
    def callback(sender, app_data, user_data):
        value = transform(app_data) if transform else app_data
        if config_manager:
            config_manager.set_value(section, key, value)
    return callback
```

### Quick Reference

| Pattern | Works? | Notes |
|---------|--------|-------|
| `lambda s, a: func(a)` | Yes | No captured variables needed |
| `lambda s, a, k=key: func(k, a)` | **NO** | `user_data` overwrites `k` |
| `lambda s, a, u, k=key: func(k, a)` | Yes | Explicit `u` for user_data, but ugly |
| Factory function | **Yes** | Recommended approach |
| `callback=func, user_data=(k,v)` | **Yes** | Clean, use tuple for multiple values |

### Debugging Tips

If values are being saved with wrong keys (especially `None` or `"null"`):

1. Check for lambda closures with default parameters in loops
2. Add print statements to verify what values the callback receives:
   ```python
   def callback(sender, app_data, user_data):
       print(f"sender={sender}, app_data={app_data}, user_data={user_data}")
   ```
3. Search codebase for the problematic pattern:
   ```bash
   grep -r "lambda s, a, .*=.*:" *.py
   ```

## Color Handling in DearPyGui

### Use the Shared Utilities

The `ui_components.py` module provides robust color conversion functions. **Always use these instead of writing custom code:**

```python
from ui_components import rgba_to_hex, hex_to_rgb, hex_to_rgba, is_valid_hex

# Convert DearPyGui color picker output to hex string
hex_color = rgba_to_hex(app_data)  # 6-digit hex, handles both 0-255 and 0.0-1.0
hex_color = rgba_to_hex(app_data, include_alpha=True)  # 8-digit hex with alpha

# Convert hex string to RGB/RGBA tuple for DearPyGui
rgb = hex_to_rgb("#FF5500")      # Returns (255, 85, 0)
rgba = hex_to_rgba("#FF55007F")  # Returns (255, 85, 0, 127) - supports 6 or 8 digit

# Validate hex input (accepts both 6 and 8 digit)
if is_valid_hex(user_input):
    # Process valid hex
```

### Ren'Py Color Format

Ren'Py accepts both formats:
- `#RRGGBB` - 6-digit hex, alpha assumed to be FF (fully opaque)
- `#RRGGBBAA` - 8-digit hex with explicit alpha

For consistency, the Game Config tab uses **8-digit hex** for all colors.

### DearPyGui Color Format Gotcha

**DearPyGui `color_edit` returns floats 0.0-1.0, not integers 0-255!**

```python
# BAD - assumes 0-255 range (WRONG!)
def on_color_change(sender, app_data, user_data):
    r, g, b = int(app_data[0]), int(app_data[1]), int(app_data[2])
    # Result: int(0.6) = 0, colors become #000000

# GOOD - use rgba_to_hex which handles both formats
def on_color_change(sender, app_data, user_data):
    hex_color = rgba_to_hex(app_data)  # Correctly converts 0.0-1.0 to hex
```

### Pre-built Color Widget

For paired color picker + hex input, use `add_color_edit_with_hex`:

```python
from ui_components import add_color_edit_with_hex

def on_color_change(sender, hex_color, user_data):
    # hex_color is already a proper hex string like "#FF5500"
    section, key = user_data
    config.set_value(section, key, hex_color.lower())

# Creates synced color picker and hex input
color_id, hex_id = add_color_edit_with_hex(
    label="Accent Color",
    default_value="#0099cc",
    callback=on_color_change,
    user_data=("colors", "accent"),
    color_width=150,
    hex_width=80
)
```

### DearPyGui Color Input Format

When setting color picker values, use `[r, g, b, 255]` format with 0-255 integers:

```python
# Helper to convert hex to DearPyGui format
def _hex_to_rgba_list(hex_str: str) -> list:
    rgb = hex_to_rgb(hex_str)  # Returns (r, g, b) tuple
    return [rgb[0], rgb[1], rgb[2], 255]

# Setting a color picker value
dpg.set_value(color_picker_tag, _hex_to_rgba_list("#FF5500"))
```

---

## JSON File Handling

### Auto-Save Pattern

For real-time saving as users edit fields:

```python
class ConfigManager:
    def set_value(self, section: str, key: str, value: Any):
        """Set value and auto-save."""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        self._notify_change()
        self.save()  # Auto-save on every change
```

### Escaping Special Characters

When generating code files (like Ren'Py .rpy files), escape special characters:

```python
def escape_for_renpy_string(text: str) -> str:
    """Escape text for use in Ren'Py string literals."""
    text = text.replace('\\', '\\\\')  # Escape backslashes first
    text = text.replace('"', '\\"')    # Escape quotes
    text = text.replace('\n', '\\n')   # Convert newlines to escape sequences
    return text

# Usage
quit_message = config.get("quit_message", "")
escaped = escape_for_renpy_string(quit_message)
output = f'define gui.QUIT = _("{escaped}")'
```

### Nullable Fields

For optional fields where 0 or empty means "use default":

```python
# In JSON: store null for "use default"
{
    "button_width": null,
    "button_height": 60
}

# In UI: display 0 for null, save 0 as null
default_value = data.get("width") or 0  # null -> 0 for display

def _make_callback_nullable(section: str, key: str):
    def callback(sender, app_data, user_data):
        value = app_data if app_data > 0 else None  # 0 -> null for storage
        config_manager.set_value(section, key, value)
    return callback
```
