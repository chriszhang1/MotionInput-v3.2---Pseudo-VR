"""
Author: Alexandros Theofanous
"""

import cv2 as cv

from scripts import *
from scripts.eye_module.eye_calibration import HeadCalibrator
from scripts.gesture_event_handlers.edit_config import EditConfigFile
from .eye_tracking_event import EyeTrackingEvent
from .simple_gesture_event import SimpleGestureEvent
from .. import Config


class EyeMode2Event(SimpleGestureEvent):
    _event_trigger_types = {"move"}
    _gesture_types = {"gaze_nose3d_gesture"}
    _bodypart_types = {"eye"}
    _active = True
    font = cv.FONT_HERSHEY_SIMPLEX
    duration = 500    
    _eye = EyeTrackingEvent()
    cal = HeadCalibrator()
    conf_edit = EditConfigFile()

    def __init__(self):
        super().__init__(EyeMode2Event._gesture_types,
                         EyeMode2Event._event_trigger_types,
                         EyeMode2Event._bodypart_types)

        self._config = Config()
        self._gestures = {"eye": {"gaze_nose3d_gesture": None}}

    def update(self):

        self._active: bool = self._config.get_data("handlers/eye_mode_switch/enable")
        self._calibrated: bool = self._config.get_data("handlers/eye_cal_switch/enable")
        self._go: bool = self._config.get_data("handlers/eye_go/enable")
        
        self._cursor_speed: float = self._config.get_data("modules/eye/Eye_mouse_speed")

        self.ymax: float = self._config.get_data("modules/eye/max_y")
        self.ymin: float = self._config.get_data("modules/eye/min_y")
        self.xmax: float = self._config.get_data("modules/eye/max_x")
        self.xmin: float = self._config.get_data("modules/eye/min_x")
        
        if self._calibrated:
            num_to_denoise: int = self._config.get_data("modules/eye/num_to_denoise")

            position_list = self._gestures["eye"]["gaze_nose3d_gesture"].get_last_n_positions(num_to_denoise)
            eye_gaze, nose3d = self._eye._denoise(position_list)

            if len(eye_gaze) != 0 and len(nose3d) != 0:

                if self._go:
                    self.direction: str = self._config.get_data("modules/eye/cons_direction")

                    if self.direction == "":
                        xper, yper = self._eye._get_coor(eye_gaze, nose3d)
                        self.direction = self.determine_direction(xper, yper, self.ymax, self.xmax, self.ymin, self.xmin)
                        self.conf_edit.set_value("modules/eye/cons_direction", self.direction)

                    self.move_magnet_mode(self.direction)    
                    
                elif self._active:
                    self.conf_edit.set_value("modules/eye/cons_direction", "")
                    xper, yper = self._eye._get_coor(eye_gaze, nose3d)
                    
                    self.move_grid_mode(xper,yper, self.ymax, self.xmax, self.ymin, self.xmin)
        else:
            self.cal.calibrate(self._gestures["eye"]["gaze_nose3d_gesture"])

    def move_magnet_mode(self, dir):

        if dir == "left":                                           
            self._event_triggers["move"](-self._cursor_speed,0)   
        elif dir == "right":                                          
            self._event_triggers["move"](+self._cursor_speed,0)  
        if dir == "up":                                           
            self._event_triggers["move"](0,-self._cursor_speed)  
        elif dir == "down":                                          
            self._event_triggers["move"](0,self._cursor_speed)
    
    def move_grid_mode(self, x, y, ymax, xmax, ymin, xmin):

        xdif = max(abs(x)-abs(xmax),abs(x)-abs(xmin))
        ydif = max(abs(y)-abs(ymax),abs(y)-abs(ymin))

        if x > xmin and x < xmax and y > ymin and y < ymax:
            return
        if xdif >= ydif:                                              #--------------------------------------
            if x <= xmin:                                             #|     |                        |     |
                self._event_triggers["move"](-self._cursor_speed,0)   #|     |           UP           |  R  |
            elif x >= xmax:                                           #|  L  |------------------------|  I  |
                self._event_triggers["move"](+self._cursor_speed,0)   #|  E  |         CENTER         |  G  |
        else:                                                         #|  F  |       (NO  MOVE)       |  H  |
            if y <= ymin:                                             #|  T  |------------------------|  T  |
                self._event_triggers["move"](0,-self._cursor_speed)   #|     |                        |     |
            elif y >= ymax:                                           #|     |          DOWN          |     |
                self._event_triggers["move"](0,self._cursor_speed)    #--------------------------------------
        return 

    def determine_direction(self, x, y, ymax, xmax, ymin, xmin):

        xdif = max(abs(x)-abs(self.xmax),abs(x)-abs(self.xmin))
        ydif = max(abs(y)-abs(self.ymax),abs(y)-abs(self.ymin))

        if xdif >= ydif:                                        
            if x <= xmin:                                           
                return "left" 
            elif x >= xmax:           
                return "right" 
        else:                                                     
            if y <= ymin:                                                    
                return "up"   
            elif y >= ymax:                                      
                return "down"   
        return                                          

    def _check_state(self) -> None:
        self._state = self._gestures["eye"]["gaze_nose3d_gesture"] is not None