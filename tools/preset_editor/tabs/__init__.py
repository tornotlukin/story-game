"""
tabs/ - UI tab modules for the preset editor

Each tab is self-contained with its own refresh functions and callbacks.
"""

from .transition_tab import (
    init_transition_tab,
    setup_transition_tab,
    refresh_transition_ui,
    refresh_transition_manager,
    refresh_transition_builder,
    refresh_transition_json,
    switch_transition_mode,
    add_new_transition,
)

from .shader_tab import (
    init_shader_tab,
    setup_shader_tab,
    refresh_shader_ui,
    refresh_shader_manager,
    refresh_shader_builder,
    refresh_shader_json,
    switch_shader_mode,
    add_new_shader,
)

from .textshader_tab import (
    init_textshader_tab,
    setup_textshader_tab,
    refresh_textshader_ui,
    refresh_textshader_manager,
    refresh_textshader_builder,
    refresh_textshader_json,
    switch_textshader_mode,
    add_new_textshader,
)

from .demo_tab import (
    init_demo_tab,
    setup_demo_tab,
    refresh_demo_tab,
)

from .gameconfig_tab import (
    init_gameconfig_tab,
    setup_gameconfig_tab,
    refresh_gameconfig_tab,
    show_output_window,
)

__all__ = [
    # Transition
    'init_transition_tab',
    'setup_transition_tab',
    'refresh_transition_ui',
    'refresh_transition_manager',
    'refresh_transition_builder',
    'refresh_transition_json',
    'switch_transition_mode',
    'add_new_transition',
    # Shader
    'init_shader_tab',
    'setup_shader_tab',
    'refresh_shader_ui',
    'refresh_shader_manager',
    'refresh_shader_builder',
    'refresh_shader_json',
    'switch_shader_mode',
    'add_new_shader',
    # Text Shader
    'init_textshader_tab',
    'setup_textshader_tab',
    'refresh_textshader_ui',
    'refresh_textshader_manager',
    'refresh_textshader_builder',
    'refresh_textshader_json',
    'switch_textshader_mode',
    'add_new_textshader',
    # Demo
    'init_demo_tab',
    'setup_demo_tab',
    'refresh_demo_tab',
    # Game Config
    'init_gameconfig_tab',
    'setup_gameconfig_tab',
    'refresh_gameconfig_tab',
    'show_output_window',
]
