"""
Author: Carmen Meinson
Contributors: Andrzej Szablewski, Anelia Gaydardzhieva
"""
from typing import Optional
from scripts.core.model import Model
from scripts.event_mapper import EventMapper
from scripts.gesture_event_handlers import GestureEventHandlers
from scripts.tools.config import Config
from scripts.tools.json_editors.mode_editor import ModeEditor
from scripts.tools.view import View

# TODO: Complete the Hotkeys Process
#import os
#import json
#from typing import Optional, List
#import pyautogui
#from scripts.tools.hotkeys_manager import HotkeysManager
#from win32gui import GetWindowText, GetForegroundWindow 
#HOTKEYS_ENABLED = Config().get_data("modules/speech/speech_hotkeys/hotkeys_enabled")
#DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "data"))
#HOTKEYS_SAVED_USER = Config().get_data("modules/speech/speech_hotkeys/hotkeys_saved_username")

SHOW_MODE_NAME = Config().get_data("general/view/show_mode_name")
JOYPAD_ENABLED_FLAG = Config().get_data("general/joypad-enabled")


class ModeController:
    def __init__(self, model: Model, view: View): # , custom_hotkeys_folder :str = "custom_hotkeys"
        self._mode_editor = ModeEditor()
        mode_config = self._mode_editor.get_all_data()
        #config_editor = Config().get_editor()

        self._modes = mode_config["modes"]
        self._iteration_order = mode_config["iteration_order"]
        self._current_mode = mode_config["current_mode"]
        self._mappings = mode_config["mode_labels"]
        self._next_mode = mode_config["current_mode"]
        #self.current_hotkeys_user = ""

        self._model = model
        self._event_handlers = GestureEventHandlers(self.set_next_mode, view)
        self._event_mapper = EventMapper(self._event_handlers)
        mode_name = self._current_mode
        if mode_name in self._mappings:
            mode_name = self._mappings[mode_name]
        # Print the mode name on the screen
        if SHOW_MODE_NAME:
            self._view = view
            self._view.update_display_element("active_mode_name", {"name": mode_name})

        self._event_mapper.switch_events_in_model(model, set(), self._modes[self._current_mode])

    #    ### TODO: Complete the Hotkeys Process ### (and move out of this file!!!please:))
    #    self.current_username = ""
    #    self.current_user_path = ""
    #    self.previous_app_opened = ""
    #    self.current_app_opened = ""
    #    # If Hotkeys enabled
    #    if HOTKEYS_ENABLED:
    #        self.hotkeys_folder = os.path.join(DATA_PATH, custom_hotkeys_folder)
    #        # If custom_hotkeys folder NOT exist
    #        if not os.path.isdir(self.hotkeys_folder):
    #            config_editor.update("modules/speech/speech_hotkeys/hotkeys_enabled", "false")
    #        # If custom_hotkeys folder exists
    #        else:
    #            self.users_dict = self.get_hotkeys_users() # get all users/apps (folders/json files)
    #            # If there IS a Saved hotkeys user
    #            if HOTKEYS_SAVED_USER != "":
    #                # If saved username folder exists
    #                for user, apps in self.users_dict:
    #                    # If saved user folder exists
    #                    if HOTKEYS_SAVED_USER == user: 
    #                        self.current_hotkeys_user = HOTKEYS_SAVED_USER # set current to saved
    #                # If saved user folder doen NOT exist
    #                if self.current_hotkeys_user == "":
    #                    self.popup_cannot_find_saved_user()
    #            # If NO Saved user
    #            else:
    #                proceed = self.popup_setup_hotkeys()
    #                # If user does not wish to set up
    #                if not proceed:
    #                    config_editor.update("modules/speech/speech_hotkeys/hotkeys_enabled", "false")
    #                # If user wants to set up
    #                else: 
    #                    pc_autorised = self.popup_setup_manual_or_auto()
    #                    # Grab os username
    #                    if pc_autorised:
    #                        self.current_username = os.getlogin()
    #                    # Ask for manual type username
    #                    else:
    #                        self.current_username = self.spk_popup_custom_username()
    #                    self.current_user_path = os.path.join(self.hotkeys_folder, self.current_username)
    #                    save_authorised = self.popup_save_user()
    #                    # If Save user authorised
    #                    if save_authorised:
    #                        config_editor.update("modules/speech/speech_hotkeys/hotkeys_saved_username", 
    #                                             self.current_username)


    #def change_hotkeys_folder_if_needed(self):

    #    # If hotkeys not setup: return
    #    if not HOTKEYS_ENABLED or self.current_user == "":
    #        return
    #    # Get app on focus
    #    current_app = GetWindowText(GetForegroundWindow())
    #    # Lower case
    #    self.current_app_opened = current_app.tolower().replace(' ', '_')
    #    if self.current_app_opened == self.previous_app_opened:
    #        return
    #    self.previous_app_opened = self.current_app_opened

    #    target_app = ""
    #    for user, apps in self.users_dict.items():
    #        for app in apps:
    #            if app in self.current_app_opened:
    #                target_app = app
    #    if target_app == "":
    #        return
    #    json_name = target_app + ".json"
    #    editor_path = "custom_hotkeys/" + json_name
    #    path = os.path.join(self.current_user_path, json_name)

    #    current_events = self._modes[self._current_mode]
    #    events_to_remove = []
    #    for event in self._modes[self._current_mode]:
    #        if event.startswith("speech_"):
    #            events_to_remove.append(event)

    #    new_events = []
    #    with open(path, "r") as f:
    #        custom_events = json.load(f)
    #        for key, value in custom_events.items():
    #            new_events.append(key)
    #    events_to_add = new_events - current_events

    #    self._event_mapper.switch_events_in_model(self._model, events_to_remove, events_to_add, editor_path)


    #def get_hotkeys_users(self) -> List[str]:
    #    """
    #    Get Users list
    #    """
    #    users_dict = {}
    #    for user in os.listdir(self.hotkeys_folder): # for every user/folder name in custom_hotkeys
    #        apps = []
    #        if os.path.isdir(os.path.join(self.hotkeys_folder, user)) and user not in users_dict: # and folder path exists
    #            user_path = os.path.join(self.hotkeys_folder, user) # set user path
    #            for json_file in os.listdir(user_path): # for every file in a user folder 
    #                json_file_path = os.path.join(user_path, json_file) # set file path
    #                if os.path.isfile(json_file_path) and json_file_path.ednswith(".json"):
    #                    app = '_'.join(json_file.split('.')[0].split('_')[1:]) # app name = ending of file name
    #                    apps.append(app)
    #            users_dict.update({ "user":user,"apps": apps}) # add user to dict
    #    print(users_dict)
    #    return users_dict




