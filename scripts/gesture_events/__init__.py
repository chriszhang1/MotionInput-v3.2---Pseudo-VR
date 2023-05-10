"""
Author: Carmen Meinson
"""
from scripts.gesture_events.extremity_walking_event import (
    ExtremityWalkingEvent,
)
from scripts.gesture_events.eye_mode_2 import EyeMode2Event
from scripts.gesture_events.pseudovr_event import PseudoVRMode1Event, PseudoVRMode2Event, PseudoVRMode3Event
from scripts.gesture_events.gamepad_event import GamepadMode1Event, GamepadMode2Event, GamepadMode3Event
from .boundaries_nose_box_event import BoundariesNoseBoxEvent
from .click_press_event import (
    ClickPressEvent,
    SingleHandExclusiveClickPressEvent
)
# hand
from .hand_active_event import HandActiveEvent
from .hand_depth_click_event import HandDepthClickEvent
from .palm_height_change_event import PalmHeightChangeEvent
from .customized_gesture_event import CustomizedGestureEvent
from .gestures_active_event import GesturesActiveEvent
from .scroll_event import ScrollEvent
from .touch_press_event import TouchPressEvent
from .zoom_event import ZoomEvent
from .pen_drag_event import PenDragEvent
from.hand_drive_event import HandDriveRotateEvent, HandDriveForwardBackwardEvent, HandDriveUpDownEvent
from .mr_swipe_event import MRSwipeEvent
from .samurai_swipe_event import SamuraiSwipeEvent
from .spiderman_thwip import SpidermanThwipEvent
# body
from .exercise_event import ExerciseEvent
from .extremity_trigger_event import ExtremityTriggerEvent
from .gun_move_event import GunMoveEvent
from .idle_state_change_event import IdleStateChangeEvent
from .joystick_event import JoystickButtonPressEvent, JoystickWristEvent
from .keyboard_active_event import KeyboardActiveEvent
from .keyboard_click_event import KeyboardClickEvent
# head
from .head_gesture_trigger_event import (
    OpenMouthEvent,
    RaiseEyeBrowEvent,
    SmilingEvent,
    FishFaceEvent,
    TurnLeftEvent,
    TurnRightEvent,
    TiltLeftEvent,
    TiltRightEvent
)
from .move_nose_box_event import MoveNoseBoxEvent
from .nose_direction_tracking_event import NoseDirectionTrackingEvent
from .nose_direction_tracking_event_nose_box import \
    NoseDirectionTrackingEventNoseBox
from .nose_scroll_event import NoseScrollEvent
from .nose_tracking_event import NoseTrackingEvent
from .nose_zoom_event import NoseZoomEvent
from .eye_tracking_event import EyeTrackingEvent
# speech
from .speech_event import SpeechEvent

# this should store every available handler
events = {
    "ClickPressEvent": ClickPressEvent,
    "SingleHandExclusiveClickPressEvent": SingleHandExclusiveClickPressEvent,
    "TouchPressEvent": TouchPressEvent,
    "KeyboardActiveEvent": KeyboardActiveEvent,
    "KeyboardClickEvent": KeyboardClickEvent,
    "PalmHeightChangeEvent": PalmHeightChangeEvent,
    "IdleStateChangeEvent": IdleStateChangeEvent,
    "HandActiveEvent": HandActiveEvent,
    "HandDepthClickEvent": HandDepthClickEvent,
    "ScrollEvent": ScrollEvent,
    "ExtremityTriggerEvent": ExtremityTriggerEvent,
    "ZoomEvent": ZoomEvent,
    "ExerciseEvent": ExerciseEvent,
    "ExtremityWalkingEvent": ExtremityWalkingEvent,
    "GamepadMode1Event": GamepadMode1Event,
    "GamepadMode2Event": GamepadMode2Event,
    "GamepadMode3Event": GamepadMode3Event,
    "PseudoVRMode1Event": PseudoVRMode1Event,
    "PseudoVRMode2Event": PseudoVRMode2Event,
    "PseudoVRMode3Event": PseudoVRMode3Event,
    "SpeechEvent": SpeechEvent,
    "SmilingEvent": SmilingEvent,
    "FishFaceEvent": FishFaceEvent,
    "TurnLeftEvent": TurnLeftEvent,
    "TurnRightEvent": TurnRightEvent,
    "TiltLeftEvent": TiltLeftEvent,
    "TiltRightEvent": TiltRightEvent,
    "NoseTrackingEvent": NoseTrackingEvent,
    "NoseDirectionTrackingEvent": NoseDirectionTrackingEvent,
    "OpenMouthEvent": OpenMouthEvent,
    "RaiseEyeBrowEvent": RaiseEyeBrowEvent,
    "GesturesActiveEvent": GesturesActiveEvent,
    "PenDragEvent": PenDragEvent,
    "EyeTrackingEvent": EyeTrackingEvent,
    "EyeMode2Event": EyeMode2Event,
    "NoseDirectionTrackingEventNoseBox": NoseDirectionTrackingEventNoseBox,
    "MoveNoseBoxEvent": MoveNoseBoxEvent,
    "BoundariesNoseBoxEvent": BoundariesNoseBoxEvent,
    "NoseScrollEvent": NoseScrollEvent,
    "NoseZoomEvent": NoseZoomEvent,
    "JoystickButtonPressEvent": JoystickButtonPressEvent,
    "JoystickWristEvent": JoystickWristEvent,
    "CustomizedGestureEvent": CustomizedGestureEvent,
    "GunMoveEvent": GunMoveEvent,
    "HandDriveRotateEvent": HandDriveRotateEvent,
    "HandDriveForwardBackwardEvent": HandDriveForwardBackwardEvent,
    "HandDriveUpDownEvent": HandDriveUpDownEvent,
    "MRSwipeEvent": MRSwipeEvent,
    "SamuraiSwipeEvent": SamuraiSwipeEvent,
    "SpidermanThwipEvent": SpidermanThwipEvent
}


class GestureEvents:
    @staticmethod
    def get_event(name: str):
        if name not in events:
            raise RuntimeError("Attempt to get an undefined event :", name)
        return events[name]
