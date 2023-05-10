'''
Authors: Samuel Emilolorun
'''
from typing import List
from .simple_gesture_event import SimpleGestureEvent


class SpeechEvent(SimpleGestureEvent):
    # TODO: docstring
    """_summary_

    [trigger types]:
    [bodypart types]:
    [gestures types]:
    """
    _bodypart_types = {"speech"}

    def __init__(self, phrase : str, hotkey_combo: List[str] = None, action_type="") -> None:
        super().__init__({phrase}, {phrase}, SpeechEvent._bodypart_types)
        self._phrase = phrase
        self._gestures = {"speech": {self._phrase: None}}
        self._hotkey_combo = hotkey_combo
        self._action_type = action_type

    def update(self) -> None:
        if self._hotkey_combo is not None:
            self._event_triggers[self._phrase](*self._hotkey_combo) # for hotkey presses
        elif self._action_type == "CustomizedGesture":
            self._event_triggers[self._phrase](self._phrase)
        else:
            self._event_triggers[self._phrase]()

    def _check_state(self) -> None:
        self._state = self._gestures["speech"][self._phrase] is not None
