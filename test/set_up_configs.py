CONFIG = {
    "general": {
        "view": {
            "window_name": "UCL MotionInput v3.0",
            "show_mode_name": True
        },
        "camera": {
            "camera_w": 640,
            "camera_h": 480,
            "camera_nr": 0
        }
    },
    "events": {
        "click_press": {
            "frames_for_press": 2
        },
        "idle_state_change": {
            "frames_for_switch": 10
        },
        "palm_height_change": {
            "frames_for_switch": 10,
            "levels": [
                0,
                0.105,
                0.155
            ]
        },
        "scroll": {
            "frames_for_switch": 2,
            "index_middle_distance_threshold": 0.3,
            "speed_multiplier": 2,
            "change_direction": -1,
            "TO IMPLEMENT: scroll_sensitivity": "num"
        },
        "zoom": {
            "frames_for_switch": 4
        },
        "mouth_events": {
            "frames_for_press": 3,
            "trigger_count": 10
        },
        "nose_tracking": {
            "scaling_factor": 400,
            "nose_box_percentage_size": 0.04
        },
        "mode_change": {
            "frames_for_switch": 4
        },
        "keyboard": {
            "landmarks": [
                "index",
                "middle",
                "ring"
            ],
            "gesture_type": "pulldown",
            "single_tap_min_bound": 0.02,
            "single_tap_max_bound": 1,
            "hold_press_min_duration": 3,
            "default_key_font_size": 0.75,
            "default_key_width": 50,
            "default_key_height": 50,
            "default_key_bg_colour": [
                0,
                0,
                0
            ],
            "default_transparency": 0.7
        },
        "extremity_walking": {
            "up_key": "w",
            "left_key": "a",
            "right_key": "d"
        },
        "exercise_events": {
            "hold_key_down_interval": 0.2,
            "exercise_release_interval": 0.4
        },
        "gaming_extremity_walking": {
            "walking_extremities": {
                "extremity_left_walking": "a",
                "extremity_right_walking": "d",
                "extremity_up_walking": "w",
                "extremity_down_walking": "s"
            },
            "button_extremities": {
                "extremity_left_button": "j",
                "extremity_right_button": "b",
                "extremity_up_button": "k",
                "extremity_down_button": "l",
                "extremity_quit_key": "esc",
                "extremity_start_key": "space"
            }
        }
    },
    "modules": {
        "hand": {
            "gestures_max_pos_queue": None,
            "position_pinch_sensitivity": 0.15,
            "position_scissor_sensitivity": 0.1,
            "position_threshold_distance": 0,
            "min_detection_confidence": 0.6,
            "min_tracking_confidence": 0.6,
            "max_num_hands": 2
        },
        "exercise": {
            "gestures_max_pos_queue": None,
            "mode": "no_equipment",
            "TO IMPLEMENT: logging": "bool",
            "TO IMPLEMENT: move_coordinates": "?",
            "TO IMPLEMENT: key down_time": "num 0-1 seconds (i think)",
            "TO IMPLEMENT: change_mode/main_menu": "?"
        },
        "face": {
            "TO IMPLEMENT: cursor": "eye/nose",
            "TO_IMPLEMENT: cursor_type": "grid/floating",
            "TO IMPLEMENT: mode_cursor_switch": "gesture_name",
            "TO IMPLEMENT: camera_height(cm)": 35.0,
            "TO IMPLEMENT: monitor_width(cm)": 61.0,
            "TO IMPLEMENT: monitor_height(cm)": 5.0
        },
        "eye": {
            "gestures_max_pos_queue": None,
            "screen_h": 35.0,
            "screen_w": 61.0,
            "camera_h": 5.0,
            "distance_bias": 40,
            "ys_calibrate": 4,
            "y_coefficient": 1,
            "y_x_coefficient": 0.01,
            "x_l_coefficient": 1.33,
            "x_r_coefficient": 0.75,
            "x_bias": 0,
            "x_r_y_coefficient": 0.001,
            "num_to_denoise": 5,
            "Show_Head_Position_output": 1,
            "Show_Landmark_detection_output": 0,
            "Show_Gaze_estimation_output": 0
        },
        "head": {
            "gestures_max_pos_queue": None,
            "smiling": 0.29,
            "fish_face": 0.2,
            "open_mouth": 1.05,
            "raise_eyebrow": 0.23,
            "eyes_close": 0.13,
            "turn_left": 0.5,
            "turn_right": 1.5,
            "TO IMPLEMENT: frames_for_press": "num 1-60",
            "TO IMPLEMENT: trigger_count": "num 1-60",
            "TO IMPLEMENT: nose_box_percentage": "num 0-1",
            "TO IMPLEMENT: scaling_factor": "num 100-1000"
        },
        "body": {
            "gestures_max_pos_queue": None,
            "mode": "no_equipment",
            "min_confidence_threshold": 5,
            "extremity_circle_radius": 30,
            "ankle_visibility_threshold": 0.5
        },
        "speech": {
            "language": "english"
        }
    },
    "handlers": {
        "aoi": {
            "spacing_levels": [
                0.3,
                0.4,
                0.5
            ]
        },
        "mouse": {
            "smoothing": 3,
            "sensitivity": 3
        },
        "finger": {
            "radius": 5
        },
        "zoom": {
            "smoothing": 3,
            "speed": 1.14
        },
        "scroll": {
            "speed": 10
        }
    },
    "body_gestures": {
        "extremity_triggers": {
            "punch_left": {
                "landmark": "left_wrist_extremity",
                "coordinates": [
                    139,
                    289
                ],
                "action": "key_press",
                "key": "h",
                "activated": True
            },
            "arm_left": {
                "landmark": "left_wrist_extremity",
                "coordinates": [
                    195,
                    235
                ],
                "action": "key_press",
                "key": "a",
                "activated": True
            },
            "kick_left": {
                "landmark": "left_ankle_extremity",
                "coordinates": [
                    225,
                    450
                ],
                "action": "left_click",
                "key": "",
                "activated": True
            },
            "up": {
                "landmark": "nose_extremity",
                "coordinates": [
                    320,
                    80
                ],
                "action": "key_down",
                "key": "w",
                "activated": True
            },
            "kick_right": {
                "landmark": "right_ankle_extremity",
                "coordinates": [
                    406,
                    450
                ],
                "action": "right_click",
                "key": "",
                "activated": True
            },
            "arm_right": {
                "landmark": "right_wrist_extremity",
                "coordinates": [
                    411,
                    234
                ],
                "action": "key_press",
                "key": "d",
                "activated": True
            },
            "punch_right": {
                "landmark": "right_wrist_extremity",
                "coordinates": [
                    477,
                    289
                ],
                "action": "key_press",
                "key": "s",
                "activated": True
            },
            "left_walking": {
                "landmark": "left_wrist_extremity",
                "coordinates": [
                    80,
                    200
                ],
                "action": "key_press",
                "key": "a",
                "activated": False
            },
            "right_walking": {
                "landmark": "left_wrist_extremity",
                "coordinates": [
                    230,
                    200
                ],
                "action": "key_press",
                "key": "d",
                "activated": False
            },
            "up_walking": {
                "landmark": "left_wrist_extremity",
                "coordinates": [
                    150,
                    130
                ],
                "action": "key_press",
                "key": "w",
                "activated": False
            },
            "down_walking": {
                "landmark": "left_wrist_extremity",
                "coordinates": [
                    150,
                    280
                ],
                "action": "key_press",
                "key": "s",
                "activated": False
            },
            "left_button": {
                "landmark": "right_wrist_extremity",
                "coordinates": [
                    380,
                    200
                ],
                "action": "key_press",
                "key": "x",
                "activated": False
            },
            "right_button": {
                "landmark": "right_wrist_extremity",
                "coordinates": [
                    520,
                    200
                ],
                "action": "key_press",
                "key": "b",
                "activated": False
            },
            "up_button": {
                "landmark": "right_wrist_extremity",
                "coordinates": [
                    450,
                    130
                ],
                "action": "key_press",
                "key": "y",
                "activated": False
            },
            "down_button": {
                "landmark": "right_wrist_extremity",
                "coordinates": [
                    450,
                    280
                ],
                "action": "key_press",
                "key": "a",
                "activated": False
            },
            "start_key": {
                "landmark": "left_wrist_extremity",
                "coordinates": [
                    150,
                    30
                ],
                "action": "key_press",
                "key": "space",
                "activated": False
            },
            "quit_key": {
                "landmark": "right_wrist_extremity",
                "coordinates": [
                    450,
                    30
                ],
                "action": "key_press",
                "key": "esc",
                "activated": False
            }
        },
        "exercises": {
            "no_equipment": {
                "walking": {
                    "states": {
                        "walking_left": {
                            "activated": True
                        },
                        "walking_right": {
                            "activated": True
                        }
                    },
                    "activated": True,
                    "action": "key_down",
                    "key": "w",
                    "count_to_activate": 1
                },
                "squating": {
                    "states": {
                        "squating_down": {
                            "activated": True
                        }
                    },
                    "activated": True,
                    "action": "key_press",
                    "key": "s",
                    "count_to_activate": 1
                }
            },
            "equipment": {
                "cycling": {
                    "states": {
                        "cycling_left": {
                            "activated": True
                        },
                        "cycling_right": {
                            "activated": True
                        }
                    },
                    "activated": True,
                    "action": "key_down",
                    "key": "w",
                    "count_to_activate": 1
                }
            }
        }
    }
}

