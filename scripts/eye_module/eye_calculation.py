"""
Author: Yadong (Adam) Liu
Author from MotionInput v2: Guanlin Li
"""
import numpy as np
import pyautogui

# GAZE & NOSE3D to Pixel ########################################################################################
from scripts import Config


class gaze2screen:
    def __init__(self, config: Config) -> None:

        self.screen_h: float = config.get_data("modules/eye/screen_h")
        self.screen_w: float = config.get_data("modules/eye/screen_w")
        self.camera_h: float = config.get_data("modules/eye/camera_h")
        #
        self.monitor_width, self.monitor_height = pyautogui.size()  # Get the size of the primary monitor
        # self.ave_gaze: int = int(args.a_g)
        # self.ave_nose: int = int(args.a_n)
        self.distance_bias: float = config.get_data("modules/eye/distance_bias")  # 20 25 30 35 (Don't know meaning)
        self.ys_calibrate: float = config.get_data("modules/eye/ys_calibrate")  # distance between eye and nose
        self.y_coefficient: float = config.get_data("modules/eye/y_coefficient")  # coefficient
        # for left and right conner y calibration
        self.y_x_coefficient: float = config.get_data("modules/eye/y_x_coefficient")
        self.x_l_coefficient: float = config.get_data("modules/eye/x_l_coefficient")  # left and right respect to user
        self.x_r_coefficient: float = config.get_data("modules/eye/x_r_coefficient")
        self.x_bias: float = config.get_data("modules/eye/x_bias")
        # for right conner x calibration
        self.x_r_y_coefficient: float = config.get_data("modules/eye/x_r_y_coefficient")

    def point2screen(self, nose_3d: np.ndarray, gaze_vector: np.ndarray) -> tuple[float, float]:
        """
            Takes the nose 3d and the gaze vector as input!
            nose 3d = x0, y0, z0
            gaze vector = a, b, c
            point on screen = x, y, z  (respect to camera coordinates)

            t = (z - z0) / c
            line equations:

            x = x0 + t*a
            y = y0 + t*b
            z = z0 + t*c    =>

            Returns point on the screen
            z == 0 as we assume its on the same plane with the sensor
        """
        t = (0 - nose_3d[2]) / gaze_vector[2]
        x = nose_3d[0] + t * gaze_vector[0]
        y = nose_3d[1] + t * gaze_vector[1]

        if x >= 0:  # left
            x = x * self.x_l_coefficient + self.x_bias
        else:  # right
            x = x * self.x_r_coefficient + self.x_bias + self.x_r_y_coefficient * x * y

        y = y * self.y_coefficient + self.y_x_coefficient * abs(x) * y  # for calibration
        return x, y

    def convert2screen(self, x: float, y: float) -> tuple[float, float]:
        """
        convert the x,y to screen coordinates xs,ys in cm
        then convert it to pixel unit
        :param x: respect to camera coordinates
        :param y:
        :return:
        """
        ys = (-y - self.camera_h) + self.ys_calibrate

        xs = (-x + (self.screen_w / 2))

        return xs, ys

    def convert2pixel(self, xs: float, ys: float) -> tuple[float, float]:
        """
        convert it to pixel unit
        :param xs:
        :param ys:
        :return:
        """

        yp = (ys / self.screen_w) * self.monitor_width  # convert it to pixel unit
        xp = (xs / self.screen_h) * self.monitor_height

        return xp, yp

    def gaze_process(self, gaze_vector: np.ndarray) -> np.ndarray:
        """
            convert the gaze vector coordinates to camera coordinates (3d pose)
            gaze vector = (x, y, z)
            :param gaze_vector:
            :return:
            """
        gaze_vector[2] = -gaze_vector[2]
        return gaze_vector

    def nose_process(self, nose_3d: np.ndarray) -> np.ndarray:
        """
        nose 3d = (z, x, y)
        calibrate the z (distance), and convert the sequence to x, y, z
        :param nose_3d
        :return:
        """
        nose_3d[0] -= self.distance_bias
        nose_3d = np.array([nose_3d[1], nose_3d[2], nose_3d[0]])
        return nose_3d

    def xy2screen_percent(self, x, y):
        """
        convert x,y pixel values into x,y
        :param x: x-pixel value, y: y-pixel value
        :return xper: x-percentage, yper: y-percentage
        """

        xper = x / self.monitor_width
        yper = y / self.monitor_height

        return xper, yper


    def get_coor(self, gaze_vector: np.ndarray, nose_3d: np.ndarray) -> tuple[float, float]:

        nose_pro = self.nose_process(nose_3d)
        gaze_pro = self.gaze_process(gaze_vector)
        #
        x1, y1 = self.point2screen(nose_pro, gaze_pro)
        xs, ys = self.convert2screen(x1, y1)
        xp, yp = self.convert2pixel(xs, ys)
        xper, yper = self.xy2screen_percent(xp, yp)

        return xper, yper
