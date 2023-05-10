# Reference https://github.com/Daniil-Osokin/lightweight-human-pose-estimation-3d-demo.pytorch
"""
Author: Yadong (Adam) Liu
Author from MotionInput v2: Guanlin Li
"""

import os

import cv2
import numpy as np

from scripts.eye_module.pose3d.modules.parse_poses import parse_poses


class pose_args:
    def __init__(self) -> None:
        self.model = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "data",
                                  "ml_models", "eye",
                                  "public", "human-pose-estimation-3d-0001", "human-pose-estimation-3d.xml")
        self.device = 'CPU'
        self.height_size = 256
        self.fx = -1


class pose3d:
    def __init__(self, args: pose_args) -> None:

        self.stride = 8
        from scripts.eye_module.pose3d.modules.inference_engine_openvino import InferenceEngineOpenVINO
        self.net = InferenceEngineOpenVINO(args.model, args.device)
        self.base_height = args.height_size
        self.fx = args.fx
        print("pose3d initialized")

    def nose3d(self, frame: np.ndarray) -> np.ndarray:
        if frame is None:
            print("[warning] no frame input in nose 3d")
            return np.array([])

        input_scale = self.base_height / frame.shape[0]
        scaled_img = cv2.resize(frame, dsize=None, fx=input_scale, fy=input_scale)
        scaled_img = scaled_img[:,
                     0:scaled_img.shape[1] - (scaled_img.shape[1] % self.stride)]  # better to pad, but cut out for demo
        if self.fx < 0:  # Focal length is unknown
            self.fx = np.float32(0.8 * frame.shape[1])

        inference_result = self.net.infer(scaled_img)
        poses_3d, poses_2d = parse_poses(inference_result, input_scale, self.stride, self.fx, False)
        edges = []
        if len(poses_3d):
            poses_3d_copy = poses_3d.copy()  # copy
            x = poses_3d_copy[:, 0::4]
            y = poses_3d_copy[:, 1::4]
            z = poses_3d_copy[:, 2::4]
            poses_3d[:, 0::4], poses_3d[:, 1::4], poses_3d[:, 2::4] = -z, x, -y
            poses_3d = poses_3d.reshape(poses_3d.shape[0], 19, -1)[:, :, 0:3]
            # print("[info] pose 3d process finished, return nose position")
            return poses_3d[0][1]
        else:
            print("[info] pose 3d process finished, no human detected")
            return np.array([])


def onlyNose() -> pose3d:
    args = pose_args()
    mypose = pose3d(args)
    print("initialized onlyNose")
    return mypose
