"""
Author: Andrzej Szablewski
"""
from scripts.tools import Config
from .simple_gesture_event import SimpleGestureEvent


class NoseDirectionTrackingEventNoseBox(SimpleGestureEvent):
    """Nose Direction tracking event with visual nosebox and nosepoint.
    Because of the visual features, always active when face and the nosepoint
    can be detected (nose_position_gesture). Mouse movement active only when
    at least one of other nose gestures is active. Defines the mouse direction
    vector from the center of the nosebox and nosepoint. Using the vector and
    the scaling_factor relatively moves mouse in that direction.

    [trigger types]:
        "move": relatively moves mouse in the direction of the vector from the
                center of the nosebox to the nosepoint.
        "nose_box": visualizing nosebox and current nosepoint position
    [bodypart types]:
        "head"
    [gestures types]:
        "nose_right_gesture": active when the nosepoint is to the right of
                              the nosebox.
        "nose_left_gesture": active when the nosepoint is to the left of
                             the nosebox.
        "nose_up_gesture": active when the nosepoint is above the nosebox.
        "nose_down_gesture": active when the nosepoint is below the nosebox.
        "nose_position_gesture": active when a face and the nosepoint can be
                                 detected.
    """
    _event_trigger_types = {"move",
                            "nose_box",
                            "remove_nose_box"}

    _gesture_types = {"nose_right_gesture",
                      "nose_left_gesture",
                      "nose_up_gesture",
                      "nose_down_gesture",
                      "nose_position_gesture"}
    _bodypart_types = {"head"}

    def __init__(self):
        super().__init__(
            NoseDirectionTrackingEventNoseBox._gesture_types,
            NoseDirectionTrackingEventNoseBox._event_trigger_types,
            NoseDirectionTrackingEventNoseBox._bodypart_types
        )
        self._gestures = {
            "head": {
                "nose_right_gesture": None,
                "nose_left_gesture": None,
                "nose_up_gesture": None,
                "nose_down_gesture": None,
                "nose_position_gesture": None,
            }
        }
        self.config = Config()
        self._scaling_factor = self.config.get_data(
            "events/nose_tracking/scaling_factor")
        self._nose_box_percentage_size = self.config.get_data(
            "events/nose_tracking/nose_box_percentage_size")
        self.nose_box_centre_X = self.config.get_data(
            "events/nose_tracking/nose_box_centre_X")
        self.nose_box_centre_Y = self.config.get_data(
            "events/nose_tracking/nose_box_centre_Y")

    def update(self):
        self.nose_box_centre_X = self.config.get_data(
            "events/nose_tracking/nose_box_centre_X")
        self.nose_box_centre_Y = self.config.get_data(
            "events/nose_tracking/nose_box_centre_Y")
        #  nose_box_percentage size is a percentage of the screen dimension that needs to be travelled
        #  by user's nose from the center of the screen to activate movement.
        dir_dict = {
            "nose_right_gesture": 0,
            "nose_left_gesture": 0,
            "nose_up_gesture": 0,
            "nose_down_gesture": 0
        }

        if self._gestures["head"]["nose_right_gesture"] is not None:
            dir_dict["nose_right_gesture"] = self._scaling_factor * (abs(self.nose_box_centre_X - self._gestures["head"][
                "nose_right_gesture"].get_last_position().get_landmark("nose_point")[0]) - self._nose_box_percentage_size)
        if self._gestures["head"]["nose_left_gesture"] is not None:
            dir_dict["nose_left_gesture"] = self._scaling_factor * (abs(self.nose_box_centre_X - self._gestures["head"][
                "nose_left_gesture"].get_last_position().get_landmark("nose_point")[0]) - self._nose_box_percentage_size)
        if self._gestures["head"]["nose_up_gesture"] is not None:
            dir_dict["nose_up_gesture"] = self._scaling_factor * (abs(self.nose_box_centre_Y - self._gestures["head"][
                "nose_up_gesture"].get_last_position().get_landmark("nose_point")[1]) - self._nose_box_percentage_size)
        if self._gestures["head"]["nose_down_gesture"] is not None:
            dir_dict["nose_down_gesture"] = self._scaling_factor * (abs(self.nose_box_centre_Y - self._gestures["head"][
                "nose_down_gesture"].get_last_position().get_landmark("nose_point")[1]) - self._nose_box_percentage_size)

        self._event_triggers["move"](
            dir_dict["nose_right_gesture"] - dir_dict["nose_left_gesture"],
            dir_dict["nose_down_gesture"] - dir_dict["nose_up_gesture"]
        )

        self._event_triggers["nose_box"](
            self._gestures["head"]["nose_position_gesture"].get_last_position(
            ).get_landmark("nose_point")
        )

    def force_deactivate(self) -> None:
        """remove nose box when mode was changed"""
        self._event_triggers["remove_nose_box"]()

    def _check_state(self) -> None:
        # Because of the continuous nose tracking for visual!!!
        self._state = \
            self._gestures["head"]["nose_position_gesture"] is not None
