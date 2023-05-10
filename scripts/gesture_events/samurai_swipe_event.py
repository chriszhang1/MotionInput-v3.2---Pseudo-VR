'''
Author: Ben McNally
'''
from scripts.tools.config import Config
from .simple_gesture_event import SimpleGestureEvent

config = Config()

class SamuraiSwipeEvent(SimpleGestureEvent):
    
    _gesture_types = {"samurai_swipe"}
    _event_trigger_types = {"move", "press", "release"}
    _bodypart_types = {"dom_hand", "off_hand"}

    def __init__(self, sensitivity):
        self._gestures = {}
        self.initialise_gestures()
        super().__init__(SamuraiSwipeEvent._gesture_types, SamuraiSwipeEvent._event_trigger_types, SamuraiSwipeEvent._bodypart_types)
        self._click_held = False
        self._current_hand = "dom_hand"
        self._sensitivity = sensitivity

    def initialise_gestures(self) -> None:
        for hand in self._bodypart_types:
            self._gestures[hand] = {}
            for gesture in self._gesture_types:
                self._gestures[hand][gesture] = None

    def update(self):
        if self._state:
            # which hand is making gesture
            if self._gestures["dom_hand"]["samurai_swipe"] is None:
                self._current_hand = "off_hand"
            elif self._current_hand != "dom_hand":
                self._current_hand = "dom_hand"

            # get hand coords
            hand_position = self._gestures[self._current_hand]["samurai_swipe"].get_last_position()
            middle_coords = hand_position.get_landmark("middle_tip")
            pinch_dist = hand_position.get_landmarks_distance("index_tip", "thumb_tip")
            pinky_dist = hand_position.get_landmarks_distance("pinky_base", "pinky_tip")
            
            # mouse follow hand
            self._event_triggers["move"](middle_coords[0], middle_coords[1])

            #divide by pinky_dist for consistency with varying hand distance from screen
            if pinch_dist/pinky_dist > self._sensitivity:
                # press mouse if not already held
                if not self._click_held:
                    self._click_held = True
                    if self._event_triggers["press"] is not None:
                        self._event_triggers["press"]()
            else:
                if self._click_held:
                    self._click_held = False
                    if self._event_triggers["release"] is not None: 
                        self._event_triggers["release"]()

    def _check_state(self) -> None:
        self._state = (self._gestures["dom_hand"]["samurai_swipe"] is not None) or (self._gestures["off_hand"]["samurai_swipe"] is not None) 
        if not self._state:
            if self._gestures[self._current_hand]["samurai_swipe"] is None:
                self._click_held = False
                self._state = False
                if self._event_triggers["release"] is not None: 
                    self._event_triggers["release"]()