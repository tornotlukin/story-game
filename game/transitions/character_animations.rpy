## character_animations.rpy - Character entrance/exit transform factory
##
## Creates callable transforms from JSON configuration for character
## entrances and exits with movement, fade, scale, and rotation.
## Transforms accept position parameters (xalign, yalign, etc.)
##
## Usage:
##     show character at slide_left_enter(xalign=0.5, yalign=1.0)
##     show character at rise_up_enter(xalign=0.3, yalign=1.0)
##
## Related files: transition_loader.rpy, transitions.json

init -3 python:

    def get_direction_offsets(direction, offset):
        """
        Calculate x/y offsets based on direction.
        Returns offsets to ADD to starting position.

        Args:
            direction: Direction string (left, right, top, bottom, corners)
            offset: Pixel distance

        Returns:
            Tuple of (xoffset, yoffset)
        """
        directions = {
            "left": (-offset, 0),
            "right": (offset, 0),
            "top": (0, -offset),
            "bottom": (0, offset),
            "top_left": (-offset, -offset),
            "top_right": (offset, -offset),
            "bottom_left": (-offset, offset),
            "bottom_right": (offset, offset),
        }
        return directions.get(direction, (0, 0))

    def get_easing_function(easing_name):
        """
        Get Ren'Py warper function from name.
        """
        easings = {
            "linear": None,
            "ease": _warper.ease,
            "ease_in": _warper.easein,
            "ease_out": _warper.easeout,
            "easein": _warper.easein,
            "easeout": _warper.easeout,
        }
        return easings.get(easing_name)

    def play_transition_sound(sound, volume, delay):
        """
        Play a sound effect for a transition.
        Uses renpy.music.play with sound channel and relative_volume.
        """
        if sound is None:
            return

        def _play():
            renpy.music.play(sound, channel='sound', loop=False, relative_volume=volume)

        if delay > 0:
            # For delayed sounds, we can't easily delay in a transform
            # So we just play immediately (delay handled by animation timing)
            _play()
        else:
            _play()


