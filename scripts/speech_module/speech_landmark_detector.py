'''
Authors: Samuel Emilolorun
Comments:
This file grabs the recognised words and phrases from Vosk KITA
and tries to match these to Speech Commands
'''
from numpy import ndarray
from scripts.tools.config import Config
from .kita import KITA
from scripts.core import RawData, LandmarkDetector

class SpeechLandmarkDetector(LandmarkDetector):
    kita = None

    def __init__(self) -> None:
        self._active = Config().get_data("modules/speech/enabled")  # read enabled value
        print("Speech Active: ", self._active)
        try:
            SpeechLandmarkDetector.kita = KITA()
            if not SpeechLandmarkDetector.kita.is_running():
                SpeechLandmarkDetector.kita.start()
        except Exception:
            self._active = False

    def get_raw_data(self, raw_data: RawData, image: ndarray) -> None:
        """
        Adds current phrase to RawData Instance so that it can be passed to the position class
        :param raw_data: RawData instance to add the landmarks to
        :type raw_data: RawData
        :param image: Image to proccess with mediapipe and read the landmarks locations from
        :type image: ndarray
        Using Vosk Partial results ensures high speed in speech commands execution
        """

        if not self._active:
            raw_data.add_landmark(bodypart_name="speech", landmark_name="", coordinates=None)
            return

        current_phrase = SpeechLandmarkDetector.kita.current_phrase
        
        raw_data.add_landmark(bodypart_name="speech", landmark_name=current_phrase, coordinates=None)
