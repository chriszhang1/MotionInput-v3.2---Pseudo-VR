"""
Author: Yadong (Adam) Liu
"""

from typing import Dict, Optional, Set

import numpy as np

from scripts.core import Position


class EyePosition(Position):
    def __init__(self, raw_eye_data: Dict[str, np.ndarray], used_primitives: Set[str] = None) -> None:
        self._landmarks = raw_eye_data
        self._used_primitives = used_primitives  # TODO add calculating only used primitves
        self._primitives = {}

        if self._landmarks is not None:
            self._calculate_primitives()

    def get_primitives_names(self) -> Set[str]:
        return self._used_primitives

    def get_primitive(self, name: str) -> Optional[bool]:
        """Returns the state of the given primitive in the Position if it has been calcualated.
        Returns None If the primitive has not been calculated, hendce if it either is not defined for current module or the land marks needed to calcualte it were not provided

        :param name: name of the primitive (e.g. "palm_facing_camera" or "index_pinched")
        :type name: str
        :return: state of the primitive
        :rtype: Optional[bool]
        """
        if name not in self._primitives:
            return None
        return self._primitives[name]

    def get_landmark(self, name: str) -> Optional[np.array]:
        """Returns the coordinates of the landmark.
        Returns None if the landmarks was not provided to the Position on initialization

        :param name: name of the landmark (e.g. "index_tip" or "wrist")
        :type name: str
        :return: coordinates of the landmark
        :rtype: Optional[np.array]
        """
        if name not in self._landmarks:
            return None
        return self._landmarks[name]

    def _calculate_gaze_nose3d(self):
        self._primitives["gaze"] = len(self.get_landmark("eye_gaze")) != 0
        self._primitives["nose3d"] = len(self.get_landmark("nose3D")) != 0

    def _calculate_primitives(self):
        self._calculate_gaze_nose3d()
