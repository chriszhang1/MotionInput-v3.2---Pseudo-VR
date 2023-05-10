"""
Author: Andrzej Szablewski
Contributor: Alexandros Theofanous
"""
from typing import Optional, Tuple
from .monitor_tracker import MonitorTracker
from scripts.tools import View, Config

class NoseBox:
    def __init__(self, view: View, monitor_tracker: MonitorTracker):
        self._cam_height, self._cam_width = view.get_frame_size()
        self._monitor_tracker = monitor_tracker
        self.config = Config()
        self._view = view
        self._nose_box_size = self.config.get_data(
            "events/nose_tracking/nose_box_percentage_size"
        )
        self.nose_box_centre_X = self.config.get_data("events/nose_tracking/nose_box_centre_X")
        self.nose_box_centre_Y = self.config.get_data("events/nose_tracking/nose_box_centre_Y")
        self.update_nose_box()

    def update_nose_box(self, nose_point: Optional[Tuple[float, float]] = None) -> None:
        self._view.update_display_element(
            "nose_box_display_element",
            {
                "nose_box_size": self._nose_box_size,
                "nose_point": nose_point,
                "nose_box_centre": (self.nose_box_centre_X, self.nose_box_centre_Y)
            }
        )

    def remove_nose_box(self):
        self._view.update_display_element(
            "nose_box_display_element",
            {
                "nose_box_size": None,
                "nose_point": None,
                "nose_box_centre": None
            }
        )

    def update_boundaries_text(self, direction):
        self._view.update_display_element(
            "nose_bound_element",
            {
                "direction" : direction
            }
        )

    def update_nose_box_centre(self, nose_box_centre: Tuple[float, float]) -> None:
        self.config.get_editor().update("events/nose_tracking/nose_box_centre_X", nose_box_centre[0])
        self.config.get_editor().update("events/nose_tracking/nose_box_centre_Y", nose_box_centre[1])
        self.nose_box_centre_X = self.config.get_data("events/nose_tracking/nose_box_centre_X")
        self.nose_box_centre_Y = self.config.get_data("events/nose_tracking/nose_box_centre_Y") 
    
    def update_nose_box_boundaries(self, change, nose_box_centre: Tuple[float, float], nose_box_adjustment) -> None:
        left_bound = self.config.get_data("events/nose_tracking/nose_box_up_left_bound")
        right_bound = self.config.get_data("events/nose_tracking/nose_box_bot_right_bound")
        if change:
            self.config.get_editor().update("events/nose_tracking/nose_box_centre_X", nose_box_centre[0])
            self.config.get_editor().update("events/nose_tracking/nose_box_centre_Y", nose_box_centre[1])

            vector = self.config.get_data("events/nose_tracking/scaling_factor")
            self._nose_box_size = self.config.get_data("events/nose_tracking/nose_box_percentage_size")

            self.config.get_editor().update("events/nose_tracking/nose_box_percentage_size", (self._nose_box_size * nose_box_adjustment))
            self.config.get_editor().update("events/nose_tracking/scaling_factor", (vector * nose_box_adjustment))

            self.nose_box_centre_X = self.config.get_data("events/nose_tracking/nose_box_centre_X")
            self.nose_box_centre_Y = self.config.get_data("events/nose_tracking/nose_box_centre_Y")
            self._nose_box_size = self.config.get_data("events/nose_tracking/nose_box_percentage_size")

        if left_bound == [0,0] and right_bound == [0,0]:
            self.update_boundaries_text("none")
        elif left_bound != [0,0] and right_bound != [0,0]:
            self.update_boundaries_text("both")
        elif left_bound == [0,0]:
            self.update_boundaries_text("right")
        else:
            self.update_boundaries_text("left")

        self.update_nose_box()

