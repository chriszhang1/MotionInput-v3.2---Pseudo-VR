import subprocess
import os

from scripts.tools.json_editors.mode_editor import ModeEditor
from scripts.tools.json_editors.config_editor import ConfigEditor

mode_editor = ModeEditor()
config_editor = ConfigEditor()


"""
Launch settings MFC without opening a shell window.
"""
def launch_settings():

    mode = mode_editor.get_data("current_mode")
    version = config_editor.get_data("general/version")

    base_path = "MI3-%s-" + version + "-MFC.exe"
    target_path = ""
    if "hand" in mode:
        target_path = base_path % "Multitouch"
    elif "eye" in mode or "nose" in mode:
        target_path = base_path % "Facial-Navigation"
    elif "pseudovr" in mode:
        target_path = base_path % "PseudoVR"

    if target_path != "":
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.Popen(target_path, startupinfo=startupinfo)

def launch_help():

    mode = mode_editor.get_data("current_mode")
        
    base_path = os.path.abspath(os.path.join(os.getcwd(), "data", "help"))
    target_path = os.path.join(base_path, "general", "help.txt")
    
    if "hand" in mode:
        target_path = os.path.join(base_path, "hand", "help.txt")
    elif "eye" in mode or "nose" in mode:
        target_path = os.path.join(base_path, "head", "help.txt")
    elif "pseudovr" in mode:
        target_path = os.path.join(base_path, "pseudovr", "help.txt")

    os.startfile(target_path)

