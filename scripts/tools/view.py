'''
Authors: Carmen Meinson, Jason Ho and Oluwaponmile Femi-Sunmaila
Contributors: Andrzej Szablewski, Anelia Gaydardzhieva
'''
from time import perf_counter
from typing import Dict, Tuple

import cv2
import numpy as np

from scripts.tools.config import Config
from scripts.tools.display_element import (
    AreaOfInterestElement,
    ChangeCameraElement,
    DrawFPSElement,
    ExerciseDisplayElement,
    ExtremityCirclesElement,
    FaceBoxElement,
    HeadPosElement,
    FaceLandMarkElement,
    EyeGazeElement,
    HelpMessageElement,
    LowLightIndicatorElement,
    NoseBoxElement,
    InAirKeyboardElement,
    ActiveModeNameElement,
    TranscribeModeElement,
    CorrectionModeElement,
    SpeakerIdElement,
    NoseBoundElement
)


class View:
    def __init__(self, head_screen_top: bool = True, hidden: bool = False):
        config = Config()
        self._height = config.get_data("general/camera/camera_h")
        self._width = config.get_data("general/camera/camera_w")
        self._head_screen_top = head_screen_top
        self._change_camera = False
        self._current_camera = 0
        self._window_name = config.get_data("general/view/window_name") + " v%s" %config.get_data("general/version")
        self._display_fps = config.get_data("general/view/show_fps")
        self.frames = 0
        self.second = 0
        self.fps = 0

        self._display_element_classes = {
            "area_of_interest_element": {
                "type": AreaOfInterestElement,
                "args": {"height": self._height, "width": self._width}
            },
            "extremity_circles_element": {
                "type": ExtremityCirclesElement,
                "args": {}
            },
            "exercise_display_element": {
                "type": ExerciseDisplayElement,
                "args": {}
            },
            "facebox_display_element": {
                "type": FaceBoxElement,
                "args": {}
            },
            "head_pos_display_element": {
                "type": HeadPosElement,
                "args": {}
            },
            "face_landmark_display_element": {
                "type": FaceLandMarkElement,
                "args": {}
            },
            "eye_gaze_display_element": {
                "type": EyeGazeElement,
                "args": {}
            },
            "nose_box_display_element": {
                "type": NoseBoxElement,
                "args": {
                    "height": self._height,
                    "width": self._width
                }
            },
            "in_air_keyboard_element":  {
                "type": InAirKeyboardElement,
                "args": {}
            },
            "active_mode_name": {
                "type": ActiveModeNameElement,
                "args": {}
            },
            "transcribe_element": {
                "type": TranscribeModeElement,
                "args": {}
            },
            "correction_element": {
                "type": CorrectionModeElement,
                "args": {}
            },
            "speaker_identification_element": {
                "type": SpeakerIdElement,
                "args": {}
            },            
            "nose_bound_element": {
                "type": NoseBoundElement,
                "args": {}
            },
            "draw_fps_element": {
                "type": DrawFPSElement,
                "args": {}
            },
            "change_camera_element": {
                "type": ChangeCameraElement,
                "args": {}
            },
            "low_light_indicator_element": {
                "type": LowLightIndicatorElement,
                "args": {}
            },
            "help_message_element": {
                "type": HelpMessageElement,
                "args": {}
            }
        }
        self._display_element_dict = {}
        self._hidden = hidden
        self._closed_by_user = False
        self._window_open = False


    def update_display_element(self, name: str, update_args: Dict[str,str] = {}) -> None:
        """Updates a display element, e.g. area of interest element, by passing in 
        updated arguments to update its attributes. 
        If the display element class is not already initialised, then it also initialises the class.

        :param name: Reference name of the DisplayElement class handled by the View
        :type name: str
        :param update_args: Keyword arguments to be passed into the DisplayElement class' update method
        :type update_args: Dict[str, str]
        """
        
        if name not in self._display_element_classes:
            raise RuntimeError("Attempt to get an undefined display element :", name)

        if name not in self._display_element_dict:
            #print("Adding new dictionary element for",name)
            #print("in",self._display_element_dict)
            #print("class_type = ",self._display_element_classes[name]["type"])
            #print("class_args = ",self._display_element_classes[name]["args"])
            
            class_type = self._display_element_classes[name]["type"]
            class_args = self._display_element_classes[name]["args"]
            #print("class_type(**(class_args))",class_type(**(class_args)))
            self._display_element_dict[name] = class_type(**(class_args))

            #print("dict[name]",self._display_element_dict[name])

        #if name == "speaker_identification_element":
        #    print(f"{name} already in dict {self._display_element_dict}")
  
        self._display_element_dict[name].update(**(update_args))
        #xxx =self._display_element_dict[name]

        #if name == "speaker_identification_element":
        #    print("self._display_element_dict[name]",self._display_element_dict[name])

    def update_display(self, frame: np.ndarray) -> None:
        """Takes an image object and loops through all activated DisplayElements, running their update_display method allowing them to draw to the
        image

        :param frame: image object for the DisplayElement instances to draw to
        :type frame: np.ndarray
        """
        if self._hidden:
            if self._window_open: self.close()
            return

        self.update_display_element("low_light_indicator_element", {})
        self.update_display_element("change_camera_element", {"display":self._change_camera, "index": self._current_camera})
        self.update_display_element("help_message_element", {})
        if self._display_fps:
            self._draw_fps(frame)
            self.update_display_element("draw_fps_element", {"fps": str(self.fps)})

        for display_element in self._display_element_dict.values():
            display_element.update_display(frame)

        cv2.imshow(self._window_name, np.copy(frame))
        self._window_open = True

        # if esc pressed or closed with x
        pressed_key = cv2.waitKey(1)
        if pressed_key == 27 or cv2.getWindowProperty(self._window_name, cv2.WND_PROP_VISIBLE) < 1:
            self._closed_by_user = True
            return pressed_key

        # Window always on top regardless of activity:
        if self._head_screen_top is True:
            cv2.setWindowProperty(self._window_name, cv2.WND_PROP_TOPMOST, 1)
        return pressed_key

    def update_change_camera(self, val: bool, index: int):
        self._change_camera = val
        self._current_camera = index
        #print("Toggled camera change")



    # Draw FPS code from MI2 (slightly modified)
    def _draw_fps(self, image: np.ndarray) -> None:
        if perf_counter() < self.second + 1:
            self.frames += 1
        else:
            self.fps = self.frames
            self.second = perf_counter()
            self.frames = 1
        #cv2.putText(image, str(self.fps), (590, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    def hide(self) -> None:
        self._hidden = True

    def show(self) -> None:
        self._hidden = False

    def close(self):
        self._window_open = False
        cv2.destroyAllWindows() # I only changed that because it gave me the same error that gave Siam
        print("close: window destroyed")

    def was_closed_by_user(self) -> bool:
        return self._closed_by_user

    def get_frame_size(self) -> Tuple[int, int]:
        return self._height, self._width

