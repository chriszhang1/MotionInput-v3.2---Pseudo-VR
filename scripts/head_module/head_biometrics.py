"""
Author: Alex Clarke

Migrated to mediapipe landmarks for v3.11.

Optimised prior calculations for speed and variable head position.

Prior dlib landmark detector implemented by Andrzej Szablewski and Rakshita Kumar.
"""
from typing import Dict

from scripts.tools import Config
import numpy as np
import math

from .head_gesture_classifier import FacialGestureClassifier

# Avoid calculating the square root wherever possible - when done for all biometrics this is costly
# Often the actual distance is not needed - just the ratio between two distances.
def getSquaredDistance(distanceVector):
    return (distanceVector[0]**2 + distanceVector[1]**2)

"""
Avoid processing by only calculating metrics as they are needed, either as 
a dependency to another metric, or a requested metric from the HeadPosition class.
"""
class HeadBiometrics:
    def __init__(self, landmarks: Dict[str, np.ndarray]):

        """Initializes HeadBiometrics instance and calculates all biometrics.

        :param landmarks: dictionary containing landmarks names
            mapped to their coords
        :type landmarks: Dict[str, numpy.ndarray]
        """
        self._config = Config()

        self._frame_metrics = {}
        self._calib_metrics = dict(self._config.get_data("modules/head/user_calibration"))

        self._landmarks = landmarks
    
        self._calculator_map = {

            "predicted_gesture": self._add_predicted_gesture,

            "head_tilt_angle": self._add_head_tilt_angle,
            "head_turn_ratio": self._add_head_turn_ratio,

            "nose_box_left_offset": self._add_nose_box_left_offset,
            "nose_box_right_offset": self._add_nose_box_right_offset,
            "nose_box_top_offset": self._add_nose_box_top_offset,
            "nose_box_bottom_offset": self._add_nose_box_bottom_offset,

        }

        self._calibration_map = {

            "nose_box_percentage_size": "events/nose_tracking/nose_box_percentage_size",
            "nose_box_centre_X": "events/nose_tracking/nose_box_centre_X",
            "nose_box_centre_Y": "events/nose_tracking/nose_box_centre_Y"

        }        


    def _add_head_turn_ratio(self) -> None:
        """Calculates head turn ratio and stores it in metrics dictionary.
         <1 - head turned left
         >1 - head turned right.
        """
        # Euclidean distance between nose tip and left cheek:
        point_distance_left = getSquaredDistance(
            self._landmarks["nose-tip"] - self._landmarks["left-cheek"]
        )
        # Euclidean distance between nose tip and right cheek:
        point_distance_right = getSquaredDistance(
            self._landmarks["nose-tip"] - self._landmarks["right-cheek"]
        )

        head_turn_ratio = point_distance_left - point_distance_right

        return head_turn_ratio

    def _add_head_tilt_angle(self) -> None:
        """Calculates head tilt towards either shoulder"""

        height_vector = self._landmarks["temple-centre"] - self._landmarks["chin-centre"]

        tilt_angle = math.atan2(height_vector[1], height_vector[0]) + math.pi/2

        return tilt_angle

    def _add_nose_box_left_offset(self) -> None:

        left_offset = self.get_calib_metric("nose_box_centre_X") - self._landmarks["nose-tip"][0]
        
        return left_offset 

    def _add_nose_box_right_offset(self) -> None:

        right_offset = self._landmarks["nose-tip"][0] - self.get_calib_metric("nose_box_centre_X")
        
        return right_offset

    def _add_nose_box_top_offset(self) -> None:

        top_offset = self.get_calib_metric("nose_box_centre_Y") - self._landmarks["nose-tip"][1]

        return top_offset

    def _add_nose_box_bottom_offset(self) -> None:

        bottom_offset = self._landmarks["nose-tip"][1] - self.get_calib_metric("nose_box_centre_Y")

        return bottom_offset

    def _add_predicted_gesture(self) -> None:

        prediction_label = FacialGestureClassifier.evaluate()

        return prediction_label

    """
    Return a metric calculated from the current frame, accessed by its key
    that maps to a calculator function in _calculator_map
    """
    def get_frame_metric(self, metric: str):

        if metric not in self._frame_metrics:

            # Calculate this metric, it hasn't been calculated yet.
            self._frame_metrics[metric] = self._calculator_map[metric]()

        return self._frame_metrics[metric]

    """
    Return a metric stored from the head module's calibration, accessed by a key
    that maps to a path in _calibration_map
    """
    def get_calib_metric(self, metric: str):

        if metric not in self._calib_metrics:

            metric_path = self._calibration_map[metric]
            self._calib_metrics[metric] = self._config.get_data(metric_path)

        return self._calib_metrics[metric]
 