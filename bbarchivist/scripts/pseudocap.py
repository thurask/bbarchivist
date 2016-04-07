#!/usr/bin/env python3
"""cap.exe, implemented in Python."""

import sys  # load arguments
import os  # local dir
from bbarchivist import utilities  # path checking
from bbarchivist import pseudocap  # actually making the loader
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def pseudocap_main():
    """
    Parse arguments from argparse.

    Invoke :func:`bbarchivist.pseudocap.make_autoloader` with arguments.
    """
    parser = scriptutils.default_parser("bb-pseudocap", "BlackBerry CAP, in Python.",
                                        ("folder"))
    parser.add_argument("filename", help="Filename")
    files = parser.add_argument_group()
    files.add_argument(
        "files",
        help="1-6 signed files, space separated",
        nargs="+",
        type=utilities.signed_file_args)
    parser.set_defaults()
    args = parser.parse_args(sys.argv[1:])
    if args.folder is None:
        args.folder = os.getcwd()
    if not args.filename.endswith(".exe"):
        args.filename += ".exe"
    pseudocap.make_autoloader(args.filename, args.files, args.folder)


if __name__ == "__main__":
    pseudocap_main()
