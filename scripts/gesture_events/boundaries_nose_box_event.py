""" 
Authors: Alexandros Theofanous 
"""
from scripts.tools.config import Config
from .simple_gesture_event import SimpleGestureEvent


class BoundariesNoseBoxEvent(SimpleGestureEvent):
    _bodypart_types = {"speech", "head"}

    def __init__(self, phrase : str, direction : "str") -> None:
        super().__init__({phrase, "nose_position_gesture"}, {phrase}, BoundariesNoseBoxEvent._bodypart_types)
        self._phrase = phrase
        self.direction = direction
        self.config = Config()
        self._gestures = {"speech": {self._phrase: None},
                          "head": {"nose_position_gesture": None}}
        self.nose_box_centre_X = self.config.get_data("events/nose_tracking/nose_box_centre_X")
        self.nose_box_centre_Y = self.config.get_data("events/nose_tracking/nose_box_centre_Y")
        self.nose_box_up_left = 0
        self.nose_box_up_left = 0
        self.sensitivity = self.config.get_data("events/nose_tracking/bound_sensitivity")

    def update(self) -> None:

        self.nose_box_up_left = self.config.get_data("events/nose_tracking/nose_box_up_left_bound")
        self.nose_box_bot_right = self.config.get_data("events/nose_tracking/nose_box_bot_right_bound")

        head_position = self._gestures["head"]["nose_position_gesture"].get_last_position()
        nose_position = head_position.get_landmark("nose_point")
        nose_position_x = nose_position[0]
        nose_position_y = nose_position[1]

        if self.direction == "left" and self.nose_box_bot_right == [0,0]:
            self.nose_box_up_left[0] = nose_position_x
            self.nose_box_up_left[1] = nose_position_y

            self.config.get_editor().update("events/nose_tracking/nose_box_up_left_bound", self.nose_box_up_left)
            self._event_triggers[self._phrase](False,[0,0],1)
        elif self.direction == "right" and self.nose_box_up_left == [0,0]:
            self.nose_box_bot_right[0] = nose_position_x
            self.nose_box_bot_right[1] = nose_position_y


            self.config.get_editor().update("events/nose_tracking/nose_box_bot_right_bound", self.nose_box_bot_right)
            self._event_triggers[self._phrase](False, [0,0], 1)
        elif self.direction != "reset":
            if self.direction == "left":
                self.nose_box_up_left[0] = nose_position_x
                self.nose_box_up_left[1] = nose_position_y
            else:
                self.nose_box_bot_right[0] = nose_position_x
                self.nose_box_bot_right[1] = nose_position_y
            xcentre = (self.nose_box_bot_right[0] + self.nose_box_up_left[0])/2
            ycentre = (self.nose_box_bot_right[1] + self.nose_box_up_left[1])/2

            self.config.get_editor().update("events/nose_tracking/nose_box_bot_right_bound", self.nose_box_bot_right)
            
            self.config.get_editor().update("events/nose_tracking/nose_box_centre_X", xcentre)
            self.config.get_editor().update("events/nose_tracking/nose_box_centre_Y", ycentre)
            self.nose_box_centre_X = self.config.get_data("events/nose_tracking/nose_box_centre_X")
            self.nose_box_centre_Y = self.config.get_data("events/nose_tracking/nose_box_centre_Y")

            adj = self.sensitivity * abs(self.nose_box_bot_right[0] - self.nose_box_up_left[0])

            if adj > 1:
                adj =1

            self._event_triggers[self._phrase](True, [xcentre,ycentre], adj)
        else:
            self.config.get_editor().update("events/nose_tracking/nose_box_up_left_bound", [0,0])
            self.config.get_editor().update("events/nose_tracking/nose_box_bot_right_bound", [0,0])
            self.config.get_editor().update("events/nose_tracking/nose_box_percentage_size", 0.04)
            self.config.get_editor().update("events/nose_tracking/scaling_factor", int(400))

            self._event_triggers[self._phrase](True, nose_position,1)

        self._state = False

    def _check_state(self) -> None:
        self._state = (self._gestures["speech"][self._phrase] is not None
                       ) and self._gestures["head"]["nose_position_gesture"] is not None
