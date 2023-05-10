'''
Authors: Carmen Meinson
Contributors: Andrzej Szablewski, Alexandros Theofanous, Anelia Gaydardzhieva
'''

from typing import Callable

from scripts.gesture_event_handlers.exercise_display import ExerciseDisplay
from scripts.gesture_event_handlers.extremity_circles import ExtremityCircles
from scripts.gesture_event_handlers.extremity_walking import ExtremityWalkingActions
from scripts.gesture_event_handlers.pseudovr_actions import PseudoVRActions
from scripts.gesture_event_handlers.gamepad_actions import GamepadActions
from scripts.gesture_event_handlers.monitor_tracker import MonitorTracker
from .area_of_interest import AreaOfInterest
from .correction_mode import CorrectionMode
from .desktop_mouse import AOIMouse, DesktopMouse
from .desktop_pen import DesktopPenInput
from .desktop_touch import DesktopTouch
from .edit_config import EditConfigFile
from .exercise_actions import ExerciseActions
from .extremity_actions import ExtremityActions
from .in_air_keyboard import InAirKeyboard
from .keyboard import Keyboard
from .nose_box import NoseBox
from .speaker_identification import SpeakerIdentification
from .transcription import Transcriber

try:
    from .gaming_joystick import GamingJoystick
except:
    print("ViGEmBus is not installed on machine") # required only if joypad mode is enabled


# this should store every available handler
from scripts.gesture_events.customized_gesture_event import CustomizedGestureEvent


class GestureEventHandlers:
    def __init__(self, mode_change_method: Callable, view):
        self._view = view
        self._mode_change_method = mode_change_method

        self._aoi = None
        self._monitor_tracker = None
        self._aoi_mouse = None
        self._mouse = None
        self._touch = None
        self._pen = None
        self._in_air_keyboard = None
        self._keyboard = None
        self._exercise_display = None
        self._extremity_circles = None
        self._extremity_actions = None
        self._exercise_actions = None
        self._nose_box = None
        self._extremity_walking_actions = None
        self._gamepad_actions = None
        self._pseudovr_actions = None
        self._edit_config = None
        self._gaming_joystick = None
        self._transcriber = None # speech
        self._correction_mode = None # speech
        self._speaker_identification = None # speech


        # names of all the handler classes that are available, mapped to functions below that contain all the functions
        # within each specific class that are available
        self._handlers = {
            "ModeChange": self._get_mode_change_func,
            "IterativeModeChange": self._get_mode_iterative_change_func,
            "DesktopMouse": self._get_desktop_mouse_func,
            "AOIMouse": self._get_aoi_mouse_func,
            "DesktopTouch": self._get_desktop_touch_func,
            "DesktopPenInput": self._get_desktop_pen_func,
            "Keyboard": self._get_keyboard_func,
            "InAirKeyboard": self._get_in_air_keyboard_func,
            "AreaOfInterest": self._get_aoi_func,
            "MonitorTracker": self._get_monitor_tracker_func,
            "ExtremityActions": self._get_extremity_actions_func,
            "ExerciseActions": self._get_exercise_actions_func,
            "NoseBox": self._get_nose_box_func,
            "Transcriber": self._get_transcribe_func, # speech
            "CorrectionMode":self._get_correction_mode_func, # speech
            "SpeakerIdentification":self._get_speaker_identification_func, # speech
            "EditConfigFile": self._get_config_editor_func,
            "ExtremityWalkingActions": self._get_extremity_walking_actions_func,
            "GamepadActions": self._get_gamepad_actions_func,
            "GamingJoystick": self._get_gaming_joystick_func,
            "PseudoVRActions": self._get_pseudovr_actions_func,
            "CustomizeGestureNotification": self._get_customize_gesture_notification_func
        }

    def get_handler_func(self, handler_name: str, function_name: str):
        if handler_name not in self._handlers:
            raise RuntimeError("Attempt to get an undefined event handler:", handler_name)

        return self._handlers[handler_name](function_name)

    def _get_mode_change_func(self, mode: str):
        return lambda: self._mode_change_method(mode)

    def _get_mode_iterative_change_func(self, _: str):
        return self._mode_change_method

# -------------------------------------------------------------------------------------------
# CustomizedGestureEvent
    def _get_customize_gesture_notification_func(self, name):
        funcs = {
            "notify_audio_flag": CustomizedGestureEvent.notify_audio_flag
        }
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from CustomizedGestureEvent")
        return funcs[name]

