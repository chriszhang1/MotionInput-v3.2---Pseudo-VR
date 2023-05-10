'''
Author: Siam Islam
'''

from scripts.tools.config import Config
from .simple_gesture_event import SimpleGestureEvent

class KeyboardClickEvent(SimpleGestureEvent):
    """This event is active when any one of the gestures of interest is currently active.
    Click event trigger passes the hand, gesture name and the time that gesture has been held for, when called.
    Release event trigger passes the hand and the name of the gesture that is no longer active when called. 
    
    [trigger types]:
        "click": called when any one of the gestures of interest becomes active
        "release": called when a gesture of interest which was previously active becomes inactive    
    [bodypart types]:
        "dom_hand": the dominant hand on which we track the gestures of interest
        "off_hand": the off hand on which we track the gestures of interest
    [gestures types]:
        defined in config under the keyboard event settings.
    """

    _event_trigger_types = {"click", "release"}
    _bodypart_types = {"dom_hand", "off_hand"}

    def __init__(self):
        config = Config()
        gesture_type = "_" + config.get_data("events/keyboard/gesture_type")
        landmarks = config.get_data("events/keyboard/landmarks")
        self._gesture_types = set(landmark + gesture_type for landmark in landmarks)
        self._gestures = {}
        self._click_held = {}
        self.initialise_gestures()
        super().__init__(self._gesture_types, KeyboardClickEvent._event_trigger_types, KeyboardClickEvent._bodypart_types)

    def initialise_gestures(self) -> None:
        for hand in self._bodypart_types:
            self._gestures[hand] = {}
            self._click_held[hand] = {}
            for gesture in self._gesture_types:
                self._gestures[hand][gesture] = None
                self._click_held[hand][gesture] = False


    def update(self):
        for hand, gestures in self._gestures.items():
            for gesture_name, gesture in gestures.items():
                if gesture is not None:
                    if not self._click_held[hand][gesture_name]:
                        self._click_held[hand][gesture_name] = True
                        self._event_triggers["click"](hand, gesture_name, self._gestures[hand][gesture_name].get_time_held())
                    # update time_held if click gesture is being held
                    else:
                        self._event_triggers["click"](hand, gesture_name, self._gestures[hand][gesture_name].get_time_held())
            
                # if click gesture just deactivated, do release and set state to false
                if self._click_held[hand][gesture_name]:
                    if gesture is None:
                        self._click_held[hand][gesture_name] = False
                        self._event_triggers["release"](hand, gesture_name)


    def _check_state(self) -> None:
        state = False
        for hand, gestures in self._gestures.items():
            for gesture in gestures.values():
                if gesture is not None or self._click_held[hand]:
                    state = True
                    break
        self._state = state
