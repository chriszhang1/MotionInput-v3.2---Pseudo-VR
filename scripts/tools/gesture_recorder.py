import json

from scripts.tools.recording_database import RecordingDatabase


class GestureRecorder:

    def __init__(self):
        self.hand_bodypart_name = ["Left", "Right"]
        self.exercise_bodypart_name = ["body"]

        self.activate_gestures = []
        self.gesture_sequences = {}

        self.DB = RecordingDatabase()
        self.frame_index = self.DB.get_last_line_id() + 1
        self.recorded_frames = {}
        self.key_frames = set()  # store all the key frame index
        self.module_name = ""

    def record_gesture(self, frame_data, model):
        if len(model.get_module_names()) == 0:
            return
        module_names = list(model.get_module_names())
        if "hand" in module_names:
            self.module_name = "hand"
        elif "body" in module_names:
            self.module_name = "body"
        frame_landmarks = {}
        body_part_name_list = []

        if self.module_name == 'hand':
            body_part_name_list = self.hand_bodypart_name
        elif self.module_name == 'body':
            body_part_name_list = self.exercise_bodypart_name

        # record landmarks for all the body_part, e.g. hand: Left, Right
        for bodypart_name in body_part_name_list:
            detected_body_part = frame_data.get_data(bodypart_name)
            if detected_body_part is not None:
                frame_landmarks[bodypart_name] = dict()
                for k in detected_body_part.keys():
                    frame_landmarks[bodypart_name][k] = \
                        [detected_body_part[k][0], detected_body_part[k][1], detected_body_part[k][2]]

        activate_events = model.get_activate_events()
        if len(activate_events) > 0 and len(frame_landmarks) > 0:
            self.recorded_frames[self.frame_index] = frame_landmarks

        current_gesture_names = []
        for event in activate_events:
            for gesture_type in event.get_all_used_gestures():
                for body_type in event.get_bodypart_types():
                    gestures_dict = event.get_all_gestures()
                    if gesture_type == 'peace' or body_type == 'speech':
                        continue
                    if gestures_dict[body_type][gesture_type] is not None and gesture_type not in current_gesture_names:
                        current_gesture_names.append(gesture_type)

        deactivate_gestures = list(set(self.activate_gestures) - set(current_gesture_names))
        for gesture in current_gesture_names:
            if gesture not in self.activate_gestures:
                self.activate_gestures.append(gesture)
                self.key_frames.add(self.frame_index)
                if self.gesture_sequences.get(gesture, None) is not None:
                    self.gesture_sequences[gesture].append([self.frame_index])
                else:
                    self.gesture_sequences[gesture] = [[self.frame_index]]

        if len(frame_landmarks) == 0:
            for gesture in self.activate_gestures:
                self.key_frames.add(self.frame_index - 1)
                self.gesture_sequences[gesture][-1].append(self.frame_index - 1)
                self.activate_gestures.remove(gesture)
        elif len(deactivate_gestures) > 0:
            for gesture in deactivate_gestures:
                self.key_frames.add(self.frame_index - 1)
                self.gesture_sequences[gesture][-1].append(self.frame_index - 1)
                self.activate_gestures.remove(gesture)

        self.frame_index += 1

    def write_data_into_DB(self):
        if len(self.activate_gestures) > 0:
            self.key_frames.add(self.frame_index - 1)
            for gesture in self.activate_gestures:
                self.gesture_sequences[gesture][-1].append(self.frame_index - 1)

        if len(self.recorded_frames.keys()) == 0:
            return
        # using reduction_algorithm
        frame_data, compress_data = self.recorded_gesture_reduction()
        # print(len(self.recorded_frames.keys()))
        # print(self.key_frames)
        # print(frame_data.keys())
        # print(compress_data)

        for frame_id, data in frame_data.items():
            compressed = compress_data[frame_id]
            gesture_json_str = json.dumps(data)
            # print(gesture_json_str)
            self.DB.record(frame_id, gesture_json_str, compressed)

        for gesture, gesture_seq in self.gesture_sequences.items():
            for start_id, end_id in gesture_seq:
                self.DB.record_gesture(gesture, start_id, end_id)
        self.DB.close_db()

    def recorded_gesture_reduction(self):
        landmark_num = 0
        if self.module_name == 'hand':
            landmark_num = 18
        elif self.module_name == 'body':
            landmark_num = 5

        x_threshold = 40
        y_threshold = 40
        z_threshold = 30

        x_width = 640
        y_height = 480
        z_depth = 1000

        reduced_frame = {}
        reduced_compress = {}

        trivial_count = 0  # count the trivial frame need to be compressed
        key_frame_index = list(self.recorded_frames.keys())[0]
        key_frame = self.recorded_frames[key_frame_index]  # first frame as key frame
        reduced_frame[key_frame_index] = key_frame

        for i in range(1, len(self.recorded_frames.keys())):  # start from 1
            this_frame_index = list(self.recorded_frames.keys())[i]
            this_frame = self.recorded_frames[this_frame_index]

            # comment out code is used in bodypart number change senario
            '''
            if len(Key_frame.keys()) != len(self.recorded_gesture_sequence["facing_camera"][0][i].keys()):
                print(Key_frame)
                Key_frame = self.recorded_gesture_sequence["facing_camera"][0][i]
                trivial_count = 0
            '''

            if this_frame_index in self.key_frames or len(key_frame.keys()) != len(this_frame.keys()):
                if len(this_frame.keys()) != 0:
                    reduced_compress[key_frame_index] = trivial_count
                    trivial_count = 0
                    key_frame_index = this_frame_index
                    key_frame = this_frame
                    reduced_frame[this_frame_index] = this_frame
                    reduced_compress[this_frame_index] = 0

            else:
                # len(Key_frame.keys())*23 count the number of compared landmark
                landmark_count = 0

                exit_flag = False
                for bodypart in key_frame.keys():
                    if this_frame.get(bodypart, None) is not None:
                        for landmark in key_frame[bodypart].keys():  # calculate delta
                            x = abs(key_frame[bodypart][landmark][0] - this_frame[bodypart][landmark][0])
                            y = abs(key_frame[bodypart][landmark][1] - this_frame[bodypart][landmark][1])
                            z = abs(key_frame[bodypart][landmark][2] - this_frame[bodypart][landmark][2])
                            if x * x_width < x_threshold and y * y_height < y_threshold and z * z_depth < z_threshold:
                                landmark_count = landmark_count + 1
                            else:
                                exit_flag = True
                                break
                    else:
                        continue
                    if exit_flag:
                        exit_flag = False
                        break
                # check whether all landmark delta < threshold, 18 need to be changed in different module
                if landmark_count == len(key_frame.keys()) * landmark_num:
                    trivial_count = trivial_count + 1
                else:
                    reduced_compress[key_frame_index] = trivial_count
                    trivial_count = 0
                    key_frame_index = this_frame_index
                    key_frame = this_frame
                    reduced_frame[this_frame_index] = this_frame
                    reduced_compress[this_frame_index] = 0

        return reduced_frame, reduced_compress
