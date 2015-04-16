#!/usr/bin/env python3
"""
@author: Thurask
"""

import os
import argparse
import platform
import shutil


def file_exists(file):
    """
    Check if file exists. Used for parsing file inputs from command line.
    :param file: \\path\\to\\file.ext
    :type file: str
    """
    if not os.path.exists(file):
        raise argparse.ArgumentError("{0} does not exist".format(file))
    return file


def str2bool(v):
    """Parse bool from string input.

    :param v: String to check if it means True or False.
    :type v: str
    """
    return str(v).lower() in ("yes", "true", "t", "1", "y")


def is_amd64():
    """
    Returns true if script is running on an AMD64 system
    :returns bool
    """
    amd64 = platform.machine().endswith("64")
    return amd64


def is_windows():
    """
    Returns true if script is running on Windows.
    """
    windows = platform.system() == "Windows"
    return windows


def is_mac():
    """
    Returns true if script is running on OSX.
    """
    mac = platform.system() == "Darwin"
    return mac


def is_linux():
    """
    Returns true if script is running on Linux.
    """
    linux = platform.system() == "Linux"
    return linux


def get_seven_zip(talkative=False):
    """
    Return name of 7-Zip executable.

    On POSIX, it MUST be 7za.
    On Windows, it can be installed or supplied with the script.
    ``win_seven_zip()`` is used to determine if it's installed.

    :param bool talkative: Whether to output to screen. False by default.
    """
    if is_windows():
        smeg = win_seven_zip(talkative)
        return smeg
    else:
        return "7za"


def win_seven_zip(talkative=False):
    """
    For Windows, checks where 7-Zip is.
    Consults registry first for any installed instances of 7-Zip.
    If it's not there, it falls back onto the supplied executables.
    :param talkative bool: Whether to output to screen. False by default.
    :type talkative: bool
    """
    if talkative:
        print("CHECKING INSTALLED FILES...")
    try:
        import winreg  # windows registry
        hk7z = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\7-Zip")
        path = winreg.QueryValueEx(hk7z, "Path")
    except Exception as e:
        if talkative:
            print("SOMETHING WENT WRONG")
            print(str(e))
            print("TRYING LOCAL FILES...")
        listdir = os.listdir(os.getcwd())
        filecount = 0
        for i in listdir:
            if i == "7za.exe" or i == "7za64.exe":
                filecount += 1
        if filecount == 2:
            if talkative:
                print("7ZIP USING LOCAL FILES")
            if is_amd64():
                return "7za64.exe"
            else:
                return "7za.exe"
        else:
            if talkative:
                print("NO LOCAL FILES")
            return "error"
    else:
        if talkative:
            print("7ZIP USING INSTALLED FILES")
        return '"' + os.path.join(path[0], "7z.exe") + '"'


def get_core_count():
    """
    Find out how many CPU cores this system has.
    Good for multicore compression.
    """
    cores = str(os.cpu_count())  # thank you Python 3.4
    if os.cpu_count() is None:
        cores = str(1)
    return cores


def prep_seven_zip():
    """
    Check for presence of 7-Zip.
    On POSIX, checks for p7zip.
    On Windows, checks for 7-Zip.
    False if not found, True if found.
    """
    if is_mac():
        path = shutil.which("7za")
        if path is None:
            print("NO 7ZIP")
            print("PLEASE INSTALL p7zip FROM SOURCE/HOMEBREW/MACPORTS")
            return False
        else:
            print("7ZIP FOUND AT", path)
            return True
    elif is_linux():
        path = shutil.which("7za")
        if path is None:
            print("NO 7ZIP")
            print("PLEASE INSTALL p7zip AND ANY RELATED PACKAGES")
            print("CONSULT YOUR PACKAGE MANAGER, OR GOOGLE IT")
            return False
        else:
            print("7ZIP FOUND AT", path)
            return True
    elif is_windows():
        smeg = get_seven_zip(True)
        if smeg == "error":
            return False
        else:
            return True