# -------------------------------------------------------------------------------------------
# Desktop Mouse
    def _get_desktop_mouse_func(self, name: str):
        self._check_mouse_initialized()
        funcs = {
            "move_cursor": self._mouse.move_cursor,
            "move_cursor_relative": self._mouse.move_cursor_relative,
            "left_click": self._mouse.left_click,
            "left_press": self._mouse.left_press,
            "left_release": self._mouse.left_release,
            "right_click": self._mouse.right_click,
            "right_press": self._mouse.right_press,
            "right_release": self._mouse.right_release,
            "double_click": self._mouse.double_click,
            "scroll": self._mouse.scroll,
            "zoom": self._mouse.zoom}
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from DesktopMouse")
        return funcs[name]

    def _check_mouse_initialized(self):
        if self._mouse is None:
            self._check_monitor_tracker_initialized()
            self._mouse = DesktopMouse(self._monitor_tracker)
# -------------------------------------------------------------------------------------------
# AOI Mouse
    def _get_aoi_mouse_func(self, name: str):
        self._check_aoi_mouse_initialized()
        funcs = {
            "move_cursor": self._aoi_mouse.move_cursor,
            "move_cursor_relative": self._aoi_mouse.move_cursor_relative,
            "left_click": self._aoi_mouse.left_click,
            "left_press": self._aoi_mouse.left_press,
            "left_release": self._aoi_mouse.left_release,
            "right_click": self._aoi_mouse.right_click,
            "right_press": self._aoi_mouse.right_press,
            "right_release": self._aoi_mouse.right_release,
            "double_click": self._aoi_mouse.double_click,
            "scroll": self._aoi_mouse.scroll,
            "zoom": self._aoi_mouse.zoom}
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from AOIMouse")
        return funcs[name]

    def _check_aoi_mouse_initialized(self):
        if self._aoi_mouse is None:
            self._check_aoi_initialized()
            self._aoi_mouse = AOIMouse(self._aoi)

# -------------------------------------------------------------------------------------------
# Monitor Tracker
    def _get_monitor_tracker_func(self, name: str):
        self._check_monitor_tracker_initialized()
        funcs = {
            "change_monitor": self._monitor_tracker.change_monitor,
        }
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from MonitorTracker")
        return funcs[name]

    def _check_monitor_tracker_initialized(self):
        if self._monitor_tracker is None:
            self._monitor_tracker = MonitorTracker()

# -------------------------------------------------------------------------------------------
# Desktop Touch
    def _get_desktop_touch_func(self, name: str):
        self._check_touch_initialized()
        funcs = {
            "move_cursor": self._touch.move_cursor,
            "singletap": self._touch.singletap,
            "tap": self._touch.tap,
            "press": self._touch.press,
            "triple_swipe": self._touch.triple_swipe,
            "release": self._touch.release
            #Not working/ not defined
            #"cont_press": self._touch.cont_press
            }
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from DesktopTouch")
        return funcs[name]

    def _check_touch_initialized(self):
        if self._touch is None:
            self._check_aoi_initialized()
            self._touch = DesktopTouch(self._aoi)

# -------------------------------------------------------------------------------------------
# Desktop Pen
    def _get_desktop_pen_func(self, name: str):
        self._check_pen_initalized()
        funcs = {
            "move_cursor": self._pen.move_cursor,
            "tap": self._pen.tap,
            "press": self._pen.press,
            "release": self._pen.release,
            "update_pressure": self._pen.update_pressure,
            "eraser_activate": self._pen.eraser_activate,
            "eraser_deactivate": self._pen.eraser_deactivate,
            "update_pen": self._pen.update_pen}
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from DesktopPenInput")
        return funcs[name]

    def _check_pen_initalized(self):
        if self._pen is None:
            self._check_aoi_initialized()
            self._pen = DesktopPenInput(self._aoi)
