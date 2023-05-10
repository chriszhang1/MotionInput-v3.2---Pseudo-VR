"""
Author: Yadong (Adam) Liu
Author from MotionInput v2: Guanlin Li
"""

from scripts.eye_module.core.result_objs import HeadResult
from scripts.eye_module.utils.helper import cut_rois, resize_input
# !/usr/bin/env python3
from scripts.eye_module.utils.ie_module import Module


class HeadPosEstimator(Module):

    def __init__(self, model):
        super(HeadPosEstimator, self).__init__(model)
        self.input_blob = next(iter(model.input_info))
        self.output_blob = next(iter(model.outputs))
        self.input_shape = model.input_info[self.input_blob].input_data.shape

    def preprocess(self, frame, rois):
        # "Frame shape should be [1, c, h, w]"
        inputs = cut_rois(frame, rois)
        inputs = [resize_input(input, self.input_shape) for input in inputs]
        return inputs

    def enqueue(self, input):
        return super(HeadPosEstimator, self).enqueue({self.input_blob: input})

    def start_async(self, frame, rois):
        inputs = self.preprocess(frame, rois)
        for input in inputs:
            self.enqueue(input)

    def get_head_position(self):
        outputs = self.get_outputs()
        return HeadResult(outputs[0])
