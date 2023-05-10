'''
Author: Oluwaponmile Femi-Sunmaila
'''
# Class for reading, and editing the config JSON file
from typing import Dict, Any
from scripts.tools.json_editors.json_editor import JSONEditor


class ConfigEditor(JSONEditor):
    """Class that handles the reading/writing of the config JSON"""

    def __init__(self):
        super().__init__("config.json")

    def get_activated_gesture_names(self, gesture_type: str) -> list[str]:
        """Gets all the names of the activated gestures in the JSON.values.

        :param gesture_type: Specifies whether the gestures are "extremity_triggers"
        or "exercises".
        :type gesture_type: str
        :return: A list of all the activated gestures.
        :rtype: list
        """
        out = []
        if gesture_type == "extremity_triggers":
            data = self.get_data(f"body_gestures/extremity_triggers")
            for trigger, vals in data.items():
                if vals["activated"]:
                    out.append(trigger)
        else:
            mode = self.get_data("modules/body/mode")
            data = self.get_data(f"body_gestures/exercises/{mode}")

            for _, vals in data.items():
                if vals["activated"]:
                    states = vals["states"]
                    for state, attributes in states.items():
                        if attributes["activated"]:
                            out.append(state)
        return out

    def get_activated_gestures(self, gesture_type: str) -> Dict[str, Any]:
        """Gets all the information of activated gestures.

        :param gesture_type: Specifies whether the gestures are "extremity_triggers" 
        or "exercises".
        :type gesture_type: str
        :return: A dictionary containing all the activated gestures and their attributes.
        :rtype: Dict
        """
        out = {}
        if gesture_type == "extremity_triggers":
            data = self.get_data(f"body_gestures/extremity_triggers")
            for trigger, attributes in data.items():
                if attributes["activated"]:
                    out[trigger] = attributes
        else:
            mode = self.get_data("modules/body/mode")
            data = self.get_data(f"body_gestures/exercises/{mode}")
            for _, vals in data.items():
                if vals["activated"]:
                    states = vals["states"]
                    for state, attributes in states.items():
                        if attributes["activated"]:
                            out[state] = attributes
        return out