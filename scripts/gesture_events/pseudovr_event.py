'''
Author: Chris Zhang
'''
import datetime
from typing import Any, Dict, List, Optional

from scripts.gesture_events.extremity_walking_event import ExtremityWalkingEvent
from scripts.tools import ModeEditor
from scripts.tools.config import Config

config = Config()
mode = ModeEditor()
class PseudoVRModeEvent(ExtremityWalkingEvent):
    """Class representing the walking + extremity triggers pseudovr mode. Special mode to allow for walking to perform an action along with holding an
    extremity trigger, as well as standalone extremity triggers to act as buttons. Its child classes are variations of the mode
    
    [trigger types]:
        Defined by the _event_trigger_types attributes of its child classes
    [bodypart types]:
        "body": using gestures that are activated by body landmarks
    [gestures types]:
        Defined by the _gesture_types attribute of its child classes
    """

    def __init__(self) -> None:
        super().__init__(self._gesture_types, self._event_trigger_types)
        self._set_extremity_keys()
        
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

    def _set_extremity_keys(self) -> None:
        self._walking_keys = config.get_data("events/pseudovr_mode_keys/walking_extremities")
        self._button_keys = config.get_data("events/pseudovr_mode_keys/button_extremities")

        for extremity, key in self._walking_keys.items():
            self._gesture_info_dict[extremity]["key"] = key
        for extremity, key in self._button_keys.items():
            self._gesture_info_dict[extremity]["key"] = key
    
    def _hold_walking_after_release(self, key_list: Optional[List[str]] = None) -> None:
        # after an exercise is stopped being detected, there is a 'key down interval', which is used to continue the walking for a set duration
        if self._time_difference(self._event_released_time, datetime.datetime.now()) < self._exercise_release_interval:
            if self._time_since_state_released("walking_left_state") > self._hold_key_down_interval or self._time_since_state_released("walking_right_state") > self._hold_key_down_interval:
                self._walking_hold_action(key_list)
        else:
            self._walking_release_action(key_list)

    def _walking_hold_action(self, key_list: Optional[List[str]] = None) -> None:
        if key_list is None:
            extremity_dict = self._get_extremity_dict(True)
            key_list = [key for extremity, key in self._walking_keys.items() if extremity in extremity_dict]
        self._event_triggers["held"](key_list)
        self._gesture_info_dict["walking_left_state"]["released_time"] = datetime.datetime.now() 
        self._gesture_info_dict["walking_right_state"]["released_time"] = datetime.datetime.now()

    def _check_triggered(self) -> None:
        walking = False
        for gesture_type in self._gesture_types:
            if self._gesture_info_dict[gesture_type]["state"] and not self._gesture_info_dict[gesture_type]["activated"]:
                self._gesture_info_dict[gesture_type]["activated"] = True
                if gesture_type in {"walking_left_state", "walking_right_state"} and not self._held_before_release:
                        walking = True
                        self._gesture_info_dict[gesture_type]["repeats"] += 1
                else:
                    self._extremity_trigger_action(gesture_type)
                self._gesture_info_dict[gesture_type]["released_time"] = datetime.datetime.now()

        if walking:
            self._walking_trigger_action()
    
    def _extremity_trigger_action(self, gesture_type: str) -> None:
        extremity_name = gesture_type[10:] # remove _extremity from string
        repeats = self._gesture_info_dict[gesture_type]["repeats"]

        if gesture_type in self._button_keys: #extremity buttons should be triggered
            self._event_triggers["extremity_triggered"](extremity_name, repeats, self._button_keys[gesture_type])

        elif gesture_type in self._walking_keys:
            self._event_triggers["extremity_triggered"](extremity_name, repeats)
        self._gesture_info_dict[gesture_type]["released_time"] = datetime.datetime.now()

    def _walking_trigger_action(self, key_list: Optional[List[str]] = None) -> None:
        if key_list is None:        
            extremity_dict = self._get_extremity_dict(True)
            key_list = [key for extremity, key in self._walking_keys.items() if extremity in extremity_dict]
        walking_repeats = self._get_walking_repeats()
        self._event_triggers["walking_triggered"](walking_repeats, key_list) # check if walking is on, and light up extremity circles. if both, then cause a key down

    def _check_held(self, key_list: Optional[List[str]] = None) -> None:
        # only need to check if walking is still activated, and pass what keys are triggered
        # extremity_dict = self._get_activated_extremity_dict()
        extremity_dict = self._get_extremity_dict(True)
        for gesture_type in self._gesture_types:
            if self._gesture_info_dict[gesture_type]["activated"] and self._gestures["body"][gesture_type] is not None :
                if self._time_since_state_released(gesture_type) > self._hold_key_down_interval :
                    self._hold_action(gesture_type, extremity_dict, key_list)
                    
    def _hold_action(self, gesture_type: str, extremity_dict: str, key_list: Optional[List[str]] = None) -> None:
        if gesture_type in {"walking_left_state", "walking_right_state"} and not self._held_before_release:
            if key_list is None:
                key_list = [key for extremity, key in self._walking_keys.items() if extremity in extremity_dict]
            self._event_triggers["held"](key_list)

        elif gesture_type in self._button_keys:
            self._event_triggers["held"]([self._button_keys[gesture_type]])
        self._gesture_info_dict[gesture_type]["released_time"] = datetime.datetime.now()

    def _check_released(self) -> None:
        for gesture_type in self._gesture_types:
            if self._gesture_info_dict[gesture_type]["activated"] and self._gestures["body"][gesture_type] is None:
                if gesture_type not in {"walking_left_state", "walking_right_state"}:
                    self._extremity_release_action(gesture_type)

                elif not self._held_before_release:
                    self._held_before_release = True
                    self._event_released_time = datetime.datetime.now()
                    continue
                self._gesture_info_dict[gesture_type]["state"] = False
                self._gesture_info_dict[gesture_type]["activated"] = False
                self._gesture_info_dict[gesture_type]["released_time"] = datetime.datetime.now()
        self._check_state()
    
    def _extremity_release_action(self, gesture_type) -> None:
        extremity_name = gesture_type[10:]
        self._gesture_info_dict[gesture_type]["repeats"] += 1
        if gesture_type in self._button_keys:
            self._event_triggers["extremity_released"](extremity_name, self._gesture_info_dict[gesture_type]["repeats"], self._button_keys[gesture_type])
        
        else:
            self._event_triggers["extremity_released"](extremity_name, self._gesture_info_dict[gesture_type]["repeats"])
    
    def _walking_release_action(self, key_list: Optional[List[str]] = None) -> None:
        if key_list is None:
            extremity_dict = self._get_extremity_dict()
            key_list = [extremity_dict[extremity]["key"] for extremity in extremity_dict]

        self._event_triggers["walking_released"](key_list) # check if walking is on, and light up extremity circles. if both, then cause a key down
        self._event_released_time = datetime.datetime.now()
        self._held_before_release = False
        self._check_state()

    def _get_extremity_dict(self, state_of_extremities = None) -> Dict[str, Dict[str, Any]]:
        # returns dict with extremity as key and a dict with repeats and key as value
        # state_of_extremities determines whether only activated or deactivated extremities are added to the dict, with the default being add all
        extremity_dict = {}
        for extremity_gesture in self._gesture_info_dict:
            if extremity_gesture not in {"walking_left_state", "walking_right_state"}:
                if (state_of_extremities is None) \
                     or (state_of_extremities and self._gesture_info_dict[extremity_gesture]["activated"]) \
                     or (not state_of_extremities and self._gesture_info_dict[extremity_gesture]["deactivated"]):
                    extremity_dict[extremity_gesture] = {"repeats": self._gesture_info_dict[extremity_gesture]["repeats"], "key": self._gesture_info_dict[extremity_gesture]["key"]}
        return extremity_dict


