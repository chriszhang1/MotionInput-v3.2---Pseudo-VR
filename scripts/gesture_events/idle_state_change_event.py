'''
Author: Carmen Meinson
'''
from scripts.tools import Config
from .simple_gesture_event import SimpleGestureEvent


class IdleStateChangeEvent(SimpleGestureEvent):
    """Switching between the idle(hand resting or not facing the camera) and active hand states.

    [trigger types]:
        "idle": called when currently_idle is False and the state of the hand has been idle for frames_for_switch frames
        "active": called when currently_idle is True and the state of the hand has been active for frames_for_switch frames
    [bodypart types]:
        "hand": the hand on which we track the gesture of interest
    [gestures types]:
        "facing_camera": the hand is considered idle when the gesture is inactive
    """
    _event_trigger_types = {"idle", "active"}
    _gesture_types = {"facing_camera"}
    _bodypart_types = {"hand"}

    def __init__(self, currently_idle=False):
        self._gestures = {"hand": {"facing_camera": None}}
        super().__init__(IdleStateChangeEvent._gesture_types, IdleStateChangeEvent._event_trigger_types,
                         IdleStateChangeEvent._bodypart_types)
        config = Config()
        self._n_frames_for_switch = config.get_data("events/idle_state_change/frames_for_switch")
        self._frame_count = 0
        self._currently_idle = currently_idle

    def update(self):
        # self._check_state()
        if not self._state:
            self._frame_count = 0
            return

        self._frame_count += 1
        if self._frame_count == self._n_frames_for_switch:
            if self._currently_idle:
                self._event_triggers["active"]()
            else:
                self._event_triggers["idle"]()
            self._state = False
            self._frame_count = 0
            # self._currently_idle = not self._currently_idle not needed cause for each #currently state we have a separate model aka separate event instance

    def _check_state(self) -> None:
        # Conditions for idleness: if any of these are met, the state is idle. If not, the state is active.
        # Condition 1: The hand is turned around so the palm is facing inward i.e. not outwards towards the camera.
        # Condition 2: The hand is closed / resting so that the tip of the index finger is below the tip of the thumb.
        position_is_idle = (self._gestures["hand"]["facing_camera"] is None)
        # the state of the event is true only if the current position of the hand could possibly change the state
        self._state = self._currently_idle != position_is_idle
