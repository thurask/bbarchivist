#!/usr/bin/env python3

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
    Work with either local cap or system cap. Since cx_freeze is dumb.
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


def filesize_parser(num):
    """
    Raw byte filesize to human-readable string.

    :param num: Number to parse.
    :type num: float
    """
    if num is None:
        return "N/A"
    else:
        num = float(num)
        for x in ['b', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
            if num < 1024.0:
                return "{:3.1f}{}".format(num, x)
            num /= 1024.0
        return "{:3.1f}{}".format(num, 'YB')


def file_exists(file):
    """
    Check if file exists. Used for parsing file inputs from command line.

    :param file: Path to a file, including extension.
    :type file: str
    """
    if not os.path.exists(file):
        raise argparse.ArgumentError(argument=None,
                                     message="{0} not found.".format(file))
    return file


def positive_integer(inputint):
    """
    Check if number > 0. Used for parsing integer inputs from command line.

    :param inputint: Integer to check.
    :type inputint: int
    """
    if int(inputint) <= 0:
        raise argparse.ArgumentError(argument=None,
                                     message="{0} is not >0.".format(str(inputint))) #@IgnorePep8
    return int(inputint)


def escreens_pin(pin):
    """
    Check if given PIN is valid (8 character hexadecimal)

    :param pin: PIN to check.
    :type pin: str
    """
    if len(pin) == 8:
        try:
            int(pin, 16)  # hexadecimal-ness
        except ValueError:
            raise argparse.ArgumentError("Invalid PIN.")
        else:
            return pin.lower()
    else:
        raise argparse.ArgumentError("Invalid PIN.")


def escreens_duration(duration):
    """
    Check if escreens duration is valid.

    :param duration: Duration to check.
    :type duration: int
    """
    if int(duration) in (1, 3, 6, 15, 30):
        return int(duration)
    else:
        raise argparse.ArgumentError("Invalid duration.")


def str2bool(input_check):
    """
    Parse bool from string input.

    :param input_check: String to check if it means True or False.
    :type input_check: str
    """
    return str(input_check).lower() in ("yes", "true", "t", "1", "y")


def is_amd64():
    """
    Returns true if script is running on an AMD64 system.
    """
    return platform.machine().endswith("64")


def is_windows():
    """
    Returns true if script is running on Windows.
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
    For Windows, checks where 7-Zip is.
    Consults registry first for any installed instances of 7-Zip.
    If it's not there, it falls back onto the supplied executables.
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
    Good for multicore compression.
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
    On POSIX, checks for p7zip.
    On Windows, checks for 7-Zip.
    Returns False if not found, True if found.
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


def return_model(index):
    """
    Return device model from selected HWID/variant index.
    Lists found in bbconstants module.

    :param index: The index to look up.
    :type index: int
    """
    if 0 <= index <= 3:
        return 0  # Z10
    elif 4 <= index <= 5:
        return 1  # P9982
    elif 6 <= index <= 10:
        return 2  # Q10
    elif 11 <= index <= 13:
        return 3  # Q5
    elif 14 <= index <= 15:
        return 4  # P9983
    elif 16 <= index <= 21:
        return 5  # Z30
    elif 22 <= index <= 26:
        return 6  # Classic
    elif 27 <= index <= 28:
        return 7  # Leap
    elif 29 <= index <= 30:
        return 8  # Z3
    elif 31 <= index <= 34:
        return 9  # Passport


def return_family(index):
    """
    Return device family from selected HWID.
    Lists found in bbconstants module.

    :param index: The index to look up.
    :type index: int
    """
    if index == 0:  # STL100-1
        return 0
    elif 1 <= index <= 5:  # STL100-2/3/4, P9982
        return 1
    elif 6 <= index <= 15:  # Q10, Q5, P9983
        return 2
    elif 16 <= index <= 28:  # Z30, Classic, Leap
        return 3
    elif 29 <= index <= 30:  # Z3
        return 4
    elif 31 <= index <= 34:  # Passport
        return 5


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
