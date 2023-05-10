'''
Author: Jason Ho
Contributors: Andrzej Szablewski, Keyur Narotomo, Siam Islam, Chris Zhang, Anelia Gaydardzhieva
'''
from time import perf_counter
from typing import Dict, Optional, Tuple

import cv2
import numpy as np
from numpy import sin, cos, pi

from scripts.tools.config import Config
from scripts.tools.json_editors.mode_editor import ModeEditor


class DisplayElement:
    def __init__(self) -> None:
        self._font = cv2.FONT_HERSHEY_SIMPLEX
        self._colour_dict = {"red": (0, 0, 255), # BRG not RGB! :)
                             "blue": (255, 0, 0),
                             "green": (0, 255, 0),
                             "orange": (0, 165, 255),
                             "orange2": (56, 159, 249),
                             "black": (0, 0, 0),
                             "white": (255, 255, 255),
                             "gray": (86, 86, 86),
                             "lightGray": (114, 114, 114)
                             }

    def update(self, **kwargs) -> None:
        """
        Takes in parameters and updates the DisplayElement's attributes accordingly.
        Called by view's update_display_element class, whenever an event handler that uses a tool, 
        e.g. area of interest or extremity circles, needs
        to update some information that's stored as attributes in a DisplayElement class
        """
        raise NotImplementedError()

    def update_display(self, image) -> None:
        """
        Takes a cv2 image object and updates the image, adding in extra display features, 
        such as the area of interest or extremity circles.
        Called every frame by the view's update_display class, 
        to ensure that for each initialised DisplayElement class, it will add the required
        things to the cv2 image
        """
        raise NotImplementedError()

# -------------------------------------------------------------------------------------

class ExerciseDisplayElement(DisplayElement):
    def __init__(self) -> None:
        self._exercise_repeats_dict = {}
        super().__init__()

    def update_display(self, image) -> None:
        """
        Takes a cv2 image object and updates the image, adding in the information 
        for the activated exercises and the number of repeats.
        """
        if len(self._exercise_repeats_dict) > 0:
            for index, (exercise, repeats) in enumerate(self._exercise_repeats_dict.items()):
                image = cv2.putText(image, f"{exercise}: {str(repeats)}", (10, 30 * (index + 1) + 25), self._font, 0.8,
                                    self._colour_dict["blue"], 2, 0)

    def update(self, exericses_repeats_dict: Dict[str, int]) -> None:
        """
        Takes in parameters and updates the ExerciseDisplayElement's attributes accordingly.

        :param exericses_repeats_dict: Dictionary of exercises to display with info about number of repeats
        :type exericses_repeats_dict: Dict[str, int]
        """
        self._exercise_repeats_dict = exericses_repeats_dict

# -------------------------------------------------------------------------------------

