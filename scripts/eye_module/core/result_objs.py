"""
Author: Yadong (Adam) Liu
"""

import numpy as np

class FaceResult:
    OUTPUT_SIZE = 7

    # https://docs.openvino.ai/2020.2/_models_intel_face_detection_retail_0004_description_face_detection_retail_0004.html
    """
    The net outputs a blob with shape: [1, 1, N, 7], where N is the number of detected bounding boxes. For each detection, 
    the description has the format: [image_id, label, conf, x_min, y_min, x_max, y_max], where:

    image_id - ID of the image in the batch
    label - predicted class ID
    conf - confidence for the predicted class
    (x_min, y_min) - coordinates of the top left bounding box corner
    (x_max, y_max) - coordinates of the bottom right bounding box corner.
    """

    def __init__(self, output):
        self.image_id = output[0]
        self.label = int(output[1])
        self.confidence = output[2]
        self.position = np.array((output[3], output[4]))  # (x, y)
        self.size = np.array((output[5], output[6]))  # (w, h)

    def rescale_roi(self, roi_scale_factor=1.0):
        self.position -= self.size * 0.5 * (roi_scale_factor - 1.0)
        self.size *= roi_scale_factor

    def resize_roi(self, frame_width, frame_height):
        self.position[0] *= frame_width
        self.position[1] *= frame_height
        self.size[0] = self.size[0] * frame_width - self.position[0]
        self.size[1] = self.size[1] * frame_height - self.position[1]

    def clip(self, width, height):
        min = [0, 0]
        max = [width, height]
        self.position[:] = np.clip(self.position, min, max)
        self.size[:] = np.clip(self.size, min, max)


class HeadResult:
    def __init__(self, output):
        self.head_position_x = output["angle_y_fc"][0]  # Yaw
        self.head_position_y = output["angle_p_fc"][0]  # Pitch
        self.head_position_z = output["angle_r_fc"][0]  # Roll


class LandMarkResult:
    def __init__(self, outputs):
        self.points = outputs
        p = lambda i: self[i]
        self.left_eye = p(0)
        self.right_eye = p(1)
        self.nose_tip = p(2)
        self.left_lip_corner = p(3)
        self.right_lip_corner = p(4)

    def __getitem__(self, idx):
        return self.points[idx]

    def get_array(self):
        return np.array(self.points, dtype=np.float64)
