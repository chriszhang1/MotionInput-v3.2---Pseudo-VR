'''
Author: Carmen Meinson
'''
from typing import Dict
from .simple_gesture_event import SimpleGestureEvent


class GesturesActiveEvent(SimpleGestureEvent):
    """Calls the 'active' trigger once all the specified gestures have been in the specified states for the given nr of frames

    [trigger types]:
        "active": called when all the specified gestures have been in the specified states for the given nr of frames
    [bodypart types]:
        retrieved from the desired_gesture_states 
    [gestures types]:
        retrieved from the desired_gesture_states 
    """
    _event_trigger_types = {"active"}

    def __init__(self, desired_gesture_states: Dict[str, Dict[str, bool]], frames_nr=1):
        """
        :param desired_gesture_states: all events of interest in form {"bodypart_type":{"gesture_type":desired_state, ...}, ...}
        :type desired_gesture_states: Dict[str,Dict[str, bool]]
        :param frames_nr: the number of frames the event needs to be active before the trigger func is called, defaults to 1
        :type frames_nr: int, optional
        """
        self._desired_gesture_states = desired_gesture_states
        self._gestures = {}
        gesture_types = set()
        bodypart_types = desired_gesture_states.keys()
        for bodypart, bodypart_gestures in desired_gesture_states.items():
            self._gestures[bodypart] = {}
            for gesture_type in bodypart_gestures.keys():
                self._gestures[bodypart][gesture_type] = None
                gesture_types.add(gesture_type)

        super().__init__(gesture_types, GesturesActiveEvent._event_trigger_types, bodypart_types)
        self._n_frames_for_switch = frames_nr
        # TODO: alterantive to giving the frames nr as a parameter(this does not allow us to change it on runtime) is to specify the setting name that needs to be retrieved from the Config 

    def update(self):
        if self._get_frames_held() == self._n_frames_for_switch:
            self._event_triggers["active"]()

    def _check_state(self):
        self._state = True
        for bodypart, bodypart_gestures in self._gestures.items():
            for gesture_type, gesture in bodypart_gestures.items():
                if (gesture is not None) != (self._desired_gesture_states[bodypart][gesture_type]):
                    self._state = False

    def _get_frames_held(self) -> int:
        gestures_frames_held = []
        for bodypart_gestures in self._gestures.values():
            for gesture in bodypart_gestures.values():
                gestures_frames_held.append(gesture.get_frames_held())

        return min(gestures_frames_held)
