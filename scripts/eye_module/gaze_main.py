"""
Author: Yadong (Adam) Liu
Author from MotionInput v2: Guanlin Li
"""

# Reference https://github.com/nullbyte91/Computer-Pointer-Controller

import logging as log
import os
import os.path as osp
import time

import cv2
import numpy as np
from openvino.inference_engine import IENetwork

# from .utils.helper import cut_rois, resize_input
from scripts.eye_module.core.face_detector import FaceDetector
from scripts.eye_module.core.gaze_Estimator import GazeEstimator
from scripts.eye_module.core.headPos_Estimator import HeadPosEstimator
from scripts.eye_module.core.landmarks_detector import LandmarksDetector
from scripts.eye_module.utils.ie_module import load_iecore

DEVICE_KINDS = ['CPU', 'GPU', 'FPGA', 'MYRIAD', 'HETERO', 'HDDL']


class GazeArgs:
    def __init__(self):
        # for the detail information in each arguments please check the help in build_argparser()

        self.i = 'cam'
        self.mode_face_detection = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "data",
                                                "ml_models", "eye",
                                                "intel", "face-detection-retail-0004", "FP32",
                                                "face-detection-retail-0004.xml")
        self.d_fd = 'CPU'
        self.t_fd = 0.4
        self.o_fd = False
        self.model_head_position = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "data",
                                                "ml_models", "eye",
                                                "intel", "head-pose-estimation-adas-0001", "FP32",
                                                "head-pose-estimation-adas-0001.xml")
        self.d_hp = 'CPU'
        self.o_hp = True  # Show Head Position output
        self.model_landmark_regressor = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "data",
                                                     "ml_models", "eye",
                                                     "intel", "facial-landmarks-35-adas-0002", "FP32",
                                                     "facial-landmarks-35-adas-0002.xml")
        self.d_lm = 'CPU'
        self.o_lm = False  # Show Landmark detection output
        self.model_gaze = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "data",
                                       "ml_models", "eye",
                                       "intel", "gaze-estimation-adas-0002", "FP32",
                                       "gaze-estimation-adas-0002.xml")
        self.d_gm = 'CPU'
        self.o_gm = True  # Show Gaze estimation output
        self.o_mc = False
        self.exp_r_fd = 1.15
        self.cw = 0
        self.perf_stats = False
        self.cpu_lib = ''
        self.gpu_lib = ''
        self.o = ''
        self.no_show = False
        self.timelapse = False
        self.crop_width = 0
        self.crop_height = 0


