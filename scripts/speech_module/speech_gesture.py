'''
Author: Carmen Meinson
'''
from typing import Callable
from scripts.core import PositionTracker, Position, Gesture


class SpeechGesture(Gesture):
    def __init__(self, name: str, position_checker: Callable[[Position], bool], tracker: PositionTracker) -> None:
        super().__init__(name, position_checker, tracker)

    def update(self) -> bool:
        """Records the current Position of the speech bodypart the speechGesture was created from.

          :return: The current state of the Gesture
          :rtype: bool
        """
        self._frames_held += 1
        self._positions.append(self._tracker.get_current_position())
        # as the speech gesture (aka the phrase said) should be active only 1 frame:
        return 1 == self.get_frames_held()
