'''
Author: Anelia Gaydardzhieva
Comments:
Used in kita_speaker_process.py 
to read and edit speakers_data.json
'''
import json
from scripts.tools.json_editors.json_editor import JSONEditor


class SPKEditor(JSONEditor):
    def __init__(self):
        super().__init__("speakers_data.json")


    def update_json(self, json_data) -> None:
        with open(self.path, "w") as f:
            json.dump(json_data, f, indent=4, sort_keys=True)