class ProcessOnFrame:
    # Queue size will be used to put frames in a queue for
    # Inference Engine
    QUEUE_SIZE = 1

    def __init__(self, args):
        start_time = time.perf_counter()

        # # Load face detection model on Inference Engine
        face_detector_net = load_iecore(args.d_fd, args.mode_face_detection)
        # # Load Headposition model on Inference Engine
        head_position_net = load_iecore(args.d_hp, args.model_head_position)
        # # Load Landmark regressor model on Inference Engine
        landmarks_net = load_iecore(args.d_lm, args.model_landmark_regressor)
        # # Load gaze estimation model on IE
        gaze_net = load_iecore(args.d_gm, args.model_gaze)

        stop_time = time.perf_counter()
        # print("[info] 4 Gaze Models are loaded")
        # print("[INFO] Model Load Time: {}".format(stop_time - start_time))

        # Configure Face detector [detection threshold, ROI Scale]
        self.face_detector = FaceDetector(face_detector_net,
                                          confidence_threshold=args.t_fd,
                                          roi_scale_factor=args.exp_r_fd)

        # Configure Head Pose Estimation
        self.head_estimator = HeadPosEstimator(head_position_net)

        # Configure Landmark regressor
        self.landmarks_detector = LandmarksDetector(landmarks_net)

        # Configure Gaze Estimation
        self.gaze_estimator = GazeEstimator(gaze_net)

        # Face detector
        self.face_detector.deploy()

        # Head Position Detector
        self.head_estimator.deploy()

        # Landmark detector
        self.landmarks_detector.deploy()

        # Gaze Estimation
        self.gaze_estimator.deploy()

        # print("[info] 4 Gaze Models are deployed")

    def load_model(self, model_path):
        """
        Initializing IENetwork(Inference Enginer) object from IR files:
        
        Args:
        Model path - This should contain both .xml and .bin file

        :return Instance of IENetwork class
        """

        model_path = osp.abspath(model_path)
        model_description_path = model_path
        model_weights_path = osp.splitext(model_path)[0] + ".bin"

        # Load model on IE
        model = IENetwork(model=model_description_path, weights=model_weights_path)
        # model = IECore().read_network(model=model_description_path, weights=model_weights_path)
        # log.info("Model is loaded")

        return model

    def frame_pre_process(self, frame):
        """
        Pre-Process the input frame given to model

        Args:
        frame: Input frame from video stream

        Return:
        frame: Pre-Processed frame
        """

        orig_image = frame.copy()
        frame = frame.transpose((2, 0, 1))  # HWC to CHW
        frame = np.expand_dims(frame, axis=0)
        return frame

    def face_detector_process(self, frame):
        """
        Predict Face detection

        Args:
        The Input Frame

        return: roi [xmin, xmax, ymin, ymax]
        """
        frame = self.frame_pre_process(frame)

        # Clear Face detector from previous frame
        self.face_detector.clear()

        # When we use async IE use buffer by using Queue
        self.face_detector.start_async(frame)

        # Predict and return ROI
        rois = self.face_detector.get_roi_proposals(frame)

        if self.QUEUE_SIZE < len(rois):
            log.warning("Too many faces for processing." \
                        " Will be processed only %s of %s." % \
                        (self.QUEUE_SIZE, len(rois)))
            rois = rois[:self.QUEUE_SIZE]

        self.rois = rois

        return rois

    def head_position_estimator_process(self, frame):
        """
        Predict head_position

        Args:
        The Input Frame

        :return headPoseAngles[angle_y_fc, angle_p_fc, angle_2=r_fc]
        """
        frame = self.frame_pre_process(frame)

        # Clean Head Position detection from previous frame
        self.head_estimator.clear()

        # Predict and return head position[Yaw, Pitch, Roll]
        self.head_estimator.start_async(frame, self.rois)
        headPoseAngles = self.head_estimator.get_head_position()

        return headPoseAngles

    def face_landmark_detector_process(self, frame):
        """
        Predict Face Landmark
        
        Args:
        The Input Frame

        :return landmarks[left_eye, right_eye, nose_tip, left_lip_corner, right_lip_corner]
        """
        frame = self.frame_pre_process(frame)

        # Clean Landmark detection from previous frame
        self.landmarks_detector.clear()

        # Predict and return landmark detection[left_eye, right_eye, nose_tip, 
        # left_lip_corner, right_lip_corner]
        self.landmarks_detector.start_async(frame, self.rois)
        landmarks = self.landmarks_detector.get_landmarks()

        return landmarks

    def gaze_estimation_process(self, headPositon, right_eye, left_eye):
        """
        Predict Gaze estimation
        
        Args:
        The Input Frame

        :return gaze_vector
        """

        # Clear gaze vector from the previous frame
        self.landmarks_detector.clear()

        # Get the gaze vector
        self.gaze_estimator.start_async(headPositon, right_eye, left_eye)
        gaze_vector = self.gaze_estimator.get_gaze_vector()
        return gaze_vector

    # TODO: need to remain in new MI?
    # def get_performance_stats(self):
    #     stats = {
    #         'face_detector': self.face_detector.get_performance_stats(),
    #         'landmarks': self.landmarks_detector.get_performance_stats(),
    #         'head_estimator': self.head_estimator.get_performance_stats(),
    #         'gaze_estimator': self.gaze_estimator.get_performance_stats(),
    #     }
    #
    #     return stats


