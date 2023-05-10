'''
Authors: Yan Lai, Tianhao Chen
'''
from .simple_gesture_event import SimpleGestureEvent
from scripts.tools.config import Config

config = Config()

class JoystickButtonPressEvent(SimpleGestureEvent):
    """Joystick button press event with the gesture_type specified.
    [trigger types]:
        "press": called when the gesture of interest becomes active IF a button has not been pressed.
        "release": called when the gesture of interest becomes unactive IF the button has been pressed.
    [bodypart types]:
        "hand": defined in the json file.
    [gestures types]:
        defined by the gesture_type arg.
    """
    _event_trigger_types = {"press", "release"}
    _bodypart_types = {"hand"}

    def __init__(self, button_name: str, gesture_type: str):
        super().__init__({gesture_type}, JoystickButtonPressEvent._event_trigger_types, JoystickButtonPressEvent._bodypart_types)
        self._button_name = button_name
        self._gesture_type = gesture_type
        self._gestures = {"hand": {gesture_type: None}}
        self._off_button_pressed = False
        self._dom_button_pressed = False

    def update(self):
        if self._hand_active_state and not self._off_button_pressed:
            self._off_button_pressed = True
            if self._event_triggers["press"] is not None:
                self._event_triggers["press"](self._button_name)
        elif self._hand_active_state == False and self._off_button_pressed:
            if self._gestures["hand"][self._gesture_type] is None:
                self._off_button_pressed = False
                if self._event_triggers["release"] is not None:  self._event_triggers["release"](self._button_name)

    def _check_state(self):
        self._state = 1
        self._check_hand_active_state()

    def _check_hand_active_state(self):
        self._hand_active_state = self._gestures["hand"][self._gesture_type] is not None



