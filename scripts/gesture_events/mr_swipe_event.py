'''
Author: Ben McNally
'''
from scripts.tools.config import Config
from .simple_gesture_event import SimpleGestureEvent

"""
need to establish initial position of hand, and then calculate if hand movement
is left, right, above, or below this position then press appropriate arrow button

centre_grid if 0.3 < x <= 0.6 and 0.3 < y <= 0.6
"""

class MRSwipeEvent(SimpleGestureEvent):

    _event_trigger_types = {"up", "down", "right", "left", "press"}
    _bodypart_types = {"hand"}

    def __init__(self, horizontal, sensitivity, threshold_min, threshold_max):
        config = Config()
        self._gesture_types = {"mr_swipe"}
        self._gestures = {}
        self._click_held = {}
        self.initialise_gestures()
        super().__init__(self._gesture_types, MRSwipeEvent._event_trigger_types, MRSwipeEvent._bodypart_types)

        # user must initialise gesture in centre before they can scroll
        self._horizontal = horizontal # True for left/right, False for up/down
        self._started = False # must be true to trigger movement, True after gesture performed in centre grid
        self._counter = 0 # if > self._sensitivity then button is held down
        self._sensitivity = sensitivity # number of frames before button held down
        self._previous_direction = None # compare to current direction to check when to press button initially
        self._threshold_min = threshold_min # if coord <= value, move left/down
        self._threshold_max =  threshold_max # if coord > value, move right/up

    def initialise_gestures(self) -> None:
        for hand in self._bodypart_types:
            self._gestures[hand] = {}
            self._click_held[hand] = {}
            for gesture in self._gesture_types:
                self._gestures[hand][gesture] = None
                self._click_held[hand] = False


    def update(self):
        if self._state:
            hand_position = self._gestures["hand"]["mr_swipe"].get_last_position()
            hand_coords = hand_position.get_landmark("middle_tip") # get hand coords
            if self._started is not True:
                self._started = self._check_is_centre(hand_coords) # only start after gesture performed in centre grid
            else:
                direction = self._check_hand_pos(hand_coords) # get direction user is moving in

                if direction:
                    if direction == self._previous_direction and not self._check_is_centre(hand_coords):
                        self._counter += 1
                    else:
                        self._counter = 0

                    for hand, gestures in self._gestures.items():
                        for gesture_name, gesture in gestures.items():
                            if gesture is not None:
                                if not self._click_held[hand]:
                                    self._click_held[hand] = True
                                if self._previous_direction != direction:
                                    self._event_triggers["press"](direction)
                                elif self._click_held[hand] and self._counter > self._sensitivity:
                                    self._event_triggers[direction]()
                        
                            elif self._click_held[hand]:
                                self._click_held[hand] = False

                self._previous_direction = direction

    def _check_is_centre(self, coords):
        if self._threshold_min < coords[0] <= self._threshold_max and self._threshold_min < coords[1] <= self._threshold_max:
            return True
        return False

    def _check_hand_pos(self, coords):
        if self._horizontal:
            if coords[0] > self._threshold_max:
                return "right"
            elif coords[0] <= self._threshold_min:
                return "left"
        elif not self._horizontal:
            if coords[1] > self._threshold_max:
                return "up"
            elif coords[1] <= self._threshold_min:
                return "down"
        return False

    def _check_state(self) -> None:
        self._state = (self._gestures["hand"]["mr_swipe"] is not None)
        if not self._state:
            self._started = False
            self._counter = 0
            self._previous_direction = None