'''
Author: Carmen Meinson
'''

from typing import Dict, Optional, Set

import numpy as np


# position represents the state of 1 body part in one frame

# class to store:
#  - location of all the points/landmarks
#  - all primitives (aka boolean values calculated from the points)
# has functions to calculate all the other data points like angle/distance/....

class Position:
    # contains the passed raw data and thus the coordinates of all points of interest
    # calculates dict of primitives, with true/false values

    def __init__(self, raw_data: Dict[str, np.ndarray], used_primitives: Set[str] = None) -> None:
        # takes in the frame data
        # calculates the primitives and stores the locations of the points
        # if used_primitives is None then we calculate all primitives if names of primitives are given we calculate only the needed ones
        raise NotImplementedError()

    def get_primitive(self, name: str) -> Optional[bool]:
        """Returns the state of the given primitive in the Position if it has been calcualated.
        Returns None If the primitive has not been calculated, hence if it either is not defined for current module or the land marks needed to calculate it were not provided

        :param name: name of the primitive (e.g. "palm_facing_camera", "index_pinched" or "punchleft")
        :type name: str
        :return: state of the primitive
        :rtype: Optional[bool]
        """
        raise NotImplementedError()

    def get_landmark(self, name: str) -> Optional[np.ndarray]:
        """Returns the coordinates of the landmark.
        Returns None if the landmarks was not provided to the Position on initialization

        :param name: name of the landmark
        :type name: str
        :return: coordinates of the landmark [x,y(,z)]
        :rtype: Optional[np.ndarray]
        """
        raise NotImplementedError()

    def get_primitives_names(cls) -> Set[str]:
        """
        :return: Names of all primitives that are calculated by the specific modules Position class on initialization
        :rtype: List[str]
        """
        raise NotImplementedError()
    # ...
    # some getters
    # other commonly used calculation functions (like distance between 2 fingers?)
