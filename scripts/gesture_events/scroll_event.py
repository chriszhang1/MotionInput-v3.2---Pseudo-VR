'''
Author: Carmen Meinson
'''
from typing import List

from scripts.core import Position
from scripts.tools import Config
from .simple_gesture_event import SimpleGestureEvent


class ScrollEvent(SimpleGestureEvent):
    """Scrolling by holding up middle and index finger. Scrolling speed and direction determined by the distance on y axis between the tip and the upper joint of the middle finger. 

    [trigger types]:
        "scroll": called every frame after frames_for_switch as long as the change in distance since the last frame is above threshold and the distance between the middle and index finger tips are below the threshold. With arguments (speed) reflecting the change in distance since last frame.
    [bodypart types]:
        "hand": the hand to scroll with
    [gestures types]:
        "scroll": the current gesure used
    """
    _event_trigger_types = {"scroll"}
    _gesture_types = {"scroll"}  # TODO: in the v2 there was also the requirement of the thumb being close to the pinky. do we add it back?
    _bodypart_types = {"hand"}

    def __init__(self):
        self._gestures = {"hand": {"scroll": None}}
        super().__init__(ScrollEvent._gesture_types, ScrollEvent._event_trigger_types, ScrollEvent._bodypart_types)
        config = Config()
        self._threshold = config.get_data("events/scroll/index_middle_distance_threshold")
        self._movement_threshold = config.get_data("events/scroll/movement_threshold")
        self._n_frames_for_switch = config.get_data("events/scroll/frames_for_switch")

    def update(self):
        if self._gestures["hand"][
            "scroll"].get_frames_held() < self._n_frames_for_switch or not self._index_middle_together():
            return

        speed = self._get_tip_and_upperj_diff() + 0.15  # TODO: needs better configuration. maybe map the dist to like parabolic speed

        if abs(speed) < self._movement_threshold: return

        self._event_triggers["scroll"](speed)

    def _get_avg_index_tip_y(self, positions: List[Position]) -> float:
        # can be optimized by not dividing both averages and also by using prev data for each frame
        sum = 0
        for position in positions:
            sum += position.get_landmark("index_tip")[1]
        return sum / len(positions)

    def _check_state(self) -> None:
        self._state = self._gestures["hand"]["scroll"] is not None

    def _index_middle_together(self) -> bool:
        position = self._gestures["hand"]["scroll"].get_last_position()
        index_middle_dist = position.get_landmarks_distance("index_tip", "middle_tip")
        palm_height = position.get_palm_height()
        return index_middle_dist / palm_height < self._threshold

    def _get_tip_and_upperj_diff(self) -> float:
        tip = self._gestures["hand"]["scroll"].get_last_position().get_landmark("middle_tip")
        joint = self._gestures["hand"]["scroll"].get_last_position().get_landmark("middle_upperj")
        palm_height = self._gestures["hand"]["scroll"].get_last_position().get_palm_height()
        return (tip[1] - joint[1]) / palm_height