# -------------------------------------------------------------------------------------------
# Keyboard
    def _get_keyboard_func(self, name: str):
        self._check_keyboard_initialized()
        funcs = {
            "up_arrow_press": self._keyboard.up_arrow_press,
            "down_arrow_press": self._keyboard.down_arrow_press,
            "right_arrow_press": self._keyboard.right_arrow_press,
            "left_arrow_press": self._keyboard.left_arrow_press,
            "cut": self._keyboard.cut,
            "copy": self._keyboard.copy,
            #"paste": self._keyboard.paste,
            #"undo": self._keyboard.undo,
            #"print": self._keyboard.print,
            #"save": self._keyboard.save,
            "vs_open_all_windows": self._keyboard.vs_open_all_windows,
            "vs_maximize": self._keyboard.vs_maximize,
            "vs_minimize": self._keyboard.vs_minimize,
            "vs_zoom_in": self._keyboard.vs_zoom_in,
            "vs_zoom_out": self._keyboard.vs_zoom_out,
            "vs_reset_zoom": self._keyboard.vs_reset_zoom,
            "vs_insert_to_editor": self._keyboard.vs_insert_to_editor,
            "vs_copy_to_clipboard": self._keyboard.vs_copy_to_clipboard,
            "switch": self._keyboard.switch,
            "help": self._keyboard.help,
            "settings": self._keyboard.settings,
            "hashtag": self._keyboard.hashtag,
            "windows_key": self._keyboard.windows_key,
            "windows_run": self._keyboard.windows_run,
            "macros": self._keyboard.macros,
            "right_arrow": self._keyboard.right_arrow,
            "left_arrow": self._keyboard.left_arrow,
            "up_arrow": self._keyboard.up_arrow,
            "down_arrow": self._keyboard.down_arrow,
            "escape": self._keyboard.escape,
            "enter": self._keyboard.enter,
            "space": self._keyboard.space,
            "page_up": self._keyboard.page_up,
            "page_down": self._keyboard.page_down,
            "volume_up": self._keyboard.volume_up,
            "volume_down": self._keyboard.volume_down,
            "delete": self._keyboard.delete_press,
            "backspace": self._keyboard.backspace,
            "capital_letters": self._keyboard.capital_letters,
            "hotkey_combination": self._keyboard.hotkey_combination,
            "key_combination": self._keyboard.key_combination,
            "key_down": self._keyboard.key_down,
            "key_up": self._keyboard.key_up,
            "key_press": self._keyboard.key_press,
            "ibm_game_e": self._keyboard.ibm_game_e,
            "ibm_game_q": self._keyboard.ibm_game_q,
            "exit_program_MI": self._keyboard.exit_program_MI
        }
        if name not in funcs:
            try:
                func = getattr(self._keyboard, name)  # WHY WAS THIS NOT ADDED BEFORE HOW MUCH DO I NEED TO HARDCODE
            except AttributeError:
                raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from Keyboard")

            return func

        return funcs[name]

    def _check_keyboard_initialized(self):
        if self._keyboard is None:
            self._keyboard = Keyboard()


# -------------------------------------------------------------------------------------------
# In-Air Keyboard
    def _get_in_air_keyboard_func(self, name: str):
        self._check_in_air_keyboard_initalized()
        funcs = {
            "click": self._in_air_keyboard.click,
            "release": self._in_air_keyboard.release,
            "key_selection": self._in_air_keyboard.key_selection,
            "clear": self._in_air_keyboard.clear_keyboard_keys}

        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from InAirKeyboard")
        return funcs[name]

    def _check_in_air_keyboard_initalized(self):
        if self._in_air_keyboard is None:
            self._check_keyboard_initialized()
            self._check_transcription_initialized()
            self._in_air_keyboard = InAirKeyboard(self._view, self._keyboard, self._transcriber)


# ######################################## BODY MODULE ###################################################
# -------------------------------------------------------------------------------------------
# Extremity Actions
    def _get_extremity_actions_func(self, name: str):
        self._check_extremity_actions_initialized()
        self._extremity_actions.set_extremity_circles()
        funcs = {
            "set_extremity_circles": self._extremity_actions.set_extremity_circles,
            "trigger_action": self._extremity_actions.trigger_action,
            "held_action": self._extremity_actions.held_action,
            "release_action": self._extremity_actions.release_action,
            "clear_extremity_circles": self._extremity_actions.clear_extremity_circles}
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from ExtremityActions")
        return funcs[name]

    def _check_extremity_actions_initialized(self):
        self._check_extremity_circles_initialized()
        if self._extremity_actions is None:
            self._extremity_actions = ExtremityActions(self._extremity_circles)
# -------------------------------------------------------------------------------------------
# Exercise Actions
    def _get_exercise_actions_func(self, name: str):
        self._check_exercise_actions_initialized()
        funcs = {
            "set_exercise_display": self._exercise_actions.set_exercise_display,
            "trigger_action": self._exercise_actions.trigger_action,
            "held_action": self._exercise_actions.held_action,
            "release_action": self._exercise_actions.release_action,
            "clear_exercise_display": self._exercise_actions.clear_exercise_display}
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from ExerciseActions")
        return funcs[name]

    def _check_exercise_actions_initialized(self):
        self._check_exercise_display_initialized()
        if self._exercise_actions is None:
            self._exercise_actions = ExerciseActions(self._exercise_display)
