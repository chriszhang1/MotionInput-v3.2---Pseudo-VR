import ctypes
import math

import numpy as np

from scripts.tools import Config
from scripts.tools.json_editors.json_editor import JSONEditor
from .simple_gesture_event import SimpleGestureEvent

config = Config()


# a class to be to store customized gestures
class CustomizedGestureEvent(SimpleGestureEvent):
    _event_trigger_types = {"triggered"}
    _gesture_types = set()
    _bodypart_types = set()

    _delay = False
    _time_count = 0
    _audio_detected = False
    _detected_phrase = ""

    def __init__(self, gesture_name, gesture_type, bodypart_name, fps, action_type, frame_count,
                 camera_w_h_ratio, phrase, attention_point, test_mode):
        self._timer = 0  # so that it doesn't get activated at the beginning
        self.config_path = "customize_gestures\\"
        # put into /data folder
        self.action_type = action_type
        self._gesture_name = gesture_name
        self._gesture_type = gesture_type
        self._left_hand_name = None
        self._right_hand_name = None
        self._camera_w_h_ratio = camera_w_h_ratio
        self._phrase = phrase  # for the voice activation
        self._attention_point = attention_point
        self._test_mode = test_mode
        if bodypart_name == 'Both':
            self._left_hand_name = gesture_name + '_Left'
            self._right_hand_name = gesture_name + '_Right'
            self._gestures = {"dom_hand": {self._left_hand_name: None},
                              "off_hand": {self._right_hand_name: None}}
            self.set_gesture_types(self._left_hand_name)
            self.set_gesture_types(self._right_hand_name)
            self._two_hands_flag = True
        else:
            self._gestures = {gesture_type: {gesture_name: None}}
            self.set_gesture_types(gesture_name)
            self._two_hands_flag = False
        super().__init__(CustomizedGestureEvent._gesture_types, CustomizedGestureEvent._event_trigger_types,
                         CustomizedGestureEvent._bodypart_types)

        self._trace = self._get_recorded_trace_from_json()
        self._audio_flag = False
        self._window_size = max(math.ceil(frame_count / fps), 2) * fps
        self._threshold = 5
        self.key_frames_number = 16
        self._frame_buffer = []
        self.window_step = self._window_size
        self._samples = np.linspace(0, self._window_size - 1, num=16, dtype=int)
        self._time_setting = config.get_data(f"customize_gestures/time_setting") * fps

    @classmethod
    def set_gesture_types(cls, gesture_name):
        cls._gesture_types.add(gesture_name)

    def update(self):
        """check if the audio is detected and if the timer is still active"""
        if self._audio_flag and self._timer < self._time_setting:
            self._timer += 1

            gesture_landmark_record = dict()
            for hand, hand_gestures in self._gestures.items():
                for name in hand_gestures.keys():
                    bodypart_name = self._gestures[hand][name].get_bodypart_name()

                    wrist_landmark = self._gestures[hand][name].get_last_position().get_landmark("wrist")  #
                    middle_base_landmark = self._gestures[hand][name].get_last_position().get_landmark("middle_base")  #
                    distance_to_camera = 1 - self.distance(wrist_landmark, middle_base_landmark)
                    attention_point_position = self._gestures[hand][name].get_last_position().get_landmark(
                        self._attention_point)  # [x,y,z]
                    position = [attention_point_position[0], attention_point_position[1], attention_point_position[2],
                                distance_to_camera * 45.0]

                    angle = self.calculate_angle(position)
                    gesture_landmark_record[bodypart_name] = angle

            self._frame_buffer.append(gesture_landmark_record)

            if CustomizedGestureEvent._delay:
                self._frame_buffer = []
                if CustomizedGestureEvent.time_count <= self.window_step:
                    CustomizedGestureEvent.time_count += 1
                else:
                    CustomizedGestureEvent.time_count = 0
                    CustomizedGestureEvent._delay = False
                    return
            if len(self._frame_buffer) == self._window_size:  # buffer full
                temp_keyframe_list = self._extract_key_frames(self._frame_buffer)  # extract 16 keyframes
                diff_feature = self.translate_into_diff(temp_keyframe_list)

                if self.check_if_static(diff_feature):
                    self._frame_buffer.pop(0)
                    return
                recognized_flag, action_flag = self._check_similarity(diff_feature)
                # loop and check if the gesture is recognized
                if recognized_flag and action_flag:  # similarity small enough, recognized
                    # call computer event
                    CustomizedGestureEvent._delay = True
                    CustomizedGestureEvent.time_count = 0

                    if self.action_type == 'Point':
                        attention_point = self._gestures['hand'][name].get_last_position().get_landmark(
                            self._attention_point)
                        self._event_triggers["triggered"](attention_point[0], attention_point[1])
                    else:
                        self._event_triggers["triggered"]()
                    # TODO: this is a quick fix for the calibration, needs to be reconsidered.
                    if self._test_mode == 1:
                        ctypes.windll.user32.MessageBoxW(0, "OK", "Customize gesture calibration")
                    # print("trigger")
                else:
                    self._frame_buffer.pop(0)
        elif self._timer >= 500:  # reset timer to 500 so it won't activate
            self._timer = 0
            CustomizedGestureEvent._audio_detected = False
            CustomizedGestureEvent._detected_phrase = ""
            self._audio_flag = False
            print("time out")

    def _get_recorded_trace_from_json(self):
        """get original trace data from json file"""
        file_name = self.config_path + self._gesture_name + ".json"
        json_editor = JSONEditor(file_name)
        data = json_editor.get_all_data()
        return data

    def check_if_static(self, diff_feature):
        """check if the user's hand kept still for a while, if so, return true
            :param diff_feature: the difference between the current frame and the last frame
            :return: True if the user's hand is still, False otherwise
        """
        var_list = []
        for bodypart_name, diff_feature in diff_feature.items():
            xy = [abs(k[0]) for k in diff_feature]
            yx = [abs(k[1]) for k in diff_feature]
            z = [abs(k[2]) for k in diff_feature]
            var_x = np.sum(xy)
            var_y = np.sum(yx)
            var_z = np.sum(z)
            var_list.append(var_x)
            var_list.append(var_y)
            var_list.append(var_z)
        for var_t in var_list:
            if var_t > 25.0:
                return False
        return True

    def _check_similarity(self, diff_feature):
        """check similarity the live feed and gesture data and see if the gesture is recognized
        :param diff_feature: the difference between the live feed and gesture data
        """
        min_distance = self._threshold
        recognized_gesture_name = "no action"
        trace_distance_list = []
        all_trace_similarity = []

        for bodypart_name in self._trace.keys():
            trace_feature1 = []
            trace_feature2 = []
            trace_distance = 0.0
            for i in range(len(diff_feature[bodypart_name])):
                trace_distance += self.calculate_trace_distance(diff_feature[bodypart_name][i],
                                                                self._trace[bodypart_name][i])
                trace_feature1.append(diff_feature[bodypart_name][i])
                trace_feature2.append(self._trace[bodypart_name][i])

            trace_distance = trace_distance / len(diff_feature[bodypart_name])
            trace_distance_list.append(trace_distance)
            all_trace_similarity.append(self.calculate_trace_similarity(trace_feature1, trace_feature2))

        distance = 0.0
        for t_distance in trace_distance_list:
            distance += t_distance
        distance = distance / len(trace_distance_list) / 2

        # print(self._gesture_name + " : " + str(distance))
        if distance < min_distance:
            flag = True
            for trace_similarity in all_trace_similarity:
                # compare trace cosine similarity to show the movement backward or forward
                if trace_similarity < 0:
                    # print(self._gesture_name + " trace_similarity_xy: " + str(
                    #     trace_similarity_1) + " trace_similarity_yx: " + str(trace_similarity_2))
                    return False, True
                elif trace_similarity < 0.6:  # 0.6 generated by testing
                    flag = False
                    break
            if flag:
                recognized_gesture_name = self._gesture_name
                min_distance = distance

        if recognized_gesture_name != "no action" and min_distance <= self._threshold:
            # print("recognized: " + recognized_gesture_name + " distance: " + str(min_distance))
            return True, True
        else:
            return False, False

    def _extract_key_frames(self, frame_sequence):  # make sure there are at least 16 key frames
        """extract key frames from the frame sequence
        :param frame_sequence:
        :return: key_frames: a list of key frames
        """
        key_frames = []
        for idx in self._samples:
            key_frames.append(frame_sequence[idx])
        return key_frames

    @classmethod
    def notify_audio_flag(cls, phrase):
        """notify the gesture recognizer that audio is detected
        :param phrase: the phrase to detected
        """
        cls._audio_detected = True
        cls._detected_phrase = phrase
        print("detected " + phrase)

    def _check_state(self):
        if not CustomizedGestureEvent._audio_detected:
            self._state = False
            return
        if self._phrase == CustomizedGestureEvent._detected_phrase:
            self._audio_flag = True
        if not self._audio_flag:
            self._state = False
        else:
            if self._two_hands_flag:
                self._state = self._gestures["dom_hand"][self._left_hand_name] is not None and \
                              self._gestures["off_hand"][self._right_hand_name] is not None
            else:
                self._state = self._gestures[self._gesture_type][self._gesture_name] is not None

    def distance(self, point1, point2) -> float:
        """calculate the distance between two points
        :param point1: (x, y)
        :param point2: (x, y)
        :return: distance
        """
        dx = point1[0] - point2[0]
        dy = point1[1] - point2[1]
        dz = point1[2] - point2[2]
        return math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

    def calculate_cosine_similarity(self, vector1, vector2):
        """calculate the cosine value between two vectors using numpy
        :param vector1: a list of feature points
        :param vector1: a list of feature points
        :return: the cosine value between two traces
        """
        num = np.dot(vector1, vector2)
        s = np.linalg.norm(vector1) * np.linalg.norm(vector2)
        if s == 0.0:
            return 0.0
        else:
            return num / s

    def calculate_trace_similarity(self, feature1, feature2):
        """calculate the similarity between two gesture feature traces
        :param feature1: a list of feature points
        :param feature2: a list of feature points
        :return: the similarity between two traces
        """

        x_xy = np.array([z[0] for z in feature1])
        y_xy = np.array([z[0] for z in feature2])
        cos_xy = self.calculate_cosine_similarity(x_xy, y_xy)
        return cos_xy

    def calculate_trace_distance(self, feature1, feature2):
        """calculate the distance between two gesture feature traces
        :param feature1: a list of feature points
        :param feature2: a list of feature points
        :return: the distance between two traces
        """

        x = np.array(feature1)
        y = np.array(feature2)
        return np.linalg.norm(x - y)

    def calculate_angle(self, value):
        """transform location to angle inralation of the top left and right conner
        :param value: a location
        :return: the angle
        """
        angle = [math.degrees(math.atan(self._camera_w_h_ratio * (float(value[0]) / float(value[1])))),
                 math.degrees(math.atan(self._camera_w_h_ratio * (float(1.0 - value[0]) / float(value[1])))),
                 float(value[3])]
        return angle

    def translate_into_diff(self, key_frames):
        """translate the key frames into diff value
        :param key_frames: a list of key frames
        :return: a list of diff value
        """
        init = dict()
        key_frames_feature = []
        for bodypart_name, values in key_frames[0].items():
            init[bodypart_name] = values
        key_frames = key_frames[1:]
        for key_frame in key_frames:
            frame_temp = dict()
            for bodypart_name, key_values in key_frame.items():
                bodypart_temp = []

                bodypart_temp.append(key_values[0] - init.get(bodypart_name)[0])
                bodypart_temp.append(key_values[1] - init.get(bodypart_name)[1])
                bodypart_temp.append(key_values[2] - init.get(bodypart_name)[2])

                frame_temp[bodypart_name] = bodypart_temp
            key_frames_feature.append(frame_temp)
        output = dict()
        for frame in key_frames_feature:
            for key, values in frame.items():
                if output.get(key, None) is not None:
                    output[key].append(values)
                else:
                    output[key] = [values]

        return output
