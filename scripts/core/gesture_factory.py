'''
Author: Carmen Meinson
'''

from collections import namedtuple
from typing import Set, Optional, Type

from .gesture import Gesture
from .position import Position
from .position_tracker import PositionTracker

Primitive = namedtuple('Primitive', ['name', 'state'])  # Set[Tuple[str, boolean]]


# Every gesture factory instance is generated from a set of (String,Bool) pairs that describe the gesture
# The factory creates a gesture instance if the conditions (truth values of all primitives) are met

class GestureFactory:
    def __init__(self, name: str, gesture_class: Type[Gesture], primitives: Set[Primitive]) -> None:
        self._primitives = primitives
        self._gesture_class = gesture_class
        self._name = name

    def update(self, tracker: PositionTracker) -> Optional[Gesture]:
        """Creates an instance of the gesture it represents if the current position in the provided tracker matches the gesture criteria (if all the primitives of interest are in needed states)

        :param tracker: tracker containing the current position to be checked
        :type tracker: PositionTracker
        :return: a new gesture instance if such is created
        :rtype: Optional[Gesture]
        """
        if self._check_position(tracker.get_current_position()):
            return self._gesture_class(self._name, self._check_position, tracker)
        return None

    def get_name(self) -> str:
        return self._name

    def _check_position(self, position: Position) -> bool:
        # if all primitives match or if no primitives were defined, returns true!
        if position is None: return False
        for primitive in self._primitives:
            if position.get_primitive(primitive.name) != primitive.state:
                return False
        return True
