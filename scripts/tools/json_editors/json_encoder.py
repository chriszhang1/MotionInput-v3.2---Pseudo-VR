'''
Author: Oluwaponmile Femi-Sunmaila
Contributor: Anelia Gaydardzhieva
Comments:
Customises set data to list and datetime to custom str format
'''
from datetime import datetime
import json
from time import strftime
# Encodes sets into lists, because JSON does not like sets.
from typing import Dict, Any
# TODO: Handle 

class JSONEncoder(json.JSONEncoder):
    """ Class that handles any custom encoding conversions """
    def default(self, obj: Dict[str, Any]) -> Any:
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, datetime):
            return obj,strftime('%Y-%m-%d %H:%M:%S')
        return json.JSONEncoder.default(self, obj)
