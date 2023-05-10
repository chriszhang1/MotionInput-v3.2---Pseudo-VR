'''
Author: Oluwaponmile Femi-Sunmaila
'''
# Class for reading, and editing the gesture JSON file
from typing import Dict, Set, Any

from scripts.core.gesture_factory import Primitive
from scripts.tools.json_editors.json_editor import JSONEditor

MODULES = ("head", "hand", "body", "eye", "speech")


class GestureEditor(JSONEditor):
    """Class that handles the reading/writing of the gesture JSON

    Gestures should be of the form
    {
        gesture_name : {
            primitive_name : bool,
            primitive_name : bool,
            ...,
        }
    }
    """

    def __init__(self, get_primitives : bool=True):
        super().__init__("gestures.json")
        self._as_primitives = get_primitives


    def get_all_data(self) -> Dict[str, Any]:
        """Use this to get all gestures

        :return: The contents of the JSON file, with all primitives being their corresponding python objects.
        :rtype: Dict[str, Dict[str]]
        """
        raw_data = super().get_all_data()
        if not self._as_primitives: return raw_data
        for _, bodypart in enumerate(raw_data):
            for _, (gesture, primitives) in enumerate(raw_data[bodypart].items()):
                primitive_set = set()
                for primitive, val in primitives.items():
                    primitive_set.add(Primitive(primitive, val))
                raw_data[bodypart][gesture] = primitive_set
        return raw_data

    def get_data(self, path : str) -> Set[Primitive]:
        """Gets all the primitives of a specified gesture.

        :param path: The path to the event to retrieve.
        :type path: str
        :return: A set of primitives representing the gesture.
        :rtype: Set[Primitive]
        """
        list_path = path.split("/")
        gesture_name = list_path[-1]
        try:
            data = self._traverse_json(list_path)[gesture_name]
        except KeyError:
            raise Exception("JSON path does not exist")
        if not self._as_primitives: return data
        primitives = set()
        for prim, val in data.items():
            primitives.add(Primitive(prim, val))
        return primitives

    def remove(self, path):
        if path in MODULES: raise Exception("You almost deleted an entire module worth of gestures, try fixing your path.")
        list_path = path.split("/")
        mode = self._traverse_json(list_path)
        try:
            mode.pop(list_path[-1])
        except Exception:
            raise Exception(f"{list_path[-1]} is not in the JSON file")

    def add(self, path, gesture):
        """Adds A Gesture to the gesture JSON
        """  
        gesture = self._to_correct_type(gesture)
        name = self.validate_gesture(gesture)
        del gesture["name"]
        super().add(path, gesture, name)

    def validate_gesture(self, gesture):
        if not isinstance(gesture, dict): raise TypeError("Gestures must be of type dict")
        for key in gesture:
            if key == "name": continue
            if not isinstance(gesture[key], bool): raise Exception(f"Invalid gesture value for {key}, must be of type bool, not {type(gesture[key])}")
        if "name" not in gesture: raise Exception("Missing gesture name param")
        if len(gesture) == 1: raise Exception("Gesture must have at least 1 primitive")
        return gesture["name"]

    def set_as_primitives(self, get_primitives: bool):
        self._as_primitives = get_primitives
