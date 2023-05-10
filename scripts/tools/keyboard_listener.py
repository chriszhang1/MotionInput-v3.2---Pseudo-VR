'''
Author: Anelia Gaydardzhieva
Comments:
# TODO: Currently not in use
Class Thread listening to all keyboard actions. 
It is waiting for a particular key (or a sequence of keys) to be pressed to take action.
It could be made to wait
'''
from scripts.tools.logger import get_logger
log = get_logger(__name__)
from pynput.keyboard import Key, Listener
from threading import Thread, Event, RLock
from scripts.tools.config import Config
#import pyautogui

# Lock
lock = RLock()

class KeyboardListener(Thread):
    """ Keyboard Listener Thread """
    _instance = None
    _is_running = False
    def __new__(cls):
        with lock:
            if cls._instance is None and not cls._is_running:
                cls._instance = super(KeyboardListener, cls).__new__(cls)
                cls.config = Config()
                cls.editor = cls.config.get_editor()
                cls.event_flag = Event()
                cls.daemon = True
                cls.name = "Thread Keyboard Listener"
                cls.listener = Listener(on_press=cls.on_press, on_release=cls.on_release)


                # pynput specific keys
                cls.codes = [
                    Key.alt, Key.alt_gr, Key.backspace, Key.caps_lock, Key.cmd, Key.ctrl, Key.delete, Key.down,
                    Key.end, Key.enter, Key.esc, Key.f1, Key.esc.f2, Key.f3, Key.f4, Key.f5,
                    Key.f6, Key.f7, Key.f8, Key.f9, Key.f10, Key.f11, Key.f12, Key.f13, Key.f14, Key.f15,
                    Key.f16,  Key.f17,  Key.f18, Key.f19, Key.f20, Key.home, Key.left,
                    Key.page_down, Key.page_up, Key.right,
                    Key.shift, Key.space, Key.tab, Key.up, Key.insert, Key.menu, Key.num_lock, 
                    Key.pause, Key.print_screen, Key.scroll_lock
                    ]
                # pynput specific strings for keys
                cls.texts = [
                    'alt', 'alt gr', 'backspace', 'caps lock', 'cmd', 'ctrl', 'delete','down', 
                    'end', 'enter', 'esc', 'f1', 'f2', 'f3', 'f4', 'f5', 
                    'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 
                    'f16', 'f17', 'f18', 'f19', 'f20', 'home', 'left', 
                    'page down', 'page up', 'right', 
                    'shift', 'space', 'tab', 'up', 'insert', 'menu',
                    'num lock', 'pause', 'print screen', 'scroll lock'
                    ]
                cls.pressed_keys = []
                cls.seq_letters = []
                cls.seq_digits = []
                cls.list_action_phrases = []

            return cls._instance

    def run(self) -> None:
        """
        Overwrite thread run
        """
        with lock:
            KeyboardListener._is_running = True
            with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                listener.join()


    def on_press(self, key) -> None:
        """
        On key Press during keyboard listener
        """
        try:
            if key in self.codes:
                kt = self.texts[self.codes.index(key)]
                if kt not in self.pressed_keys: self.pressed_keys.append(kt)
                print("Key in self.codes:: ", key)
            else:
                k = str(self.listener.canonical(key))
                if k != '.' and '.' in k: k = k.split('.')[1]
                if k not in self.pressed_keys: self.pressed_keys.append(k)
                print("Key NOT in self.codes:: ", key)
        except Exception as e:
            print("Keyboard Listener: There was a problem: ", e)


    def on_release(self, key) -> None:
        """
        Keyboard Listener
        """
        if key == Key.f8:  # individual key action
            self.custom_key_action_1()
        #elif key == Key.space: # individual key action
        #    self.custom_key_action_X()
        #    self.seq_letters = [] # reset list
        #    self.seq_digits = [] # reset list
        #TODO: 
        # if key in alphabet: 
        #   seq_letters.append(key)
        #   if seq_letters.strip(),tolower() in self.list_action_phrases:
        #   execute something


    def custom_key_action_1(self) -> None:
        """
        Currently called On key press f8
        if Keyboard started
        """
        # read data
        self.show_welcome_msg = self.config.get_data("general/show_welcome_msg")
        # rotate true/false options
        if self.show_welcome_msg:
            self.editor.update("modules/speech/show_welcome_msg", "false")
        else: self.editor.update("modules/speech/show_welcome_msg", "true")
        self.editor.save()


    def is_running(self):
        return self.running

