'''
Author: Anelia Gaydardzhieva
Comments: 
Speech command to control SPKID are triggered from here.
At the bottom of the file there are timed popup msg boxes
'''
from scripts.tools.logger import get_logger
log = get_logger(__name__)

# Standard
from threading import Thread, Event, Lock, RLock
import time

# Third party
import pyautogui
import pymsgbox

# Local
from scripts.tools.config import Config
from scripts.speech_module import KITA 
from scripts.tools.view import View


lock = Lock()

class SpeakerIdentification:
    """ Class to manage actions and view on SPKID speech commands """

    def __init__(self, view: View):
        self._is_running = False
        self.config = Config()
        self.kita = KITA()
        self._view = view
        self.editor = self.config.get_editor()
        self.intro_pop_event = Event()
        self.track_lock_event = Event()
        self.intro_popup_thread = Thread(target=self._intro_popup_thread_target, daemon = True, name="SPKID: Thread 1 (Introduction popup)")
        self.track_lock_thread = Thread(target=self._track_lock_thread_target, daemon = True, name="SPKID: Thread 2 (Speaker Lock track)")

###-------------------------------------- SPEECH EVENTS ------------------------------------------------------


    def start_speaker_identification(self) -> None:
        """ 
        START Speaker Identification Process

        phrase: 'speaker identify'
        """
        if self.is_running() or not self.kita.is_running():
            self.popup_already_on()
            return
        with lock: # Grab JSON data
            self.speaker_enabled = self.config.get_data("modules/speech/speaker/speaker_enabled") # bool
        if not self.speaker_enabled:
            self.popup_already_on()
            return
        with lock:
            self.kita.spk.spk_start_speaker()
            self.is_spk_locked = self.kita.spk.spk_locked # bool
            self.spk_locked_details = self.kita.spk.spk_locked_details # dict
            self.speaker_process_msg = self.config.get_data("modules/speech/speaker/speaker_process_msg") # str
            
        if self.is_spk_locked:
            self._view.update_display_element("speaker_identification_element", {
                                                    "speaker_identification": False, 
                                                    "speaker_locked": True, 
                                                    "spk_lock_id": self.spk_locked_details['speaker_saved_id'], 
                                                    "spk_lock_name": self.spk_locked_details['speaker_saved_name']})
        else:
            self._view.update_display_element("speaker_identification_element", {
                                                    "speaker_identification": True, 
                                                    "speaker_locked": False, 
                                                    "spk_lock_id": "", 
                                                    "spk_lock_name": ""})
            try: 
                self.intro_popup_thread.start() # Thread 1 - Introduction popup
                self.track_lock_thread.start() # Thread 2 - Waits to update view on Speaker Locked 
            except:
                log.info("SPKID main two threads already started")
            finally:
                self.intro_pop_event.set()
                self.track_lock_event.set()
        self.set_running(True)
        log.info("SPKID ON")



    def stop_speaker_identification(self) -> None:
        """ 
        STOP Speaker Identification Process
        Reset all Speaker Identification variables 

        phrase: 'stop speaker identify'
        """
        if not self.is_running():
            self.popup_already_off()
            return
        with lock:
            self.intro_pop_event.clear() 
            self.track_lock_event.clear() 
            self.set_running(False) 
            self.kita.spk.spk_stop_speaker()

            self._view.update_display_element("speaker_identification_element", {
                                                        "speaker_identification": False, 
                                                        "speaker_locked": False, 
                                                        "spk_lock_id": "", 
                                                        "spk_lock_name": ""})
            log.info("SPKID OFF")



    def remove_locked_speaker(self) -> None:
        """
        Remove the locked speaker from config.json

        phrase: 'remove locked speaker'
        """
        speaker_lock = self.config.get_data("modules/speech/speaker/speaker_locked")
        if not speaker_lock:
            return
        spk_details = {"speaker_saved_id": "",
                        "speaker_saved_name": "",
                        "speaker_saved_username": "",
                        "speaker_saved_vector": []
                        }
        try: 
            with lock:
                self.editor.update("modules/speech/speaker/speaker_locked", "false")
                self.editor.update("modules/speech/speaker/speaker_lock_saved", spk_details)
                self.editor.save()
            self._view.update_display_element("speaker_identification_element", {
                                                    "speaker_identification": False, 
                                                    "speaker_locked": False, 
                                                    "spk_lock_id": "", 
                                                    "spk_lock_name": ""})
        except Exception as e:
            log.error(f"Remove locked speaker Error: {e}")



    def enable_speaker_identify(self) -> None:
        """
        speaker_enabled : true in config.json

        phrase: 'enable speaker mode'
        """
        with lock: # Grab latest info
            self.speaker_enabled = self.config.get_data("modules/speech/speaker/speaker_enabled") # bool
        if self.speaker_enabled:
            return
        try:
            with lock:
                self.editor.update("modules/speech/speaker/speaker_enabled", "true")
                self.editor.save()
            pymsgbox.alert(text="SPKID has been ENABLED.", title='SPKID', button='auto closes in 5 seconds', timeout = 5000) # 5 sec
        except Exception as e:
            log.error(f"Enable SPKID Error: {e}")



    def disable_speaker_identify(self) -> None:
        """
        Remove the locked speaker from config.json

        phrase: 'disable speaker mode'
        """
        with lock: # Grab latest info
            self.speaker_enabled = self.config.get_data("modules/speech/speaker/speaker_enabled") # bool
        if not self.speaker_enabled:
            return
        try:
            with lock:
                self.editor.update("modules/speech/speaker/speaker_enabled", "false")
                self.editor.save()
            pymsgbox.alert(text="SPKID has been DISABLED.", title='SPKID', button='auto closes in 5 seconds', timeout = 5000) # 5 sec
            self.kita.spk.spk_stop_speaker()
        except Exception as e:
            log.error(f"Disable SPKID Error: {e}")

