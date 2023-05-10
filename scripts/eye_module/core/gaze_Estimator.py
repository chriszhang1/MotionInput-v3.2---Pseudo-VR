"""
Author: Yadong (Adam) Liu
Author from MotionInput v2: Guanlin Li
"""

import cv2
import numpy as np

from scripts.eye_module.utils.ie_module import Module


class GazeEstimator(Module):
    """
    Load and configure inference plugins for the specified target devices 
    and performs synchronous and asynchronous modes for the specified infer requests.
    """

    def __init__(self, model):
        super(GazeEstimator, self).__init__(model)

        # For gaze estimation model has three input blobs
        # 1. right_eye_image
        # 2. head_pose_angles
        # 3. left_eye_image

        self.input_blob = []
        self.input_shape = []

        self.input_blob = next(iter(model.input_info))
        self.input_shape = next(iter(model.input_info[self.input_blob].input_data.shape))
        self.output_blob = next(iter(model.outputs))

    def enqueue(self, head_pose, right_eye, left_eye):
        return super(GazeEstimator, self).enqueue({'left_eye_image': left_eye,
                                                    'right_eye_image': right_eye,
                                                    'head_pose_angles': head_pose})

    def start_async(self, headPosition, right_eye_image, left_eye_image):

        head_pose = headPosition.flatten()

        left_eye = cv2.resize(left_eye_image, (60, 60), interpolation=cv2.INTER_AREA)
        left_eye = np.moveaxis(left_eye, -1, 0)

        right_eye = cv2.resize(right_eye_image, (60, 60), interpolation=cv2.INTER_AREA)
        right_eye = np.moveaxis(right_eye, -1, 0)
        self.enqueue(head_pose, right_eye, left_eye)

    def get_gaze_vector(self):
        outputs = self.get_outputs()
        return outputs
