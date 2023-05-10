'''
Author: Carmen Meinson
'''

from typing import Dict, Callable, Set

from .gesture import Gesture


# consists of one or multiple gestures that the activation of the triggers depends on
# eg. "rabbit" gesture and the time it has been held or the angle of the wrist

# initialized outside of the model
class GestureEvent:
    def __init__(self, gesture_types: Set[str], event_trigger_types: Set[str], bodypart_types: Set[str]):
        self._gesture_types = gesture_types
        self._event_trigger_types = event_trigger_types
        self._bodypart_types = bodypart_types

    def set_trigger_functions(self, funcs: Dict[str, Callable]) -> None:
        raise NotImplementedError()

    def set_bodypart_names(self, bodypart_names) -> None:
        raise NotImplementedError()

    def set_up(self) -> None:
        """Called right after the event is added to the model - so after the trigger functions and bodypart names have been set.
        The method could be used to for example set up the display elements.
        """
        pass

    def update(self) -> None:
        """Checks the event firing conditions and then may call according trigger functions.
        (the function is expected to be called each frame until the state of the GestureEvent becomes False)"""
        raise NotImplementedError()

    def get_state(self) -> bool:
        raise NotImplementedError()

    def force_deactivate(self) -> None:
        """
        As some events need to finish some processing before being deactivated, they can implement this method.
        It is called when the events are removed from the model.
        (e.g. for example if an event has called the mouse press function it needs to release the mouse before deactivation)
        """
        pass

    def notify_gesture_activated(self, gesture: Gesture) -> None:  # TODO: maybe join the 2 notify functions into 1 as often similar
        """Notifies that a new gesture of the same type that is used by the GestureEvent has activated.
        If the activated gesture has the correct body part name and gesture type combination, it is stored in the GestureEvent instance. The state of the GestureEvent is then checked in case the activation of the gesture changed it.

        :param gesture: the gesture that activated
        :type gesture: Gesture
        """
        raise NotImplementedError()

    def notify_gesture_deactivated(self, gesture: Gesture) -> None:
        """Notifies that a new gesture of the same type that is used by the GestureEvent has deactivated.
        If the deactivated gesture was previously stored in the GestureEvent instance it is now removed (although there may be cases where it is kept to perform calculations later). The state of the GestureEvent is then checked in case the deactivation of the gesture changed it.

        :param gesture: the gesture that deactivated
        :type gesture: Gesture
        """
        # if later needed it could still keep the gesture instance
        raise NotImplementedError()

    def get_all_used_gestures(self) -> Set[str]:
        return self._gesture_types

    def get_event_trigger_types(self) -> Set[str]:
        return self._event_trigger_types

    def get_bodypart_types(self) -> Set[str]:
        return self._bodypart_types
