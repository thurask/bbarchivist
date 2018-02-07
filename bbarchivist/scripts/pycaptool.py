#!/usr/bin/env python3
"""cap.exe, implemented in Python."""

import os  # local dir
import sys  # load arguments

from bbarchivist import argutils  # arguments
from bbarchivist import pseudocap  # actually making the loader
from bbarchivist import utilities  # path checking

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2018 Thurask"


def pycaptool_main():
    """
    Parse arguments from argparse.

    Invoke :func:`bbarchivist.pseudocap.make_autoloader` with arguments.
    """
    parser = argutils.default_parser("bb-pseudocap", "BlackBerry CAP, in Python.", ("folder"))
    parser.add_argument("filename", help="Filename")
    parser.add_argument("files", help="1-6 signed files, space separated", nargs="+")
    parser.set_defaults()
    args = parser.parse_args(sys.argv[1:])
    args.folder = utilities.dirhandler(args.folder, os.getcwd())
    if not args.filename.endswith(".exe"):
        args.filename += ".exe"
    args.files = argutils.signed_file_args(args.files)
    pseudocap.make_autoloader(args.filename, args.files, args.folder)


if __name__ == "__main__":
    pycaptool_main()
