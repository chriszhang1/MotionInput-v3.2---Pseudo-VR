'''
Author: Carmen Meinson
'''

from typing import Dict, Optional, Set

import numpy as np


class RawData:
    def __init__(self):
        self._data = {}  # "body": None, "head":None ....

    def add_landmark(self, bodypart_name: str, landmark_name: str, coordinates: np.ndarray) -> None:
        if bodypart_name not in self._data: self._data[bodypart_name] = {}
        self._data[bodypart_name][landmark_name] = coordinates

    def combine(self, raw_data: 'RawData') -> None:
        """Combine the data from 2 RawData instances.
        Note the instances MUST contain different body parts.

        :param raw_data: RawData instance the data of which should be copied over to this one
        :type raw_data: RawData
        :raises RuntimeError: raised if the instances do contain the same body parts
        """
        if len(self.get_bodyparts() & raw_data.get_bodyparts()) >0:
            raise RuntimeError("Attempt to combine two RawData instances that contain the same body parts")
        for bodypart in raw_data.get_bodyparts():
            self._data[bodypart] = raw_data.get_data(bodypart)        

    def get_bodyparts(self) -> Set[str]:
        """
        :return: names of all the body parts that have been added to the RawData instance
        :rtype: Set[str]
        """
        return self._data.keys()

    def get_data(self, bodypart_name: str) -> Optional[Dict[str, np.ndarray]]:
        """Returns the data of the body part, if it has been added (aka if it has been detected in the frame)

        :param bodypart_name: bodypart, the data of which should be returned. e.g. "body" or "Left"
        :type bodypart_name: str
        :return: Dictionary of all the landmarks added to the specific body part with the name of the landmark as key and the coordinates [x,y(,z)] as value
        :rtype: Optional[Dict[str, np.ndarray]]
        """
        if bodypart_name not in self._data: return None
        return self._data[bodypart_name]

    def get_landmark(self, bodypart_name: str, landmark_name: str) -> Optional[np.ndarray]:
        """Returns the coordinates of the landmark, if it has been added to the specified body part (aka if it has been detected in the frame)

        :param bodypart_name: body part that the specified landmark should belong to e.g. "body" or "Left"
        :type bodypart_name: str
        :param landmark_name: landmark, the coordinate of which should be returned. e.g. "index_tip" or "wrist"
        :type landmark_name: str
        :return: coordinate of the landmark [x,y(,z)]
        :rtype: Optional[np.ndarray]
        """
        if bodypart_name not in self._data: return None
        if landmark_name not in self._data[bodypart_name]: return None
        return self._data[bodypart_name][landmark_name]