EVENTS = {
    "hand_to_idle_mode_left_hand": {
        "type": "IdleStateChangeEvent",
        "args": {"currently_idle": False},
        "bodypart_names_to_type": {"Left": "hand"},
        "triggers": {
            "idle": ["ModeChange","idle_hand"]
        }
    },
    "hand_to_idle_mode_right_hand": {
        "type": "IdleStateChangeEvent",
        "args": {"currently_idle": False},
        "bodypart_names_to_type": {"Right": "hand"},
        "triggers": {
            "idle": ["ModeChange","idle_hand"]
        }
    },
    "hand_to_active_mode_left_hand": {
        "type": "IdleStateChangeEvent",
        "args": {"currently_idle": True},
        "bodypart_names_to_type": {"Left": "hand"},
        "triggers": {
            "active": ["ModeChange","basic_hand"]
        }
    },
    "hand_to_active_mode_right_hand": {
        "type": "IdleStateChangeEvent",
        "args": {"currently_idle": True},
        "bodypart_names_to_type": {"Right": "hand"},
        "triggers": {
            "active": ["ModeChange","basic_hand"]
        }
    },
    "general_rocknroll_next_mode": {
        "type": "GesturesActiveEvent",
        "args": {"desired_gesture_states": {"dom_hand": {"rocknroll": True}, "off_hand": {"rocknroll": True}}},
        "bodypart_names_to_type": {"Left": "dom_hand", "Right": "off_hand"},
        "triggers": {
            "active": ["IterativeModeChange",""]
        }
    },
    "hand_open_keyboard_right_hand": {
        "type": "GesturesActiveEvent",
        "args": {"desired_gesture_states": {"dom_hand": {"peace":True}, "off_hand": {}}},
        "bodypart_names_to_type": {"Right": "dom_hand", "Left": "off_hand"},
        "triggers": {
            "active": ["ModeChange","keyboard_hand"]
        }
    },
    "hand_open_keyboard_left_hand": {
        "type": "GesturesActiveEvent",
        "args": {"desired_gesture_states": {"dom_hand": {"peace":True}, "off_hand": {}}},
        "bodypart_names_to_type": {"Left": "dom_hand", "Right": "off_hand"},
        "triggers": {
            "active": ["ModeChange","keyboard_hand"]
        }
    },
    "hand_mouse_switch_right_hand": {
        "type": "GesturesActiveEvent",
        "args": {"desired_gesture_states": {"dom_hand": {"gun":True}, "off_hand": {}}},
        "bodypart_names_to_type": {"Right": "dom_hand", "Left": "off_hand"},
        "triggers": {
            "active": ["ModeChange","basic_hand"]
        }
    },
    "hand_mouse_switch_left_hand": {
        "type": "GesturesActiveEvent",
        "args": {"desired_gesture_states": {"dom_hand": {"gun":True}, "off_hand": {}}},
        "bodypart_names_to_type": {"Left": "dom_hand", "Right": "off_hand"},
        "triggers": {
            "active": ["ModeChange","basic_hand"]
        }
    },
    "hand_palm_height_change_aoi_resize_left_hand": {
        "type": "PalmHeightChangeEvent",
        "args": {},
        "bodypart_names_to_type": {"Left": "hand"},
        "triggers": {
            "level_change": ["AreaOfInterest","update_spacing_level"]
        }
    },
    "hand_palm_height_change_aoi_resize_right_hand": {
        "type": "PalmHeightChangeEvent",
        "args": {},
        "bodypart_names_to_type": {"Right": "hand"},
        "triggers": {
            "level_change": ["AreaOfInterest","update_spacing_level"]
        }
    },
    "hand_palm_center_move_mouse_left_hand": {
        "type": "HandActiveEvent",
        "args": {},
        "bodypart_names_to_type": {"Left": "hand"},
        "triggers": {
            "move": ["AOIMouse","move_cursor"]
        }
    },
    "hand_palm_center_move_mouse_right_hand": {
        "type": "HandActiveEvent",
        "args": {},
        "bodypart_names_to_type": {"Right": "hand"},
        "triggers": {
            "move": ["AOIMouse","move_cursor"]
        }
    },
	"in_air_keyboard_active": {
		"type": "KeyboardActiveEvent",
		"args": {},
		"bodypart_names_to_type": { "Right": "dom_hand", "Left": "off_hand" },
		"triggers": {
			"move": [ "InAirKeyboard", "key_selection" ],
			"clear": [ "InAirKeyboard", "clear" ]
		}
	},
	"in_air_keyboard_click": {
		"type": "KeyboardClickEvent",
		"args": {},
		"bodypart_names_to_type": { "Right": "dom_hand", "Left": "off_hand" },
		"triggers": {
			"click": [ "InAirKeyboard", "click" ],
			"release": [ "InAirKeyboard", "release" ]
		}
	},
    "hand_index_pinch_left_press_left_hand": {
        "type": "SingleHandExclusiveClickPressEvent",
        "args": {"gesture_type":"index_pinch"},
        "bodypart_names_to_type": {"Left": "hand", "Right": "off_hand"},
        "triggers": {
            "press": ["AOIMouse","left_press"],
            "release": ["AOIMouse","left_release"]
        }
    },
    "hand_index_pinch_left_press_right_hand": {
        "type": "SingleHandExclusiveClickPressEvent",
        "args": {"gesture_type":"index_pinch"},
        "bodypart_names_to_type": {"Right": "hand", "Left": "off_hand"},
        "triggers": {
            "press": ["AOIMouse","left_press"],
            "release": ["AOIMouse","left_release"]
        }
    },
    "hand_index_pinch_touch_press_left_hand": {
        "type": "SingleHandExclusiveClickPressEvent",
        "args": {"gesture_type":"index_pinch"},
        "bodypart_names_to_type":  {"Left": "hand", "Right": "off_hand"},
        "triggers": {
            "press": ["DesktopTouch","press"],
            "release": ["DesktopTouch","release"]
        }
    },
    "hand_index_pinch_touch_press_right_hand": {
        "type": "SingleHandExclusiveClickPressEvent",
        "args": {"gesture_type":"index_pinch"},
        "bodypart_names_to_type":  {"Right": "hand", "Left": "off_hand"},
        "triggers": {
            "press": ["DesktopTouch","press"],
            "release": ["DesktopTouch","release"]
        }
    },
    "hand_middle_pinch_right_press_left_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"middle_pinch"},
        "bodypart_names_to_type": {"Left": "hand"},
        "triggers": {
            "press": ["AOIMouse","right_press"],
            "release": ["AOIMouse","right_release"]
        }
    },
    "hand_middle_pinch_right_press_right_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"middle_pinch"},
        "bodypart_names_to_type": {"Right": "hand"},
        "triggers": {
            "press": ["AOIMouse","right_press"],
            "release": ["AOIMouse","right_release"]
        }
    },
    "hand_pinky_pinch_monitor_change_left_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"pinky_pinch"},
        "bodypart_names_to_type": {"Left": "hand"},
        "triggers": {
            "press": ["MonitorTracker","change_monitor"]
        }
    },
    "hand_pinky_pinch_monitor_change_right_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"pinky_pinch"},
        "bodypart_names_to_type": {"Right": "hand"},
        "triggers": {
            "press": ["MonitorTracker","change_monitor"]
        }
    },
    "hand_double_pinch_double_click_left_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"double_pinch"},
        "bodypart_names_to_type": {"Left": "hand"},
        "triggers": {
            "click": ["AOIMouse","double_click"]
        }
    },
    "hand_double_pinch_double_click_right_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"double_pinch"},
        "bodypart_names_to_type": {"Right": "hand"},
        "triggers": {
            "click": ["AOIMouse","double_click"]
        }
    },
    "hand_index_pulldown_left_press_left_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"index_pulldown"},
        "bodypart_names_to_type": {"Left": "hand"},
        "triggers": {
            "press": ["AOIMouse","left_press"],
            "release": ["AOIMouse","left_release"]
        }
    },
    "hand_index_pulldown_left_press_right_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"index_pulldown"},
        "bodypart_names_to_type": {"Right": "hand"},
        "triggers": {
            "press": ["AOIMouse","left_press"],
            "release": ["AOIMouse","left_release"]
        }
    },
    "hand_index_scissor_left_press_left_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"index_scissor"},
        "bodypart_names_to_type": {"Left": "hand"},
        "triggers": {
            "press": ["AOIMouse","left_press"],
            "release": ["AOIMouse","left_release"]
        }
    },
    "hand_index_scissor_left_press_right_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"index_scissor"},
        "bodypart_names_to_type": {"Right": "hand"},
        "triggers": {
            "press": ["AOIMouse","left_press"],
            "release": ["AOIMouse","left_release"]
        }
    },
    "hand_thumb_scissor_right_press_left_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"thumb_scissor"},
        "bodypart_names_to_type": {"Left": "hand"},
        "triggers": {
            "press": ["AOIMouse","right_press"],
            "release": ["AOIMouse","right_release"]
        }
    },
    "hand_thumb_scissor_right_press_right_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"thumb_scissor"},
        "bodypart_names_to_type": {"Right": "hand"},
        "triggers": {
            "press": ["AOIMouse","right_press"],
            "release": ["AOIMouse","right_release"]
        }
    },
    "hand_double_scissor_doubleclick_left_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"double_scissor"},
        "bodypart_names_to_type": {"Left": "hand"},
        "triggers": {
            "click": ["AOIMouse","double_click"]
        }
    },
    "hand_double_scissor_doubleclick_right_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"double_scissor"},
        "bodypart_names_to_type": {"Right": "hand"},
        "triggers": {
            "click": ["AOIMouse","double_click"]
        }
    },
    "hand_fist_doubleclick_left_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"fist"},
        "bodypart_names_to_type": {"Left": "hand"},
        "triggers": {
            "click": ["AOIMouse","double_click"]
        }
    },
    "hand_fist_doubleclick_right_hand": {
        "type": "ClickPressEvent",
        "args": {"gesture_type":"fist"},
        "bodypart_names_to_type": {"Right": "hand"},
        "triggers": {
            "click": ["AOIMouse","double_click"]
        }
    },
    "hand_index_middle_scroll_left_hand": {
        "type": "ScrollEvent",
        "args": {},
        "bodypart_names_to_type": {"Left": "hand"},
        "triggers": {
            "scroll": ["AOIMouse","scroll"]
        }
    },
    "hand_index_middle_scroll_right_hand": {
        "type": "ScrollEvent",
        "args": {},
        "bodypart_names_to_type": {"Right": "hand"},
        "triggers": {
            "scroll": ["AOIMouse","scroll"]
        }
    },
    "hand_double_index_pinch_zoom": {
        "type": "ZoomEvent",
        "args": {},
        "bodypart_names_to_type":  {"Left": "dom_hand", "Right": "off_hand"},
        "triggers": {
            "zoom": ["AOIMouse","zoom"]
        }
    },
    "extremity_up": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "up"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_arm_left": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "arm_left"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_arm_right": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "arm_right"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_punch_left": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "punch_left"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_punch_right": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "punch_right"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_kick_left": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "kick_left"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },

    "extremity_kick_right": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "kick_right"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_left_walking": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "left_walking"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_right_walking": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "right_walking"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_up_walking": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "up_walking"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_down_walking": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "down_walking"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_left_button": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "left_button"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_right_button": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "right_button"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_up_button": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "up_button"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_down_button": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "left_button"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_start_key": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "start_key"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "extremity_quit_key": {
        "type": "ExtremityTriggerEvent",
        "args": {"extremity_name": "quit_key"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_extremity_circles": ["ExtremityActions","set_extremity_circles"],
            "triggered": ["ExtremityActions","trigger_action"],
            "held": ["ExtremityActions","held_action"],
            "released": ["ExtremityActions","release_action"],
            "clear": ["ExtremityActions", "clear_extremity_circles"]
        }
    },
    "exercise_squating": {
        "type": "ExerciseEvent",
        "args": {"exercise_name": "squating", "mode": "no_equipment"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_exercise_display": ["ExerciseActions","set_exercise_display"],
            "triggered": ["ExerciseActions","trigger_action"],
            "held": ["ExerciseActions","held_action"],
            "released": ["ExerciseActions","release_action"],
            "clear": ["ExerciseActions", "clear_exercise_display"]
        }
    },
    "exercise_walking": {
        "type": "ExerciseEvent",
        "args": {"exercise_name": "walking", "mode": "no_equipment"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_exercise_display": ["ExerciseActions","set_exercise_display"],
            "triggered": ["ExerciseActions","trigger_action"],
            "held": ["ExerciseActions","held_action"],
            "released": ["ExerciseActions","release_action"],
            "clear": ["ExerciseActions", "clear_exercise_display"]
        }
    },
    "cycling_exercise": {
        "type": "ExerciseEvent",
        "args": {"exercise_name": "cycling", "mode": "equipment"},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_exercise_display": ["ExerciseActions","set_exercise_display"],
            "triggered": ["ExerciseActions","trigger_action"],
            "held": ["ExerciseActions","held_action"],
            "released": ["ExerciseActions","release_action"],
            "clear": ["ExerciseActions", "clear_exercise_display"]
        }
    },
    "extremity_walking_event": {
        "type": "ExtremityWalkingEvent",
        "args": {},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_displays": ["ExtremityWalkingActions","set_displays"],
            "walking_triggered": ["ExtremityWalkingActions","walking_trigger_action"],
            "extremity_triggered": ["ExtremityWalkingActions","extremity_trigger_action"],
            "held": ["ExtremityWalkingActions","held_action"],  
            "walking_released": ["ExtremityWalkingActions","walking_release_action"],
            "extremity_released": ["ExtremityWalkingActions","extremity_release_action"],
            "clear": ["ExtremityWalkingActions", "clear_display"]
        }
    },
    "gaming_extremity_walking_event": {
        "type": "GamingExtremityWalkingEvent",
        "args": {},
        "bodypart_names_to_type": {"body": "body"},
        "triggers": {
            "set_displays": ["GamingExtremityWalkingActions","set_displays"],
            "walking_triggered": ["GamingExtremityWalkingActions","walking_trigger_action"],
            "extremity_triggered": ["GamingExtremityWalkingActions","extremity_trigger_action"],
            "held": ["GamingExtremityWalkingActions","held_action"],  
            "walking_released": ["GamingExtremityWalkingActions","walking_release_action"],
            "extremity_released": ["GamingExtremityWalkingActions","extremity_release_action"],
            "clear": ["GamingExtremityWalkingActions", "clear_display"]
        }
    },
    "speech_clicking": {
        "type": "SpeechEvent",
        "args": {"phrase": "click"},
        "bodypart_names_to_type": {"speech": "speech"},
        "triggers": {
            "click": ["DesktopMouse", "left_click"]
        }
    },

    "speech_right_clicking": {
        "type": "SpeechEvent",
        "args": {"phrase": "right click"},
        "bodypart_names_to_type": {"speech": "speech"},
        "triggers": {
            "right click": ["DesktopMouse", "right_click"]
        }
    },
    "speech_double_clicking": {
        "type": "SpeechEvent",
        "args": {"phrase": "double click"},
        "bodypart_names_to_type": {"speech": "speech"},
        "triggers": {
            "double click": ["DesktopMouse", "double_click"]
        }
    },

    "speech_hotkey_save": {
        "type": "SpeechEvent",
        "args": {"phrase": "save"},
        "bodypart_names_to_type": {"speech": "speech"},
        "triggers": {
            "save": ["Keyboard", "save"]
        }
    },

    "speech_start_transcribe": {
        "type": "SpeechEvent",
        "args": {"phrase": "transcribe"},
        "bodypart_names_to_type": {"speech": "speech"},
        "triggers": {
            "transcribe": ["Transcriber", "start_transcribe"]
        }
    },

    "speech_stop_transcribe": {
        "type": "SpeechEvent",
        "args": {"phrase": "stop transcribe"},
        "bodypart_names_to_type": {"speech": "speech"},
        "triggers": {
            "stop transcribe": ["Transcriber", "stop_transcribe"]
        }
    },

    "head_smile_right_click": {
        "type": "SmilingEvent",
        "args": {},
        "bodypart_names_to_type": {
            "head": "head"
        },
        "triggers": {
            "click": ["DesktopMouse", "right_click"]
        }
    },
    "head_fishface_left_click": {
        "type": "FishFaceEvent",
        "args": {},
        "bodypart_names_to_type": {
            "head": "head"
        },
        "triggers": {
            "click": ["DesktopMouse", "right_click"]
        }
    },
    "head_open_mouth_left_press_hold_release": {
        "type": "OpenMouthEvent",
        "args": {},
        "bodypart_names_to_type": {
            "head": "head"
        },
        "triggers": {
            "press": ["AOIMouse", "left_press"],
            "release": ["DesktopMouse", "left_release"]
        }
    },
    "head_raise_head_raise_eyebrows_double_click": {
        "type": "RaiseEyeBrowEvent",
        "args": {},
        "bodypart_names_to_type": {
            "head": "head"
        },
        "triggers": {
            "click": ["DesktopMouse", "double_click"]
        }
    },
    "head_nose_tracking": {
        "type": "NoseTrackingEvent",
        "args": {},
        "bodypart_names_to_type": {
            "head": "head"
        },
        "triggers": {
            "move": ["AOIMouse", "move_cursor"]
        }
    },
    "head_nose_direction_tracking": {
        "type": "NoseDirectionTrackingEvent",
        "args": {},
        "bodypart_names_to_type": {
            "head": "head"
        },
        "triggers": {
            "move": ["DesktopMouse", "move_cursor_relative"]
        }
    },

    "head_nose_direction_tracking_nosebox": {
        "type": "NoseDirectionTrackingEventNoseBox",
        "args": {},
        "bodypart_names_to_type": {
            "head": "head"
        },
        "triggers": {
            "move": ["DesktopMouse", "move_cursor_relative"],
            "nose_box": ["NoseBox", "show_nose_box"]
        }
    },
    "head_nose_scroll": {
        "type": "NoseScrollEvent",
        "args": {},
        "bodypart_names_to_type": {"head": "head"},
        "triggers": {
            "scroll": ["AOIMouse", "scroll"]
        }
    },
    "head_nose_zoom": {
        "type": "NoseZoomEvent",
        "args": {},
        "bodypart_names_to_type": {"head": "head"},
        "triggers": {
            "zoom": ["AOIMouse","zoom"]
        }
    },
    "head_eye_tracking": {
        "type": "EyeTrackingEvent",
        "args": {},
        "bodypart_names_to_type": {"eye": "eye"},
        "triggers": {
            "move": ["DesktopMouse", "move_cursor"]
        }
    }
}

