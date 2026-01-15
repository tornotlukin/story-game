"""
json_manager.py - JSON file management with undo/redo support

Handles loading, saving, and modification of preset JSON files.
Maintains undo/redo history for all changes.
"""

import json
import copy
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable


@dataclass
class UndoState:
    """Snapshot of JSON data for undo/redo."""
    transition_data: Dict
    shader_data: Dict
    description: str = ""


class JsonManager:
    """
    Manages preset JSON files with undo/redo support.

    Features:
    - Load/save JSON files
    - Auto-save on changes
    - Undo/redo stack (50 levels)
    - Change notifications
    """

    MAX_UNDO_LEVELS = 50

    def __init__(self):
        self.transition_path: str = ""
        self.shader_path: str = ""

        self.transition_data: Dict = {}
        self.shader_data: Dict = {}

        self.undo_stack: List[UndoState] = []
        self.redo_stack: List[UndoState] = []

        self._auto_save = True
        self._on_change_callbacks: List[Callable] = []

    def set_paths(self, transition_path: str, shader_path: str):
        """Set the paths to JSON files."""
        self.transition_path = transition_path
        self.shader_path = shader_path

    def load(self) -> bool:
        """Load both JSON files."""
        success = True

        if self.transition_path:
            self.transition_data = self._load_json(self.transition_path)
            if not self.transition_data:
                success = False

        if self.shader_path:
            self.shader_data = self._load_json(self.shader_path)
            if not self.shader_data:
                success = False

        # Clear undo/redo on load
        self.undo_stack.clear()
        self.redo_stack.clear()

        self._notify_change()
        return success

    def _load_json(self, filepath: str) -> Dict:
        """Load a single JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"JsonManager: File not found: {filepath}")
            return {}
        except json.JSONDecodeError as e:
            print(f"JsonManager: Invalid JSON in {filepath}: {e}")
            return {}
        except Exception as e:
            print(f"JsonManager: Error loading {filepath}: {e}")
            return {}

    def save(self) -> bool:
        """Save both JSON files."""
        success = True

        if self.transition_path and self.transition_data:
            if not self._save_json(self.transition_path, self.transition_data):
                success = False

        if self.shader_path and self.shader_data:
            if not self._save_json(self.shader_path, self.shader_data):
                success = False

        return success

    def _save_json(self, filepath: str, data: Dict) -> bool:
        """Save data to a JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"JsonManager: Error saving {filepath}: {e}")
            return False

    # =========================================================================
    # Undo/Redo
    # =========================================================================

    def push_undo(self, description: str = ""):
        """Push current state to undo stack."""
        state = UndoState(
            transition_data=copy.deepcopy(self.transition_data),
            shader_data=copy.deepcopy(self.shader_data),
            description=description
        )
        self.undo_stack.append(state)

        # Limit stack size
        if len(self.undo_stack) > self.MAX_UNDO_LEVELS:
            self.undo_stack.pop(0)

        # Clear redo stack on new change
        self.redo_stack.clear()

    def undo(self) -> bool:
        """Undo last change. Returns True if successful."""
        if not self.undo_stack:
            return False

        # Push current state to redo
        current = UndoState(
            transition_data=copy.deepcopy(self.transition_data),
            shader_data=copy.deepcopy(self.shader_data)
        )
        self.redo_stack.append(current)

        # Restore previous state
        prev = self.undo_stack.pop()
        self.transition_data = prev.transition_data
        self.shader_data = prev.shader_data

        if self._auto_save:
            self.save()

        self._notify_change()
        return True

    def redo(self) -> bool:
        """Redo last undone change. Returns True if successful."""
        if not self.redo_stack:
            return False

        # Push current state to undo
        current = UndoState(
            transition_data=copy.deepcopy(self.transition_data),
            shader_data=copy.deepcopy(self.shader_data)
        )
        self.undo_stack.append(current)

        # Restore redo state
        next_state = self.redo_stack.pop()
        self.transition_data = next_state.transition_data
        self.shader_data = next_state.shader_data

        if self._auto_save:
            self.save()

        self._notify_change()
        return True

    @property
    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0

    @property
    def undo_count(self) -> int:
        return len(self.undo_stack)

    @property
    def redo_count(self) -> int:
        return len(self.redo_stack)

    # =========================================================================
    # Transition Presets
    # =========================================================================

    def get_transition_names(self) -> List[str]:
        """Get list of transition preset names (excluding comments)."""
        presets = self.transition_data.get("presets", {})
        if not presets:
            return []
        return [k for k in presets.keys() if k and not k.startswith("_")]

    def get_transition(self, name: str) -> Optional[Dict]:
        """Get a transition preset by name."""
        return self.transition_data.get("presets", {}).get(name)

    def set_transition(self, name: str, data: Dict, push_undo: bool = True):
        """Set/update a transition preset."""
        if push_undo:
            self.push_undo(f"Edit transition: {name}")

        if "presets" not in self.transition_data:
            self.transition_data["presets"] = {}

        self.transition_data["presets"][name] = data

        if self._auto_save:
            self.save()
        self._notify_change()

    def add_transition(self, name: str, data: Dict):
        """Add a new transition preset."""
        self.push_undo(f"Add transition: {name}")

        if "presets" not in self.transition_data:
            self.transition_data["presets"] = {}

        self.transition_data["presets"][name] = data

        if self._auto_save:
            self.save()
        self._notify_change()

    def delete_transition(self, name: str):
        """Delete a transition preset."""
        if name in self.transition_data.get("presets", {}):
            self.push_undo(f"Delete transition: {name}")
            del self.transition_data["presets"][name]

            if self._auto_save:
                self.save()
            self._notify_change()

    def delete_transitions(self, names: List[str]):
        """Delete multiple transition presets."""
        if not names:
            return

        self.push_undo(f"Delete {len(names)} transitions")

        for name in names:
            if name in self.transition_data.get("presets", {}):
                del self.transition_data["presets"][name]

        if self._auto_save:
            self.save()
        self._notify_change()

    def rename_transition(self, old_name: str, new_name: str) -> bool:
        """Rename a transition preset."""
        presets = self.transition_data.get("presets", {})
        if old_name not in presets or new_name in presets:
            return False

        self.push_undo(f"Rename transition: {old_name} -> {new_name}")

        presets[new_name] = presets.pop(old_name)

        if self._auto_save:
            self.save()
        self._notify_change()
        return True

    def duplicate_transition(self, name: str, new_name: str) -> bool:
        """Duplicate a transition preset."""
        presets = self.transition_data.get("presets", {})
        if name not in presets:
            return False

        self.push_undo(f"Duplicate transition: {name}")

        presets[new_name] = copy.deepcopy(presets[name])

        if self._auto_save:
            self.save()
        self._notify_change()
        return True

    def move_transition(self, name: str, direction: str) -> bool:
        """
        Move a transition in the list order.

        direction: 'top', 'up', 'down', 'bottom'
        """
        names = self.get_transition_names()
        if name not in names:
            return False

        idx = names.index(name)

        if direction == 'top' and idx > 0:
            names.remove(name)
            names.insert(0, name)
        elif direction == 'up' and idx > 0:
            names[idx], names[idx - 1] = names[idx - 1], names[idx]
        elif direction == 'down' and idx < len(names) - 1:
            names[idx], names[idx + 1] = names[idx + 1], names[idx]
        elif direction == 'bottom' and idx < len(names) - 1:
            names.remove(name)
            names.append(name)
        else:
            return False

        self.push_undo(f"Move transition {direction}: {name}")
        self._reorder_transitions(names)

        if self._auto_save:
            self.save()
        self._notify_change()
        return True

    def _reorder_transitions(self, new_order: List[str]):
        """Reorder transitions to match the given list."""
        old_presets = self.transition_data.get("presets", {})
        new_presets = {}

        # Preserve comment keys at the beginning
        for key in old_presets:
            if key.startswith("_"):
                new_presets[key] = old_presets[key]

        # Add presets in new order
        for name in new_order:
            if name in old_presets:
                new_presets[name] = old_presets[name]

        self.transition_data["presets"] = new_presets

    # =========================================================================
    # Shader Presets
    # =========================================================================

    def get_shader_names(self) -> List[str]:
        """Get list of shader preset names (excluding comments)."""
        presets = self.shader_data.get("shader_presets", {})
        if not presets:
            return []
        return [k for k in presets.keys() if k and not k.startswith("_")]

    def get_shader(self, name: str) -> Optional[Dict]:
        """Get a shader preset by name."""
        return self.shader_data.get("shader_presets", {}).get(name)

    def set_shader(self, name: str, data: Dict, push_undo: bool = True):
        """Set/update a shader preset."""
        if push_undo:
            self.push_undo(f"Edit shader: {name}")

        if "shader_presets" not in self.shader_data:
            self.shader_data["shader_presets"] = {}

        self.shader_data["shader_presets"][name] = data

        if self._auto_save:
            self.save()
        self._notify_change()

    def add_shader(self, name: str, data: Dict):
        """Add a new shader preset."""
        self.push_undo(f"Add shader: {name}")

        if "shader_presets" not in self.shader_data:
            self.shader_data["shader_presets"] = {}

        self.shader_data["shader_presets"][name] = data

        if self._auto_save:
            self.save()
        self._notify_change()

    def delete_shader(self, name: str):
        """Delete a shader preset."""
        if name in self.shader_data.get("shader_presets", {}):
            self.push_undo(f"Delete shader: {name}")
            del self.shader_data["shader_presets"][name]

            if self._auto_save:
                self.save()
            self._notify_change()

    def delete_shaders(self, names: List[str]):
        """Delete multiple shader presets."""
        if not names:
            return

        self.push_undo(f"Delete {len(names)} shaders")

        for name in names:
            if name in self.shader_data.get("shader_presets", {}):
                del self.shader_data["shader_presets"][name]

        if self._auto_save:
            self.save()
        self._notify_change()

    def rename_shader(self, old_name: str, new_name: str) -> bool:
        """Rename a shader preset."""
        presets = self.shader_data.get("shader_presets", {})
        if old_name not in presets or new_name in presets:
            return False

        self.push_undo(f"Rename shader: {old_name} -> {new_name}")

        presets[new_name] = presets.pop(old_name)

        if self._auto_save:
            self.save()
        self._notify_change()
        return True

    def duplicate_shader(self, name: str, new_name: str) -> bool:
        """Duplicate a shader preset."""
        presets = self.shader_data.get("shader_presets", {})
        if name not in presets:
            return False

        self.push_undo(f"Duplicate shader: {name}")

        presets[new_name] = copy.deepcopy(presets[name])

        if self._auto_save:
            self.save()
        self._notify_change()
        return True

    def move_shader(self, name: str, direction: str) -> bool:
        """Move a shader in the list order."""
        names = self.get_shader_names()
        if name not in names:
            return False

        idx = names.index(name)

        if direction == 'top' and idx > 0:
            names.remove(name)
            names.insert(0, name)
        elif direction == 'up' and idx > 0:
            names[idx], names[idx - 1] = names[idx - 1], names[idx]
        elif direction == 'down' and idx < len(names) - 1:
            names[idx], names[idx + 1] = names[idx + 1], names[idx]
        elif direction == 'bottom' and idx < len(names) - 1:
            names.remove(name)
            names.append(name)
        else:
            return False

        self.push_undo(f"Move shader {direction}: {name}")
        self._reorder_shaders(names)

        if self._auto_save:
            self.save()
        self._notify_change()
        return True

    def _reorder_shaders(self, new_order: List[str]):
        """Reorder shaders to match the given list."""
        old_presets = self.shader_data.get("shader_presets", {})
        new_presets = {}

        # Preserve comment keys
        for key in old_presets:
            if key.startswith("_"):
                new_presets[key] = old_presets[key]

        # Add presets in new order
        for name in new_order:
            if name in old_presets:
                new_presets[name] = old_presets[name]

        self.shader_data["shader_presets"] = new_presets

    # =========================================================================
    # Change Notifications
    # =========================================================================

    def on_change(self, callback: Callable):
        """Register a callback for data changes."""
        self._on_change_callbacks.append(callback)

    def _notify_change(self):
        """Notify all registered callbacks of a change."""
        for callback in self._on_change_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"JsonManager: Callback error: {e}")

    # =========================================================================
    # Utility
    # =========================================================================

    def get_unique_transition_name(self, base: str = "new_preset") -> str:
        """Generate a unique transition preset name."""
        existing = self.get_transition_names()
        name = base
        counter = 1
        while name in existing:
            name = f"{base}_{counter}"
            counter += 1
        return name

    def get_unique_shader_name(self, base: str = "new_shader") -> str:
        """Generate a unique shader preset name."""
        existing = self.get_shader_names()
        name = base
        counter = 1
        while name in existing:
            name = f"{base}_{counter}"
            counter += 1
        return name
