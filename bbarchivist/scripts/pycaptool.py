#!/usr/bin/env python3
"""cap.exe, implemented in Python."""

import sys  # load arguments
import os  # local dir
from bbarchivist import utilities  # path checking
from bbarchivist import pseudocap  # actually making the loader
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2017 Thurask"


def pycaptool_main():
    """
    Parse arguments from argparse.

    Invoke :func:`bbarchivist.pseudocap.make_autoloader` with arguments.
    """
    parser = scriptutils.default_parser("bb-pseudocap", "BlackBerry CAP, in Python.", ("folder"))
    parser.add_argument("filename", help="Filename")
    parser.add_argument("files", help="1-6 signed files, space separated", nargs="+")
    parser.set_defaults()
    args = parser.parse_args(sys.argv[1:])
    args.folder = utilities.dirhandler(args.folder, os.getcwd())
    if not args.filename.endswith(".exe"):
        args.filename += ".exe"
    args.files = utilities.signed_file_args(args.files)
    pseudocap.make_autoloader(args.filename, args.files, args.folder)


if __name__ == "__main__":
    pycaptool_main()