GESTURES = {
    "hand": {
        "index_pinch": {
            "index_pinched": True,
            "middle_pinched": False,
            "ring_pinched": False,
            "pinky_pinched": False
        },
        "middle_pinch": {
            "index_pinched": False,
            "middle_pinched": True,
            "ring_pinched": False,
            "pinky_pinched": False
        },
        "ring_pinch": {
            "index_pinched": False,
            "middle_pinched": False,
            "ring_pinched": True,
            "pinky_pinched": False
        },
        "pinky_pinch": {
            "index_pinched": False,
            "middle_pinched": False,
            "ring_pinched": False,
            "pinky_pinched": True
        },
        "double_pinch": {
            "index_pinched": True,
            "middle_pinched": True,
            "ring_pinched": False,
            "pinky_pinched": False
        },
        "rabbit": {
            "index_pinched": False,
            "middle_pinched": True,
            "ring_pinched": True,
            "pinky_pinched": False
        },
        "gun": {
            "thumb_stretched" : True,
            "index_stretched" : True,
            "middle_folded": True,
            "ring_folded": True,
            "pinky_folded": True
        },
        "scroll": {
            "index_pinched": False,
            "middle_pinched": False,
            "ring_folded": True,
            "pinky_folded": True
        },
        "fist": {
            "index_folded": True,
            "middle_folded": True,
            "ring_folded": True,
            "pinky_folded": True
        },
        "stretched": {
            "thumb_stretched": True,
            "index_stretched": True,
            "middle_stretched": True,
            "ring_stretched": True,
            "pinky_stretched": True
        },
        "index_pulldown": {
            "index_pulldown": True
        },
        "middle_pulldown": {
            "middle_pulldown": True
        },
        "ring_pulldown": {
            "ring_pulldown": True
        },
        "index_scissor": {
            "index_scissor": True,
            "thumb_scissor": False
        },
        "thumb_scissor": {
            "index_scissor": False,
            "thumb_scissor": True
        },
        "double_scissor": {
            "index_scissor": True,
            "thumb_scissor": True
        },
        "rocknroll": {
            "index_stretched": True,
            "middle_folded": True,
            "ring_folded": True,
            "pinky_stretched": True
        },
        "peace": {
            "thumb_folded":True,
            "index_stretched": True,
            "middle_stretched": True,
            "ring_folded": True,
            "pinky_folded": True
        },
        "resting" : {
            "hand_closed" : True 
        },
        "facing_camera": {
            "palm_facing_camera": True
        }
    },
    "body": {
        "extremity_up": {
            "up": True
        },
        "extremity_arm_left": {
            "arm_left": True
        },
        "extremity_arm_right": {
            "arm_right": True
        },
        "extremity_punch_left": {
            "punch_left": True
        },
        "extremity_punch_right": {
            "punch_right": True
        },
        "extremity_kick_left": {
            "kick_left": True
        },
        "extremity_kick_right": {
            "kick_right": True
        },
        "extremity_left_walking": {
            "left_walking" : True
        },
        "extremity_right_walking": {
            "right_walking" : True
        },
        "extremity_up_walking": {
            "up_walking" : True
        },
        "extremity_down_walking": {
            "down_walking" : True
        },
        "extremity_down_button": {
            "down_button" : True
        },
        "extremity_right_button": {
            "right_button" : True
        },
        "extremity_left_button": {
            "left_button" : True
        },
        "extremity_up_button": {
            "up_button" : True
        },
        "extremity_start_key": {
            "start_key" : True
        },
        "extremity_quit_key": {
            "quit_key" : True
        },
        "squating_down_state": {
            "squating_down": True
        },
        "walking_left_state": {
            "walking_left": True
        },
        "walking_right_state": {
            "walking_right": True
        }
    },
    "head": {
        "smiling_gesture": {
            "smiling": True
        },
        "fish_face_gesture": {
            "fish_face": True
        },
        "open_mouth_gesture": {
            "open_mouth": True
        },
        "raise_eye_brow_gesture": {
            "raise_eye_brow": True
        },
        "eyes_close_gesture": {
            "eyes_close": True
        },
        "turn_left_gesture": {
            "turn_left": True
        },
        "turn_right_gesture": {
            "turn_right": True
        },
        "nose_position_gesture": {
            "nose_point": True
        },
        "nose_right_gesture": {
            "nose_right": True,
            "fish_face": False
        },
        "nose_left_gesture": {
            "nose_left": True,
            "fish_face": False
        },
        "nose_up_gesture": {
            "nose_up": True,
            "smiling": False
        },
        "nose_down_gesture": {
            "nose_down": True,
            "smiling": False
        },
        "nose_scroll_up_gesture": {
            "smiling": True,
            "nose_up": True
        },
        "nose_scroll_down_gesture": {
            "smiling": True,
            "nose_down": True
        },
        "nose_zoom_in_gesture": {
            "fish_face": True,
            "nose_left": True
        },
        "nose_zoom_out_gesture": {
            "fish_face": True,
            "nose_right": True
        }
    },
    "eye": {
        "gaze_nose3d_gesture": {
            "gaze": True,
            "nose3d": True
        }
    },
    "speech": {
        "click": {
            "click": True
        },
        "double click": {
            "double click": True
        },
        "right click": {
            "right click": True
        },
        "save": {
            "save": True
        },
        "transcribe": {
            "transcribe": True
        },
        "stop transcribe": {
            "stop transcribe": True
        }
    }
}

