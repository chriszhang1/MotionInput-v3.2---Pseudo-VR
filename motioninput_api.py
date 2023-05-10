'''
Author: Carmen Meinson
Contributors: Siam Islam, Anelia Gaydardzhieva, Chris Zhang
Comments: 
This is the starting point of MI
''' 
# Standard
import os
import time
from threading import Lock
from typing import Set

# Local
from scripts.tools.logger import logger_config, logger_stop
from scripts import *

# TODO: KeyboardListener currently not used 
#from scripts.tools.keyboard_listener import KeyboardListener

# TODO: Custom gestures currently not used 
from scripts.tools.customize_gesture_recorder import CustomizeGestureRecorder
# from scripts.tools.gesture_recorder import GestureRecorder
# from scripts.tools.heat_map import HeatMap

from scripts.tools.welcome_message import WelcomeMsg
# Logging Configuration
log = logger_config(file_name = 'data/logging/MI_logs.log', config = Config())

from scripts.tools.launch_utils import launch_settings, launch_help


class MotionInputAPI:
    _lock = Lock()
    _mode_editor = ModeEditor()
    _gestures_editor = GestureEditor(get_primitives=False)
    _events_editor = EventEditor()
    _config_editor = Config().get_editor()
    _customize_gesture_recorder = CustomizeGestureRecorder()
    # TODO: KeyboardListener
    #_keyboard_listener = KeyboardListener()
    #_keyboard_listener.start()
    _camera = None
    _view = None
    _view_hidden = False
    _model = None
    _mode_controller = None
    _change_camera = False
    _calibrating = None
    _calibrating_params = None
    _active = False
    _stop_next_iteration = False  # as the view needs to be closed by the main thread and not the communicator thread we use this little hack (:
    _modules = {
        "hand": HandModule,
        "speech": SpeechModule,
        "body": BodyModule,
        "head": HeadModule,
        "eye": EyeModule
    }
    _welcome_msg = WelcomeMsg()
    # TODO: Custom gestures - Heatmap
    # _heatmap = HeatMap()
    # _gesture_recorder = None

    @classmethod
    def init_modules(cls, names: Set[str]) -> None:
        """
        Calls the pre-initialization method on all given modules. 
        This performs all of the time consuming setup of the Module before initialization.
        If is not called, then all the setup is done when the Modules are first initialized. 
        :param names: set of module names ("hand"/"speech"/"body"/"head"/"eye")
        :type names: Set[str]
        """
        with cls._lock:
            if cls._active:
                raise RuntimeError("Cannot pre-initialize modules. MI is already running")
            for name in names:
                cls._modules[name].pre_initialize()

    @classmethod
    def start(cls) -> None:
        """
        ### START MI ###
        :raises RuntimeError: error raised if an instance of MI is already running
        """
        with cls._lock:
           
            if cls._active:
                raise RuntimeError("MI is already running")
            
            cls._camera = Camera()
            cls._model = Model()
            cls._view = View(hidden=cls._view_hidden)
            # cls._gesture_recorder = GestureRecorder()
            # to change the events that are used, change the mode_config dict in the mode_controller.py
            cls._mode_controller = ModeController(cls._model, cls._view)
            cls._active = True

        log.info("[[MI Started]]")


    @classmethod
    def run(cls) -> None:
        """
        Inside Main loop
        """
        with cls._lock:

            # Calibration
            if cls._calibrating is not None: # allows calibrating from main thread (for opencv to work)
                cls._modules[cls._calibrating].calibrate(cls._calibrating_params)
                cls._calibrating_params = None
                cls._calibrating = None

            # Modes Iteration
            if cls._stop_next_iteration:
                cls._stop()
                cls._stop_next_iteration = False

            # If MI running
            if cls._active:
                # Read Camera
                image, data = cls._camera.read()
                # Mode change if needed
                cls._mode_controller.change_mode_if_needed()
                # TODO: Hotkeys
                #cls._mode_controller.change_hotkeys_folder_if_needed()
                # TODO is frame_data used here?
                # FPS
                frame_data = cls._model.process_frame(image)
                # TODO: Custom gestures
                # cls._gesture_recorder.record_gesture(frame_data, cls._model)

                # Pressed Keys for Camera
                pressed_key = cls._view.update_display(image)
                if pressed_key == ord('.') and not cls._change_camera:
                    cls._change_camera = True
                    cls._view.update_change_camera(True, data["camera_nr"])
                    pressed_key = -1

                # Pressed ? for Help - Opens help.txt depending on current_mode (also triggered by saying 'help')
                elif pressed_key == ord('?'):
                    
                    launch_help()

                # Settings MFC GUIs
                elif pressed_key == ord(','):

                    launch_settings()

                # Camera setup 
                if not data["pass"] or cls._change_camera:
                    if cls._camera.change_camera(pressed_key):
                        cls._change_camera = False
                        cls._view.update_change_camera(False, data["camera_nr"])

                # Check if View closed => stop MI
                if cls._view.was_closed_by_user():  # if the user exited with the esc key or the [x] button
                    print("closing")
                    cls._stop()
                    log.info("View closed: _stop() triggered")



    @classmethod
    def is_active(cls) -> bool:
        """
        Returns if there is an instance of the MI model running
        """
        return cls._active


    @classmethod
    def _stop(cls) -> None:
        cls._active = False

        # cls._gesture_recorder.write_data_into_DB()
        if cls._view is not None:
            cls._view.close()
        if cls._mode_controller is not None:
            cls._mode_controller.close()
        if cls._camera is not None:
            cls._camera.close()

        cls._view = None
        cls._camera = None
        cls._model = None
        cls._mode_controller = None
        # cls._gesture_recorder = None


    @classmethod
    def stop(cls) -> None:
        """
        ### STOP MI ###
        :raises RuntimeError: error raised if MI is not running
        """
        if not cls._active:
            raise RuntimeError("MI is not running")
        cls._stop_next_iteration = True
        while cls._stop_next_iteration:
            """
            needs improvement 
            OpenCv does not like multithreading
            so had to make sure that all the method calls that interact with
            the OpenCV window are made from the main thread 
            """
            time.sleep(0.01)


    @classmethod
    def show_view(cls) -> None:
        """
        If the view is hidden, shows the view (the openCV window with the camera image)
        """
        cls._view_hidden = False
        if cls._view is not None:
            cls._view.show()


    @classmethod
    def hide_view(cls) -> None:
        """
        If the view is shown, hides the view (the openCV window with the camera image)
        """
        cls._view_hidden = True
        if cls._view is not None:
            cls._view.hide()


    @classmethod
    def change_mode(cls, mode: Optional[str] = None) -> None:
        """
        Set the interaction mode that the model will be set to from the next frame.
        If no mode is indicated the next mode is set according to the iteration_order, provided
        :param mode: name of the mode, defaults to None
        :type mode: Optional[str], optional
        """
        if not cls._active:
            raise RuntimeError("Cannot change mode. MI is not running")
        cls._mode_controller.set_next_mode(mode)

    @classmethod
    def calibrate_module(cls, name: str, params: Optional[Any] = None) -> None:
        """
        Calls the calibration method on the specified module
        :param name: name of the module ("hand"/"speech"/"body"/"head"/"eye")
        :type name: str
        """
        with cls._lock:
            if cls._active:
                raise RuntimeError("Cannot calibrate. MI is already running")
            cls._calibrating = name
            cls._calibrating_params = params

        """
        while cls._calibrating is not None:

            time.sleep(0.01)
        """

    @classmethod
    def get_config_editor(cls) -> ConfigEditor:
        return cls._config_editor


    @classmethod
    def get_mode_editor(cls) -> ModeEditor:
        return cls._mode_editor


    @classmethod
    def get_gestures_editor(cls) -> GestureEditor:
        return cls._gestures_editor


    @classmethod
    def get_events_editor(cls) -> EventEditor:
        return cls._events_editor


    @classmethod
    def record_gesture(cls, parameter_dict):
        try:
            file_path = parameter_dict['file_path']
            name = parameter_dict['name']
            phrase = parameter_dict['tag']
            hand = parameter_dict['hand']
            # TODO is event_type used here?
            event_type = parameter_dict['event_type']

            event = parameter_dict["event"]
            attention_point = parameter_dict["focus"]
            if parameter_dict["angle"] == "False":
                angle_change = False
            else:
                angle_change = True
            res = cls._customize_gesture_recorder.record_gesture_from_file(file_path, "hand", hand, name, angle_change,
                                                                        phrase, attention_point, event,
                                                                        cls._gestures_editor, cls._mode_editor, 
                                                                        cls._events_editor)
        except Exception as exc:
            log.critical(f"Record gesture failed: {exc}")
            raise
        return res


    # TODO: Heatmap code
    # @classmethod
    # def create_heatmap(cls, parameter_dict):
    #     name = parameter_dict['gesture_name']
    #     start = parameter_dict['start']
    #     end = parameter_dict['end']
    #     return cls._heatmap.generate_heatmap(name, start, end)





if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "exercise_calibration":
        from scripts.body_module.calibrate_exercises import RepetitiousExerciseCalibration
        exercise_calibration = RepetitiousExerciseCalibration(selected_exercises=sys.argv[2:])
        exercise_calibration.calibration()
    try:
        # Start MI
        MotionInputAPI.start()
        log.info("[MI Started]")
        print("[MI Started]")
        while MotionInputAPI.is_active():
                MotionInputAPI.run()
        # Stop MI
        log.info("[MI Stopped]")
        print("[MI Stopped]]]")
        logger_stop()
        print("[Logger Stopped]")
    # Exceptions 
    except Exception as e:
        try:
            MotionInputAPI._stop()
            print(f"[MI Stopped with _stop() because of Exception: {e}]")
        except Exception as ex:
            print(f"[MI failed to stop with _stop() because of Exception: {ex}]")
            raise
        raise
    # SystemExit
    except SystemExit as se:
        print(f"SystemExit: {se, se.code}")
        raise
