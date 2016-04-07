#!/usr/bin/env python3
"""Compress all files in a directory."""

import sys  # load arguments
import os  # path operations
from bbarchivist import barutils  # main program
from bbarchivist import utilities  # bool parsing
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def kompressor_main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.barutils.compress` with those arguments.
    """
    parser = scriptutils.default_parser("bb-kompressor", "Compress files")
    parser.add_argument(
        "-m",
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
    szexe = utilities.get_seven_zip(False) if (method == "7z" and utilities.prep_seven_zip(False)) else None
    workfolder = args.folder
    barutils.compress_config_writer()
    print(" ")
    barutils.compress_suite(workfolder, method, szexe, False)


if __name__ == "__main__":
    kompressor_main()
