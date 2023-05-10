'''
Author: Keyur Narotomo
'''

# Class for reading, and editing the in_air_keyboard JSON file
from scripts.tools.json_editors.json_editor import JSONEditor

class InAirKeyboardEditor(JSONEditor):
    def __init__(self):
        super().__init__("in_air_keyboard.json")