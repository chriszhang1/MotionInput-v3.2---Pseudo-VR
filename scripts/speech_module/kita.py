'''
Authors: Samuel Emilolorun, Anelia Gaydardzhieva
Comments: 
Vosk Speech Recognition Model
v3.1: Speaker Identification Model addition
'''
# Logging
from typing import Any, Dict
from scripts.tools.logger import get_logger
log = get_logger(__name__)
# Standard 
import json
import os
import sys
import queue
from threading import Thread, Event, RLock
# Third party 
import sounddevice as sd
from vosk import Model, KaldiRecognizer, SpkModel, SetLogLevel
SetLogLevel(-1) # 0 to allow model debug
import pyautogui
# Local 
from scripts.tools import Config
from scripts.tools.utils import Utils as u
from scripts.speech_module.kita_speaker_process import SPKProcess
#from scripts.speech_module.kita_custom_hotkeys_process import HotkeysProcess


# Path - Vosk main model - English
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "data"))
# Path - Speaker Identification (Vosk)
VOSK_PATH = os.path.join(DATA_PATH, 'ml_models', 'speech', Config().get_data("modules/speech/language"))
SPEAKER_MODEL_PATH = os.path.join(DATA_PATH, 'ml_models', 'speech', Config().get_data("modules/speech/speaker/speaker_model"))
u.check_paths(DATA_PATH, SPEAKER_MODEL_PATH)


def check_language_path(VOSK_PATH):
    """
    Language custom error handler.
    If language path is not valid, it 
    changes back to english.
    """
    if not os.path.exists(VOSK_PATH):
        log.error(f"[Check_path] Path {VOSK_PATH} was not found")
        conf = Config().get_editor()
        conf.update("modules/speech/language", "english")
        conf.save()
        log.error(f"[Check_path] Path VOSK_PATH was changed to English.")


# Lock
lock = RLock()


