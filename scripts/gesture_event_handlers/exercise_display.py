'''
Author: Jason Ho
'''
from typing import List, Optional

from scripts.tools import View


class ExerciseDisplay:
    """Displays the name of the used exercises and the number of times they have been triggered in the view."""
    def __init__(self, view: View) -> None:
        self._view = view
        self._exercises = None
        self._exercise_repeats_dict = {}

    def set_exercise_display(self, exercises: Optional[List[str]] = None) -> None:
        """Sets the dictionary containing the names of the exercises and starting with 0 repeats each, passing it to the DisplayElement to be displayed
        in the view.
        
        :param exercises: List of exercises to be displayed
        :type exercises: Optional[List[str]]
        """
        if exercises is not None:
            self._exercises = exercises
        self._exercise_repeats_dict = {exercise: 0 for exercise in self._exercises}
        self._view.update_display_element("exercise_display_element", {"exericses_repeats_dict": self._exercise_repeats_dict})
        
    def update_exercise_repeats(self, exercise: str, repeats: int) -> None:
        """Updates the dictionary with the new number of repeats for a particular exercises, passing it to the DisplayElement to be displayed in the view.
        
        :param exercise: The exercise to be updated
        :type exercise: str
        :param repeats: Then number of times the exercise has been repeated
        :type repeats: int
        """
        if exercise is not None and repeats is not None:
            self._exercise_repeats_dict[exercise] = repeats
            self._view.update_display_element("exercise_display_element", {"exericses_repeats_dict": self._exercise_repeats_dict})

    def clear_exericse_display(self) -> None:
        """Clears the displaying of the exercise text in the view by passing an empty dictionary to the DisplayElement."""
        self._view.update_display_element("exercise_display_element", {"exericses_repeats_dict": {}})

