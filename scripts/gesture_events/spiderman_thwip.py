'''
Author: Ben McNally
'''
from scripts.tools.config import Config
from .simple_gesture_event import SimpleGestureEvent

"""
Spider-Man thwip gesture with palm facing upwards to trigger web sling (LEFT-SHIFT), 
palm facing down to trigger web zip (C)
"""

config = Config()

class SpidermanThwipEvent(SimpleGestureEvent):
    _gesture_types = {"spiderman_thwip"}
    _event_trigger_types = {"press", "release"}
    _bodypart_types = {"hand"}

    def __init__(self, buttons, threshold, is_right_hand):
        self._gestures = {}
        self._click_held = {}
        self.initialise_gestures()
        super().__init__(SpidermanThwipEvent._gesture_types, SpidermanThwipEvent._event_trigger_types, SpidermanThwipEvent._bodypart_types)

        self._initial_position = None
        self._buttons = {key: [value, False] for key, value in buttons.items()}
        self._facing_up = True
        self._key_to_press = buttons["thwip_1"]
        self._is_right_hand = is_right_hand
        self._distance_threshold = threshold

    def initialise_gestures(self) -> None:
        for hand in self._bodypart_types:
            self._gestures[hand] = {}
            for gesture in self._gesture_types:
                self._gestures[hand][gesture] = None

    def _is_facing_up(self, index, pinky):
        if self._is_right_hand:
            if index > pinky and not self._facing_up:
                self._facing_up = True
                self._key_to_press = "thwip_1"
            elif index <= pinky and self._facing_up:
                self._facing_up = False
                self._key_to_press = "thwip_2"
        else:
            if index <= pinky and not self._facing_up:
                self._facing_up = True
                self._key_to_press = "thwip_1"
            elif index > pinky and self._facing_up:
                self._facing_up = False
                self._key_to_press = "thwip_2"

    def update(self):
        if self._state:
            hand = self._gestures["hand"]["spiderman_thwip"].get_last_position()
            pinky_tip = hand.get_landmark("pinky_tip")
            index_tip = hand.get_landmark("index_tip")

            self._is_facing_up(index_tip[0], pinky_tip[0])

            middle_palm_dist = hand.get_landmarks_distance("middle_tip", "index_tip")
            ring_palm_dist = hand.get_landmarks_distance("ring_tip", "pinky_tip")
            finger_tip_dist = hand.get_landmarks_distance("index_tip", "pinky_tip")

            if middle_palm_dist/finger_tip_dist > self._distance_threshold and ring_palm_dist/finger_tip_dist > self._distance_threshold:
                for key in self._buttons.keys():
                    if key == self._key_to_press:
                        if self._buttons[key][1] is False: 
                            self._buttons[key][1] = True
                            self._event_triggers["press"](self._buttons[key][0])
                    elif self._buttons[key][1] is True:
                        self._buttons[key][1] = False
                        self._event_triggers["release"](self._buttons[key][0])
            else:
                for key in self._buttons.keys():
                    if self._buttons[key][1] is True:
                        self._buttons[key][1] = False
                        self._event_triggers["release"](self._buttons[key][0])

    def _check_state(self) -> None:
        self._state = self._gestures["hand"]["spiderman_thwip"] is not None
        if not self._state:
            for key in self._buttons.keys():
                if self._buttons[key][1] is True:
                    self._buttons[key][1] = False
                    self._event_triggers["release"](self._buttons[key][0])