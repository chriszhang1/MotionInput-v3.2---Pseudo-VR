'''
Author: Jason Ho
'''
from typing import Any, Dict, Optional, Set

import numpy as np

from scripts.core import Position
from scripts.tools import Config

config = (Config()).get_editor() # TODO: see if perhaps the get_activated_gesture_names() could be moved out of the config
extremity_dict = config.get_data("body_gestures/extremity_triggers")
exercise_dict = config.get_data("body_gestures/exercises")

class BodyPosition(Position):
    _exercise_mode = config.get_data("modules/body/mode")
    _exercise_primitives = set(config.get_data(f"body_gestures/exercises/{_exercise_mode}").keys())
    _exercise_primitives.add("idle")
    _extremity_primitives = set(config.get_data("body_gestures/extremity_triggers").keys())
    _primitive_names = _exercise_primitives | _extremity_primitives

    pose_classification = None
    filtered_pose_classification = None  
    
    def __init__(self, raw_body_data: Dict[str, np.ndarray], used_primitives: Set[str] = None) -> None:
        self._data = raw_body_data 
        self._primitives = {}
        self._used_primitives = used_primitives
        if used_primitives is None: # if used_primitives is None then we calculate all primitives
            self._used_primitives = self._primitive_names
        if self._data:
            self._calculate_primitives()

    def get_primitives_names(self) -> Set[str]:
        """Returns set of used primitives.
        
        :return: Set of used primitives
        :rtype: Set[str]
        """
        return self._used_primitives

    @property
    def _get_pose_classification_object(self):
        # allows each instance of body position class to get and update the same PoseClassification class
        return self.__class__.pose_classification

    @property
    def _get_filtered_pose_classification_object(self):
        return self.__class__.filtered_pose_classification

    def get_primitive(self, name: str) -> Optional[bool]:
        """Returns the state of the given primitive in the Position if it has been calculated.
        Returns None If the primitive has not been calculated, hence either is not defined for current module or the landmarks needed to calculate it were not provided

        :param name: name of the primitive (e.g. "up" or "arm_left")
        :type name: str
        :return: state of the primitive
        :rtype: Optional[bool]
        """
        # TODO: now as we have the used_primitives we need to change this behaviour a bit:
        #    if the primitive has not yet been calculated as it is not in used primitives:
        #       try first calculating it (self._calculate_primitives()) and only then return None if that is not doable.
        if name not in self._primitives: return None
        return self._primitives[name]

    def _calculate_primitives(self) -> None:
        config = Config()
        min_confidence_threshold = config.get_data("modules/body/min_confidence_threshold")
        circle_radius = config.get_data("modules/body/extremity_circle_radius")
        self._calculate_extremity_primitives(circle_radius)
        self._calculate_exercise_primitives(min_confidence_threshold)
        
    def _calculate_exercise_primitives(self, min_confidence_threshold: float) -> None:
        if len(self._exercise_primitives) > 0 and len(self._data) >= 33: # 33 landmarks for full body + extra for extremity triggers
            min_confidence_threshold = config.get_data("modules/body/min_confidence_threshold") # minimum value the confidence score can be, for the exercise to be entered
            # filtered_classification_dict = self.filtered_pose_classification(self.pose_classification(self._landmark_array))
            self._landmark_array = self._convert_data_to_numpy_arr(self._data)
            filtered_classification_dict = self._get_filtered_pose_classification_object(self._get_pose_classification_object(self._landmark_array, self._used_primitives))

            for exercise_state in filtered_classification_dict: 
                pose_confidence_score = filtered_classification_dict[exercise_state]
                self._primitives[exercise_state] = pose_confidence_score > min_confidence_threshold

    def _calculate_extremity_primitives(self, circle_radius: float) -> None:
        self._extremity_dict = {extremity: { 
            "landmark": extremity_dict[extremity]["landmark"],
            "coordinates": extremity_dict[extremity]["coordinates"]}
            for extremity in self._extremity_primitives if extremity in self._used_primitives}
        if len(self._extremity_primitives) > 0:
            for extremity in self._extremity_dict:
                landmark = self._extremity_dict[extremity]['landmark']
                [x_coordinate, y_coordinate] = self._extremity_dict[extremity]['coordinates']
                raw_landmark_coords = self._data[landmark]
                #comparison, checks whether the extremity is within a circle centred around the point of calibration
                if (int(x_coordinate) - circle_radius) <= int(raw_landmark_coords[0]) <= (int(x_coordinate) + circle_radius) \
                    and (int(y_coordinate) - circle_radius) <= int(raw_landmark_coords[1]) <= (int(y_coordinate) + circle_radius):
                    self._primitives[extremity] = True
                else:
                    self._primitives[extremity] = False

    def _convert_data_to_numpy_arr(self, raw_body_data: Dict[str, np.ndarray]) -> np.ndarray:
        return np.array([arr for arr in raw_body_data.values()], dtype = np.float32)

    @classmethod
    def _get_attr_of_activated_extremity(cls, attr: str, extremity: str) -> Any:
        return config.get_data(f"body_gestures/extremity_triggers/{extremity}/{attr}")


        


