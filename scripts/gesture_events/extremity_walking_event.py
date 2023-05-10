'''
Author: Jason Ho
'''
import datetime
from typing import Optional

from scripts.gesture_events.simple_gesture_event import SimpleGestureEvent
from scripts.tools.config import Config

config = Config()
class ExtremityWalkingEvent(SimpleGestureEvent):
    """Class representing the walking + extremity triggers mode. Allows for walking on the spot to trigger a key holding down action, with 4 extremity
    triggers to change the key that is being held down.
    
    [trigger types]:
        "set_displays": called in the event set_up function to display the extremity circles and walking exercise in the view
        "walking_triggered": called when a walking state that wasn't activated before has been activated
        "extremity_triggered": called when an extremity trigger that wasn't activated before has been activated
        "held": called when a walking state that was already activated remains activated (not extremity trigger)
        "walking_released": called when a walking state that was already activated is now deactivated
        "extremity_released": called when an extremity trigger that was already activated is now deactivated
        "clear": called in the event force_deactivate function to remove the extremity circles and walking exercise display from the view

        Optionally defined by the optional event_trigger_types arg.
    [bodypart types]:
        "body": using gestures that are activated by body landmarks
    [gestures types]:
        "walking_left_state": state for walking (lifting left leg) with the left leg
        "walking_right_state": state for walking (lifting right leg) with the right leg
        "extremity_left_walking": left walking extremity trigger to change the keybind for walking 
        "extremity_right_walking": right walking extremity trigger  to change the keybind for walking 
        "extremity_up_walking": up walking extremity trigger  to change the keybind for walking 
        "extremity_down_walking": down walking extremity trigger  to change the keybind for walking
        
        Optionally defined by the optional gesture_types arg.
    """

    _event_trigger_types = {"set_displays", "walking_triggered", "extremity_triggered", "held", "walking_released", "extremity_released", "clear"}
    _bodypart_types = {"body"}
    _gesture_types = {"walking_left_state","walking_right_state", "extremity_left_walking", "extremity_right_walking", "extremity_up_walking", "extremity_down_walking"}  

    def __init__(self, gesture_types: Optional[set] = _gesture_types, event_trigger_types: Optional[set] = _event_trigger_types):
        super().__init__(gesture_types, event_trigger_types, ExtremityWalkingEvent._bodypart_types)
        self._set_extremity_walking_attributes()
        self._gestures = {"body": {gesture_type: None for gesture_type in self._gesture_types}}
        self._gesture_info_dict = {gesture_type: {"state": False, "activated": False, "repeats": 0, "released_time": datetime.datetime.now(), "key": None} for gesture_type in self._gesture_types}
        self._current_key = self._walking_keys["up_key"] #by default walking is the key set to the up extremity trigger
        self._held_before_release = False
        self._event_released_time = datetime.datetime.now()
        

    def _set_extremity_walking_attributes(self) -> None:
        self._walking_keys = config.get_data("events/extremity_walking")
        self._count_to_activate = config.get_data(f"body_gestures/exercises/no_equipment/walking/count_to_activate")
        self._exercise_release_interval = config.get_data("events/exercise_events/exercise_release_interval")
        self._hold_key_down_interval = config.get_data("events/exercise_events/hold_key_down_interval") # interval required to cause another key down action, to simulate holding a key down

    def update(self) -> None:
        """If the state of the exercise is True, checks the state of the gestures that the exercise depends on and triggers gesture event handler (exercise actions)
        methods (triggered, held, released) if conditions are met. These actions are either a key down if the gesture is a walking state, or colouring an 
        extremity circle.
        """
        if self._held_before_release:
            self._hold_walking_after_release()
        self._check_triggered()
        self._check_held()
        self._check_released()

    def set_up(self) -> None:
        """Sets the displaying of the extremity circles and activated exercises in the View"""
        editor = config.get_editor()
        editor.update(f"modules/body/mode", "no_equipment") # change the exercise mode to walking (so if an equipment exercise event was loaded before, we can revert it)
        self._event_triggers["set_displays"]()
        
    def _hold_walking_after_release(self) -> None:
        # after an exercise is stopped being detected, there is a 'key down interval', which is used to continue the walking for a set duration
        if self._time_difference(self._event_released_time, datetime.datetime.now()) < self._exercise_release_interval:
            if self._time_since_state_released("walking_left_state") > self._hold_key_down_interval or self._time_since_state_released("walking_right_state") > self._hold_key_down_interval:
                self._walking_hold_action()
        else:
            self._walking_release_action()
            self._check_state()
    
    def _walking_hold_action(self) -> None:
        self._event_triggers["held"](self._current_key)
        self._gesture_info_dict["walking_left_state"]["released_time"] = datetime.datetime.now() 
        self._gesture_info_dict["walking_right_state"]["released_time"] = datetime.datetime.now()

    def _walking_release_action(self) -> None:
        self._event_triggers["walking_released"](self._current_key) 
        self._event_released_time = datetime.datetime.now()
        self._held_before_release = False

    def force_deactivate(self) -> None:
        """Force deactivates the exercise by 'releasing' all gesture types/exercise states , and calling the gesture event handler (exercise actions)'s 
        clear method, which is used to remove the exercise text and extremity circles from the view.
        """
        for gesture_type in self._gesture_types:
            if self._gesture_info_dict[gesture_type]["activated"]:
                self._gesture_info_dict[gesture_type]["activated"] = False
                self._gesture_info_dict[gesture_type]["released_time"] = datetime.datetime.now()
        self._held_before_release = False
        self._event_released_time = datetime.datetime.now()
        self._event_triggers["clear"]()

    def _check_triggered(self) -> None:
        for gesture_type in self._gesture_types:
            if self._gesture_info_dict[gesture_type]["state"] and not self._gesture_info_dict[gesture_type]["activated"] :
                self._gesture_info_dict[gesture_type]["activated"] = True
                if gesture_type in {"walking_left_state", "walking_right_state"}:
                    if not self._held_before_release:
                        self._walking_trigger_action(gesture_type) # walking with the current key
                    
                else:
                    self._extremity_trigger_action(gesture_type) # change extremity trigger colour
                self._gesture_info_dict[gesture_type]["released_time"] = datetime.datetime.now()

    def _extremity_trigger_action(self, gesture_type: str) -> None:
        direction = gesture_type.split("_")[0]
        self._current_key = self._walking_keys[direction + "_key"]
        extremity_name = gesture_type[10:]
        repeats = self._gesture_info_dict[gesture_type]["repeats"]
        print(extremity_name)
        self._event_triggers["extremity_triggered"](extremity_name, repeats)

    def _walking_trigger_action(self, gesture_type: str)-> None:
        repeats = self._get_walking_repeats()
        self._gesture_info_dict[gesture_type]["repeats"] += 1
        self._event_triggers["walking_triggered"](repeats, self._current_key)

    def _check_held(self) -> None: # holding is when the gesture is already activated and still is
        for gesture_type in self._gesture_types:
            if self._gesture_info_dict[gesture_type]["activated"] and self._gestures["body"][gesture_type] is not None:
                if gesture_type in {"walking_left_state", "walking_right_state"} and not self._held_before_release:
                    if self._time_since_state_released(gesture_type) > self._hold_key_down_interval:
                        self._hold_action(gesture_type)

    def _hold_action(self, gesture_type: str) -> None:
        self._event_triggers["held"](self._current_key)
        self._gesture_info_dict[gesture_type]["released_time"] = datetime.datetime.now()

    def _check_released(self) -> None:
        for gesture_type in self._gesture_types:
            if self._gesture_info_dict[gesture_type]["activated"] and self._gestures["body"][gesture_type] is None: #exercise was triggered but now is deactivated, so we can increment
                if gesture_type not in {"walking_left_state", "walking_right_state"}:
                    self._extremity_release_action(gesture_type)

                elif not self._held_before_release: # walking has just released, so we need to account for the extra hold time
                    self._held_before_release = True
                    self._event_released_time = datetime.datetime.now()
                    continue
                self._gesture_info_dict[gesture_type]["state"] = False
                self._gesture_info_dict[gesture_type]["activated"] = False
                self._gesture_info_dict[gesture_type]["released_time"] = datetime.datetime.now()
        self._check_state()

    def _extremity_release_action(self, gesture_type: str) -> None:
        extremity_name = gesture_type[10:]
        self._gesture_info_dict[gesture_type]["repeats"] += 1
        self._gesture_info_dict[gesture_type]["state"] = False
        self._gesture_info_dict[gesture_type]["activated"] = False
        self._gesture_info_dict[gesture_type]["released_time"] = datetime.datetime.now()
        self._event_triggers["extremity_released"](extremity_name, self._gesture_info_dict[gesture_type]["repeats"])
            
    def _check_state(self) -> None:
        self._state = False
        if self._held_before_release:
            self._state = True
        for gesture_type in self._gesture_types:
            # each gesture's state is true if it's just been triggered or was triggered before, but now just deactivated. Otherwise it is false
            if self._gestures["body"][gesture_type] is not None or self._gesture_info_dict[gesture_type]["activated"]:
                self._gesture_info_dict[gesture_type]["state"] = True
                self._state = True

    def _get_walking_repeats(self) -> int:
        return self._gesture_info_dict["walking_left_state"]["repeats"] + self._gesture_info_dict["walking_right_state"]["repeats"]

    def _time_since_state_released(self, gesture_type: str) -> float:
        return self._time_difference(self._gesture_info_dict[gesture_type]["released_time"], datetime.datetime.now())

    def _time_difference(self, start_time: datetime, end_time: datetime) -> float:
        return (end_time - start_time).total_seconds()
