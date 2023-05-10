
"""
Author: Alexandros Theofanous
"""

from scripts.tools import Config

class EditConfigFile:

    def __init__(self):
        self._config = Config()

    def switch_boolean(self, path):
        # switch a boolean value in config.json
        status = self._config.get_data(path)
        config_editor = self._config.get_editor()
        if status:
            config_editor.update(path, "false")
        else:
            config_editor.update(path, "true")

    def get_value(self,path):
        return (self._config.get_data(path))

    def set_value(self, path, value):
        # switch a boolean value in config.json
        config_editor = self._config.get_editor()
        config_editor.update(path, value)
