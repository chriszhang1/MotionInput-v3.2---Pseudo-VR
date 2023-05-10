'''
Author: Chris Zhang
'''
from typing import List, Optional
from scripts.gesture_event_handlers.exercise_display import ExerciseDisplay
from scripts.gesture_event_handlers.extremity_circles import ExtremityCircles
from scripts.gesture_event_handlers.keyboard import Keyboard


class PseudoVRActions:
    """Actions for the pseudovr classes. These provide methods for the special walking on the spot + gamepad modes."""
    def __init__(self, exercise_display: ExerciseDisplay, extremity_circles: ExtremityCircles) -> None:
        self._extremity_circles = extremity_circles
        self._exercise_display = exercise_display
        self._keyboard = Keyboard()
        self._circles_displaying = False
        self._exercises_displaying = False
    
    def walking_trigger_action(self, walking_repeats: int, key_list: List[str]) -> None:
        """Performs a keydown action of the keys being used, and increments the number of walking repeats displayed.
        
        :param repeats: Number of repeats for walking
        :type repeats: int
        :param key_list: Key to perform key down
        :type current_key: List[str]
        """
        self._exercise_display.update_exercise_repeats("walking", walking_repeats)
        for key in key_list:
            self._keyboard.key_down(key)
    
    def extremity_trigger_action(self, extremity_name: str, repeats: int, key: Optional[str] = None) -> None:
        """Changes the colour of the activated extremity circle to the activated colour, and the number of repeats. Also performs any key down
        action if required (e.g. if the extremity trigger activated was a button extremity).

        :param extremity_name: Name of activated extremity
        :type extremity_name: str
        :param repeats: Number of repeats for walking
        :type repeats: int
        :param key: Key to perform key down
        :type key: Optional[str]
        """
        self._extremity_circles.update_extremity_circle(extremity_name, repeats, True)
        if key is not None:
            self._keyboard.key_down(key)

    def held_action(self, key_list: List[str]) -> None:
        """Performs a keydown action for the current keys being used, to simulate the key being held.
        
        :param key_list: List of keys to perform key down
        :type current_key: List[str]
        """
        for key in key_list:
            self._keyboard.key_down(key)

    def extremity_release_action(self, extremity_name: str, repeats: int, key: Optional[str] = None) -> None:
        """Changes the colour of the deactivated extremity circle to the deactivated colour, and the number of repeats. Also performs a key up 
        action for any keys required.

        :param extremity_name: Name of deactivated extremity
        :type extremity_name: str
        :param repeats: Number of repeats for walking
        :type repeats: int
        :param key: Key for key up
        :type key: Optional[str]
        """
        self._extremity_circles.update_extremity_circle(extremity_name, repeats, False)
        if key is not None:
            self._keyboard.key_up(key)
    
    def walking_release_action(self, key_list: List[str]) -> None:
        """Performs a key up action of the any keys being used when the walking action is complete.
        
        :param key_list: Keys for key up
        :type key_list: List[str]
        """
        for key in key_list:
            self._keyboard.key_up(key)

    def set_displays(self, extremity_list: List[str]):
        """Displays the required extremity circles and the exercises along with their repeats in view, starting at 0, if not already displayed."""
        if not self._circles_displaying:
            self._extremity_circles.set_extremity_circles_dict(extremity_list)
            self._circles_displaying = True
           
        if not self._exercises_displaying:
            self._exercise_display.set_exercise_display(["walking"])
            self._exercises_displaying = True
            
    def clear_display(self):
        """Clears the extremity circles and the exercises being displayed in the view, if not displayed already."""
        if self._circles_displaying:
            self._extremity_circles.clear_extremity_circles()
            self._circles_displaying = False
        if self._exercises_displaying:
            self._exercise_display.clear_exericse_display()
            self._exercises_displaying = False
        