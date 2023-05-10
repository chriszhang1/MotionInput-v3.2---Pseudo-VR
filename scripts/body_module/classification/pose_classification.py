'''
Author: code originally from Motioninput V2, refined by Jason Ho
'''
# This code is based on this tutorial with modifications to include customised and calibrated models, and the distance metrics is also changed.
# https://colab.research.google.com/drive/19txHpN8exWhstO6WVkfmYYVC6uug_oVR


import csv
import os
from typing import Dict, List, Optional

import numpy as np

from scripts.tools.config import Config


class FullBodyPoseEmbedder(object):
    """Converts 3D pose landmarks into 3D embeddings."""
    def __init__(self) -> None:
        # Multiplier to apply to the torso to get minimal body size.
        self._torso_size_factor = 2.5
        self._landmark_names = ['nose','left_eye_inner', 'left_eye', 'left_eye_outer','right_eye_inner', 'right_eye', 'right_eye_outer',
            'left_ear', 'right_ear','mouth_left', 'mouth_right','left_shoulder', 'right_shoulder','left_elbow', 'right_elbow','left_wrist', 'right_wrist',
            'left_pinky_1', 'right_pinky_1','left_index_1', 'right_index_1','left_thumb_2', 'right_thumb_2','left_hip', 'right_hip','left_knee', 'right_knee',
            'left_ankle', 'right_ankle','left_heel', 'right_heel','left_foot_index', 'right_foot_index']

    def __call__(self, landmarks: np.ndarray) -> np.ndarray:
        """Converts 3D pose landmarks into 3D embeddings, returning a numpy array of vectors.
        
        :param landmarks: numpy array of the landmark coordinates
        :type landmarks: np.ndarray
        :return: numpy array representing the pose embedding
        :rtype: np.ndarray
        """
        landmarks = np.copy(landmarks)
        landmarks = self._normalisation(landmarks)
        embedding = self._convert_to_vector(landmarks)
        return embedding

    def _normalisation(self, landmarks: np.ndarray) -> np.ndarray:
        "Noramlise the pose landmarks"
        landmarks = np.copy(landmarks)
        pose_centre = (landmarks[self._landmark_names.index('left_hip')] + landmarks[self._landmark_names.index('right_hip')]) * 0.5
        landmarks -= pose_centre
        pose_size = self._get_pose_size(landmarks, self._torso_size_factor)
        landmarks /= pose_size
        landmarks *= 100
        return landmarks

    def _get_pose_size(self, landmarks: np.ndarray, _torso_size_factor: float) -> float:
        """Calculates pose size by taking the maximum from the torso size and maximum distace from the pose center to other landmarks"""
        landmarks = landmarks[:, :2]
        hip_centre = (landmarks[self._landmark_names.index('left_hip')] + landmarks[self._landmark_names.index('right_hip')]) * 0.5
        shoulder_centre = (landmarks[self._landmark_names.index('left_shoulder')] + landmarks[self._landmark_names.index('right_shoulder')]) * 0.5
        torso_size = np.linalg.norm(shoulder_centre - hip_centre)
        pose_centre = (landmarks[self._landmark_names.index('left_hip')] + landmarks[self._landmark_names.index('right_hip')]) * 0.5
        max_dist = np.max(np.linalg.norm(landmarks - pose_centre, axis=1))
        pose_size = max(torso_size * _torso_size_factor, max_dist)
        return pose_size

    def _convert_to_vector(self, landmarks: np.ndarray) -> np.ndarray:
        """Converts pose landmarks into 3D embedding."""
        embedding = np.array([
            self._get_distance(
                self._get_average(landmarks, 'left_hip', 'right_hip'),
                self._get_average(landmarks, 'left_shoulder', 'right_shoulder')),
            self._get_distance_by_name(landmarks, 'left_hip', 'left_knee'),
            self._get_distance_by_name(landmarks, 'right_hip', 'right_knee'),
            self._get_distance_by_name(landmarks, 'left_knee', 'left_ankle'),
            self._get_distance_by_name(landmarks, 'right_knee', 'right_ankle'),
            self._get_distance_by_name(landmarks, 'left_shoulder', 'left_knee'),
            self._get_distance_by_name(landmarks, 'right_shoulder', 'right_knee'),
            self._get_distance_by_name(landmarks, 'left_ankle', 'right_ankle'),
            self._get_distance_by_name(landmarks, 'left_shoulder', 'left_elbow'),
            self._get_distance_by_name(landmarks, 'right_shoulder', 'right_elbow'),
            self._get_distance_by_name(landmarks, 'left_elbow', 'left_knee'),
            self._get_distance_by_name(landmarks, 'right_elbow', 'right_knee'),
            self._get_distance_by_name(landmarks, 'left_hip', 'left_ankle'),
            self._get_distance_by_name(landmarks, 'right_hip', 'right_ankle'),
            self._get_distance_by_name(landmarks, 'left_shoulder', 'left_ankle'),
            self._get_distance_by_name(landmarks, 'right_shoulder', 'right_ankle'),
            self._get_distance_by_name(landmarks, 'left_shoulder', 'right_shoulder'),
            self._get_distance_by_name(landmarks, 'left_knee', 'right_knee'),
            self._get_distance_by_name(landmarks, 'left_ankle', 'right_ankle'),
        ])
        return embedding

    def _get_average(self, landmarks: np.ndarray, name_from: str, name_to: str) -> float:
        lmk_from = landmarks[self._landmark_names.index(name_from)]
        lmk_to = landmarks[self._landmark_names.index(name_to)]
        average = (lmk_from + lmk_to) * 0.5
        return average

    def _get_distance_by_name(self, landmarks: np.ndarray, name_from: str, name_to: str) -> float:
        lmk_from = landmarks[self._landmark_names.index(name_from)]
        lmk_to = landmarks[self._landmark_names.index(name_to)]
        return self._get_distance(lmk_from, lmk_to)

    def _get_distance(self, lmk_from: float, lmk_to: float) -> float:
        return lmk_to - lmk_from