class KITA(Thread):
    """ Singleton KITA Thread """
    _instance = None
    _is_running = False

    def __new__(cls):
        with lock:
            cls.config = Config()
            cls.speech_enabled = cls.config.get_data("modules/speech/enabled")
            if cls._instance is None and not cls._is_running and cls.speech_enabled:
                ## General
                cls._instance = super(KITA, cls).__new__(cls)
                cls.daemon = True # because daemons exit with mainThread when MI is closed (do not change)
                cls.name = "Thread KITA"
                cls.speech_enabled = Config().get_data("modules/speech/enabled")
                # KITA
                cls.pause_flag = Event()
                cls.q = queue.Queue()
                cls.editor = cls.config.get_editor()
                # Audio
                device_info = sd.query_devices(kind='input') # All available devices
                cls.samplerate = int(device_info['default_samplerate']) # Selected device info
                # Vosk 
                model = Model(VOSK_PATH) # Speech recognition model
                cls.recogniser = KaldiRecognizer(model, cls.samplerate) # Recogniser (Kaldi does the actual speech-to-text conversion)
                # Speech commands
                cls.current_phrase = "" # Current transcribed text 
                cls.keyboard = None # Keyboard (for Transcription)
                ### SPK (Speaker Identification) - Model ###
                cls.spk = SPKProcess() # spk management class
                if cls.spk.is_spk_enabled():
                    spk_model = SpkModel(SPEAKER_MODEL_PATH) 
                    cls.recogniser.SetSpkModel(spk_model) # attaches itself to the recogniser; generates spk vector to Result['text'] - cannot be done once KITA is running
            return cls._instance



    def run(self) -> None:
        """
        START KITA
        """
        if not self.speech_enabled: # if speech disabled
            return
        with lock:
            KITA._is_running = True
            self.pause_flag.set() # sets the events flag to green for KITA
        # Audio Stream start
        self._start_audio_recording()
        # Loop
        while self.is_running():
            self.pause_flag.wait() # KITA waits here when the flag is cleared, until set again
            self._perform_action()
        # Stop Audio stream
        self._stop_audio_recording()



    def _perform_action(self) -> None:
        """
        Speaker Recognition, Speech Commands, Transcription, Speaker Identification, Custom Hotkeys
        """
        json_data = self._get_current_phrase_dict() 
        ## Special case
        # Allows 'stop speaker identify' speech command even if MI is locked to a different speaker
        # The speech command method handles the rest
        allowed_phrases = ("stop speaker identify", "disable speaker mode", "restart speaker mode", "remove locked speaker", "speaker identify")
        for ph in allowed_phrases:
            if "partial" in json_data:
                if ph == json_data['partial']:
                    self.current_phrase = ph
                    return
            elif "text" in json_data:
                if ph == json_data['text']:
                    self.current_phrase = ph
                    return
        # Speaker Identification Process
        if self.spk.is_spk_enabled() and self.spk.is_spk_on() and "spk" in json_data:
            self._stop_audio_recording() # Pause audio buffer and KITA
            self.spk.speaker_identification_action(json_data) # SPKID Process
            self._start_audio_recording()# Unpause audio buffer and KITA
        # Speech Commands and Transcription
        self.regular_action(json_data)



    def regular_action(self, json_data : Dict[str, Any]) -> None:
        """
        Checks if there are any SPKID restrictions.
        If the authorisation criteria are met, sets up self.current_phrase, which is accessed
        by speech_landmark_detector for Speech commands.
        Then checks if Transcription is ON and passes phrase to Keyboard.typewrite().
        """
        if self.spk.is_spk_enabled() and self.spk.is_spk_on() and not self.spk.is_spk_verified():
            # Verification ( == True if authorised speaker or Spk process is OFF => verified by default)
                return

        # Autorised Speech commands on partial
        if 'partial' in json_data:
            self.current_phrase = json_data['partial']
            return # No Transcription
        # Autorised Speech commands on text
        else: 
            self.current_phrase = json_data['text']
        # If Transcription ON
        if self.keyboard is not None:
            if self.spk.spk_on:
                self.keyboard.spk_type_write(self.current_phrase, self.spk.spk_current_id, self.spk.spk_current_name)
            else:
                self.keyboard.type_write(self.current_phrase)



    def pause_KITA(self, value : bool) -> None:
        """
        Used in speaker_identification.py to pause KITA
        during introduction popup so that no vector is generated 
        during the user reading instructions time. 
        """
        if value:
            self.pause_flag.clear() # run() pauses at self.pause_flag.wait()
            self._stop_audio_recording()
        else:
            self._start_audio_recording()
            self.pause_flag.set() # run() starts again and ignores .wait() until .clear() is triggered again



    def _start_audio_recording(self) -> None:
        """
        Provides access to setting up the recorder from methods in the class.
        Used for audio buffer management - start speaker recognition audio stream.
        """
        try: 
            self.ris =  sd.RawInputStream(samplerate=self.samplerate, blocksize=8000,
                                        device=None, dtype='int16', 
                                        channels=1, callback=self._callback)
        except Exception as e:
            log.critical(f"<KITA> sd.RawInputStream could not be initialised: {e}")
            self.kita_error(e)
        else:
            #self.recogniser.Reset()
            self.ris.start()
            sys.stdout.flush()



    def _stop_audio_recording(self) -> None:
        """
        Stop/Pause audio stream
        """
        try:
            sys.stdout.flush()
            self.ris.stop()
            self.ris.close()
        except Exception as e:
            log.critical(f"<KITA> Audio Stream could not be stopped: {e}")
            self.kita_error(e) # Allows to disable speech and continue running MI
            raise



    def _callback(self, indata, frames: int, time, status) -> None:
        """
        Called from a separate Sounddevice thread for each audio block.
        It returns the microphone audio data then fed to KITA recogniser 
        for the speech-to-text conversion.
        """
        if status:
            print(status, file=sys.stderr)
            sys.stdout.flush()
        self.q.put(bytes(indata))



    def _get_current_phrase_dict(self) -> Dict[str, Any]:
        """ 
        This function does the actual Speech Recognition, namely, speech-to-text conversion. 
        It checks if the complete Result() is ready to return. Meanwhile it keeps returning the 
        PartialResult(). Partials are used for speedy Speech commands execution. 
        Complete results are used during Transcription, Correction and Speaker Identification.
        """
        json_data = {}
        audio = self.q.get() # queue to get the transcribed audio data from user microphone
        # Speaker vector (ID/Voice print) is only generated on 'text' Result()
        if self.recogniser.AcceptWaveform(audio): # process the audio data; convert speech-to-text
            json_data = json.loads(self.recogniser.Result()) # Vosk returns a json object by default
        else:
            json_data = json.loads(self.recogniser.PartialResult())
        return json_data


    def set_transcription(self, keyboard_instance : None) -> None:
        """ 
        Ran via Transcription.py which passess a Keyboard class instance 
        when transcription has been activated.
        Or sets this to None when stopped.
        """
        self.keyboard = keyboard_instance


    def is_running(self) -> bool:
        """
        Returns whether KITA is ON or OFF
        """
        with lock:
            return KITA._is_running


    def end(self) -> None:
        """
        STOP KITA
        """
        with lock:
            KITA._is_running = False


###-------------------------------------- KITA ERROR POPUP ---------------------------------------

    def kita_error(self, e) -> None:
        """
        Handle KITA errors
        """
        msg = """
There was a problem with KITA. \n
Unfortunately Speech functionalities have to be disabled.\n
If you require this feature, please click EXIT, restart MotionInput, and try again.
        """
        error_response = pyautogui.confirm(
                        text = msg,
                        title='ERROR', 
                        buttons=['Continue without Speech', 'EXIT'])
        if error_response == "Continue without Speech":
            with lock:
                self.end()
                self.editor.update("modules/speech/speaker/enabled", "false")
                self.editor.save()
        else:
            raise e