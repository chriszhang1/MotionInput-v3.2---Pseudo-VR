'''
Authors: Fawziyah Hussain and Eva Miah
'''
from scripts.tools import Config
from .simple_gesture_event import SimpleGestureEvent

class PenDragEvent(SimpleGestureEvent):
    """Dragging using pen input mode with the gesture_type specified.
    
    [trigger types]:
        "press": called when the gesture of interest becomes active
        "release": called when the gesture of interest becomes unactive
        "update": called when the gesture of interest is currently already active
        "update_pressure": called if pressure sensitivity enabled and gesture active
    [bodypart types]:
        "hand": the hand on which we track the gesure of interest
    [gestures types]:
        defined by the gesture_type arg.
    """

    _event_trigger_types = {"update", "press", "release", "update_pressure"}
    _bodypart_types = {"hand"}

    def __init__(self, gesture_type: str):
        self._click_held = False
        self._gesture_type = gesture_type
        self._gestures = {"hand": {gesture_type: None}}
        config = Config()
        self._frames_for_press = config.get_data("events/click_press/frames_for_press")
        self._max_pressure = config.get_data("handlers/pen/max_depth")
        self._min_pressure = config.get_data("handlers/pen/min_depth")
        self._depth_range = config.get_data("handlers/pen/depth_range")
        self._pressure_enabled = config.get_data("handlers/pen/pressure_enabled")
        super().__init__({gesture_type}, PenDragEvent._event_trigger_types, PenDragEvent._bodypart_types)

    def update(self):
        # if index pinch just activated, initiate drag
        if self._state and not self._click_held:
            self._click_held = True
            if self._event_triggers["press"] is not None:
                self._event_triggers["press"]() 

        # if drag activated, release drag if pinch deactivated, otherwise update coordinates to continue drag event 
        if self._click_held:
            if self._gestures["hand"][self._gesture_type] is None:
                self._click_held = False
                self._state = False
                if self._event_triggers["release"] is not None:  self._event_triggers["release"]()
            else:
                if self._event_triggers["update"] is not None:
                    self._event_triggers["update"]()

        # if pressure sensitivity enabled, calculate new pressure and update
        if self._pressure_enabled and self._click_held:
            hand_position = self._gestures["hand"][self._gesture_type].get_last_position()
            palm_height = hand_position.get_palm_height()
            pressure = self._calculate_pressure(palm_height)
            if self._event_triggers["update_pressure"] is not None:
                self._event_triggers["update_pressure"](pressure)


    def _calculate_pressure(self, palm_height):
        """Returns a pressure value between 0 and 1024 depending on the position of users hand relative to the calibrated max and min pressure coordinates"""
        increment = self._depth_range / 1024
        if palm_height <= self._min_pressure:
            new_pressure = 0
        elif palm_height >= self._max_pressure:
            new_pressure = 1024
        else:
            new_pressure = (palm_height - self._min_pressure) / increment

        return int(new_pressure)

    
    def force_deactivate(self) -> None:
        if self._click_held: 
            if self._event_triggers["release"] is not None:  self._event_triggers["release"]()

    def _check_state(self) -> None:
        self._state = (self._gestures["hand"][self._gesture_type] is not None) or self._click_held
