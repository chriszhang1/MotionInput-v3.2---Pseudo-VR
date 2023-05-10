import numpy as np

from .landmark_frame import LandmarkFrame

class Plane:

    def __init__(self, origin, normal):

        self.origin = origin
        self.normal = normal / np.linalg.norm(normal)   

class Plane3Pt(Plane):

    def __init__(self, points):

        super().__init__(*self.get_plane_from_points(points))

    def get_plane_from_points(self, plane_points):

        a, b, c = plane_points

        AB = a - b
        AC = a - c

        normal = np.cross(AB, AC)
        #d = -a.dot(normal)

        origin = a

        return origin, normal

    def project_points(self, source_points):

        target_points = np.zeros_like(source_points)

        offset_distance = np.dot(source_points - self.origin, self.normal)

        for i in range(3):

            target_points[:, i] = source_points[:, i] - self.normal[i] * offset_distance

        return target_points



class HeadPlaneProjection:

    def __init__(self, landmark_frame):
        
        self.base_plane = Plane([0.5, 0.5, 0], [0, 0, 1])
        self.face_plane = self.get_facial_plane(landmark_frame)

    def get_facial_plane(self, landmark_frame):

        face_lower = landmark_frame.get_average(["mouth-top", "chin-centre", "left-cheek", "right-cheek"]) #"left-cheek", "right-cheek", "mouth-top", "nose-bridge"]
        face_left = landmark_frame.get_average(["left-eye-left", "temple-left"])
        face_right = landmark_frame.get_average(["right-eye-right", "temple-right"])

        plane_points = [face_lower, face_left, face_right]

        face_plane = Plane3Pt(plane_points)

        return face_plane

    def project_landmarks(self, landmark_frame):

        # Perform offset

        centred_landmarks = landmark_frame.landmarks - landmark_frame.get_landmark("nose-tip")

        mapped_frame = LandmarkFrame(centred_landmarks, landmark_frame.index_map)

        # Perform 2d projection

        mapped_frame.landmarks = self.face_plane.project_points(centred_landmarks)

        # Perform depth scaling

        face_width = mapped_frame.get_distance("left-cheek", "right-cheek", use_z=True)
        face_height = mapped_frame.get_distance("temple-centre", "chin-centre", use_z=True)

        scale_factor = 0.5 / (face_width + face_height)

        mapped_frame.landmarks *= scale_factor

        # Perform translation for display

        mapped_frame.landmarks += self.base_plane.origin 

        return mapped_frame
