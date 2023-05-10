import time
from typing import List
from os.path import dirname, abspath
import csv
import cv2
import numpy as np
from mediapipe.python.solutions import drawing_utils as mp_drawing
from mediapipe.python.solutions import pose as mp_pose


class RepetitiousExerciseCalibration:
    def __init__(self, selected_exercises):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.pose = mp_pose.Pose(
                    min_detection_confidence = 0.6,
                    min_tracking_confidence = 0.6,
                    )
        self.sample = 0
        self.noLandmarkFlag = False
        self.set_selected_exercises(selected_exercises)
        

    def set_selected_exercises(self, exercise_list: List[str]) -> None:
        # ["no_equipment", "walking"]
        # {"idle":["idle","no_equipment"],"Walking":["walking_left","walking_right","no_equipment"]}
        self._selected_exercises_dict = {"idle":["idle", f"{exercise_list[0]}"]}

        for i in range(1, len(exercise_list)):
            self._selected_exercises_dict[exercise_list[i]] = [f"{exercise_list[i]}_left", f"{exercise_list[i]}_right", f"{exercise_list[0]}"]

        self._repetitious_exercise_names = list(self._selected_exercises_dict.keys())
        
    def calibration(self):
        round = 0
        count = len(self._selected_exercises_dict)
        TIMER = int(3)
        windowName = "Repetitious Exercise Calibration"
        prev = time.time()
        font = cv2.FONT_HERSHEY_SIMPLEX
        getReadyFlag = True
        state = 0
        while count > 0 :
            while TIMER >= 0:
                success, image = self.cap.read()
                image = cv2.flip(image, 1)
                if not success:
                    print("Cannot grab frame, camera may not be functioning.")
                    break
                else:
                    if getReadyFlag:
                        cv2.putText(image, str('Get ready.'),
                                        (25, 40), font,
                                        1.5, (0, 0, 255),
                                        3, cv2.LINE_AA)
                    elif round == 0:
                        cv2.putText(image, str('Stay idle.'),
                                        (25, 40), font,
                                        1.5, (0, 0, 255),
                                        3, cv2.LINE_AA)
                    else:
                        cv2.putText(image, ("Taking a picture of: "),
                                        (25, 25), font,
                                        1, (0, 0, 255),
                                        3, cv2.LINE_AA)
                        cv2.putText(image, (str(self._repetitious_exercise_names[round]) + " : " + str(self._selected_exercises_dict[self._repetitious_exercise_names[round]][state])),
                                        (25, 60), font,
                                        0.9, (0, 0, 255),
                                        3, cv2.LINE_AA)
                #Show countdown on screen.
                cv2.putText(image, str(TIMER),
                                    (270, 270), font,
                                    6, (0, 0, 255),
                                    3, cv2.LINE_AA)
                        
                cv2.imshow(windowName, image)
                cv2.waitKey(125)
                cur = time.time()
                #Change the time.
                if cur - prev >= 1:
                    prev = cur
                    TIMER = TIMER - 1
      
            #After each round of countdown, collect the landmark coordinates.
            success, image = self.cap.read()
            image = cv2.flip(image, 1)
            if not success:
                break
            else:
                frameHeight, frameWidth = image.shape[0], image.shape[1]
                results=self.pose.process(image)
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(image, landmark_list=results.pose_landmarks, connections=mp_pose.POSE_CONNECTIONS)
                    if getReadyFlag:
                        getReadyFlag = False
                        count +=1
                        round -=1
                    else:
                        exercise = self._repetitious_exercise_names[round]
                        className = self._selected_exercises_dict[self._repetitious_exercise_names[round]][state]
                        self.create_CSV(exercise, className, results.pose_landmarks.landmark, frameHeight, frameWidth)
                        if round > 0 and (len (self._selected_exercises_dict[self._repetitious_exercise_names[round]]) > 2) and state ==0:
                            count +=1
                            round -=1
                            state = 1
                        elif state == 1:
                            state = 0
                else:
                    self.noLandmarkFlag = True
                    cv2.putText(image, str("Landmark not detected."),
                                        (25, 25), font,
                                        1, (0, 0, 255),
                                        3, cv2.LINE_AA)
                    cv2.imshow(windowName, image)
                    cv2.waitKey(2000)
                    break
            
            if self.noLandmarkFlag:
                break
            else:
                cv2.imshow(windowName, image)
                cv2.waitKey(2000)
                TIMER = int(3)
                count -=1
                round +=1
            
        self.cap.release()
        image = np.zeros((480, 640, 1), dtype = "uint8")
        cv2.putText(image, str("Calibration ended."),
                                (25, 25), font,
                                1, (0, 0, 255),
                                3, cv2.LINE_AA)
        cv2.putText(image, str("Window will now close."),
                                (25, 60), font,
                                1, (0, 0, 255),
                                3, cv2.LINE_AA)
        
        cv2.imshow(windowName, image)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()


    def create_CSV(self, exercise, className, poseLandmark, frameWidth, frameHeight):
        #Setting up the calibrated CSVs.
        modes = self._selected_exercises_dict[exercise][-1]
        csvFolder= dirname(dirname(dirname(abspath(__file__)))) + "/data/ml_models/body/" + modes
        csvPath = csvFolder + '/' + className+ '_calibrated.csv'
        with open(csvPath, mode='w', newline='') as f:
            csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            sample = 0
            while sample <20:
                row = list(np.array([[landmark.x* frameWidth, landmark.y* frameHeight, landmark.z* frameWidth] for landmark in poseLandmark]).flatten())
                row.insert(0, 'sample '+str(sample))
                csv_writer.writerow(row)
                sample += 1
