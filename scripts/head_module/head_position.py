"""
HeadPosition class for determining facial gestures from raw facial measurements (head_biometrics.py)
Reimplemented for v3.11 by Alex Clarke.
"""

from typing import Dict, Optional, Set

import numpy as np

from scripts.core import Position
from scripts.head_module.head_biometrics import HeadBiometrics

from .head_calculator import *

class HeadPosition(Position):

    def __init__(self, raw_data: Dict[str, np.ndarray],
                 used_primitives: Set[str] = None) -> None:
        self._landmarks = raw_data

        self._used_primitives = used_primitives
        self._primitives = {}

        self._calculators = {

            "smiling": smiling_calculator,
            "raise_eyebrows": raise_eyebrows_calculator,
            "fish_face": fish_face_calculator,
            "open_mouth": open_mouth_calculator,

            "nose_point": nose_point_calculator,

            "nose_left": nose_left_calculator,
            "nose_right": nose_right_calculator,

            "nose_up": nose_up_calculator,
            "nose_down": nose_down_calculator,

            "turn_left": head_turn_left_calculator,
            "turn_right": head_turn_right_calculator,

            "tilt_left": head_tilt_left_calculator,
            "tilt_right": head_tilt_right_calculator,
        }

        # firstly calculate biometrics, then calculate primitives
        if self._landmarks is not None:
            self._calculate_primitives()

    def get_primitives_names(self) -> Set[str]:
        return self._used_primitives

    def get_primitive(self, name: str) -> Optional[bool]:
        """Returns the state of the given primitive in the Position if it has
         been calculated. Returns None If the primitive has not been
         calculated, hence if it either is not defined for current module
         or landmarks needed to calculate it were not provided.

        :param name: name of the primitive (e.g. "palm_facing_camera"
            or "index_pinched")
        :type name: str
        :return: state of the primitive
        :rtype: Optional[bool]
        """
        if name not in self._primitives:
            return None
        return self._primitives[name]

    def get_landmark(self, name: str) -> Optional[np.ndarray]:
        """Returns the coordinates of the landmark.
        Returns None if the landmarks was not provided to
        the Position on initialization

        :param name: name of the landmark (e.g. "index_tip" or "wrist")
        :type name: str
        :return: coordinates of the landmark
        :rtype: Optional[np.ndarray]
        """
        if name not in self._landmarks:
            return None
        return self._landmarks[name]

    """
    Only calculate the necessary primitives
    """
    def _calculate_primitives(self):

        current_gesture = "resting"

        if "gesture_prediction" in self._landmarks:

            current_gesture = self._landmarks["gesture_prediction"]


        head_biometrics = HeadBiometrics(self._landmarks)

        for primitive in self._used_primitives:

            if primitive in self._calculators:

                calculator = self._calculators[primitive]

                self._primitives[primitive] = calculator.calculate(head_biometrics)
            
            elif current_gesture == primitive:

                self._primitives[primitive] = True

            else:

                self._primitives[primitive] = False

