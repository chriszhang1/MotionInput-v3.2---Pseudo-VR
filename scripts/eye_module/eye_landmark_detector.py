"""
Author: Yadong (Adam) Liu
Contributors: Andrzej Szablewski
"""

from typing import List, Optional

import numpy as np

from scripts.core import RawData
from scripts.eye_module.core.result_objs import FaceResult, LandMarkResult
from scripts.eye_module.gaze_main import *
from scripts.eye_module.pose3d.pose3d import onlyNose


class EyeLandmarkDetector:
    def __init__(self) -> None:
        self.my_arg = GazeArgs()
        self.my_process = ProcessOnFrame(self.my_arg)
        self.my_mouse_controller = MouseController(self.my_arg)
        self.my_pose3d_obj = onlyNose()

    def get_raw_data(self, raw_data: RawData, image: np.ndarray) -> None:
        """Adds the xyz coordinates of all the hand landmarks detected on the image into the RawData instance.

        :param raw_data: RawData instance to add the landmarks to
        :type raw_data: RawData
        :param image: Image to process with mediapipe and read the landmarks locations from
        :type image: ndarray
        """

        # NOTE: Old code mirrors the image before process
        image = cv2.flip(image, 1)

        # check if full face has been detected
        detections = self._check_face(image)
        if detections:
            self._add_headbox_landmark(raw_data, detections)

            # Get head info
            # Roll, Pitch, Yaw
            head_info = self._process_head_pos(image)
            self._add_head_angle_landmark(raw_data, head_info)

            # Get FaceLandMark
            landmarks = self._process_face_landmark(image)
            self._add_face_landmark(raw_data, landmarks)

            # calculate gaze
            gaze_vector = self._process_eye_gaze(head_info, landmarks, detections, image)
            self._add_gaze_landmark(raw_data, gaze_vector)

            # Add nose3d
            nose_pos = self._process_pose3d(image)
            self._add_pose3d(raw_data, nose_pos)

    def _process_pose3d(self, frame: np.ndarray) -> np.ndarray:
        coor = self.my_pose3d_obj.nose3d(frame)
        return coor

    @staticmethod
    def _add_pose3d(raw_data: RawData, pose3d: np.array) -> None:
        raw_data.add_landmark("eye", "nose3D", pose3d)

    @staticmethod
    def _add_gaze_landmark(raw_data: RawData, gaze_vector: np.ndarray) -> None:

        # get gaze vector numpy array
        gaze_np = np.array(gaze_vector[0]['gaze_vector'][0])
        raw_data.add_landmark("eye", "eye_gaze", gaze_np)

    @staticmethod
    def _add_face_landmark(raw_data: RawData, landmarks: List[LandMarkResult]) -> None:

        # Currently, only enables 5 points (inside detector)
        if not landmarks:
            return

        landmark = landmarks[0]

        # TODO: redo below in a correct way (this only used for displaying info).
        #       maybe able to use cv2 to inject info directly from here?

        left_eye = landmark.left_eye
        raw_data.add_landmark("eye", "left_eye_OpenVino", left_eye)

        right_eye = landmark.right_eye
        raw_data.add_landmark("eye", "right_eye_OpenVino", right_eye)

        nose_tip = landmark.nose_tip
        raw_data.add_landmark("eye", "nose_tip_OpenVino", nose_tip)

        left_lip_corner = landmark.left_lip_corner
        raw_data.add_landmark("eye", "left_lip_corner_OpenVino", left_lip_corner)

        right_lip_corner = landmark.right_lip_corner
        raw_data.add_landmark("eye", "right_lip_corner_OpenVino", right_lip_corner)

    @staticmethod
    def _add_head_angle_landmark(raw_data: RawData, head_info: np.array) -> None:
        raw_data.add_landmark("eye", "headPos", head_info)

    @staticmethod
    def _add_headbox_landmark(raw_data: RawData, detections: List[FaceResult]) -> None:
        if not detections:
            return
        roi = detections[0]

        # TOP-LEFT coordinate
        coor_tl = roi.position

        # bottom right coordinate
        coor_br = roi.position + roi.size

        raw_data.add_landmark("eye", "headBox_tl", coor_tl)
        raw_data.add_landmark("eye", "headBox_br", coor_br)

    def _check_face(self, frame: np.ndarray) -> List[FaceResult]:
        # Get Face detection
        # Since other three models are depends on face detection. Continue
        # only if detection happens
        detections = self.my_process.face_detector_process(frame)

        return detections

    def _process_head_pos(self, frame: np.ndarray) -> np.ndarray:
        head_pose_angles = self.my_process.head_position_estimator_process(frame)
        head_info = np.array(
            [
                head_pose_angles.head_position_x,
                head_pose_angles.head_position_y,
                head_pose_angles.head_position_z
            ]
        )

        return head_info

    def _process_face_landmark(self, frame: np.ndarray) -> List[LandMarkResult]:
        landmarks = self.my_process.face_landmark_detector_process(frame)

        return landmarks

    def _process_eye_gaze(self, head_info: np.ndarray, landmarks: List[LandMarkResult],
                          roi: List[FaceResult], image: np.ndarray) -> Optional[np.ndarray]:

        # Extract eye landmarks (this length has only size 1) WHY????
        if not landmarks:
            return
        landmark = landmarks[0]

        frame_to_crop = image.copy()
        outputs = self.my_mouse_controller.landmarkPostProcessing(frame_to_crop, landmark, roi, image)

        left_eye = outputs[0]
        right_eye = outputs[1]

        # TODO: refactor inner gaze estimator
        gaze_vector = self.my_process.gaze_estimation_process(head_info, right_eye, left_eye)

        return gaze_vector
