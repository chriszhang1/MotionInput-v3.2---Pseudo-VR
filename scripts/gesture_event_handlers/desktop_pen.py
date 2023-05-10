'''
Authors: Fawziyah Hussain and Eva Miah
'''
import pyautogui
from pynput.mouse import Controller

from scripts.tools import Config
from .area_of_interest import AreaOfInterest
from .desktop_mouse import Smoother
from .pen_input import Pen


class DesktopPenInput:
    def __init__(self, aoi: AreaOfInterest, Pressure=500, Erase=False):
        config = Config()
        self._cursor = Controller()

        self._pen = Pen()
        self._pressure = Pressure

        self._erase = Erase

        self._x_smoother = Smoother(config.get_data("handlers/mouse/smoothing"))
        self._y_smoother = Smoother(config.get_data("handlers/mouse/smoothing"))
        
        self._aoi = aoi

        pyautogui.FAILSAFE = False

    def move_cursor(self, cam_x:float, cam_y:float):
        """Translate the camera coordinates into the AOI coordinates. Smooth the movement of the mouse by averaging out the coordinates of the last few frames (as configured). Move the mouse accordingly."""
        # translate palm center coords to screen coordinates
        x, y = self._aoi.convert_xy(cam_x, cam_y)
        # update cursor
        self._cursor.position = (self._x_smoother.smooth(x), self._y_smoother.smooth(y))


    #NOTE: tap function not currently used for inking
    def tap(self):
        self._pen.pentap(self._cursor.position, self._pressure, self._erase)

    def press(self):
        self._pen.pendown(self._cursor.position, self._pressure, self._erase)

    def release(self):
        self._pen.penup(self._cursor.position)

    def update_pen(self):
        """Updates the cursor position and pressure value to continue an ink stroke/drag event"""
        self._pen.update_pen_info(self._cursor.position, self._pressure)
    
    def update_pressure(self, pressure):
        self._pressure = pressure

    def eraser_activate(self):
        self._erase = True

    def eraser_deactivate(self):
        self._erase = False