#    @staticmethod
#    def popup_cannot_find_saved_user() -> None:
#        """
#        Popup used during Hotkeys setup
#        In case there is a name in config.json 
#        but a folder with that name does not exist.
#        """
#        display_text = "Unfortunately, the Hotkeys saved user folder could not be found.\n Please make sure the folder is in the custom_hotkeys folder."
#        pyautogui.alert(text=display_text,
#                        title='Speech Hotkeys Process Error',
#                        button='OK')



#    @staticmethod
#    def popup_setup_hotkeys() -> bool:
#        """
#        Popup used during Hotkeys setup
#        Initial Question
#        """
#        answer = False
#        display_text = """
#MotionInput noticed that the Speech Hotkeys Process is enabled and there is no saved Hotkeys username.\n
#In the data/custom_hotkeys folder are located the users custom hotkeys folders and files.\n
#If you have a folder you wish to use, please select 'Yes'.\n
#Otherwise, please select 'Cancel' to disable this feature.
#"""
#        user_input = pyautogui.confirm(text=display_text,
#                        title='Hotkeys Process',
#                        buttons=['Yes', 'Cancel'])
#        if user_input == "Yes":
#            answer = True
#        return answer


#    @staticmethod
#    def popup_setup_manual_or_auto() -> bool:
#        """
#        Popup used during Hotkeys setup
#        Grab OS username or type manually
#        """
#        answer = False
#        display_text = """
#Would you like MotionInput to use your computer login name or you prefer providing your own username?
#"""
#        user_input = pyautogui.confirm(text=display_text,
#                        title='Setup Username',
#                        buttons=['Computer Login name', 'Custom Username'])
#        if user_input == "Computer Login name":
#            answer = True
#        return answer

#    @staticmethod
#    def spk_popup_custom_username() -> str:
#        """
#        Popup used during Hotkeys setup
#        Gets user input for USERNAME
#        Currently simple validation for the input 
#        to not be empty
#        """
#        valid = False
#        display_text = """
#Please provide your computer username or any username you wish.\n
#This could later be used to synchronise the the custom Hotkeys capability with 
#the Speaker Identification feature.\n
#Note: this field cannot be left empty
#        """
#        while not valid:
#            answer = pyautogui.prompt(display_text)
#            if answer != "":
#                valid = True
#        return answer


#    @staticmethod
#    def popup_save_user() -> bool:
#        """
#        Popup used during Hotkeys setup
#        Save Hotkeys User
#        """
#        answer = False
#        display_text = """
#Would you like to save you preference and use is as default in the future?
#"""
#        user_input = pyautogui.confirm(text=display_text,
#                        title='Hotkeys Process',
#                        buttons=['Yes', 'No'])
#        if user_input == "Yes":
#            answer = True
#        return answer




    def get_mode_name(self, name: str):
        if name in self._mappings:
            return self._mappings[name]
        return name


    def set_next_mode(self, mode: Optional[str] = None) -> None:
        """set the interaction mode that the model will be set to from the next frame. 
        (next time the change_mode_if_needed() is called)
        If no mode is indicated the next mode is set according to the iteration_order, provided

        :param mode: name of the mode, defaults to None
        :type mode: Optional[str], optional
        """
        if mode is not None:
            self._next_mode = mode
            return
        # if no mode given set the next mode according to iteration order
        self._next_mode = self._iteration_order[self._current_mode]
        if JOYPAD_ENABLED_FLAG == False and self._next_mode == "joystick":
            self._next_mode = self._iteration_order[self._next_mode]


    def change_mode_if_needed(self) -> None:
        """If the next mode has been previously set by the set_next_mode(), 
        change the events in the model accordingly.
        """
        if self._next_mode == self._current_mode: return
        current_events = self._modes[self._current_mode]
        new_events = self._modes[self._next_mode]
        events_to_remove = current_events - new_events
        events_to_add = new_events - current_events
        self._event_mapper.switch_events_in_model(self._model, events_to_remove, events_to_add)
        self._current_mode = self._next_mode
        if "idle" not in self._current_mode:
            self._mode_editor.update("current_mode", self._current_mode)
            self._mode_editor.save()
        # Print the mode name on the screen
        if SHOW_MODE_NAME:
            self._view.update_display_element("active_mode_name", {"name": self.get_mode_name(self._current_mode)})


    def close(self) -> None:
        """
        Close MI
        """
        events_to_remove = self._modes[self._current_mode]
        self._event_mapper.switch_events_in_model(self._model, events_to_remove, {})

