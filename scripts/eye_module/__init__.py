from .eye_gesture import EyeGesture
from .eye_landmark_detector import EyeLandmarkDetector
from .eye_position import EyePosition
from scripts.core import Module


class EyeModule(Module):
    _position_class = EyePosition
    _gesture_class = EyeGesture
    _landmark_detector_class = EyeLandmarkDetector
    _tracker_names = {"eye"}
