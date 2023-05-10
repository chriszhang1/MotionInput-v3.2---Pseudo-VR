'''
Author: code originally from Motioninput V2, refined by Jason Ho
'''
# This code is based on this tutorial with some modifications:
# https://colab.research.google.com/drive/19txHpN8exWhstO6WVkfmYYVC6uug_oVR

from typing import Dict


class EMASmoothing(object):
    """Smoothes pose classification."""
    def __init__(self) -> None:
        self.window_size = 10
        self.alpha = 0.3
        self.window_data = []

    def __call__(self, data: Dict[str, int]) -> Dict[str, float]:
        """Smoothes given pose classification using Exponential Moving Average for every pose
        class observed in the given time window. Missed pose classes are replaced
        with 0. (Docstring from tutorial)
        
        :param data: Data of the pose class and its confidence score
        :type data: Dict[str, int]
        :return: Smoothed pose classification data
        :rtype: Dict[str, float]
        """
        self.window_data = [data] + self.window_data
        self.window_data = self.window_data[:self.window_size]
        keys = set([key for data in self.window_data for key, _ in data.items()])

        smoothed_data = {}
        for key in keys:
            factor = 1.0
            top_sum = 0.0
            bottom_sum = 0.0
            for data in self.window_data:
                if key in data:
                    value = data[key]
                else:
                    value = 0.0
                top_sum += factor * value
                bottom_sum += factor
                factor *= (1.0 - self.alpha)
            smoothed_data[key] = top_sum / bottom_sum

        return smoothed_data