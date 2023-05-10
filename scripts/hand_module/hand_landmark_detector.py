'''
Author: Carmen Meinson
Partially based on the Hand class in the MotionInput v2 code
'''
import cv2
import mediapipe as mp
import numpy as np

from scripts.core import RawData, LandmarkDetector
from scripts.tools import Config


# NB! not the best implementation. just copied some code from old MI and hoped it worked

class HandLandmarkDetector(LandmarkDetector):
    def __init__(self):
        config = Config()
        self.hands = mp.solutions.hands.Hands(
            min_detection_confidence=config.get_data("modules/hand/min_detection_confidence"),
            min_tracking_confidence=config.get_data("modules/hand/min_tracking_confidence"),
            max_num_hands=config.get_data("modules/hand/max_num_hands"),
        )
        self.landmark_names = {
            4: "thumb_tip",
            8: "index_tip",
            12: "middle_tip",
            16: "ring_tip",
            20: "pinky_tip",
            2: "thumb_base",
            5: "index_base",
            9: "middle_base",
            13: "ring_base",
            17: "pinky_base",
            0: "wrist",
            3: "thumb_upperj",
            7: "index_upperj",
            11: "middle_upperj",
            15: "ring_upperj",
            19: "pinky_upperj",
            6: "index_lowerj",
            10: "middle_lowerj"
        }

    def get_raw_data(self, raw_data: RawData, image: np.ndarray) -> None:
        """Adds the xyz coordinates of all the hand landmarks detected on the image into the RawData instance.

        :param raw_data: RawData instance to add the landmarks to
        :type raw_data: RawData
        :param image: Image to process with mediapipe and read the landmarks locations from
        :type image: ndarray
        """
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image.flags.writeable = False
        camdata = self.hands.process(image)

        # TODO is this image var actually used somewhere?
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if camdata.multi_handedness:  # If hand(s) present in frame
            for i in range(0, len(camdata.multi_handedness)):  # For each hand
                bodypart_name = camdata.multi_handedness[i].classification[0].label
                landmarks = camdata.multi_hand_landmarks[i].landmark
                self._add_base_landmarks(raw_data, bodypart_name, landmarks)
                self._add_derived_landmarks(raw_data, bodypart_name)

    def _add_base_landmarks(self, raw_data: RawData, bodypart_name: str, landmarks: dict) -> None:
        # Get raw data from Mediapipe hands
        for lm, name in self.landmark_names.items():
            coordinates = np.array([landmarks[lm].x, landmarks[lm].y, landmarks[lm].z])
            raw_data.add_landmark(bodypart_name, name, coordinates)

    def _add_derived_landmarks(self, raw_data: RawData, bodypart_name: str) -> None:
        self._add_palm_center(raw_data, bodypart_name)
        self._add_palm_normal(raw_data, bodypart_name)

    def _add_palm_center(self, raw_data: RawData, bodypart_name: str) -> None:
        middle_base = raw_data.get_landmark(bodypart_name, "middle_base")
        wrist = raw_data.get_landmark(bodypart_name, "wrist")
        raw_data.add_landmark(bodypart_name, "palm_center", (middle_base + wrist) / 2.0)

    def _add_palm_normal(self, raw_data: RawData, bodypart_name: str) -> None:
        # palm normal is a vector pointing out of the center of the palm. can be used to detect the direction of the hand
        # if the z coordinate of the normal is less than that of the center, means it is closer to the camera and thus the palm is facing the camera
        index_base = raw_data.get_landmark(bodypart_name, "index_base")
        pinky_base = raw_data.get_landmark(bodypart_name, "pinky_base")
        palm_center = raw_data.get_landmark(bodypart_name, "palm_center")
        if bodypart_name == "Left":
            raw_data.add_landmark(bodypart_name, "palm_normal",
                                  np.cross(index_base - palm_center, pinky_base - palm_center) + palm_center)
        elif bodypart_name == "Right":
            raw_data.add_landmark(bodypart_name, "palm_normal",
                                  np.cross(pinky_base - palm_center, index_base - palm_center) + palm_center)
