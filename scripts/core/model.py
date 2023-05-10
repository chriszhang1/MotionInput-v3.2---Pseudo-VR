'''
Author: Carmen Meinson
'''
import threading
from typing import Dict, Set

import numpy as np

from .gesture import Gesture
from .gesture_event import GestureEvent
from .gesture_factory import Primitive
from .module import Module
from .raw_data import RawData


class Model:
    def __init__(self) -> None:
        # dict: name of the gesture -> gesture event instances that use it
        self._gesture_to_events = {}
        # dict: name of the gesture -> name of the module that it belongs to
        self._gesture_to_module = {}
        # gesture instances created by the factory
        self._active_gestures = set()  
        # gesture event instances that have state active and could possibly trigger an event
        self._active_events = set()

        self._events = {}  # dict: event name -> event instance
        self._modules = {}  # dict: module name -> Module instance

    def add_module(self, module_name: str, module: Module) -> None:
        self._modules[module_name] = module

    def get_module_names(self) -> Set[str]:
        """
        :return: names of all modules that are currently active in the model
        :rtype: Set[str]
        """
        return self._modules.keys()

    def switch_events(self, events_to_remove: Set[str], events_to_add: Dict[str, GestureEvent]) -> None:
        """ 
        First removes the specified events from the model and adds new ones in afterwards.
        Removing an event may also lead to removing of some gestures that are no longer used by any events in the model.
        If all gestures from one module get removed so does the module.

        :param events_to_remove: names of the events to remove
        :type events_to_remove: Set[str]
        :param events_to_add: names of the events to add mapped to the event instances
        :type events_to_add: Dict[str, GestureEvent]
        """
        for event_name in events_to_remove:
            self._remove_event(event_name)

        for event_name, event in events_to_add.items():
            event.set_up()
            self._add_event(event_name, event)

        gestures_used = list(self._gesture_to_events.keys())
        for gesture_name in gestures_used:
            # if the gesture now has no events depending on it we also remove the gesture
            if len(self._gesture_to_events[gesture_name]) == 0:
                self.remove_gesture(gesture_name)

    def _add_event(self, event_name: str, event: GestureEvent) -> None:
        """
        Adds a new event to the model. Events can be added during the runtime of the model (aka between frames).

        :param event_name: name of the event to add
        :type event_name: str
        :param event: event to add
        :type event: GestureEvent
        :raises RuntimeError: if the event (same name) is already in the model
        """
        if event_name in self._events:
            raise RuntimeError(
                "attempt to add an event to the module that has already been added: " + event_name)
        self._events[event_name] = event
        for gesture_name in event.get_all_used_gestures():
            if gesture_name not in self._gesture_to_events:
                self._gesture_to_events[gesture_name] = set()
            self._gesture_to_events[gesture_name].add(event)
        # need to update the event state as it is possible that the required gestures are already active
        for gesture in self._active_gestures:
            event.notify_gesture_activated(gesture)
        self._update_event_state(event)

    def _remove_event(self, event_name: str) -> None:
        """
        Remove an event from the model. Events can be removed during the runtime of the model (aka between frames).

        :param event_name: name of the event to remove from the model
        :type event_name: str
        :raises RuntimeError: if the model does not have this event
        """
        if event_name not in self._events:
            raise RuntimeError(
                "attempt to remove an event to the module that has not been added: " + event_name)

        event = self._events[event_name]
        self._events.pop(event_name)

        event.force_deactivate()

        if event in self._active_events:
            self._active_events.remove(event)

        # remove the mapping to the event from any of the gestures
        for gesture_name in event.get_all_used_gestures():
            self._gesture_to_events[gesture_name].remove(event)

    def add_gesture(self, module_name: str, gesture_name: str, primitives: Set[Primitive]) -> None:
        """
        Add a gesture to the given module. If the gesture is already in the module then nothing is done. (this means that if there is an attempt to add a new gesture by the same name as a previous one, it will be ignored)

        :param module_name: module to which to add the gesture to
        :type module_name: str
        :param gesture_name: name of the gesture to be added
        :type gesture_name: str
        :param primitives: primitives that describe the gesture
        :type primitives: Set[Primitive]
        :raises RuntimeError: if the module we are trying to add the gesture to is not in the model
        """
        if module_name not in self._modules:  # if the model for which we are adding gestures was not added. 
            raise RuntimeError(
                module_name, " module not found. Attempt to add a gesture ", gesture_name, " to invalid module")

        if gesture_name not in self._gesture_to_module:  # add only if it was not previously added
            self._modules[module_name].add_gesture(gesture_name, primitives)
            self._gesture_to_module[gesture_name] = module_name

    def remove_gesture(self, gesture_name: str) -> None:
        """
        Simply removes the gesture from the model so that no new instances of this gesture will be created.
        Any currently active instances of this gesture will not be deactivated (are expected to deactivate naturally)
        Does not check if any events were using it so removing a gesture in use may lead to an event that cant be activated

        :param gesture_name: name of the gesture to remove
        :type gesture_name: str
        :raises RuntimeError: if a gesture with the given name has not been added to the model
        """
        # simply removes the gesture and does not check if some events were still using it
        # if the gesture was previously active we do not remove it from active gestures. Simply no new instances will be created
        if gesture_name not in self._gesture_to_module:
            raise RuntimeError(
                "Attempt to remove a gesture that has not been added to the Module: " + gesture_name)

        module_name = self._gesture_to_module[gesture_name]
        module = self._modules[module_name]
        module.remove_gesture(gesture_name)

        if len(module.get_currently_used_primitives()) == 0:
            self._modules.pop(module_name)

        self._gesture_to_module.pop(gesture_name)
        self._gesture_to_events.pop(gesture_name)

    def process_frame(self, frame: np.ndarray) -> RawData:
        """
        Process the frame in following steps:
            - Process the frame in each module, from which we obtain the frames raw data and new Gesture instances may be created.
            - Activate in the model each Gesture that was created from the modules, which may (de)activate of some gesture events
            - Update all the currently active gestures, which may result in deactivation of some of them, 
              and consequently (de)activation of some gesture events
            - Run all active gesture events, which may result in the trigger functions in the events being called.

        :param frame: image reflecting the frame
        :type frame: ndarray
        :return: Coordinates of all the landmarks detected in the frame
        :rtype: RawData
        """

        frame_data = RawData()
        self._update_modules(frame_data, frame)
        self._update_active_gestures()
        self._update_active_events()
        return frame_data

    def _update_modules(self, frame_data: RawData, frame: np.ndarray) -> None:
        new_gestures = set()

        modules = list(self._modules.values())
        if len(modules) == 1:  # no need for threads if only 1 module is active
            self._update_module(modules[0], new_gestures, frame_data, frame)
        else:
            self._thread_updating_modules(new_gestures, frame_data, frame)

        for gesture in new_gestures:
            self._activate_gesture(gesture)

    def _thread_updating_modules(self, new_gestures: Set[Gesture], frame_data: RawData, frame: np.ndarray) -> None:
        all_threads = []
        all_frame_datas = []
        all_new_gestures = []

        for module in self._modules.values():
            module_frame_data = RawData()
            all_frame_datas.append(module_frame_data)

            module_new_gestures = set()
            all_new_gestures.append(module_new_gestures)

            # Debugging
            #if random.random() > 0.8:
            #print("MODULE: ", module)
            name = f"Thread Model: {module}"
            module_thread = threading.Thread(target=self._update_module, name=name, args=(
                module, module_new_gestures, module_frame_data, np.copy(frame)))
            all_threads.append(module_thread)

            module_thread.start()
            
        for module_thread in all_threads:
            module_thread.join()

        for gestures in all_new_gestures:
            new_gestures.update(gestures)

        for datas in all_frame_datas:
            frame_data.combine(datas)

    def _update_module(self, module: Module, new_gestures: Set[Gesture], module_frame_data: RawData,
                       frame: np.ndarray) -> None:
        new_gestures.update(
            module.update_and_get_activated_gestures(module_frame_data, frame))

    def _update_active_gestures(self) -> None:
        gestures_to_deactivate = set()
        for gesture in self._active_gestures:
            if not gesture.update():  # if no longer active
                gestures_to_deactivate.add(gesture)

        for gesture in gestures_to_deactivate:
            self._deactivate_gesture(gesture)

    def _update_active_events(self) -> None:
        events_to_deactivate = set()
        for event in self._active_events:
            event.update()
            if not event.get_state():
                events_to_deactivate.add(event)

        for event in events_to_deactivate:
            self._active_events.remove(event)

    def _activate_gesture(self, gesture: Gesture) -> None:
        self._active_gestures.add(gesture)
        # notify Events
        if gesture.get_name() in self._gesture_to_events:
            for event in self._gesture_to_events[gesture.get_name()]:
                event.notify_gesture_activated(gesture)
                self._update_event_state(event)

    def _deactivate_gesture(self, gesture: Gesture) -> None:
        self._active_gestures.remove(gesture)
        # notify events
        if gesture.get_name() in self._gesture_to_events:
            for event in self._gesture_to_events[gesture.get_name()]:
                event.notify_gesture_deactivated(gesture)
                self._update_event_state(event)

    def _update_event_state(self, event: GestureEvent) -> None:
        if event.get_state():
            self._active_events.add(event)
        else:
            if event in self._active_events:
                self._active_events.remove(event)

    def get_activate_events(self) -> Set:
        return self._active_events
