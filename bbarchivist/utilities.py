#!/usr/bin/env python3
"""This module is used for miscellaneous utilities."""

import os  # path work
import argparse  # argument parser for filters
import platform  # platform info
import glob  # cap grabbing
import configparser  # config parsing, duh
import threading  # get thread for spinner
import time  # spinner delay, timer decorator
import sys  # streams, version info
import itertools  # spinners gonna spin
import subprocess  # loader verification
import math  # rounding
from bbarchivist import bbconstants  # cap location, version, filename bits

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def enum_cpus():
    """
    Backwards compatibility wrapper for CPU count.
    """
    try:
        from os import cpu_count
    except ImportError:
        from multiprocessing import cpu_count
    finally:
        cpus = cpu_count()
    return cpus


def where_which(path):
    """
    Backwards compatibility wrapper for approximating which/where.
    """
    try:
        from shutil import which
    except ImportError:
        from shutilwhich import which
    finally:
        thepath = which(path)
    return thepath


def grab_cap():
    """
    Figure out where cap is, local, specified or system-supplied.
    """
    try:
        capfile = glob.glob(os.path.join(os.getcwd(), bbconstants.CAP.filename))[0]
    except IndexError:
        try:
            cappath = cappath_config_loader()
            capfile = glob.glob(cappath)[0]
        except IndexError:
            cappath_config_writer(bbconstants.CAP.location)
            return bbconstants.CAP.location  # no ini cap
        else:
            cappath_config_writer(os.path.abspath(capfile))
            return os.path.abspath(capfile)  # ini cap
    else:
        return os.path.abspath(capfile)  # local cap


def grab_cfp():
    """
    Figure out where cfp is, local or system-supplied.
    """
    try:
        cfpfile = glob.glob(os.path.join(os.getcwd(), bbconstants.CFP.filename))[0]
    except IndexError:
        cfpfile = bbconstants.CFP.location  # system cfp
    return os.path.abspath(cfpfile)  # local cfp


def fsizer(file_size):
    """
    Raw byte file size to human-readable string.

    :param file_size: Number to parse.
    :type file_size: float
    """
    if file_size is None:
        file_size = 0
    fsize = float(file_size)
    for sfix in ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
        if fsize < 1024.0:
            size = "{0:3.2f}{1}".format(fsize, sfix)
            break
        else:
            fsize /= 1024.0
    else:
        size = "{0:3.2f}{1}".format(fsize, 'YB')
    return size


def signed_file_args(files):
    """
    Check if there are between 1 and 6 files supplied to argparse.

    :param files: List of signed files, between 1 and 6 strings.
    :type files: list(str)
    """
    filelist = [file for file in files if file]
    if not 1 <= len(filelist) <= 6:
        raise argparse.ArgumentError(argument=None, message="Requires 1-6 signed files")
    return files


def file_exists(file):
    """
    Check if file exists, raise argparse error if it doesn't.

    :param file: Path to a file, including extension.
    :type file: str
    """
    if not os.path.exists(file):
        raise argparse.ArgumentError(argument=None, message="{0} not found.".format(file))
    return file


def positive_integer(input_int):
    """
    Check if number > 0, raise argparse error if it isn't.

    :param input_int: Integer to check.
    :type input_int: str
    """
    if int(input_int) <= 0:
        info = "{0} is not >=0.".format(str(input_int))
        raise argparse.ArgumentError(argument=None, message=info)
    return int(input_int)


def valid_method(method):
    """
    Check if compression method is valid, raise argparse error if it isn't.

    :param method: Compression method to check.
    :type method: str
    """
    methodlist = bbconstants.METHODS
    if sys.version_info[1] <= 2:
        methodlist = [x for x in bbconstants.METHODS if x != "txz"]
    if method not in methodlist:
        info = "Invalid method {0}.".format(method)
        raise argparse.ArgumentError(argument=None, message=info)
    return method


