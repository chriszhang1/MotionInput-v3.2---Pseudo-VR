'''
Author: Anelia Gaydardzhieva
Comments:
Helper Class to setup 
the Speaker Identification Process.
Directly used in KITA.
'''
# Logging
import string
from scripts.tools.logger import get_logger
log = get_logger(__name__)

# Standard 
import numpy as np

# Third party
import pyautogui
from threading import RLock
from typing import Any, Dict, List
#from pydantic import BaseModel

# Local
from scripts.tools import Config
from scripts.tools.json_editors.speakers_editor import SPKEditor

# Global Lock
lock = RLock()

class SPKProcess:
    """ Speaker Identification """

    def __init__(self):
        self.editor = SPKEditor()
        self.config = Config()
        self.config_editor = self.config.get_editor()
        # Management variables (default values)
        self.spk_on = False # on/off
        self.spk_verified = True # authorised speech commands and transcription
        self.spk_threshold = 0.6 # acceptance threshold - current vector and db vectors
        self.spk_threshold_word_count = 3
        self.spk_setup_complete = False # if true, no more popup questions to user
        self.spk_current = {}
        self.spk_current_id = ""
        self.spk_current_name = ""
        self.spk_current_username = ""
        self.spk_current_vector = []
        self.spk_enabled = False
        self.spk_locked = False
        self.spk_locked_details = {}
        self.spk_locked_id = "" 
        self.spk_locked_name = ""
        self.spk_locked_username = ""
        self.spk_locked_vector = []



    def speaker_identification_action(self, json_data : Dict[str, Any]) -> None:
        """
        Speaker Identification Process
        Starting point
        """
        # Resetting variables
        self.spk_current = {}
        self.spk_current_id = ""
        self.spk_current_name = ""
        self.spk_current_username = ""
        # Unauthorised initially
        self.spk_set_verification(False) 
        # Setup phrase
        self.spk_current_vector = json_data['spk'] 
        temp_current_phrase = json_data["text"]
        # Set up acceptable threshold depending on number of words in phrase
        self.spk_adjust_threshold(temp_current_phrase) # higher acceptance level for spk vector generated over 2, 3 spoken words
        # Get Speakers Data
        is_spk_known = self.spk_match_with_db()
        # If Speaker is Known - setup current speaker
        if is_spk_known:
            for spk_id, spk in self.spk_current.items():
                self.spk_current_id = spk_id
                self.spk_current_name = spk["name"]
                self.spk_current_username = spk["username"]
                self.spk_current_vector = spk["vector"]
        # If SPK is LOCKED
        if self.spk_locked:
            if not is_spk_known:
                return # Not Authorised
            if self.spk_current_id == self.spk_locked_id: # If matched with the locked
                self.spk_set_verification(True) # Authorised
            return # Else stays Not Authorised
        # If SPK is NOT LOCKED
        self.spk_not_locked_process(is_spk_known)



    def spk_not_locked_process(self, is_spk_known : bool) -> None:
        """
        If NO Lock exists for SPKID
        """
        self.spk_set_verification(True) # Authorised
        # If Setup completed
        if self.spk_setup_complete:
            return
        # If Speaker NOT recognised
        if not is_spk_known:
            self.spk_unrecognised_process()
        # Ask to lock if user set up
        if self.spk_current_id != "":
            self.spk_ask_lock()



    def spk_set_verification(self, verified : bool) -> None:
        """
        Sets whether the speaker is 
        verified or not
        """
        self.spk_verified = verified



    def is_spk_verified(self) -> bool:
        """
        Returns whether the speaker is
        verified or not
        """
        return self.spk_verified



    def is_spk_enabled(self) -> bool:
        """
        Returns if SPKID enabled in config.json
        """
        with lock:
            self.spk_enabled = self.config.get_data("modules/speech/speaker/speaker_enabled") # bool
        return self.spk_enabled



    def is_spk_on(self) -> bool:
        """
        Returns whether SPKID is currently running
        """
        return self.spk_on



    def spk_start_speaker(self) -> None:
        """
        Start SPKID Process
        Called from SpeakerIdentification via speech command
        (speaker_identification.py)
        """
        self.spk_on = True
        self.spk_verified = True 
        self.spk_threshold = 0.6 
        self.spk_threshold_word_count = 3
        self.spk_setup_complete = False
        self.spk_current = {}
        self.spk_current_id = ""
        self.spk_current_name = ""
        self.spk_current_username = ""
        self.spk_current_vector = []
        self.spk_enabled = False
        self.spk_locked = False
        self.spk_locked_details = {}
        self.spk_locked_id = "" 
        self.spk_locked_name = ""
        self.spk_locked_username = ""
        with lock:
            self.spk_enabled = self.config.get_data("modules/speech/speaker/speaker_enabled") # bool
            self.spk_locked = self.config.get_data("modules/speech/speaker/speaker_locked") # bool
            self.spk_locked_details = self.config.get_data("modules/speech/speaker/speaker_lock_saved") # dict



    def spk_stop_speaker(self) -> None:
        """
        Stop SPKID
        Called from SpeakerIdentification via speech command
        (speaker_identification.py)
        Resets all variables. Needed for dynamic adjustments
        """
        self.spk_on = False 
        self.spk_verified = True 
        self.spk_threshold = 0.6 
        self.spk_threshold_word_count = 2
        self.spk_setup_complete = False 
        self.spk_current = {}
        self.spk_current_id = ""
        self.spk_current_name = ""
        self.spk_current_username = ""
        self.spk_current_vector = []
        self.spk_enabled = False
        self.spk_locked = False
        self.spk_locked_details = {}
        self.spk_locked_id = "" 
        self.spk_locked_name = ""
        self.spk_locked_username = ""



    def spk_unrecognised_process(self) -> None:
        """
        The setup process steps to go through when 
        the current speaker's voice has not been identified
        """
        try:
            log.info("Unknown speaker")
            self.spk_setup_complete = False
            # ADD?
            answer = self.spk_popup_add_new_speaker()
            # No (add)
            if not answer:
                self.spk_ask_try_again()
            # Yes (add)
            else:
                self.spk_current_name = self.spk_popup_ask_name()
                self.spk_current_username = self.spk_popup_ask_username()
                self.spk_add_new_speaker()
        except Exception as e:
            log.info(f"Unknown speaker error: {e}")
            self.spk_error(e)



    def spk_save_lock_json(self) -> None:
        """
        Called when the user has selected 'Yes' on 
        saving their lock for the future
        """
        self.spk_locked_details = {}
        spk_data = self.get_speakers_data()
        for spk_id, spk in spk_data.items():
            if spk_id == self.spk_locked_id:
                self.spk_locked_details[spk_id] = spk
                self.spk_locked_name = spk["name"]
                self.spk_locked_username = spk["username"]
                self.spk_locked_vector = spk["vector"]
                spk_lock_save = {
                    "speaker_saved_id": self.spk_locked_id,
			        "speaker_saved_name": self.spk_locked_name,
			        "speaker_saved_username": self.spk_locked_username,
			        "speaker_saved_vector": self.spk_locked_vector
                    }
                with lock:
                    self.config_editor.update("modules/speech/speaker/speaker_locked", "true")
                    self.config_editor.update("modules/speech/speaker/speaker_lock_saved", spk_lock_save)
                    self.config_editor.save()



    def spk_match_with_db(self) -> bool:
        """
        Checks whether a particular speaker is in DB or not
        and returns a bool variable and information 
        about the speaker they were matched with
        """
        is_spk_known = False
        # Reset
        self.spk_current = {}
        self.spk_current_id = ""
        self.spk_current_name = ""
        self.spk_current_username = ""
        # Get latest DB data (otherwise newly added users are not recognised)
        spk_data = self.get_speakers_data()
        # DB match?
        for spk_id, spk in spk_data.items():
            spk_vector = spk["vector"]
            average_distance = self.spk_cosine_distance(spk_vector)
            # Yes (DB match)
            if average_distance < self.spk_threshold:
                is_spk_known = True
                spk_matched = {
                        spk_id : {
                        "name": spk["name"],
                        "username": spk["username"],
                        "vector": spk_vector
                            }
                        }
                self.spk_current.update(spk_matched)
                self.spk_current_id = spk_id
                self.spk_current_name = spk["name"]
                self.spk_current_username = spk["username"]
                self.spk_current_vector = spk_vector
        return is_spk_known



    def spk_add_new_speaker(self) -> None:
        """
        Add and Save a new speaker to the JSON file
        """
        spk_data = self.get_speakers_data() # grab data
        new_id = str(len(spk_data)) # calc new ID
        self.spk_current_id = new_id # set current speaker's ID
        new_spk = { 
            self.spk_current_id : {
            "name": self.spk_current_name,
            "username": self.spk_current_username,
            "vector": self.spk_current_vector
            }}
        spk_data.update(new_spk)
        self.editor.update_json(spk_data) # update JSON



    def spk_ask_lock(self) -> None:
        """
        Ask the speaker if they want to LOCK the app with their voice
        and if they would like to save the lock for the future. 
        Implements user locking preferences. 
        """
        self.spk_setup_complete = False
        # Ask user to LOCK?
        answer_lock = self.spk_popup_lock(self.spk_current_name)
        ### Answer NO LOCK
        if not answer_lock:
            # Ask try again?
            self.spk_ask_try_again()
        ### Answer YES LOCK
        else:
            # Set Local lock
            self.spk_locked_id = self.spk_current_id
            self.spk_locked_name = self.spk_current_name
            self.spk_locked = True
            # Ask Save Lock?
            answer_lock_save = self.spk_popup_lock_save()
            # Answer Yes (save lock)
            if answer_lock_save:
                self.spk_save_lock_json()
            # Answer No (save lock)
            self.spk_setup_complete = True
            # Finally popup
            self.spk_popup_lock_complete()



    def spk_ask_try_again(self) -> None:
        """
        Ask if the speaker wants to enable another try.
        Applies for a recognised speaker who did not want to Lock
        and for a new speaker who did not want to be added to DB.
        """
        self.spk_setup_complete = self.spk_popup_another_try()
        # If the speaker wants to try again: Enable second run (=> setup NOT completed yet)
        if not self.spk_setup_complete:
            self.spk_popup_reminder_second_try()



    def get_speakers_data(self) -> Dict[str, Any]:
        """
        Get Speakers data from JSON file
        """
        return self.editor.get_all_data()



    def spk_get_lock_display_info(self) -> tuple:
        """
        Called from SpeakerIdentification.py
        to update cv2 View
        """
        return self.spk_locked, self.spk_locked_id, self.spk_current_name



    def spk_cosine_distance(self, db_vector : List[float]) -> float:
        """
        Calculates and returns the average distance between 
        a vector from the DB and the newly generated vector.
        """
        #nx = np.array(eval(x))
        nx = np.array(self.spk_current_vector)
        ny = np.array(db_vector)
        average_distance = 1 - np.dot(nx, ny) / np.linalg.norm(nx) / np.linalg.norm(ny)
        return average_distance



    def spk_adjust_threshold(self, temp_current_phrase : str) -> None:
        """
        Set Speaker Acceptance Threshold based on the number of words in the current phrase.
        This is conditioned because the Speaker voice print generated on 1 or 2 words
        has low accurancy and might prevent any speaker from recognition.
        """
        spaces = temp_current_phrase.count(" ") # Count words: if spaces = 0 => 1 word; if 1 => 2 words, etc.
        if spaces < self.spk_threshold_word_count: # => 4 words threshold (on 1, 2, 3 words lower acceptance criteria)
            self.spk_threshold = 0.8



