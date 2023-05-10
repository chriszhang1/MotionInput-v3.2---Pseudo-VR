'''
Author: Fawziyah Hussain (with help from Jason Ho)
'''
import time
from math import sqrt

import cv2
import numpy as np
from mediapipe.python.solutions import hands as mp_hands

from scripts.tools.config import Config


class DepthCalibration:
    '''Opens an opencv window that allows users to calibrate depth values for the pressure 
    sensitivity feature of Digital Inking. Users choose the positions that will correspond
    to minimum and maximum pressure when inking in-air.'''
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)

        self.hands = mp_hands.Hands(
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            max_num_hands=2,
        )

        self.noLandmarkFlag = False
        self.pressure_configurations_dict = {"min_depth": None, "max_depth": None, "depth_range": None}
        self.names = list(self.pressure_configurations_dict.keys())

        self._calibrated = False

    def calibrate(self):
        min_calibrated = False
        max_calibrated = False
        TIMER = int(3)
        windowName = "Depth Calibration"
        prev = time.time()
        font = cv2.FONT_HERSHEY_SIMPLEX
        getReadyFlag = True

        while not max_calibrated:
            while TIMER >= 0:
                success, image = self.cap.read()
                image = cv2.flip(image,1)
                results = self.hands.process(image)

                if not success:
                    print("Cannot grab frame, camera may not be functioning.")
                    break

                else:
                    if getReadyFlag:
                        cv2.putText(image, str('Raise hand'),
                                        (25, 40), font,
                                        1.5, (0, 0, 255),
                                        3, cv2.LINE_AA)
                    elif not min_calibrated:
                        cv2.putText(image, str('Place hand at min pressure position'),
                                        (25, 40), font,
                                        0.8, (0, 0, 255),
                                        2, cv2.LINE_AA)

                    elif not max_calibrated:
                        cv2.putText(image, str('Place hand at max pressure position'),
                                        (25, 40), font,
                                        0.8, (0, 0, 255),
                                        2, cv2.LINE_AA)
                
                    #Show countdown on screen.
                    cv2.putText(image, str(TIMER),
                                    (270, 270), font,
                                    6, (0, 0, 255),
                                    3, cv2.LINE_AA)
                    

                    cv2.imshow(windowName, image)
                    cv2.setWindowProperty(windowName, cv2.WND_PROP_TOPMOST,1)
                    cv2.waitKey(125)
                    if cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) < 1:
                        self.close()
                    cur = time.time()
                    #Change the countdown time.
                    if cur - prev >= 1:
                        prev = cur
                        TIMER = TIMER - 1

            success, image = self.cap.read()
            image = cv2.flip(image, 1)
            
            if not success:
                break
            else:
                results = self.hands.process(image)
                if results.multi_hand_landmarks:
                    if getReadyFlag:
                        getReadyFlag = False

                    elif not min_calibrated:
                        ph = self.get_palm_height(results)
                        self.pressure_configurations_dict["min_depth"] = ph
                        min_calibrated = True

                    elif not max_calibrated:
                        ph = self.get_palm_height(results)
                        self.pressure_configurations_dict["max_depth"] = ph
                        max_calibrated = True
                        self.calculate_depth_range()

                else:
                    self.noLandmarkFlag = True
                    cv2.putText(image, str("Hand not detected. Try Again"),
                                                (25, 40), font,
                                                1, (255, 0, 0),
                                                2, cv2.LINE_AA)
                    cv2.imshow(windowName, image)
                    cv2.waitKey(2000)
                    if cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) < 1:
                        self.close()

            # next stage
            cv2.imshow(windowName, image)
            cv2.waitKey(2000)
            if cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) < 1:
                self.close()
            TIMER = int(3)


        try:
            self._update_config()
        except:
            pass
        
        self.cap.release()
        image = np.zeros((480, 640, 1), dtype = "uint8")
        cv2.putText(image, str("Calibration ended."),
                                (200, 200), font,
                                1, (255, 0, 0),
                                3, cv2.LINE_AA)
        cv2.putText(image, str("Window will now close."),
                                (160, 250), font,
                                1, (255, 0, 0),
                                3, cv2.LINE_AA)
        cv2.imshow(windowName, image)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()


    def calculate_depth_range(self):
        range = self.pressure_configurations_dict["max_depth"] - self.pressure_configurations_dict["min_depth"]
        self.pressure_configurations_dict["depth_range"] = range

    def _update_config(self):
        config = Config().get_editor()
        for var in self.names:
            config.update(f"handlers/pen/{var}", self.pressure_configurations_dict[var])
        config.save()

    def distance_xyz(self, point_0, point_1):
        return sqrt((point_0.x - point_1.x) ** 2 + (point_0.y - point_1.y) ** 2 + (point_0.z - point_1.z) ** 2)

    def get_palm_height(self, results):
        wrist = results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.WRIST]
        middle_base = results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
        palm_height = self.distance_xyz(middle_base, wrist)
        return palm_height

    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()