class PseudoVRMode1Event(PseudoVRModeEvent):
    """Class for Mode 1 of the PseudoVR mode. The walking D-pad here is used to change the keybind for walking, so
    it does not need to be continuously held down.
    
    [trigger types]:
        "set_displays": called in the event set_up function to display the extremity circles and walking exercise in the view
        "walking_triggered": called when a walking state that wasn't activated before has been activated
        "extremity_triggered": called when an extremity trigger that wasn't activated before has been activated
        "held": called when a walking state or a button extremity trigger that was already activated remains activated
        "walking_released": called when a walking state that was already activated is now deactivated
        "extremity_released": called when an extremity trigger that was already activated is now deactivated
        "clear": called in the event force_deactivate function to remove the extremity circles and walking exercise display from the view
    [bodypart types]:
        "body": using gestures that are activated by body landmarks
    [gestures types]:
        "walking_left_state": state for walking (lifting left leg) with the left leg
        "walking_right_state": state for walking (lifting right leg) with the right leg
        "extremity_left_walking": left walking extremity trigger to change the current walking keybind 
        "extremity_right_walking": right walking extremity trigger to change the current walking keybind
        "extremity_up_walking": up walking extremity trigger to activate to change the current walking keybind
        "extremity_down_walking": down walking extremity trigger to activate to change the current walking keybind
        "extremity_start_key": start key extremity trigger to cause a key down action
        "extremity_quit_key": quit key extremity trigger to cause a key down action
    """
    _gesture_types = {"walking_left_state","walking_right_state", "extremity_left_walking", "extremity_right_walking", "extremity_up_walking", "extremity_down_walking"}
    _button_keys = config.get_data("events/pseudovr_mode_keys/button_extremities")
    for extremity, key in _button_keys.items():
        _gesture_types.add(extremity)

    _event_trigger_types = {"set_displays", "walking_triggered", "extremity_triggered", "held", "walking_released", "extremity_released", "clear"}

    def __init__(self) -> None:
        super().__init__()

    def set_up(self) -> None:
        """Sets the displaying of the extremity circles and activated exercises in the View"""
        editor = config.get_editor()
        editor.update(f"modules/body/mode", "no_equipment") # change the exercise mode to walking (so if an equipment exercise event was loaded before, we can revert it)
        current_mode = mode.get_data("current_mode")
        
        button_set = set()
        button_keys = config.get_data("events/pseudovr_mode_keys/button_extremities")
        for extremity, key in button_keys.items():
            button_set.add(extremity[10:])

        if current_mode.find("left") != -1:
            button_set.update(["left_walking_rh", "right_walking_rh", "up_walking_rh", "down_walking_rh"])
            self._event_triggers["set_displays"](button_set)
        else:
            button_set.update(["left_walking", "right_walking", "up_walking", "down_walking"])
            self._event_triggers["set_displays"](button_set)

    def _set_extremity_keys(self) -> None:
        super()._set_extremity_keys()
        self._current_key = self._gesture_info_dict["extremity_up_walking"]["key"] # this mode only walks with the current key
    
    def _extremity_trigger_action(self, gesture_type: str) -> None:
        super()._extremity_trigger_action(gesture_type)
        if gesture_type in self._walking_keys:
            self._current_key = self._gesture_info_dict[gesture_type]["key"]

    def _walking_trigger_action(self) -> None:
        super()._walking_trigger_action([self._current_key])

    def _check_held(self) -> None:
        super()._check_held([self._current_key])

    def _hold_walking_after_release(self) -> None:
        super()._hold_walking_after_release([self._current_key])

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


