'''
Authors: Carmen Meinson & Oluwaponmile Femi-Sunmaila & Chris Zhang
Based on MotionInput v2 AreaOfInterest class by Ashild Kummen
'''
# area_of_interest.py - creates blue rectangle of which hand movements are processed at cursor movements within. corners map to the corners of the screen. dynamically calibrated based on distance to the camera.

from typing import Optional, Tuple

import numpy as np
from win32api import GetSystemMetrics
from win32con import SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN

from scripts.tools import ModeEditor
from scripts.tools import View, Config
from .monitor_tracker import MonitorTracker


class AreaOfInterest:
    """Blue rectangle that maps to the corners of the screen. Autocalibrated with distance to the camera."""

    # Area of interest identifies the rectangle in which to process hand gestures within,
    # e.g. to moving the cursor to the upper left corner of the area of interest rectangle moves is to the upper left corner of the screen.
    def __init__(self, view: View, monitor_tracker: MonitorTracker, current_spacing=0):
        """Creates an AreaOfInterest Object. Responsible for defining the region of space representing
        the current monitor in use.
        
        :param view: The window that the AOI is to be displayed on
        :type view: View
        :param monitor_tracker: current instance of the MonitorTracker
        :type monitor_tracker: MonitorTracker
        :param current_spacing: The index of which spacing level to use. Defaults to 0.
        :type current_spacing: int, optional
        """
        self._screen_width = GetSystemMetrics(SM_CXVIRTUALSCREEN)
        self._screen_height = GetSystemMetrics(SM_CYVIRTUALSCREEN)

        self._cam_height, self._cam_width = view.get_frame_size()
        self._cam_ratio = (self._cam_width / self._cam_height)
        self._monitor_tracker = monitor_tracker
        config = Config()
        self._screen_y_bound = config.get_data("handlers/aoi/screen_y_bound")
        self._screen_x_bound = config.get_data("handlers/aoi/screen_x_bound")
        self._view = view
        self._spacing_levels = config.get_data("handlers/aoi/spacing_levels")
        self.update_spacing_level(current_spacing)
        self._aoi_x = int(config.get_data("events/pseudovr_mode_keys/aoi_coordinates/x"))
        self._aoi_y = int(config.get_data("events/pseudovr_mode_keys/aoi_coordinates/y"))

        mode = ModeEditor()
        self._currentMode = mode.get_data("current_mode")

    def update_spacing_level(self, level: Optional[int] = None) -> None:
        """Updates the size of the AOI displayed on the view.

        :param level: The spacing level that should be used. if no level is given the AOI should be removed
        :type level: Optional[int]
        :raises RuntimeError: If an invalid spacing level is given (outside the range of spacing levels)
        """
        if level is None:
            self._view.update_display_element("area_of_interest_element", {})
            return

        if level >= len(self._spacing_levels) or level < 0:
            raise RuntimeError("Attempt to set AOI to an invalid spacing level: ", level, ". Available levels are 0 - ",
                               len(self._spacing_levels) - 1)

        self._current_height_spacing = self._spacing_levels[level]
        self._current_width_spacing = self._current_height_spacing * self._monitor_tracker.get_screen_ratio() / self._cam_ratio

        self._view.update_display_element("area_of_interest_element", {"width_spacing": self._current_width_spacing,
                                                                       "height_spacing": self._current_height_spacing})

    def convert_xy(self, x_cam_percent: float, y_cam_percent: float) -> Tuple[float, float]:
        """Does an affine transformation for camera x,y coordinates to map to the screen pixels"""
        # TODO: in the legacy code the np.interp was used here. why????
        # TODO: claculate not always by height. make it depend on how the screen and cam ratio relate to eachother aka find the best or somthing like that

        # current spacing shows how what percent of the cam height is the screen height
        # move origin to the middle
        x_cam_percent, y_cam_percent = x_cam_percent - 0.5, y_cam_percent - 0.5
        # transform the cam percentages to the screen percentages and move origin back to left top corner
        y_screen_percent = y_cam_percent / self._current_height_spacing + 0.5
        x_screen_percent = x_cam_percent / self._current_width_spacing + 0.5
        # make sure everything in range 0-1

        # the following two lines are used to keep the mouse in the bounds of the screen (if the argument given for the min is 1). 
        # this was previously disabled as a temporary fix to keep the mouse in the bounds of the screen
        # it has now been re-enabled as, in touchpoints, out of bound coordinates result in touch injection failures
        # as a temporary fix for the taskbar, i've set the argument to 1.05 for the y-screen percent (which should hopefully work for most situations)
        # x screen_percent is set to 0.999 as setting it to 1 can still result in touch injection failures (e.g. for a 1920 x 1080 display, the x-coordinate for example
        # can't exceed 1919 and the y-coordinate cannot exceed 1079 (note this is just a theory))
        y_screen_percent = max(0, min(y_screen_percent, self._screen_y_bound))
        x_screen_percent = max(0, min(x_screen_percent, self._screen_x_bound))

        # transform screen percentages to screen pixels
        return self._monitor_tracker.convert_xy(x_screen_percent, y_screen_percent)

    def convert_xy_pseudovr(self, x_cam_percent: float, y_cam_percent: float) -> Tuple[float, float]:
        """Does an affine transformation for camera x,y coordinates to map to the screen pixels"""
        x, y = (
            x_cam_percent * self._cam_width,
            y_cam_percent * self._cam_height,
        )  # from percentage to camera pixel
        window_x = self._aoi_x * 16 / 15 + 160
        window_y = self._aoi_y * 6 / 5 + 120
        # from camera pixel to screen pixel
    
        xNew = np.interp(
            x,
            (
                window_x,
                window_x + 320
            ),
            (0, 640),
        )
        yNew = np.interp(
            y,
            (
                window_y,
                window_y + 240
            ),
            (0, 480),
        )

        return (xNew / 640) * self._screen_width, (yNew / 480) * self._screen_height