init -2 python:

    class CharacterAnimationFactory:
        """
        Factory for creating callable character entrance/exit transforms
        from JSON configuration. Transforms accept position parameters.
        """

        def __init__(self):
            self._transforms = {}

        def create_entrance_function(self, name, config):
            """
            Create a callable entrance transform function.

            Returns a function that takes position params and returns a Transform.
            """
            # Extract config values
            direction = config.get("direction", "left")
            offset = config.get("offset", 200)
            duration = config.get("duration", 0.4)
            delay = config.get("delay", 0)
            easing = config.get("easing", "ease_out")
            fade = config.get("fade", True)
            start_alpha = config.get("start_alpha", 0.0)
            end_alpha = config.get("end_alpha", 1.0)
            use_scale = config.get("scale", False)
            start_scale = config.get("start_scale", 1.0)
            end_scale = config.get("end_scale", 1.0)
            rotate_amount = config.get("rotate", 0)
            sound = config.get("sound")
            sound_volume = config.get("sound_volume", 0.8)
            sound_delay = config.get("sound_delay", 0)

            dir_xoff, dir_yoff = get_direction_offsets(direction, offset)
            easing_func = get_easing_function(easing)

            def entrance_transform(xalign=0.5, yalign=1.0, xanchor=0.5, yanchor=1.0):
                """
                Returns a transform that animates entrance to the specified position.

                Args:
                    xalign: Final horizontal alignment (0.0=left, 0.5=center, 1.0=right)
                    yalign: Final vertical alignment (0.0=top, 0.5=center, 1.0=bottom)
                    xanchor: Horizontal anchor point on the image
                    yanchor: Vertical anchor point on the image
                """
                # Track if sound has played
                sound_played = [False]

                def transform_function(trans, st, at):
                    # Play sound on first frame
                    if not sound_played[0] and sound:
                        play_transition_sound(sound, sound_volume, sound_delay)
                        sound_played[0] = True

                    # Handle delay
                    if st < delay:
                        trans.xalign = xalign
                        trans.yalign = yalign
                        trans.xanchor = xanchor
                        trans.yanchor = yanchor
                        trans.xoffset = dir_xoff
                        trans.yoffset = dir_yoff
                        if fade:
                            trans.alpha = start_alpha
                        if use_scale:
                            trans.zoom = start_scale
                        if rotate_amount != 0:
                            trans.rotate = rotate_amount
                        return 0

                    # Calculate progress
                    effective_st = st - delay
                    progress = min(1.0, effective_st / duration) if duration > 0 else 1.0

                    # Apply easing
                    eased_progress = progress
                    if easing_func and progress < 1.0:
                        eased_progress = easing_func(progress)

                    # Set final position (anchors)
                    trans.xalign = xalign
                    trans.yalign = yalign
                    trans.xanchor = xanchor
                    trans.yanchor = yanchor

                    # Animate offset from direction to zero
                    trans.xoffset = dir_xoff * (1.0 - eased_progress)
                    trans.yoffset = dir_yoff * (1.0 - eased_progress)

                    # Animate alpha
                    if fade:
                        trans.alpha = start_alpha + (end_alpha - start_alpha) * eased_progress

                    # Animate scale
                    if use_scale:
                        trans.zoom = start_scale + (end_scale - start_scale) * eased_progress

                    # Animate rotation
                    if rotate_amount != 0:
                        trans.rotate = rotate_amount * (1.0 - eased_progress)

                    # Continue or finish
                    if progress >= 1.0:
                        return None
                    return 0

                return Transform(function=transform_function)

            return entrance_transform

        def create_exit_function(self, name, config):
            """
            Create a callable exit transform function.

            Returns a function that takes position params and returns a Transform.
            """
            direction = config.get("direction", "left")
            offset = config.get("offset", 150)
            duration = config.get("duration", 0.3)
            delay = config.get("delay", 0)
            easing = config.get("easing", "ease_in")
            fade = config.get("fade", True)
            start_alpha = config.get("start_alpha", 1.0)
            end_alpha = config.get("end_alpha", 0.0)
            use_scale = config.get("scale", False)
            start_scale = config.get("start_scale", 1.0)
            end_scale = config.get("end_scale", 1.0)
            rotate_amount = config.get("rotate", 0)
            sound = config.get("sound")
            sound_volume = config.get("sound_volume", 0.8)
            sound_delay = config.get("sound_delay", 0)

            dir_xoff, dir_yoff = get_direction_offsets(direction, offset)
            easing_func = get_easing_function(easing)

            def exit_transform(xalign=0.5, yalign=1.0, xanchor=0.5, yanchor=1.0):
                """
                Returns a transform that animates exit from the specified position.

                Args:
                    xalign: Starting horizontal alignment
                    yalign: Starting vertical alignment
                    xanchor: Horizontal anchor point on the image
                    yanchor: Vertical anchor point on the image
                """
                sound_played = [False]

                def transform_function(trans, st, at):
                    # Play sound on first frame
                    if not sound_played[0] and sound:
                        play_transition_sound(sound, sound_volume, sound_delay)
                        sound_played[0] = True

                    # Handle delay
                    if st < delay:
                        trans.xalign = xalign
                        trans.yalign = yalign
                        trans.xanchor = xanchor
                        trans.yanchor = yanchor
                        trans.xoffset = 0
                        trans.yoffset = 0
                        if fade:
                            trans.alpha = start_alpha
                        if use_scale:
                            trans.zoom = start_scale
                        trans.rotate = 0
                        return 0

                    # Calculate progress
                    effective_st = st - delay
                    progress = min(1.0, effective_st / duration) if duration > 0 else 1.0

                    # Apply easing
                    eased_progress = progress
                    if easing_func and progress < 1.0:
                        eased_progress = easing_func(progress)

                    # Set position (anchors)
                    trans.xalign = xalign
                    trans.yalign = yalign
                    trans.xanchor = xanchor
                    trans.yanchor = yanchor

                    # Animate offset from zero to direction
                    trans.xoffset = dir_xoff * eased_progress
                    trans.yoffset = dir_yoff * eased_progress

                    # Animate alpha
                    if fade:
                        trans.alpha = start_alpha + (end_alpha - start_alpha) * eased_progress

                    # Animate scale
                    if use_scale:
                        trans.zoom = start_scale + (end_scale - start_scale) * eased_progress

                    # Animate rotation
                    if rotate_amount != 0:
                        trans.rotate = rotate_amount * eased_progress

                    # Continue or finish
                    if progress >= 1.0:
                        return None
                    return 0

                return Transform(function=transform_function)

            return exit_transform

        def register_all_transforms(self):
            """
            Load all transitions from config and register them as callable functions.
            """
            if not transition_loader.is_loaded():
                print("CharacterAnimationFactory: TransitionLoader not loaded")
                return

            for name in transition_loader.get_all_transitions():
                config = transition_loader.get_transition(name)
                if config is None:
                    continue

                trans_type = config.get("type")

                if trans_type == "entrance":
                    func = self.create_entrance_function(name, config)
                    setattr(store, name, func)
                    self._transforms[name] = func

                elif trans_type == "exit":
                    func = self.create_exit_function(name, config)
                    setattr(store, name, func)
                    self._transforms[name] = func

            print(f"CharacterAnimationFactory: Registered {len(self._transforms)} transforms")

        def get_transform(self, name):
            """Get a registered transform function by name."""
            return self._transforms.get(name)


# Global factory instance and registration
init 1 python:
    char_anim_factory = CharacterAnimationFactory()
    char_anim_factory.register_all_transforms()
