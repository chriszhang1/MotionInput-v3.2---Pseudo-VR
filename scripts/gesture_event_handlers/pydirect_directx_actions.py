'''
Author: Jason Ho
'''
# Standard
from typing import Callable, Tuple
import threading

# Third Party
import pydirectinput


class Keyboard:
    def key_press(self, key: str) -> None:
        """Performs a keypress as a DirectX action.
        
        :param key: name of key to press
        :type key: str
        """
        self._run_thread(pydirectinput.press, (key,))
        
    def key_down(self, key: str) -> None:
        """Performs a keydown as a DirectX action.
        
        :param key: name of key for keydown
        :type key: str
        """
        self._run_thread(pydirectinput.keyDown, (key,))
        
    def key_up(self, key: str) -> None:
        """Performs a keyup as a DirectX action.
        
        :param key: name of key for keyuo
        :type key: str
        """
        self._run_thread(pydirectinput.keyUp, (key,))

    def _run_thread(self, method: Callable, args: Tuple) -> None:
        threading.Thread(target=method, args=args, name="Pydirect_direct_actions").start()

class Clicker:
    def left_click(self) -> None:
        """Performs a left click as a DirectX action.
        """
        threading.Thread(target=self._click, name="Pydirect_direct_actions: left_click", args=()).start()
    
    def right_click(self) -> None:
        """Performs a left click as a DirectX action.
        """
        threading.Thread(target=self._click, name="Pydirect_direct_actions: right_click", args=("right",)).start()

    def _click(self, click="left") -> None:
        if click == "left":
            pydirectinput.click()
        else:
            pydirectinput.click(button="right")