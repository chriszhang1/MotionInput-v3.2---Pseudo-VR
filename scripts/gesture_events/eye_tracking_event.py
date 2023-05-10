import numpy as np

from scripts.eye_module.eye_calculation import gaze2screen
from .simple_gesture_event import SimpleGestureEvent
from .. import Config


class EyeTrackingEvent(SimpleGestureEvent):
    # TODO: docstring
    """_summary_
   
    [trigger types]:
    [bodypart types]:
    [gestures types]:
    """
    _event_trigger_types = {"move"}
    _gesture_types = {"gaze_nose3d_gesture"}
    _bodypart_types = {"eye"}

    def __init__(self):
        super().__init__(EyeTrackingEvent._gesture_types,
                         EyeTrackingEvent._event_trigger_types,
                         EyeTrackingEvent._bodypart_types)

        self._config = Config()
        self._gestures = {"eye": {"gaze_nose3d_gesture": None}}

    def update(self):

        # number of mean to take
        num_to_denoise: int = self._config.get_data("modules/eye/num_to_denoise")

        position_list = self._gestures["eye"]["gaze_nose3d_gesture"].get_last_n_positions(num_to_denoise)
        eye_gaze, nose3d = self._denoise(position_list)

        if len(eye_gaze) != 0 and len(nose3d) != 0:
            xper, yper = self._get_coor(eye_gaze, nose3d)

            # TODO: remove below debug code
            # print(xper, yper)
            self._event_triggers["move"](xper, yper)

    def _get_coor(self, eye_gaze, nose3d):

        # x,y
        cal_Coor = gaze2screen(self._config)
        xper, yper = cal_Coor.get_coor(eye_gaze, nose3d)

        return xper, yper

    @staticmethod
    def _denoise(position_list):
        my_gaze = []
        my_noise3D = []
        for i in position_list:

            br = i.get_landmark("headBox_br")
            tl = i.get_landmark("headBox_tl")

            # TODO: rewrite in better way
            if tl is not None and br is not None:
                eye_gaze = i.get_landmark("eye_gaze")
                nose3d = i.get_landmark("nose3D")

                my_gaze.append(eye_gaze)
                if len(nose3d) != 0:
                    my_noise3D.append(nose3d)

        # take column mean
        gaze_pros = np.array(my_gaze).mean(axis=0)
        # print(my_noise3D)
        nose_pros = np.array(my_noise3D).mean(axis=0)

        return gaze_pros, nose_pros

    def _check_state(self) -> None:
        self._state = self._gestures["eye"]["gaze_nose3d_gesture"] is not None
