'''
Author: Oluwaponmile Femi-Sunmaila
'''
from scripts.tools.logger import get_logger
log = get_logger(__name__)
from motioninput_api import MotionInputAPI as Api
import ast
from typing import Any, Optional
from scripts.tools.json_editors.config_editor import ConfigEditor

api = Api()

EDITORS = {
    "config": api.get_config_editor(),
    "mode": api.get_mode_editor(),
    "gestures": api.get_gestures_editor(),
    "events": api.get_events_editor()
}

ERRORS = {
    "bad_request": "Invalid request format, requests should be of the form <keyword>:<request>",
    "bad_operator": f"Invalid operator used, only GET, UPDATE, ADD, REMOVE, START, END and REBOOT requests are supported",
    "bad_json": f"Invalid JSON path. Paths must be prefixed with {', '.join(EDITORS)}",
    "illegal_config_operation": "The request you made cannot be performed on the config file"
}
CONTROL_COMMANDS = ("START", "STOP", "END", "SHOW",
                    "HIDE", "REBOOT", "CURRENT_STATE")
SPEECH_ON_SUFFIX = "_speech"

events_editor = api.events_editor()

SPEECH_EVENTS = ["speech_hotkey_full_screen", "speech_hotkey_close", "speech_keyboard_windows_key", "speech_keyboard_cut", 
                 "speech_keyboard_copy", "speech_keyboard_right_arrow", "speech_start_transcribe", "speech_keyboard_space", 
                 "speech_next_mode", "speech_keyboard_windows_run", "speech_hotkey_paste", "speech_clicking", 
                 "speech_keyboard_macros", "speech_hotkey_save", "speech_keyboard_volume_down", "speech_keyboard_volume_up", 
                 "speech_keyboard_page_down", "speech_keyboard_help", "speech_right_clicking", "speech_double_clicking", 
                 "speech_stop_transcribe", "speech_keyboard_page_up", "speech_keyboard_switch", "speech_keyboard_left_arrow", 
                 "speech_hotkey_revert", "speech_keyboard_escape", "speech_hotkey_print", "speech_correction_mode_stop", "speech_correction_mode_start"]

# TODO: Catch specific Exceptions to prevent error hiding, make own exceptions maybe? Not maybe, do that.
# TODO: Put text validation logic into another class?

# CALIBRATE_MODULE: body {vals}