# -------------------------------------------------------------------------------------------
# Extremity Walking Actions
    def _get_extremity_walking_actions_func(self, name: str):
        self._check_extremity_walking_actions_initialized()
        funcs = {
            "set_displays": self._extremity_walking_actions.set_displays,
            "walking_trigger_action": self._extremity_walking_actions.walking_trigger_action,
            "extremity_trigger_action": self._extremity_walking_actions.extremity_trigger_action,
            "held_action": self._extremity_walking_actions.held_action,
            "extremity_release_action": self._extremity_walking_actions.extremity_release_action,
            "walking_release_action": self._extremity_walking_actions.walking_release_action,
            "clear_display": self._extremity_walking_actions.clear_display}
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from ExerciseActions")
        return funcs[name]

    def _check_extremity_walking_actions_initialized(self):
        self._check_exercise_display_initialized()
        self._check_extremity_circles_initialized()
        if self._extremity_walking_actions is None:
            self._extremity_walking_actions = ExtremityWalkingActions(self._exercise_display, self._extremity_circles)
# -------------------------------------------------------------------------------------------
# Gamepad Actions
    def _get_gamepad_actions_func(self, name: str):
        self._check_gamepad_actions_initialized()
        funcs = {
            "set_displays": self._gamepad_actions.set_displays,
            "walking_trigger_action": self._gamepad_actions.walking_trigger_action,
            "extremity_trigger_action": self._gamepad_actions.extremity_trigger_action,
            "held_action": self._gamepad_actions.held_action,
            "extremity_release_action": self._gamepad_actions.extremity_release_action,
            "walking_release_action": self._gamepad_actions.walking_release_action,
            "clear_display": self._gamepad_actions.clear_display}
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from ExerciseActions")
        return funcs[name]

    def _check_gamepad_actions_initialized(self):
        self._check_exercise_display_initialized()
        self._check_extremity_circles_initialized()
        if self._gamepad_actions is None:
            self._gamepad_actions = GamepadActions(self._exercise_display, self._extremity_circles)
# -------------------------------------------------------------------------------------------
# PseudoVR Actions
    def _get_pseudovr_actions_func(self, name: str):
        self._check_pseudovr_actions_initialized()
        funcs = {
            "set_displays": self._pseudovr_actions.set_displays,
            "walking_trigger_action": self._pseudovr_actions.walking_trigger_action,
            "extremity_trigger_action": self._pseudovr_actions.extremity_trigger_action,
            "held_action": self._pseudovr_actions.held_action,
            "extremity_release_action": self._pseudovr_actions.extremity_release_action,
            "walking_release_action": self._pseudovr_actions.walking_release_action,
            "clear_display": self._pseudovr_actions.clear_display}
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from PseudoVRActions")
        return funcs[name]

    def _check_pseudovr_actions_initialized(self):
        self._check_exercise_display_initialized()
        self._check_extremity_circles_initialized()
        if self._pseudovr_actions is None:
            self._pseudovr_actions = PseudoVRActions(self._exercise_display, self._extremity_circles)

    def _check_exercise_display_initialized(self):
        if self._exercise_display is None:
            self._exercise_display = ExerciseDisplay(self._view)

    def _check_extremity_circles_initialized(self):
        if self._extremity_circles is None:
            self._extremity_circles = ExtremityCircles(self._view)

# -------------------------------------------------------------------------------------------
# Gaming Joystick
    def _get_gaming_joystick_func(self, name: str):
        self._check_gaming_joystick_initialised()
        funcs = {
            "press_action": self._gaming_joystick.press_action,
            "release_action": self._gaming_joystick.release_action,
            "joystick_left_move": self._gaming_joystick.joystick_left_move,
            "joystick_right_move": self._gaming_joystick.joystick_right_move,
            "joystick_left_trigger": self._gaming_joystick.joystick_left_trigger,
            "joystick_right_trigger": self._gaming_joystick.joystick_right_trigger}
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from GamingJoystick")
        return funcs[name]

    def _check_gaming_joystick_initialised(self):
        if self._gaming_joystick is None:
            self._gaming_joystick = GamingJoystick()