class MouseController:
    BREAK_KEY_LABELS = "q(Q) or Escape"
    BREAK_KEYS = {ord('q'), ord('Q'), 27}

    def __init__(self, args):
        self.frame_processor = ProcessOnFrame(args)
        self.display = not args.no_show
        self.print_perf_stats = args.perf_stats

        self.fd_out = args.o_fd  # Face detection
        self.hp_out = args.o_hp  # Head position
        self.lm_out = args.o_lm  # Land mark detection
        self.gm_out = args.o_gm  # Gaze detection
        self.mc_out = args.o_mc  # Mouse counter

        self.frame_time = 0
        self.frame_start_time = 0
        self.fps = 0
        self.frame_num = 0
        self.frame_count = -1
        self.right_eye_coords = None
        self.left_eye_coords = None

        self.input_crop = None
        if args.crop_width and args.crop_height:
            self.input_crop = np.array((args.crop_width, args.crop_height))

        self.frame_timeout = 0 if args.timelapse else 1

        # print("[info] gaze mouseController object initialized")

    # def update_fps(self):
    #     """
    #     Calculate FPS
    #     """
    #     now = time.time()
    #     self.frame_time = now - self.frame_start_time
    #     self.fps = 1.0 / self.frame_time
    #     self.frame_start_time = now
    #     return self.fps
    #
    # def draw_detection_roi(self, frame, roi):
    #     """
    #     Draw Face detection bounding Box
    #
    #     Args:
    #     frame: The Input Frame
    #     roi: [xmin, xmax, ymin, ymax]
    #     """
    #     for i in range(len(roi)):
    #         # Draw face ROI border
    #         cv2.rectangle(frame,
    #                     tuple(roi[i].position), tuple(roi[i].position + roi[i].size),
    #                     (0, 220, 0), 2)

    def createEyeBoundingBox(self, point1, point2, scale=1.8):
        """
        Create a Eye bounding box using Two points that we got from headposition model

        Args:
        point1: First Point coordinate
        point2: Second Point coordinate
        """

        # Normalize the two points
        size = cv2.norm(np.float32(point1) - point2)
        width = int(scale * size)
        height = width

        # Find x, y mid point
        midpoint_x = (point1[0] + point2[0]) / 2
        midpoint_y = (point1[1] + point2[1]) / 2

        # Calculate eye x, y point
        startX = midpoint_x - (width / 2)
        startY = midpoint_y - (height / 2)
        return [int(startX), int(startY), int(width), int(height)]

    def landmarkPostProcessing(self, frame, landmarks, roi, org_frame):
        """
        Calculate right eye bounding box and left eye bounding box by using
        landmark keypoints

        Args:
        frame: Frame to resize/crop
        landmark: Keypoints
        roi: Detection output of Facial detection model
        org_frame: Orginal frame

        return:
        list of left and right bounding box
        """
        faceBoundingBoxWidth = roi[0].size[0]
        faceBoundingBoxHeight = roi[0].size[1]

        # keypoints = [landmarks.left_eye,
        #              landmarks.right_eye,
        #              landmarks.nose_tip,
        #              landmarks.left_lip_corner,
        #              landmarks.right_lip_corner]

        faceLandmarks = []
        left_eye_x = (landmarks.left_eye[0] * faceBoundingBoxWidth + roi[0].position[0])
        left_eye_y = (landmarks.left_eye[1] * faceBoundingBoxHeight + roi[0].position[1])
        faceLandmarks.append([left_eye_x, left_eye_y])

        right_eye_x = (landmarks.right_eye[0] * faceBoundingBoxWidth + roi[0].position[0])
        right_eye_y = (landmarks.right_eye[1] * faceBoundingBoxHeight + roi[0].position[1])
        faceLandmarks.append([right_eye_x, right_eye_y])

        nose_tip_x = (landmarks.nose_tip[0] * faceBoundingBoxWidth + roi[0].position[0])
        nose_tip_y = (landmarks.nose_tip[1] * faceBoundingBoxHeight + roi[0].position[1])
        faceLandmarks.append([nose_tip_x, nose_tip_y])

        left_lip_corner_x = (landmarks.left_lip_corner[0] * faceBoundingBoxWidth + roi[0].position[0])
        left_lip_corner_y = (landmarks.left_lip_corner[1] * faceBoundingBoxHeight + roi[0].position[1])
        faceLandmarks.append([left_lip_corner_x, left_lip_corner_y])

        leftEyeBox = self.createEyeBoundingBox(faceLandmarks[0],
                                               faceLandmarks[1],
                                               1.8)

        RightEyeBox = self.createEyeBoundingBox(faceLandmarks[2],
                                                faceLandmarks[3],
                                                1.8)
        # To crop image
        # img[y:y+h, x:x+w]
        leftEyeBox_img = org_frame[leftEyeBox[1]: leftEyeBox[1] + leftEyeBox[3],
                         leftEyeBox[0]: leftEyeBox[0] + leftEyeBox[2]]

        RightEyeBox_img = org_frame[RightEyeBox[1]: RightEyeBox[1] + RightEyeBox[3],
                          RightEyeBox[0]: RightEyeBox[0] + RightEyeBox[2]]

        return RightEyeBox_img, leftEyeBox_img