###-------------------------------------- Daemon (background) THREADS ------------------------------------------------------


    def _intro_popup_thread_target(self) -> None:
        """
        Speaker Identification Process - Introduction Manual popup
        """
        self.intro_pop_event.wait()
        log.info("SPKID: Started Thread _intro_popup_thread_target")
        while self.kita.is_running(): 
            with lock:
                self.kita.pause_KITA(True)
            pyautogui.alert(text = self.speaker_process_msg, 
                            title='[SPKID] Speaker Identification Process', 
                            button='OK')
            with lock:
                self.kita.pause_KITA(False)
            self.intro_pop_event.clear()
            self.intro_pop_event.wait()
            #Timed popup alternative
            #pymsgbox.alert(text=display_text, title='Speaker Identification Process', button='OK', timeout = 15000) # 15 sec



    def _track_lock_thread_target(self) -> None:
        """ 
        This method is called from the thread above
        to update the Display View for the camera window (cv2)
        """
        self.track_lock_event.wait()
        log.info("SPKID: Started Thread _track_lock_thread_target")
        while self.kita.is_running():
            # To minimise resource use, only checks if a speaker has been locked maximum once every 2 sec
            time.sleep(2)
            with lock:
                spk_locked, spk_locked_id, spk_current_name = self.kita.spk.spk_get_lock_display_info()
            if spk_locked:
                self._view.update_display_element("speaker_identification_element", {
                                                        "speaker_identification": False, 
                                                        "speaker_locked": True, 
                                                        "spk_lock_id": spk_locked_id, 
                                                        "spk_lock_name": spk_current_name})
                self.track_lock_event.clear()
                self.track_lock_event.wait()



###------------------------------------ Helpers -------------------------------------------

    def set_running(self, value : bool) -> None:
        """
        Sets whether the SPKID is ON or OFF
        """
        self._is_running = value


    def is_running(self) -> bool:
        """
        Returns True if SpkI is ON
        """
        return self._is_running

###-------------------------------------- POPUPS ----------------------------------------

    @staticmethod
    def popup_confirm_remove_locked_speaker() -> bool:
        """
        Confirm Speaker Lock Reset
        """
        res = False
        display_text = """
Please confirm you would like to delete the existing speaker lock.
        """
        answer = pyautogui.confirm(text=display_text,
                        title='Speaker Lock Delete Confirmation Request', 
                        buttons=['Delete', 'Cancel'])
        if answer == "Delete":
            res = True
        return res



    @staticmethod
    def popup_complete_remove_locked_speaker() -> None:
        """
        Speaker Lock Reset Complete
        """
        display_text = """
The speaker lock has been removed successfully!
        """
        pymsgbox.alert(text=display_text, title='Success', button='auto closes in 7 seconds', timeout = 7000) # 7 sec



    @staticmethod
    def popup_already_on() -> None:
        """
        Simply popup
        """
        display_text = """
Speaker Identification (SPKID) could not be started.\n\n
Common reasons:
  - SPKID is already on .
  - SPKID is currently disabled\n\n
You could try:\n
  - Enable SPKID by saying 'enable speaker identify'
  - Reset SPKID by saying 'stop speaker identify' and then 'speaker identify'\n
  - If there is a saved speaker lock you wish to remove, you could do so by saying 'remove locked speaker'\n
Alternatively, please restart MotionInput.
        """
        pymsgbox.alert(text=display_text, title='SPKID', button='auto closes in 15 seconds', timeout = 15000) # 15 sec



    @staticmethod
    def popup_already_off() -> None:
        """
        Simply popup
        """
        display_text = """
Speaker Identification mode is currently not turned on.\n\n
To use this speech command, please first turn Speaker Identification ON 
by saying 'speaker identify' \n\n
To stop the mode later just say 'stop speaker identify' at any time.
        """
        pymsgbox.alert(text=display_text, title='SPKID', button='auto closes in 7 seconds', timeout = 7000) # 7 sec


