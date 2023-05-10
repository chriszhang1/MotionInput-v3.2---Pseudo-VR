import json
import math
import os

import cv2
import numpy as np

from scripts import RawData, HandPosition, HandLandmarkDetector, BodyLandmarkDetector


class CustomizeGestureRecorder:
    events_to_triggers_dict = {
        "Double Click": {"triggered": ["AOIMouse", "double_click"]},
        "Zoom": {"triggered": ["AOIMouse", "zoom"]},
        "Scroll": {"triggered": ["AOIMouse", "scroll"]},
        "Point": {"triggered": ["AOIMouse", "move_cursor"]},
        "Up": {"triggered": ["Keyboard", "up_arrow_press"]},
        "Down": {"triggered": ["Keyboard", "down_arrow_press"]},
        "Right": {"triggered": ["Keyboard", "right_arrow_press"]},
        "Left": {"triggered": ["Keyboard", "left_arrow_press"]},
        "Delete": {"triggered": ["Keyboard", "delete_press"]}
    }

    def __init__(self):
        self.config_path = os.path.dirname(os.path.realpath(__file__)) + "\\..\\..\\data\\"
        self.gesture_editor = None
        self.mode_editor = None
        self.event_editor = None
        self.customize_gesture_dir = self.config_path + 'customize_gestures'
        if not os.path.exists(self.customize_gesture_dir):
            os.makedirs(self.customize_gesture_dir)

        self.gesture_sequence = []
        self.key_frames_number = 16
        self._primitives_names = ["palm_facing_camera", "hand_closed",
                                  "thumb_folded", "index_folded", "middle_folded", "ring_folded", "pinky_folded",
                                  "thumb_stretched", "index_stretched", "middle_stretched", "ring_stretched",
                                  "pinky_stretched",
                                  "thumb_pinched", "index_pinched", "middle_pinched", "ring_pinched", "pinky_pinched"]
        self.landmark_detector = None
        self.gesture_type = None
        self.body_part_name_list = None
        self.mode_name = 'customize'
        self.test_mode_name = 'customize_gesture_calibration'
        self.bodypart_name = None
        self.camera_w_h_ratio = 0
        self.fps = 0
        self.hand_position_features = dict()

    def set_recorder(self, gesture_type, bodypart_name, gesture_editor, mode_editor, event_editor):
        self.gesture_editor = gesture_editor
        self.mode_editor = mode_editor
        self.event_editor = event_editor
        self.gesture_type = gesture_type
        self.bodypart_name = bodypart_name
        if gesture_type == 'hand':
            self.landmark_detector = HandLandmarkDetector()
        elif gesture_type == 'body':
            self.landmark_detector = BodyLandmarkDetector()

        if bodypart_name == 'Both':
            self.body_part_name_list = ['Left', 'Right']
            self.hand_position_features['Left'] = []
            self.hand_position_features['Right'] = []
        else:
            self.body_part_name_list = [bodypart_name]
            self.hand_position_features[bodypart_name] = []

    def get_static_gesture(self, angle_change_flag):
        """ Get static gesture (configuration of the fingers) from the gesture sequence.
        :param angle_change_flag:
        """
        static_gesture = dict()
        for name in self.body_part_name_list:
            gesture_features = self.hand_position_features[name]
            benchmark_gesture = gesture_features[0]
            primitive_names = list(benchmark_gesture.get_primitives_names())
            benchmark_dict = dict()
            for primitive_name in primitive_names:
                benchmark_dict[primitive_name] = bool(benchmark_gesture.get_primitive(primitive_name))
            if angle_change_flag:
                primitive_names.remove('palm_facing_camera')
                if benchmark_dict.get('palm_facing_camera', None) is not None:
                    benchmark_dict.pop('palm_facing_camera')
            for i in range(1, len(gesture_features)):
                for primitive_name in primitive_names:
                    if benchmark_gesture.get_primitive(primitive_name) != \
                            gesture_features[i].get_primitive(primitive_name) \
                            and benchmark_dict.get(primitive_name, None) is not None:
                        benchmark_dict.pop(primitive_name)
            static_gesture[name] = benchmark_dict
        # print(static_gesture)
        return static_gesture

    def record_gesture_from_file(self, file_path, gesture_type, bodypart_name, gesture_tag, angle_change_flag,
                                 phrase, attention_point, mouse_and_key_event,
                                 gesture_editor, mode_editor, event_editor):
        """process a vid file into gesture
        :param file_path:
        :param gesture_type: hand or body
        :param bodypart_name: Left or Right
        :param gesture_tag: gesture tag
        :param angle_change_flag: if angle changed
        :param phrase: phrase
        :param attention_point: attention point
        :param mouse_and_key_event: mouse and key event
        :param gesture_editor: gesture editor from motioninput.api
        :param mode_editor: mode editor from motioninput.api
        :param event_editor: event editor from motioninput.api
        """
        # from local MP4 to trace data
        videoCapture = cv2.VideoCapture(file_path)
        fps = videoCapture.get(cv2.CAP_PROP_FPS)
        self.fps = int(fps)
        self.camera_w_h_ratio = float(
            videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH) / videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ret, frame = videoCapture.read()
        frame_sequence = []
        while ret:
            image = cv2.flip(frame, 1)
            # image = frame
            frame_sequence.append(image)
            ret, frame = videoCapture.read()
        videoCapture.release()
        self.set_recorder(gesture_type, bodypart_name, gesture_editor, mode_editor, event_editor)
        hand_loss_count = 0
        frame_count = len(frame_sequence)
        last_landmarks = dict()
        for frame in frame_sequence:
            frame_data = RawData()
            self.landmark_detector.get_raw_data(frame_data, frame)
            gesture_landmark_record = dict()
            loss_flag = False
            for name in self.body_part_name_list:
                detected_body_part = frame_data.get_data(name)
                if detected_body_part is None:
                    hand_loss_count += 1
                    # if Mediapipe get no hand data
                    temp_last_landmarks = last_landmarks.get(name, None)
                    if temp_last_landmarks is None:
                        loss_flag = True
                        break
                    else:
                        detected_body_part = temp_last_landmarks
                gesture_landmark_record[name] = dict()
                for k in detected_body_part.keys():
                    coordinates = detected_body_part[k]
                    gesture_landmark_record[name][k] = coordinates
                hand_position = HandPosition(detected_body_part)
                self.hand_position_features[name].append(hand_position)
                last_landmarks[name] = detected_body_part
            if not loss_flag:
                self.gesture_sequence.append(gesture_landmark_record)
        loss_rate = float(hand_loss_count / frame_count)
        if loss_rate > 0.5:
            raise Exception("RECORD ERROR: You have to record the gesture again as MediaPipe cannot detect your hand!")
        static_gesture = self.get_static_gesture(angle_change_flag)
        if len(static_gesture) == 0:
            raise Exception("RECORD ERROR: You have to record the gesture again, please keep your gesture!")
        key_frames_feature = self.extract_key_frames(attention_point)

        out = self.write_into_file(gesture_tag, key_frames_feature, static_gesture, frame_count, phrase,
                                   attention_point, mouse_and_key_event)
        return out

    def calculate_angle(self, value):
        """transform location to angle inralation of the top left and right conner
            :param value: a location
            :return: the angle
        """
        angle = [math.degrees(math.atan(self.camera_w_h_ratio * (float(value[0]) / float(value[1])))),
                 math.degrees(math.atan(self.camera_w_h_ratio * (float(1 - value[0]) / float(value[1]))))]
        return angle

    def translate_into_diff(self, key_frames):
        """translate the key frames into diff value
            :param key_frames: a list of key frames
            :return: a list of diff value
        """
        key_frames_feature = []
        # initial data
        init = dict()
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

    def extract_feature(self, key_frames, attention_point):
        """extract the feature of the gesture
            :param key_frames: a list of key frames
            :param attention_point: a list of attention point
            :return: a list of feature
        """
        key_frames_feature = []

        for key_frame in key_frames:
            frame_temp = dict()
            for bodypart_name, values in key_frame.items():
                feature = []
                distance_to_camera = 1 - self.distance(values['wrist'], values['middle_base'])
                for landmark_name, value in values.items():
                    if landmark_name == attention_point:
                        feature = self.calculate_angle(value)
                        feature.append(distance_to_camera * 45.0)  # 45.0 generated by testing
                frame_temp[bodypart_name] = feature
            key_frames_feature.append(frame_temp)

        return self.translate_into_diff(key_frames_feature)

    def extract_key_frames(self, attention_point):
        """extract key frames from the frame sequence
        :param frame_sequence:
        :return: key_frames: a list of key frames
        """
        # make sure there are at least 16 key frames
        frame_count = len(self.gesture_sequence)
        # print(frame_count)
        samples = np.linspace(0, frame_count - 1, num=self.key_frames_number, dtype=int)
        key_frames = []
        for idx in samples:
            key_frames.append(self.gesture_sequence[idx])

        key_frames_feature = self.extract_feature(key_frames, attention_point)
        return key_frames_feature

    def create_customized_gesture_event(self, gesture_tag, frame_count, phrase, attention_point,
                                        mouse_and_key_event):
        """create customized gesture event into corresponding json file
        :param gesture_tag:  gesture tag
        :param frame_count:  frame count
        :param phrase: voice activation phrase
        :param attention_point: the attention point (finger tip or palm center)
        :param mouse_and_key_event: mouse or key event
        """
        event_dict = dict()
        event_dict["name"] = gesture_tag
        event_dict["type"] = "CustomizedGestureEvent"
        event_dict["args"] = {"gesture_name": gesture_tag, "gesture_type": self.gesture_type,
                              "bodypart_name": self.bodypart_name, "fps": self.fps,
                              "action_type": mouse_and_key_event, "frame_count": frame_count,
                              "camera_w_h_ratio": self.camera_w_h_ratio, "phrase": phrase,
                              "attention_point": attention_point,
                              "test_mode": 1}
        if len(self.body_part_name_list) == 1:
            if self.body_part_name_list[0] == 'body':
                event_dict["bodypart_names_to_type"] = {self.body_part_name_list[0]: "body"}
            else:
                event_dict["bodypart_names_to_type"] = {self.body_part_name_list[0]: "hand"}
        else:
            event_dict["bodypart_names_to_type"] = {"Left": "dom_hand", "Right": "off_hand"}
        event_dict["triggers"] = self.events_to_triggers_dict[mouse_and_key_event]
        return event_dict

    def create_speech_gesture_event(self, phrase, speech_event_name):
        """initialize the speech gesture event
        :param phrase to be spoken
        :return: speech gesture event
        """
        event_dict = dict()
        event_dict["name"] = speech_event_name
        event_dict["type"] = "SpeechEvent"
        event_dict["args"] = {"phrase": phrase, "action_type": "CustomizedGesture"}
        event_dict["bodypart_names_to_type"] = {"speech": "speech"}
        event_dict["triggers"] = {phrase: ["CustomizeGestureNotification", "notify_audio_flag"]}
        return event_dict

    def write_into_file(self, gesture_tag, key_frames_feature, static_gesture, frame_count, phrase, attention_point,
                        mouse_and_key_event):
        """write the customized gesture into json file
        :param gesture_tag: gesture tag
        :param key_frames_feature: key frames feature
        :param static_gesture: static gesture
        :param frame_count: frame count
        :param phrase: voice activation phrase
        :param attention_point: the attention point (finger tip or palm center)
        :param mouse_and_key_event: mouse or key event
        """
        self.gesture_editor.set_as_primitives(False)
        speech_event_name = "customize_speech_" + phrase
        output_str = ""
        gestures = self.gesture_editor.get_all_data()
        if len(static_gesture.keys()) == 1:
            for bodypart_name in static_gesture.keys():
                if gestures[self.gesture_type].get(gesture_tag, None) is not None:
                    self.gesture_editor.set_as_primitives(True)
                    raise Exception("RECORD ERROR: Gesture tag need to be changed!")
                save_json = json.dumps(static_gesture[bodypart_name])
                save_json = save_json.replace('false', 'False')
                save_json = save_json.replace('true', 'True')
                save_json = save_json[: -1] + ", \"name\": \"{}\"".format(gesture_tag) + save_json[-1]
                self.gesture_editor.add(self.gesture_type, save_json)
        else:
            for bodypart_name in static_gesture.keys():
                static_gesture_name = gesture_tag + '_' + bodypart_name
                if gestures[self.gesture_type].get(static_gesture_name, None) is not None:
                    self.gesture_editor.set_as_primitives(True)
                    raise Exception("RECORD ERROR: Gesture tag need to be changed!")
                save_json = json.dumps(static_gesture[bodypart_name])
                save_json = save_json.replace('false', 'False')
                save_json = save_json.replace('true', 'True')
                save_json = save_json[: -1] + ", \"name\": \"{}\"".format(static_gesture_name) + save_json[-1]
                self.gesture_editor.add(self.gesture_type, save_json)
        if gestures['speech'].get(phrase, None) is None:
            save_json = json.dumps({phrase: True})
            save_json = save_json.replace('true', 'True')
            save_json = save_json[: -1] + ", \"name\": \"{}\"".format(phrase) + save_json[-1]
            self.gesture_editor.add("speech", save_json)
        self.gesture_editor.save()
        self.gesture_editor.set_as_primitives(True)

        mode_controller = self.mode_editor.get_all_data()
        if mode_controller["modes"].get(self.test_mode_name, None) is None:
            self.mode_editor.add("modes", self.test_mode_name)

        save_json = json.dumps([gesture_tag, speech_event_name])
        self.mode_editor.update("modes/{}".format(self.test_mode_name), save_json)

        if mode_controller["modes"].get(self.mode_name, None) is None:
            self.mode_editor.add("modes", self.mode_name)
            save_json = json.dumps([gesture_tag, speech_event_name])
            self.mode_editor.update("modes/{}".format(self.mode_name), save_json)
        else:
            save_list = list(mode_controller["modes"][self.mode_name])
            save_list.append(gesture_tag)
            if speech_event_name not in mode_controller["modes"][self.mode_name]:
                save_list.append(speech_event_name)
            else:
                output_str = speech_event_name + " has existed"
            save_json = json.dumps(save_list)
            self.mode_editor.update("modes/{}".format(self.mode_name), save_json)
        self.mode_editor.save()

        events = self.event_editor.get_all_data()
        event_dict = self.create_customized_gesture_event(gesture_tag, frame_count, phrase, attention_point,
                                                          mouse_and_key_event)
        event_json = json.dumps(event_dict)
        self.event_editor.add("", event_json)
        events[gesture_tag] = event_dict
        if events.get(speech_event_name, None) is None:
            speech_event = self.create_speech_gesture_event(phrase, speech_event_name)
            speech_event_json = json.dumps(speech_event)
            self.event_editor.add("", speech_event_json)
        self.event_editor.save()

        if len(key_frames_feature) > 0:
            gesture_json_file_path = self.customize_gesture_dir + '\\' + gesture_tag + '.json'
            with open(gesture_json_file_path, 'w') as gesture_json_file:
                gesture_json_file.write(json.dumps(key_frames_feature))
        if output_str == "":
            return "Customize Gesture created"
        else:
            return output_str
