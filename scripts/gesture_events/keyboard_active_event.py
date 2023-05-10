'''
Author: Siam Islam
'''

from scripts.tools.config import Config
from .simple_gesture_event import SimpleGestureEvent

class KeyboardActiveEvent(SimpleGestureEvent):
    """Every frame this event is active, the "move" trigger is called, passing in the landmarks specified in config, 
    for each active hand in the frame. A hand is considered "active" when it is facing the camera, 
    i.e. when the gesture "facing_camera" for that hand is available.
    
    [trigger types]:
        "move": called every frame as long as this event is active
        "clear": called in the event force_deactivate function to remove the in air keyboard display from the view
    [bodypart types]:
        "dom_hand": the dominant hand being tracked
        "off_hand": the off hand being tracked
    [gestures types]:
        "facing_camera": active when the specified hand is facing the camera
    """

    _event_trigger_types = {"move", "clear"}
    _gesture_types = {"facing_camera"}
    _bodypart_types = {"dom_hand", "off_hand"}

    def __init__(self):
        self._gestures = {hand: {"facing_camera": None} for hand in self._bodypart_types}
        landmarks = Config().get_data("events/keyboard/landmarks")
        landmarks = [landmark + "_tip" for landmark in landmarks]
        self._required_landmarks = {hand: landmarks for hand in self._bodypart_types}
        super().__init__(KeyboardActiveEvent._gesture_types, KeyboardActiveEvent._event_trigger_types, KeyboardActiveEvent._bodypart_types)

    def update(self):
        landmarks = self.get_landmarks()
        self._event_triggers["move"](landmarks)

    def get_landmarks(self):
        active_landmarks = {}
        for hand, landmarks in self._required_landmarks.items():
            if self._gestures[hand]["facing_camera"]:
                active_landmarks[hand] = set()
                for landmark in landmarks:
                    hand_position = self._gestures[hand]["facing_camera"].get_last_position()
                    landmark_coords = hand_position.get_landmark(landmark)
                    active_landmarks[hand].add((landmark_coords[0], landmark_coords[1], landmark))
        return active_landmarks

    def _check_state(self) -> None:
        self._state = True    # Keyboard should be active until user does gesture to switch to another mode
    
    def force_deactivate(self) -> None:
        self._event_triggers["clear"]()