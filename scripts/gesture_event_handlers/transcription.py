'''
Author: 
Contributor: Anelia Gaydardzhieva
Comments: 
Transcription class
Sends Keyboard class to KITA when started, to begin transcription typewrite().
View class (view.py and display_element.py) is used to 
display a label on the camera (cv2) window when Transcription is ON
and also regulates Correction mode display elements when necessary. 
'''
from scripts.tools.logger import get_logger
log = get_logger(__name__)

# Standard
import os
from threading import RLock

# Third party
import pyautogui
import pymsgbox

# Local
from scripts.gesture_event_handlers.correction_mode import CorrectionMode
from scripts.gesture_event_handlers.keyboard import Keyboard
from scripts.speech_module import KITA
from scripts.tools.config import Config
from scripts.tools.view import View

# Global 
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "data"))

lock = RLock() 
config = Config()



class Transcriber:

    def __init__(self, view=View):
        self.kita = KITA()
        self.config = Config()
        self.editor = self.config.get_editor()
        with lock:
            self._enabled = self.config.get_data("modules/speech/transcription_enabled")
            self._lang_change_enabled = self.config.get_data("modules/speech/lang_change_enabled")
        if self._enabled:
            self._view = view
            self.corr = CorrectionMode()


    def start_transcribe(self) -> None:
        """ 
        START Transcription
        """
        if not self._enabled or self.is_running():
            return
        if not self.kita.is_running():
            self.kita.start()
        with lock:
            self.kita.set_transcription(Keyboard())
            self.corr.set_transcription(True)
        # View
        self._view.update_display_element("transcribe_element", {"transcribing": True})
        if self.corr.is_running():
            self._view.update_display_element("correction_element", {"correction_mode": True, "transcriber_required": False})
        else:
            self._view.update_display_element("correction_element", {"correction_mode": False, "transcriber_required": False})
        log.info("Transcription ON")


    def stop_transcribe(self) -> None:
        """ 
        STOP Transcription 
        """
        if self.is_running():
            with lock:
                self.kita.set_transcription(None)
                self.corr.set_transcription(False)
            # View
            self._view.update_display_element("transcribe_element", {"transcribing": False})
            self._view.update_display_element("correction_element", {"correction_mode": False, "transcriber_required": False})
            log.info("Transcription OFF")


    def change_speech_language(self) -> None:
        """
        Changes the vosk language model used
        """
        if not self._lang_change_enabled:
            return
        valid = False
        display_text = """
Please provide in a single word the language you wish to change transcription to.\n
The available languages for transcription are: English, Indian English, Italian, Spanish, 
French, German, Ukrainian, Russian and Turkish.\n
Note1: Speech Commands are currently only available in English and Indian English,
while transcription is available in all the languages mentioned.\n
Note2: To enable transcription in your desired language, please make sure that you have
the language keyboard available and turned on on your device.\n
Note3: For the change to take place, please restart MI.
Note4: This feature is experimental and still in its early stages.
"""
        while not valid:
            answer = pyautogui.prompt(display_text)
            if answer != "" and " " not in answer:
                valid = True
        answer = answer.lower().strip()
        TEST_PATH = os.path.join(DATA_PATH, 'ml_models', 'speech', answer)
        if os.path.exists(TEST_PATH):
            with lock:
                self.editor.update("modules/speech/language", answer)
                self.editor.save()
            pymsgbox.alert(text="Your selected language has now been set up.\n Please restart MotionInput for the change to take place.", 
                           title='Language Change Success', button='auto closes in 7 seconds', 
                           timeout = 5000) # 5 sec
        else: 
            pymsgbox.alert(text="Unfortunately, the name provided was now a valid language.\nPlease try again later.", 
                           title='Language Change Error', button='auto closes in 7 seconds', 
                           timeout = 5000) # 5 sec
        


    def is_running(self) -> bool:
        """
        Returns True if Transcription is ON
        CorrectionMode is being used here because of the need for
        both classes to communicate information to one another and to KITA.
        Having a separate variable for Transcription._running only
        is not needed at this stage (v3.1). 
        """
        with lock:
            return self.corr.is_transcription_running()


