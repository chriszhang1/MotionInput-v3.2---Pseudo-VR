"""
Author: Andrzej Szablewski
"""
from scripts.tools import Config
from .simple_gesture_event import SimpleGestureEvent


class NoseDirectionTrackingEvent(SimpleGestureEvent):
    """CURRENTLY NOT IN USE, more optimial version of the
    NoseDirectionTrackingEventNoseBox without visuals! Nose Direction tracking
    event. Active if face can be detected and at least 1 gesture is
    active i.e. nose leaves the nosebox (defined by the noseboxpercentagesize).
    Defines the mouse direction vector from the center of the nosebox and
    the nosepoint. Using the vector and the scaling_factor relatively moves
    mouse in that direction.

    [trigger types]:
        "move": relatively moves mouse in the direction of the vector from the
                center of the nosebox to the nosepoint.
    [bodypart types]:
        "head"
    [gestures types]:
        "nose_right_gesture": active when the nosepoint is to the right of
                              the nosebox.
        "nose_left_gesture": active when the nosepoint is to the left of
                             the nosebox.
        "nose_up_gesture": active when the nosepoint is above the nosebox.
        "nose_down_gesture": active when the nosepoint is below the nosebox.
    """
    _event_trigger_types = {"move"}
    _gesture_types = {"nose_right_gesture",
                      "nose_left_gesture",
                      "nose_up_gesture",
                      "nose_down_gesture"}
    _bodypart_types = {"head"}

    def __init__(self):
        super().__init__(NoseDirectionTrackingEvent._gesture_types,
                         NoseDirectionTrackingEvent._event_trigger_types,
                         NoseDirectionTrackingEvent._bodypart_types)
        self._gestures = {
            "head": {
                "nose_right_gesture": None,
                "nose_left_gesture": None,
                "nose_up_gesture": None,
                "nose_down_gesture": None
            }
        }
        config = Config()
        self._scaling_factor = config.get_data(
            "events/nose_tracking/scaling_factor")
        self._nose_box_percentage_size = config.get_data(
            "events/nose_tracking/nose_box_percentage_size")

    def update(self):
        #  nose_box_percentage size is a percentage of the screen dimension
        #  that needs to be travelled by user's nose from the center of
        #  the screen to activate movement.
        dir_dict = {
            "nose_right_gesture": 0,
            "nose_left_gesture": 0,
            "nose_up_gesture": 0,
            "nose_down_gesture": 0
        }

        dir_dict = {
            gesture_name:
                self._scaling_factor *
                (
                    abs(
                        0.5 - self._gestures["head"][gesture_name].get_last_position().get_landmark("nose_point")[
                            0 if gesture_name in ["nose_right_gesture", "nose_left_gesture"] else 1
                        ]
                    )
                    - self._nose_box_percentage_size
                )
                if self._gestures["head"][gesture_name] is not None
                else 0
                for gesture_name in dir_dict
        }
        
        self._event_triggers["move"](
            dir_dict["nose_left_gesture"] - dir_dict["nose_right_gesture"],
            dir_dict["nose_down_gesture"] - dir_dict["nose_up_gesture"]
        )

    def _check_state(self) -> None:
        gesture_obj_list = [
            False if gesture is None
            else True
            for gesture
            in self._gestures["head"].values()
        ]

        self._state = True in gesture_obj_list
