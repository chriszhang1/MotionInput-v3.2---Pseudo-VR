'''
Author: Anelia Gaydardzhieva
Comments: 
TODO: Complete Hotkeys Feature
Not used at the moment!!
'''
from scripts.tools.logger import get_logger
log = get_logger(__name__)

import os
from typing import Dict, Any, Optional

from scripts.tools.json_editors.json_editor import JSONEditor
REQUIRED_ATTRS = ("type", "args", "bodypart_names_to_type", "triggers", "name")
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "data"))


class HotkeysEditor(JSONEditor):
    """ Class to manage the events JSON files during Hotkeys Process """

    def __init__(self, path: str, iter_type: Optional[str] = None):
        """
        Initialisation # TODO
        """
        self.path = DATA_PATH + "\\" +path
        if not(os.path.exists(self.path) and self.path.endswith(".json")):
            log.error(f"__init__: {self.path} path was not found")
            raise FileNotFoundError(f"file_not_found: {self.path}")
        self._read_data()
        if iter_type:
            self.data = self._to_iter(self.data, iter_type)


    def remove(self, path):
        """
        Remove
        """
        list_path = path.split("/")
        mode = self._traverse_json(list_path)
        mode.pop(list_path[-1], None)


    def add(self, path, event):
        """
        Adding a Gesture 
        """
        event = self._to_correct_type(event)
        name = self.validate_event(event)
        del event["name"]
        super().add(path, event, name)


    def validate_event(self, event):
        """
        Event Validations
        """
        if not isinstance(event, dict):
            raise TypeError("Events must be of type dict")
        for key in event:
            if key not in REQUIRED_ATTRS:
                raise KeyError(f"Invalid event attribute: {key}")
        if len(event.keys()) != len(REQUIRED_ATTRS):
            raise KeyError(f"Missing event attribute")
        return event["name"]

