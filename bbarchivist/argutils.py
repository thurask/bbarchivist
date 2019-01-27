#!/usr/bin/env python3
"""This module is used for argument utilities."""

import argparse  # argument parser for filters
import glob  # file lookup
import os  # path work
import subprocess  # running cfp/cap
import sys  # getattr

from bbarchivist import bbconstants  # constants
from bbarchivist import utilities  # version checking

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2018-2019 Thurask"


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


def valid_method_poptxz(methodlist):
    """
    Remove .tar.xz support if system is too old.

    :param methodlist: List of all methods.
    :type methodlist: tuple(str)
    """
    if not utilities.new_enough(3):
        methodlist = [x for x in bbconstants.METHODS if x != "txz"]
    return methodlist


def valid_method(method):
    """
    Check if compression method is valid, raise argparse error if it isn't.

    :param method: Compression method to check.
    :type method: str
    """
    methodlist = bbconstants.METHODS
    methodlist = valid_method_poptxz(methodlist)
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
    if len(str(mcc_mnc)) > 3 or not str(mcc_mnc):
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
    devices = ("Priv", "DTEK50", "DTEK60", "KEYone", "Aurora", "Motion", "KEY2", "KEY2LE")
    if device is None:
        return None
    else:
        for dev in devices:
            if dev.lower() == device.lower():
                return dev
        raise argparse.ArgumentError(argument=None, message="Invalid device.")


def shortversion():
    """
    Get short app version (Git tag).
    """
    if not getattr(sys, 'frozen', False):
        ver = bbconstants.VERSION
    else:
        verfile = glob.glob(os.path.join(os.getcwd(), "version.txt"))[0]
        with open(verfile) as afile:
            ver = afile.read()
    return ver


def longversion():
    """
    Get long app version (Git tag + commits + hash).
    """
    if not getattr(sys, 'frozen', False):
        ver = (bbconstants.LONGVERSION, bbconstants.COMMITDATE)
    else:
        verfile = glob.glob(os.path.join(os.getcwd(), "longversion.txt"))[0]
        with open(verfile) as afile:
            ver = afile.read().split("\n")
    return ver


def slim_preamble(appname):
    """
    Standard app name header.

    :param appname: Name of app.
    :type appname: str
    """
    print("~~~{0} VERSION {1}~~~".format(appname.upper(), shortversion()))


def standard_preamble(appname, osversion, softwareversion, radioversion, altsw=None):
    """
    Standard app name, OS, radio and software (plus optional radio software) print block.

    :param appname: Name of app.
    :type appname: str

    :param osversion: OS version, 10.x.y.zzzz. Required.
    :type osversion: str

    :param radioversion: Radio version, 10.x.y.zzzz. Can be guessed.
    :type radioversion: str

    :param softwareversion: Software release, 10.x.y.zzzz. Can be guessed.
    :type softwareversion: str

    :param altsw: Radio software release, if not the same as OS.
    :type altsw: str
    """
    slim_preamble(appname)
    print("OS VERSION: {0}".format(osversion))
    print("OS SOFTWARE VERSION: {0}".format(softwareversion))
    print("RADIO VERSION: {0}".format(radioversion))
    if altsw is not None:
        print("RADIO SOFTWARE VERSION: {0}".format(altsw))



def default_parser_vers(vers=None):
    """
    Prepare version for default parser.

    :param vers: Versions: [git commit hash, git commit date]
    :param vers: list(str)
    """
    if vers is None:
        vers = longversion()
    return vers


def default_parser_flags(parser, flags=None):
    """
    Handle flags for default parser.

    :param parser: Parser to modify.
    :type parser: argparse.ArgumentParser

    :param flags: Tuple of sections to add.
    :type flags: tuple(str)
    """
    if flags is not None:
        parser = dpf_flags_folder(parser, flags)
        parser = dpf_flags_osr(parser, flags)
    return parser


def dpf_flags_folder(parser, flags=None):
    """
    Add generic folder flag to parser.

    :param parser: Parser to modify.
    :type parser: argparse.ArgumentParser

    :param flags: Tuple of sections to add.
    :type flags: tuple(str)
    """
    if "folder" in flags:
        parser.add_argument("-f",
                            "--folder",
                            dest="folder",
                            help="Working folder",
                            default=None,
                            metavar="DIR",
                            type=file_exists)
    return parser


def dpf_flags_osr(parser, flags=None):
    """
    Add generic OS/radio/software flags to parser.

    :param parser: Parser to modify.
    :type parser: argparse.ArgumentParser

    :param flags: Tuple of sections to add.
    :type flags: tuple(str)
    """
    if "osr" in flags:
        parser.add_argument("os",
                            help="OS version")
        parser.add_argument("radio",
                            help="Radio version, 10.x.y.zzzz",
                            nargs="?",
                            default=None)
        parser.add_argument("swrelease",
                            help="Software version, 10.x.y.zzzz",
                            nargs="?",
                            default=None)
    return parser


def default_parser(name=None, desc=None, flags=None, vers=None):
    """
    A generic form of argparse's ArgumentParser.

    :param name: App name.
    :type name: str

    :param desc: App description.
    :type desc: str

    :param flags: Tuple of sections to add.
    :type flags: tuple(str)

    :param vers: Versions: [git commit hash, git commit date]
    :param vers: list(str)
    """
    vers = default_parser_vers(vers)
    homeurl = "https://github.com/thurask/bbarchivist"
    parser = argparse.ArgumentParser(prog=name, description=desc, epilog=homeurl)
    parser.add_argument("-v",
                        "--version",
                        action="version",
                        version="{0} {1} committed {2}".format(parser.prog, vers[0], vers[1]))
    parser = default_parser_flags(parser, flags)
    return parser


def generic_windows_shim(scriptname, scriptdesc, target, version):
    """
    Generic CFP/CAP runner; Windows only.

    :param scriptname: Script name, 'bb-something'.
    :type scriptname: str

    :param scriptdesc: Script description, i.e. scriptname -h.
    :type scriptdesc: str

    :param target: Path to file to execute.
    :type target: str

    :param version: Version of target.
    :type version: str
    """
    parser = default_parser(scriptname, scriptdesc)
    capver = "|{0}".format(version)
    parser = external_version(parser, capver)
    parser.parse_known_args(sys.argv[1:])
    if utilities.is_windows():
        subprocess.call([target] + sys.argv[1:])
    else:
        print("Sorry, Windows only.")


def arg_verify_none(argval, message):
    """
    Check if an argument is None, error out if it is.

    :param argval: Argument to check.
    :type argval: str

    :param message: Error message to print.
    :type message: str
    """
    if argval is None:
        raise argparse.ArgumentError(argument=None, message=message)


def external_version(parser, addition):
    """
    Modify the version string of argparse.ArgumentParser, adding something.

    :param parser: Parser to modify.
    :type parser: argparse.ArgumentParser

    :param addition: What to add.
    :type addition: str
    """
    verarg = [arg for arg in parser._actions if isinstance(arg, argparse._VersionAction)][0]
    verarg.version = "{1}{0}".format(addition, verarg.version)
    return parser
