'''
Authors: Siam Islam and Keyur Narotomo
'''

import webbrowser
from bisect import bisect_left
from .transcription import Transcriber
from .keyboard import Keyboard
from scripts.tools import Config
from scripts.tools.view import View
from scripts.tools.json_editors.in_air_keyboard_editor import InAirKeyboardEditor


class Button:

    """ 
    A class used to represent a sqaure button. 
    
    :param text: text to display on the button
    :type text: str
    :param x: x position of the top left corner
    :type x: int
    :param y: y position of the top left corner
    :type y: int
    :param width: width of the button
    :type width: int
    :param height: height of the button
    :type height: int
    :param font_size: size of the text in the button
    :type font_size: float
    :param bg_colour: background colour of the button in RBG format
    :type bg_colour: list[int, int, int]
    :param action: action to perform when the button is clicked, None if no special action is required
    :type action: list
    """

    def __init__(self, text: str, x: int, y: int, width: int, height: int, font_size: float, bg_colour: list[int, int, int], action: list) -> None:
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_size = font_size
        self.bg_colour = bg_colour
        self.action = action

    def get_position(self) -> tuple[int, int]:
        
        """
        Gets the coordinates of the top left corner.

        :return: (x,y)
        :rtype: tuple[int, int]
        """

        return (self.x, self.y)

    def get_size(self) -> tuple[int, int]:

        """
        Gets the width and height of the button.

        :return: (width, height)
        :rtype: tuple[int, int]
        """

        return (self.width, self.height)


class KeyboardLoader:

    """
    A class for storing and initialising all the data needed for the in air keyboard.
    """

    def __init__(self) -> None:
        self.single_tap_min = None
        self.single_tap_max = None
        self.hold_min_duration = None
        self.default_key_font_size = None
        self.default_key_width = None
        self.default_key_height = None
        self.default_key_bg_colour = None
        self.gesture_type = None
        self.landmarks = None
        self.keyboard_layouts = None
        self.holdable_special_keys = None
        self.current_keyboard_layout = None
        self.all_keys = None
        self.load_from_config()
        self.load_fron_in_air_keyboard()

    def load_from_config(self) -> None:

        """
        Initialises the in air keyboard by getting all the data from
        data/config.json.
        """

        config = Config()
        self.single_tap_min = config.get_data("events/keyboard/single_tap_min_bound")
        self.single_tap_max = config.get_data("events/keyboard/single_tap_max_bound")
        self.hold_min_duration = config.get_data("events/keyboard/hold_press_min_duration")
        self.default_key_font_size = config.get_data("events/keyboard/default_key_font_size")
        self.default_key_width = config.get_data("events/keyboard/default_key_width")
        self.default_key_height = config.get_data("events/keyboard/default_key_height")
        self.default_key_bg_colour = config.get_data("events/keyboard/default_key_bg_colour")
        self.gesture_type = "_" + config.get_data("events/keyboard/gesture_type")
        self.landmarks = config.get_data("events/keyboard/landmarks")

    def load_fron_in_air_keyboard(self) -> None:

        """
        Initialises the in air keyboard by getting all the data from
        data/in_air_keyboard.json.
        """

        keyboard_data = InAirKeyboardEditor()
        self.keyboard_layouts = keyboard_data.get_data("layouts")
        self.holdable_special_keys = set(keyboard_data.get_data("holdable_special_keys"))
        first_layout = next(iter(self.keyboard_layouts))
        self.current_keyboard_layout = self.keyboard_layouts[first_layout]
        self.all_keys = keyboard_data.get_data("keys")


