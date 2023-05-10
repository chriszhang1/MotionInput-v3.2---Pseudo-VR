import os
import struct
import time
from concurrent.futures import ThreadPoolExecutor
from subprocess import Popen

from communicator import Communicator
from motioninput_api import MotionInputAPI
from scripts.tools.json_editors.config_editor import ConfigEditor

PIPE_PATH = r'\\.\pipe\NPtest'  # ! hardcoded named pipe: NPtest


config_editor = ConfigEditor()
communicator = Communicator()


"""Constantly reads the named pipe connected with the GUI exe.
To be passed to concurrent.futures' ThreadPoolExecutor so that
it can run on background thread.
Message format: <4bytes int: str msg length> <actual str msg>
E.g. 5 hello
"""


def read_pipe():
    global pipe_active
    pipe_active = True
    # HACKY: waits for GUI exe to fully start the ServerPipe which python connects to
    time.sleep(4)

    # open named pipe for IPC with GUI
    with open(PIPE_PATH, 'r+b', 0) as pipe:
        print("opened pipe")
        while pipe_active:
            # reads 4 bytes i.e. int representing msg length
            msg_length = struct.unpack('I', pipe.read(4))[0]
            msg = pipe.read(msg_length).decode(
                'ascii')  # reads actual msg string

            # msg = input()  # Manual input for testing
            print(f"Frontend says: {msg}")
            out = communicator.process_command(msg)
            print(f"Backend says: {out}")
            if not out:
                print("Closing communication")
                msg_to_send = "Communication Closed".encode('ascii')
                pipe_active = False
                pipe.close()
                break
            msg_to_send = out.encode('ascii')
            pipe.write(struct.pack('I', len(msg_to_send)) + msg_to_send)
            pipe.seek(0)
            # TODO handle case where GUI windows is closed


if __name__ == "__main__":
    gui_process = Popen(os.path.join(os.path.dirname(os.path.realpath(__file__)), "netcoreapp3.1", "WpfParent.exe"))
    # gui_process = Popen(os.path.join(os.path.dirname( os.path.realpath(__file__)), "MI_WpfGUI.exe"))

    executor = ThreadPoolExecutor(1)
    # places read_pipe() into a background thread
    future_pipe = executor.submit(read_pipe)

    while pipe_active:
        MotionInputAPI.run()


# Start the Communicator thread.
# Start a while active to run the api.