class Communicator:
    """ Class to communicate with motioninput_api"""
    def __init__(self):
        self.VALID_OPERATORS = {
            "GET": self._process_get_request,
            "UPDATE": self._process_update_request,
            "ADD": self._process_add_request,
            "REMOVE": self._process_remove_request,
            "START": self._start,
            "STOP": self._stop,
            "END": self._end,
            "REBOOT": self._reboot,
            "HIDE": self._hide,
            "SHOW": self._show,
            "CURRENT_STATE": self._get_state,
            "CHANGE_MODE": self._change_mode,
            "RECORD": self._process_record_request,
            # "HEATMAP": self._process_heatmap_request,
            "CALIBRATE_MODULE": self._process_calibration_request,
            "SPEECH": self._process_speech_request
        }
        self.operation = None
        self.request = None
        self.out = None

    def process_command(self, request: str) -> str:
        """Processes a command sent from front end and sends back a response

        :param input: The command to be processed
        :type input: str
        :return: The return message to be sent to front end.
        :rtype: str
        """
        try:
            out = self._process_command(request)
            if not out:
                return None
            return f"SUCCESS: {out}"
        except Exception as error:
            return f"ERROR: " + str(error)


    def _process_command(self, msg: str) -> str:
        self.out = {}
        if msg in CONTROL_COMMANDS:
            return self._process_control_request(msg)
        self.operation, self.request = self._split_by_delim(msg, ": ")
        if self.operation not in self.VALID_OPERATORS:
            raise Exception(f"{ERRORS['bad_operator']}")
        return self._process_request()


    def _process_request(self) -> str:
        out = self.VALID_OPERATORS[self.operation](self.request)
        return out


    def _process_control_request(self, request):
        try:
            return self.VALID_OPERATORS[request]()
        except Exception as error:
            raise Exception(f"{error}")


    def _process_get_request(self, request: str) -> str:
        list_request, json_path = self._unpack_request(request)
        editor = self._get_json(list_request[0])
        if request in EDITORS:
            self.out[request] = editor.get_all_data()
        else:
            self.out[request] = editor.get_data(json_path)
        return self.out


    @staticmethod
    def _reboot():
        api.stop()
        api.start()
        log.info("Communicator: Rebooted")
        return "Rebooted"


    @staticmethod
    def _start():
        api.start()
        log.info("Communicator: MI Started")
        return "MI Started"


    @staticmethod
    def _stop():
        api.stop()
        log.info("Communicator: MI Stopped")
        return "MI Stopped"


    @staticmethod
    def _end():
        try:
            api.stop()
            log.info("Communicator: Attempting End")
        except:
            pass  # Even if MotionInput is not running we still want to end communication
        return None


    @staticmethod
    def _get_state():
        if api.get_state():
            return "Active"
        return "Inactive"


    @staticmethod
    def _hide():
        api.hide_view()
        return "View hidden"


    @staticmethod
    def _show():
        api.show_view()
        return "View shown"


    @staticmethod
    def _reboot():
        api.stop()
        api.start()


    @staticmethod
    def _change_mode(mode: str):
        api.change_mode(mode)
        return "Mode changed"


    @staticmethod
    def _calibrate_module(module: str, params: Optional[Any] = None):
        api.calibrate_module(module, params)
        return f"Calibrated module: {module}"


    def _process_calibration_request(self, request: str):
        module, params = self._split_by_delim(request, " ")
        return self._calibrate_module(module, ast.literal_eval(params))


    def _process_add_request(self, request: str) -> str:
        path, object_to_add = self._split_by_delim(request, "=")
        list_request, json_path = self._unpack_request(path)
        editor = list_request[0]
        if editor == "config":
            raise PermissionError(ERRORS["illegal_config_operation"])
        editor = self._get_json(editor)
        print(f"json path: {json_path}")
        print(f"object_to_add: {object_to_add}")
        self.out[path] = editor.add(
            json_path, object_to_add)
        if list_request[0] == "mode":
            editor.add(json_path, object_to_add + SPEECH_ON_SUFFIX)
        editor.save()
        return "Object added to JSON file"


    def _process_speech_request(self, request: str) -> str:
        speech_state = request.lstrip().lower()
        editor = self._get_json("mode")
        current_mode = editor.get_data("current_mode")
        has_speech_on = current_mode.endswith(SPEECH_ON_SUFFIX)
        if speech_state == "on" and not has_speech_on:
            editor.update("current_mode", current_mode + SPEECH_ON_SUFFIX)
        elif speech_state == "off" and has_speech_on:
            editor.update("current_mode", current_mode.removesuffix(SPEECH_ON_SUFFIX))
        elif (speech_state == "on" and has_speech_on) or (speech_state == "off" and not has_speech_on):
            return "No speech change from before"
        else:
            raise TypeError("Unknown error processing speech request")
        editor.save()
        return "Registered Speech Change"


    def _process_record_request(self, request: str) -> str:
        parameter_dict = ast.literal_eval(request)
        try:
            out = api.record_gesture(parameter_dict)
        except Exception as error:
            return f"{error}"
        return out


    def _process_update_request(self, request: str) -> str:
        request, value = self._split_by_delim(request, "=")
        list_request, json_path = self._unpack_request(request)
        editor = self._get_json(list_request[0])
        if isinstance(editor, ConfigEditor):
            self._config_update(json_path, value)
        else:
            self.out[request] = editor.update(json_path, value)
            if list_request[0] == 'mode' and value.startswith("/modes"):
                normal_mode_values = ast.literal_eval(value)
                update_with_speech_values = normal_mode_values + SPEECH_EVENTS
                editor.update(json_path + SPEECH_ON_SUFFIX, str(update_with_speech_values))
        editor.save()
        # self._reboot() #Changes take effect
        return "JSON updated"

    def _process_remove_request(self, request: str) -> str:
        list_request, json_path = self._unpack_request(request)
        editor = list_request[0]
        if editor not in EDITORS:
            raise TypeError(ERRORS["bad_json"])
        if editor == "config":
            raise PermissionError(ERRORS["illegal_config_operation"])
        editor = EDITORS[editor]
        self.out[request] = editor.remove(json_path)
        if list_request[0] == "mode":
            editor.remove(json_path + SPEECH_ON_SUFFIX)
        editor.save()
        return self.out

    @ staticmethod
    def _split_by_delim(inp: str, delim: str) -> Optional[list[str]]:
        out = inp.split(delim)
        if len(out) > 2:
            return out[0], delim.join(out[1:])
        return out

    @ staticmethod
    def _unpack_request(request: str):
        list_request = request.split("/")
        json_path = "/".join(list_request[1:])
        return list_request, json_path

    def _config_update(self, request, value):
        self.out[request] = EDITORS["config"].update(request, value)

    def _get_json(self, editor):
        if editor in EDITORS:
            return EDITORS[editor]
        raise TypeError(ERRORS["bad_json"])


    # def _process_heatmap_request(self, request: str) -> str:
    #     parameter_dict = ast.literal_eval(request)
    #     try:
    #         out = api.create_heatmap(parameter_dict)
    #         for editor_name, editor in EDITORS.items():
    #             editor._read_data()
    #     except Exception as error:
    #         return f"{error}"
    #
    #     return out