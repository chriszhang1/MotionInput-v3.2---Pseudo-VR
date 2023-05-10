"""
Author: Alexandros Theofanous
"""

import time

import cv2 as cv
import numpy as np
import winsound

from scripts import *
from scripts.gesture_event_handlers.edit_config import EditConfigFile
from scripts.gesture_events.eye_tracking_event import EyeTrackingEvent
from scripts.tools import Config
from scripts.tools import Camera


class HeadCalibrator:
    
    font = cv.FONT_HERSHEY_SIMPLEX
    frequency = 2500 
    duration = 500    
    eye = EyeTrackingEvent()

    def __init__(self):
        self.windowName = ""
        self.config = Config()
        self.active = True
        self.config_update_calibrated = EditConfigFile()
        self.config_editor = self.config.get_editor()

    def calibrate(self,gesture):
        self.cap = Camera()
        self.windowName = self.config.get_data("general/view/window_name")
        self.camera_height: int = self.config.get_data("general/camera/camera_h")
        self.camera_width: int = self.config.get_data("general/camera/camera_w")

        _image, _ = self.cap.read()

        black_image = np.zeros((480, 640, 3), dtype=np.uint8)
        black_image1 = np.zeros((480, 640, 3), dtype=np.uint8)
        black_image2 = np.zeros((480, 640, 3), dtype=np.uint8)
        black_image3 = np.zeros((480, 640, 3), dtype=np.uint8)
        black_image4 = np.zeros((480, 640, 3), dtype=np.uint8)

        self.active = self.wait(8, black_image)
        if not self.active:
            return

        black_image1 = self.look(black_image1, 'UP' )
        final_maxy,self.active = self.find_average_calibration('y', black_image1 ,gesture)
        if not self.active:
            return
            
        black_image2 = self.look(black_image2, 'RIGHT' )
        final_maxx,self.active = self.find_average_calibration('x',black_image2 ,gesture)
        if not self.active:
            return

        black_image3 = self.look(black_image3, 'DOWN' )
        final_miny,self.active = self.find_average_calibration('y',black_image3 ,gesture)
        if not self.active:
            return

        black_image4 = self.look(black_image4, 'LEFT' )
        final_minx,self.active = self.find_average_calibration('x',black_image4 ,gesture)
        if not self.active:
            return

        self.config_update_calibrated.switch_boolean("handlers/eye_cal_switch/enable")

        self.config_editor.update("modules/eye/max_y",final_maxy)
        self.config_editor.update("modules/eye/max_x",final_maxx)
        self.config_editor.update("modules/eye/min_y",final_miny)
        self.config_editor.update("modules/eye/min_x",final_minx)
            
        cv.destroyAllWindows()

        return

    def wait(self, sec, black_image):
        start = time.time()
        elapsed = 0

        black_image = cv.putText(black_image, 'EYE CALIBRATION PHASE', (60, 60), self.font, 1.3, (128, 0, 128), 2, cv.LINE_AA)
        black_image = cv.putText(black_image, 'The next screen will show you calibration instructions.', (40, 100), self.font, 0.6, (64, 224, 208), 2, cv.LINE_AA)
        black_image = cv.putText(black_image, 'You will need to look at the midpoint between center', (40, 140), self.font, 0.6, (64, 224, 208), 2, cv.LINE_AA)
        black_image = cv.putText(black_image, 'and top, right, bottom and left edge of the screen. ', (40, 180), self.font, 0.6, (64, 224, 208), 2, cv.LINE_AA)
        black_image = cv.putText(black_image, 'A beep will follow when to look the next direction.', (40, 220), self.font, 0.6, (64, 224, 208), 2, cv.LINE_AA)
        
        while elapsed < sec:
            current = time.time()
            elapsed = current - start
 
            _image, _ = self.cap.read()
            _final_image = np.hstack((_image, black_image))
            cv.imshow(self.windowName,_final_image)
            cv.waitKey(125)

            if cv.getWindowProperty(self.windowName, cv.WND_PROP_VISIBLE) < 1:
                self.close()
                return False

        return True

    def look(self, black_image, direction ):
        black_image = np.zeros((480, 640, 3), dtype=np.uint8)

        black_image = cv.putText(black_image, 'EYE CALIBRATION PHASE', (60, 60), self.font, 1.3, (128, 0, 128), 2,
                                    cv.LINE_AA)
        black_image = cv.putText(black_image, 'LOOK ' + direction, (250, 180), self.font, 1, (64, 224, 208), 2,
                        cv.LINE_AA)
        black_image = cv.putText(black_image, 'Look at the midpoint between the' \
                    , (30, 300), self.font, 1, (64, 224, 208), 2,cv.LINE_AA)
        black_image = cv.putText(black_image, 'center of the screen and' \
                    , (30, 340), self.font, 1, (64, 224, 208), 2,cv.LINE_AA)
        if direction == "UP":
            black_image = cv.putText(black_image, 'the TOP edge' \
                        , (30, 380), self.font, 1, (64, 224, 208), 2,cv.LINE_AA)
        elif direction == "DOWN":
            black_image = cv.putText(black_image, 'the BOTTOM edge' \
                        , (30, 380), self.font, 1, (64, 224, 208), 2,cv.LINE_AA)
        else:
            black_image = cv.putText(black_image, 'the ' + direction + ' edge' \
                    , (30, 380), self.font, 1, (64, 224, 208), 2,cv.LINE_AA)
        winsound.Beep(self.frequency, self.duration)

        return black_image

    def find_average_calibration(self, axis, black_image , gesture):
        values = []
        start = time.time()
        seconds = 3

        current = time.time()
        elapsed = current - start

        while elapsed < seconds:
            _image, _ = self.cap.read()
            _final_image = np.hstack((_image, black_image))
            cv.imshow(self.windowName,_final_image)
            cv.waitKey(125)

            num_to_denoise: int = self.config.get_data("modules/eye/num_to_denoise")
            position_list = gesture.get_last_n_positions(num_to_denoise)
            eye_gaze, nose3d = self.eye._denoise(position_list)

            if elapsed > 1:
                if len(eye_gaze) != 0 and len(nose3d) != 0:
                    if axis == 'y':
                        x, edge = self.eye._get_coor(eye_gaze, nose3d)
                    else:
                        edge, y = self.eye._get_coor(eye_gaze, nose3d)
                    values.append(edge)
            
            current = time.time()
            elapsed = current - start

            if cv.getWindowProperty(self.windowName, cv.WND_PROP_VISIBLE) < 1:
                self.close()
                return False

    
        final = sum(values)/len(values)

        return final, True

    def close(self):
        self.cap.close()
        cv.destroyAllWindows()
        sys.exit()

    def _check_state(self) -> None:
        self._state = self._gestures["eye"]["gaze_nose3d_gesture"] is not None