"""
Author: Radu-Bogdan Priboi
Contributors: Andrzej Szablewski
"""
from scripts.tools import Config
from .simple_gesture_event import SimpleGestureEvent


class HeadGestureTriggerEvent(SimpleGestureEvent):
    """
    Left Clicking/Pressing when mouth is opened. Currently as there is no
    logic of how to decide if a press or a click should be started.
    Right Clicking is triggers by smiling and Double Clicking by
    raising eyebrows.

    [trigger types]:
        “click”: called once when the gesture of interest becomes active;
        “press”: called when the gesture of interest becomes
                 active IF the “click” trigger type was not defined;
        “release”: called when the gesture of interest becomes unactive
    [bodypart types]:
        "head"
    [gestures types]:
        "smiling_gesture" & "open_mouth_gesture" & "raise_eye_brow_gesture"
    """
    _event_trigger_types = {"click", "press", "release"}
    _bodypart_types = {"head"}

    def __init__(self, gesture_types) -> None:
        super().__init__(gesture_types,
                         HeadGestureTriggerEvent._event_trigger_types,
                         HeadGestureTriggerEvent._bodypart_types)
        self._click_held = False
        config = Config()
        self.trigger_count = 1
        self.current_count = 0
        self._already_triggered = False
        if len(self._gesture_types) != 1:
            raise RuntimeError(
                "invalid _gesture_types given to "
                "the child class of the HeadGestureTriggerEvent")
        self._gesture_type = next(iter(self._gesture_types))

    def _check_state(self) -> None:
        self._state = (
            self._gestures["head"][self._gesture_type] is not None
        ) or self._click_held

    def update(self):
        if self._state and not self._click_held:
            self.current_count = self.current_count + 1
            if self.current_count == self.trigger_count:
                self._click_held = True
                # trigger the click
                if self._event_triggers["click"] is not None:
                    self._event_triggers["click"]()  # TODO: PRESS&CLICK LOGIC
                elif self._event_triggers["press"] is not None:
                    self._event_triggers["press"]()
        if self._click_held:
            if self._gestures["head"][self._gesture_type] is None:
                self._click_held = False
                self._state = False
                self.current_count = 0
                if self._event_triggers["release"] is not None:
                    self._event_triggers["release"]()


class SmilingEvent(HeadGestureTriggerEvent):
    _gesture_types = {"smiling_gesture"}

    def __init__(self, key=None) -> None:
        self._key = key
        self._gestures = {"head": {"smiling_gesture": None}}
        super().__init__(SmilingEvent._gesture_types)


class FishFaceEvent(HeadGestureTriggerEvent):
    _gesture_types = {"fish_face_gesture"}

    def __init__(self, key=None) -> None:
        self._key = key
        self._gestures = {"head": {"fish_face_gesture": None}}
        super().__init__(FishFaceEvent._gesture_types)


class OpenMouthEvent(HeadGestureTriggerEvent):
    _gesture_types = {"open_mouth_gesture"}

    def __init__(self, key=None) -> None:
        self._key = key
        self._gestures = {"head": {"open_mouth_gesture": None}}
        super().__init__(OpenMouthEvent._gesture_types)


class RaiseEyeBrowEvent(HeadGestureTriggerEvent):
    _gesture_types = {"raise_eyebrows_gesture"}

    def __init__(self, key=None) -> None:
        self._key = key
        self._gestures = {"head": {"raise_eyebrows_gesture": None}}
        super().__init__(RaiseEyeBrowEvent._gesture_types)


class FishFaceEvent(HeadGestureTriggerEvent):
    _gesture_types = {"fish_face_gesture"}

    def __init__(self, key=None) -> None:
        self._key = key
        self._gestures = {"head": {"fish_face_gesture": None}}
        super().__init__(FishFaceEvent._gesture_types)

class TurnLeftEvent(HeadGestureTriggerEvent):
    _gesture_types = {"turn_left_gesture"}

    def __init__(self, key=None) -> None:
        self._key = key
        self._gestures = {"head": {"turn_left_gesture": None}}
        super().__init__(TurnLeftEvent._gesture_types)

class TurnRightEvent(HeadGestureTriggerEvent):
    _gesture_types = {"turn_right_gesture"}

    def __init__(self, key=None) -> None:
        self._key = key
        self._gestures = {"head": {"turn_right_gesture": None}}
        super().__init__(TurnRightEvent._gesture_types)

class TiltLeftEvent(HeadGestureTriggerEvent):
    _gesture_types = {"tilt_left_gesture"}

    def __init__(self, key=None) -> None:
        self._key = key
        self._gestures = {"head": {"tilt_left_gesture": None}}
        super().__init__(TiltLeftEvent._gesture_types)

class TiltRightEvent(HeadGestureTriggerEvent):
    _gesture_types = {"tilt_right_gesture"}

    def __init__(self, key=None) -> None:
        self._key = key
        self._gestures = {"head": {"tilt_right_gesture": None}}
        super().__init__(TiltRightEvent._gesture_types)