'''
Author: Anelia Gaydardzhieva
Comments: 
Simple static methods class
'''
from scripts.tools.logger import get_logger
import os
import inspect

def caller_file_name():
    frame = inspect.stack()[1]
    filename = frame[0].f_code.co_filename
    return filename

log = get_logger(caller_file_name())

class Utils:
    """ Static useful methods class """

    def __init__(self):
        self.caller_name = caller_file_name()


    @staticmethod
    def check_paths(*paths):
        """
        Adapted for multipath checks
        """
        for path in paths:
            if not os.path.exists(path):
                log.error(f"[Check_path] Path {path} was not found")
                raise FileNotFoundError(f"[Check_path] Path {path} was not found")