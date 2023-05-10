'''
Author: Carmen Meinson
'''
from scripts.tools import Config
from .simple_gesture_event import SimpleGestureEvent


class ClickPressEvent(SimpleGestureEvent):
    """Clicking/Pressing with the gesture_type specified.
    Currently as there is no logic of how to decide if a press or a click should be started press is trigerred only if the click trigger was not given
    
    [trigger types]:
        "click": called once when the gesture of interest becomes active
        "press": called when the gesture of interest becomes active IF the "click" trigger type was not defined
        "release": called when the gesture of interest becomes unactive IF the "click" trigger type was not defined
    [bodypart types]:
        "hand": the hand on which we track the gesure of interest
    [gestures types]:
        defined by the gesture_type arg.
    """
    _event_trigger_types = {"click", "press", "release"}
    _bodypart_types = {"hand"}

    def __init__(self, gesture_type: str, additional_bodypart_types=set()):
        bodypart_types = additional_bodypart_types | ClickPressEvent._bodypart_types
        super().__init__({gesture_type}, ClickPressEvent._event_trigger_types, bodypart_types)
        self._click_held = False
        self._gesture_type = gesture_type
        self._gestures = {"hand": {gesture_type: None}}
        config = Config()
        self._frames_for_press = config.get_data("events/click_press/frames_for_press")

    def update(self):
        # TODO: HOW TO JUST CLICK VS PRESS!!!!! currently done in the same manner as v2 but could be a better solution
        # if index pinched just activated, do left left_click
        if self._state and not self._click_held:
            self._click_held = True
            if self._event_triggers["click"] is not None:
                self._event_triggers["click"]()  # TODO: LOGIC OF PRESS AND CLICK
            elif self._event_triggers["press"] is not None:
                self._event_triggers["press"]()
        # if index pinch just deactivated do release and set state to false
        if self._click_held:
            if self._gestures["hand"][self._gesture_type] is None:
                self._click_held = False
                self._state = False
                if self._event_triggers["release"] is not None:  self._event_triggers["release"]()

            # elif self._gestures["index_pinch"].get_frames_held()==self._frames_for_press:
            # if  self._event_triggers["press"] is not None: self._event_triggers["press"]()

    def force_deactivate(self) -> None:
        if self._click_held:
            if self._event_triggers["release"] is not None:  self._event_triggers["release"]()

    def _check_state(self) -> None:
        self._state = (self._gestures["hand"][self._gesture_type] is not None) or self._click_held


class SingleHandExclusiveClickPressEvent(ClickPressEvent):
    """Clicking/Pressing only if the same gesture is NOT made on the off_hand.
    RN used so that mouse would not be clicked during zooming as both use index_pinch
    """
    _bodypart_types = {"hand", "off_hand"}

    def __init__(self, gesture_type: str):
        super().__init__(gesture_type, {"off_hand"})
        self._gestures["off_hand"] = {"index_pinch": None}

    def _check_state(self) -> None:
        self._state = (self._gestures["off_hand"][self._gesture_type] is None) and (
                    self._gestures["hand"][self._gesture_type] is not None or self._click_held)
