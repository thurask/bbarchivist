#!/usr/bin/env python3
#pylint: disable = I0011, R0201, W0613, C0301, R0913, R0912, R0914, R0915, E0611, W0150
"""This module is used for miscellaneous utilities."""

__author__ = "Thurask"
__license__ = "Do whatever"
__copyright__ = "2015 Thurask"

import os  # path work
import argparse  # argument parser for filters
import platform  # platform info
import glob  # cap grabbing
import configparser  # config parsing, duh
import threading  # get thread for spinner
import time  # spinner delay
import sys  # streams, version info
import itertools  # spinners gonna spin
from bbarchivist import bbconstants  # cap location, version


def enum_cpus():
    """
    Backwards compatibility wrapper for CPU count.
    """
    try:
        from os import cpu_count  #@Unused Import
    except ImportError:  # pragma: no cover
        from multiprocessing import cpu_count #@UnusedImport
    finally:
        cpus = cpu_count()
    return cpus


def where_which(path):
    """
    Backwards compatibility wrapper for approximating which/where.
    """
    try:  # pragma: no cover
        from shutil import which  #@UnusedImport
    except ImportError:  # pragma: no cover
        try:
            from shutilwhich import which  #@UnusedImport
        except ImportError:
            raise SystemExit
    finally:  # pragma: no cover
        thepath = which(path)
    return thepath  # pragma: no cover


def grab_cap():
    """
    Figure out where cap is, local, specified or system-supplied.
    """
    try:
        caplo = bbconstants.CAPLOCATION
        here = os.getcwd()
        capfile = glob.glob(os.path.join(here, os.path.basename(caplo)))[0]
    except IndexError:  # pragma: no cover
        try:
            cappath = cappath_config_loader()
            capfile = glob.glob(cappath)[0]
        except IndexError:
            cappath_config_writer(bbconstants.CAPLOCATION)
            return bbconstants.CAPLOCATION  # no ini cap
        else:
            cappath_config_writer(os.path.abspath(capfile))
            return os.path.abspath(capfile)  # ini cap
    else:
        return os.path.abspath(capfile)  # local cap


def grab_json():
    """
    Figure out where JSON is, local or system-supplied.
    """
    try:
        jfile = file_exists(bbconstants.JSONFILE)  # system JSON
    except argparse.ArgumentError:  # pragma: no cover
        jfile = glob.glob(os.path.join(os.getcwd(), "bbconstants.json"))[0]  # local JSON
    finally:
        return os.path.abspath(jfile)


def filesize_parser(file_size):
    """
    Raw byte file size to human-readable string.

    :param file_size: Number to parse.
    :type file_size: float
    """
    if file_size is None:
        file_size = 0
    file_size = float(file_size)
    for sfix in ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
        if file_size < 1024.0:
            return "{:3.2f}{}".format(file_size, sfix)
        file_size /= 1024.0
    return "{:3.2f}{}".format(file_size, 'YB')


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
                                     message="{0} is not >=0.".format(str(input_int)))
    return int(input_int)


def valid_method(method):
    """
    Check if compression method is valid, raise argparse error if it isn't.

    :param method: Compression method to check.
    :type method: str
    """
    methodlist = bbconstants.METHODS
    if sys.version_info[1] <= 2:  # pragma: no cover
        methodlist = methodlist[:-1]  # strip last
    if method not in methodlist:
        raise argparse.ArgumentError(argument=None, message="Invalid method {0}.".format(method))
    return method


