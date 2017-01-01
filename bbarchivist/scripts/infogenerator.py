#!/usr/bin/env python3
"""Makes a nice info file for a folder of autoloaders."""

import sys  # load arguments
import os  # path operations
from bbarchivist import utilities  # input validation
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2016-2017 Thurask"


def infogenerator_main():
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
        if args.folder is None:
            args.folder = os.getcwd()
        scriptutils.make_info(args.folder, args.os, args.radio, args.swrelease, args.device)
    else:
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
        scriptutils.make_info(folder, osver, radio, software, device)


if __name__ == "__main__":
    infogenerator_main()
