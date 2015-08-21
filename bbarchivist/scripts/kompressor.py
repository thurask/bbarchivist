#!/usr/bin/env python3

import argparse  # parse arguments
import sys  # load arguments
import os  # path operations
from bbarchivist import barutils  # main program
from bbarchivist import bbconstants  # constants/versions
from bbarchivist import utilities  # bool parsing


def kompressor_main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.barutils.compress` with those arguments.
    """
    parser = argparse.ArgumentParser(
        prog="bb-kompressor",
        description="Compress all files in a directory.",
        epilog="http://github.com/thurask/bbarchivist")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " +
        bbconstants.VERSION)
    parser.add_argument(
        "-m"
        "--method",
        help="Compression method",
        nargs="?",
        default=None,
        dest="method",
        type=utilities.valid_method)
    parser.add_argument(
        "folder",
        help="Working directory, default is local",
        nargs="?",
        default=None)
    parser.set_defaults()
    args = parser.parse_args(sys.argv[1:])
    if args.folder is None:
        args.folder = os.getcwd()
    if args.method is None:
        method = barutils.compress_config_loader()
        if method == "7z" and not utilities.prep_seven_zip(False):
            method = "zip"
    else:
        method = args.method
    if method == "7z" and utilities.prep_seven_zip(False):
        szexe = utilities.get_seven_zip(False)
    else:
        szexe = None
    workfolder = args.folder
    print(" ")
    barutils.compress_suite(workfolder,
                            method,
                            szexe,
                            False)
if __name__ == "__main__":
    kompressor_main()