class JoystickWristEvent(SimpleGestureEvent):
    """Depending on user settings, moves either controller's sticks or presses triggers.
    
    sticks: Move the chosen stick by rotating the corresponding wrist.
            The motion of joystick is the same to your rotation.
    triggers: Press both triggers by rotating the chosen wrist.
              Intensity is 0 when hand is upright, increased when hand moves outwards (for both directions).
              default: Left trigger is pressed when hand moves left, right trigger is pressed when hand moves right.
              swap: Right trigger is pressed when hand moves left, left trigger is pressed when hand moves right.

    [trigger types]:
        "stick_move": called every frame after your wrist rotates.
        "joystick_left_trig": called every frame after your wrist rotates.
        "joystick_right_trig": called every frame after your wrist rotates.
    [bodypart types]:
        "hand": the angle between the vertical line and direction of four fingers is calculated for the hand.
    [gestures types]:
        "stretched": the current gesture used.
    """
    _event_trigger_types = {"stick_move","joystick_left_trig", "joystick_right_trig"}
    _bodypart_types = {"hand"}
    
    def __init__(self, analog_name:str, gesture_type:str, switch:str, mode:str):
        super().__init__({gesture_type},JoystickWristEvent._event_trigger_types, JoystickWristEvent._bodypart_types)
        self._n_frames_for_switch = max(2,config.get_data("events/joystick/settings/frames_for_switch"))
        self._last_hands_dist = None
        self._analog_name = analog_name
        self._gesture_type = gesture_type
        self._gestures={"hand":{gesture_type:None}}
        self._switch = switch
        self._mode = mode
        self._state = False
        self._set_ratios()

    def update(self):
        if self._state:
            if self._get_frames_held() >= self._n_frames_for_switch:            
                # FB -> front/back rotation; LR -> left/right rotation
                FB_ratio, LR_ratio = self._get_ratio()
                max_input_range_joystick = 32767
                max_input_range_trigger = 255
                
                if self._analog_name == "sticks":
                    if self._switch == "on":
                        # threshould tan(5)=0.0875 to ignore randon rotation
                        if abs(FB_ratio) > 0.0875 or abs(LR_ratio) > 0.0875:
                            self._stick_mapper(FB_ratio, LR_ratio, max_input_range_joystick)

                else: # triggers                    
                    if self._switch == "on":
                        # threshould tan(8.5)=0.15 to ignore randon rotation
                        if abs(LR_ratio) > 0.15:
                            self._trigger_mapper(LR_ratio, max_input_range_trigger)

    # FB_ratio is calculated by the change in z divided by change in y for the wirst and middle base
    def _stick_mapper(self, FB_ratio, LR_ratio, max_input_range_joystick):
        if FB_ratio > 0: # hand move forward
            FB_ratio = FB_ratio/self.ratio_stick_forward*max_input_range_joystick
            if FB_ratio > max_input_range_joystick: FB_ratio = max_input_range_joystick
        else: # hand move backward
            FB_ratio = FB_ratio/self.ratio_stick_backward*max_input_range_joystick
            if FB_ratio < -max_input_range_joystick: FB_ratio = -max_input_range_joystick
        if LR_ratio > 0: # hand move left
            LR_ratio = LR_ratio/self.ratio_stick_left*max_input_range_joystick
            if LR_ratio > max_input_range_joystick: LR_ratio = max_input_range_joystick
        else: # hand move right
            LR_ratio = LR_ratio/self.ratio_stick_right*max_input_range_joystick
            if LR_ratio < -max_input_range_joystick: LR_ratio = -max_input_range_joystick
        # input only accept int value
        FB_ratio = round(FB_ratio)
        LR_ratio = round(LR_ratio)
        self._event_triggers["stick_move"](-LR_ratio, FB_ratio)

    # LR_ratio is calculated by the change in x divided by change in y for the wrist and middle_base, 
    # which implys the angle between vertical line and palm direction
    def _trigger_mapper(self, LR_ratio, max_input_range_trigger):
        T = LR_ratio
        if self._mode == "default":
            if T > 0: # hand move left - press left trigger
                T = T/self.ratio_trigger_outwards*max_input_range_trigger
                if T > max_input_range_trigger: T = max_input_range_trigger
                # input only accept int value
                T = round(T)
                self._event_triggers["joystick_left_trig"](T)
                self._event_triggers["joystick_right_trig"](0)
            else: # hand move right - press right trigger
                T = T/self.ratio_trigger_inwards*max_input_range_trigger
                if T < -max_input_range_trigger: T = -max_input_range_trigger
                T = round(T)
                self._event_triggers["joystick_right_trig"](-T)
                self._event_triggers["joystick_left_trig"](0)
        else: # swap mode
            if T > 0: # hand move left - press right trigger
                T = T/self.ratio_trigger_inwards*max_input_range_trigger
                if T > max_input_range_trigger: T = max_input_range_trigger
                T = round(T)
                self._event_triggers["joystick_right_trig"](T)
                self._event_triggers["joystick_left_trig"](0)
            else: # hand move right - press left trigger
                T = T/self.ratio_trigger_outwards*max_input_range_trigger
                if T < -max_input_range_trigger: T = -max_input_range_trigger
                T = round(T)
                self._event_triggers["joystick_left_trig"](-T)
                self._event_triggers["joystick_right_trig"](0)

    def _check_state(self) -> bool:
        self._state = self._gestures["hand"]["stretched"] is not None

    def _get_ratio(self) -> float:
        # FB -> front/back rotation; LR -> left/right rotation
        # the ratio is the tan value of the angle
        hand = self._gestures["hand"]["stretched"]
        position= hand.get_last_position()
        FB_ratio = position.get_palm_front_back_tilt()  
        LR_ratio = position.get_palm_left_right_tilt()
        return FB_ratio, LR_ratio

    def _get_frames_held(self) -> int:
        hand = self._gestures["hand"]["stretched"]
        return hand.get_frames_held()

    def _set_ratios(self) -> None: # sensitivity configuration
        self.ratio_stick_left = config.get_data("events/joystick/ratios/stick_left")
        self.ratio_stick_right = config.get_data("events/joystick/ratios/stick_right")
        self.ratio_stick_forward = config.get_data("events/joystick/ratios/stick_forward")
        self.ratio_stick_backward = config.get_data("events/joystick/ratios/stick_backward")
        self.ratio_trigger_outwards = config.get_data("events/joystick/ratios/trigger_outwards")
        self.ratio_trigger_inwards = config.get_data("events/joystick/ratios/trigger_inwards")
