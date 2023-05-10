'''
Author: Jason Ho
'''
from typing import List, Optional

from scripts.tools.config import Config
from .exercise_display import ExerciseDisplay
from .pydirect_directx_actions import Clicker, Keyboard


class ExerciseActions:
    """Actions for the ExerciseEvent class. This class mainly performs keyboard actions like pressing a key, holding a key, releasing a key, as well as
    pressing and releasing the left and right mouse keys."""
    def __init__(self, exercise_display: ExerciseDisplay) -> None:
        self._exercise_display = exercise_display
        self._keyboard = Keyboard()
        self._clicker = Clicker()
        self._exercises_displaying = False

    def trigger_action(self, exercise: str, matching_count: bool, action_type: str, repeats: int = 0, key: Optional[str] = None) -> None:
        """Performs the action associated with an exercise when it is triggered.
        
        :param exercise: name of exercise
        :type exercise: str
        :param action_type: name of action type (key_press, key_down, left_click or right_click)
        :type action_type: str
        :param repeats: number of times the exercise has been repeated
        :type repeats: int
        :param key: name of the key associated with the action, if any
        :type key: Optional[str]
        """
        # if the action is key_down, it is ignored because it will be handled in held_action
        # print("TRIGGERED")
        if action_type == "key_press" and matching_count: 
            self._keyboard.key_press(key)
        elif action_type == "left_click" and matching_count:
            self._clicker.left_click()
        elif action_type == "right_click" and matching_count:
            self._clicker.right_click()
        elif action_type == "key_down": # no check for matching_count
            self._keyboard.key_down(key)
        self._exercise_display.update_exercise_repeats(exercise, repeats)

    def held_action(self, action_type: str, key: Optional[str] = None) -> None:
        """Performs the action (pressing a specific key down) associated with an exercise when it is held. This is only when the action type is keydown

        :param action_type: name of action type (key_press, key_down, left_click or right_click)
        :type action_type: str
        :param key: name of the key associated with the action, if any
        :type key: Optional[str]
        """
        if action_type == "key_down":
            self._keyboard.key_down(key) 

    def release_action(self, action_type: str, key: Optional[str] = None) -> None:
        """Performs the action (pressing a specific key up/releasing a key) associated with an exercise when it is released.
        
        :param exercise: name of exercise
        :type exercise: str
        :param action_type: name of action type (key_press, key_down, left_click or right_click)
        :type action_type: str
        :param repeats: number of times the exercise has been repeated
        :type repeats: int
        :param key: name of the key associated with the action, if any
        :type key: Optional[str]
        """
        print("RELEASED")

        if action_type == "key_down":
            self._keyboard.key_up(key)

    def clear_exercise_display(self) -> None:
        """Calls an exercise display method to clear the exercise text from the view"""
        self._exercise_display.clear_exericse_display()
        self._exercises_displaying = False
    
    def set_exercise_display(self, exercises: Optional[List[str]] = None) -> None:
        """Uses the config to get the exercises it needs to display in view, and calls an exercise display method to display it.

        :param exercises: List of exercises for the count to be displayed
        :type exercises: Optional[List[str]]
        """
        # if no exercise list gets passed, then the default is to add all of the activated exercises
        if not self._exercises_displaying:
            if exercises is None:
                config = Config()
                mode = config.get_data("modules/body/mode")
                exercises_dict = config.get_data(f"body_gestures/exercises/{mode}")
                exercises = [exercise for exercise in exercises_dict if exercises_dict[exercise]["activated"]]
            self._exercise_display.set_exercise_display(exercises)
            self._exercises_displaying = True