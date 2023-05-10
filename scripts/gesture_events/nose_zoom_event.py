"""
Author: Radu-Bogdan Priboi
Contributors: Andrzej Szablewski
"""
from scripts.tools import Config
from .simple_gesture_event import SimpleGestureEvent


class NoseZoomEvent(SimpleGestureEvent):
    """Zooming by doing a fishface and moving the nose to left (to zoom in) or
    right (to zoom out). Zooming speed is proportional to the distance from
    the tip of the nose to the centre.

    [trigger types]:
        "zoom": called every frame after frames_for_switch as long as
        the speed is above threshold. With arguments (speed) reflecting
        the distance from the nose tip to the centre.
    [bodypart types]:
        "head"
    [gestures types]:
        "nose_zoom_in_gesture" & "nose_zoom_out_gesture": gestures activated
         when fishface is detected and nose tip to left/right
    """
    _event_trigger_types = {"zoom"}
    _bodypart_types = {"head"}
    _gesture_types = {"nose_zoom_in_gesture", "nose_zoom_out_gesture"}

    def __init__(self):
        super().__init__(NoseZoomEvent._gesture_types,
                         NoseZoomEvent._event_trigger_types,
                         NoseZoomEvent._bodypart_types)
        config = Config()
        self._n_frames_for_switch = max(
            2,
            config.get_data("events/zoom/frames_for_switch")
        )
        self._gestures = {
            "head": {
                "nose_zoom_in_gesture": None,
                "nose_zoom_out_gesture": None
            }
        }

    def update(self):
        if self._gestures["head"][self._get_active_gesture()].get_frames_held() < self._n_frames_for_switch:
            return

        speed = (self._get_nose_xposition() - 0.5)

        if abs(speed) < 0.05:
            return

        self._event_triggers["zoom"](speed)

    def _check_state(self) -> None:
        gesture_list = [
            False if gesture is None else True
            for gesture in self._gestures["head"].values()
        ]
        self._state = True in gesture_list

    def _get_nose_xposition(self) -> float:
        x = self._gestures["head"][self._get_active_gesture()].get_last_position().get_landmark("nose_point")[0]
        return x

    def _get_active_gesture(self) -> str:
        if self._gestures["head"]["nose_zoom_in_gesture"] is not None:
            return "nose_zoom_in_gesture"
        else:
            return "nose_zoom_out_gesture"
