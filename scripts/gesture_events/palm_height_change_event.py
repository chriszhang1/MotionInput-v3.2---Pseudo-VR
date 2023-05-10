'''
Author: Carmen Meinson
'''
from scripts.tools import Config
from .simple_gesture_event import SimpleGestureEvent


class PalmHeightChangeEvent(SimpleGestureEvent):
    """
    Palm height level is an array where each element represents the lower bound of the range so if the possible ranges for the levels were [0, 12), [12, 23), [23, inf) the array would be [0,12,23]
    in the legacy code [0, 0.18-0.075, 0.18-0.25] lower the level the further the hand is from the camera

    [trigger types]:
        "level_change": called when the palm height has been in a size bracket from different from active_level for frames_for_switch frames
    [bodypart types]:
        "hand": the hand on which we track the gesure of interest
    [gestures types]:
        "facing_camera": the palm height levels change only when the hand is facing the camera.
    """
    _event_trigger_types = {"level_change"}
    _gesture_types = {"facing_camera"}
    _bodypart_types = {"hand"}

    def __init__(self, active_level=None):
        self._gestures = {"hand": {"facing_camera": None}}
        super().__init__(PalmHeightChangeEvent._gesture_types, PalmHeightChangeEvent._event_trigger_types,
                         PalmHeightChangeEvent._bodypart_types)
        config = Config()
        self._palm_height_levels = config.get_data("events/palm_height_change/levels")
        self._n_frames_for_switch = config.get_data("events/palm_height_change/frames_for_switch")

        self._active_level = active_level
        self._prev_level = active_level
        self._frame_count = 0

    def set_up(self) -> None:
        """sets the aoi level to either active_level that was given as an arg on initialization or to the level 0 in order for it to be displayed
        """
        if self._active_level is None:
            self._event_triggers["level_change"](0)  # TODO: do we define the default aoi size?
        else:
            self._event_triggers["level_change"](self._active_level)

    def update(self):
        level = self._get_level()
        if (not self._state) or self._active_level == level:
            self._frame_count = 0
            return

        if self._prev_level != level:
            self._frame_count = 0

        self._frame_count += 1
        if self._frame_count == self._n_frames_for_switch:
            self._event_triggers["level_change"](level)
            self._active_level = level

        self._prev_level = level

    def force_deactivate(self) -> None:
        self._event_triggers["level_change"]()

    def _check_state(self) -> None:
        self._state = self._gestures["hand"]["facing_camera"] is not None

    # returns -1 if out of range
    def _get_level(self) -> bool:
        hand_position = self._gestures["hand"]["facing_camera"].get_last_position()
        palm_height = hand_position.get_palm_height()
        for i, lower_bound in enumerate(self._palm_height_levels):
            if palm_height < lower_bound:
                return i - 1
        return len(self._palm_height_levels) - 1
