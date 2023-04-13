import os
import datetime

import logging
from logging.handlers import TimedRotatingFileHandler
from colorlog import ColoredFormatter


def colorlogger(name: str = 'my-discord-bot') -> logging.Logger:
    # Initialize the logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Define the log file path
    log_dir = './logs'
    os.makedirs(log_dir, exist_ok=True)
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'{today}.log')

    # Add a console handler
    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter(
        "%(reset)s%(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Add a file handler
    file_handler = TimedRotatingFileHandler(log_file, when='midnight')
    file_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


log = colorlogger()
