'''
Author: Carmen Meinson
'''

from collections import deque
from time import perf_counter
from typing import Callable, List, Optional

from .position import Position
from .position_tracker import PositionTracker


# gesture represents a certain position (aka some combination of primitives) along with
# the movement of the body part throughout the time interval the position has been held.

# once initialized it is tied to 1 specific position tracker class
# and when run it checks with that specific instance if it is still active.
# this is done to support things like multiple hands in a frame
# in which case there would be 1 tracker for every hand and thus
# each gesture instance would reference 1 specific hand

class Gesture:
    def __init__(self, name: str, position_checker: Callable[[Position], bool], tracker: PositionTracker,
                 max_pos_q_size: Optional[int] = None):
        self._name = name
        self._position_checker = position_checker  # position_checker function that determines if the gesture is still active
        self._tracker = tracker  # tracker instance from which the gesture was initialized (to check if still active)
        self._time_started = perf_counter()
        if max_pos_q_size is None:
            self._positions = deque()
        else:
            self._positions = deque(maxlen=max_pos_q_size)
        self._frames_held = 0

    def update(self) -> bool:
        """Records the current Position of the body part this Gesture was created from. With that Position checks if the Gesture still remains active (if all the states of the primitives of interest are in the required states)
        (This function is intended to be called each frame until the Gesture deactivates)

        :return: The current state of the Gesture
        :rtype: bool
        """
        self._frames_held += 1
        self._positions.append(self._tracker.get_current_position())
        return self._position_checker(self._positions[-1])

    def get_name(self) -> str:
        """Returns name of represented gesture.
        
        :return: name of represented gesture
        :rtype: str
        """
        return self._name

    def get_bodypart_name(self) -> str:
        """Returns name of the body part of the represented gesture.
        
        :return: name of body part
        :rtype: str
        """
        return self._tracker.get_name()

    def get_frames_held(self) -> int:
        """Note the number of positions stored and retrievable from the gesture instance may be less then the number of frames held in case the max_pos_q_size has been reached.

        :return: number of frames the gesture as been held for
        :rtype: int
        """
        return self._frames_held

    def get_frames_stored(self) -> int:
        """Note the number of positions stored and retrievable from the gesture instance may be less then the number of frames held in case the max_pos_q_size has been reached.

        :return: number of positions stored in the gesture instance
        :rtype: int
        """
        return len(self._positions)

    def get_last_position(self) -> Position:
        return self._positions[-1]

    def get_last_n_positions(self, n: int) -> List[Position]:
        return list(self._positions)[-n:]

    def get_time_held(self) -> float:
        return perf_counter() - self._time_started

    # bunch of helper functions like dist travelled per point? time held? frames held?
