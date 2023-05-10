'''
Author: Carmen Meinson & Chris Zhang
'''
import ctypes
from collections import deque
from typing import Tuple

import pynput._util.win32
from pynput.keyboard import Controller as Controller_k
from pynput.keyboard import Key
from pynput.mouse import Button
from pynput.mouse import Controller as Controller_m
import pyautogui
from pyautogui import mouseUp, mouseDown
from scripts.gesture_event_handlers.monitor_tracker import MonitorTracker
from scripts.tools import Config
from scripts.tools import ModeEditor
from .area_of_interest import AreaOfInterest

SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)

pyautogui.FAILSAFE = False

def set_pos(dx, dy):
    dx = int(dx)
    dy = int(dy)
    extra = ctypes.c_ulong(0)
    ii_ = pynput._util.win32.INPUT_union()
    ii_.mi = pynput._util.win32.MOUSEINPUT(dx, dy, 0, 0x0001, 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
    event = pynput._util.win32.INPUT(ctypes.c_ulong(0), ii_)
    SendInput(1, ctypes.pointer(event), ctypes.sizeof(event))


class Smoother:
    def __init__(self, smoothing_frames: int):
        self._smoothing_buffer = deque(maxlen=smoothing_frames)

    def smooth(self, val: float) -> float:
        # averages the value over given number of past frames
        # TODO: could be implemented more efficiently by tracking the sum
        self._smoothing_buffer.append(val)
        sum = 0
        for v in self._smoothing_buffer:
            sum += v
        coord = sum / len(self._smoothing_buffer)
        #print("Coord: ",coord)
        #print("Buffer: ", self._smoothing_buffer)
        #print("Buffer: ", self._smoothing_buffer)
        #print(len(self._smoothing_buffer))
        return coord


class BaseMouse:
    def __init__(self):
        # cursor movement
        config = Config()
        self._mouse = Controller_m()

        self._mouse_x_smoother = Smoother(config.get_data("handlers/mouse/smoothing"))
        self._mouse_y_smoother = Smoother(config.get_data("handlers/mouse/smoothing"))
        self._zoom_smoother = Smoother(config.get_data("handlers/zoom/smoothing"))

        self._zoom_multiplier = config.get_data("handlers/zoom/speed")  # TODO make dynamic
        self._scroll_multiplier = config.get_data("handlers/scroll/speed")

        self._cursor_xy = [0, 0]
        self._mouse_smoothing = 5
        self._mouse_buffer_x = [0 for i in range(self._mouse_smoothing)]
        self._mouse_buffer_y = [0 for i in range(self._mouse_smoothing)]
        mode = ModeEditor()
        self._currentMode = mode.get_data("current_mode")

    def move_cursor_pixel(self, pixel_x: float, pixel_y: float):
        """moving the cursor to specified pixels on the screen. 
        Smooth the movement of the mouse by averaging out the coordinates of the last few frames (as configured)."""
        # update cursor
        self._mouse.position = self._smooth_mouse(pixel_x, pixel_y)

    def _smooth_mouse(self, x: float, y: float) -> Tuple[float, float]:
        return self._mouse_x_smoother.smooth(x), self._mouse_y_smoother.smooth(y)

    def move_cursor_relative(self, change_x: int, change_y: int):
        """Moves the cursor relative to the current location.

        :param change_x: change in pixels in the x direction with positive value meaning movement to the right
        :type change_x: int
        :param change_y: change in pixels in the y direction with positive value meaning movement downwards
        :type change_y: int
        """
        self._mouse.move(change_x, change_y)

    def left_click(self):
        self._mouse.click(Button.left, 1)

    def left_press(self):
        mouseDown()

    def left_release(self):
        mouseUp()

    def right_click(self):
        self._mouse.click(Button.right, 1)

    def right_press(self):
        mouseDown(button = 'right')

    def right_release(self):
        mouseUp(button = 'right')

    def double_click(self):
        self._mouse.click(Button.left, 2)

    def scroll(self, speed: float = 5.0):
        """
        :param speed: speed of scrolling, where positive speed means scrolling down and negative speed scrolling up
        :type speed: float
        """
        self._mouse.scroll(0, speed * self._scroll_multiplier)

    def zoom(self, speed: float = 5.0):
        """Zoom simulating the Ctrl key press with mouse scroller.
        Smooth the zooming by averaging out the coordinates of the last few frames (as configured).

        :param speed: speed of the zooming, where positive speed means zooming in and negative speed zooming out
        :type speed: float
        """
        keyboard = Controller_k()
        with keyboard.pressed(Key.ctrl):
            self._mouse.scroll(0, self._zoom_smoother.smooth(speed * self._zoom_multiplier))


class DesktopMouse(BaseMouse):
    def __init__(self, monitor_tracker: MonitorTracker):
        super().__init__()
        self._monitor_tracker = monitor_tracker

    def move_cursor(self, screen_precent_x: float, screen_precent_y: float):
        """Translate the screen percentages into screen pixels. Smooth the movement of the mouse by averaging out the coordinates of the last few frames (as configured). Move the mouse accordingly."""
        # translate palm center coords to screen coordinates
        x, y = self._monitor_tracker.convert_xy(screen_precent_x, screen_precent_y)
        # update cursor
        self._mouse.position = self._smooth_mouse(x, y)


class AOIMouse(BaseMouse):
    def __init__(self, aoi: AreaOfInterest):
        super().__init__()
        self._aoi = aoi

    def move_cursor(self, cam_x: float, cam_y: float):
        """Translate the camera coordinates into the AOI coordinates. Smooth the movement of the mouse by averaging out the coordinates of the last few frames (as configured). Move the mouse accordingly."""
        # translate palm center coords to screen coordinates
        if self._currentMode.find("pseudovr") != -1:
            x, y = self._aoi.convert_xy_pseudovr(cam_x, cam_y)
            old_position = self._cursor_xy
            new_position_x, new_position_y = x, y
            self._cursor_xy = [new_position_x, new_position_y]
            set_pos(new_position_x - old_position[0],
                    new_position_y - old_position[1])

        else:
            x, y = self._aoi.convert_xy(cam_x, cam_y)
            # update cursor
            self._mouse.position = self._smooth_mouse(x, y)
