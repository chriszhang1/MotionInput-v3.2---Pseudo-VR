'''
Author: Oluwaponmile Femi-Sunmaila
Contributors: Anelia Gaydardzhieva
Comments:
Class for reading and editing JSON files
'''
from scripts.tools.logger import get_logger
log = get_logger(__name__)

# Standard
import ast
import json
import sys
import os
from typing import Dict, Any, Optional

# Local
from scripts.tools.json_editors.json_encoder import JSONEncoder


def get_data_path():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),"../../../data"))
 

DATA_PATH = get_data_path()
ERRORS = {
    "illegal_update": (
        f"Cannot update as path leads to a JSON"
        "object, not an attribute. To change an "
        "entire JSON object, you need to do it manually: "),
    "path_does_not_exist" : "JSON path does not exist",
    "not_dynamic":"The file you are trying to update does not support dynamic update, try using the .update() method",
    "file_not_found": "Missing data file: "
}
# TODO: Error handling is not useful in its current shape.
# Rewrite this class and the rest of the editors in this directory 
# into pydantic BaseModel extension dataclasses!
# Pydantic is probably the most advanced open-source validation library.
# TODO: No method to overwrite a JSON file, only targeted JSON objects


class JSONEditor:
    """ JSON data handler - Used as abstract class for other editors """

    def __init__(self, path: str, iter_type: Optional[str] = None):
        """Initialises JSONEditor object by reading contents of the 
        JSON file in the specified path.

        :param path: The path of the JSON file to be read/edited.
        :type path: str
        :iter_type: The type of iterable JSON lists should be converted to.
        """
        self.path = DATA_PATH + "\\" +path
        if not(os.path.exists(self.path) and self.path.endswith(".json")):
            log.error(f"__init__: {self.path} path was not found")
            raise FileNotFoundError(f"{ERRORS['file_not_found']}{self.path}")
        self._read_data()
        if iter_type:
            self.data = self._to_iter(self.data, iter_type)


    def get_all_data(self) -> Dict[str, Any]:
        """Retrieves the data stored in the JSONEditor object, 
        reflects all unsaved changes made to the JSON file.

        :return: The data stored in the JSONEditor Object.
        :rtype: Dict[str, Any]
        """
        return self.data


    def get_data(self, path: str) -> Dict[str, Any]:
        """Retrieves some data stored in the JSON file.

        :param path: The location of the JSON object to be read.
        :type path: str
        :return: The retrieved data from the JSON file.
        :rtype: [Dict]
        """
        list_path = path.split("/")
        try:
            out = self._traverse_json(list_path)[list_path[-1]]
        except KeyError:
            log.error(f"get_data: {self.path} path does not exist")
            raise KeyError(ERRORS["path_does_not_exist"]) 
        return out


    def update(self, path: str, val: str) -> None:
        """Updates the data JSON file.

        :param path: The gesture to be added to the JSON
        :type path: str
        :param val: The value that is being added to the JSON
        :type val: Any
        """
        val = self._to_correct_type(val)
        list_path = path.split("/")
        try:
            obj = self._traverse_json(list_path)
        except KeyError:
            self._read_data()
            log.error(f"update: {self.path} path does not exist")
            raise KeyError(ERRORS["path_does_not_exist"])
        obj[list_path[-1]] = val


    def add(self, path: str, val: Dict[str, Any], key: str) -> None:
        """Adds an object to the JSON file.

        :param path: The path the object should be added to.
        :type path: str
        :param val: The object to be added.
        :type val: Dict[str, Any]
        :param key: The name of the object to be added.
        :type key: str
        # TODO: Optimise! Handle accurate SPECIFIC exceptions!
        """                
        list_path = path.split("/")
        if list_path == [""]:
            list_path = []
        position = self._traverse_json(list_path)
        if list_path == []:
            position[key] = val
        else:
            position[list_path[-1]][key] = val


    def save(self) -> None:
        """
        Saves all changed made to the JSON file
        """
        json_object = json.dumps(
            self.data, indent=4, sort_keys=True, cls=JSONEncoder)
        with open(self.path, "w") as file:
            file.write(json_object)


    @classmethod
    def _to_iter(cls, data: Dict[str, Any], iter_type: str) -> Dict[str, Any]:
        """
        Deals with particualr data type interations.
        TODO: Defining these in the individual editors 
        which extend this class might be better.
        """
        iterator = None
        if iter_type == "tuple":
            iterator = tuple
        if iter_type == "set":
            iterator = set
        if isinstance(data, list):
            return iterator(cls._to_iter(elements, iter_type) for elements in data)
        elif isinstance(data, dict):
            return {key: cls._to_iter(items, iter_type) for key, items in data.items()}
        return data


    def _traverse_json(self, path: list, current_obj: Optional[Dict[str, Any]] = None) -> Dict[str, Any]: 
        """
        Traversing a JSON file 
        TODO: Optimise!
        """
        if len(path) == 0: return self.data
        if not current_obj: current_obj = self.data
        next_object = path[0]
        if next_object in current_obj:
            if len(path) == 1:
                return current_obj
            else:
                next_object = current_obj[next_object]
                return self._traverse_json(path[1:], next_object)
        log.error(f"_traverse_json: path <{self.path}> does not exist")
        raise KeyError(ERRORS["path_does_not_exist"])


    def _read_data(self) -> None:
        """
        Reads all data from a JSON file
        """
        with open(self.path, "r") as file:
            self.data = json.load(file)


    @staticmethod
    def _to_correct_type(val: Any) -> Any:
        """
        Transforms types
        TODO: Here again, if we were defining pydantic classes
        this would not be necessary.
        """
        val = str(val)
        if '[' in val or '{' in val:
            return ast.literal_eval(val)
        if val == "true":
            return True
        if val == "false":
            return False
        if "." in val:
            return (float(val))
        if not val.isnumeric():
            return val
        return int(val)


    @staticmethod
    def grab_json_encoder():
        """
        Currently called from SPKEditor 
        for custom file update
        """
        return JSONEncoder