def valid_carrier(mcc_mnc):
    """
    Check if MCC/MNC is valid (1-3 chars), raise argparse error if it isn't.

    :param mcc_mnc: MCC/MNC to check.
    :type mcc_mnc: str
    """
    if not str(mcc_mnc).isdecimal():
        infod = "Non-integer {0}.".format(str(mcc_mnc))
        raise argparse.ArgumentError(argument=None, message=infod)
    if len(str(mcc_mnc)) > 3 or len(str(mcc_mnc)) == 0:
        infol = "{0} is invalid.".format(str(mcc_mnc))
        raise argparse.ArgumentError(argument=None, message=infol)
    else:
        return mcc_mnc


def escreens_pin(pin):
    """
    Check if given PIN is valid, raise argparse error if it isn't.

    :param pin: PIN to check.
    :type pin: str
    """
    if len(pin) == 8:
        try:
            int(pin, 16)  # hexadecimal-ness
        except ValueError:
            raise argparse.ArgumentError(argument=None, message="Invalid PIN.")
        else:
            return pin.lower()
    else:
        raise argparse.ArgumentError(argument=None, message="Invalid PIN.")


def escreens_duration(duration):
    """
    Check if Engineering Screens duration is valid.

    :param duration: Duration to check.
    :type duration: int
    """
    if int(duration) in (1, 3, 6, 15, 30):
        return int(duration)
    else:
        raise argparse.ArgumentError(argument=None, message="Invalid duration.")


def s2b(input_check):
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
    if talkative:
        print("CHECKING INSTALLED FILES...")
    try:
        import winreg  # windows registry
        hk7z = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\7-Zip")
        path = winreg.QueryValueEx(hk7z, "Path")
    except OSError as exc:
        if talkative:
            print("SOMETHING WENT WRONG")
            print(str(exc))
            print("TRYING LOCAL FILES...")
        return win_seven_zip_local(talkative)
    else:
        if talkative:
            print("7ZIP USING INSTALLED FILES")
        return '"{0}"'.format(os.path.join(path[0], "7z.exe"))


def win_seven_zip_local(talkative=False):
    """
    If 7-Zip isn't in the registry, fall back onto supplied executables.
    If *those* aren't there, return "error".

    :param talkative: Whether to output to screen. False by default.
    :type talkative: bool
    """
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


def get_core_count():
    """
    Find out how many CPU cores this system has.
    """
    try:
        cores = str(enum_cpus())  # 3.4 and up
    except NotImplementedError:
        cores = "1"  # 3.2-3.3
    else:
        if enum_cpus() is None:
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
        except ImportError:
            if talkative:
                print("PLEASE INSTALL SHUTILWHICH WITH PIP")
            return False
        else:
            if path is None:
                if talkative:
                    print("NO 7ZIP")
                    print("PLEASE INSTALL p7zip")
                return False
            else:
                if talkative:
                    print("7ZIP FOUND AT", path)
                return True


def increment(version, inc=3):
    """
    Increment version by given number. For repeated lookups.

    :param version: w.x.y.ZZZZ, becomes w.x.y.(ZZZZ + increment).
    :type version: str

    :param inc: What to increment by. Default is 3.
    :type inc: str
    """
    splitos = version.split(".")
    splitos[3] = int(splitos[3])
    if splitos[3] > 9996:  # prevent overflow
        splitos[3] = 0
    splitos[3] += int(inc)
    splitos[3] = str(splitos[3])
    return ".".join(splitos)


