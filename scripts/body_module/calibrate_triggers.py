'''
Author: Motioninput V2 developers (Copied over and slightly modified by Jason Ho)
'''
import time
from typing import Dict, List

import cv2
import numpy as np
from mediapipe.python.solutions import pose as mp_pose

from scripts.tools.config import Config

config = Config()
class ExtremityTriggerCalibration:
    """Class that opens up an opencv window, allowing the user to go through a list of selected triggers, and
    update their position on the screen by manually positioning their landmarks to where they want it to be.
    
    Code copied and slightly modified from Motioninput V2"""
    def __init__(self) -> None:
        self._landmark_name_dict = {'left_wrist_extremity': 'Left Wrist', 
                                    'right_wrist_extremity': 'Right Wrist',
                                    'left_ankle_extremity': 'Left Ankle',
                                    'right_ankle_extremity': 'Right Ankle', 
                                    'nose_extremity': 'Head'}

        self._landmark_index_dict = {'left_wrist_extremity': 16, 
                                    'right_wrist_extremity': 15,
                                    'left_ankle_extremity': 28,
                                    'right_ankle_extremity': 27, 
                                    'nose_extremity': 0}

        self._limb_landmark_names=['Right Wrist', 'Left Wrist', 'Right Ankle', 'Left Ankle', 'Head']
        self._limb_landmark_index=[15, 16, 27, 28, 0]
        self._coordinates_dict={}
        self._idle_limb_coordinates = {}
        self._idle_head_coordinates = {}
        self._max_changed_coordinate = {}
        self._cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self._cap.set(3, 640)
        self._cap.set(4, 480)
        
        self._pose = mp_pose.Pose(
                    min_detection_confidence=0.6,
                    min_tracking_confidence=0.6,
        )
        self._no_landmark_flag = False

    def set_selected_triggers(self, trigger_list: List[str]) -> None:
        """Allows a list of triggers to be passed in for the program to calibrate.
        
        :param trigger_list: List of extremity trigger names
        :type trigger_list: List[str]"""
        self._selected_extremity_triggers_dict = {}
        for trigger in trigger_list:
            landmark = config.get_data(f"body_gestures/extremity_triggers/{trigger}/landmark")
            self._selected_extremity_triggers_dict[trigger] = self._landmark_name_dict[landmark]
        self._head_extremity_count = 0
        
        self._extremity_trigger_names = list(self._selected_extremity_triggers_dict.keys())
        for x in self._extremity_trigger_names:
            if self._selected_extremity_triggers_dict[x] == "Head":
                self._head_extremity_count +=1
                
    def calibrate(self) -> None:
        """Runs the calibration program, opening an opencv window and allowing the user to specify position of
        triggers, which then updates the config files to save their settings."""
        round=0
        count = len(self._selected_extremity_triggers_dict)
        TIMER = int(3)
        window_name = "Extremity Trigger Calibration"
        prev = time.time()
        font = cv2.FONT_HERSHEY_SIMPLEX
        get_ready_flag = True
        
        while count >=0:
            while TIMER >= 0:
                success, image = self._cap.read()
                image = cv2.flip(image, 1)
                if not success:
                    print("Cannot grab frame, camera may not be functioning.")
                    break
                else:
                    frame_height, frame_width = image.shape[0], image.shape[1]
                    if len(self._coordinates_dict)>0:
                        for x in range (len(self._coordinates_dict.values())):
                            cv2.circle(image, list(self._coordinates_dict.values())[x], 30, (0, 0, 255), -1)
                
                    if get_ready_flag:
                        cv2.putText(image, str('Get ready.'),
                                        (25, 40), font,
                                        1.5, (0, 255, 255),
                                        3, cv2.LINE_AA)
                    elif round == 0:
                        cv2.putText(image, str('Stay idle.'),
                                        (25, 40), font,
                                        1.5, (0, 255, 255),
                                        3, cv2.LINE_AA)

                    elif self._selected_extremity_triggers_dict[self._extremity_trigger_names[round-1]] == "Head":
                        self._find_extremity_head(image, frame_height, frame_width)
                        cv2.putText(image, str('Head extremity: ') + str(self._extremity_trigger_names[round-1]),
                                        (25, 25), font,
                                        1, (0, 255, 255),
                                        3, cv2.LINE_AA)
                        cv2.putText(image, str('Jump or move your head.'),
                                        (25, 60), font,
                                        1, (0, 255, 255),
                                        3, cv2.LINE_AA)

                    else:
                        cv2.putText(image, str('Extremity: ') + str(self._extremity_trigger_names[round-1]),
                                        (25, 25), font,
                                        1, (0, 255, 255),
                                        3, cv2.LINE_AA)
                        cv2.putText(image, str('Move your: ') + str(self._selected_extremity_triggers_dict[self._extremity_trigger_names[round-1]]).lower(),
                                        (25, 60), font,
                                        1, (0, 255, 255),
                                        3, cv2.LINE_AA)
                
                    #Show countdown on screen.
                    cv2.putText(image, str(TIMER),
                                    (270, 270), font,
                                    6, (0, 255, 255),
                                    3, cv2.LINE_AA)
                    

                    cv2.imshow(window_name, image)
                    cv2.waitKey(125)
                    cur = time.time()
                    #Change the countdown time.
                    if cur - prev >= 1:
                        prev = cur
                        TIMER = TIMER - 1

                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    self._close()
                    
            #After each round of countdown, collect the landmark coordinates.
            success, image = self._cap.read()
            image = cv2.flip(image, 1)
            if not success:
                break
            else:
                frame_height, frame_width = image.shape[0], image.shape[1]
                
                #process the frame to get the coordinate of the limbs
                results=self._pose.process(image)
                if results.pose_landmarks:
                    extremity_landmarks = {}
                    for x in self._limb_landmark_index:
                        extremity_landmarks[self._limb_landmark_names[self._limb_landmark_index.index(x)]] = {'x':results.pose_landmarks.landmark[x].x*frame_width, 'y': results.pose_landmarks.landmark[x].y*frame_height}
                    if get_ready_flag:
                        get_ready_flag = False
                        round -= 1
                        count += 1
                    # Get the idle coordinates.
                    elif round==0:
                        if self._head_extremity_count > 0:
                            self._idle_head_coordinates['x'] = results.pose_landmarks.landmark[0].x*frame_width
                            self._idle_head_coordinates['y'] = results.pose_landmarks.landmark[0].y*frame_height
                            self._max_changed_coordinate['x'] = int(self._idle_head_coordinates['x'])
                            self._max_changed_coordinate['y'] = int(self._idle_head_coordinates['y'])
                        for x in self._limb_landmark_index:
                            self._idle_limb_coordinates[self._limb_landmark_names[self._limb_landmark_index.index(x)]] = {'x':results.pose_landmarks.landmark[x].x*frame_width, 'y': results.pose_landmarks.landmark[x].y*frame_height}
                    elif self._selected_extremity_triggers_dict[self._extremity_trigger_names[round-1]] == "Head":
                        self._coordinates_dict[self._extremity_trigger_names[round-1]]=[self._max_changed_coordinate['x'],self._max_changed_coordinate['y']]
                        self._max_changed_coordinate['x'] = int(self._idle_head_coordinates['x'])
                        self._max_changed_coordinate['y'] = int(self._idle_head_coordinates['y'])
                    else:
                        self._find_extremity_limb(extremity_landmarks, round)
                else:
                    self._no_landmark_flag = True
                    cv2.putText(image, str("Landmark not detected."),
                                        (25, 25), font,
                                        0.8, (255, 0, 0),
                                        3, cv2.LINE_AA)
                    cv2.imshow(window_name, image)
                    cv2.waitKey(2000)
                    break
        
            if self._no_landmark_flag:
                break
            else:
                if len(self._coordinates_dict)>0:
                    for x in range (len(self._coordinates_dict.values())):
                        cv2.circle(image, list(self._coordinates_dict.values())[x], 30, (0, 0, 255), -1)
                cv2.imshow(window_name, image)
                cv2.waitKey(2000)
                TIMER = int(3)
                count = count - 1
                round = round + 1
        
        try:
            self._update_config()
        except:
            pass

        self._cap.release()
        image = np.zeros((480, 640, 1), dtype = "uint8")
        cv2.putText(image, str("Calibration ended."),
                                (25, 25), font,
                                1, (255, 0, 0),
                                3, cv2.LINE_AA)
        cv2.putText(image, str("Window will now close."),
                                (25, 60), font,
                                1, (255, 0, 0),
                                3, cv2.LINE_AA)
        cv2.imshow(window_name, image)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()
        #sys.exit()
    
    def _update_config(self) -> None:
        # extremity key, and coordinates
        config = Config().get_editor()
        
        for extremity, coordinates in self._coordinates_dict.items():
            config.update(f"body_gestures/extremity_triggers/{extremity}/coordinates", coordinates)
        config.save()

    def _find_extremity_limb(self, extremity_landmarks: Dict[str, Dict[str, int]], round) -> None:
        set_landmark_name = self._selected_extremity_triggers_dict[self._extremity_trigger_names[round-1]]
        self._coordinates_dict[self._extremity_trigger_names[round-1]]=[int(extremity_landmarks[set_landmark_name]['x']), int(extremity_landmarks[set_landmark_name]['y'])]
        return self._coordinates_dict

    def _find_extremity_head(self, image: np.ndarray, frame_height: int, frame_width: int) -> None:
        results=self._pose.process(image)
        if results.pose_landmarks:
            if (((results.pose_landmarks.landmark[0].x*frame_width - self._idle_head_coordinates['x'])**2 + (results.pose_landmarks.landmark[0].y*frame_height - self._idle_head_coordinates['y'])**2)**0.5 > 
            ((self._max_changed_coordinate['x'] - self._idle_head_coordinates['x'])**2 + (self._max_changed_coordinate['y']- self._idle_head_coordinates['y'])**2)**0.5):
                self._max_changed_coordinate['x'] = int(results.pose_landmarks.landmark[0].x*frame_width)
                self._max_changed_coordinate['y'] = int(results.pose_landmarks.landmark[0].y*frame_height)
        return self._max_changed_coordinate

    def _close(self):
        self._cap.release()
        cv2.destroyAllWindows()