'''
Author: Carmen Meinson
'''
from typing import Any, Optional
from scripts.tools.json_editors.config_editor import ConfigEditor

# Config class is a singelton so that whatever class needs some configuration it can just do Config() instead of having a bunch of parameters
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class Config():
    def __init__(self):
        self._config_editor = ConfigEditor()
    
    def get_data(self, key: str) -> Optional[Any]:
        """Returns value paired with an inputted key in the config dictionary.
        :return: value associated with inputted key string
        :rtype: Optional[Any]"""
        return self._config_editor.get_data(key)

    def get_editor(self) -> ConfigEditor:
        return self._config_editor


            

