#!/usr/bin/env python3
"""This module is used for miscellaneous utilities."""

import os  # path work
import argparse  # argument parser for filters
import platform  # platform info
import glob  # cap grabbing
import hashlib  # base url creation
import threading  # get thread for spinner
import time  # spinner delay
import sys  # streams, version info
import itertools  # spinners gonna spin
import subprocess  # loader verification
from bbarchivist import bbconstants  # cap location, version, filename bits
from bbarchivist import compat  # backwards compat
from bbarchivist import dummy  # useless stdout
from bbarchivist import exceptions  # exceptions
from bbarchivist import iniconfig  # config parsing

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


def grab_datafile(datafile):
    """
    Figure out where a datafile is.

    :param datafile: Datafile to check.
    :type datafile: bbconstants.Datafile
    """
    try:
        afile = glob.glob(os.path.join(os.getcwd(), datafile.filename))[0]
    except IndexError:
        afile = datafile.location if datafile.name == "cfp" else grab_capini(datafile)
    return os.path.abspath(afile)


def grab_capini(datafile):
    """
    Get cap location from .ini file, and write if it's new.

    :param datafile: Datafile to check.
    :type datafile: bbconstants.Datafile
    """
    try:
        apath = cappath_config_loader()
        afile = glob.glob(apath)[0]
    except IndexError:
        cappath_config_writer(datafile.location)
        return bbconstants.CAP.location  # no ini cap
    else:
        cappath_config_writer(os.path.abspath(afile))
        return os.path.abspath(afile)  # ini cap:


def grab_cap():
    """
    Figure out where cap is, local, specified or system-supplied.
    """
    return grab_datafile(bbconstants.CAP)


def grab_cfp():
    """
    Figure out where cfp is, local or system-supplied.
    """
    return grab_datafile(bbconstants.CFP)


def new_enough(minver):
    """
    Check if we're at or above a minimum Python version.

    :param minver: Minimum Python version (3.minver).
    :type minver: int
    """
    return False if minver > sys.version_info[1] else True


def dirhandler(directory, defaultdir):
    """
    If directory is None, turn it into defaultdir.

    :param directory: Target directory.
    :type directory: str

    :param defaultdir: Default directory.
    :type defaultdir: str
    """
    directory = defaultdir if directory is None else directory
    return directory


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
    if not new_enough(3):
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


def droidlookup_hashtype(method):
    """
    Check if Android autoloader lookup hash type is valid.

    :param method: None for regular OS links, "sha256/512" for SHA256 or 512 hash.
    :type method: str
    """
    if method.lower() in ("sha512", "sha256"):
        return method.lower()
    else:
        raise argparse.ArgumentError(argument=None, message="Invalid type.")


def droidlookup_devicetype(device):
    """
    Check if Android autoloader device type is valid.

    :param device: Android autoloader types to check.
    :type device: str
    """
    devices = ("Priv", "DTEK50", "DTEK60", "KEYone", "Aurora")
    if device is None:
        return None
    else:
        for dev in devices:
            if dev.lower() == device.lower():
                return dev
        raise argparse.ArgumentError(argument=None, message="Invalid device.")


def s2b(input_check):
    """
    Return Boolean interpretation of string input.

    :param input_check: String to check if it means True or False.
    :type input_check: str
    """
    return str(input_check).lower() in ("yes", "true", "t", "1", "y")


def is_amd64():
    """
    Check if script is running on an AMD64 system (Python can be 32/64, this is for subprocess)
    """
    return platform.machine().endswith("64")


def is_windows():
    """
    Check if script is running on Windows.
    """
    return platform.system() == "Windows"


def talkaprint(msg, talkative=False):
    """
    Print only if asked to.

    :param msg: Message to print.
    :type msg: str

    :param talkative: Whether to output to screen. False by default.
    :type talkative: bool
    """
    if talkative:
        print(msg)


