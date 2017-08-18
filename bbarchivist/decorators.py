#!/usr/bin/env python3
"""This module is used for decorators."""

import time  # spinner delay, timer decorator
import math  # rounding
import os  # path check
import sys  # frozen
import sqlite3  # the sql library
from bbarchivist import dummy  # useless stdout
from bbarchivist import exceptions  # exceptions

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


def wrap_keyboard_except(method):
    """
    Decorator to absorb KeyboardInterrupt.

    :param method: Method to use.
    :type method: function
    """
    def wrapper(*args, **kwargs):
        """
        Try function, absorb KeyboardInterrupt and leave gracefully.
        """
        try:
            method(*args, **kwargs)
        except KeyboardInterrupt:
            dummy.UselessStdout.write("ASDASDASD")
    return wrapper


def timer(method):
    """
    Decorator to time a function.

    :param method: Method to time.
    :type method: function
    """
    def wrapper(*args, **kwargs):
        """
        Start clock, do function with args, print rounded elapsed time.
        """
        starttime = time.clock()
        method(*args, **kwargs)
        endtime = time.clock() - starttime
        endtime_proper = math.ceil(endtime * 100) / 100  # rounding
        mins, secs = divmod(endtime_proper, 60)
        hrs, mins = divmod(mins, 60)
        print("COMPLETED IN {0:02d}:{1:02d}:{2:02d}".format(int(hrs), int(mins), int(secs)))
    return wrapper


def sql_excepthandler(integrity):
    """
    Decorator to handle sqlite3.Error.

    :param integrity: Whether to allow sqlite3.IntegrityError.
    :type integrity: bool
    """
    def exceptdecorator(method):
        """
        Call function in sqlite3.Error try/except block.

        :param method: Method to use.
        :type method: function
        """
        def wrapper(*args, **kwargs):
            """
            Try function, handle sqlite3.Error, optionally pass sqlite3.IntegrityError.
            """
            return sql_exceptwrapper(method, integrity, *args, **kwargs)
        return wrapper
    return exceptdecorator


def sql_exceptwrapper(method, integrity, *args, **kwargs):
    """
    Try function, handle sqlite3.Error, optionally pass sqlite3.IntegrityError.

    :param method: Method to use.
    :type method: function

    :param integrity: Whether to allow sqlite3.IntegrityError.
    :type integrity: bool
    """
    try:
        result = method(*args, **kwargs)
        return result
    except sqlite3.IntegrityError if bool(integrity) else exceptions.DummyException:
        dummy.UselessStdout.write("ASDASDASD")  # DummyException never going to happen
    except sqlite3.Error as sqerror:
        print(sqerror)


def sql_existhandler(sqlpath):
    """
    Decorator to check if SQL database exists.

    :param sqlpath: Path to SQL database.
    :type sqlpath: str
    """
    def existdecorator(method):
        """
        Call function if SQL database exists.

        :param method: Method to use.
        :type method: function
        """
        def wrapper(*args, **kwargs):
            """
            Check existence of database, leave if it doesn't.
            """
            if os.path.exists(sqlpath):
                result = method(*args, **kwargs)
                return result
            else:
                print("NO SQL DATABASE FOUND!")
                raise SystemExit
        return wrapper
    return existdecorator


def enter_to_exit(checkfreeze=True):
    """
    Press enter to exit a script.

    :param checkfreeze: If this triggers only in frozen executables. Default is true.
    :type checkfreeze: bool
    """
    greenlight = bool(getattr(sys, 'frozen', False)) if checkfreeze else True
    if greenlight:
        smeg = input("Press Enter to exit")
        if smeg or not smeg:
            raise SystemExit