class InAirKeyboard:

    """
    A class used to represent an in air keyboard.

    :param view: the window that the in air keyboard is to be displayed on
    :type view: View
    :param keyboard: instance of keyboard object used for pressing keys and performing key combinations
    :type keyboard: Keyboard
    :param kita_transcriber: instance of Ask Kita Transcriber object used for transcription
    :type kita_transcriber: Transcriber
    """

    def __init__(self, view: View, keyboard: Keyboard, kita_transcriber: Transcriber) -> None:
        self.view = view
        self.kb = keyboard
        self.caps_lock = False
        self.buttons = None
        self.button_x_coords = None
        self.button_y_coords = None
        self.hands = {}
        self.actions = {
            "link": self.open_link,
            "speech_to_text": self.speech_to_text,
            "press_special": self.press_special_key,
            "toggle_caps_lock": self.toggle_caps_lock,
            "switch_layout": self.switch_keyboard_layout,
            "press_special_combination": self.kb.key_combination,
        }

        self.keyboard_loader = KeyboardLoader()
        self.kita = kita_transcriber
        self.initialise_hands()
        self.update_buttons(self.keyboard_loader.current_keyboard_layout)
        

    def initialise_hands(self) -> None:

        """
        Initliases the data strucuture required for validating key presses from click gestures.
        """

        hands = {"dom_hand", "off_hand"}
        for hand in hands:
            self.hands[hand] = {}
            self.hands[hand]["pressed"] = {}
            self.hands[hand]["key_activate"] = {}
            self.hands[hand]["time_held"] = {}
            self.hands[hand]["last_key"] = {}
            for landmark in self.keyboard_loader.landmarks:
                gesture = landmark + self.keyboard_loader.gesture_type
                self.hands[hand]["pressed"][gesture] = False
                self.hands[hand]["key_activate"][gesture] = False
                self.hands[hand]["time_held"][gesture] = 0
                self.hands[hand]["last_key"][gesture] = None


    def update_buttons(self, layout: list[str]) -> None:
                
        """
        Creates a button for each key in layout.

        :param layout: keys you want to create buttons for
        :type text: list[str]
        """
        self.button_x_coords = []
        self.button_y_coords = {}
        self.buttons = {}

        for key in layout:
            button = self.create_button(key)
            self.update_button_coordinates(button)

        self.button_x_coords.sort()

        for lst in self.button_y_coords.values():
            lst.sort()


    def create_button(self, key: str) -> None:
        key_details = self.keyboard_loader.all_keys[key]
        action = None
        if "action" in key_details:
            action = key_details["action"]
        if self.caps_lock and action is None:
            key = key.upper()
        width, height, font_size, bg_colour = self.get_attributes(key_details)
        return Button(key, key_details["x"], key_details["y"], width, height, font_size, bg_colour, action)


    def update_button_coordinates(self, button: Button) -> None:
        center_x = button.x + button.width/2
        center_y = button.y + button.height/2
        self.buttons[(center_x, center_y)] = button
        self.button_x_coords.append(center_x)

        if center_x not in self.button_y_coords:
            self.button_y_coords[center_x] = [center_y]
        else: 
            self.button_y_coords[center_x].append(center_y)
        

    def get_attributes(self, key_details: dict) -> list:
        
        """
        Gets the attributes required for creating a button.

        :param key_details: details of the key stored in data/in_air_keyboard.json
        :type key_details: dict
        :return: [width, height, font_size, bg_colour]
        :rtype: list
        """

        attributes = [
            ["width", int, self.keyboard_loader.default_key_width], 
            ["height", int, self.keyboard_loader.default_key_height], 
            ["font_size", float, self.keyboard_loader.default_key_font_size],
            ["bg_colour", list, self.keyboard_loader.default_key_bg_colour]
        ]

        for attribute in attributes:
            name, instance = attribute[0], attribute[1]
            if name in key_details:
                if isinstance(key_details[name], instance):
                    attribute[2] = key_details[name]
                else:
                    raise RuntimeError("Unknown key " + name)
        return [attribute[2] for attribute in attributes]

    def toggle_caps_lock(self) -> None:
        self.caps_lock = not self.caps_lock
        self.update_buttons(self.keyboard_loader.current_keyboard_layout)

    def press_special_key(self, key: str) -> None:
        self.kb.press(self.kb.special_keys[key])


    def open_link(self, link: str) -> None:
        webbrowser.open(link)


    def switch_keyboard_layout(self, layout: list[str]) -> None:
        try:
            layout = self.keyboard_loader.keyboard_layouts[layout]
        except: 
            raise RuntimeError("Unknown keyboard layout")
        self.keyboard_loader.current_keyboard_layout = layout
        self.update_buttons(self.keyboard_loader.current_keyboard_layout)


    def speech_to_text(self) -> None:
        """ This is not KITA as a whole, it is only the Transcriber """
        if self.kita.is_running():
            self.kita.stop_transcribe()
        else:
            self.kita.start_transcribe()


    def click(self, hand: str, gesture: str, time_held: float) -> None:
        self.hands[hand]["key_activate"][gesture] = True
        self.hands[hand]["time_held"][gesture] = time_held


    def release(self, hand: str, gesture: str) -> None:
        self.hands[hand]["key_activate"][gesture] = False
        self.hands[hand]["time_held"][gesture] = None


    def key_selection(self, landmarks: dict) -> None:

        """
        Checks if the specified landmarks are currently hovering over a key, or if a key is being clicked,
        every frame, and passes the set of hovered and clicked keys to the view to update the display
        accordingly.

        :param landmarks: a dictionary storing the required landmark coordinates for multitouch
        :type landmarks: dict
        """

        hovered_keys = set()
        pressed_keys = set()
         # storing clicked keys (that have a count of 1) in a seperate set, using the same set for view
         # results in clicked key state appearing for a single frame
        keys_to_click = set()
        
        for hand, landmark_set in landmarks.items():
            for landmark in landmark_set:
                position, button = self.get_closest_key(landmark)
                if self.check_if_inside_button_boundary(position, button):
                    # get name of finger (finger tips are used for tracking position)
                    gesture = landmark[2][:-4] + self.keyboard_loader.gesture_type
                    if self.hands[hand]["key_activate"][gesture] is True :
                        hovered_keys.add(button)
                        self.check_clicks(hand, gesture, button, pressed_keys, keys_to_click)
                    else:
                        hovered_keys.add(button)
                        # storing the last hovered key for each gesture
                        # to prevent accidentally clicking another key when performing click gesture
                        self.hands[hand]["last_key"][gesture] = button 
                        self.hands[hand]["pressed"][gesture] = False
        
        self.view.update_display_element("in_air_keyboard_element", {"buttons":self.buttons,"hovered_keys":hovered_keys, "clicked_keys": pressed_keys})
        self.click_buttons(keys_to_click)


    def check_clicks(self, hand: str, gesture: str, button: Button, pressed_keys: set, keys_to_click: set) -> None:

        """
        Uses time held value for a given gesture to determine whether to click keys, and to differentiate between
        doing a single press and key hold.
        """

        time_held = self.hands[hand]["time_held"][gesture]
        single_tap = self.keyboard_loader.single_tap_min <= time_held <= self.keyboard_loader.single_tap_max
        if single_tap or time_held >= self.keyboard_loader.hold_min_duration:
            last_key = self.hands[hand]["last_key"][gesture]
            if single_tap:
                 # the pressed flag is used to prevent a clicked key from being pressed multiple times 
                 # when the user intends to only perform a single click
                if not self.hands[hand]["pressed"][gesture]:
                    self.hands[hand]["pressed"][gesture] = True
                    if last_key is not None:
                        keys_to_click.add(last_key)
                pressed_keys.add(last_key)
            else:
                if button.action is None or button.text in self.keyboard_loader.holdable_special_keys:
                    keys_to_click.add(last_key)
                    pressed_keys.add(last_key)


    def get_closest_key(self, landmark: tuple[float, float]) -> tuple[tuple, Button]:

        """
        For a given landmark, finds the closest button in the current layout. It first finds
        the closest x-coordinate to the landmark from all buttons in the current layout and then finds 
        the closest y-coordinate from the buttons with just that x-coordinate.

        :param landmark: a tuple of floats storing x,y coordinates for the given landmark
        :type landmark: tuple[float, float]
        :return landmark_position, button: returns landmark position relative to camera window and the closest button
        :rtype: tuple[float, float], Button
        """

        landmark_position = (landmark[0] * self.view._width, landmark[1] * self.view._height)
        closest_x = self.find_closest_value(landmark_position[0], self.button_x_coords)
        closest_y = self.find_closest_value(landmark_position[1], self.button_y_coords[closest_x])
        button = self.buttons.get((closest_x, closest_y))
        return landmark_position, button


    def find_closest_value(self, num: float, lst: list) -> float:

        """
        Searches through the pre-sorted input list of floats to find the point of insertion
        for the input number, using bisect_left, and then returns whichever value is closest to the input by comparing
        against adjacent values.
        """

        index = bisect_left(lst, num)
        if index == 0:
            return lst[0]
        elif index == len(lst):
            return lst[-1]
        else:
            prev_value = lst[index-1]
            next_value = lst[index]
            if (num - prev_value) <= (next_value - num):
                return prev_value
            else: 
                return next_value
    

    def check_if_inside_button_boundary(self, position: tuple[float,float], button: Button) -> bool:
        check_width = button.x <= position[0] <= (button.x + button.width)
        return check_width and (button.y <= position[1] <= (button.y + button.height))


    def click_buttons(self, buttons: list[Button]) -> None:
        for button in buttons:
            if button is not None:
                if button.action is not None:
                    function, args = button.action
                    # call the function by using the factory design pattern
                    # then unpack the args into it
                    self.actions[function](*args)
                else:
                    self.kb.press(button.text)


    def get_key_details(self, button: Button) -> dict:
        if button.text not in self.keyboard_loader.all_keys:
            # if the text of the button is not in self.keyboard_loader.all_keys 
            # then it is either an invalid button or the user has caps lock on 
            # so check to see if the lowercase version is in 
            # self.keyboard_loader.all_keys
            try:
                return self.keyboard_loader.all_keys[button.text.lower()]
            except KeyError:
                raise RuntimeError("Unknown Key Text: " + button.text)
        return self.keyboard_loader.all_keys[button.text]
        

    def clear_keyboard_keys(self) -> None:
        self.view.update_display_element("in_air_keyboard_element", {"buttons":{},"hovered_keys": set(), "clicked_keys": set()})