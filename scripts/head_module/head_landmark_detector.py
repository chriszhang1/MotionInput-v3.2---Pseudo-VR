"""
Author: Alex Clarke

Migration to mediapipe facial mesh ML model for MotionInput 3.11.
https://google.github.io/mediapipe/solutions/face_mesh

Prior dlib landmark detector implemented by Andrzej Szablewski and Rakshita Kumar.
"""

import os

import cv2
import mediapipe as mp
import numpy as np

from numpy import ndarray

from scripts.core import LandmarkDetector
from scripts.core import RawData
from scripts.tools import Config

from .landmark_frame import get_face_mesh_frame
from .head_gesture_classifier import FacialGestureClassifier

class HeadLandmarkDetector(LandmarkDetector):

    def __init__(self) -> None:

        # initialize camera size
        config = Config()

        self.tracker = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            refine_landmarks=True,
            min_detection_confidence=config.get_data("modules/head/min_detection_confidence"),
            min_tracking_confidence=config.get_data("modules/head/min_tracking_confidence"),
            max_num_faces=1
        )

        self.classifier = FacialGestureClassifier

    def _process_frame(self, frame: np.ndarray) -> tuple:

        # Prepare image array for mediapipe model.
        # See mediapipe demo on their website, setting writeable flags improves performance

        frame.flags.writeable = False

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.tracker.process(frame)

        frame.flags.writeable = True

        # Extract landmarks into a 'landmark frame' from mediapipe datatypes
        landmark_frame = None

        if results.multi_face_landmarks:

            landmark_frame = get_face_mesh_frame(results.multi_face_landmarks[0]) # Only retrieve landmarks from the first detected face

            self.classifier.consume(landmark_frame)

        return frame, landmark_frame

    def get_raw_data(self, raw_data: RawData, image: ndarray) -> None:

        processed_image, landmark_frame = self._process_frame(image)

        if landmark_frame is None:
            return

        # Add useful landmarks to raw_data, using their names as the key field
        for lm_name in landmark_frame.index_map:

            raw_data.add_landmark("head", lm_name, landmark_frame.get_landmark(lm_name, use_z=False))

        # Add nose point as required
        raw_data.add_landmark("head", "nose_point", landmark_frame.get_landmark("nose-tip", use_z=False))
