import pickle

from .head_transformation import HeadPlaneProjection
import numpy as np

"""
The following sklearn imports are definitely needed for successful compilation!
When the facial classifier model is unpickled, it requires the sklearn library to run.
"""

from sklearn import svm, metrics
import sklearn.metrics._pairwise_distances_reduction._datasets_pair
import sklearn.metrics._pairwise_distances_reduction._middle_term_computer

MODEL_PATH = "./data/ml_models/head/facial-gesture-classifier.bin"

GESTURE_CLASSES = ["resting", "open_mouth", "raise_eyebrows", "smiling", "fish_face"]

FACIAL_METRICS = [

    (("left-cheek-inner", "lip-left"), ("left-undereye", "mouth-top")),
    (("right-cheek-inner", "lip-right"),  ("right-undereye", "mouth-top")),
    
    (("lip-top", "lip-bottom"), ("mouth-top", "chin-centre")),

    (("lip-left", "lip-right"), ("left-undereye", "right-undereye")),

    (("lip-top-left", "lip-bottom-left"), ("mouth-top", "chin-centre")),
    (("lip-top-right", "lip-bottom-right"), ("mouth-top", "chin-centre")),

    (("left-eyebrow-lower", "left-eye-bottom"), ("nose-tip", "mouth-top")),
    (("right-eyebrow-lower", "right-eye-bottom"), ("nose-tip", "mouth-top")),

]


class _FacialGestureClassifier:

    def __init__(self):

        self.model = pickle.load(open(MODEL_PATH, "rb"))

        self.landmark_frame = None

    def get_metrics(self, projected_frame):

        use_z = True

        metric_count = len(FACIAL_METRICS)
        metrics = np.zeros(metric_count)

        for index in range(metric_count):
                
            metric, norm = FACIAL_METRICS[index]

            metric_val = projected_frame.get_distance_sq(metric[0], metric[1], use_z=use_z)
            norm_val = projected_frame.get_distance_sq(norm[0], norm[1], use_z=use_z)

            metrics[index] = metric_val / norm_val

        return metrics

    def consume(self, landmark_frame):

        self.landmark_frame = landmark_frame

    def evaluate(self):

        prediction_label = GESTURE_CLASSES[0]

        if self.landmark_frame is not None:

            head_transformation = HeadPlaneProjection(self.landmark_frame)

            plane_projected_frame = head_transformation.project_landmarks(self.landmark_frame)

            metrics = self.get_metrics(plane_projected_frame)

            class_prediction = self.model.predict(metrics.reshape(1, -1))[0]

            prediction_label = GESTURE_CLASSES[class_prediction]

        return prediction_label



FacialGestureClassifier = _FacialGestureClassifier() 

"""
Create a singleton classifier that can consume new frames from HeadLandmarkDetector
but only perform classification if gestures are actually needed, in HeadPosition.

This is a workaround, since to optionally perform classification, we need to know 
whether gesture primitives are needed, but we only have access to 'used_primitives' 
in head_position class. This isn't the best imo, but it avoids modifications to
core code.
"""