'''
Authors: Carmen Meinson and Samuel Emilolorun
'''
from scripts.core import Position
from typing import Optional, Set


class SpeechPosition(Position):

    def __init__(self, raw_data, used_primitives: Set[str] = None) -> None:
        self._primitives_names = sorted(list(used_primitives), key=len, reverse=True)
        # used_primitives will contain all the phrases we are interested in
        # e.g. "a string of words", "a string", "detected words"

        self._primitives = {}
        # calculate primitives
        if raw_data is not None:
            # as we know that there should just always be one key that refelect the phrase with the value None (because phrase has no coordinates)
            self._current_phrase = list(raw_data.keys())[0]
            self._calculate_primitives()

    def get_primitive(self, name: str) -> Optional[bool]:
        """ 
         Returns the state of a primitive and none if name isn't a primitive
        :param name: name of the primitive (e.g. "click")
        :type name: str
        :return: state of primitive
        :rtype: Optional[bool]
        """

        if name not in self._primitives: return None

        return self._primitives[name]

    def _calculate_primitives(self) -> None:
        """ 
        Sets the states of the primitives based on the current phrase
        """
        # TODO: this is clearly no the way this should be done - just for testing
        for command in self._primitives_names:
            if command in self._current_phrase:
                self._primitives[command] = True
                return
        # here gotta do some braining and basically (efficently) figure out which of the "primitives" are contained in the current phrase
        # eg self._primitives_names = ["a string of words", "a string", "detected words"]
        # self._current_phrase = "a string of detected words"
        # set the self._primitives to {"a string of words":False, "a string":True, "detected words":True}

    def get_primitives_names(self) -> Set[str]:
        """
        :return: Names of all primitives that are calcualted by the speech position class
        :rtype: Set[str]
        """
        return set(self._primitives_names)
