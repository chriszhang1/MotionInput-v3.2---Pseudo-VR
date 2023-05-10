'''
Authors: Samuel Emilolorun
'''
from scripts.core.module import Module
from scripts.speech_module.kita import KITA
from scripts.speech_module.speech_gesture import SpeechGesture
from scripts.speech_module.speech_landmark_detector import SpeechLandmarkDetector
from scripts.speech_module.speech_position import SpeechPosition


class SpeechModule(Module):
    _position_class = SpeechPosition
    _gesture_class = SpeechGesture
    _landmark_detector_class = SpeechLandmarkDetector

    _tracker_names = {"speech"}

    def reset(self) -> None:
        """Resets all position trackers"""
        for name, tracker in self._position_trackers.items():
            tracker.reset()
        if SpeechModule._landmark_detector_class.kita is not None:
            if SpeechModule._landmark_detector_class.kita.is_running():
                SpeechModule._landmark_detector_class.kita.end()
