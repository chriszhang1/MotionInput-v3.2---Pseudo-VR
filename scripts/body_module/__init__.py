from typing import Any, Optional

from scripts.body_module.calibrate_triggers import ExtremityTriggerCalibration
from scripts.body_module.classification.classification_smoothing import EMASmoothing
from scripts.body_module.classification.pose_classification import PoseClassification
from scripts.core import Module
from scripts.tools.config import Config
from .body_gesture import BodyGesture
from .body_landmark_detector import BodyLandmarkDetector
from .body_position import BodyPosition

config = Config()
class BodyModule(Module):
    _position_class = BodyPosition
    _gesture_class = BodyGesture
    _landmark_detector_class = BodyLandmarkDetector

    _tracker_names = {"body"}

    @classmethod
    def _do_pre_initialization(cls) -> None:
        # all the time consuming setup required for each module sould be implemented here.
        BodyPosition.pose_classification = PoseClassification()
        BodyPosition.filtered_pose_classification = EMASmoothing()
    
    @classmethod
    def calibrate(cls,  params: Optional[Any] = None) -> None:
        """Called to allow the user to specify the positions of the hit triggers by manually moving their body
        landmarks."""
        trigger_calibrator = ExtremityTriggerCalibration()
        selected_triggers = config.get_data("modules/body/calibrate_triggers/selected_triggers_to_calibrate")
        trigger_calibrator.set_selected_triggers(selected_triggers)
        trigger_calibrator.calibrate()
        