class PoseSample(object):
    """Object to represent a pose sample."""
    def __init__(self, name: str, landmarks: np.ndarray, class_name: str, embedding: np.ndarray) -> None: #class_name = exercise state e.g. squating_down # name = file name e.q. squating_down.csv
        self.name = name
        self.landmarks = landmarks
        self.class_name = class_name
        self.embedding = embedding

class PoseClassification(object):
    """Classifies pose landmarks."""
    def __init__(self, used_exercises: Optional[set] = None) -> None:
        self._pose_embedder = FullBodyPoseEmbedder()
        self._no_equipment_pose_samples = self.load_samples("no_equipment", self._pose_embedder, used_exercises) #can do _no_equipment_pose_samples.class_name and name
        self._equipment_pose_samples = self.load_samples("equipment", self._pose_embedder, used_exercises)

    def load_samples(self, exercise_mode: str, pose_embedder: FullBodyPoseEmbedder, used_exercises: str) -> List[PoseSample]:
        """Loads pose samples in the form of .csv files from the given folder.
        
        :param exercise_mode: mode of the training model .csv files
        :type exercise_mode: str
        :param pose_embedder: Pose embedder object
        :type pose_embedder: FullBodyPoseEmbedder
        :param used_exercises: list of exercises to only load their .csv files for
        :type used_exercises: str
        :return: List of PoseSample objects for each exercise state
        :rtype: List[PoseSample]
        """
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..","..", "..", "data", "ml_models", "body", exercise_mode)
        if used_exercises is not None:
            fileNames = [name for name in os.listdir(path) if name.endswith('.csv') and name[:-4] in used_exercises]
        else:
            fileNames = [name for name in os.listdir(path) if name.endswith('.csv')]
        pose_samples = []
        self.selected_pose_classes_calibrated = []
        self.selected_pose_classes = []
        for x in fileNames:
            self.selected_pose_classes.append(x[:-4])
            self.selected_pose_classes_calibrated.append(x[:-4] + "_calibrated")
        self.selected_pose_classes += self.selected_pose_classes_calibrated
        print(f"Pose Classes for {exercise_mode} mode:", self.selected_pose_classes)
        for fileName in fileNames:
            # if fileName[:-4] in self.selected_pose_classes:
            if "_calibrated" in fileName[:-4]:
                class_name = fileName[:-4].replace("_calibrated", "")
            else:
                class_name = fileName[:-4] #file name of csv training file
            # Parse CSV.
            with open(os.path.join(path, fileName)) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    landmarks = np.array(row[1:], np.float32).reshape([33, 3])
                    pose_samples.append(PoseSample(
                        name=row[0],
                        landmarks=landmarks,
                        class_name=class_name,
                        embedding=pose_embedder(landmarks),
                ))
        print(f"Number of samples for {exercise_mode} mode:", len(pose_samples))
        return pose_samples

    def __call__(self, pose_landmarks: np.ndarray, used_primitives: Optional[set] = None) -> Dict[str, int]:
        """Classifies given pose landmarks to detect which exercise state is being performed.
        
        :param pose_landmarks: numpy array containing landmark data
        :type pose_landmarks: np.ndarray
        :param used_primitives: Set of primitives from the body position class that need to be checked as exercise states
        :type used_primitives: Optional[set]
        :return: Dictionary of pose samples and their count (how close the exercise is to the one being performed)
        :rtype: Dict[str, int]
        """
        config = Config()
        mode = config.get_data("modules/body/mode")
        if mode == "equipment":
            pose_samples = self._equipment_pose_samples
        else:
            pose_samples = self._no_equipment_pose_samples

        pose_embedding = self._pose_embedder(pose_landmarks)
        euclidean_distances = []
        if used_primitives is None:
            used_pose_samples = pose_samples
        else:
            used_primitives.add("idle")
            used_pose_samples = [sample for sample in pose_samples if sample.class_name in used_primitives] # restricts checked exercises to the ones actually being used
        for sample_idx, sample in enumerate(used_pose_samples):
            euclidean_dist =np.linalg.norm((sample.embedding - pose_embedding) * (1., 1., 0.2))
            euclidean_distances.append([euclidean_dist, sample_idx])

        euclidean_distances = sorted(euclidean_distances, key=lambda x: x[0])
        euclidean_distances = euclidean_distances[:10]
        class_names = [used_pose_samples[sample_idx].class_name for _, sample_idx in euclidean_distances]
        result = {class_name: class_names.count(class_name) for class_name in set(class_names)} #squating_down is a class name
        return result
