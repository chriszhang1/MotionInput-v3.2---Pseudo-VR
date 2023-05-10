'''
Author: Anelia Gaydardzhieva
Comments:
Our work on large applications such as MI can benefit from
having a method to provide information about app activities.
With multithreading in particular, print statements are not always reliable.
Therefore, other that Visual Studio debugging tools, 
logging provides an easy way of tracking actions throughout the application.
'''
import os
import logging
from logging.handlers import RotatingFileHandler

MI_LOGGER_NAME = "motioninput_api"

def logger_config(file_name : str = "", config = None) -> None: 
    """
    Logger Configuration in motioninput_api.py
    Code inspired from https://github.com/yashprakash13/data-another-day 
    """
    logger = logging.getLogger(MI_LOGGER_NAME)
    logger_enabled = False
    if config:
        logger_enabled = config.get_data("general/logging_enabled")
    if logger_enabled and os.path.exists(file_name):
        logger.setLevel(logging.DEBUG)
    else:
        logger.handlers.clear()
        return logger

    fmt = "%(asctime)s <%(levelname)s> ['%(message)s']  -  Path: <%(name)s>  -  Function Name: %(funcName)s - Line: %(lineno)s"

    # Human friendly format
    formatter = logging.Formatter(fmt)

    # Optional Detailed format
#    formatter = logging.Formatter(
#    fmt=f"%(levelname)s %(created)s (%(relativeCreated)d) \t %(pathname)s F%(funcName)s L%(lineno)s - %(message)s",
#    datefmt="%Y-%m-%d %H:%M:%S"
#)

    # Set Rotation handler
    # This is configuration for 3 additional files for backup and their rotation.
    # When MI_logs.log reaches 100KB, the file gets renamed to MI_logs.log.1
    # and a new MI_logs.log is created. 
    # This sets a max limit of 400KB information stored on any device 
    # and will allow thorough investigation of bugs and problems. 
    # Ask the user to copy and send the "logger" folder across to our team
    # to investigate any problems. 
    # To ensure useful information is stored in this folder, 
    # our team has to provide detailed logs which can help during an
    # investigation of potential bugs and issues.

    fileHandler = RotatingFileHandler(
    filename=file_name, 
    maxBytes=100_000, 
    backupCount=3
    )

    logger.addHandler(fileHandler)
    fh = logging.FileHandler(file_name)
    fh.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(fh)
    return logger


def get_logger(filename : str):
    """
    Import and Definition in a file:

    from scripts.tools.logger import get_logger
    log = get_logger(__name__)

    Use Options:

    log.info('Info message')
    log.debug('Debug message')
    log.warning('Warning message')
    log.error('Error message')
    log.critical('Critical message')
    """
    return logging.getLogger(MI_LOGGER_NAME).getChild(filename)


def logger_stop() -> None:
    """
    STOP
    Flush and close all handlers 
    """
    logging.shutdown()


