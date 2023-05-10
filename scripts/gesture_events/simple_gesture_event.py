'''
Author: Carmen Meinson
'''
from scripts.core import Gesture, GestureEvent
from typing import Dict, Callable, Set


# a class to be used by child classes that utilize similar logic
# assumes that per each gesture type and body part type you cna have only one gesture
class SimpleGestureEvent(GestureEvent):
    """Parent class to be used by standard GestureEvents.
    Provides the methods that guarantee that all the gestures of interest are in the self._gestures after the notify methods are called by the model.
    """

    def __init__(self, gesture_types: Set[str], event_trigger_types: Set[str], bodypart_types: Set[str]):
        super().__init__(gesture_types, event_trigger_types, bodypart_types)
        self._state = False
        self._event_triggers = {_: None for _ in self._event_trigger_types}
        self._bodypart_name_to_type = {}

    def set_trigger_functions(self, funcs: Dict[str, Callable]) -> None:
        for event_name in funcs:
            if event_name not in self._event_triggers:
                raise RuntimeError("Unable to add trigger to event. ", event_name, " not defined in event class.")

        for event_name in funcs:
            self._event_triggers[event_name] = funcs[event_name]

    def set_bodypart_names(self, name_to_type: Dict[str, str]):
        given_types = set(name_to_type.values())
        if len(given_types | self._bodypart_types) != len(given_types):
            raise RuntimeError("Unable to add bodypart names to event. ", self._bodypart_types, " expected, but ",
                               given_types, " given")

        self._bodypart_name_to_type = name_to_type

    def get_state(self) -> bool:
        self._check_state()
        return self._state

    def notify_gesture_activated(self, gesture: Gesture):
        # called when some gesture that it depends on has activated
        # checks if it is active aka the conditions
        if gesture.get_bodypart_name() in self._bodypart_name_to_type:
            bodypart_type = self._bodypart_name_to_type[gesture.get_bodypart_name()]
            if gesture.get_name() in self._gestures[bodypart_type]:
                self._gestures[bodypart_type][gesture.get_name()] = gesture
                self._check_state()

    def notify_gesture_deactivated(self, gesture: Gesture):
        # called when some gesture that it depends on has deactivated
        # checks if it is active aka the conditions
        if gesture.get_bodypart_name() in self._bodypart_name_to_type:
            bodypart_type = self._bodypart_name_to_type[gesture.get_bodypart_name()]
            if gesture.get_name() in self._gestures[bodypart_type]:
                self._gestures[bodypart_type][gesture.get_name()] = None
                self._check_state()

    def update(self):
        # checks the event firing condition and if true calls the _event_trigger
        raise NotImplementedError()

    def _check_state(self) -> bool:
        raise NotImplementedError()

    def get_all_gestures(self):
        return self._gestures