def get_seven_zip(talkative=False):
    """
    Return name of 7-Zip executable.
    On POSIX, it MUST be 7za.
    On Windows, it can be installed or supplied with the script.
    :func:`win_seven_zip` is used to determine if it's installed.

    :param talkative: Whether to output to screen. False by default.
    :type talkative: bool
    """
    return win_seven_zip(talkative) if is_windows() else "7za"


def win_seven_zip(talkative=False):
    """
    For Windows, check where 7-Zip is ("where", pretty much).
    Consult registry first for any installed instances of 7-Zip.

    :param talkative: Whether to output to screen. False by default.
    :type talkative: bool
    """
    talkaprint("CHECKING INSTALLED FILES...", talkative)
    try:
        import winreg  # windows registry
        hk7z = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\7-Zip")
        path = winreg.QueryValueEx(hk7z, "Path")
    except OSError as exc:
        if talkative:
            exceptions.handle_exception(exc, xit=None)
        talkaprint("TRYING LOCAL FILES...", talkative)
        return win_seven_zip_local(talkative)
    else:
        talkaprint("7ZIP USING INSTALLED FILES", talkative)
        return '"{0}"'.format(os.path.join(path[0], "7z.exe"))


def win_seven_zip_local(talkative=False):
    """
    If 7-Zip isn't in the registry, fall back onto supplied executables.
    If *those* aren't there, return "error".

    :param talkative: Whether to output to screen. False by default.
    :type talkative: bool
    """
    filecount = len([x for x in os.listdir(os.getcwd()) if x in ["7za.exe", "7z.exe"]])
    if filecount == 2:
        talkaprint("7ZIP USING LOCAL FILES", talkative)
        szexe = "7za.64.exe" if is_amd64() else "7za.exe"
    else:
        talkaprint("NO LOCAL FILES", talkative)
        szexe = "error"
    return szexe


def get_core_count():
    """
    Find out how many CPU cores this system has.
    """
    try:
        cores = str(compat.enum_cpus())  # 3.4 and up
    except NotImplementedError:
        cores = "1"  # 3.2-3.3
    else:
        if compat.enum_cpus() is None:
            cores = "1"
    return cores


def prep_seven_zip_path(path, talkative=False):
    """
    Print p7zip path on POSIX, or notify if not there.

    :param path: Path to use.
    :type path: str

    :param talkative: Whether to output to screen. False by default.
    :type talkative: bool
    """
    if path is None:
        talkaprint("NO 7ZIP\nPLEASE INSTALL p7zip", talkative)
        return False
    else:
        talkaprint("7ZIP FOUND AT {0}".format(path), talkative)
        return True


def prep_seven_zip_posix(talkative=False):
    """
    Check for p7zip on POSIX.

    :param talkative: Whether to output to screen. False by default.
    :type talkative: bool
    """
    try:
        path = compat.where_which("7za")
    except ImportError:
        talkaprint("PLEASE INSTALL SHUTILWHICH WITH PIP", talkative)
        return False
    else:
        return prep_seven_zip_path(path, talkative)


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
        return prep_seven_zip_posix(talkative)


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


def create_base_url(softwareversion):
    """
    Make the root URL for production server files.

    :param softwareversion: Software version to hash.
    :type softwareversion: str
    """
    # Hash software version
    swhash = hashlib.sha1(softwareversion.encode('utf-8'))
    hashedsoftwareversion = swhash.hexdigest()
    # Root of all urls
    baseurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/{0}".format(hashedsoftwareversion)
    return baseurl


def format_app_name(appname):
    """
    Convert long reverse DNS name to short name.

    :param appname: Application name (ex. sys.pim.calendar -> "calendar")
    :type appname: str
    """
    final = appname.split(".")[-1]
    return final


