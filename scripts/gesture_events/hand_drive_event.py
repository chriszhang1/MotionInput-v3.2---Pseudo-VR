'''
Author: Ben McNally
'''
from scripts.tools.config import Config
from .simple_gesture_event import SimpleGestureEvent
import math


config = Config()

class HandDriveRotateEvent(SimpleGestureEvent):

    """
    takes in Left, Right buttons and checks to see which should be pressed/released. Left/Right buttons pressed
    depending upon angle of hand-drive gesture.
    """

    _gesture_types = {"hand_drive"}
    _event_trigger_types = {"press", "release"}
    _bodypart_types = {"dom_hand", "off_hand"}

    def __init__(self, buttons, threshold):
        self._gestures = {}
        self.initialise_gestures()
        super().__init__(HandDriveRotateEvent._gesture_types, HandDriveRotateEvent._event_trigger_types, HandDriveRotateEvent._bodypart_types)

        self._buttons = {key: [value, False] for key, value in buttons.items()} # direction: [key, currently_pressed]
        self._movement_threshold = threshold # if angle between hands and midpoint exceeds threshold then turn

    def initialise_gestures(self) -> None:
        for hand in self._bodypart_types:
            self._gestures[hand] = {}
            for gesture in self._gesture_types:
                self._gestures[hand][gesture] = None

    def update(self):
        if self._state:
            # get hand coords
            left_hand_coords = self._gestures["off_hand"]["hand_drive"].get_last_position().get_landmark("middle_base")
            right_hand_coords = self._gestures["dom_hand"]["hand_drive"].get_last_position().get_landmark("middle_base")


            # calculate angle between middle bases
            direction = self._check_direction(left_hand_coords, right_hand_coords)

            if direction:
                for key in self._buttons.keys():
                    if direction == key:
                        if self._buttons[key][1] is False:
                            self._buttons[key][1] = True # set button currently_pressed to True
                            self._event_triggers["press"](self._buttons[key][0])
                    elif direction != key:
                        if self._buttons[key][1] is True:
                            self._buttons[key][1] = False
                            self._event_triggers["release"](self._buttons[key][0])
            else:
                # if false, release every button that is currently true
                for key in self._buttons.keys():
                    if self._buttons[key][1] is True:
                        self._buttons[key][1] = False
                        self._event_triggers["release"](self._buttons[key][0])


    def _check_direction(self, left, right):
        angle = self._calculate_angles(left, right)
        deltas = self._get_delta(left, right)
        distance = (deltas[0] + deltas[1])**(1/2)

        if angle * distance > self._movement_threshold: # account for distance hands are apart to prevent from hands needing to rotate more at larger distances
            if left[1] > right[1]:
                return "Left"
            elif left[1] < right[1]:
                return "Right"
        return False
    
    def _calculate_angles(self, hand_coords: float, midpoint_coords: float):
        hand_midpoint_deltas = self._get_delta(hand_coords, midpoint_coords)
        degrees = math.atan2(hand_midpoint_deltas[1], hand_midpoint_deltas[0])*(180/math.pi) # angle between hand position and midpoint
        return degrees

    def _get_delta(self, point1: float, point2: float):
        delta_x = (point1[0] - point2[0])**2
        delta_y = (point1[1] - point2[1])**2
        return [delta_x, delta_y]

    def _check_state(self) -> None:
        self._state = (self._gestures["off_hand"]["hand_drive"] is not None) and (self._gestures["dom_hand"]["hand_drive"] is not None)
        if not self._state:
            for key in self._buttons.keys():
                if self._buttons[key][1] is True:
                    self._buttons[key][1] = False
                    self._event_triggers["release"](self._buttons[key][0])



