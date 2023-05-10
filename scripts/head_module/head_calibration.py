"""
Author: Alex Clarke

Interactive GUI for facial gesture calibration.
"""

import cv2
from scripts.tools import Camera
from scripts.tools.config import Config

from scripts.core.raw_data import RawData

from scripts.head_module.head_biometrics import HeadBiometrics
from scripts.head_module.head_landmark_detector import HeadLandmarkDetector

from scripts.speech_module.speech_landmark_detector import SpeechLandmarkDetector
from scripts.speech_module.speech_position import SpeechPosition

import time

from .calibration_ui import *
from .calibration_pose import *



class _HeadCalibrator:

    WINDOW_NAME = "Facial Calibration"
    EXPORT_PRECISION_DP = 5 # decimal places for calibration parameters stored in JSON

    def __init__(self):

        self._camera = Camera()
        self._overlay = Overlay()

        self._config = Config()

        self._pose_sequence = (None, baseline, tilt_left, tilt_right, turn_left, turn_right, None)
        self._pose_index = 0

        self._pose_confidence_default = self._config.get_data("modules/head/pose_confidence_default")
        self._pose_confidence_increment = self._config.get_data("modules/head/pose_confidence_increment")
        self._pose_confidence_min = self._config.get_data("modules/head/pose_confidence_min")

        """
        Total number of poses, excluding start and end poses which are empty.
        """
        self._pose_count = sum([1 if pose is not None else 0 for pose in self._pose_sequence])

        self._face_detector = HeadLandmarkDetector()
        self._speech_detector = SpeechLandmarkDetector()

        self._info_elements = None
        self._graphic_elements = None

        self._running = False

        self._current_phrase = None

        self._speech_mappings = { 
            "continue": self._navigate_next,
            "return": self._navigate_back,
            "lower": self._increase_sensitivity,
            "higher": self._decrease_sensitivity,
        }

        self._tones = { "record_start": Tone(233, 0.15, 0.85), "record_end": Tone(311, 0.15, 0.85), "metric_activated": Tone(392, 0.25, 0.85) }

        self._results = {}

        self._completed = False

    def _build(self):


        big_info = self._overlay.add_element(TextBox("", (0, 0), 1.8, Colour.WHITE))
        small_info = self._overlay.add_element(TextBox("", (0, 0), 1, Colour.WHITE))

        navigation_info = self._overlay.add_element(TextBox("", (0, 0), 0.9, Colour.WHITE))

        countdown_info = self._overlay.add_element(TextBox("", (0, 0), 2, Colour.WHITE))
        step_info = self._overlay.add_element(TextBox("", (0, 0), 0.9, Colour.WHITE, centred=False))

        recording_bar = self._overlay.add_element(ParameterBar(colour=Colour.RED))
        step_bar = self._overlay.add_element(StepBar(divisions=self._pose_count))

        metric_slider = self._overlay.add_element(ThresholdSlider(min_value=self._pose_confidence_min, max_value=1, clip_start=self._pose_confidence_min, clip_end=1, colour=Colour.WHITE, toggle_colour=Colour.BLUE, accent_colour=Colour.LIGHT_GREY))

        self._info_elements = [big_info, small_info, countdown_info, step_info, navigation_info]
        self._graphic_elements = [recording_bar, step_bar, metric_slider]

        cv2.namedWindow(_HeadCalibrator.WINDOW_NAME)

        self._running = True

        self._completed = False

    def run(self):

        self._build()

        while self._running:

            frame, biometrics = self._capture_biometrics()

            self._capture_speech()

            if biometrics is None:
                continue

            self._update_current_pose(frame, biometrics)

            self._update_ui_elements(frame)

            cv2.imshow(_HeadCalibrator.WINDOW_NAME, frame)

            self._check_keyboard_inputs()

            if cv2.getWindowProperty(_HeadCalibrator.WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                self.exit()

        self._terminate()

    def exit(self):

        if self._running:
            self._running = False

    def _update_current_pose(self, frame, biometrics):

            current_pose = self._pose_sequence[self._pose_index]

            if current_pose is not None:
         
                metric_values = [biometrics.get_frame_metric(source) for source in current_pose.biometric_sources]

                current_state, changed_state = current_pose.update(metric_values)

                if changed_state:

                    if current_state == Pose.RECORDING:

                        self._tones["record_start"].play()

                    elif current_state == Pose.TUNING:

                        self._tones["record_end"].play()

                        if not current_pose.is_saved():
                            pose_results = current_pose.save()

                            for result in pose_results:
                                self._results[result] = pose_results[result]

            
                if current_state == Pose.TUNING:

                    current_pose.update_confidences(self._results)

                elif current_state == Pose.SAVING:

                    current_pose.update_confidences(self._results)

                    if current_pose.is_paused():

                        current_pose.set_previous_state() # Return to tuning overlay when complete
                        current_pose.resume()


    def _update_ui_elements(self, frame):

        frame_height, frame_width = frame.shape[:2]
        centre_x, centre_y = (int(frame_width/2), int(frame_height/2))

        big_info, small_info, countdown_info, step_info, navigation_info = self._info_elements
        recording_bar, step_bar, metric_slider = self._graphic_elements

        big_info.location = (centre_x, centre_y - 20)
        small_info.location = (centre_x, centre_y + 40)
        countdown_info.location = (centre_x, centre_y + 140)
        step_info.location = (recording_bar.origin[0], recording_bar.origin[1] - recording_bar.size[1])

        navigation_info.location = (centre_x, centre_y - 200)

        big_info.colour = Colour.WHITE

        bar_margin = 20
        bar_size = (frame_width - bar_margin * 2, 25)
        recording_bar.origin = step_bar.origin = metric_slider.origin = (bar_margin, frame_height - bar_margin - bar_size[1])
        recording_bar.size = step_bar.size = metric_slider.size = bar_size

        metric_slider.toggle_size = (bar_size[0] / 50, bar_size[1] * 1.4)

        step_info.visible = step_bar.visible = False
        recording_bar.visible = False
        metric_slider.visible = False

        countdown_info.visible = False
        navigation_info.visible = False


        current_pose = self._pose_sequence[self._pose_index]

        big_info.content = ""
        small_info.content = ""

        if current_pose is not None:

            pose_state, pose_progress = current_pose.get_progress()
            stage_progress, countdown_remaining = pose_progress

            if pose_state == Pose.AWAITING:

                big_info.content = "Get ready."
                big_info.colour = Colour.GREEN

                small_info.content = "In this stage, you will need to \n%s." %current_pose.hint

                step_info.visible = step_bar.visible = True
                step_bar.index = self._pose_index - 1

            elif pose_state == Pose.RECORDING:

                big_info.content = current_pose.prompt
                big_info.colour = Colour.RED

                small_info.content = "Recording..."

                countdown_info.content = "%d" %(countdown_remaining + 1)
                countdown_info.visible = True

                recording_bar.parameter = stage_progress
                recording_bar.visible = True

            elif pose_state == Pose.TUNING or pose_state == Pose.SAVING:

                big_info.colour = Colour.BLUE

                confidences = current_pose.get_last_confidences()
                
                if len(confidences) > 0:
                    
                    metric_confidence = list(confidences.values())[0]

                    metric_slider.visible = True

                    metric_slider.bar_value = metric_confidence["parameter"]
                    metric_slider.toggle_value = current_pose.get_threshold()

                    metric_colour = Colour.GREEN if metric_confidence["activated"] else Colour.YELLOW
                    metric_slider.colour = metric_colour
                    big_info.colour = metric_colour


                    if metric_confidence["changed"] and metric_confidence["activated"]:

                        self._tones["metric_activated"].play()

                        if pose_state == Pose.TUNING:

                            current_pose.set_next_state()

                    big_info.content = "Adjust..."
                    small_info.content = "Say 'higher' or 'lower' or use the\n'+' and '-' keys to adjust the toggle\nuntil you can just about hit the\ntarget by %s." %current_pose.friendly_name

                    if pose_state == Pose.SAVING:

                        navigation_info.visible = True
                        navigation_info.content = "Continue - say 'continue' or press 'enter'.\nRetry - say 'return' or press 'backspace'."


                else:

                    big_info.content = "Saved."
                    small_info.content = "Say 'continue' or press 'enter'\nfor the next step.\n\nSay 'return' or press 'backspace'\nto retry a step or go back."

  
            step_info.content = "Step %d of %d" %(self._pose_index, self._pose_count)

        else:

            big_info.colour = Colour.YELLOW
            

            if self._pose_index == 0:
                big_info.content = "Facial Calibration"
                small_info.content = "Get ready to calibrate gestures.\nThis will take a couple of minutes.\n\nSay 'continue' or press 'enter'\nto proceed."

            else:
                big_info.content = "Calibration complete."
                small_info.content = "Say 'continue' or press 'enter'\nto launch MotionInput."


        self._overlay.update(frame)

    def _set_last_pose(self):

        if self._pose_index > 0:

            self._pose_index -= 1

            current_pose = self._pose_sequence[self._pose_index]
    
            if current_pose is not None:
                current_pose.restart(self._pose_confidence_default)

    def _set_next_pose(self):

        if self._pose_index < len(self._pose_sequence) - 1:
         
            self._pose_index += 1

            current_pose = self._pose_sequence[self._pose_index]

            if current_pose is not None:
                current_pose.start(self._pose_confidence_default)
            
        else:
            self._completed = True
            self._running = False

    def _navigate_next(self):

        current_pose = self._pose_sequence[self._pose_index]

        if current_pose is None:
            self._set_next_pose()
        elif current_pose is not None:
            
            current_state = current_pose.get_state()
            
            if current_state == Pose.TUNING or current_state == Pose.SAVING:
                self._set_next_pose()


    def _navigate_back(self):

        current_pose = self._pose_sequence[self._pose_index]

        if current_pose is not None and current_pose.get_state() != Pose.AWAITING:
            current_pose.restart(self._pose_confidence_default)

        else:
            self._set_last_pose()

    def _increase_sensitivity(self):

        current_pose = self._pose_sequence[self._pose_index]

        if current_pose is not None and current_pose.is_saved():

            threshold = current_pose.get_threshold() - self._pose_confidence_increment
            current_pose.set_threshold(min(1, max(self._pose_confidence_min, threshold)))

    def _decrease_sensitivity(self):

        current_pose = self._pose_sequence[self._pose_index]

        if current_pose is not None and current_pose.is_saved():

            threshold = current_pose.get_threshold() + self._pose_confidence_increment
            current_pose.set_threshold(min(1, max(self._pose_confidence_min, threshold)))

    def _check_keyboard_inputs(self):

        key = cv2.waitKey(1)

        # Enter
        if key == ord("\r"):

            self._navigate_next()

        # Backspace
        elif key == 8:

            self._navigate_back()

        # '+'
        elif key == ord("+"):

            self._decrease_sensitivity()

        # "-"
        elif key == ord("-"):

            self._increase_sensitivity()

    def _check_speech_inputs(self):

        if self._current_phrase in self._speech_mappings:

            self._speech_mappings[self._current_phrase]()

    def _capture_biometrics(self):

        """
        Extract biometric data from camera frame.
        """
        frame, _ = self._camera.read()

        frame_data = RawData()
        self._face_detector.get_raw_data(frame_data, frame)

        landmarks = frame_data.get_data("head")
        biometrics = None

        if landmarks is not None:

            biometrics = HeadBiometrics(landmarks)

        return frame, biometrics

    def _capture_speech(self):

        speech_data = RawData()
        self._speech_detector.get_raw_data(speech_data, None)

        current_phrase = list(speech_data.get_data("speech").keys())[0]

        if current_phrase:

            if self._current_phrase != current_phrase:

                self._current_phrase = current_phrase

                self._check_speech_inputs()

        else:

            self._current_phrase = None

    def _save(self):

        """
        Use a weighted average to tune the sensitivity of gestures.
        Values from 0 to 1, where lower means easier to trigger.
        """
        editor = self._config.get_editor()

        for pose in self._pose_sequence:

            if pose is not None and len(pose.ranges) > 0:

                _, range_min_name, range_max_name = pose.ranges[0]

                exported_data = None

                if pose.is_saved():

                    range_min = self._results[range_min_name]
                    range_max = self._results[range_max_name]
                    range_param = pose.get_threshold()
                    range_val = range_min + range_param * (range_max - range_min)

                    range_data = {
                        "range_min": round(range_min, _HeadCalibrator.EXPORT_PRECISION_DP), 
                        "range_max": round(range_max, _HeadCalibrator.EXPORT_PRECISION_DP),
                        "range_param": round(range_param, _HeadCalibrator.EXPORT_PRECISION_DP), 
                        "range_val": round(range_val, _HeadCalibrator.EXPORT_PRECISION_DP)
                    }

                    exported_data = range_data

                else:

                    default_data = editor.get_data("modules/head/default_calibration/%s" %pose.name)
                    exported_data = default_data

                editor.update("modules/head/user_calibration/%s" %pose.name, exported_data)

        # Current behaviour: if calibration finished (or cancelled), do not force-run on next boot.
        editor.update("modules/head/run_calibration", "false") # if self._completed else "true"
        editor.save()

    def _terminate(self):

        # Destroying only this window gives a NULL window error
        # This is also the case for the view.py class.
        cv2.destroyAllWindows() 

        self._save()


HeadCalibrator = _HeadCalibrator() # Global variable behaves like a singleton 