def create_bar_url(softwareversion, appname, appversion, clean=False):
    """
    Make the URL for any production server file.

    :param softwareversion: Software version to hash.
    :type softwareversion: str

    :param appname: Application name, preferably like on server.
    :type appname: str

    :param appversion: Application version.
    :type appversion: str

    :param clean: Whether or not to clean up app name. Default is False.
    :type clean: bool
    """
    baseurl = create_base_url(softwareversion)
    if clean:
        appname = format_app_name(appname)
    return "{0}/{1}-{2}-nto+armle-v7+signed.bar".format(baseurl, appname, appversion)


def generate_urls(softwareversion, osversion, radioversion, core=False):
    """
    Generate a list of OS URLs and a list of radio URLs based on input.

    :param softwareversion: Software version to hash.
    :type softwareversion: str

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version.
    :type radioversion: str

    :param core: Whether or not to return core URLs as well.
    :type core: bool
    """
    osurls = [
        create_bar_url(softwareversion, "winchester.factory_sfi.desktop", osversion),
        create_bar_url(softwareversion, "qc8960.factory_sfi.desktop", osversion),
        create_bar_url(softwareversion, "qc8960.factory_sfi.desktop", osversion),
        create_bar_url(softwareversion, "qc8974.factory_sfi.desktop", osversion)
    ]
    radiourls = [
        create_bar_url(softwareversion, "m5730", radioversion),
        create_bar_url(softwareversion, "qc8960", radioversion),
        create_bar_url(softwareversion, "qc8960.omadm", radioversion),
        create_bar_url(softwareversion, "qc8960.wtr", radioversion),
        create_bar_url(softwareversion, "qc8960.wtr5", radioversion),
        create_bar_url(softwareversion, "qc8930.wtr5", radioversion),
        create_bar_url(softwareversion, "qc8974.wtr2", radioversion)
    ]
    coreurls = []
    osurls, radiourls = filter_urls(osurls, radiourls, osversion)
    if core:
        coreurls = [x.replace(".desktop", "") for x in osurls]
    return osurls, radiourls, coreurls


def newer_103(splitos, third):
    """
    Return True if given split OS version is 10.3.X or newer.

    :param splitos: OS version, split on the dots: [10, 3, 3, 2205]
    :type: list(int)

    :param third: The X in 10.3.X.
    :type third: int
    """
    newer = True if ((splitos[1] >= 4) or (splitos[1] == 3 and splitos[2] >= third)) else False
    return newer


def filter_urls(osurls, radiourls, osversion):
    """
    Filter lists of OS and radio URLs.

    :param osurls: List of OS URLs.
    :type osurls: list(str)

    :param radiourls: List of radio URLs.
    :type radiourls: list(str)

    :param osversion: OS version.
    :type osversion: str
    """
    splitos = [int(i) for i in osversion.split(".")]
    osurls[2] = filter_1031(osurls[2], splitos, 5)  # Z3 10.3.1+
    osurls[3] = filter_1031(osurls[3], splitos, 6)  # Passport 10.3.1+
    osurls[0], radiourls[0] = pop_stl1(osurls[0], radiourls[0], splitos)  # STL100-1 10.3.3+
    return osurls, radiourls


def filter_1031(osurl, splitos, device):
    """
    Modify URLs to reflect changes in 10.3.1.

    :param osurl: OS URL to modify.
    :type osurl: str

    :param splitos: OS version, split and cast to int: [10, 3, 2, 2876]
    :type splitos: list(int)

    :param device: Device to use.
    :type device: int
    """
    if newer_103(splitos, 1):
        filterdict = {5: ("qc8960.factory_sfi", "qc8960.factory_sfi_hybrid_qc8x30"), 6: ("qc8974.factory_sfi", "qc8960.factory_sfi_hybrid_qc8974")}
        osurl = filter_osversion(osurl, device, filterdict)
    return osurl


