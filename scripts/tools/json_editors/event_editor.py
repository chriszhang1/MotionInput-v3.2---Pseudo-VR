'''
Author: Oluwaponmile Femi-Sunmaila
'''
# Class for reading, and editing the event JSON file
from scripts.tools.json_editors.json_editor import JSONEditor
REQUIRED_ATTRS = ("type", "args", "bodypart_names_to_type", "triggers", "name")


class EventEditor(JSONEditor):
    """Class that handles the reading/writing of the event JSON

    Events should be of the form
    event_name : {
        type : EventClassName
        args : {}
        bodypart_names_to_type : {bodypart_name : type}
        triggers: {
            trigger_name : (trigger_class, trigger_function)
        }
    }
    """

    def __init__(self):
        super().__init__("events.json", iter_type="tuple")

    def remove(self, path):
        list_path = path.split("/")
        mode = self._traverse_json(list_path)
        mode.pop(list_path[-1], None)

    def add(self, path, event):
        """Adds A Gesture to the event JSON
        """
        event = self._to_correct_type(event)
        name = self.validate_event(event)
        del event["name"]
        super().add(path, event, name)

    def validate_event(self, event):
        if not isinstance(event, dict):
            raise TypeError("Events must be of type dict")
        for key in event:
            if key not in REQUIRED_ATTRS:
                raise KeyError(f"Invalid event attribute: {key}")
        if len(event.keys()) != len(REQUIRED_ATTRS):
            raise KeyError(f"Missing event attribute")
        return event["name"]