MODES = {
    "default": "basic_hand",
    "iteration_order": {
        "idle_hand": "idle_hand",
        "basic_hand": "touchpoint_hand",
        "touchpoint_hand": "extremity_triggers",
        "extremity_triggers": "gaming_extremity_walking",
        "gaming_extremity_walking": "head_nose_position",
        "head_nose_position": "head_nose_direction",
        "head_nose_direction": "eye",
        "eye": "speech",
        "speech": "exercise_no_equipment",
        "exercise_no_equipment":  "exercise_equipment",
        "exercise_equipment": "basic_hand"
    },
    "modes": {
        "basic_hand": [
            "general_rocknroll_next_mode",
            "hand_palm_height_change_aoi_resize_left_hand",
            "hand_index_pulldown_left_press_left_hand",
            "hand_double_index_pinch_zoom",
            "hand_palm_center_move_mouse_left_hand",
            "hand_to_idle_mode_left_hand",
            "hand_middle_pinch_right_press_left_hand",
            "hand_pinky_pinch_monitor_change_left_hand",
            "hand_fist_doubleclick_left_hand",
            "hand_index_pinch_left_press_left_hand",
            "hand_index_middle_scroll_left_hand",
            "hand_open_keyboard_left_hand"
        ],
        "keyboard_hand":[
            "hand_mouse_switch_left_hand",
            "in_air_keyboard_click",
            "in_air_keyboard_active"
        ],
        "touchpoint_hand": [
            "general_rocknroll_next_mode",
            "hand_palm_center_move_mouse_left_hand",
            "hand_index_pinch_touch_press_left_hand",
            "hand_double_index_pinch_zoom",
            "hand_index_middle_scroll_left_hand"
        ],
        "idle_hand": [
            "hand_to_active_mode_left_hand"
        ],
        "extremity_triggers": [
            "general_rocknroll_next_mode",
            "extremity_punch_right",
            "extremity_up",
            "extremity_arm_right",
            "extremity_arm_left",
            "extremity_punch_left",
            "extremity_kick_left",
            "extremity_kick_right"
        ],
        "exercise_no_equipment": [
            "general_rocknroll_next_mode",
            "exercise_squating",
            "exercise_walking"
        ],
        "exercise_equipment": [
            "general_rocknroll_next_mode",
            "cycling_exercise"
        ],
        "extremity_walking": [
            "general_rocknroll_next_mode",
            "extremity_walking_event"
        ],
        "gaming_extremity_walking": [
            "general_rocknroll_next_mode",
            "gaming_extremity_walking_event"
        ],
        "speech": [
            "general_rocknroll_next_mode",
            "speech_double_clicking",
            "speech_clicking",
            "speech_right_clicking",
            "speech_hotkey_save",
            "speech_start_transcribe",
            "speech_stop_transcribe"
        ],
        "head_nose_position": [
            "general_rocknroll_next_mode",
            "head_open_mouth_left_press_hold_release",
            "head_nose_tracking",
            "head_raise_head_raise_eyebrows_double_click",
            "head_smile_right_click",
            "head_fishface_left_click"
        ],
        "head_nose_direction": [
            "general_rocknroll_next_mode",
            "head_smile_right_click",
            "head_nose_direction_tracking_nosebox",
            "head_open_mouth_left_press_hold_release",
            "head_raise_head_raise_eyebrows_double_click",
            "head_fishface_left_click",
            "head_nose_scroll",
            "head_nose_zoom"
        ],
        "eye": [
            "general_rocknroll_next_mode",
            "head_eye_tracking"
        ]
    }
}

