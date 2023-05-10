'''
Author: Siam Islam
'''

from time import perf_counter
from scripts.core.position import Position
from scripts.tools.config import Config
from .simple_gesture_event import SimpleGestureEvent

# while the hand is not active the we update the location of the cursor
class HandDepthClickEvent(SimpleGestureEvent):
    """EXPERIMENTAL - Should not be connected to the GUI.
    This event is currently not in use and is simply present for testing and future devs.

    Clicks can be triggered by doing a quick forward press motion with the hand. The speed and distance
    the hand needs to move for a click to be triggered can be adjusted by changing the threshold values,
    "max_duration" and "min_distance" in Config.

    In its current state, this gesture event is only suitable for pausing and playing videos or clicking in interfaces
    with large hit targets, due to its high inaccuracy compared to other hand gestures. 
    A potential use case is mapping the click trigger to keyboard buttons, e.g. to space for pausing/playing movies in VLC,
    media buttons for prev/next track etc.
     
    [trigger types]:
        "move": called to update coordinates to the start position of the forward press motion just before calling "click trigger". 
        Called with inputs (palm_center_x_coordinate, palm_center_y_coordinate). 
        Coordinates in percentage of the camera view relative to the left top corner
        "click": called once when the  requirements of this gesture event are met, i.e. there is a sufficient increase
        in the palm height and this change occurs within the specified duration
    [bodypart types]:
        "hand": which hands movement is tracked
    [gestures types]:
        "facing_camera": the hand being tracked is facing the camera

    """
    _event_trigger_types = {"move", "click"}
    _gesture_types = {"facing_camera"}
    _bodypart_types = {"hand"}

    def __init__(self):
        self._gestures = {"hand": {"facing_camera": None}}
        super().__init__(HandDepthClickEvent._gesture_types, HandDepthClickEvent._event_trigger_types, HandDepthClickEvent._bodypart_types)
        self._previous_height = None
        self._start_height = None
        self._time_started = None
        self._click_position = None
        config = Config()
        # the lower the value, the quicker the hand needs to move before a click occurs
        self._max_duration = config.get_data("events/hand_depth_click/max_duration")
        # the higher the value, the more the hand needs to move before a click occurs
        self._min_distance = config.get_data("events/hand_depth_click/min_distance")


    def update(self):
        hand_position = self._gestures["hand"]["facing_camera"].get_last_position()
        current_height = hand_position.get_palm_height()
        
        if self._previous_height is not None:
            if current_height > self._previous_height:   # hand is moving towards screen
                self._check_if_start_of_motion(current_height, hand_position)
            
            # if moving away, check if valid forward press motion occured
            elif self._previous_height > current_height:
                if self._check_if_valid_motion(current_height):
                    # move cursor back to the start position for an instant before clicking
                    if self._event_triggers["move"] is not None: # move trigger is optional
                        self._event_triggers["move"](self._click_position[0], self._click_position[1])
                    self._event_triggers["click"]()
                self._start_height = None # reset start height as hand is moving away
                    
        self._previous_height = current_height

    def _check_if_valid_motion(self, current_height: float) -> bool:
        if self._start_height is not None:
            # stop timers and check if there is a sufficient %increase in palm height and if
            # the motion occured within the specified duration
            change_in_height = current_height - self._start_height
            change_in_height = change_in_height / self._start_height # percentage increase in height
            time_taken = perf_counter() - self._time_started
            if change_in_height > self._min_distance and time_taken < self._max_duration:
                return True
        return False
    
    def _check_if_start_of_motion(self, current_height: float, hand_position: Position) -> None:
        if self._start_height is None:
            self._start_height = current_height
            self._click_position = hand_position.get_landmark("palm_center")
            self._time_started = perf_counter()

    def _check_state(self) -> None:
        self._state = self._gestures["hand"]["facing_camera"] is not None
