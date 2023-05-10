'''
Author: Jason Ho
'''
from typing import Callable

from scripts.core.gesture import Gesture
from scripts.core.position import Position
from scripts.core.position_tracker import PositionTracker
from scripts.tools import Config


class BodyGesture(Gesture):
    def __init__(self, name: str, position_checker: Callable[[Position],bool], tracker: PositionTracker) -> None:
        print("gesture type: ", name)
        max_pos_q_size = Config().get_data("modules/body/gestures_max_pos_queue")
        super().__init__(name, position_checker, tracker, max_pos_q_size)
