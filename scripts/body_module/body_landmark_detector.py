'''
Author: Jason Ho
'''
import cv2
import mediapipe as mp
import numpy as np

from scripts.core import RawData, LandmarkDetector
from scripts.tools.config import Config


class BodyLandmarkDetector(LandmarkDetector):
    def __init__(self) -> None: 
        self._pose = mp.solutions.pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)
        self._landmark_index_dict = { #there's gotta be a better way of doing this
            "nose":0,
            "left_eye_inner":1,
            "left_eye":2,
            "left_eye_outer":3,
            "right_eye_inner":4,
            "right_eye":5,
            "right_eye_outer":6,
            "left_ear":7,
            "right_ear":8,
            "mouth_left":9,
            "mouth_right":10,
            "left_shoulder":11,
            "right_shoulder":12,
            "left_elbow":13,
            "right_elbow":14,
            "left_wrist":15,
            "right_wrist":16,
            "left_pinky":17,
            "right_pinky":18,
            "left_index":19,
            "right_index":20,
            "left_thumb":21,
            "right_thumb":22,
            "left_hip":23,
            "right_hip":24,
            "left_knee":25,
            "right_knee":26,
            "left_ankle":27,
            "right_ankle":28,
            "left_heel":29,
            "right_heel":30,
            "left_foot_index":31,
            "right_foot_index":32
        }
        self._extremity_landmark_index_dict = {
            "nose_extremity":0,
            "left_wrist_extremity":16, # completely baffled on why the direction needs to be reversed for extremity
            "right_wrist_extremity":15,
            "left_ankle_extremity":28,
            "right_ankle_extremity":27
            }
        config = Config()
        self._ankle_visibility_threshold = config.get_data("modules/body/ankle_visibility_threshold")


    def get_raw_data(self, raw_data: RawData, image: np.ndarray) -> None:
        """Adds the coordinates of all landmarks detected on the image into the RawData instance.

        :param raw_data: RawData instance to add the landmarks to
        :type raw_data: RawData
        :param image: Image to proccess with mediapipe and read the landmarks locations from
        :type image: np.ndarray
        """
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self._pose.process(image)
        pose_landmarks = results.pose_landmarks
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        frame_height, frame_width = image.shape[0], image.shape[1]
        
        if pose_landmarks:
            left_ankle_index = self._landmark_index_dict["left_ankle"]
            right_ankle_index = self._landmark_index_dict["right_ankle"]
            # Only attempt to add data if the whole body is visible, defined mediapipe believing the probability of the right or left ankle being
            # on screen > ankle_visibility_threshold (probs remove this if we want to allow half body exercises ?)
            if (pose_landmarks.landmark[left_ankle_index].visibility > self._ankle_visibility_threshold) \
                or (pose_landmarks.landmark[right_ankle_index].visibility > self._ankle_visibility_threshold):
                for landmark in self._landmark_index_dict.keys():
                    index = int(self._landmark_index_dict[landmark])
                    coordinates = np.array([pose_landmarks.landmark[index].x * frame_width, pose_landmarks.landmark[index].y * frame_height, pose_landmarks.landmark[index].z])
                    raw_data.add_landmark("body", landmark, coordinates)
            
            if len(self._extremity_landmark_index_dict) > 0:
                for landmark in self._extremity_landmark_index_dict.keys():
                    index = int(self._extremity_landmark_index_dict[landmark])
                    coordinates = np.array([pose_landmarks.landmark[index].x * frame_width, pose_landmarks.landmark[index].y * frame_height, pose_landmarks.landmark[index].z])
                    raw_data.add_landmark("body", landmark, coordinates)
                    