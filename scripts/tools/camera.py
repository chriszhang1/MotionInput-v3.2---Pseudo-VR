'''
Author: Carmen Meinson
Contributors: Siam Islam
'''
# Logging
from scripts.tools.logger import get_logger
log = get_logger(__name__)

# Standard
import cv2
import numpy as np
import time
import threading
from typing import NoReturn

# Local
from scripts.tools.config import Config


def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class Camera:
    """
    New camera objects were previously created in the eye and head calibration classes, 
    so the Camera class has now been turned into a singleton to 
    prevent additional threads running unnecessarily
    """
    def __init__(self):
        self._active = True
        self._data = {
            "pass": True,
            "camera_nr": Config().get_data("general/camera/camera_nr"),
            "error_at_startup": False,
            "sources": set()
        }
        self._data["pass"] = True
        self._data["camera_nr"] = Config().get_data("general/camera/camera_nr")
        self._change_camera = False
        self._cap = cv2.VideoCapture(self._data["camera_nr"], cv2.CAP_DSHOW) 
        self.config = Config()
        self.editor = self.config.get_editor()
        self.width = self.config.get_data("general/camera/camera_w")
        self.height = self.config.get_data("general/camera/camera_h")
        self.black_image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.error_frame = self.create_error_frame()
        
        self.set_camera_properties()
        self.check_startup()
        self.set_camera_properties() # just in case
        
        self._frame = self._get_frame()
        self._new_frame = False
        self._thread = threading.Thread(target=self._update_frame, name="Thread Camera")
        self._thread.start()

    def create_error_frame(self):
        error_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        msg = "Error encountered when reading the camera."
        msg2 = "Please restart MotionInput."
        cv2.putText(error_frame, msg, (30, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(error_frame, msg2, (30, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 1, cv2.LINE_AA)
        return error_frame

    def check_startup(self) -> None:
        """
        Checks if the initial camera index can be successfuly read from. 
        Otherwise the check_camera function is called
        to check if any additional cameras are available.
        """
        success, _ = self._cap.read()
        if not success:
            print("Error: could not read camera at startup. Checking cameras...")
            self._data["error_at_startup"] = True
            self._check_camera()
        else:
            print("Successfully read camera at startup")
    
    def set_camera_properties(self) -> None:
        """
        Utility function to set camera properties.
        """
        self.fps = self._cap.get(cv2.CAP_PROP_FPS) 
        self._cap.set(3, self.width)
        self._cap.set(4, self.height)

    def read(self) -> np.ndarray:
        while not self._new_frame:
            time.sleep(0.01)
        self._new_frame = False
        return self._frame, self._data

    def _update_frame(self):
        # TODO: check code. Exception handling rn done poorly
        while self._active:
            self._frame = self._get_frame()
            self._new_frame = True
            #print("Update Called (Camera Thread)")
        log.info("Camera Thread Ended")


    def _get_frame(self):
        try:
            if not self._data["pass"]:
                time.sleep(0.01)
                return self.black_image
            if self._cap is not None or self._cap.isOpened():
                success, image = self._cap.read()
                if not success:
                    #print("SKIPPED FRAME")
                    image = self._frame
                    #print("Not success!")
                    #raise RuntimeError('reading frame unsuccessful')
            else:
                image = self._frame
            image = cv2.flip(image, 1)  # TODO: not sure at what point should the image be flipped
            return image
        except Exception as e:
            return self.error_frame
            # have only encountered this "Could not read the frame raise once after 
            # latest changes but adding this error
            # frame as a just in case measure"
            #raise RuntimeError('Could not read the frame', e)

    def _check_camera(self):
        """
        Checks through indexes 0-9 to find out which indexes correspond to a real camera. 
        Then calls _draw_camera_sources
        to display these indexes to the user.
        """
        if self._cap is None or not self._cap.isOpened():
            self._data["pass"] = False
            for i in range(9, -1, -1):  # test indexes 9 to 0
                self._test_index(i, self._data["sources"])
        else:
            self._data["pass"] = True
            return
            
        print("Detected sources: ", self._data["sources"])
        
        self.editor.update("general/camera/suggested_sources", list(self._data["sources"]))
        self._draw_camera_sources()
    
    def _draw_camera_sources(self):
        msg = "Suggested camera numbers: "
        if len(self._data["sources"]) > 0:
            for i, source in enumerate(self._data["sources"]):
                msg += str(source)
                if i < len(self._data["sources"]) - 1:
                    msg += ", "
            cv2.putText(self.black_image, msg, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1, cv2.LINE_AA)
            msg2 = "Please press full stop and then a number shown above"
            msg3 = "to switch between cameras"
            cv2.putText(self.black_image, msg2, (30, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1, cv2.LINE_AA)
            cv2.putText(self.black_image, msg3, (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1, cv2.LINE_AA)
        else:
            msg = "No cameras detected"
            cv2.putText(self.black_image, msg, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1, cv2.LINE_AA)


    def _test_index(self, index, sources):
        """
        Checks if a given camera index can be used to successfully create a capture object. 
        Adds valid indexes to a sources set.
        """
        camera = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if camera is None or not camera.isOpened():
            print("Unable to open: ", index)
        else:
            sources.add(index)

    def change_camera(self, index: int) -> bool:
        """
        Function to change between cameras. Takes in a camera index, 
        verifies that it is an index between 0 and 9
        and that it is different to the current camera index. 
        Allows free switching of the camera if there was no error at startup
        (since available sources are not checked for in this). 
        If there was an error, then available sources were calculated
        _test_index and allows switching between only those indexes. 
        Returns True if the camera was successfully changed or if the camera
        toggle button (full stop) was pressed.
        """
        if index != -1:
            if chr(index).isdigit():
                index = int(chr(index))
                print("INDEX: ", index)
                if (0<=index<=9) and index != self._data["camera_nr"]:
                    if (not self._data["error_at_startup"]) or (self._data["sources"] is not None and index in self._data["sources"]):
                        self.init_new_camera(index)
                        return True
            elif index == ord('.'):
                return True
        return False

    def init_new_camera(self, index: int):
        """
        Releases the current capture object and initialises a new one based on 
        the given camera index. This function is called when there
        is an error with the initial camera index.
        """
        self._cap.release()
        self._cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) 
        self.set_camera_properties()
        self._data["pass"] = True
        success, _ = self._cap.read()
        if not success:
            self._data["pass"] = False
        self._data["camera_nr"] = index
        self.editor.update("general/camera/camera_nr", index)


    def close(self) -> NoReturn: 
        self._active = False
        self._thread.join()
        print("Camera Thread: ", self._thread.is_alive())
        self.editor.save()
        self._cap.release()