class PseudoVRMode2Event(PseudoVRModeEvent):
    """Class for Mode 2 of the PseudoVR mode. The triggers in the walking D-pad need to be held with walking together to
    cause an action.
    
    [trigger types]:
        "set_displays": called in the event set_up function to display the extremity circles and walking exercise in the view
        "walking_triggered": called when a walking state that wasn't activated before has been activated
        "extremity_triggered": called when an extremity trigger that wasn't activated before has been activated
        "held": called when a walking state or a button extremity trigger that was already activated remains activated
        "walking_released": called when a walking state that was already activated is now deactivated
        "extremity_released": called when an extremity trigger that was already activated is now deactivated
        "clear": called in the event force_deactivate function to remove the extremity circles and walking exercise display from the view
    [bodypart types]:
        "body": using gestures that are activated by body landmarks
    [gestures types]:
        "walking_left_state": state for walking (lifting left leg) with the left leg
        "walking_right_state": state for walking (lifting right leg) with the right leg
        "extremity_left_walking": left walking extremity trigger to activate with walking to cause a key down action
        "extremity_right_walking": right walking extremity trigger to activate with walking to cause a key down action
        "extremity_up_walking": up walking extremity trigger to activate with walking to cause a key down action
        "extremity_down_walking": down walking extremity trigger to activate with walking to cause a key down action
        "extremity_start_key": start key extremity trigger to cause a key down action
        "extremity_quit_key": quit key extremity trigger to cause a key down action
    """
    _gesture_types = {"walking_left_state","walking_right_state", "extremity_left_walking", "extremity_right_walking", "extremity_up_walking", "extremity_down_walking"}
    _button_keys = config.get_data("events/pseudovr_mode_keys/button_extremities")
    for extremity, key in _button_keys.items():
        _gesture_types.add(extremity)

    _event_trigger_types = {"set_displays", "walking_triggered", "extremity_triggered", "held", "walking_released", "extremity_released", "clear"}

    def __init__(self) -> None:
        super().__init__()
    
    def set_up(self) -> None:
        """Sets the displaying of the extremity circles and activated exercises in the View"""
        editor = config.get_editor()
        editor.update(f"modules/body/mode", "no_equipment") # change the exercise mode to walking (so if an equipment exercise event was loaded before, we can revert it)
        current_mode = mode.get_data("current_mode")
        
        button_set = set()
        button_keys = config.get_data("events/pseudovr_mode_keys/button_extremities")
        for extremity, key in button_keys.items():
            button_set.add(extremity[10:])
        
        if current_mode.find("left") != -1:
            button_set.update(["left_walking_rh", "right_walking_rh", "up_walking_rh", "down_walking_rh"])
            self._event_triggers["set_displays"](button_set)
        else:
            button_set.update(["left_walking", "right_walking", "up_walking", "down_walking"])
            self._event_triggers["set_displays"](button_set)

