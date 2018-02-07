#!/usr/bin/env python3
"""This module is used for argument utilities."""

import argparse  # argument parser for filters
import os  # path work

from bbarchivist import bbconstants  # filename bits
from bbarchivist import utilities  # version checking

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2018 Thurask"


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
    devices = ("Priv", "DTEK50", "DTEK60", "KEYone", "Aurora", "Motion")
    if device is None:
        return None
    else:
        for dev in devices:
            if dev.lower() == device.lower():
                return dev
        raise argparse.ArgumentError(argument=None, message="Invalid device.")
