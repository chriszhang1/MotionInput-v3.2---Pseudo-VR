'''
Author: Jason Ho
'''
import datetime

from scripts.gesture_events.simple_gesture_event import SimpleGestureEvent
from scripts.tools.config import Config

# Exericse event represents an exercise, with each gesture representing an exercise state e.g. "walking_left" and "walking_right"
# Performs the same action, and each exercise state/gesture will trigger that same action but independent of each other
config = Config()
class ExerciseEvent(SimpleGestureEvent):
    """Class representing an exercise event. Each event is an exercise e.g. walking, and the gestures it handles correspond to the exercise states
    that it has activated e.g. walking_left_state. Allows for actions including key press, holding a key down, and mouse clicks.

    [trigger types]:
        "set_exercise_display": called in the event set_up function to display the chosen exercises on the view
        "triggered": called when an exercise state that wasn't activated before has been activated
        "held": called when an exercise state that was already activated remains activated
        "released": called when an exercise state that was already activated is now deactivated
        "clear": called in the event force_deactivate function to remove the exercise state from the view
    [bodypart types]:
        "body": using gestures that are activated by body landmarks
    [gestures types]:
        defined by the activate exercise states of the activated exercise
    """
    _event_trigger_types = {"set_exercise_display","triggered", "held", "released", "clear"}
    _bodypart_types = {"body"}

    def __init__(self, exercise_name: str, mode: str) -> None:
        self._exercise_name = exercise_name
        self._mode = mode
        self._set_exercise_attributes()
        self._set_gesture_types()
        super().__init__(self._gesture_types, ExerciseEvent._event_trigger_types, ExerciseEvent._bodypart_types)
        self._gestures = {"body": {gesture_type: None for gesture_type in self._gesture_types}}
        self._gesture_info_dict = {gesture_type: {"state": False, "activated": False, "repeats": 0, "released_time": datetime.datetime.now()} for gesture_type in self._gesture_types}
        self._repeats = 0
        self._held_before_release = False
        self._event_released_time = datetime.datetime.now()

    def _set_gesture_types(self) -> None:
        self._gesture_types = set()
        # gesture types for exercise event are the activated exercise states for an exercise
        states_dict = config.get_data(f"body_gestures/exercises/{self._mode}/{self._exercise_name}/states")
        for state in states_dict:
            if states_dict[state]["activated"]:
                self._gesture_types.add(state + "_state")

    def _set_exercise_attributes(self) -> None:
        self._exercise_release_interval = config.get_data("events/exercise_events/exercise_release_interval") # how long key should be held after exercise release
        self._hold_key_down_interval = config.get_data("events/exercise_events/hold_key_down_interval") # interval required to cause another key down action, to simulate holding a key down
        exercise_dict = config.get_data(f"body_gestures/exercises/{self._mode}/{self._exercise_name}")
        self._action_type = exercise_dict["action"]
        self._key = exercise_dict["key"]
        self._count_to_activate = exercise_dict["count_to_activate"]
        # print("ALL:", self._mode, self._exercise_release_interval, self._action_type, self._key, self._count_to_activate)

    def get_all_used_gestures(self) -> set:
        """Returns the set of the gestures that the exercise event depends on.
        
        :return: set of gestures that the exercise depends on
        :rtype: set
        """
        return self._gesture_types

    def get_exercise_name(self) -> str:
        """Returns name of the exercise that the event represents.
        
        :return: name of exercise
        :rtype: str
        """
        return self._exercise_name

    def update(self) -> None:
        """If the state of the exercise is True, checks the state of the gestures that the exercise depends on and triggers gesture event handler (exercise actions)
        methods (triggered, held, released) if conditions are met. These actions are either a key press, a key down (holding the key), and left or right mouse clicks.
        """
         # if the exercise is being held after release, then no need to check the gestures, we just let it hold before releasing
        if self._held_before_release:
            self._hold_exercise_after_release()
        self._check_triggered()
        self._check_held()
        self._check_released()

    def set_up(self) -> None:
        """Sets the displaying of the activated exercises in the View"""
        editor = config.get_editor()
        editor.update(f"modules/body/mode", self._mode) # allows for exercise mode to be switched whenever the event is added (so we can go from a no equipment mode like extremity walking to an equipment exercise)
        self._event_triggers["set_exercise_display"]()

    def _hold_exercise_after_release(self):
        # after an exercise is stopped being detected, there is a 'key down interval', which is used to continue the exercise action for a set duration
        if self._time_difference(self._event_released_time, datetime.datetime.now()) < self._exercise_release_interval:
            if any(self._time_since_state_released(gesture_type) > self._hold_key_down_interval for gesture_type in self._gesture_types):
                self._event_triggers["held"](self._action_type, self._key)
                for gesture_type in self._gesture_types:
                    self._gesture_info_dict[gesture_type]["released_time"] = datetime.datetime.now()
                    
        else:
            self._release_action()
            self._check_state()

    def _check_matching_count(self):
        return (self._repeats > 0) and (self._repeats % self._count_to_activate == 0)

    def _release_action(self):
        self._event_triggers["released"](self._key) 
        self._event_released_time = datetime.datetime.now()
        self._held_before_release = False

    def force_deactivate(self) -> None:
        """Force deactivates the exercise by 'releasing' all gesture types/exercise states of the exercise, and calling the gesture event handler (exercise actions)'s 
        clear method, which is used to remove the exercise text from the view.
        """
        self._held_before_release = False
        for gesture_type in self._gesture_types:
            if self._gesture_info_dict[gesture_type]["activated"]:
                self._gesture_info_dict[gesture_type]["activated"] = False
                self._event_triggers["released"](self._action_type, self._key)
                self._gesture_info_dict[gesture_type]["released_time"] = datetime.datetime.now()
        self._event_triggers["clear"]()

    def _check_triggered(self) -> None:
        # exercise state (gesture_type) is triggered if it wasn't activated and now the gesture is activated
        for gesture_type in self._gesture_types:
            if self._gesture_info_dict[gesture_type]["state"] and not self._gesture_info_dict[gesture_type]["activated"] and not self._held_before_release:
                self._trigger_action(gesture_type) # walking with the current key
                
    def _trigger_action(self, gesture_type) -> None:
        matching_count = (self._repeats % self._count_to_activate == 0)
        self._gesture_info_dict[gesture_type]["activated"] = True
        self._gesture_info_dict[gesture_type]["repeats"] += 1
        self._repeats += 1
        self._gesture_info_dict[gesture_type]["released_time"] = datetime.datetime.now()
        self._event_triggers["triggered"](self._exercise_name, matching_count, self._action_type, self._repeats, self._key) 

    def _check_held(self) -> None:
        # exercise state (gesture_type) is held if it was already activated and the gesture is still activated
        for gesture_type in self._gesture_types:
            if self._gesture_info_dict[gesture_type]["activated"] and self._gestures["body"][gesture_type] is not None and not self._held_before_release:
                if self._time_since_state_released(gesture_type) > self._hold_key_down_interval:
                    self._hold_action(gesture_type)

    def _hold_action(self, gesture_type: str) -> None:
        self._event_triggers["held"](self._action_type, self._key)
        self._gesture_info_dict[gesture_type]["released_time"] = datetime.datetime.now()

    def _check_released(self) -> None:
        # exercise state (gesture_type) is released if it was activated and now the gesture is deactivated
        for gesture_type in self._gesture_types:
            if self._gesture_info_dict[gesture_type]["activated"] and self._gestures["body"][gesture_type] is None and not self._held_before_release: #exercise was triggered but now is deactivated, so we can increment
                if self._action_type == "key_down":
                    self._held_before_release = True
                self._gesture_info_dict[gesture_type]["state"] = False
                self._gesture_info_dict[gesture_type]["activated"] = False
                self._gesture_info_dict[gesture_type]["released_time"] = datetime.datetime.now()
                self._event_released_time = datetime.datetime.now()
        self._check_state()

    def _check_state(self) -> None:
        self._state = False
        if self._held_before_release:
            self._state = True
        for gesture_type in self._gesture_types:
            # each gesture's state is true if it's just been triggered or was triggered before, but now just deactivated. Otherwise it is false
            if self._gestures["body"][gesture_type] is not None or self._gesture_info_dict[gesture_type]["activated"]:
                self._gesture_info_dict[gesture_type]["state"] = True
                self._state = True
                
    def _time_since_state_released(self, gesture_type: str) -> float:
        return self._time_difference(self._gesture_info_dict[gesture_type]["released_time"], datetime.datetime.now())
    
    def _time_difference(self, start_time: datetime, end_time: datetime) -> float:
        return (end_time - start_time).total_seconds()