def stripper(name):
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
    suffix = "nto+armle-v7+signed.bar"
    osurls = [
        "{0}/winchester.factory_sfi.desktop-{1}-{2}".format(baseurl, osversion, suffix),
        "{0}/qc8960.factory_sfi.desktop-{1}-{2}".format(baseurl, osversion, suffix),
        "{0}/qc8960.factory_sfi.desktop-{1}-{2}".format(baseurl, osversion, suffix),
        "{0}/qc8974.factory_sfi.desktop-{1}-{2}".format(baseurl, osversion, suffix)
    ]
    radiourls = [
        "{0}/m5730-{1}-{2}".format(baseurl, radioversion, suffix),
        "{0}/qc8960-{1}-{2}".format(baseurl, radioversion, suffix),
        "{0}/qc8960.omadm-{1}-{2}".format(baseurl, radioversion, suffix),
        "{0}/qc8960.wtr-{1}-{2}".format(baseurl, radioversion, suffix),
        "{0}/qc8960.wtr5-{1}-{2}".format(baseurl, radioversion, suffix),
        "{0}/qc8930.wtr5-{1}-{2}".format(baseurl, radioversion, suffix),
        "{0}/qc8974.wtr2-{1}-{2}".format(baseurl, radioversion, suffix)
    ]
    coreurls = []
    splitos = osversion.split(".")
    splitos = [int(i) for i in splitos]
    if splitos[1] >= 4 or (splitos[1] == 3 and splitos[2] >= 1):  # 10.3.1+
        osurls[2] = osurls[2].replace("qc8960.factory_sfi", "qc8960.factory_sfi_hybrid_qc8x30")
        osurls[3] = osurls[3].replace("qc8974.factory_sfi", "qc8960.factory_sfi_hybrid_qc8974")
    if core:
        for url in osurls:
            coreurls.append(url.replace(".desktop", ""))
    return osurls, radiourls, coreurls


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
    suffix = "nto+armle-v7+signed.bar"
    splitos = [int(i) for i in osversion.split(".")]
    if device == 0:
        osurl = "{0}/winchester.factory_sfi.desktop-{1}-{2}".format(baseurl, osversion, suffix)
        radiourl = "{0}/m5730-{1}-{2}".format(baseurl, radioversion, suffix)
    elif device == 1:
        osurl = "{0}/qc8960.factory_sfi.desktop-{1}-{2}".format(baseurl, osversion, suffix)
        radiourl = "{0}/qc8960-{1}-{2}".format(baseurl, radioversion, suffix)
    elif device == 2:
        osurl = "{0}/qc8960.verizon_sfi.desktop-{1}-{2}".format(baseurl, osversion, suffix)
        radiourl = "{0}/qc8960.omadm-{1}-{2}".format(baseurl, radioversion, suffix)
    elif device == 3:
        osurl = "{0}/qc8960.factory_sfi.desktop-{1}-{2}".format(baseurl, osversion, suffix)
        radiourl = "{0}/qc8960.wtr-{1}-{2}".format(baseurl, radioversion, suffix)
    elif device == 4:
        osurl = "{0}/qc8960.factory_sfi.desktop-{1}-{2}".format(baseurl, osversion, suffix)
        radiourl = "{0}/qc8960.wtr5-{1}-{2}".format(baseurl, radioversion, suffix)
    elif device == 5:
        osurl = "{0}/qc8960.factory_sfi.desktop-{1}-{2}".format(baseurl, osversion, suffix)
        radiourl = "{0}/qc8930.wtr5-{1}-{2}".format(baseurl, radioversion, suffix)
        if (splitos[1] >= 4) or (splitos[1] == 3 and splitos[2] >= 1):
            osurl = osurl.replace("qc8960.factory_sfi", "qc8960.factory_sfi_hybrid_qc8x30")
    elif device == 6:
        osurl = "{0}/qc8974.factory_sfi.desktop-{1}-{2}".format(baseurl, osversion, suffix)
        radiourl = "{0}/qc8974.wtr2-{1}-{2}".format(baseurl, radioversion, suffix)
        if (splitos[1] >= 4) or (splitos[1] == 3 and splitos[2] >= 1):
            osurl = osurl.replace("qc8974.factory_sfi", "qc8960.factory_sfi_hybrid_qc8974")
    return osurl, radiourl


