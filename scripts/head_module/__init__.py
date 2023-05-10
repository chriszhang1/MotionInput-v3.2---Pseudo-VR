from typing import Any, Optional

from scripts.core import Module

from .head_gesture import HeadGesture
from .head_landmark_detector import HeadLandmarkDetector
from .head_position import HeadPosition

from .head_calibration import HeadCalibrator

class HeadModule(Module):
    _position_class = HeadPosition
    _gesture_class = HeadGesture
    _landmark_detector_class = HeadLandmarkDetector

    _tracker_names = {"head"}

    @classmethod
    def calibrate(cls,  params: Optional[Any] = None) -> None:

        HeadCalibrator.run()