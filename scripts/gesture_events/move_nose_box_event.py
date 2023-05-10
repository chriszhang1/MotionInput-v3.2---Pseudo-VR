from .simple_gesture_event import SimpleGestureEvent


class MoveNoseBoxEvent(SimpleGestureEvent):
    _bodypart_types = {"speech", "head"}

    def __init__(self, phrase : str) -> None:
        super().__init__({phrase, "nose_position_gesture"}, {phrase}, MoveNoseBoxEvent._bodypart_types)
        self._phrase = phrase
        self._gestures = {"speech": {self._phrase: None},
                          "head": {"nose_position_gesture": None}}
        self.setup_nose_box_at_startup = True

    def update(self) -> None:
        head_position = self._gestures["head"]["nose_position_gesture"].get_last_position()
        nose_position = head_position.get_landmark("nose_point")

        self._event_triggers[self._phrase](nose_position)
        self.setup_nose_box_at_startup = False
        self._state = False

    def _check_state(self) -> None:
        self._state = (self._gestures["speech"][self._phrase] is not None
                       or self.setup_nose_box_at_startup is True
                       ) and self._gestures["head"]["nose_position_gesture"] is not None
