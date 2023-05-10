'''
Author: Jason Ho
'''
from typing import Dict, List, Optional, Tuple
from scripts.tools import Config, View

config = Config().get_editor()
class ExtremityCircles:
    """Class for the circles representing the Extremity triggers (hit targets). These are circles displayed on the view, which when activated, change
    colour. They also display a number inside the circle, which represents the number of times the extremity trigger has been activated."""
    def __init__(self, view: View) -> None:
        self._view = view
        self._extremity_circles_dict = {}
        self._extremity_coordinates = None

    def set_extremity_circles_dict(self, activated_extremities: Optional[List[str]] = None) -> None:
        """Sets the dictionary containing the names of the activated extremities and a tuple of their coordinates, activation status and repeats for
        the DisplayElement to be displayed in the view.
        
        :param activated_extremities: List of extremities to be displayed
        :type activated_extremities: Optional[List[str]]
        """
        if activated_extremities is not None:
            self._set_extremity_coordinates(activated_extremities)
        self._extremity_circles_dict = {extremity: ((x_coordinate, y_coordinate), False, 0) for extremity, [x_coordinate, y_coordinate] in self._extremity_coordinates.items()}
        self._view.update_display_element("extremity_circles_element", {"extremity_circles_dict": self._extremity_circles_dict})
    
    def _set_extremity_coordinates(self, activated_extremities: Optional[List[str]] = None):
        if activated_extremities is not None:
            self._extremity_coordinates = {}
            extremities_dict = config.get_data(f"body_gestures/extremity_triggers")
            self._extremity_coordinates = {extremity: extremities_dict[extremity]["coordinates"] for extremity in activated_extremities}

    def _get_extremity_circle_coords(self, extremity: str) -> Tuple[int]:
        extremity_circle_tuple = self._extremity_circles_dict.get(extremity)
        if extremity_circle_tuple is not None:
            return extremity_circle_tuple[0]
    
    def _get_extremity_circle_repeats(self, extremity: str) -> int:
        extremity_circle_tuple = self._extremity_circles_dict.get(extremity)
        if extremity_circle_tuple is not None:
            return extremity_circle_tuple[-1]
    
    def update_extremity_circle(self, extremity: str, repeats: Optional[int] = 0, activated: Optional[bool] = False) -> None:
        """Updates the colour of an extremity circle when the extremity is activated or deactivated by updating the list of extremity circles. 
        If an extremity is activated, the circle turns to the activated colour and vice versa. Also adds the number of times the extremity has 
        been triggered.

        :param extremity: Name of extremity
        :type extremity: str
        :param repeats: Number of times the extremity has been triggered
        :type repeats: Optional[int]
        :param activated: If the extremity is activated
        :type activated: Optional[bool]
        """
        self._extremity_circles_dict[extremity] = (self._get_extremity_circle_coords(extremity), activated, repeats)
        self._view.update_display_element("extremity_circles_element", {"extremity_circles_dict": self._extremity_circles_dict})

    def clear_extremity_circles(self) -> None:
        """Clears the displaying of the extremity circles in the view by passing an empty dictionary to the DisplayElement."""
        self._view.update_display_element("extremity_circles_element", {"extremity_circles_dict": {}})

    @staticmethod
    def _get_attr_of_activated_extremity(attr: str) -> Dict:
        # TODO: see if perhaps the get_activated_gestures() could be moved out of the config
        activated_primitives = config.get_activated_gestures("extremity_triggers")
        out = {}
        for extremity, vals in activated_primitives.items():
            out[extremity] = vals[attr]
        return out

        