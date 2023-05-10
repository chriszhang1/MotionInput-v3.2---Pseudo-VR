'''
Author: Oluwaponmile Femi-Sunmaila
'''
# Class for reading, and editing the mode_controller JSON file
from scripts.tools.json_editors.json_editor import JSONEditor


class ModeEditor(JSONEditor): 
    """Class that handles the reading of the mode_controller JSON"""    

    def __init__(self):
        super().__init__("mode_controller.json", iter_type="set")

    def remove(self, path, ):
        if not path.startswith("modes"): raise Exception("Only modes can be removed from the mode_controller JSON")
        list_path = path.split("/")
        if len(list_path) == 2:
            modes = self.data["modes"]
            modes.pop(list_path[-1], None)
        else:
            raise Exception(f"Cannot remove element'{list_path[1]}' as it is not a mode")

    def add(self, path, value):
        if not path.startswith("modes"): raise Exception("Only modes can be added to the mode_controller JSON")
        list_path = path.split("/")
        if not len(list_path) == 1:
            raise Exception("Only modes can be added to the mode_controller JSON")
        super().add(path, [], value)
            
