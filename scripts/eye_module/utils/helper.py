from typing import Tuple, List

import cv2
import numpy as np
from numpy import clip

from scripts.eye_module.core.result_objs import FaceResult


def cut_roi(frame: np.ndarray, roi: FaceResult) -> np.ndarray:
    p1 = roi.position.astype(int)
    p1 = clip(p1, [0, 0], [frame.shape[-1], frame.shape[-2]])
    p2 = (roi.position + roi.size).astype(int)
    p2 = clip(p2, [0, 0], [frame.shape[-1], frame.shape[-2]])
    return np.array(frame[:, :, p1[1]:p2[1], p1[0]:p2[0]])


def cut_rois(frame: np.ndarray, rois: List[FaceResult]) -> List[np.ndarray]:
    return [cut_roi(frame, roi) for roi in rois]


def resize_input(frame: np.ndarray, target_shape: Tuple[int, ...]) -> np.ndarray:
    assert len(frame.shape) == len(target_shape), \
        "Expected a frame with %s dimensions, but got %s" % \
        (len(target_shape), len(frame.shape))

    assert frame.shape[0] == 1, "Only batch size 1 is supported"
    n, c, h, w = target_shape

    input = frame[0]
    if not np.array_equal(target_shape[-2:], frame.shape[-2:]):
        input = input.transpose((1, 2, 0))  # to HWC
        input = cv2.resize(input, (w, h))
        input = input.transpose((2, 0, 1))  # to CHW

    return input.reshape((n, c, h, w))
