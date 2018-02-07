#!/usr/bin/env python3
"""Compress all files in a directory."""

import os  # path operations
import sys  # load arguments

from bbarchivist import argutils  # arguments
from bbarchivist import archiveutils  # main program
from bbarchivist import scriptutils  # default parser
from bbarchivist import utilities  # bool parsing

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


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
        type=argutils.valid_method)
    parser.add_argument(
        "-nv",
        "--no-verify",
        help="Don't verify archives",
        action="store_false",
        default=True,
        dest="verify")
    parser.add_argument(
        "folder",
        help="Working directory, default is local",
        nargs="?",
        default=None)
    parser.set_defaults()
    args = parser.parse_args(sys.argv[1:])
    args.folder = utilities.dirhandler(args.folder, os.getcwd())
    if args.method is None:
        method = archiveutils.compress_config_loader()
        if method == "7z" and not utilities.prep_seven_zip(False):
            method = "zip"
    else:
        method = args.method
    psz = utilities.prep_seven_zip(False)
    szexe = utilities.get_seven_zip(False) if (method == "7z" and psz) else None
    workfolder = args.folder
    archiveutils.compress_config_writer()
    print(" ")
    archiveutils.compress(workfolder, method, szexe, None)
    if args.verify:
        archiveutils.verify(workfolder, method, szexe, "arcsonly")


if __name__ == "__main__":
    kompressor_main()
