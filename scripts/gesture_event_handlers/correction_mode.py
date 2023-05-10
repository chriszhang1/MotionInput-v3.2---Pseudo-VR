'''
Author: Anelia Gaydardzhieva
Comments: 
This file edits KITA's transcribed text before typewrite() in Keyboard
Correction mode includes:
- Spelling
- Maths symbols and numbers
- Punctuation
- Profanity filter
'''
from scripts.tools.logger import get_logger
log = get_logger(__name__)

# Standard
import json
import os
import re
from threading import RLock

# Local
from scripts.tools.view import View
from scripts.tools.config import Config
from scripts.tools.utils import Utils as u

# Path - Correction Data
CORRECTION_MODE_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "data", "correction_data.json"))
u.check_paths(CORRECTION_MODE_DATA_PATH)

lock = RLock() 


class CorrectionMode:
    _is_running = False
    _transcription_running = False

    def __init__(self, view=View):
        self.config = Config()
        with lock:
            self._enabled = self.config.get_data("modules/speech/correction_enabled") 
        if self._enabled:
            self._view = view
            self.editor = self.config.get_editor()
            # Get Single words 
            with open(CORRECTION_MODE_DATA_PATH, "r") as repl_words:
                words_replace = json.load(repl_words)
                self.single_words_replace = words_replace["single_words"]
            # Get Multiple words
            multiple_words_replace = words_replace["multiple_words"].items()
            self.multiple_words_replace = tuple((re.compile(match), replacement) 
                                                for (match, replacement) in multiple_words_replace)


    def start_correction_mode(self) -> None:
        """ 
        START Correction mode 
        """
        if not self._enabled or self.is_running(): 
            return
        # If Transcription OFF (it is necessary)
        if not self.is_transcription_running():
            self._view.update_display_element("correction_element", {"correction_mode": False, "transcriber_required": True })
        else:
            # If Transcription ON
            with lock:
                self.set_correction(True)
            self._view.update_display_element("correction_element", {"correction_mode": True, "transcriber_required": False })
            log.info("Correction mode ON")


    def stop_correction_mode(self) -> None:
        """
        STOP Correction mode
        """
        with lock:
            self.set_correction(False)
        self._view.update_display_element("correction_element", {"correction_mode": False, "transcriber_required": False})
        log.info("Correction mode OFF")


    def transform_current_phrase(self, phrase : str) -> str:
        """ 
        Transformation/Edit recognised spoken words/phrases 
        """
        # First replace Multiple words
        for match, replacement in self.multiple_words_replace:
            try:
                phrase = match.sub(replacement, phrase)
            except Exception as e:
                log.error(f"Correction mode: There was a problem with multiples: {e}")
        # Then Single words
        words = phrase.split(" ")
        for index, wd in enumerate(words):
            try:
                try_word = self.single_words_replace.get(wd)
                if try_word is not None:
                    wd = try_word
                words[index] = wd
            except Exception as exc:
                log.error(f"Correction mode: There was a problem with singles: {exc}")
            words[:] = [wd for wd in words if wd]
        return " ".join(words)


    def is_running(self) -> bool:
        """ 
        Called from Keyboard before typewrite() 
        """
        return CorrectionMode._is_running


    def is_transcription_running(self) -> bool:
        """ 
        Called from Keyboard before typewrite() 
        """
        return CorrectionMode._transcription_running


    def set_transcription(self, value : bool) -> None:
        """ 
        Transcription communication
        """
        CorrectionMode._transcription_running = value


    def set_correction(self, value : bool) -> None:
        """
        Set correction mode
        """
        CorrectionMode._is_running = value
