'''
Author: Carmen Meinson
Contributors: Siam Islam, Tianhao Chen
Partially based on the Hand class in the MotionInput v2 code
'''
from typing import Callable, Dict, Optional, Set

import numpy as np

from scripts.core import Position
from scripts.tools import Config


# TODO: the current methods for calculating some primitives are kinda messed up :) - taken straight from v2

def dist(x, y):
    return np.sqrt(np.sum((x - y) ** 2))


class HandPosition(Position):

    def __init__(self, raw_hand_data: Dict[str, np.ndarray], used_primitives: Set[str] = None) -> None:
        # if used_primitives is None then we calculate all primitives

        config = Config()

        self._pinch_sensitivity = config.get_data("modules/hand/position_pinch_sensitivity")
        self._scissor_sensitivity = config.get_data("modules/hand/position_scissor_sensitivity")
        self._threshold_distance = config.get_data(
            "modules/hand/position_threshold_distance")  # TODO: WHERE DOES THIS COME FROM???????? do we read it from config or do we calculate that
        self._landmarks = raw_hand_data
        self._primitives = {}
        self._primitives_calculators = self._get_primitives_calculators()

        self._used_primitives = used_primitives
        if used_primitives is None:  # if used_primitives is None then we calculate all primitives
            self._used_primitives = self._primitives_calculators.keys()
        # calculate primitives
        if self._landmarks is not None:
            self._calculate_primitives()

    def get_primitives_names(self) -> Set[str]:
        return self._used_primitives

    def get_primitive(self, name: str) -> Optional[bool]:
        """Returns the state of the given primitive in the Position if it has been calculated.
        Returns None If the primitive has not been calculated, hence if it either is not defined for current module or the land marks needed to calculate it were not provided

        :param name: name of the primitive (e.g. "palm_facing_camera" or "index_pinched")
        :type name: str
        :return: state of the primitive
        :rtype: Optional[bool]
        """
        # TODO: is it possible that ony some of the landmarks were detected and so the calculations fail?
        if self._landmarks is None: return

        if name not in self._primitives:
            # if the primitive now requested was not initially in the used_primitives, it is possible that it was not calculated, although it could have been
            self._calculate_primitive(name)
        if name in self._primitives:
            return self._primitives[name]

    def get_landmark(self, name: str) -> Optional[np.ndarray]:
        """Returns the coordinates of the landmark.
        Returns None if the landmarks was not provided to the Position on initialization

        :param name: name of the landmark (e.g. "index_tip" or "wrist")
        :type name: str
        :return: coordinates of the landmark
        :rtype: Optional[np.ndarray]
        """
        if name not in self._landmarks: return None
        return self._landmarks[name]

    def get_landmarks_distance(self, name1: str, name2: str) -> float:
        return dist(self.get_landmark(name1), self.get_landmark(name2))

    def get_palm_height(self) -> Optional[float]:
        """Returns the distance between the wrist and the base of the middle finger"""
        # TODO am i repeatedly recalculating it.
        if "wrist" not in self._landmarks or "middle_base" not in self._landmarks: return None
        return self.get_landmarks_distance("middle_base", "wrist")

    def get_palm_scalar(self) -> float:
        """Returns the perimeter of the triangle formed from the wrist, index_base and pinky_base"""
        palm_scalar = (  # TODO: currently calculating it too many times
                self.get_landmarks_distance("wrist", "index_base")
                + self.get_landmarks_distance("wrist", "pinky_base")
                + self.get_landmarks_distance("pinky_base", "index_base")
        )
        return palm_scalar

    def get_finger_tilted_left(self, finger_name: str) -> Optional[bool]:
        """Returns weather the given finger is tilted to the left from the users perspective.
        Tilted left is defined as the tip of the finger being further left than the wrist."""
        if "wrist" not in self._landmarks or (finger_name + "_tip") not in self._landmarks: return None
        return self._landmarks[finger_name + "_tip"][0] < self._landmarks["wrist"][0]

    def get_finger_tilted_right(self, finger_name: str) -> Optional[bool]:
        """Returns weather the given finger is tilted to the right from the users perspective.
        Tilted right is defined as the tip of the finger being further right than the wrist."""
        return not self.get_finger_tilted_left(finger_name)

    def get_palm_front_back_tilt(self) -> Optional[float]:
        if "wrist" not in self._landmarks or ("middle_base") not in self._landmarks: return None
        dy = self._landmarks["middle_base"][1] - self._landmarks["wrist"][1]
        dz = self._landmarks["middle_base"][2] - self._landmarks["wrist"][2]
        return dz / dy

    def get_palm_left_right_tilt(self) -> Optional[float]:
        if "wrist" not in self._landmarks or ("middle_base") not in self._landmarks: return None
        dy = self._landmarks["middle_base"][1] - self._landmarks["wrist"][1]
        dx = self._landmarks["middle_base"][0] - self._landmarks["wrist"][0]
        return dx / dy

    def _get_primitives_calculators(self) -> Dict[str, Callable]:
        primitives_calculators = {
            "palm_facing_camera": self._calculate_palm_facing_camera,
            "hand_closed": self._calculate_hand_closed,
            "index_pulldown": lambda: self._calculate_pulldown("index"),
            "middle_pulldown": lambda: self._calculate_pulldown("middle"),
            "ring_pulldown": lambda: self._calculate_pulldown("ring"),
            "index_scissor": lambda: self._calculate_scissor("index", "middle_tip"),
            "thumb_scissor": lambda: self._calculate_scissor("thumb", "index_base"),
            "thumb_folded": lambda: self._calculate_folded("thumb"),
            "index_folded": lambda: self._calculate_folded("index"),
            "middle_folded": lambda: self._calculate_folded("middle"),
            "ring_folded": lambda: self._calculate_folded("ring"),
            "pinky_folded": lambda: self._calculate_folded("pinky"),
            "thumb_stretched": lambda: self._calculate_stretched("thumb"),
            "index_stretched": lambda: self._calculate_stretched("index"),
            "middle_stretched": lambda: self._calculate_stretched("middle"),
            "ring_stretched": lambda: self._calculate_stretched("ring"),
            "pinky_stretched": lambda: self._calculate_stretched("pinky"),
            "thumb_pinched": lambda: self._calculate_pinched("thumb"),
            "index_pinched": lambda: self._calculate_pinched("index"),
            "middle_pinched": lambda: self._calculate_pinched("middle"),
            "ring_pinched": lambda: self._calculate_pinched("ring"),
            "pinky_pinched": lambda: self._calculate_pinched("pinky"),
        }
        return primitives_calculators

    def _calculate_primitives(self) -> None:
        self._update_threshold_distance()  # TODO: investigate what is the threshold distance exactly

        for primitive in self._used_primitives:
            self._calculate_primitive(primitive)

    def _calculate_primitive(self, primitive_name: str) -> None:
        if primitive_name not in self._primitives_calculators:
            raise RuntimeError("Attempth to calculate an invalid primitive for the Hand mosule: " + primitive_name)

        self._primitives_calculators[primitive_name]()

    def _calculate_folded(self, finger: str) -> None:
        tip = finger + "_tip"
        base = finger + "_base"
        primitive = finger + "_folded"
        self._primitives[primitive] = False

        # detect if finger tip is closer to palm center than the base
        if (self.get_landmarks_distance(tip,
                                        "palm_center") <  # TODO: NB! this was initially distance_xy. WHY???????????!
                self.get_landmarks_distance(base, "palm_center")
        ):
            self._primitives[primitive] = True

        # Detect if the z-distance of the tip to the palm center is below threshold
        if self.get_landmarks_distance("palm_center", tip) < self._threshold_distance:
            self._primitives[primitive] = True

    def _calculate_pinched(self, finger: str) -> None:
        # Add up the distances between the 3 outer palm landmarks
        tip = finger + "_tip"
        primitive = finger + "_pinched"
        self._primitives[primitive] = False

        pinch_distance = self.get_landmarks_distance(tip, "thumb_tip") / self.get_palm_scalar()
        if pinch_distance < self._pinch_sensitivity:
            self._primitives[primitive] = True

    def _calculate_stretched(self, finger: str) -> None:
        # TODO: the calculations make no sense rn
        tip = finger + "_tip"
        upperj = finger + "_upperj"
        base = finger + "_base"
        primitive = finger + "_stretched"
        self._primitives[primitive] = False

        # for thumb: check if tip of thumb is closer to tip of index finger than center of palm
        if finger == "thumb":
            if self.get_landmarks_distance(tip, "palm_center") > self.get_landmarks_distance(upperj, "palm_center"):
                self._primitives[primitive] = True
        else:
            # for other fingers: check if distance between tip of finger to center of palm is higher than upper finger joint to wrist

            if self.get_landmarks_distance(tip, base) > self.get_landmarks_distance(upperj,
                                                                                    base):  # TODO: NB this was xy dist
                self._primitives[primitive] = True

    def _calculate_pulldown(self, finger: str):
        upperj = finger + "_upperj"
        tip = finger + "_tip"
        full_length = self.get_landmarks_distance("wrist", tip)
        upperj_length = self.get_landmarks_distance("wrist", upperj)
        primitive = finger + "_pulldown"

        self._primitives[primitive] = False

        if full_length <= upperj_length:
            self._primitives[primitive] = True

    def _calculate_scissor(self, finger1: str, finger2_joint: str) -> None:
        primitive = finger1 + "_scissor"
        finger1_joint = finger1 + "_tip"

        self._primitives[primitive] = False
        # dividing by palm scalar allows comparison to sensitivity value regardless of the distance
        # between the hand and the camera
        distance = self.get_landmarks_distance(finger1_joint, finger2_joint) / self.get_palm_scalar()

        if distance < self._scissor_sensitivity:
            self._primitives[primitive] = True

    def _calculate_palm_facing_camera(self):
        normal_vector = self._landmarks["palm_normal"] - self._landmarks["palm_center"]
        self._primitives["palm_facing_camera"] = (normal_vector[2] < 0)

    def _calculate_hand_closed(self):
        # The hand is closed / resting when that the tip of the index finger is below the tip of the thumb.
        self._primitives["hand_closed"] = (self._landmarks["index_tip"][1] > self._landmarks["thumb_tip"][1])

    def _update_threshold_distance(self):
        self._threshold_distance = self.get_landmarks_distance("index_base", "pinky_base") * 1.1
        # TODO: WHYYYYYYY THIS
