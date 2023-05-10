'''
Author:
Contributors: Siam Islam, Keyur Narotomo, Anelia Gaydardzhieva, Chris Zhang
Comments:
Hotkeys, Transcription, Correction mode
Hardcoded methods are only defined for specific single keys or
hotkeys that have been observed to be problematic when ran via hotkey_combination()
Single or multiple keys should first be defined in events.json as hotkey_combination()
prior to hardcoding additional methods.
'''

from scripts.tools.logger import get_logger
log = get_logger(__name__)

# Standard
import os
import subprocess
import threading
from typing import Callable, Tuple
import time

# Third Party
from pynput.keyboard import Controller, Key
import pyautogui
import pydirectinput
import pyperclip
from text2digits import text2digits

# Local
from scripts.gesture_event_handlers.correction_mode import CorrectionMode
from scripts.tools.json_editors.mode_editor import ModeEditor
from scripts.tools.launch_utils import launch_settings, launch_help


class Keyboard:

    def __init__(self) -> None:
        self.thread_name = "Keyboard: Not defined"
        self.kb = Controller()
        self.correction_mode = CorrectionMode()
        self.mode_editor = ModeEditor()
        # TODO: Complete logic for custom email typewrite
        self.custom_email = ""
        # custom labels pydirectinput
        self.special_keys = {
            "esc": Key.esc,
            "ctrl": Key.ctrl,
            "shift": Key.shift,
            "alt": Key.alt,
            "windows": Key.cmd,
            "enter": Key.enter,
            "f1": Key.f1,
            "f2": Key.f2,
            "f3": Key.f3,
            "f4": Key.f4,
            "f5": Key.f5,
            "f6": Key.f6,
            "f7": Key.f7,
            "f8": Key.f8,
            "f9": Key.f9,
            "f10": Key.f10,
            "f11": Key.f11,
            "f12": Key.f12,
            "print_screen": Key.print_screen,
            "insert": Key.insert,
            "delete": Key.delete,
            "home": Key.home,
            "end": Key.end,
            "page_up": Key.page_up,
            "page_down": Key.page_down,
            "space": Key.space
        }



    # Pydirectinput methods are an alternative to pyautogui
    # In some applications pyautogui might not trigger any keys 
    # especially in games
    @staticmethod
    def up_arrow_press() -> None:
        pydirectinput.press("up")  

    @staticmethod
    def down_arrow_press() -> None:
        pydirectinput.press("down")

    @staticmethod
    def right_arrow_press() -> None:
        pydirectinput.press("right")

    @staticmethod
    def left_arrow_press() -> None:
        pydirectinput.press("left")


    # Threads - used in Exercise and Gaming
    def _run_thread(self, method: Callable, args: Tuple) -> None:
        threading.Thread(target=method, args=args, name = self.thread_name).start()

    def key_press(self, key) -> None:
        self.thread_name = "Keyboard: key_press"
        self._run_thread(pydirectinput.press, (key,))

    def key_down(self, key) -> None:
        self.thread_name = "Keyboard: key_down"
        self._run_thread(pydirectinput.keyDown, (key,))

    def key_up(self, key) -> None:
        self.thread_name = "Keyboard: key_up"
        self._run_thread(pydirectinput.keyUp, (key,))

    # kb is Controller() 
    def delete_press(self) -> None:
        self.kb.press(self.special_keys["delete"])


    # Direction arrows
    @staticmethod
    def up_arrow() -> None:
        pyautogui.press('up')

    @staticmethod
    def down_arrow() -> None:
        pyautogui.press('down')

    @staticmethod
    def left_arrow() -> None:
        pyautogui.press('left')

    @staticmethod
    def right_arrow() -> None:
        pyautogui.press('right')


    # Default pyautogui single keys
    @staticmethod
    def copy() -> None:
        """
        Kept as manual definition due to observed
        issue during Transcription and Correction modes.
        """
        pyautogui.hotkey('ctrl', 'c')

    @staticmethod
    def cut() -> None:
        """
        Kept as manual definition due to observed
        issue during Transcription and Correction modes.
        """
        pyautogui.hotkey('ctrl', 'x')


    ##### CUSTOM #####

    def settings(self) -> None:
        """
        Runs settings MFC GUI depending on current mode
        """
        launch_settings()

    def help(self) -> None:
        """ 
        Opens a help.txt depending on current mode
        """
        launch_help()


    # Visual Studio project specials
    @staticmethod
    def vs_open_all_windows() -> None:
        pyautogui.hotkey('ctrl', 'k')
        pyautogui.hotkey('shift', '1')

    @staticmethod
    def vs_maximize() -> None:
        pyautogui.hotkey('ctrl', 'k')
        pyautogui.hotkey('shift', '2')

    @staticmethod
    def vs_minimize() -> None:
        pyautogui.hotkey('ctrl', 'k')
        pyautogui.hotkey('shift', '3')

    @staticmethod
    def vs_zoom_in() -> None:
        pyautogui.hotkey('ctrl', 'k')
        pyautogui.hotkey('shift', '4')

    @staticmethod
    def vs_zoom_out() -> None:
        pyautogui.hotkey('ctrl', 'k')
        pyautogui.hotkey('shift', '5')

    @staticmethod
    def vs_reset_zoom() -> None:
        pyautogui.hotkey('ctrl', 'k')
        pyautogui.hotkey('shift', '6')

    @staticmethod
    def vs_insert_to_editor() -> None:
        pyautogui.hotkey('ctrl', 'k')
        pyautogui.hotkey('shift', '7')

    @staticmethod
    def vs_copy_to_clipboard() -> None:
        pyautogui.hotkey('ctrl', 'k')
        pyautogui.hotkey('shift', '8')

    # Single Cases
    # TODO: These need thorough testing to safely move to hotkeys
    @staticmethod
    def windows_key() -> None:
        pyautogui.press('win')

    @staticmethod
    def enter() -> None:
        pyautogui.press('enter')

    @staticmethod
    def escape() -> None:
        pyautogui.press('esc')

    @staticmethod
    def space() -> None:
        pyautogui.press('space')

    @staticmethod
    def page_up() -> None:
        pyautogui.press('pageup')

    @staticmethod
    def page_down() -> None:
        pyautogui.press('pagedown')

    @staticmethod
    def volume_up() -> None:
        pyautogui.press('volumeup')

    @staticmethod
    def volume_down() -> None:
        pyautogui.press('volumedown')

    # Transcription/Correction mode
    @staticmethod
    def capital_letters() -> None:
        pyautogui.press('capslock')

    @staticmethod
    def backspace() -> None:
        pyautogui.press('backspace')

    # Hashtag - Correction mode
    def hashtag(self) -> None:
        """ 
        It copy/pastes '#' 
        Needed because it is not possible to typewrite some 
        special chars with pyautogui alone.
        """
        if self.correction_mode.is_correction_running():
            pyperclip.copy('#')
            pyautogui.hotkey('ctrl', 'v')
            pyperclip.copy('')

    # Type Custom Email
    def send_custom_email(self) -> None:
        """
        #TODO:
        """
        if self.custom_email != "":
            pyautogui.typewrite(f'{self.custom_email}\n')

    # Open cmd prompt
    @staticmethod
    def windows_run() -> None:
        pyautogui.hotkey('win', 'r')

    def macros(self) -> None:
        self.windows_run()
        pyautogui.typewrite('cmd\n')

    def exit_program_MI(self) -> None:
        self.macros()
        pyautogui.typewrite('taskkill/im MI3-Facial-Navigation-3.11.exe')

    # FaceNav - Switches tabs
    @staticmethod
    def switch() -> None:
        pyautogui.hotkey('ctrl', 'shift', 'tab')

    # IBM game
    @staticmethod
    def ibm_game_e():
        pydirectinput.press("e")

    @staticmethod
    def ibm_game_q():
        pydirectinput.press("q")

    # Spider-Man 
    @staticmethod
    def spiderman_shoot():
        pydirectinput.press("e", 5, 0.05)

    @staticmethod
    def spiderman_throw():
        pydirectinput.keyDown("q")
        time.sleep(0.5)
        pydirectinput.keyUp("q")

    @staticmethod
    def spiderman_step():
        pydirectinput.press("ctrl", 2, 0.5)
    
    @staticmethod
    def spiderman_strike():
        pydirectinput.press("f")

    @staticmethod
    def spiderman_run():
        pydirectinput.keyDown("shift")
        pydirectinput.keyDown("w")

    @staticmethod
    def spiderman_walk():
        pydirectinput.keyUp("shift")
        pydirectinput.keyDown("w")

    @staticmethod
    def spiderman_hit():
        pydirectinput.mouseDown(duration=0.1)
        pydirectinput.mouseUp()

    @staticmethod
    def spiderman_stand():
        pydirectinput.keyUp("w")

    @staticmethod
    def spiderman_swing():
        pydirectinput.press("space", 1, 0.15)
        pydirectinput.keyDown("shift")
        time.sleep(2)
        pydirectinput.keyUp("shift")
        pydirectinput.press("space")

    @staticmethod
    def spiderman_jump():
        pydirectinput.press("space", 2, 0.5)

    @staticmethod
    def spiderman_health():
        pydirectinput.press("1")

    @staticmethod
    def spiderman_finish():
        pydirectinput.press("2")

    @staticmethod
    def game_press_e():
        pydirectinput.press("e")

    @staticmethod
    def game_press_q():
        pydirectinput.press("q")
    @staticmethod
    def spiderman_step():
        pydirectinput.press("ctrl", 2, 0.5)
    
    @staticmethod
    def game_press_f():
        pydirectinput.press("f")

    @staticmethod
    def game_run():
        pydirectinput.keyDown("ctrl")

    @staticmethod
    def game_walk():
        pydirectinput.keyUp("ctrl")

    @staticmethod
    def game_sneak():
        pydirectinput.keyDown("shift")

    @staticmethod
    def game_sneakUp():
        pydirectinput.keyUp("shift")

    @staticmethod
    def game_jump():
        pydirectinput.press("space")

    @staticmethod
    def game_one():
        pydirectinput.press("1")

    @staticmethod
    def game_two():
        pydirectinput.press("2")

    @staticmethod
    def game_three():
        pydirectinput.press("3")

    @staticmethod
    def game_four():
        pydirectinput.press("4")

    @staticmethod
    def game_five():
        pydirectinput.press("5")

    @staticmethod
    def game_six():
        pydirectinput.press("6")

    @staticmethod
    def game_seven():
        pydirectinput.press("7")

    @staticmethod
    def game_eight():
        pydirectinput.press("8")

    @staticmethod
    def game_nine():
        pydirectinput.press("9")
        

    ##################### Core Functionality Methods ######################

    def press(self, key) -> None:
        """
        Added due to self.key_press not supporting full range key press.
        Required in InAirKeyboard event handler
        e.g. print screen, page down etc.
        """
        self.kb.press(key)

    @staticmethod
    def hotkey_combination(*args) -> None:
        pyautogui.hotkey(*args)
        

    def key_combination(self, keys) -> None:
        self.press_release_keys(keys, True)  # first press the key(s)
        self.press_release_keys(keys, False)  # then release the key(s)


    def press_release_keys(self, keys, press) -> None:
        """
        Helper method for self.key_combination()
        Presses/releases all keys depending on the value of press (bool)
        """
        for key in keys:
            if len(key) != 1 and key in self.special_keys:
                key = self.special_keys[key]
            if press:
                self.kb.press(key)
            else:
                self.kb.release(key)


    @staticmethod
    def phrases_to_ignore(phrase : str) -> str:
        """
        Word which should not be transcribed
        """
        phrases_to_ignore = ("stop correction mode", "correction mode", "stop speaker identify", "speaker identify", "transcribe")
        for ph in phrases_to_ignore:
            if ph in phrase:
                phrase = ""
        return phrase


    def correction_conversions(self, phrase : str) -> str:
        """
        Used when Correction mode is ON
        """
        # Converting number words to digits
        t2d = text2digits.Text2Digits()
        phrase = t2d.convert(phrase)  # numbers filter -> including dates and in-text digits
        # Custom filter -> Applying Spelling, Profanity filter and Spoken Punctuation
        phrase = self.correction_mode.transform_current_phrase(phrase)
        return phrase


    @staticmethod
    def transcription_conversions(phrase : str) -> str:
        """
        Used is standard conditions when
        Correction mode is OFF
        """
        phrase = phrase[0].upper() + phrase[1:] # Capitalise the first character
        if " i " in phrase:
            phrase = phrase.replace(" i ", " I ")
        if " i'm " in phrase:
            phrase = phrase.replace(" i'm ", " I'm ")
        if " i've " in phrase:
            phrase = phrase.replace(" i've ", " I've ")
        phrase = f"{phrase}\n"
        return phrase


    def spk_type_write(self, phrase, spk_id, spk_name) -> None:
        """
        Used during Speaker Identification
        instead of type_write()
        """
        phrase = self.phrases_to_ignore(phrase)
        if phrase == "":
            return
        # CORRECTION MODE
        if self.correction_mode.is_running():
            phrase = self.correction_conversions(phrase)
        # TRANSCRIPTION MODE
        else:
            phrase = self.transcription_conversions(phrase)
            if spk_name == "": spk_name = "Unknown"
            phrase = f"[{spk_id}]{spk_name}: {phrase}"
        # FINALLY
        pyautogui.typewrite(f"{phrase}") # type text + new line


    def type_write(self, phrase : str) -> None:
        """ 
        Check for particular phrases to remove from 
        typewrite() during Transcription and Correction modes.
        These additions were made to ensure these 4 speech commands
        do not get typed during these modes. 
        Other keywords have been defined in correction_mode.json
        """
        phrase = self.phrases_to_ignore(phrase)
        if phrase == "":
            return
        # CORRECTION MODE
        if self.correction_mode.is_running():
            phrase = self.correction_conversions(phrase)
        # TRANSCRIPTION MODE
        else:
            phrase = self.transcription_conversions(phrase)
        # FINALLY
        pyautogui.typewrite(f"{phrase}")



### List of all possible keyboard keys for pyautogui below (Note: Some special characters like # or ~ are failing. To solve this look at hashtag() method up for example.)

#['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', 
#'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
#':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', 
#'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 
#'{', '|', '}', '~', 
#'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace', 'browserback', 'browserfavorites', 'browserforward', 'browserhome', 'browserrefresh', 'browsersearch', 'browserstop', 
#'capslock', 'clear', 'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete', 'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 
#'f1', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20', 'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 
#'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja', 'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail', 'launchmediaselect', 'left', 
#'modechange', 'multiply', 'nexttrack', 'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'num7', 'num8', 'num9', 'numlock', 
#'pagedown', 'pageup', 'pause', 'pgdn', 'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn', 'prtsc', 'prtscr', 'return', 'right', 
#'scrolllock', 'select', 'separator', 'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab', 'up', 
#'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen', 'command', 'option', 'optionleft', 'optionright'] 
