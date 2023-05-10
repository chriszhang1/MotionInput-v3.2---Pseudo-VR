'''
Author: Anelia Gaydardzhieva
Comments:
This class could be adapted for other messages as well
It is only ran once, after which 'show_welcome_msg' is set to false and MI opens.
No keyboard key has been made available to reset or show the message again at this point,
since keys are limited and the usefulness of this method has not been concluded yet.
'''
# Standard
from threading import Lock

# Third party
from pyautogui import alert

# Local
from scripts.tools import Config

lock = Lock()


class WelcomeMsg:
    """ Class for Welcome Message """
    def __init__(self):
        self.config = Config()
        self.editor = self.config.get_editor()
        self.show_welcome_msg = Config().get_data("general/show_welcome_msg") # bool
        # Welcome Message
        if self.show_welcome_msg:
            self.welcome_message()


    def welcome_message(self) -> None:
        """
        Triggers a welcome message if enabled
        """
        welcome_msg = self.config.get_data("general/welcome_msg") # str
        alert(text=welcome_msg, title='Welcome to UCL MotionInput v3.1!', button='OK')
        with lock:
            self.editor.update("general/show_welcome_msg", "false") # disable
            self.editor.save()