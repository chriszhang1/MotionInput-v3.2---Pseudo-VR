'''
Author: Oluwaponmile Femi-Sunmaila
'''
from win32api import EnumDisplayMonitors, GetMonitorInfo  # pip install pywin32
from typing import Tuple

work_area = Tuple[int, int, int, int]
class MonitorTracker:
    def __init__(self):
        """Tracks the currently active monitor and it's size.
        """
        self._screen_width = None
        self._screen_height = None
        self._screen_ratio = None
        self._top_left = None
        self._current_monitor = -1
        self._monitors = self._init_monitors()
        self.change_monitor()

    def get_monitor_size(self) -> Tuple[int,int]:
        """
        :return: monitor size in pixels [width, height]
        :rtype: Tuple[int,int]
        """
        return [self._screen_width, self._screen_height]

    def get_screen_ratio(self) -> float:
        """
        :return: screen ration defined as width/height
        :rtype: float
        """
        return self._screen_ratio

    def change_monitor(self) -> None:
        """Changes the active monitor aka the monitor in relation to which the size and the xy coordinates are calculated."""        
        if self._current_monitor == len(self._monitors)-1:
            self._current_monitor = 0
        else:
            self._current_monitor += 1
        self._top_left = self._monitors[self._current_monitor][0:2]
        self._update_proportions()

    def convert_xy(self, x_screen_percent: float, y_screen_percent: float) -> Tuple[float,float]:
        """Convert the percentage coordinates of the screen to the pixel coordinates of the current monitor in relation to the main one
        """
        return self._top_left[0] + x_screen_percent * self._screen_width, self._top_left[1] + y_screen_percent * self._screen_height

    @staticmethod
    def _init_monitors() -> dict[int, work_area]:
        #Get all monitors and their working areas
        all_monitors = {}
        for index, monitor in enumerate(EnumDisplayMonitors()):
            monitor_data = GetMonitorInfo(monitor[0])
            all_monitors[index] = monitor_data["Work"]
        return all_monitors  

    def _update_proportions(self) -> None:
        monitor_info = self._monitors[self._current_monitor]
        self._screen_width = monitor_info[2]-monitor_info[0]
        self._screen_height = monitor_info[3]-monitor_info[1]
        self._screen_ratio = (self._screen_width / self._screen_height)