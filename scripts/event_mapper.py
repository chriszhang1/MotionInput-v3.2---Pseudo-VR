'''
Author: Carmen Meinson
'''
from typing import Set, Dict, Optional

from scripts.core import Model
from scripts.gesture_event_handlers import *
from scripts.gesture_events import *
from scripts.tools.json_editors.event_editor import EventEditor
#from scripts.tools.json_editors.hotkeys_editor import HotkeysEditor
from .gesture_loader import GestureLoader


class EventMapper:
    def __init__(self, event_handlers: GestureEventHandlers):
        self._events = EventEditor().get_all_data()

        self._event_classes = GestureEvents()
        self._event_handlers = event_handlers
        self._gesture_loader = GestureLoader()


    def switch_events_in_model(self, model: Model, 
                                event_names_to_remove: Set[str], 
                                event_names_to_add: Set[str]) -> None:
        """
        Based on the given event names 
        creates the GestureEvent instances to be added to the model.
        All the gestures and modules used by the given events will also be added to 
        the model by the GestureLoader, if they have not been before.
        Then all the events are switched in the model.

        Removing an event may also lead to removing of some gestures that are 
        no longer used by any events in the model.
        If all gestures from one module get removed so does the module.

        :param model: model in which to switch the events
        :type model: Model
        :param event_names_to_remove: names of the events to remove
        :type event_names_to_remove: Set[str]
        :param event_names_to_add: names of the events to add
        :type event_names_to_add: Set[str]
        """
        events_to_add = {}
        gestures_to_add = set()

        for name in event_names_to_add:
            event_class = self._event_classes.get_event(self._events[name]["type"])
            event = event_class(**(self._events[name]["args"]))

            functions = self._get_trigger_functions(self._events[name]["triggers"])
            event.set_trigger_functions(functions)
            event.set_bodypart_names(self._events[name]["bodypart_names_to_type"])
            ###
            events_to_add[name] = event
            gestures_to_add = gestures_to_add | set(event.get_all_used_gestures())
        
        # TODO: Complete Hotkeys Feature
        #if path:
        #    self._hotkeys_editor = HotkeysEditor(path)
        #    self._hotkeys_events = HotkeysEditor().get_all_data()

        #    hotkeys_event_class = self._event_classes.get_event(self._hotkeys_events[name]["type"])
        #    hotkeys_event = hotkeys_event_class(**(self._hotkeys_events[name]["args"]))
        #    functions = self._get_trigger_functions(self._hotkeys_events[name]["triggers"])
        #    hotkeys_event.set_trigger_functions(functions)
        #    hotkeys_event.set_bodypart_names(self._hotkeys_events[name]["bodypart_names_to_type"])
        #    ###
        #    events_to_add[name] = hotkeys_event
        #    gestures_to_add = gestures_to_add | set(hotkeys_event.get_all_used_gestures())

        self._gesture_loader.add_gestures_to_model(model, gestures_to_add)
        model.switch_events(event_names_to_remove, events_to_add)


    def _get_trigger_functions(self, trigger_to_name: Dict[str, str]) -> Dict[str, Callable]:
        trigger_to_func = {}
        for trigger, name in trigger_to_name.items():
            trigger_to_func[trigger] = self._event_handlers.get_handler_func(*name)
        return trigger_to_func