class PseudoVRMode3Event(PseudoVRMode1Event):
    """Class for Mode 3 of the PseudoVR mode. Here, all triggers act as buttons, with walking on the spot fixed
    to the same key.
    
    [trigger types]:
        "set_displays": called in the event set_up function to display the extremity circles and walking exercise in the view
        "walking_triggered": called when a walking state that wasn't activated before has been activated
        "extremity_triggered": called when an extremity trigger that wasn't activated before has been activated
        "held": called when a walking state or a button extremity trigger that was already activated remains activated
        "walking_released": called when a walking state that was already activated is now deactivated
        "extremity_released": called when an extremity trigger that was already activated is now deactivated
        "clear": called in the event force_deactivate function to remove the extremity circles and walking exercise display from the view
    [bodypart types]:
        "body": using gestures that are activated by body landmarks
    [gestures types]:
        "walking_left_state": state for walking (lifting left leg) with the left leg
        "walking_right_state": state for walking (lifting right leg) with the right leg
        "extremity_left_walking": left walking extremity trigger to cause a key down action 
        "extremity_right_walking": right walking extremity trigger to cause a key down action
        "extremity_down_walking": down walking extremity trigger to activate to cause a key down action
        "extremity_start_key": start key extremity trigger to cause a key down action
        "extremity_quit_key": quit key extremity trigger to cause a key down action
    """
    _gesture_types = {"walking_left_state","walking_right_state", "extremity_left_walking", "extremity_right_walking", "extremity_down_walking"}
    _button_keys = config.get_data("events/pseudovr_mode_keys/button_extremities")
    for extremity, key in _button_keys.items():
        _gesture_types.add(extremity)
    
    _event_trigger_types = {"set_displays", "walking_triggered", "extremity_triggered", "held", "walking_released", "extremity_released", "clear"}

    def __init__(self) -> None:
        super().__init__()
        self._set_extremity_keys()
    
    def _set_extremity_keys(self) -> None:
        self._button_keys = config.get_data("events/pseudovr_mode_keys/button_extremities") | config.get_data("events/pseudovr_mode_keys/walking_extremities")
        self._current_key = self._button_keys.pop("extremity_up_walking")
        self._walking_keys = {}

    def set_up(self) -> None:
        """Sets the displaying of the extremity circles and activated exercises in the View"""
        editor = config.get_editor()
        editor.update(f"modules/body/mode", "no_equipment") # change the exercise mode to walking (so if an equipment exercise event was loaded before, we can revert it)
        current_mode = mode.get_data("current_mode")
        
        button_set = set()
        button_keys = config.get_data("events/pseudovr_mode_keys/button_extremities")
        for extremity, key in button_keys.items():
            button_set.add(extremity[10:])

        if current_mode.find("left") != -1:
            button_set.update(["left_walking_rh", "right_walking_rh", "down_walking_rh"])
            self._event_triggers["set_displays"](button_set)
        else:
            button_set.update(["left_walking", "right_walking", "down_walking"])
            self._event_triggers["set_displays"](button_set)