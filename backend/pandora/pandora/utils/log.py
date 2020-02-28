#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import os
import pandora.utils.constants as cst

__all__ = ["setup_logging"]


def _init_log_to_file(log_file, level, _format):
    # file_handler = logging.handlers.TimedRotatingFileHandler(log_file,  when="M", interval=1, backupCount=10)
    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=cst.LOG_MAX_SIZE,
                                                        backupCount=cst.LOG_BACKEUP_COUNT)
    file_handler.setLevel(level)
    # file_handler.suffix = "%Y-%m-%d"
    file_handler.setFormatter(logging.Formatter(_format, datefmt='%Y-%m-%d %H:%M:%S'))
    return file_handler


def _init_log_to_console(level, _format):
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(logging.Formatter(_format))
    return console


def _init_log(log_file, level=cst.FILE_LOG_LEVEL, clevel=cst.CONSOLE_LOG_LEVEL):
    # _format = '%(asctime)s <%(levelname)s> [%(funcName)s.%(lineno)d]: %(message)s'
    # _format = '%(asctime)s [%(levelname)s] %(message)s'
    # _verbose = '[%(filename)s:%(lineno)d] %(levelname)s %(asctime)s %(funcName)s ### %(message)s'
    _verbose = '[%(levelname)s] %(asctime)s.%(msecs)d %(filename)s(%(lineno)s)/%(funcName)s : %(message)s'
    # _simple = '[%(filename)s:%(lineno)d] <%(levelname)s> ### %(message)s'
    _null = '%(message)s'
    file_handler = _init_log_to_file(log_file, level, _verbose)
    console = _init_log_to_console(clevel, _null)
    return file_handler, console


def setup_logging(log_file=cst.LOG_FILE, level=cst.FILE_LOG_LEVEL, clevel=cst.CONSOLE_LOG_LEVEL):
    if not os.path.isdir(cst.LOG_DIR):
        os.makedirs(cst.LOG_DIR)
    log_file = os.path.join(cst.LOG_DIR, log_file)
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    file_handler, console = _init_log(log_file, level, clevel)
    log.addHandler(file_handler)
    log.addHandler(console)