class HandDriveForwardBackwardEvent(SimpleGestureEvent):
    """
    Measures distance between hand and index middle knuckle to determine key press
    """

    _gesture_types = {"hand_drive"}
    _event_trigger_types = {"press", "release"}
    _bodypart_types = {"dom_hand", "off_hand"}

    def __init__(self, buttons, threshold):
        self._gestures = {}
        self._click_held = {}
        self.initialise_gestures()
        super().__init__(HandDriveForwardBackwardEvent._gesture_types, HandDriveForwardBackwardEvent._event_trigger_types, HandDriveForwardBackwardEvent._bodypart_types)

        self._buttons = {key: [value, False] for key, value in buttons.items()}
        self._movement_threshold = threshold # if change in z-axis exceeds threshold then move forward/backward

    def initialise_gestures(self) -> None:
        for hand in self._bodypart_types:
            self._gestures[hand] = {}
            for gesture in self._gesture_types:
                self._gestures[hand][gesture] = None

    def update(self):
        if self._state:
            # get left hand coords
            left_hand = self._gestures["off_hand"]["hand_drive"].get_last_position()
            left_hand_knuckle_dist = left_hand.get_landmarks_distance("index_base","pinky_base")
            left_hand_thumb_dist = left_hand.get_landmarks_distance("thumb_tip","index_lowerj")

            # get right hand coords
            right_hand = self._gestures["dom_hand"]["hand_drive"].get_last_position()
            right_hand_knuckle_dist = right_hand.get_landmarks_distance("index_base","pinky_base")
            right_hand_thumb_dist = right_hand.get_landmarks_distance("thumb_tip","index_lowerj")

            # trigger Down
            if (left_hand_thumb_dist/left_hand_knuckle_dist) < self._movement_threshold:
                self._trigger_keys("Down")
            # trigger Up
            elif (right_hand_thumb_dist/right_hand_knuckle_dist) < self._movement_threshold:
                self._trigger_keys("Up")
            # release all keys
            else:
                self._trigger_keys(False)

    def _trigger_keys(self, direction):
        if direction:
            for key in self._buttons.keys():
                if direction == key: 
                    if self._buttons[key][1] is False:
                        self._buttons[key][1] = True # set button currently_pressed to True
                        self._event_triggers["press"](self._buttons[key][0])
                elif direction != key:
                    if self._buttons[key][1] is True:
                        self._buttons[key][1] = False
                        self._event_triggers["release"](self._buttons[key][0])
        else:
            for key in self._buttons.keys():
                if self._buttons[key][1] is True:
                    self._buttons[key][1] = False
                    self._event_triggers["release"](self._buttons[key][0])

    def _check_state(self) -> None:
        self._state = (self._gestures["off_hand"]["hand_drive"] is not None) and (self._gestures["dom_hand"]["hand_drive"] is not None)
        if not self._state:
            self._trigger_keys(False)



class HandDriveUpDownEvent(SimpleGestureEvent):

    """
    Triggers key press if pinky tip x-coord > pinky upper knuckle x-coord (i.e. pinky extended perpendicular to clenched fist facing camera)
    """
    _gesture_types = {"hand_drive"}
    _event_trigger_types = {"press", "release"}
    _bodypart_types = {"dom_hand", "off_hand"}

    def __init__(self, buttons):
        self._gestures = {}
        self._click_held = {}
        self.initialise_gestures()
        super().__init__(HandDriveUpDownEvent._gesture_types, HandDriveUpDownEvent._event_trigger_types, HandDriveUpDownEvent._bodypart_types)

        self._buttons = {key: [value, False] for key, value in buttons.items()}

    def initialise_gestures(self) -> None:
        for hand in self._bodypart_types:
            self._gestures[hand] = {}
            for gesture in self._gesture_types:
                self._gestures[hand][gesture] = None

    def update(self):
        if self._state:
            # calculate for left if pinky tip x cooord is > than pinky upperj coord
            # clacualte for right if pinky tip x coord is < than pinky upperj coord
            right_hand = self._gestures["dom_hand"]["hand_drive"].get_last_position()
            right_hand_pinky_upper = right_hand.get_landmark("pinky_upperj")
            right_hand_pinky_tip = right_hand.get_landmark("pinky_tip")

            left_hand = self._gestures["off_hand"]["hand_drive"].get_last_position()
            left_hand_pinky_upper = left_hand.get_landmark("pinky_upperj")
            left_hand_pinky_tip = left_hand.get_landmark("pinky_tip")

            # trigger Down
            if left_hand_pinky_tip[0] > left_hand_pinky_upper[0]:
                self._trigger_keys("Down")
            # trigger Up
            elif right_hand_pinky_tip[0] < right_hand_pinky_upper[0]:
                self._trigger_keys("Up")
            # release all keys
            else:
                self._trigger_keys(False)


    def _trigger_keys(self, direction):
        if direction:
            for key in self._buttons.keys():
                if direction == key: 
                    if self._buttons[key][1] is False:
                        self._buttons[key][1] = True # set button currently_pressed to True
                        self._event_triggers["press"](self._buttons[key][0])
                elif direction != key:
                    if self._buttons[key][1] is True:
                        self._buttons[key][1] = False
                        self._event_triggers["release"](self._buttons[key][0])
        else:
            for key in self._buttons.keys():
                if self._buttons[key][1] is True:
                    self._buttons[key][1] = False
                    self._event_triggers["release"](self._buttons[key][0])

    def _check_state(self) -> None:
        self._state = (self._gestures["off_hand"]["hand_drive"] is not None) and (self._gestures["dom_hand"]["hand_drive"] is not None)
        if not self._state:
            self._trigger_keys(False)