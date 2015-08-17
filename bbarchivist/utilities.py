﻿#!/usr/bin/env python3

"""This module is used for miscellaneous utilities."""

__author__ = "Thurask"
__license__ = "Do whatever"
__copyright__ = "2015 Thurask"

import os  # path work
import argparse  # argument parser for filters
import platform  # platform info
import shutil  # "which" command
import glob  # cap grabbing
from bbarchivist import bbconstants  # cap location, version
try:
    from shutil import which  # @UnusedImport
except ImportError:
    import shutilwhich  # @UnusedImport


def grab_cap():
    """
    Figure out where cap is, local or system-supplied.
    """
    try:
        capfile = glob.glob(
                    os.path.join(
                        os.getcwd(),
                        os.path.basename(bbconstants.CAPLOCATION)))[0]
    except IndexError:
        return bbconstants.CAPLOCATION  # no local cacerts
    else:
        return os.path.abspath(capfile)  # local cacerts


def filesize_parser(file_size):
    """
    Raw byte file size to human-readable string.

    :param file_size: Number to parse.
    :type file_size: float
    """
    if file_size is None:
        return "N/A"
    else:
        file_size = float(file_size)
        for x in ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
            if file_size < 1024.0:
                return "{:3.1f}{}".format(file_size, x)
            file_size /= 1024.0
        return "{:3.1f}{}".format(file_size, 'YB')


def file_exists(file):
    """
    Check if file exists, raise argparse error if it doesn't.

    :param file: Path to a file, including extension.
    :type file: str
    """
    if not os.path.exists(file):
        raise argparse.ArgumentError(argument=None,
                                     message="{0} not found.".format(file))
    return file


def positive_integer(input_int):
    """
    Check if number > 0, raise argparse error if it isn't.

    :param input_int: Integer to check.
    :type input_int: str
    """
    if int(input_int) <= 0:
        raise argparse.ArgumentError(argument=None,
                                     message="{0} is not >=0.".format(str(input_int))) #@IgnorePep8
    return int(input_int)


def valid_carrier(mcc_mnc):
    """
    Check if MCC/MNC is valid (1-3 chars), raise argparse error if it isn't.

    :param mcc_mnc: MCC/MNC to check.
    :type mcc_mnc: str
    """
    if not str(mcc_mnc).isdecimal():
        raise argparse.ArgumentError(argument=None,
                                         message="{0} is not an integer.".format(str(mcc_mnc))) #@IgnorePep8
    else:
        if len(str(mcc_mnc)) > 3 or len(str(mcc_mnc)) == 0:
            raise argparse.ArgumentError(argument=None,
                                             message="{0} is an invalid code.".format(str(mcc_mnc))) #@IgnorePep8
        else:
            return mcc_mnc


def escreens_pin(pin):
    """
    Check if given PIN is valid (8 character hexadecimal, raise argparse error if it isn't.

    :param pin: PIN to check.
    :type pin: str
    """
    if len(pin) == 8:
        try:
            int(pin, 16)  # hexadecimal-ness
        except ValueError:
            raise argparse.ArgumentError(argument=None,
                                         message="Invalid PIN.")
        else:
            return pin.lower()
    else:
        raise argparse.ArgumentError(argument=None,
                                     message="Invalid PIN.")


def escreens_duration(duration):
    """
    Check if Engineering Screens duration is valid.

    :param duration: Duration to check.
    :type duration: int
    """
    if int(duration) in (1, 3, 6, 15, 30):
        return int(duration)
    else:
        raise argparse.ArgumentError(argument=None,
                                     message="Invalid duration.")


def str2bool(input_check):
    """
    Return Boolean interpretation of string input.

    :param input_check: String to check if it means True or False.
    :type input_check: str
    """
    return str(input_check).lower() in ("yes", "true", "t", "1", "y")


def is_amd64():
    """
    Check if script is running on an AMD64 system.
    """
    return platform.machine().endswith("64")


def is_windows():
    """
    Check if script is running on Windows.
    """
    return platform.system() == "Windows"


def get_seven_zip(talkative=False):
    """
    Return name of 7-Zip executable.
    On POSIX, it MUST be 7za.
    On Windows, it can be installed or supplied with the script.
    :func:`win_seven_zip` is used to determine if it's installed.

    :param talkative: Whether to output to screen. False by default.
    :type talkative: bool
    """
    if is_windows():
        return win_seven_zip(talkative)
    else:
        return "7za"


def win_seven_zip(talkative=False):
    """
    For Windows, check where 7-Zip is ("where", pretty much).
    Consult registry first for any installed instances of 7-Zip.
    If it's not there, fall back onto the supplied executables.
    If *those* aren't there, return "error".

    :param talkative: Whether to output to screen. False by default.
    :type talkative: bool
    """
    if talkative:
        print("CHECKING INSTALLED FILES...")
    try:
        import winreg  # windows registry
        hk7z = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\7-Zip")
        path = winreg.QueryValueEx(hk7z, "Path")
    except Exception as exc:
        if talkative:
            print("SOMETHING WENT WRONG")
            print(str(exc))
            print("TRYING LOCAL FILES...")
        listdir = os.listdir(os.getcwd())
        filecount = 0
        for i in listdir:
            if i in ["7za.exe", "7za64.exe"]:
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
    """
    try:
        cores = str(os.cpu_count())  # thank you Python 3.4
    except AttributeError:  # less than 3.4
        import multiprocessing
        try:
            cores = str(multiprocessing.cpu_count())  # @UndefinedVariable
        except Exception:
            cores = "1"
    else:
        if os.cpu_count() is None:
            cores = "1"
    return cores


def prep_seven_zip():
    """
    Check for presence of 7-Zip.
    On POSIX, check for p7zip.
    On Windows, check for 7-Zip.
    """
    if is_windows():
        return get_seven_zip(True) != "error"
    else:
        try:
            path = shutil.which("7za")
        except ImportError:  # less than 3.3
            try:
                import shutilwhich  # @UnusedImport
            except ImportError:
                print("PLEASE INSTALL SHUTILWHICH WITH PIP")
                return False
        else:
            if path is None:
                print("NO 7ZIP")
                print("PLEASE INSTALL p7zip")
                return False
            else:
                print("7ZIP FOUND AT", path)
                return True


def version_incrementer(version, increment=3):
    """
    Increment version by given number. For repeated lookups.

    :param version: w.x.y.ZZZZ, becomes w.x.y.(ZZZZ+increment).
    :type version: str

    :param increment: What to increment by. Default is 3.
    :type increment: str
    """
    splitos = version.split(".")
    splitos[3] = int(splitos[3])
    if splitos[3] > 9996:  # prevent overflow
        splitos[3] = 0
    splitos[3] += int(increment)
    splitos[3] = str(splitos[3])
    return ".".join(splitos)


def barname_stripper(name):
    """
    Strip fluff from bar filename.

    :param name: Bar filename, must contain '-nto+armle-v7+signed.bar'.
    :type name: str
    """
    return name.replace("-nto+armle-v7+signed.bar", "")
