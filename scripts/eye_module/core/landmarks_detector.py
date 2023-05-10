"""
Author: Yadong (Adam) Liu
Author from MotionInput v2: Guanlin Li
"""

from scripts.eye_module.core.result_objs import LandMarkResult
from scripts.eye_module.utils.helper import cut_rois, resize_input
from scripts.eye_module.utils.ie_module import Module

"""
https://docs.openvino.ai/2019_R1/_facial_landmarks_35_adas_0002_description_facial_landmarks_35_adas_0002.html
"""

class LandmarksDetector(Module):
    POINTS_NUMBER = 5

    def __init__(self, model):
        super(LandmarksDetector, self).__init__(model)

        self.update = False
        # "Expected 1 input blob"
        # "Expected 1 output blob"
        self.input_blob = next(iter(model.input_info))
        self.output_blob = next(iter(model.outputs))
        self.input_shape = model.input_info[self.input_blob].input_data.shape

    def preprocess(self, frame, rois):
        # "Frame shape should be [1, c, h, w]"
        inputs = cut_rois(frame, rois)

        inputs = [resize_input(input, self.input_shape) for input in inputs]
        return inputs

    def enqueue(self, input):
        return super(LandmarksDetector, self).enqueue({self.input_blob: input})

    def start_async(self, frame, rois):
        inputs = self.preprocess(frame, rois)
        for input in inputs:
            self.enqueue(input)

    def get_landmarks(self):
        outputs = self.get_outputs()
        results = [LandMarkResult(out[self.output_blob].reshape((-1, 2))) \
                   for out in outputs]
        return results
