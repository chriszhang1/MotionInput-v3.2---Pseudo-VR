'''
Author: Carmen Meinson
'''

from typing import Any, Optional, Set

import numpy as np

from scripts.core.position import Position
from .gesture import Gesture
from .gesture_factory import GestureFactory, Primitive
from .position_tracker import PositionTracker
from .raw_data import RawData


class LandmarkDetector:
    """Interface for each modules landmark detector"""

    def __init__(self):
        raise NotImplementedError()

    def get_raw_data(self, raw_data: RawData, image: np.ndarray) -> None:
        """Adds the xy(z) coordinates of all the landmarks detected on the image into the RawData instance.

        :param raw_data: RawData instance to add the landmarks to
        :type raw_data: RawData
        :param image: Image to process with mediapipe and read the landmarks locations from
        :type image: ndarray
        """
        raise NotImplementedError()


class Module:
    _position_class = Position  # e.g. HandPosition
    _gesture_class = Gesture  # e.g. HandGesture
    _landmark_detector_class = LandmarkDetector  # e.g. HandLandmarkDetector

    _tracker_names = set()  # names of the trackers from the specific landmark detector e.g. {"Left", "Right"}

    _pre_initialized = False

    def __init__(self) -> None:
        self.pre_initialize()
        self._primitive_to_gesture_factories = {}  # dict: name of the primitive -> gesture factory instances that use it / can be expanded on runtime
        self._gesture_name_to_factory = {}  # dict: name of the gesture -> the gestures factory
        self._position_trackers = {name: PositionTracker(name, self._position_class) for name in
                                   self._tracker_names}  # dict: name of the tracker -> tracker instance / can be expanded or decreased on runtime
        self._landmark_detector = self._landmark_detector_class()
        self._active = False

    def update_and_get_activated_gestures(self, frame_data: RawData, image: np.ndarray) -> Set[Gesture]:
        """ 
        - Use the modules landmark detector (ML library) to retrieve the RawData (aka the coordinates of all landmarks) from the frame.
        - Update all position trackers with the RawData, which results in a set of primitives that had changed since the last frame.
        - Update all the gesture factories that use the changed primitives, which may create new active Gestures.

        :param frame_data: RawData instance to store the detected landmarks in
        :type frame_data: RawData
        :param image: frame
        :type image: ndarray
        :return: set of the new Gestures that were created
        :rtype: Set[Gesture]
        """
        if not self._active:
            return set()
        self._landmark_detector.get_raw_data(frame_data, image)
        return self._update_trackers_and_factories(frame_data)

    def add_gesture(self, gesture_name: str, primitives: Set[Primitive]) -> None:
        """Adds a new available gesture to the module.

        :param gesture_name: name of the gesture to be added
        :type gesture_name: str
        :param primitives: primitives that describe the gesture
        :type primitives: Set[Primitive]
        """
        self._active = True
        factory = GestureFactory(gesture_name, self._gesture_class, primitives)
        self._gesture_name_to_factory[gesture_name] = factory
        # detect what gesture factories are using what primitives
        for primitive in primitives:
            if primitive.name not in self._primitive_to_gesture_factories:
                self._primitive_to_gesture_factories[primitive.name] = set()
            self._primitive_to_gesture_factories[primitive.name].add(factory)

    def remove_gesture(self, gesture_name: str) -> None:
        """Remove the gesture from the module. 
        May lead to removal of some primitives (if the primitive is not used by any gestures anymore)

        :param gesture_name: name of the gesture to remove
        :type gesture_name: str
        """
        factory_to_remove = self._gesture_name_to_factory[gesture_name]
        self._gesture_name_to_factory.pop(gesture_name)

        primitves_to_remove = set()
        for primitive_name, factories in self._primitive_to_gesture_factories.items():
            # remove the instance of the gesture factory
            if factory_to_remove in factories:
                self._primitive_to_gesture_factories[primitive_name].remove(factory_to_remove)
                # if the primitive now has no gestures depending on it we also remove the primitive
                if len(self._primitive_to_gesture_factories[primitive_name]) == 0:
                    primitves_to_remove.add(primitive_name)

        for primitive_name in primitves_to_remove:
            self._primitive_to_gesture_factories.pop(primitive_name)

        if len(self._primitive_to_gesture_factories) == 0:
            self.reset()
            self._active = False

    def get_currently_used_primitives(self) -> Set[str]:
        """Get names of all primitives that are used by any of the available gestures.

        :return: names of currently used primitives
        :rtype: Set[str]
        """
        return set(self._primitive_to_gesture_factories.keys()).copy()

    def reset(self) -> None:
        """Resets all position trackers"""
        for name, tracker in self._position_trackers.items():
            tracker.reset()

    @classmethod
    def calibrate(self, params: Optional[Any] = None) -> None:
        # if needed the specific modules can cal the calibration
        # TODO: should we keep calibration within the modules or perhaps all calibration separate?
        pass

    @classmethod
    def pre_initialize(cls) -> None:
        """Can be called to perform all of the time consuming setup of the Module before initialization.
        If is not called then all the setup is done when the Module is first initialized. 
        """        
        if cls._pre_initialized: return
        cls._do_pre_initialization()
        cls._pre_initialized = True

    @classmethod
    def _do_pre_initialization(cls) -> None:
        # all the time consuming setup required for each module should be implemented here.
        pass

    def _update_trackers_and_factories(self, raw_data: RawData) -> Set[Gesture]:
        # update the position based on raw data aka coordinates
        new_gestures = set()
        for name, tracker in self._position_trackers.items():
            used_primitives = self.get_currently_used_primitives()
            changed_primitives = tracker.update(raw_data, used_primitives)
            # update factories
            gest_factories_to_update = self._get_factories_to_update(changed_primitives)
            # update the needed gesture factories
            for gest_factory in gest_factories_to_update:
                new_gesture = gest_factory.update(tracker)
                if new_gesture is not None:  # if new gesture instance created
                    new_gestures.add(new_gesture)
        return new_gestures

    def _get_factories_to_update(self, changed_primitives: Set[str]) -> Set[GestureFactory]:
        gest_factories_to_update = set()
        for prim_name in changed_primitives:
            if prim_name in self._primitive_to_gesture_factories:  # if primitive used by any gestures
                gest_factories_for_prim = self._primitive_to_gesture_factories[prim_name]
                gest_factories_to_update = gest_factories_to_update.union(gest_factories_for_prim)
        return gest_factories_to_update
