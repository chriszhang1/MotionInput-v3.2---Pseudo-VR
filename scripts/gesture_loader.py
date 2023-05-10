'''
Author: Carmen Meinson
'''
from scripts.eye_module import EyeModule
from scripts.core.model import Model
from typing import Set

from scripts.hand_module import HandModule
from scripts.body_module import BodyModule

from scripts.speech_module import SpeechModule
from scripts.head_module import HeadModule

from scripts.tools.json_editors.gesture_editor import GestureEditor
from scripts.tools.config import Config

# # we may need to split into no_equipment and equipment, because apparently the ML classification may overlap and mistake equipment and no equipment events e.g. squatting and rowing
# # alternatively the GUI can just ensure that the user just can't select both modes, so only exercises of one mode are loaded

class GestureLoader:
    def __init__(self):
        gesture_editor = GestureEditor()
        self._gestures = gesture_editor.get_all_data()

        self._modules = {
            "hand": HandModule,
            "speech": SpeechModule,
            "body": BodyModule,
            "head": HeadModule,
            "eye": EyeModule
        }

    def add_gestures_to_model(self, model: Model, gesture_names: Set[str]) -> None:
        """Based on the given gesture names, add the desired gestures to the model as well as the moules used by said gestures

        :param model: model to add the gestures to
        :type model: Model
        :param gesture_names: names of the gestures to add
        :type gesture_names: Set[str]
        """
        for gesture_name in gesture_names:
            for module_name in self._gestures:
                if gesture_name in self._gestures[module_name]:
                    if module_name not in model.get_module_names():

                        module_instance = self._modules[module_name]()
                        run_calibration = Config().get_data("modules/%s/run_calibration"%module_name)

                        if run_calibration:
                            module_instance.calibrate()

                        model.add_module(module_name, module_instance)
                    model.add_gesture(module_name, gesture_name, self._gestures[module_name][gesture_name])
        
