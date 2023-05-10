"""
Author: Radu-Bogdan Priboi
Contributors: Andrzej Szablewski
"""
from scripts.tools import Config
from .simple_gesture_event import SimpleGestureEvent


class NoseScrollEvent(SimpleGestureEvent):
    """Scrolling by smiling and moving the nose up (to scroll up) or
    down (to scroll down). Scrolling speed is proportional to the distance
    from the tip of the nose to the centre.

    [trigger types]:
        "scroll": called every frame after frames_for_switch as long as
        the speed is above threshold. With arguments (speed) reflecting
        the distance from the nose tip to the centre.
    [bodypart types]:
        "head"
    [gestures types]:
        "nose_scroll_up_gesture" & "nose_scroll_down_gesture": gestures
        activated when smiling is detected and nose tip is up/down
    """
    _event_trigger_types = {"scroll"}
    _bodypart_types = {"head"}
    _gesture_types = {"nose_scroll_up_gesture", "nose_scroll_down_gesture"}

    def __init__(self):
        super().__init__(NoseScrollEvent._gesture_types,
                         NoseScrollEvent._event_trigger_types,
                         NoseScrollEvent._bodypart_types)
        self.config = Config()
        self._n_frames_for_switch = self.config.get_data("events/nose_scroll/frames_for_switch")
        self._change_direction = self.config.get_data("events/nose_scroll/change_direction")
        self._gestures = {
            "head": {
                "nose_scroll_up_gesture": None,
                "nose_scroll_down_gesture": None
            }
        }

    def update(self):
        if self._gestures["head"][self._get_active_gesture()].get_frames_held() < self._n_frames_for_switch:
            return

        y_nosebox_center = self.config.get_data("events/nose_tracking/nose_box_centre_Y")
        speed = (self._get_nose_yposition() - y_nosebox_center) * self._change_direction

        if abs(speed) < 0.05:
            return

        self._event_triggers["scroll"](speed)

    def _check_state(self) -> None:
        gesture_list = [
            False if gesture is None else True
            for gesture in self._gestures["head"].values()
        ]
        self._state = True in gesture_list

    def _get_nose_yposition(self) -> float:
        y = self._gestures["head"][self._get_active_gesture()].get_last_position().get_landmark("nose_point")[1]
        return y

    def _get_active_gesture(self) -> str:
        if self._gestures["head"]["nose_scroll_up_gesture"] is not None:
            return "nose_scroll_up_gesture"
        else:
            return "nose_scroll_down_gesture"
