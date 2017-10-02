#!/usr/bin/env python3
"""Makes a nice info file for a folder of autoloaders."""

import sys  # load arguments
import os  # path operations
from bbarchivist import utilities  # input validation
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2016-2017 Thurask"


def grab_args():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.scriptutils.make_info` with those arguments.
    """
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-infogen", "Generate info files", flags=("folder", "osr"))
        parser.add_argument(
            "-d",
            "--device",
            help="Device (Android only)",
            nargs="?",
            default=None,
            type=utilities.droidlookup_devicetype)
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        execute_args(args)
    else:
        questionnaire()


def questionnaire():
    """
    Questions to ask if no arguments given.
    """
    folder = os.getcwd()
    osver = input("OS VERSION: ")
    android = utilities.s2b(input("ANDROID OS (Y/N)?: "))
    if android:
        device = input("DEVICE: ")
        radio = None
        software = None
    else:
        device = None
        radio = input("RADIO VERSION: ")
        software = input("SOFTWARE RELEASE: ")
    print(" ")
    infogenerator_main(folder, osver, radio, software, device)


def execute_args(args):
    """
    Get args and decide what to do with them.

    :param args: Arguments.
    :type args: argparse.Namespace
    """
    args.folder = utilities.dirhandler(args.folder, os.getcwd())
    infogenerator_main(args.folder, args.os, args.radio, args.swrelease, args.device)


def infogenerator_main(folder, osver, radio=None, swrelease=None, device=None):
    """
    Wrap around :mod:`bbarchivist.scriptutils` info generation.

    :param folder: Path to folder to analyze.
    :type folder: str

    :param osver: OS version, required for both types.
    :type osver: str

    :param radio: Radio version, required for QNX.
    :type radio: str

    :param swrelease: Software release, required for QNX.
    :type swrelease: str

    :param device: Device type, required for Android.
    :type device: str
    """
    scriptutils.make_info(folder, osver, radio, swrelease, device)


if __name__ == "__main__":
    grab_args()
