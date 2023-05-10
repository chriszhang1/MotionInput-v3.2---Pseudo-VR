import numpy as np

class LandmarkFrame:

    def __init__(self, landmarks, index_map):

        self.landmarks = landmarks
        self.index_map = index_map

    def get_landmark(self, label, use_z=True):

        landmark = self.landmarks[self.index_map[label]]

        return landmark if use_z else landmark[:2]

    def get_landmarks(self, labels, use_z=True):

        landmarks = []
        for label in labels:
            landmarks.append(self.get_landmark(label, use_z))

        return landmarks

    def get_vector(self, start, end, use_z=True):

        start_lm = self.get_landmark(start, use_z)
        end_lm = self.get_landmark(end, use_z)

        return end_lm - start_lm

    def get_distance(self, start, end, use_z=True):

        return self.get_distance_sq(start, end, use_z) ** 0.5

    def get_distance_sq(self, start, end, use_z=True):

        delta = self.get_vector(start, end, use_z)

        return delta[0]**2 + delta[1]**2 + (delta[2]**2 if use_z else 0)

    def get_average(self, labels, use_z=True):

        average = np.zeros(3 if use_z else 2)
        for label in labels:
            average += self.get_landmark(label, use_z)

        return average / len(labels)

# Unfortunately, no convenient definitions for the mediapipe face mesh vertices

FACIAL_LANDMARK_MAP = {
    "temple-centre": 10, 
    "temple-left": 103, "temple-right": 332,
    "nose-tip": 4,
    "nose-bridge": 6,
    "mouth-top": 164,
    "left-eyebrow-lower": 52, 
    "right-eyebrow-lower": 282,
    "left-eyebrow-top-left": 63, "left-eyebrow-top-right": 66,
    "left-eye-top-left": 160, "left-eye-top-right": 158,
    "left-eye-left": 33, "left-eye-right": 173,
    "left-eye-bottom-left": 144, "left-eye-bottom-right": 153,
    "left-eye-bottom": 145,
    "right-eyebrow-top-left": 296, "right-eyebrow-top-right": 293,
    "right-eye-top-left": 385, "right-eye-top-right": 387,
    "right-eye-left": 398, "right-eye-right": 263,
    "right-eye-bottom-left": 380, "right-eye-bottom-right": 373,
    "right-eye-bottom": 374,
    "lip-top": 13, "lip-bottom": 14, 
    "lip-left": 78, "lip-right": 308,
    "lip-top-left": 81, "lip-bottom-left": 178, 
    "lip-top-right": 311, "lip-bottom-right": 402,
    "left-cheek": 132, 
    "left-cheek-inner": 187,
    "right-cheek": 361, 
    "right-cheek-inner": 411,
    "left-undereye": 101,
    "right-undereye": 330,
    "chin-centre": 152
}

FACIAL_LANDMARK_COUNT=468



def get_face_mesh_frame(raw_landmarks):

    # Only extract the landmarks that are explicitly labelled (required for calculations) to save time.

    landmarks = np.zeros((len(FACIAL_LANDMARK_MAP), 3), dtype=np.float32)
    index_map = {}

    index = 0
    for label in FACIAL_LANDMARK_MAP:

        lm = raw_landmarks.landmark[FACIAL_LANDMARK_MAP[label]]

        landmarks[index][0] = lm.x
        landmarks[index][1] = lm.y
        landmarks[index][2] = lm.z

        index_map[label] = index
        index += 1

    landmark_frame = LandmarkFrame(landmarks, index_map)

    return landmark_frame


