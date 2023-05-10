import json
import os
import unittest

from communicator import Communicator
from scripts.tools.json_editors.json_encoder import JSONEncoder
from .set_up_configs import *

EDITORS = {
    "config": CONFIG,
    "mode_controller": MODES,
    "gestures": GESTURES,
    "events": EVENTS
}

EXPECTED_ERRORS = {
    "bad_request": "Invalid request format, requests should be of the form <keyword>:<request>",
    "bad_operator": f"Invalid operator used, only GET, UPDATE, ADD, REMOVE, START, END and REBOOT requests are supported",
    "bad_json": f"Invalid JSON path. Paths must be prefixed with config, mode, gestures, events",
    "illegal_config_operation": "The request you made cannot be performed on the config file",
    "path_does_not_exist" : "JSON path does not exist",
    "missing_attr": "Missing event attribute",
    "invalid_attr": "Invalid event attribute: ",
}

class TestCommunicator(unittest.TestCase):

    def setUp(cls):
        cls.communicator = Communicator()

    def tearDown(self) -> None:
        for editor in EDITORS:
            path = os.path.abspath(
                os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    f"data/{editor}.json"
                ))
            with open(path, 'w') as file:
                json_object = json.dumps(EDITORS[editor], indent=4, cls=JSONEncoder)
                file.write(json_object)

    def test_invalid_config(cls):
        out = cls.communicator.process_command("I WILL CAUSE PROBLEMS")
        cls.assertEqual(out, f"ERROR: {EXPECTED_ERRORS['bad_request']}")

    def test_bad_command(cls):
        out = cls.communicator.process_command("SUB: this/to/that")
        cls.assertEqual(out, f"ERROR: {EXPECTED_ERRORS['bad_operator']}")

    def test_invalid_config(cls):
        out = cls.communicator.process_command("ADD: some_fake_config/this_and_that=a")
        cls.assertEqual(out, f"ERROR: {EXPECTED_ERRORS['bad_json']}")

    def test_update_config(cls):
        cls.communicator.process_command("UPDATE: config/general/view/window_name=A_new_name!")
        out = cls.communicator.process_command("GET: config/general/view/window_name")
        cls.assertEqual(out, "SUCCESS: {'config/general/view/window_name': 'A_new_name!'}")

    def test_update_default_mode(cls):
        cls.communicator.process_command("UPDATE: mode/default=some_mode")
        out = cls.communicator.process_command("GET: mode/default")
        cls.assertEqual(out, "SUCCESS: {'mode/default': 'some_mode'}")

    def test_update_iteration_order(cls):
        cls.communicator.process_command("UPDATE: mode/iteration_order={'a': 'b', 'b': 'a'}")
        out = cls.communicator.process_command("GET: mode/iteration_order")
        cls.assertEqual(out, "SUCCESS: {'mode/iteration_order': {'a': 'b', 'b': 'a'}}")
 

    def test_update_event(cls):
        cls.maxDiff = None
        cls.communicator.process_command("UPDATE: events/hand_to_idle_mode_right_hand={'type': 'IdleStateChangeEvent', 'args': {'currently_idle': 'true'}, 'bodypart_names_to_type': {'Right': 'hand'}, 'triggers': {'active': ['ModeChange','basic_hand']}}")
        out = cls.communicator.process_command("GET: events/hand_to_idle_mode_right_hand")
        cls.assertEqual(out, "SUCCESS: {'events/hand_to_idle_mode_right_hand': {'type': 'IdleStateChangeEvent', 'args': {'currently_idle': 'true'}, 'bodypart_names_to_type': {'Right': 'hand'}, 'triggers': {'active': ['ModeChange', 'basic_hand']}}}")
    
    def test_update_invalid_path_returns_error(cls):
        out = cls.communicator.process_command("UPDATE: gestures/wand/index_pinched=False")
        cls.assertEqual(out, f"ERROR: '{EXPECTED_ERRORS['path_does_not_exist']}'")


    def test_add_config_raises_error(cls):
        out = cls.communicator.process_command("ADD: config/modules=feet")
        cls.assertEqual(out, f"ERROR: {EXPECTED_ERRORS['illegal_config_operation']}")

    def test_remove_config_raises_error(cls):
        out = cls.communicator.process_command("REMOVE: config/general/modules/hand")
        cls.assertEqual(out, f"ERROR: {EXPECTED_ERRORS['illegal_config_operation']}")
            

    def test_get_config(cls):
        out = cls.communicator.process_command("GET: config/general/view/window_name")
        cls.assertEqual(out, "SUCCESS: {'config/general/view/window_name': 'UCL MotionInput v3.0'}")

    def test_add_mode(cls):
        cls.communicator.process_command("ADD: mode/modes=A_new_mode")
        expected = cls.communicator.process_command("GET: mode/modes/A_new_mode")
        cls.assertTrue(expected, "SUCCESS: {'mode/modes/A_new_mode': []}")

    def test_remove_mode(cls):
        cls.communicator.process_command("REMOVE: mode/modes/basic_hand")
        out = cls.communicator.process_command("GET: mode/modes/basic_hand")
        cls.assertEqual(out, f"ERROR: '{EXPECTED_ERRORS['path_does_not_exist']}'")

    def test_get_default_mode(cls):
        out = cls.communicator.process_command("GET: mode/default")
        cls.assertEqual(out, "SUCCESS: {'mode/default': 'basic_hand'}")


    def test_get_event(cls):
        out = cls.communicator.process_command("GET: events/hand_open_keyboard_left_hand/type")
        cls.assertEqual(out, "SUCCESS: {'events/hand_open_keyboard_left_hand/type': 'GesturesActiveEvent'}")


    def test_get_from_fake_path_returns_error(cls):
        out = cls.communicator.process_command("GET: gestures/wand/index_pinched")
        cls.assertEqual(out, f"ERROR: {EXPECTED_ERRORS['path_does_not_exist']}")

    def test_adding_to_config_raises_error(cls):
        out = cls.communicator.process_command("ADD: config/modules=feet")
        cls.assertEqual(out, f"ERROR: {EXPECTED_ERRORS['illegal_config_operation']}")

    def test_adding_event_without_required_attribute_raises_error(cls):
        out = cls.communicator.process_command("ADD: events={'name': 'invalid_event','type': 'IdleStateChangeEvent', 'args': {'currently_idle': 'true'}, 'triggers': {'active': ['ModeChange','basic_hand']}}")
        cls.assertEqual(out, f"ERROR: '{EXPECTED_ERRORS['missing_attr']}'")

    def test_adding_event_with_unknown_attribute_raises_error(cls):
        out = cls.communicator.process_command("ADD: events={'this_will_break': 'oops'}")
        cls.assertEqual(out, f"ERROR: '{EXPECTED_ERRORS['invalid_attr']}this_will_break'")

    def test_add_event(cls):
        cls.communicator.process_command("ADD: events={'name': 'valid_event','type': 'IdleStateChangeEvent',  'bodypart_names_to_type':  {'Left': 'hand'}, 'args': {'currently_idle': 'true'}, 'triggers': {'active': ['ModeChange','basic_hand']}}")
        out = cls.communicator.process_command("GET: events/valid_event")
        cls.assertEqual(out, "SUCCESS: {'events/valid_event': {'type': 'IdleStateChangeEvent', 'bodypart_names_to_type': {'Left': 'hand'}, 'args': {'currently_idle': 'true'}, 'triggers': {'active': ['ModeChange', 'basic_hand']}}}")

    def test_add_gesture(cls):
        cls.communicator.process_command("ADD: gestures/hand={'name': 'new_hand_gesture', 'pinky_up': True}")
        out = cls.communicator.process_command("GET: gestures/hand/new_hand_gesture")
        cls.assertEqual(out, "SUCCESS: {'gestures/hand/new_hand_gesture': {'pinky_up': True}}")

    def test_remove_mode(cls):
        cls.communicator.process_command("REMOVE: mode/modes/basic_hand")
        out = cls.communicator.process_command("GET: mode/modes/basic_hand")
        cls.assertEqual(out, f"ERROR: '{EXPECTED_ERRORS['path_does_not_exist']}'")

    def test_remove_gesture(cls):
        cls.communicator.process_command("REMOVE: gestures/hand/index_pinch")
        out = cls.communicator.process_command("GET: gestures/hand/index_pinch")
        cls.assertEqual(out, f"ERROR: {EXPECTED_ERRORS['path_does_not_exist']}")

    def test_remove_event(cls):
        cls.communicator.process_command("REMOVE: events/hand_to_idle_mode_left_hand")
        out = cls.communicator.process_command("GET: events/hand_to_idle_mode_left_hand")
        cls.assertEqual(out, f"ERROR: '{EXPECTED_ERRORS['path_does_not_exist']}'")

    def test_remove_mode(cls):
        out = cls.communicator.process_command("REMOVE: code/modes/basic_hand")
        cls.assertEqual(out, f"ERROR: {EXPECTED_ERRORS['bad_json']}")


if __name__ == '__main__':
    unittest.main()