# ######################################## FACE MODULE ######################################
# -------------------------------------------------------------------------------------------
# EyeEventSwitch
    def _get_config_editor_func(self, name:str):
        self._check_change_config_initialized()
        funcs = {
            "off_eye_gaze": lambda: (   self._edit_config.set_value("handlers/eye_mode_switch/enable", "false"),
                                        self._edit_config.set_value("modules/eye/cons_direction", "" ),
                                        self._edit_config.set_value("handlers/eye_go/enable", "false"),
                                    ),
            "on_eye_gaze": lambda: (    self._edit_config.set_value("handlers/eye_mode_switch/enable","true"),
                            self._edit_config.set_value("handlers/eye_go/enable", "false"),
                        ),
            "on_off_cal": lambda: self._edit_config.switch_boolean("handlers/eye_cal_switch/enable"),
            "on_off_eye_go": lambda: (
                                    self._edit_config.set_value("handlers/eye_go/enable","true"),
                                    self._edit_config.set_value("modules/eye/cons_direction", "")
                                    ),
            "on_off_eye_gaze": lambda: self._edit_config.switch_boolean("handlers/eye_mode_switch/enable")

        }
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from EyeEventSwitch")
        return funcs[name]

    def _check_change_config_initialized(self):
        if self._edit_config is None:
            self._edit_config = EditConfigFile()
# -------------------------------------------------------------------------------------------
# NoseBox
    def _get_nose_box_func(self, name: str):
        self._check_nose_box_initialized()
        funcs = {
            "show_nose_box": self._nose_box.update_nose_box,
            "update_nose_box_centre": self._nose_box.update_nose_box_centre,
            "remove_nose_box": self._nose_box.remove_nose_box,
            "bound_nose_box": self._nose_box.update_nose_box_boundaries
        }
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from NoseBox")
        return funcs[name]

    def _check_nose_box_initialized(self):
        if self._nose_box is None:
            self._check_monitor_tracker_initialized()
            self._nose_box = NoseBox(self._view, self._monitor_tracker)


# -------------------------------------------------------------------------------------------
# AreaOfInterest
    def _get_aoi_func(self, name: str):
        self._check_aoi_initialized()
        funcs = {
            "update_spacing_level": self._aoi.update_spacing_level,
        }
        if name not in funcs:
            raise RuntimeError("Attempt to get an undefined event handler function:" + name + " from AreaOfInterest")
        return funcs[name]

    def _check_aoi_initialized(self):
        if self._aoi is None:
            self._check_monitor_tracker_initialized()
            self._aoi = AreaOfInterest(self._view, self._monitor_tracker)



# ######################################## SPEECH MODULE ####################################
# -------------------------------------------------------------------------------------------
# Transcription
    def _get_transcribe_func(self, name: str):
        """ Transcription """
        self._check_transcription_initialized()
        funcs = {
            "start_transcribe": self._transcriber.start_transcribe,
            "stop_transcribe": self._transcriber.stop_transcribe,
            "change_speech_language": self._transcriber.change_speech_language,
        }
        if name not in funcs:
            raise RuntimeError(
                "Attempt to get an undefined event handler function:" + name + " from KITA Transcription")
        return funcs[name]

    def _check_transcription_initialized(self):
        """ Check Transcription """
        if self._transcriber is None:
            self._transcriber = Transcriber(self._view)    
# -------------------------------------------------------------------------------------------
# Correction mode           
    def _get_correction_mode_func(self, name: str):
        """ Correction mode """
        self._check_correction_mode_initialized()
        funcs = {
            "start_correction_mode": self._correction_mode.start_correction_mode,
            "stop_correction_mode": self._correction_mode.stop_correction_mode,
        }
        if name not in funcs:
            raise RuntimeError(
                "Attempt to get an undefined event handler function:" + name + " from KITA Correction")
        return funcs[name]

    def _check_correction_mode_initialized(self):
        """ Check Correction mode """
        if self._correction_mode is None:
            self._correction_mode = CorrectionMode(self._view)

# -------------------------------------------------------------------------------------------
# Speaker Identification           
    def _get_speaker_identification_func(self, name: str):
        """ Speaker Identification """
        self._check_speaker_identification_initialized()
        funcs = {
            "start_speaker_identification": self._speaker_identification.start_speaker_identification,
            "stop_speaker_identification": self._speaker_identification.stop_speaker_identification,
            "remove_locked_speaker": self._speaker_identification.remove_locked_speaker,
            "enable_speaker_identify": self._speaker_identification.enable_speaker_identify,
            "disable_speaker_identify": self._speaker_identification.disable_speaker_identify,
        }
        if name not in funcs:
            raise RuntimeError(
                "Attempt to get an undefined event handler function:" + name + " from KITA SpeakerIdentification")
        return funcs[name]

    def _check_speaker_identification_initialized(self):
        """ Check Speaker Identification """
        if self._speaker_identification is None:
            self._speaker_identification = SpeakerIdentification(self._view)
