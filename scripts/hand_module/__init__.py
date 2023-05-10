'''
Author: Carmen Meinson
'''
from typing import Any, Optional

from scripts.core.module import Module
from .calibrate_depth import DepthCalibration
from .hand_gesture import HandGesture
from .hand_landmark_detector import HandLandmarkDetector
from .hand_position import HandPosition


class HandModule(Module):
    _position_class = HandPosition
    _gesture_class = HandGesture
    _landmark_detector_class = HandLandmarkDetector

    _tracker_names = {"Left", "Right"}

    @classmethod
    def calibrate(cls,  params: Optional[Any] = None) -> None:
        if params == 'depth':
            depth_calibrator = DepthCalibration()
            depth_calibrator.calibrate()

