import os
import sys

from .body_module import *  # TODO: make sure this needs to be imported?
from .core import *
from .event_mapper import EventMapper
from .eye_module import *
from .gesture_event_handlers import *
from .gesture_events import *
from .gesture_loader import GestureLoader
from .hand_module import *
from .head_module import *
from .mode_controller import ModeController
from .speech_module import *
from .tools import *

# use: from scripts import DATA_PATH, to get absolute path of data folder.
# ALWAYS use DATA_PATH

DATA_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(
            os.path.realpath(__file__)
        ),
        "../data"
    )
) 
