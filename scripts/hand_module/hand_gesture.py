'''
Author: Carmen Meinson
'''

from typing import Callable

from scripts.core import PositionTracker, Position, Gesture
from scripts.tools import Config


class HandGesture(Gesture):
    def __init__(self, name: str, position_checker: Callable[[Position], bool], tracker: PositionTracker) -> None:
        max_pos_q_size = Config().get_data("modules/hand/gestures_max_pos_queue")
        super().__init__(name, position_checker, tracker, max_pos_q_size)

    # bunch of functions like dist travelled per point? time held? frames held?