def pop_stl1(osurl, radiourl, splitos):
    """
    Replace STL100-1 links in 10.3.3+.

    :param osurl: OS URL to modify.
    :type osurl: str

    :param radiourl: Radio URL to modify.
    :type radiourl: str

    :param splitos: OS version, split and cast to int: [10, 3, 3, 2205]
    :type splitos: list(int)
    """
    if newer_103(splitos, 3):
        osurl = osurl.replace("winchester", "qc8960")  # duplicates get filtered out later
        radiourl = radiourl.replace("m5730", "qc8960")
    return osurl, radiourl


def filter_osversion(osurl, device, filterdict):
    """
    Modify URLs based on device index and dictionary of changes.

    :param osurl: OS URL to modify.
    :type osurl: str

    :param device: Device to use.
    :type device: int

    :param filterdict: Dictionary of changes: {device : (before, after)}
    :type filterdict: dict(int:(str, str))
    """
    if device in filterdict.keys():
        osurl = osurl.replace(filterdict[device][0], filterdict[device][1])
    return osurl


def generate_lazy_urls(softwareversion, osversion, radioversion, device):
    """
    Generate a pair of OS/radio URLs based on input.

    :param softwareversion: Software version to hash.
    :type softwareversion: str

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version.
    :type radioversion: str

    :param device: Device to use.
    :type device: int
    """
    splitos = [int(i) for i in osversion.split(".")]
    rads = ["m5730", "qc8960", "qc8960.omadm", "qc8960.wtr",
            "qc8960.wtr5", "qc8930.wtr4", "qc8974.wtr2"]
    oses = ["winchester.factory", "qc8960.factory", "qc8960.verizon",
            "qc8974.factory"]
    maps = {0:0, 1:1, 2:2, 3:1, 4:1, 5:1, 6:3}
    osurl = create_bar_url(softwareversion, "{0}_sfi.desktop".format(oses[maps[device]]), osversion)
    radiourl = create_bar_url(softwareversion, rads[device], radioversion)
    osurl = filter_1031(osurl, splitos, device)
    return osurl, radiourl


def bulk_urls(softwareversion, osversion, radioversion, core=False, altsw=None):
    """
    Generate all URLs, plus extra Verizon URLs.

    :param softwareversion: Software version to hash.
    :type softwareversion: str

    :param osversion: OS version.
    :type osversion: str

    :param radioversion: Radio version.
    :type radioversion: str

    :param device: Device to use.
    :type device: int

    :param core: Whether or not to return core URLs as well.
    :type core: bool

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str
    """
    baseurl = create_base_url(softwareversion)
    osurls, radurls, coreurls = generate_urls(softwareversion, osversion, radioversion, core)
    vzwos, vzwrad = generate_lazy_urls(softwareversion, osversion, radioversion, 2)
    osurls.append(vzwos)
    radurls.append(vzwrad)
    vzwcore = vzwos.replace("sfi.desktop", "sfi")
    if core:
        coreurls.append(vzwcore)
    osurls = list(set(osurls))  # pop duplicates
    radurls = list(set(radurls))
    if core:
        coreurls = list(set(coreurls))
    if altsw is not None:
        altbase = create_base_url(altsw)
        radiourls2 = []
        for rad in radurls:
            radiourls2.append(rad.replace(baseurl, altbase))
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
        self.file = dummy.UselessStdout()

    def after(self):
        """
        Iterate over itertools.cycle, write to file.
        """
        try:
            self.file.write(next(self.wheel))
            self.file.flush()
            self.file.write("\b\r")
            self.file.flush()
        except (KeyboardInterrupt, SystemExit):
            self.stop()

    def stop(self):
        """
        Kill output.
        """
        self.file = dummy.UselessStdout()


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
        self.spinner.file = dummy.UselessStdout()

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
            except (KeyboardInterrupt, SystemExit):
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
            print("\n")


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


def bulkfilter_printer(afile):
    """
    Print filename and verify a loader file.

    :param afile: Path to file.
    :type afile: str
    """
    print("TESTING: {0}".format(os.path.basename(afile)))
    if not verify_loader_integrity(afile):
        return os.path.basename(afile)