####################################### POPUPS ##########################################
# TODO: There are only 3 types of popups and all of the methods below 
# could be exdended from a single base class without the need to manually code each. 

    @staticmethod
    def spk_popup_ask_name() -> str:
        """
        Gets user input for NAME
        Currently simple validation in place.
        Field cannot be empty, include punctuation and has to contain a space.
        Not concerned with duplicates since spk 
        IDs are always unique (and people can have the same names)
        """
        valid = False
        display_text = "Please provide your first and last names separated by a space: "
        display_text = """
Please provide your first and last names separated by a space.\n
Note: This field cannot be left empty and requires at least two of your names
        """
        while not valid:
            answer = pyautogui.prompt(display_text)
            if answer != "" and " " in answer: # answer cannot be empty, requires at least one space (=> min two names)
                answer = answer.translate(str.maketrans('', '', string.punctuation)) # remove any punctuation
                valid = True
        return answer



    @staticmethod
    def spk_popup_ask_username() -> str:
        """
        Gets user input for USERNAME
        Currently simple validation for the input to not be empty
        and removes punctuation for user input. 
        Not too concerned with duplicates at this stage since spk 
        IDs are always unique
        """
        valid = False
        display_text = """
Please provide your computer username or any username.\n
This could later be used to synchronise the Speaker Identification 
feature with the custom Hotkeys capability.\n\n
Note: This field cannot be left empty
        """
        while not valid:
            answer = pyautogui.prompt(display_text)
            if answer != "": # answer cannot be empty
                answer = answer.translate(str.maketrans('', '', string.punctuation)) # remove any punctuation
                valid = True
        return answer



    @staticmethod
    def spk_popup_add_new_speaker() -> bool:
        answer = False
        display_text = "Would you like to ADD yourself as a new speaker?"
        spk_input = pyautogui.confirm(text=display_text, 
                                    title='New Speaker Recognised', 
                                    buttons=['Yes', 'No'])
        if spk_input == "Yes":
            answer = True
        return answer



    @staticmethod
    def spk_popup_another_try() -> bool:
        spk_setup_complete = True
        display_text = "Would you like to try the Speaker Identification Process one more time?"
        spk_input = pyautogui.confirm(text=display_text,
                                            title='Another attempt?', 
                                            buttons=['Yes', 'No'])
        if spk_input == "Yes":
            spk_setup_complete = False
        return spk_setup_complete



    @staticmethod
    def spk_popup_lock_save() -> bool:
        answer = False
        display_text = """ 
KITA has now been locked!\n\n
Would you like KITA to save your Speaker Lock preference and use it as default in the future? \n
If you select 'Yes', the next time you run MotionInput, KITA will already be locked to your voice.\n
To remove this setting later, you can use the 'remove locked speaker' speech command.
        """
        spk_input = pyautogui.confirm(text=display_text,
                                            title='Save Speaker Lock setup?', 
                                            buttons=['Yes', 'No'])
        if spk_input == "Yes":
            answer = True
        return answer



    @staticmethod
    def spk_popup_lock(spk_name : str) -> bool:
        answer = False
        display_text = f"Hi, {spk_name}!!\nKITA recognises your voice now!\nWould you like to LOCK the app with your voice?\nIf you say 'Yes' only you will be able to use KITA until you 'stop speaker identify'."
        title_lock = "Lock KITA Speech?"
        spk_input = pyautogui.confirm(text=display_text, 
                                     title=title_lock,
                                     buttons=['Yes', 'No'])
        if spk_input == "Yes":
            answer = True
        return answer



    @staticmethod
    def spk_popup_lock_complete() -> None:
        display_text = """
Your app has now been locked with your voice!\n\n
If you have selected 'Yes' for saving your lock the next
time you run MotionInput, your preferences will be ready to use 
at speech command 'speaker identify'
        """
        pyautogui.alert(text=display_text,
                        title='Success! Process complete!', 
                        button='OK')



    @staticmethod
    def spk_popup_reminder_second_try() -> None:
        display_text = """
Reminders:\n
Avoid making pauses for a minimum of 5 seconds.\n 
Speak clearly but as close to comfortable daily speech as possible.\n\n
Whenever you are ready...
            """
        pyautogui.alert(text=display_text,
                        title='Another Attempt',
                        button='Ready')



    def spk_error(self, ex) -> None:
        """
        Handle SPKID errors.
        Allows to disable SPKID 
        and continue running MI without it.
        """
        msg = """
There was a problem with Speaker Identification. \n
Unfortunately it would have to be disabled.\n
If you require this feature, please click EXIT, restart MotionInput and try again.
        """
        log.error(f"<KITA> There was a problem with Speaker Identification: {ex}")
        error_response = pyautogui.confirm(
                        text = msg,
                        title='SPKID ERROR', 
                        buttons=['Continue without Speaker ID', 'EXIT'])
        if error_response == "Continue without Speaker ID":
            self.spk_stop_speaker()
            with lock:
                self.config_editor.update("modules/speech/speaker/speaker_enabled", "false")
                self.config_editor.save()
        else:
            raise ex
