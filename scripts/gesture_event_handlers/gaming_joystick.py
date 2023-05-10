'''
Author: Yan Lai
'''

import vgamepad as vg

class GamingJoystick:
    """trigger the function call with the Vgamepad function"""
    def __init__(self) -> None:
        self.gamepad = vg.VX360Gamepad()

    def press_action(self, button_name: str):
        if button_name == "up":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
        elif button_name == "down":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        elif button_name == "left":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
        elif button_name == "right":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
        elif button_name == "s_left":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        elif button_name == "s_right":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
        elif button_name == "a":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        elif button_name == "b":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        elif button_name == "x":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        elif button_name == "y":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
        elif button_name == "start":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
        elif button_name == "back":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
        
        self.gamepad.update()

    def release_action(self, button_name: str):
        if button_name == "up":
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
        elif button_name == "down":
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        elif button_name == "left":
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
        elif button_name == "right":
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
        elif button_name == "s_left":
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        elif button_name == "s_right":
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
        elif button_name == "a":
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        elif button_name == "b":
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        elif button_name == "x":
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        elif button_name == "y":
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
        elif button_name == "start":
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
        elif button_name == "back":
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
        
        self.gamepad.update()

    def joystick_left_move(self, x_value: int, y_value: int):  # int values between -32768 and 32767
        self.gamepad.left_joystick(x_value, y_value)
        self.gamepad.update()

    def joystick_right_move(self, x_value :int, y_value: int):  # int values between -32768 and 32767
        self.gamepad.right_joystick(x_value, y_value)
        self.gamepad.update()

    def joystick_left_trigger(self, value: int): # int values between 0 and 255
        self.gamepad.left_trigger(value)

    def joystick_right_trigger(self, value: int): # int values between 0 and 255
        self.gamepad.right_trigger(value)
