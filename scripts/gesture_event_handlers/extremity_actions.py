'''
Author: Jason Ho
'''
from typing import List, Optional

from scripts.gesture_event_handlers.pydirect_directx_actions import Keyboard, Clicker
from scripts.tools.config import Config
from .extremity_circles import ExtremityCircles


class ExtremityActions:
    """Actions for the ExtremityTriggerEvent class. This class mainly performs keyboard actions like pressing a key, holding a key, releasing a key, 
    as well as pressing and releasing the left and right mouse keys."""
    def __init__(self, extremity_circles: ExtremityCircles) -> None:
        self._extremity_circles = extremity_circles
        self._keyboard = Keyboard()
        self._clicker = Clicker()
        self._circles_displaying = False

    def trigger_action(self, extremity: str, action_type: str, repeats: int = 0, key: Optional[str] = None) -> None:
        """Performs the action (pressing a specific key down) associated with an extremity when it is triggered, if its action type is keydown.
        If the action type is key press or click, this does not perform it because they are done when the extremity is released. Also changes the
        colour of the extremity circle activated to the activated colour.
        
        :param extremity: name of extremity triggered
        :type extremity: str
        :param action_type: name of action type (key_press, key_down, left_click or right_click)
        :type action_type: str
        :param repeats: number of times the extremity has been repeated
        :type repeats: int
        :param key: name of the key associated with the action, if any
        :type key: Optional[str]
        """
        # action can be keypress, keydown. keydown holds the key
        self._extremity_circles.update_extremity_circle(extremity, repeats, True)
        if action_type == "key_down":
            self._keyboard.key_down(key)

    def held_action(self, action_type: str, key: Optional[str] = None) -> None:
        """Performs the action (pressing a specific key down) associated with an extremity when it is held. This is only when the action type is keydown.

        :param action_type: name of action type (key_press, key_down, left_click or right_click)
        :type action_type: str
        :param key: name of the key associated with the action, if any
        :type key: Optional[str]
        """
        if action_type == "key_down":
            self._keyboard.key_down(key) 

    def release_action(self, extremity: str, action_type: str, repeats: int = 0, key: Optional[str] = None) -> None:
        """Performs the action (pressing a specific key down) associated with an extremity when it is released. Also changes the colour of the
        extremity circle to the deactivated colour.
        
        :param extremity: name of extremity triggered
        :type extremity: str
        :param action_type: name of action type (key_press, key_down, left_click or right_click)
        :type action_type: str
        :param repeats: number of times the extremity has been repeated
        :type repeats: int
        :param key: name of the key associated with the action, if any
        :type key: Optional[str]
        """
        self._extremity_circles.update_extremity_circle(extremity, repeats, False)
        if action_type == "key_press": # a keypress is triggered after it gets released
            self._keyboard.key_press(key)
        elif action_type == "left_click":
            self._clicker.left_click()
        elif action_type == "right_click":
            self._clicker.right_click()
        elif action_type == "key_down":
            self._keyboard.key_up(key)
    
    def set_extremity_circles(self, extremities: Optional[List[str]] = None) -> None:
        """Sets the default displaying of the extremity circles in the view, if not already displaying. This displays specified extremity triggers,
        or the ones that are activated if none are given.
        
        :param extremities: List of extremities to display
        :type extremities: Optional[List[str]]
        """
        if not self._circles_displaying:
            if extremities is None:
                # if no extremities are passed, default is all activated ones
                config = Config().get_editor()
                extremities = [extremity for extremity in config.get_activated_gesture_names("extremity_triggers")] 
            self._extremity_circles.set_extremity_circles_dict(extremities)
            self._circles_displaying = True

    def clear_extremity_circles(self) -> None:
        """Clears the displaying of the extremity circles in the view. """
        self._extremity_circles.clear_extremity_circles()
        self._circles_displaying = False