def bulkfilter(files):
    """
    Verify all loader files in a given list.

    :param files: List of files.
    :type files: list(str)
    """
    brokens = [bulkfilter_printer(file) for file in files if prepends(os.path.basename(file), bbconstants.PREFIXES, ".exe")]
    return brokens


def verify_bulk_loaders(ldir):
    """
    Run :func:`verify_loader_integrity` for all files in a dir.

    :param ldir: Directory to use.
    :type ldir: str
    """
    if not is_windows():
        pass
    else:
        files = [os.path.join(ldir, file) for file in os.listdir(ldir) if not os.path.isdir(file)]
        brokens = [file for file in bulkfilter(files) if file]
        return brokens


def list_workers(input_data, workerlimit):
    """
    Count number of threads, either length of iterable or provided limit.

    :param input_data: Input data, some iterable.
    :type input_data: list

    :param workerlimit: Maximum number of workers.
    :type workerlimit: int
    """
    runners = len(input_data) if len(input_data) < workerlimit else workerlimit
    return runners


def cpu_workers(input_data):
    """
    Count number of CPU workers, smaller of number of threads and length of data.

    :param input_data: Input data, some iterable.
    :type input_data: list
    """
    return list_workers(input_data, compat.enum_cpus())


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


def prepends(file, pre, suf):
    """
    Check if filename starts with/ends with stuff.

    :param file: File to check.
    :type file: str

    :param pre: Prefix(es) to check.
    :type pre: str or list or tuple

    :param suf: Suffix(es) to check.
    :type suf: str or list or tuple
    """
    return file.startswith(pre) and file.endswith(suf)


def lprint(iterable):
    """
    A oneliner for 'for item in x: print item'.

    :param iterable: Iterable to print.
    :type iterable: list/tuple
    """
    for item in iterable:
        print(item)


def cappath_config_loader(homepath=None):
    """
    Read a ConfigParser file to get cap preferences.

    :param homepath: Folder containing ini file. Default is user directory.
    :type homepath: str
    """
    capini = iniconfig.generic_loader('cappath', homepath)
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
    cappath = grab_cap() if cappath is None else cappath
    results = {"path": cappath}
    iniconfig.generic_writer("cappath", results, homepath)


def def_args(dirs):
    """
    Return prepared argument list for most instances of :func:`cond_check:.

    :param dirs: List of directories.
    :type dirs: list(str)
    """
    return [dirs[4], dirs[5], dirs[2], dirs[3]]


def cond_do(dofunc, goargs, restargs=None, condition=True):
    """
    Do a function, check a condition, then do same function but swap first argument.

    :param dofunc: Function to do.
    :type dofunc: function

    :param goargs: List of variable arguments.
    :type goargs: list(str)

    :param restargs: Rest of arguments, which are constant.
    :type restargs: list(str)

    :param condition: Condition to check in order to use secondarg.
    :type condition: bool
    """
    restargs = [] if restargs is None else restargs
    dofunc(goargs[0], *restargs)
    if condition:
        dofunc(goargs[1], *restargs)


def cond_check(dofunc, goargs, restargs=None, condition=True, checkif=True, checkifnot=True):
    """
    Do :func:`cond_do` based on a condition, then do it again based on a second condition.

    :param dofunc: Function to do.
    :type dofunc: function

    :param goargs: List of variable arguments.
    :type goargs: list(str)

    :param restargs: Rest of arguments, which are constant.
    :type restargs: list(str)

    :param condition: Condition to check in order to use secondarg.
    :type condition: bool

    :param checkif: Do :func:`cond_do` if this is True.
    :type checkif: bool

    :param checkifnot: Do :func:`cond_do` if this is False.
    :type checkifnot: bool
    """
    if checkif:
        cond_do(dofunc, goargs[0:2], restargs, condition)
    if not checkifnot:
        cond_do(dofunc, goargs[2:4], restargs, condition)