class ExtremityCirclesElement(DisplayElement):
    def __init__(self) -> None:
        self._extremity_circles_dict = {}
        super().__init__()

    def update_display(self, image: np.ndarray) -> None:
        """
        Takes an image object and updates the image, adding in the extremity circles 
        representing the extremity triggers, including its state and repeats.

        :param image: Current frame being processed
        :type image: np.ndarray
        """
        config = Config()
        radius = int(config.get_data("modules/body/extremity_circle_radius"))
        mode = ModeEditor().get_data("current_mode")
        extremity_path = "body_gestures/extremity_triggers/"
            
        if len(self._extremity_circles_dict) > 0:
            for (extremity, ((x, y), activated, repeats)) in self._extremity_circles_dict.items():
                key = config.get_data(extremity_path + extremity + "/key")
                if activated:
                    rgb = self._colour_dict["green"]
                else:
                    rgb = self._colour_dict["red"]
                image = cv2.circle(image, (x, y), radius, rgb, -1)
                text_size, _ = cv2.getTextSize(key, self._font, 0.8, 2)
                image = cv2.putText(image, key, (x - text_size[0] // 2 + 5, y + text_size[1] // 2), self._font,
                                    0.6, self._colour_dict["black"], 2, 0)


    def update(self, extremity_circles_dict: Dict[str, Tuple]) -> None:
        """
        Takes in parameters and updates the ExtremityCirclesElement's attributes accordingly.
        
        :param extremity_circles_dict: Dictionary of extremity triggers to display 
        with info about coordinates, activation and repeats
        :type extremity_circles_dict: Dict[str, Tuple]
        """
        self._extremity_circles_dict = extremity_circles_dict

# -------------------------------------------------------------------------------------

class AreaOfInterestElement(DisplayElement):
    def __init__(self, height: int, width: int) -> None:
        self._aoi_start = None
        self._aoi_end = None
        self._height = height
        self._width = width
        super().__init__()

    def update_display(self, image) -> None:
        """
        Takes a cv2 image object and updates the image, adding in the area of interest.
        update_aoi
        """
        if self._aoi_start is not None:
            image = cv2.rectangle(image, self._aoi_start, self._aoi_end, self._colour_dict["blue"], 1)

    def update(self, width_spacing: Optional[float] = None, height_spacing: Optional[float] = None) -> None:
        """
        Takes in parameters and updates the AreaOfInterestElement's 
        attributes accordingly. If no parameters are given AOI is no longer displayed
        """
        if height_spacing is None and width_spacing is None:
            self._aoi_start = None
            self._aoi_end = None
            return

        height_from_origin = self._height * (1 - height_spacing) * 0.5
        width_from_origin = self._width * (1 - width_spacing) * 0.5

        mode = ModeEditor()
        currentMode = str(mode.get_data("current_mode"))

        if currentMode.find("pseudovr") != -1:  # pseudovr mode
            config = Config()
            x = int(config.get_data("events/pseudovr_mode_keys/aoi_coordinates/x"))
            y = int(config.get_data("events/pseudovr_mode_keys/aoi_coordinates/y"))

            self._aoi_start = (int(width_from_origin) + x, int(height_from_origin) + y)
            self._aoi_end = (int(self._width - width_from_origin) + x, int(self._height - height_from_origin) + y)

        else:  # hand module
            self._aoi_start = (int(width_from_origin), int(height_from_origin))
            self._aoi_end = (int(self._width - width_from_origin), int(self._height - height_from_origin))

# -------------------------------------------------------------------------------------        

class InAirKeyboardElement(DisplayElement):
    def __init__(self) -> None:
        super().__init__()
        self.buttons = {}
        self.hovered_keys = {}
        self.clicked_keys = {}
        self.font = cv2.FONT_HERSHEY_SIMPLEX  
        self.font_weight = 2
        self.font_colour = self._colour_dict["white"]
        self.font_colour_on_hover = self._colour_dict["black"]
        self.key_bg_on_hover = self._colour_dict["white"]
        self.key_bg_on_click = self._colour_dict["green"]
        self.alpha = Config().get_data("events/keyboard/default_transparency")
        

    def update(self, buttons: dict, hovered_keys: set, clicked_keys: set):
        self.buttons = buttons
        self.hovered_keys = hovered_keys
        self.clicked_keys = clicked_keys
    
    
    # update_display with transparency effects   
    def update_display(self, image) -> None:
        """
        Takes a cv2 image and draws all the keyboard buttons, with different colours being used 
        for keys which have been hovered over or clicked.
        """
        overlay = image.copy()
        self.draw_buttons(overlay)
        cv2.addWeighted(overlay, self.alpha, image, 1 - self.alpha, 0, image)


    def draw_buttons(self, overlay):
        for button in self.buttons.values():
            x, y = button.get_position()
            w, h = button.get_size()
            if button in self.hovered_keys:
                self.draw_button(overlay, x, y, w, h, button.font_size, self.key_bg_on_hover, button.text, self.font_colour_on_hover)        
                if button in self.clicked_keys:
                    self.draw_button(overlay, x, y, w, h, button.font_size, self.key_bg_on_click, button.text, self.font_colour) 
            else:
                self.draw_button(overlay, x, y, w, h, button.font_size, button.bg_colour, button.text, self.font_colour)


    def draw_button(self, overlay, x, y, w, h, text_size, bg_colour, text, text_colour):
        text_offset_x = int(w*0.1)
        text_offset_y = int(h*0.6)
        cv2.rectangle(overlay, (x, y), (x + w, y + h), bg_colour, cv2.FILLED)
        cv2.putText(overlay, text, (x + text_offset_x, y + text_offset_y), self.font, text_size, text_colour, self.font_weight) 

# -------------------------------------------------------------------------------------

class NoseBoxElement(DisplayElement):
    def __init__(self, height: int, width: int) -> None:
        self._nose_box_start = None
        self._nose_box_end = None
        self._height = height
        self._width = width
        self._nose_point = None
        self._nose_box_size = None
        self.nose_box_centre = None
        super().__init__()

    def update_display(self, image) -> None:
        """
        Takes a cv2 image object and updates the image, adding in the nose box.
        if self._nose_box_centre is None, then do not show nose box
        """
        if self.nose_box_centre is None:
            return

        height_from_origin = self._height * (self.nose_box_centre[1] - self._nose_box_size)
        width_from_origin = self._width * (self.nose_box_centre[0] - self._nose_box_size)

        self._nose_box_start = (int(width_from_origin), int(height_from_origin))   #upper left
        self._nose_box_end = (int(width_from_origin + 2 * self._nose_box_size * self._width),
         int(height_from_origin + 2 * self._nose_box_size * self._height)) #bottom right
        
        if self._nose_box_start is not None:
            image = cv2.rectangle(image, self._nose_box_start, self._nose_box_end, self._colour_dict["blue"], 2)

        if self._nose_point is not None:
            image = cv2.line(image, (int(self._width * self.nose_box_centre[0]), int(self._height * self.nose_box_centre[1])), self._nose_point, self._colour_dict["green"], 1)
            image = cv2.circle(image, self._nose_point, 5, self._colour_dict["red"], -1)

    def update(self, nose_box_size, nose_point, nose_box_centre) -> None:
        """
        Takes in parameters and updates the nosebox's attributes accordingly.
        If no parameters are given the nosebox is no longer displayed
        """
        if nose_point is not None:
            self._nose_point = (int(nose_point[0] * self._width), int(nose_point[1] * self._height))
        self._nose_box_size = nose_box_size
        self.nose_box_centre = nose_box_centre

# -------------------------------------------------------------------------------------
# Active Mode Display
class ActiveModeNameElement(DisplayElement):
    """
    Display Element for an active mode name.
    """
    def __init__(self) -> None:
        # self._height = height
        # self._width = width
        self._active_mode_text = None
        super().__init__()

    def update_display(self, image) -> None:
        """
        Takes a cv2 image object and updates the image with the name of the active mode.
        """

        if self._active_mode_text is None:
            return

        # Currently print mode name in left upper corner
        text_pos = (8, 22)
        image = cv2.putText(
            image,
            text=self._active_mode_text,
            org=text_pos,
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.6,
            color=self._colour_dict["black"],
            thickness=1,
            lineType=cv2.LINE_AA
        )

    def update(self, name) -> None:
        """
        Takes in new mode name.
        :param name: New mode name
        :type name: str
        :return: None
        :rtype: None
        """
        if name is not None:
            self._active_mode_text = name

# -------------------------------------------------------------------------------------
# LowLight Indicator
class LowLightIndicatorElement(DisplayElement):
    def __init__(self) -> None:
        config = Config()
        self._check_low_light = config.get_data("general/view/low_light_indicator_on")
        self._min_brightness = config.get_data("general/view/brightness_threshold")
        super().__init__()


    def update_display(self, image):
        if not self._check_low_light:
            return
        
        grayscale = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        #blurred_image = cv2.blur(grayscale, (640, 480))
        average_brightness = cv2.mean(grayscale)
        #print("Brightness :", average_brightness)
        if average_brightness[0] < self._min_brightness:
            msg = "Your camera may be disconnected"
            msg2= "Or there is not enough light where you are"
            cv2.putText(image, msg, (160, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(image, msg2, (130, 255), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
            #print("Dark lighting")
    
    def update(self):
        return

# -------------------------------------------------------------------------------------
# Help Message Element
class HelpMessageElement(DisplayElement):
    def __init__(self) -> None:
        self._start_time = perf_counter()
        self._show = True
        super().__init__()

    def update_display(self, image) -> None:
        if not self._show:
            return
        
        text_pos = (470, 22)
        # white text with black outline, so that the message can be seen clearly both when
        # there is a black screen at startup (due to multiple cameras) and during normal operation
        cv2.putText(image, text="Press ? for Help", org=text_pos, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0,0,0), thickness=3, lineType=cv2.LINE_AA)
        cv2.putText(image, text="Press ? for Help", org=text_pos, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(255,255,255), thickness=1, lineType=cv2.LINE_AA)
    
    def update(self) -> None:
        if self._show:
            time = perf_counter() - self._start_time
            if time > 10:
                self._show = False

# -------------------------------------------------------------------------------------

class DrawFPSElement(DisplayElement):
    def __init__(self) -> None:
        self._fps = None
        super().__init__()

    def update_display(self, image) -> None:
        """
        Takes a cv2 image object and updates the image with the current FPS.
        """

        if self._fps is None:
            return

        text_pos = (600, 470)
        image = cv2.putText(
            image,
            text=self._fps,
            org=text_pos,
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.7,
            color=(0,)*3,
            thickness=1,
            lineType=cv2.LINE_AA
        )

    def update(self, fps: str) -> None:
        """
        Takes in new FPS value.
        :param fps: Current FPS value
        :type fps: str
        :return: None
        :rtype: None
        """
        if fps is not None:
            self._fps = fps

class ChangeCameraElement(DisplayElement):
    def __init__(self) -> None:
        self._display = False
        self._current_camera = None

        super().__init__()

    def update_display(self, image) -> None:
        """
        Takes a cv2 image object and updates the image with Camera Change 
        indicator and the current camera index.
        """
        if not self._display or self._current_camera is None:
            return

        text_pos = (30, 375)
        self.draw_outlined_text(image, "Camera Switch Mode On", text_pos, 1)
        index_pos = (30, 400)
        self.draw_outlined_text(image, "Current Camera: "+self._current_camera, index_pos, 0.8)

    
    def draw_outlined_text(self, image, text, text_pos, size) -> None:
        cv2.putText(
            image,
            text=text,
            org=text_pos,
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=size,
            color=(0,)*3,
            thickness=2,
            lineType=cv2.LINE_AA
        )
        cv2.putText(
            image,
            text=text,
            org=text_pos,
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=size,
            color=(255,)*3,
            thickness=1,
            lineType=cv2.LINE_AA
        )


    def update(self, display: bool, index: int) -> None:
        """
        Updates the display indicator and camera index variables
        
        :param dispaly: Display/hide change camera indicator
        :type display: bool
        :param index: Current camera index
        :type index: int
        :return: None
        :rtype: None
        """
        if display is not None:
            self._display = display
        if index is not None:
            self._current_camera = str(index)



# ------------------------- EYE MODULE VIEWERS ---------------------------------
class FaceBoxElement(DisplayElement):
    def __init__(self) -> None:
        self._startPos = None
        self._endPos = None
        super().__init__()

    def update_display(self, image) -> None:
        """
        Takes a cv2 image object and updates the image, adding a 
        facebox boundary (rectangle) in the frame.
        """
        if self._startPos is not None and self._endPos is not None:
            image = self.drawBox(image)

    def update(self, tl: Optional[np.array] = None, br: Optional[np.array] = None) -> None:
        """
        Update topLeft & Bottom right coordinate for boundary box
        """
        self._startPos = tl
        self._endPos = br

    def drawBox(self, image):
        colour = self._colour_dict["green"]
        width = 2
        frame = image
        frame = cv2.rectangle(frame,
                              self._startPos.astype(int), self._endPos.astype(int),
                              colour, width)
        return frame

# -------------------------------------------------------------------------------------

class HeadPosElement(DisplayElement):
    def __init__(self) -> None:
        self._headInfo = None
        self._headTl = None
        self._headBr = None
        super().__init__()

    def update_display(self, image) -> None:
        """
        Takes a cv2 image object and updates the image, adding 
        headVector in the frame with (ROLL, PITCH, YAW) info. 
        """

        # ONLY happens when face detected
        if self._headTl is not None and self._headBr is not None:
            image = self.drawHeadPos(image)

    def update(self, headInfo: Optional[np.array] = None, headTl: Optional[np.array] = None,
               headBr: Optional[np.array] = None) -> None:
        """
        Update information about head Roll, Pitch, Yaw
        """
        self._headInfo = headInfo
        self._headTl = headTl
        self._headBr = headBr

    # TODO: clean code
    def drawHeadPos(self, frame):

        faceBoundingBoxWidth = self._headBr[0] - self._headTl[0]
        faceBoundingBoxHeight = self._headBr[1] - self._headTl[1]

        # Draw headPoseAxes
        # Here head_position_x --> angle_y_fc  # Yaw
        #      head_position_y --> angle_p_fc  # Pitch
        #      head_position_z --> angle_r_fc  # Roll
        yaw = self._headInfo[0]
        pitch = self._headInfo[1]
        roll = self._headInfo[2]

        # for debug
        text = f"yaw: {yaw} \r\n pitch: {pitch} \r\n roll: {roll} \r\n"
        frame = self.draw_text(frame, text=text, uv_top_left=(0, 0))

        sinY = sin(yaw * pi / 180.0)
        sinP = sin(pitch * pi / 180.0)
        sinR = sin(roll * pi / 180.0)

        cosY = cos(yaw * pi / 180.0)
        cosP = cos(pitch * pi / 180.0)
        cosR = cos(roll * pi / 180.0)

        axis_ratio = 0.4
        axisLength = axis_ratio * faceBoundingBoxWidth
        xCenter = int(self._headTl[0] + faceBoundingBoxWidth / 2)
        yCenter = int(self._headTl[1] + faceBoundingBoxHeight / 2)

        # center to right
        cv2.line(frame, (xCenter, yCenter),
                 ((xCenter + int(axisLength * (cosR * cosY + sinY * sinP * sinR))),
                  (yCenter + int(axisLength * cosP * sinR))),
                 (0, 0, 255), thickness=2)
        # center to top
        cv2.line(frame, (xCenter, yCenter),
                 ((xCenter + int(axisLength * (cosR * sinY * sinP + cosY * sinR))),
                  (yCenter - int(axisLength * cosP * cosR))),
                 (0, 255, 0), thickness=2)

        # Center to forward
        cv2.line(frame, (xCenter, yCenter),
                 ((xCenter + int(axisLength * sinY * cosP)),
                  (yCenter + int(axisLength * sinP))),
                 (255, 0, 0), thickness=2)

        return frame

    # TODO: helper function to print text, need refactory
    def draw_text(self, img,
                  *,
                  text,
                  uv_top_left,
                  color=(255, 255, 255),
                  fontScale=0.5,
                  thickness=1,
                  fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                  outline_color=(0, 0, 0),
                  line_spacing=1.5,
                  ):
        """
        Draws multiline with an outline.
        """
        assert isinstance(text, str)

        uv_top_left = np.array(uv_top_left, dtype=float)
        assert uv_top_left.shape == (2,)

        for line in text.splitlines():
            (w, h), _ = cv2.getTextSize(
                text=line,
                fontFace=fontFace,
                fontScale=fontScale,
                thickness=thickness,
            )
            uv_bottom_left_i = uv_top_left + [0, h]
            org = tuple(uv_bottom_left_i.astype(int))

            if outline_color is not None:
                cv2.putText(
                    img,
                    text=line,
                    org=org,
                    fontFace=fontFace,
                    fontScale=fontScale,
                    color=outline_color,
                    thickness=thickness * 3,
                    lineType=cv2.LINE_AA,
                )
            cv2.putText(
                img,
                text=line,
                org=org,
                fontFace=fontFace,
                fontScale=fontScale,
                color=color,
                thickness=thickness,
                lineType=cv2.LINE_AA,
            )

            uv_top_left += [0, h * line_spacing]

        return img


class FaceLandMarkElement(DisplayElement):
    def __init__(self) -> None:
        self._headTl = None
        self._headBr = None
        self._landMarks = ()
        super().__init__()

    def update_display(self, image) -> None:
        """
        Takes a cv2 image object and updates the image, adding landmark points in the frame
        """

        # ONLY happens when face detected
        if self._headTl is not None and self._headBr is not None:
            image = self.drawLandMarks(image)

    def update(self, landmarks: Optional[tuple[np.array]] = (), headTl: Optional[np.array] = None,
               headBr: Optional[np.array] = None) -> None:
        """
        Update information about head Roll, Pitch, Yaw
        """
        self._headTl = headTl
        self._headBr = headBr
        self._landMarks = landmarks

    def drawLandMarks(self, frame):
        # var: point
        # type: np.array
        for point in self._landMarks:
            topLeft = self._headTl
            size = [self._headBr[0] - self._headTl[0], self._headBr[1] - self._headTl[1]]
            # print(point.x, point.y)
            center = topLeft + size * point
            # print(center)
            cv2.circle(frame, tuple(center.astype(int)), 2, (255, 255, 0), 4)
        return frame

# -------------------------------------------------------------------------------------

# TODO: clean code & update colour dict
class EyeGazeElement(DisplayElement):
    def __init__(self) -> None:
        self._headTl = None
        self._headBr = None
        self._gaze = None
        self._landmarks = ()
        super().__init__()

    def update_display(self, image) -> None:
        """
        Takes a cv2 image object and updates the image, draw gazeVector in the frame
        ONLY happens when face detected
        """
        if self._headTl is not None and self._headBr is not None:
            image = self.drawGaze(image)

    def update(self, headTl: Optional[np.array] = None, headBr: Optional[np.array] = None,
               landmarks: Optional[tuple[np.array]] = (), gaze: Optional[np.array] = None) -> None:
        self._headTl = headTl
        self._headBr = headBr
        self._gaze = gaze
        self._landmarks = landmarks

    def drawGaze(self, frame):
        faceBoundingBoxWidth = self._headBr[0] - self._headTl[0]
        faceBoundingBoxHeight = self._headBr[1] - self._headTl[1]

        myLandMark = self._landmarks

        # Draw Gaze vector with final frame
        # check testFile (about belowing indexes)

        left_eye_x = (myLandMark[0][0] * faceBoundingBoxWidth + self._headTl[0])

        left_eye_y = (myLandMark[0][1] * faceBoundingBoxHeight + self._headTl[1])

        right_eye_x = (myLandMark[1][0] * faceBoundingBoxWidth + self._headTl[0])
        right_eye_y = (myLandMark[1][1] * faceBoundingBoxHeight + self._headTl[1])

        nose_tip_x = (myLandMark[2][0] * faceBoundingBoxWidth + self._headTl[0])
        nose_tip_y = (myLandMark[2][1] * faceBoundingBoxHeight + self._headTl[1])

        left_lip_corner_x = (myLandMark[3][0] * faceBoundingBoxWidth + self._headTl[0])
        left_lip_corner_y = (myLandMark[3][1] * faceBoundingBoxHeight + self._headTl[1])

        leftEyeMidpoint_start = int((left_eye_x + right_eye_x) / 2)
        leftEyeMidpoint_end = int((left_eye_y + right_eye_y) / 2)
        rightEyeMidpoint_start = int((nose_tip_x + left_lip_corner_x) / 2)
        rightEyeMidpoint_End = int((nose_tip_y + left_lip_corner_y) / 2)

        # Gaze out
        arrowLength = 0.4 * faceBoundingBoxWidth
        # gaze = gaze_vector[0]
        gazeArrow_x = int((self._gaze[0]) * arrowLength)
        gazeArrow_y = int(-(self._gaze[1]) * arrowLength)

        cv2.arrowedLine(frame,
                        (leftEyeMidpoint_start, leftEyeMidpoint_end),
                        ((leftEyeMidpoint_start + gazeArrow_x),
                         leftEyeMidpoint_end + gazeArrow_y),
                        (0, 255, 0), 3)

        cv2.arrowedLine(frame,
                        (rightEyeMidpoint_start, rightEyeMidpoint_End),
                        ((rightEyeMidpoint_start + gazeArrow_x),
                         rightEyeMidpoint_End + gazeArrow_y),
                        (0, 255, 0), 3)

        return frame

# -------------------------------------------------------------------------------------

class TranscribeModeElement(DisplayElement):
    """
    Display Element for showing that speech transcription is enabled
    """
    def __init__(self) -> None:
        self._transcribing = False
        super().__init__()

    def update_display(self, image: np.ndarray) -> None:
        """
        Takes a cv2 image object and updates the image with the name of the active mode.
        :param image: The frame to draw onto
        :type image: np.ndarray
        """
        if self._transcribing:
            # bottom left corner
            text_pos = (5, 470)
            image = cv2.putText(
                image,
                text= "TRANSCRIPTION",
                org=text_pos,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.6,
                color=self._colour_dict["red"],
                lineType=cv2.LINE_AA
            )

    def update(self, transcribing: bool) -> None:
        """
        Takes in new mode name.
        :param transcribing: Whether the speech module is transcribing
        :type transcribing: bool
        """
        self._transcribing = transcribing

# -------------------------------------------------------------------------------------

class CorrectionModeElement(DisplayElement):
    """
    Display Element for showing that speech Correction mode is enabled during Transcription
    and without Transcription
    """
    def __init__(self) -> None:
        self._correction_mode = False
        self._transcriber_required = False
        super().__init__()

    def update_display(self, image: np.ndarray) -> None:
        """
        Takes a cv2 image object and updates the image with the name of the active mode.
        :param image: The frame to draw onto
        :type image: np.ndarray
        """
        if self._correction_mode:
            # bottom right corner
            text_pos = (5, 450)
            image = cv2.putText(
                image,
                text= "CORRECTION",
                org=text_pos,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=self._colour_dict["blue"],
                lineType=cv2.LINE_AA
            )

        # alternative message - Please first activate Transcribe mode
        if self._transcriber_required:
            text_pos2 = (5, 460)
            image = cv2.putText(
                image,
                text= "Correction mode requires Transcription. To activate say 'transcribe'",
                org=text_pos2,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=self._colour_dict["blue"],
                lineType=cv2.LINE_AA
            )

    def update(self, correction_mode: bool, transcriber_required: bool) -> None:
        """
        Takes in new mode name.
        :param correction_mode: Whether the speech module is in Correction mode
        :type correction_mode: bool
        """
        self._correction_mode = correction_mode
        self._transcriber_required = transcriber_required

# -------------------------------------------------------------------------------------

class SpeakerIdElement(DisplayElement):
    """
    Display Element for showing that Speaker Identification is enabled
    and for Speaker Locked (if only one user's voice is to be recognise)
    """
    def __init__(self) -> None:
        self._speaker_id = False
        self._speaker_locked = False
        self._speaker_lock_id = ""
        self._speaker_lock_name = ""
        super().__init__()

    def get_text_size(self, text):
        """
        Calculates the size of the text to display and adjust its position accordingly.
        Used to display the id and name of the locked speaker in the top right corner.
        """
        text_size = cv2.getTextSize(
        text,
        fontFace = cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.5,
        thickness=3
        )
        text_length_x = text_size[0][0]
        text_height_y = text_size[0][1]
        return text_length_x, text_height_y

    def update_display(self, image: np.ndarray) -> None:
        """
        Takes a cv2 image object and updates the image with the name of the active mode.
        :param image: The frame to draw onto
        :type image: np.ndarray
        """
        if self._speaker_id:
            # 1. First message - Speaker Identification on
            text_pos = (440, 22)
            text1 = "SPEAKER IDENTIFICATION"
            image = cv2.putText(
                image,
                text= text1,
                org=text_pos,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=self._colour_dict["gray"],
                thickness=3,
                lineType=cv2.LINE_AA
            )
            image = cv2.putText(
                image,
                text= text1,
                org=text_pos,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=self._colour_dict["orange2"],
                thickness=1,
                lineType=cv2.LINE_AA
            )

        # 2.1. Second message - Speaker Locked
        if self._speaker_locked:

            # Reminder: camera window size: 640, 480 = x, y
            # self._text_size(text) return format: ((50, 12), 6)
            text_pos2 = (490, 22)
            text2 = "SPEAKER LOCKED"
            image = cv2.putText(
                image,
                text= text2,
                org=text_pos2,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=self._colour_dict["gray"],
                thickness=3,
                lineType=cv2.LINE_AA
            )
            image = cv2.putText(
                image,
                text= text2,
                org=text_pos2,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=self._colour_dict["orange2"],
                thickness=1,
                lineType=cv2.LINE_AA
            )

            # 2.2. Second message - second line
            text3 = f"[{self._speaker_lock_id}]{self._speaker_lock_name}"
            text_length_x, text_height_y = self.get_text_size(text3)
            # Self regulated position - top right corner
            x_pos = 640 - text_length_x - 7
            y_pos = 0 + text_height_y * 2 + 17 

            text_pos3 = (x_pos, y_pos)

            # TODO: The code below makes design nicer but needs more testing for visibility
            image = cv2.putText(
                image,
                text= text3,
                org=text_pos3,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=self._colour_dict["gray"],
                thickness=3,
                lineType=cv2.LINE_AA
            )
            image = cv2.putText(
                image,
                text= text3,
                org=text_pos3,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=self._colour_dict["orange2"],
                thickness=1,
                lineType=cv2.LINE_AA
            )
            # 2.3. Second message - third line
            text_pos4 = (389, y_pos + text_height_y + 7)
            text4 = "[to unlock say 'stop speaker identify']"
            image = cv2.putText(
                image,
                text= text4,
                org=text_pos4,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.4,
                color=self._colour_dict["gray"],
                thickness=1,
                lineType=cv2.LINE_AA
            )

    def update(self, speaker_identification: bool, speaker_locked: bool, spk_lock_id: str, spk_lock_name: str) -> None:
        """
        Takes in new view name.
        :param speaker_identification: Whether the speech module is in speaker identification mode
        :param speaker_locked:
        :type speaker_identification: bool
        :type speaker_locked: bool
        """
        self._speaker_id = speaker_identification
        self._speaker_locked = speaker_locked

        self._speaker_lock_id = spk_lock_id
        self._speaker_lock_name = spk_lock_name

# -------------------------------------------------------------------------------------

class NoseBoundElement(DisplayElement):
    """
    Display Element for showing which NoseBox boundaries are set in Nose In-Range Mode
    """
    def __init__(self) -> None:
        self.direction = "None"
        self.presented_text = ""
        super().__init__()

    def update_display(self, image: np.ndarray) -> None:
        """
        Takes a cv2 image object and updates the image with the name of the active mode.
        
        :param image: The frame to draw onto
        :type image: np.ndarray
        """
        if self.direction == "none":
            return
        elif self.direction == "right" or self.direction == "left":
            self.presented_text = self.direction + " range is calibrated"
        else:
            self.presented_text = "Both ranges calibrated"

        if self.direction != "none":
            # bottom corner
            text_pos = (10, 440)
            image = cv2.putText(
                image,
                text= self.presented_text,
                org=text_pos,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.7,
                color=self._colour_dict["white"],
                lineType=cv2.LINE_AA
            )

    def update(self, direction) -> None:
        """
        Takes in new mode name.
        :param transcribing: Whether the speech module is transcribing
        :type transcribing: bool
        """
        self.direction = direction
  
