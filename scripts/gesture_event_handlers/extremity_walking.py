'''
Author: Jason Ho
'''
from typing import Any, Dict, List
from .exercise_display import ExerciseDisplay
from .extremity_circles import ExtremityCircles
from .pydirect_directx_actions import Keyboard

class ExtremityWalkingActions:
    """Actions for the ExtremityWalkingEvent class. These allow for walking on the spot to trigger a key hold, and for extremity triggers to
    be activated and deactivated."""
    
    def __init__(self, exercise_display: ExerciseDisplay, extremity_circles: ExtremityCircles) -> None:
        self._extremity_circles = extremity_circles
        self._exercise_display = exercise_display
        self._keyboard = Keyboard()
        self._circles_displaying = False
        self._exercises_displaying = False

    def walking_trigger_action(self, repeats: int, current_key: str) -> None:
        """Performs a keydown action of the current key being used, and increments the number of walking repeats displayed.
        
        :param repeats: Number of repeats for walking
        :type repeats: int
        :param current_key: Key to perform key down
        :type current_key: str
        """
        self._keyboard.key_down(current_key)
        self._exercise_display.update_exercise_repeats("walking", repeats)
    
    def extremity_trigger_action(self, extremity_name: str, repeats: int) -> None:
        """Changes the colour of the activated extremity circle to the activated colour, and the number of repeats.

        :param extremity_name: Name of activated extremity
        :type extremity_name: str
        :param repeats: Number of repeats for walking
        :type repeats: int
        """
        self._extremity_circles.update_extremity_circle(extremity_name, repeats, True)

    def held_action(self, current_key: str) -> None:
        """Performs a keydown action of the current key being used, to simulate the key being held.
        
        :param current_key: Key to perform key down
        :type current_key: str
        """
        self._keyboard.key_down(current_key)

    def extremity_release_action(self, extremity_name: str, repeats: int) -> None:
        """Changes the colour of the deactivated extremity circle to the deactivated colour, and the number of repeats.

        :param extremity_name: Name of deactivated extremity
        :type extremity_name: str
        :param repeats: Number of repeats for walking
        :type repeats: int
        """
        self._extremity_circles.update_extremity_circle(extremity_name, repeats, False)
    
    def walking_release_action(self, current_key: str) -> None:
        """Performs a key up action of the current key being used when the walking action is complete.
        
        :param current_key: Key to press up
        :type current_key: str"""
        self._keyboard.key_up(current_key)

    def set_displays(self):
        """Displays the required extremity circles and the exercises along with their repeats in view, starting at 0, if not already displayed."""
        if not self._circles_displaying:
            self._extremity_circles.set_extremity_circles_dict(["left_walking", "right_walking", "up_walking", "down_walking"]) #add full gamepad
            self._circles_displaying = True
           
        if not self._exercises_displaying:
            self._exercise_display.set_exercise_display(["walking"])
            self._exercises_displaying = True

    def clear_display(self) -> None:
        """Clears the extremity circles and the exercises being displayed in the view, if not cleared already."""
        if self._circles_displaying:
            self._extremity_circles.clear_extremity_circles()
            self._circles_displaying = False
        if self._exercises_displaying:
            self._exercise_display.clear_exericse_display()
            self._exercises_displaying = False
