'''
Author: Siam Islam
'''

from .simple_gesture_event import SimpleGestureEvent

class TouchPressEvent(SimpleGestureEvent):
    '''Pressing using touchpoints.
    Holding the gesture of interest with just the dominant hand activates 1 touchpoint.
    Holding with both hands activates 2 touchpoints.
    
    [trigger types]:
        "click": called when the gesture of interest first becomes active
        "press": called when the gesture of interest is already active (gesture being held)
        "release": called when the gesture of interest becomes inactive
    [bodypart types]:
        "dom_hand": the dominant hand on which we track the gestures of interest
        "off_hand": the off hand on which we track the gestures of interest
    [gestures types]:
        defined by the gesture_type arg.
    '''
    _event_trigger_types = {"click", "press", "release"}
    _bodypart_types = {"dom_hand", "off_hand"}


    def __init__(self, gesture_type: str):
        super().__init__({gesture_type}, TouchPressEvent._event_trigger_types, self._bodypart_types)
        self._gesture_type = gesture_type
        self._gestures = {hand: {gesture_type: None} for hand in self._bodypart_types}
        self._click_held = {hand:False for hand in self._bodypart_types}

    def update(self):
        if self._state and not self._click_held["dom_hand"]:
            self._click_held["dom_hand"] = True
            if self._event_triggers["click"] is not None:
                self._event_triggers["click"]()
        if self._click_held["dom_hand"]:
            if self._gestures["dom_hand"][self._gesture_type] is None:
                self._click_held["dom_hand"] = False
                self._state = False
                if self._event_triggers["release"] is not None:  self._event_triggers["release"]()
            else:
                if self._gestures["off_hand"][self._gesture_type] is None:
                    if self._event_triggers["press"] is not None:
                        self._event_triggers["press"](None)
                else:
                    hand_position = self._gestures["off_hand"][self._gesture_type].get_last_position()
                    landmark = hand_position.get_landmark("index_tip")
                    self._event_triggers["press"]((landmark[0], landmark[1]))

    def force_deactivate(self) -> None:
        if self._click_held: 
            if self._event_triggers["release"] is not None:  self._event_triggers["release"]()

    def _check_state(self) -> None:
        self._state = (self._gestures["dom_hand"][self._gesture_type] is not None) or self._click_held["dom_hand"]
