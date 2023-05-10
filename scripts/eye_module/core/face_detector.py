"""
Author: Yadong (Adam) Liu
Author from MotionInput v2: Guanlin Li
"""

from scripts.eye_module.core.result_objs import FaceResult
from scripts.eye_module.utils.helper import resize_input
from scripts.eye_module.utils.ie_module import Module


class FaceDetector(Module):

    # From old code, confidence_threshold=0.5, roi_scale_factor=1.15 are predefined in old-code
    def __init__(self, model, confidence_threshold=0.5, roi_scale_factor=1.15):
        super(FaceDetector, self).__init__(model)

        # "Expected 1 input blob"
        # "Expected 1 output blob"
        self.input_blob = next(iter(model.input_info))
        self.output_blob = next(iter(model.outputs))
        self.input_shape = model.input_info[self.input_blob].input_data.shape
        self.output_shape = model.outputs[self.output_blob].shape

        # "Confidence threshold is expected to be in range [0; 1]"
        self.confidence_threshold = confidence_threshold

        # "Expected positive ROI scale factor"
        self.roi_scale_factor = roi_scale_factor

    def preprocess(self, frame):
        # "Frame shape should be [1, c, h, w]"
        input = resize_input(frame, self.input_shape)
        return input

    def start_async(self, frame):
        input = self.preprocess(frame)
        self.enqueue(input)

    def enqueue(self, input):
        return super(FaceDetector, self).enqueue({self.input_blob: input})

    def get_roi_proposals(self, frame):
        outputs = self.get_outputs()[0][self.output_blob]
        # outputs shape is [N_requests, 1, 1, N_max_faces, 7]

        frame_width = frame.shape[-1]
        frame_height = frame.shape[-2]

        results = []
        for output in outputs[0][0]:
            result = FaceResult(output)
            if result.confidence < self.confidence_threshold:
                break  # results are sorted by confidence decrease

            result.resize_roi(frame_width, frame_height)
            result.rescale_roi(self.roi_scale_factor)
            result.clip(frame_width, frame_height)

            results.append(result)
        return results
