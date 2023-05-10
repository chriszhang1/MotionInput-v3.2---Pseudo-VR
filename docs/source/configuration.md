# Configuration
Settings that are unique to each users can be configured by editing the four JSON files located in the data directory. For the time being these settings can only be changed manually, however the aim is to be able to update them during runtime. The four JSON files are responsible for holding information about:
* [Gestures](https://motioninput.github.io/configuration.html#gestures)
* [Events](https://motioninput.github.io/configuration.html#events)
* [Modes](https://motioninput.github.io/configuration.html#modes)
* [General Settings](https://motioninput.github.io/configuration.html#config)

Developers can read values from these JSON files using the JSONEditor classes.

## Gestures

Gestures are composed of primitives which are either activated or deactivated, represented by a boolean value.

The gestures are split between the separate modules:

* hand
* body
* head
* eye
* speech

A gesture will be of the form:

```
"gesture_name": {
	"primitive_1": bool,
	"primitive_2": bool,
	"primitive_3": bool,
	...
}
```
## Events

The events are mappings of [GestureEvent](https://motioninput.github.io/apidocs/scripts.gesture_events.html) classes to [event handlers](https://motioninput.github.io/apidocs/scripts.gesture_event_handlers.html) method(s).

The GestureEvent class ("type") determines under what conditions and when will the handler methods ("triggers") be called. These conditions can be modified by the "args" if the conditions are event instance-specific or by elements in the config file if those conditions are event class-specific.

The "bodypart_names_to_type" determines what detected body parts (aka trackers in the modules like "Left"(hand), "Right"(hand) or "head") will be used by the event instances. This is mostly used to determine the hand used in hand gestures.

The "triggers" are pairs of handler classes and its methods that we want to be called when the event calls its trigger functions.
All available methods are well visible in the \_\_init\_\_.py in gesture_event_handlers

An event will be of the form:

```
"event_name": {
	"type": "GestureEvent_class_name",
	"args": {
		"arg_1": val,
		"arg_2": val,
		...
	},
	"bodypart_names_to_type": {
		"modules_tracker_name_1": "events_bodypart_name",
		...
	},
	"triggers": {
		"trigger_1_name": ["GestureEventHandler_class_name","method_name"],
		"trigger_2_name": ["GestureEventHandler_class_name","method_name"],
		...
	}
}
```

### Currently available Events

Note: in case the gesture names are unclear pleas refer to the data/gestures.json to see the exact primitives they are comprised of.

* `hand_to_idle_mode_left_hand`: Changes the mode to "idle_hand" whenever the left palm is not facing the camera
* `hand_to_active_mode_left_hand`: Changes the mode to "basic_hand" whenever the left palm is facing the camera
* `general_rocknroll_next_mode`: By doing the rocknroll gesture on both hands the mode is changed to the next one according to the set iteration order
* `hand_palm_height_change_aoi_resize_left_hand`: Updates the size of the AOI based on the size of the palm (so by how far it is from the camera)
* `hand_palm_center_move_mouse_left_hand`: Movinge the cursor according to the center of the palm
* `hand_index_pinch_left_press_left_hand`: Left click by pinching the index finger
* `hand_index_pinch_touch_press_left_hand`:  Touchpoint press by pinching the index finger
* `hand_middle_pinch_right_press_left_hand`: Right click by pinching the middle finger
* `hand_pinky_pinch_monitor_change_left_hand`: Changing the display the mouse is moved on by pinching the pinky finger
* `hand_double_pinch_double_click_left_hand`: Doubleclick by pinching both the index and the middle finger
* `hand_index_pulldown_left_press_left_hand`: Left click by lowering the tip of the index finger below its upper joint (DIP joint)
* `hand_index_scissor_left_press_left_hand`: Left click by touching the index finger to the middle finger
* `hand_thumb_scissor_right_press_left_hand`: Right click by touching the thumb to the index finger
* `hand_double_scissor_doubleclick_left_hand`: Double click by pressing the thumb, index and middle finger against each other
* `hand_fist_doubleclick_left_hand`: Doubleclick by clenching the fist
* `hand_index_middle_scroll_left_hand`: Scrolling by holding up only the index and middle fingers and moving them up or down together
* `hand_double_index_pinch_zoom`: Zooming by holding index pinched on both hands and moving the hands closer together or apart
* `extremity_up`: Extremity circle activated by the nose landmark
* `extremity_arm_left`: Extremity circle activated by the left wrist landmark
* `extremity_punch_left`: Extremity circle activated by the left wrist landmark (intended to be outstretched arm compared to arm_left)
* `extremity_kick_left`: Extremity circle activated by the left ankle landmark
* `extremity_arm_right`: Extremity circle activated by the right wrist landmark
* `extremity_punch_right`:  Extremity circle activated by the right wrist landmark (intended to be outstretched arm compared to arm_right)
* `extremity_kick_right`: Extremity circle activated by the right ankle landmark
* `extremity_left_walking`: Extremity circle activated by the left wrist landmark (Gamepad mode, left D-Pad, used with walking on spot)
* `extremity_right_walking`: Extremity circle activated by the left wrist landmark (Gamepad mode, right D-Pad, used with walking on spot)
* `extremity_up_walking`: Extremity circle activated by the left wrist landmark (Gamepad mode, up D-Pad, used with walking on spot)
* `extremity_down_walking`: Extremity circle activated by the left wrist landmark (Gamepad mode, down D-Pad, used with walking on spot)
* `extremity_left_button`: Extremity circle activated by the right wrist landmark (Gamepad mode, left D-Pad)
* `extremity_right_button`: Extremity circle activated by the right wrist landmark (Gamepad mode, right D-Pad)
* `extremity_up_button`: Extremity circle activated by the right wrist landmark (Gamepad mode, up D-Pad)
* `extremity_down_button`: Extremity circle activated by the right wrist landmark (Gamepad mode, down D-Pad)
* `extremity_quit_key`: Extremity circle activated by the right ankle landmark (Gamepad mode, button intended for end program/game keybind)
* `extremity_start_key`: Extremity circle activated by the left wrist landmark (Gamepad mode, button intended for start program/game keybind)
* `exercise_walking`: Exercise activated by walking on the spot
* `exercise_squating`: Exercise activated by squatting
* `gamepad_mode_1_event`: 1st gamepad mode: Walking D-Pad changes current keybind for walking.
* `gamepad_mode_2_event`: 2nd gamepad mode: Walking D-Pad needs to be held with walking on the spot to move.
* `gamepad_mode_3_event`: 2nd gamepad mode: Walking set to the keybind of the up trigger (not shown). Other triggers are all buttons.
* `speech_clicking`: Saying click implements a left click
* `speech_double_clicking`: Saying double click implements a double left click   
* `head_smile_right_click`: Right click when smiling (widening lips)
* `head_fishface_left_click`: Left click when making fish face (lips forming a circle)
* `head_open_mouth_left_press_hold_release`: Right click press when opening mouth, left click release when closing
* `head_raise_head_raise_eyebrows_double_click`: Double left click when raising eyebrows
* `head_nose_tracking`: Continuously moving cursor to a position on screen corresponding to your nose position on the camera preview.
* `head_nose_direction_tracking`: Moving cursor in the direction of a vector starting in the centre of the nose box and ending in a nose tip (aka nose grid mode)
* `head_nose_direction_tracking_nosebox`: Moving cursor in the direction of a vector starting in the centre of the nose box and ending in a nose tip (aka nose grid mode)
* `head_nose_scroll`: Scrolling down when smiling and moving nose down, scrolling up when smiling and moving nose up
* `head_nose_zoom`: Zooming in when smiling and moving nose left, zooming out when smiling and moving nose right
* `head_eye_tracking`: Moving cursor in the direction of a vector produced by the user's eye gaze (aka floating mouse)
* `eye_mode_2`: Moving cursor in the in one of four basic directions (UP, DOWN, LEFT or RIGHT) based on the vector produced by the
user's eye gaze (aka eye grid mode)
* `in_air_keyboard_active_event`: Activates the in air keyboard. Move fingers over keys, when palms are facing the camera, to hover over them
* `in_air_keyboard_click_event`: Press a key on the in air keyboard by hovering over a key and performing selected click gesture (pulldown, pinch or scissor). Hold down the key by holding the click gesture for at least the selected duration (3s by default)
* `pen_active_right_hand`: Moves the pen cursor while the right palm is facing the camera
* `pen_index_pinch_right_hand`: Simulates pen input when pinching index finger (hold pinch and move hand for dragging/ink strokes)
* `pen_index_pinch_eraser_left_hand`: Activates eraser when pinching index finger
* `pen_pinch_hold_right_hand`: Allows inking whilst holding a pen as long as index finger is close to thumb and pinky finger is folded


## Modes

The modes determine the sets of [events](https://motioninput.github.io/configuration.html#events) that are available to the user at any one time. When the MI starts the events from the "default" mode are loaded into the model and then afterwards the user can switch between modes in one of the following ways:

1. By having an event with the "trigger" ["ModeChange","mode_name"]. This handler sets the mode to whatever mode name is specified.
2.  By having an event with the "trigger" ["IterativeModeChange",""]. This handler sets the mode to whichever one follows the current order specified in the "iteration_order".
3. If using the GUI then it will be possible to request the mode change through the protocol.

The "iteration_order" should contain every mode name that is listed in the "modes" with another mode name from there. Ideally, the iteration orders should make one or multiple closed loops (possibly of size 1 if changing from that mode does not make sense) meaning it should be possible to get back to the mode where the user started.

The JSON file has the following format:

```
"default": "mode_name",
"iteration_order": {
	"mode_name_1": "mode_name_2",
	"mode_name_2": "mode_name_1",
	"mode_name_3": "mode_name_3",
	...
	},
"modes": {
	"mode_name_1":[
		"event_name_1",
		"event_name_2"
		...
	],
	"mode_name_2": [
		"event_name_1",
		...
	],
	...
}
```

## Config

### General
Non-specific higher level settings:
```
"general": {
        "view": {
            "window_name": "UCL MotionInput v3.0"
        }
		...
    }
```

### Events
Event configs hold settings for a given event:
```
"event": {
	"event_val_1" : 1,
	"event_val_2" : 1,
	...
} 	
```

#### Pinch Events
```
"index_pinch": {
	"frames_for_press": 2
},
"middle_pinch": {
	"frames_for_press": 2
},
"double_pinch": {
	"frames_for_press": 2
},
"index_pulldown": {
	"frames_for_press": 2
}
```
* `frames_for_press`: The amount of frames the gesture needs to be active to trigger a press.

#### Idle Event
```
"idle_state_change": {
	"frames_for_switch": 10
}
```
* `frames_for_switch`: The amount of frames the idle event needs to be active to switch to idle mode (turn off area of interest and stop looking for gestures other than the active gesture).

#### Palm Height Change Event
```
"palm_height_change": {
	"frames_for_switch": 10,
	"levels": [
		0,
		0.105,
		0.155
	]
},
```
* `frames_for_switch`: The amount of frames the palm change gesture needs to be active for the palm height to be registered as changed.
* `levels`: The different palm height levels, being outside of your current level for 10 frames will cause your current level to update.

#### Scroll Event
```
"scroll": {
	"frames_for_switch": 2,
	"index_middle_distance_threshold": 0.3
},
```
* `frames_for_switch`: The number of frames the scroll gesture needs to be active to cause the scroll action.
* `index_middle_distance`: The threshold used for determining whether the middle and index fingers are together.

#### Zoom Event
```
"zoom": {
	"frames_for_switch": 4
},
```
* `frames_for_switch`: The number of frames the zoom gesture needs to be active to cause the zoom action.

#### Mode Change Event
```
"mode_change": {
	"frames_for_switch": 4
}
```
* `frames_for_switch`: The number of frames the mode switch gesture needs to be active to switch to the next mode.

#### Nose Tracking
```
"nose_tracking": {
            "scaling_factor": 400,
            "nose_box_percentage_size": 0.04
        },
```
* `scaling_factor`: defines speed of the cursor during nose direction tracking 
* `nose_box_percentage_size`: defines the size of the half of the nose box (e.g. `0.04` means that the nose box will have the size of `(camera_width\*0.08, camera_height\*0.08)`)

### Modules
Holds information for each of the different modules.

#### Hand
* `position_pinch_sensitivity`: The sensitivity of pinch events.

* `position_threshold_distance`:  Threshold used for determining whether or not a finger is folded.

* `min_detection_confidence`: Minimum confidence value from the hand detection model for the detection to be considered successful.

* `min_tracking_confidence`: Minimum confidence value from the landmark-tracking model for the hand landmarks to be considered tracked successfully.

* `max_num_hands`: The maximum number of hands used by MI

#### Exercise
`mode`: Whether equipment is being used or not, can be `noequipment` or `equipment`.

### Body Gestures
Holds information about extremity triggers and exercise gestures.

#### Extremity Triggers
Represents information of an extremity trigger, of the form:
```
"trigger_name": {
	"landmark": "trigger_landmark",
	"coordinates": [x,y],
	"action": "trigger_action",
	"key": "trigger_key",
	"activated": true/false
},
```
* `landmark`: Which body part can activate the extremity trigger.
* `coordinates`: The position of the extremity trigger on the view.
* `action`:  What activating the extremity trigger does.
* `key`: What key the extremity trigger presses/holds down.
* `activated`: Whether or not the extremity trigger is used

#### Exercise
Holds information about exercise gestures, seperated by exercises using equipment and exercises without equipment.
```
"exercise_name": {
	"states": {
		"state_1": {
			"activated": true/false,
			"val" : 1
		},
		"state_2": {
			"activated": true/false,
			"val" : 1
		}
	"action": "exercise_action",
	"key": "exercise_key",
	"count": 1
}
```
* `states`: The different gestures that make up an exercises.
	* `activated`: Whether or not the state is active.
	* `val`: Each state has a counter, this value holds the starting count (soon to be removed)
* `action`: What performing the exercise does.
* `key`: Whether activating the exercise presses/holds down a key.
* `count`: Each exercise has a counter representing how many times the exercise has been carried out, this value holds the starting count.
* `activated`: Whether or not the exercise is used

### Handlers
Holds information on all of the event handlers.

#### Area of Interest
```
"aoi": {
	"spacing_levels": [
		0.3,
		0.4,
		0.5
	]
}
```
* `spacing_levels_`: The size scalers of the area of interest.

#### Mouse
```
"mouse": {
	"smoothing": 3,
	"sensitivity": 3
}
```
* `smoothing`: How smooth mouse movements are.
* `sensitivity`: Mouse sensitivity.

#### Finger
 ```
 "finger": {
	"radius": 5
}
```
* `radius`: The radius of the circle that can be made by the finger.

#### Zoom
```
"zoom": {
	"smoothing": 3
}
```
* `smoothing`: The smoothness of the zoom action
