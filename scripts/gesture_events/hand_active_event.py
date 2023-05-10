'''
Author: Carmen Meinson
'''
from .simple_gesture_event import SimpleGestureEvent


# while the hand is active we update the location of the cursor
class HandActiveEvent(SimpleGestureEvent):
    """Each frame the facing_camera gesture is active, the 'move' trigger is called with the coordinates of the palm center
    
    [trigger types]:
        "move": called every frame when the event is active (so when the hand is facing the camera) with input of (palm_center_x_coordinate, palm_center_y_coordinate). coordinates in percentage of the camera view relative to the left top corner
    [bodypart types]:
        "hand": which hands movement is tracked
    [gestures types]:
        "facing_camera": 
    """
    _event_trigger_types = {"move"}
    _gesture_types = {"facing_camera"}
    _bodypart_types = {"hand"}

    def __init__(self):
        self._gestures = {"hand": {"facing_camera": None}}
        super().__init__(HandActiveEvent._gesture_types, HandActiveEvent._event_trigger_types,
                         HandActiveEvent._bodypart_types)

    def update(self):
        hand_position = self._gestures["hand"]["facing_camera"].get_last_position()
        palm_center = hand_position.get_landmark("palm_center")
        self._event_triggers["move"](palm_center[0], palm_center[1])

    def _check_state(self) -> None:
        self._state = self._gestures["hand"]["facing_camera"] is not None
