'''
Author: Jason Ho
'''
import datetime

from scripts.tools.config import Config
from .simple_gesture_event import SimpleGestureEvent

# class allows for multiple extremities to trigger THE SAME KINDS OF ACTIONS e.g. the same keypress
# each ExtremityTriggerEvent is made unique by the extremities it handles, so e.g. the extremity_up_event passes {extremity_up} as a gesture, whereas extremity_arm_left_event passes {extremity_arm_left}
# this means there's no need to make lots of child classes for each extremity, and allows for custom extremities
config = Config()
class ExtremityTriggerEvent(SimpleGestureEvent):
    # TODO: docstring
    """Class representing an extremity trigger event. Each event corresponds to an extremity trigger (represented as a circle in the view).
    Allows for actions including key press, holding a key down, and mouse clicks, and changing the colour of the extremity circle.

    [trigger types]:
        "set_exercise_display": called in the event set_up function to display the default extremity circles on the view
        "triggered": called when an extremity trigger that wasn't activated before has been activated
        "held": called when an extremity trigger that was already activated remains activated
        "released": called when an extremity trigger that was already activated is now deactivated
        "clear": called in the event force_deactivate function to remove the extremity circles from the view
    [bodypart types]:
        "body": using gestures that are activated by body landmarks
    [gestures types]:
        defined by the gesture corresponding to the represented extremity trigger
    """
    _event_trigger_types = {"set_extremity_circles", "triggered", "held", "released", "clear"}
    _bodypart_types = {"body"}
    def __init__(self, extremity_name: str) -> None:
        self._extremity_name = extremity_name
        self._gesture_types = {"extremity_" + extremity_name}
        self._set_extremity_attributes()
        super().__init__(self._gesture_types, ExtremityTriggerEvent._event_trigger_types, ExtremityTriggerEvent._bodypart_types)
        self._gestures = {"body": {gesture_type: None for gesture_type in self._gesture_types}}
        self._gesture_info_dict = {gesture_type: {"state": False, "activated": False, "repeats": 0, "triggered_time": datetime.datetime.now()} for gesture_type in self._gesture_types}

    def _set_extremity_attributes(self) -> None:
        self._hold_key_down_interval = config.get_data("events/exercise_events/hold_key_down_interval") # interval required to cause another key down action, to simulate holding a key down
        extremity_dict = config.get_data(f"body_gestures/extremity_triggers/{self._extremity_name}")
        self._action_type = extremity_dict["action"]
        self._key = extremity_dict["key"]

    def get_all_used_gestures(self) -> set:
        """ Returns the names of the associated gestures with the extremity, which is normally the extremity names.

        :return gesture_types: names of the associated gesture (e.g. "{arm_left}" or "{up}")
        :rtype gesture_types: set
        """
        return self._gesture_types

    def update(self) -> None:
        """If the state of the extremity trigger is True, checks the state of the gestures that the extremity trigger depends on and triggers gesture event handler (extremity actions)
        methods (triggered, held, released) if conditions are met. These actions are either a key press, a key down (holding the key), and left or right mouse clicks, as well
        as colouring the corresponding extremity circle to represent whether it is activated or deactivated.
        """
        self._check_triggered()
        self._check_held()
        self._check_released()
       
    def set_up(self) -> None:
        """Sets the displaying of the extremity circles in the View"""
        self._event_triggers["set_extremity_circles"]()

    def force_deactivate(self) -> None:
        """Force deactivates the exercise by deactivating all gesture types/extremity triggers of the exericise, and calling the gesture event handler (extremity actions)'s 
        clear method, which is used to remove the extremity circles from the view.
        """
        for gesture_type in self._gesture_types:
            extremity = gesture_type[10:]
            if self._gesture_info_dict[gesture_type]["activated"]:
                self._gesture_info_dict[gesture_type]["activated"] = False
                self._event_triggers["released"](extremity, self._action_type, self._gesture_info_dict[gesture_type]["repeats"], self._key)
                self._gesture_info_dict[gesture_type]["triggered_time"] = datetime.datetime.now()
        self._event_triggers["clear"]()

    def _check_triggered(self) -> None:
        # extremity trigger is triggered if it wasn't activated before, and now the gesture associated with it is activated
        for gesture_type in self._gesture_types:
            if self._gesture_info_dict[gesture_type]["state"] and not self._gesture_info_dict[gesture_type]["activated"]:
                self._gesture_info_dict[gesture_type]["activated"] = True
                extremity_name = gesture_type[10:]
                self._event_triggers["triggered"](extremity_name, self._action_type, self._gesture_info_dict[gesture_type]["repeats"], self._key)
                self._gesture_info_dict[gesture_type]["triggered_time"] = datetime.datetime.now()

    def _check_held(self) -> None:
        # extremity trigger is held if it was already activated from before, and the gesture associated with it is still activated
        for gesture_type in self._gesture_types:
            if self._gesture_info_dict[gesture_type]["activated"] and self._gestures["body"][gesture_type] is not None:
                if self._time_since_last_triggered(gesture_type) > self._hold_key_down_interval: 
                    self._event_triggers["held"](self._action_type, self._key)
                    self._gesture_info_dict[gesture_type]["triggered_time"] = datetime.datetime.now()

    def _check_released(self) -> None:
        # extremity trigger is released if it was already activated from before, and the gesture associated with it is now not activated
        for gesture_type in self._gesture_types:
            if self._gesture_info_dict[gesture_type]["activated"] and self._gestures["body"][gesture_type] is None: #the extremity trigger is now deactivated
                self._gesture_info_dict[gesture_type]["state"] = False
                self._gesture_info_dict[gesture_type]["activated"] = False
                self._gesture_info_dict[gesture_type]["repeats"] += 1
                repeats = self._gesture_info_dict[gesture_type]["repeats"]
                extremity_name = gesture_type[10:]
                self._event_triggers["released"](extremity_name, self._action_type, repeats, self._key)
                self._gesture_info_dict[gesture_type]["triggered_time"] = datetime.datetime.now()
        self._check_state()

    def _check_state(self) -> None:
        self._state = False
        for gesture_type in self._gesture_types:
            # each gesture's state is true if it's just been triggered or was triggered before, but now just deactivated. Otherwise it is false
            if self._gestures["body"][gesture_type] is not None or self._gesture_info_dict[gesture_type]["activated"]:
                self._gesture_info_dict[gesture_type]["state"] = True
                self._state = True

    def _time_since_last_triggered(self, gesture_type: str) -> float:
        return self._time_difference(self._gesture_info_dict[gesture_type]["triggered_time"], datetime.datetime.now())

    def _time_difference(self, start_time: datetime, end_time: datetime) -> float:
        return (end_time - start_time).total_seconds()

