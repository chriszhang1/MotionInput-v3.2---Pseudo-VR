"""
Author: Andrzej Szablewski
"""
from .simple_gesture_event import SimpleGestureEvent


class NoseTrackingEvent(SimpleGestureEvent):
    """Nose tracking event. Active if face can be detected. Maps nosepoint
    position to the screen coordinate and moves mouse cursor in that direction.

    [trigger types]:
        "move": maps normalized position to screen coordinates and moves
        mouse cursor there.
    [bodypart types]:
        "head"
    [gestures types]:
        "nose_position_gesture": gesture always active when face is detected
        and nosepoint position is available
    """
    _event_trigger_types = {"move", "level_change"}
    _gesture_types = {"nose_position_gesture"}
    _bodypart_types = {"head"}

    def __init__(self):
        super().__init__(NoseTrackingEvent._gesture_types,
                         NoseTrackingEvent._event_trigger_types,
                         NoseTrackingEvent._bodypart_types)
        self._gestures = {"head": {"nose_position_gesture": None}}

    def update(self):
        head_position = \
            self._gestures["head"]["nose_position_gesture"].get_last_position()
        nose_position = head_position.get_landmark("nose_point")

        self._event_triggers["move"](nose_position[0], nose_position[1])

    def force_deactivate(self) -> None:
        self._event_triggers["level_change"]()


    def _check_state(self) -> None:
        self._state = \
            self._gestures["head"]["nose_position_gesture"] is not None
