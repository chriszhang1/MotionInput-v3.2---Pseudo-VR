'''
Author: Carmen Meinson
'''
import numpy as np
from scripts.tools import Config
from .simple_gesture_event import SimpleGestureEvent


class ZoomEvent(SimpleGestureEvent):
    """Zooming by holding the index pinch gesture on both hands. Zooming direction and speed according tho the change in the index finger tips distance.

    [trigger types]:
        "zoom": called every frame after frames_for_switch as long as the change in distance since the last frame is above threshold. With arguments (speed) reflecting the change in distance since last frame.
    [bodypart types]:
        "dom_hand" & "off_hand": the  distance (aka speed) is calculated from the distance between the "index_tip"s of these hands
    [gestures types]:
        "index_pinch": the current gesture used
    """
    _event_trigger_types = {"zoom"}
    _gesture_types = {"index_pinch"}
    _bodypart_types = {"dom_hand", "off_hand"}

    def __init__(self):
        self._gestures = {"dom_hand": {"index_pinch": None},
                          "off_hand": {"index_pinch": None}}

        super().__init__(ZoomEvent._gesture_types, ZoomEvent._event_trigger_types, ZoomEvent._bodypart_types)
        config = Config()
        self._n_frames_for_switch = max(2, config.get_data("events/zoom/frames_for_switch"))
        self._movement_threshold = config.get_data("events/zoom/movement_threshold")
        self._last_hands_dist = None

    def update(self):
        hands_dist = self._get_hands_dist()

        if self._get_frames_held() >= self._n_frames_for_switch:
            speed = hands_dist - self._last_hands_dist

            if abs(speed) > self._movement_threshold:
                self._event_triggers["zoom"](speed)

        self._last_hands_dist = hands_dist

    def _check_state(self):
        self._state = self._gestures["dom_hand"]["index_pinch"] is not None and self._gestures["off_hand"][
            "index_pinch"] is not None

    def _get_frames_held(self) -> int:
        hand1 = self._gestures["dom_hand"]["index_pinch"]
        hand2 = self._gestures["off_hand"]["index_pinch"]
        return min(hand1.get_frames_held(), hand2.get_frames_held())

    def _get_hands_dist(self) -> float:
        hand1 = self._gestures["dom_hand"]["index_pinch"]
        hand2 = self._gestures["off_hand"]["index_pinch"]
        pos1, pos2 = hand1.get_last_position(), hand2.get_last_position()
        index_tip1 = pos1.get_landmark("index_tip")
        index_tip2 = pos2.get_landmark("index_tip")
        fingers_dist = np.sqrt(np.sum((index_tip1 - index_tip2) ** 2))
        tot_palm_height = (pos1.get_palm_height() + pos2.get_palm_height())
        return fingers_dist * 2 / tot_palm_height