def bulk_urls(baseurl, osversion, radioversion, core=False, alturl=None):
    """
    Generate all URLs, plus extra Verizon URLs.

    :param baseurl: The URL, from http to the hashed software release.
    :type baseurl: str

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version.
    :type radioversion: str

    :param device: Device to use.
    :type device: int

    :param core: Whether or not to return core URLs as well.
    :type core: bool

    :param alturl: The base URL for any alternate radios.
    :type alturl: str
    """
    osurls, radurls, coreurls = generate_urls(baseurl, osversion, radioversion, core)
    vzwos, vzwrad = generate_lazy_urls(baseurl, osversion, radioversion, 2)
    osurls.append(vzwos)
    radurls.append(vzwrad)
    vzwcore = vzwos.replace("sfi.desktop", "sfi")
    if core:
        coreurls.append(vzwcore)
    osurls = list(set(osurls))  # pop duplicates
    radurls = list(set(radurls))
    if core:
        coreurls = list(set(coreurls))
    if alturl is not None:
        radiourls2 = []
        for rad in radurls:
            radiourls2.append(rad.replace(baseurl, alturl))
        radurls = radiourls2
        del radiourls2
    return osurls, coreurls, radurls


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

    def after(self):
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
                self.spinner.after()
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
        if not is_windows():  # pragma: no cover
            print("\n")


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
        return True


class DummyException(Exception):
    """
    Exception that is not raised at all.
    """
    pass


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


def verify_loader_integrity(loaderfile):
    """
    Test for created loader integrity. Windows-only.

    :param loaderfile: Path to loader.
    :type loaderfile: str
    """
    if not is_windows():
        pass
    else:
        excode = None
        try:
            with open(os.devnull, 'rb') as dnull:
                cmd = "{0} fileinfo".format(loaderfile)
                excode = subprocess.call(cmd, stdout=dnull, stderr=subprocess.STDOUT)
        except OSError:
            excode = -1
        return excode == 0  # 0 if OK, non-zero if something broke


def verify_bulk_loaders(a_dir):
    """
    Run :func:`verify_loader_integrity` for all files in a dir.

    :param a_dir: Directory to use.
    :type a_dir: str
    """
    if not is_windows():
        pass
    else:
        files = [file for file in os.listdir(a_dir) if not os.path.isdir(file)]
        brokens = []
        for file in files:
            if file.endswith(".exe") and file.startswith(bbconstants.PREFIXES):
                print("TESTING: {0}".format((file)))
                if not verify_loader_integrity(file):
                    brokens.append(file)
        return brokens


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


def workers(input_data):
    """
    Count number of CPU workers, smaller of number of threads and length of data.

    :param input_data: Input data, some iterable.
    :type input_data: list
    """
    runners = len(input_data) if len(input_data) < enum_cpus() else enum_cpus()
    return runners


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
            pass
    return wrapper


def prep_logfile():
    """
    Prepare log file, labeling it with current date. Select folder based on frozen status.
    """
    logfile = "{0}.txt".format(time.strftime("%Y_%m_%d_%H%M%S"))
    root = os.getcwd() if getattr(sys, 'frozen', False) else os.path.expanduser("~")
    basefolder = os.path.join(root, "lookuplogs")
    os.makedirs(basefolder, exist_ok=True)
    record = os.path.join(basefolder, logfile)
    open(record, "w").close()
    return record


def cappath_config_loader(homepath=None):
    """
    Read a ConfigParser file to get cap preferences.

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    config = configparser.ConfigParser()
    homepath = os.path.expanduser("~") if homepath is None else homepath
    conffile = os.path.join(homepath, "bbarchivist.ini")
    if not os.path.exists(conffile):
        open(conffile, 'w').close()
    config.read(conffile)
    if not config.has_section('cap'):
        config['cap'] = {}
    capini = config['cap']
    cappath = capini.get('path', fallback=bbconstants.CAP.location)
    return cappath


def cappath_config_writer(cappath=None, homepath=None):
    """
    Write a ConfigParser file to store cap preferences.

    :param cappath: Method to use.
    :type cappath: str

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    if cappath is None:
        cappath = grab_cap()
    config = configparser.ConfigParser()
    if homepath is None:
        homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    if not os.path.exists(conffile):
        open(conffile, 'w').close()
    config.read(conffile)
    if not config.has_section('cap'):
        config['cap'] = {}
    config['cap']['path'] = cappath
    with open(conffile, "w") as configfile:
        config.write(configfile)