def valid_carrier(mcc_mnc):
    """
    Check if MCC/MNC is valid (1-3 chars), raise argparse error if it isn't.

    :param mcc_mnc: MCC/MNC to check.
    :type mcc_mnc: str
    """
    if not str(mcc_mnc).isdecimal():
        raise argparse.ArgumentError(argument=None, message="Non-integer {0}.".format(str(mcc_mnc)))
    if len(str(mcc_mnc)) > 3 or len(str(mcc_mnc)) == 0:
        raise argparse.ArgumentError(argument=None, message="{0} is invalid.".format(str(mcc_mnc)))
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

    :param talkative: Whether to output to screen. False by default.
    :type talkative: bool
    """
    if talkative:  # pragma: no cover
        print("CHECKING INSTALLED FILES...")
    try:
        import winreg  # windows registry
        hk7z = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\7-Zip")
        path = winreg.QueryValueEx(hk7z, "Path")
    except OSError as exc:  # pragma: no cover
        if talkative:  # pragma: no cover
            print("SOMETHING WENT WRONG")
            print(str(exc))
            print("TRYING LOCAL FILES...")
        return win_seven_zip_local(talkative)  # pragma: no cover
    else:
        if talkative:  # pragma: no cover
            print("7ZIP USING INSTALLED FILES")
        return '"' + os.path.join(path[0], "7z.exe") + '"'


def win_seven_zip_local(talkative=False):
    """
    If 7-Zip isn't in the registry, fall back onto supplied executables.
    If *those* aren't there, return "error".

    :param talkative: Whether to output to screen. False by default.
    :type talkative: bool
    """
    listdir = os.listdir(os.getcwd())  # pragma: no cover
    filecount = 0  # pragma: no cover
    for i in listdir:  # pragma: no cover
        if i in ["7za.exe", "7za64.exe"]:
            filecount += 1
    if filecount == 2:  # pragma: no cover
        if talkative:  # pragma: no cover
            print("7ZIP USING LOCAL FILES")
        if is_amd64():
            return "7za64.exe"
        else:
            return "7za.exe"
    else:  # pragma: no cover
        if talkative:  # pragma: no cover
            print("NO LOCAL FILES")
        return "error"


def get_core_count():
    """
    Find out how many CPU cores this system has.
    """
    try:
        cores = str(enum_cpus())  # 3.4 and up
    except NotImplementedError:  # pragma: no cover
        cores = "1"  # 3.2-3.3
    else:
        if enum_cpus() is None:  # pragma: no cover
            cores = "1"
    return cores


def prep_seven_zip(talkative=False):
    """
    Check for presence of 7-Zip.
    On POSIX, check for p7zip.
    On Windows, check for 7-Zip.

    :param talkative: Whether to output to screen. False by default.
    :type talkative: bool
    """
    if is_windows():
        return get_seven_zip(talkative) != "error"
    else:
        try:
            path = where_which("7za")
        except ImportError:  # pragma: no cover
            if talkative:
                print("PLEASE INSTALL SHUTILWHICH WITH PIP")
            return False
        else:
            if path is None:
                if talkative:  # pragma: no cover
                    print("NO 7ZIP")
                    print("PLEASE INSTALL p7zip")
                return False
            else:
                if talkative:  # pragma: no cover
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


def generate_urls(baseurl, osversion, radioversion, core=False):
    """
    Generate a list of OS URLs and a list of radio URLs based on input.

    :param baseurl: The URL, from http to the hashed software release.
    :type baseurl: str

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version.
    :type radioversion: str

    :param core: Whether or not to return core URLs as well.
    :type core: bool
    """
    osurls = [baseurl + "/winchester.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              baseurl + "/qc8960.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              baseurl + "/qc8960.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              baseurl + "/qc8974.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar"]
    radiourls = [baseurl + "/m5730-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8960-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8960.omadm-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8960.wtr-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8960.wtr5-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8930.wtr5-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8974.wtr2-" + radioversion +
                 "-nto+armle-v7+signed.bar"]
    coreurls = []
    splitos = osversion.split(".")
    splitos = [int(i) for i in splitos]
    if (splitos[1] >= 4) or (splitos[1] == 3 and splitos[2] >= 1):  # 10.3.1+
        osurls[2] = osurls[2].replace("qc8960.factory_sfi",
                                      "qc8960.factory_sfi_hybrid_qc8x30")  # pragma: no cover
        osurls[3] = osurls[3].replace("qc8974.factory_sfi",
                                      "qc8960.factory_sfi_hybrid_qc8974")  # pragma: no cover
    for url in osurls:
        coreurls.append(url.replace(".desktop", ""))
    if core:
        target = osurls, radiourls, coreurls
    else:
        target = osurls, radiourls, []  # pragma: no cover
    return target


def generate_lazy_urls(baseurl, osversion, radioversion, device):
    """
    Generate a pair of OS/radio URLs based on input.

    :param baseurl: The URL, from http to the hashed software release.
    :type baseurl: str

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version.
    :type radioversion: str

    :param device: Device to use.
    :type device: int
    """
    splitos = osversion.split(".")
    splitos = [int(i) for i in splitos]
    if device == 0:
        osurl = baseurl + "/winchester.factory_sfi.desktop-"
        osurl += osversion + "-nto+armle-v7+signed.bar"
        radiourl = baseurl + "/m5730-"
        radiourl += radioversion + "-nto+armle-v7+signed.bar"
    elif device == 1:
        osurl = baseurl + "/qc8960.factory_sfi.desktop-"
        osurl += osversion + "-nto+armle-v7+signed.bar"
        radiourl = baseurl + "/qc8960-"
        radiourl += radioversion + "-nto+armle-v7+signed.bar"
    elif device == 2:
        osurl = baseurl + "/qc8960.verizon_sfi.desktop-"
        osurl += osversion + "-nto+armle-v7+signed.bar"
        radiourl = baseurl + "/qc8960.omadm-"
        radiourl += radioversion + "-nto+armle-v7+signed.bar"
    elif device == 3:
        osurl = baseurl + "/qc8960.factory_sfi.desktop-"
        osurl += osversion + "-nto+armle-v7+signed.bar"
        radiourl = baseurl + "/qc8960.wtr-"
        radiourl += radioversion + "-nto+armle-v7+signed.bar"
    elif device == 4:
        osurl = baseurl + "/qc8960.factory_sfi.desktop-"
        osurl += osversion + "-nto+armle-v7+signed.bar"
        radiourl = baseurl + "/qc8960.wtr5-"
        radiourl += radioversion + "-nto+armle-v7+signed.bar"
    elif device == 5:
        osurl = baseurl + "/qc8960.factory_sfi.desktop-"
        osurl += osversion + "-nto+armle-v7+signed.bar"
        radiourl = baseurl + "/qc8930.wtr5-"
        radiourl += radioversion + "-nto+armle-v7+signed.bar"
        if (splitos[1] >= 4) or (splitos[1] == 3 and splitos[2] >= 1):
            osurl = osurl.replace("qc8960.factory_sfi", "qc8960.factory_sfi_hybrid_qc8x30")
    elif device == 6:
        osurl = baseurl + "/qc8974.factory_sfi.desktop-"
        osurl += osversion + "-nto+armle-v7+signed.bar"
        radiourl = baseurl + "/qc8974.wtr2-"
        radiourl += radioversion + "-nto+armle-v7+signed.bar"
        if (splitos[1] >= 4) or (splitos[1] == 3 and splitos[2] >= 1):
            osurl = osurl.replace("qc8974.factory_sfi", "qc8960.factory_sfi_hybrid_qc8974")
    return osurl, radiourl


def line_begin():
    """
    Go to beginning of line, to overwrite whatever's there.
    """
    sys.stdout.write("\r")
    sys.stdout.flush()


def spinner_clear():
    """
    Get rid of any spinner residue left in stdout.
    """
    sys.stdout.write("\b \b")
    sys.stdout.flush()


class Spinner(object):
    """
    A basic spinner using itertools. No need for progress.
    """
    def __init__(self):
        self.wheel = itertools.cycle(['-', '/', '|', '\\'])
        self.file = UselessStdout()

    def next(self):
        """
        Iterate over itertools.cycle, write to file.
        """
        try:
            self.file.write(next(self.wheel))
            self.file.flush()
            self.file.write("\b\r")
            self.file.flush()
        except (KeyboardInterrupt, SystemExit):  # pragma: no cover
            self.stop()

    def stop(self):
        """
        Kill output.
        """
        self.file = UselessStdout()


class SpinManager(object):
    """
    Wraps around the itertools spinner, runs it in another thread.
    """
    def __init__(self):
        spinner = Spinner()
        self.spinner = spinner
        self.thread = threading.Thread(target=self.loop, args=())
        self.thread.daemon = True
        self.scanning = False
        self.spinner.file = UselessStdout()

    def start(self):
        """
        Begin the spinner.
        """
        self.spinner.file = sys.stderr
        self.scanning = True
        self.thread.start()

    def loop(self):
        """
        Spin if scanning, clean up if not.
        """
        while self.scanning:
            time.sleep(0.5)
            try:
                line_begin()
                self.spinner.next()
            except (KeyboardInterrupt, SystemExit):  # pragma: no cover
                self.scanning = False
                self.stop()

    def stop(self):
        """
        Stop the spinner.
        """
        self.spinner.stop()
        self.scanning = False
        spinner_clear()
        line_begin()
        if not is_windows():
            print("\n")  # pragma: no cover


class UselessStdout(object):
    """
    A dummy IO stream. Does nothing, by design.
    """
    @staticmethod
    def write(inp):
        """
        Do nothing.
        """
        pass

    @staticmethod
    def flush():
        """
        Do nothing.
        """
        pass

    @staticmethod
    def isatty():
        """
        Convince module we're in a terminal.
        """
        return True  # pragma: no cover


def return_and_delete(target):
    """
    Read text file, then delete it. Return contents.

    :param target: Text file to read.
    :type target: str
    """
    with open(target, "r") as thefile:
        content = thefile.read()
    os.remove(target)
    return content


def cappath_config_loader():
    """
    Read a ConfigParser file to get cap preferences.
    """
    config = configparser.ConfigParser()
    homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    config.read(conffile)
    if not config.has_section('cap'):
        config['cap'] = {}
        with open(conffile, "w") as configfile:
            config.write(configfile)
    capini = config['cap']
    cappath = capini.get('path', fallback=bbconstants.CAPLOCATION)
    return cappath


def cappath_config_writer(cappath=None):
    """
    Write a ConfigParser file to store cap preferences.

    :param cappath: Method to use.
    :type cappath: str
    """
    if cappath is None:
        cappath = grab_cap()
    config = configparser.ConfigParser()
    homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    config.read(conffile)
    config['cap']['path'] = cappath
    with open(conffile, "w") as configfile:
        config.write(configfile)
