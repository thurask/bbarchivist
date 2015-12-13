#!/usr/bin/env python3
"""cap.exe, implemented in Python."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015 Thurask"

import sys  # load arguments
import os  # local dir
from bbarchivist import utilities  # path checking
from bbarchivist import pseudocap  # actually making the loader
from bbarchivist import scriptutils  # default parser


def cap_main():
    """
    Parse arguments from argparse.

    Invoke :func:`bbarchivist.pseudocap.make_autoloader` with arguments.
    """
    parser = scriptutils.default_parser("bb-pseudocap",
                                        "BlackBerry CAP, in Python.")
    parser.add_argument("filename",
                        help="Filename")
    files = parser.add_argument_group()
    files.add_argument("first",
                       help="First file")
    files.add_argument("second",
                       help="Second file, optional",
                       nargs="?",
                       default=None)
    files.add_argument("third",
                       help="Third file, optional",
                       nargs="?",
                       default=None)
    files.add_argument("fourth",
                       help="Fourth file, optional",
                       nargs="?",
                       default=None)
    files.add_argument("fifth",
                       help="Fifth file, optional",
                       nargs="?",
                       default=None)
    files.add_argument("sixth",
                       help="Sixth file, optional",
                       nargs="?",
                       default=None)
    parser.add_argument(
        "-f",
        "--folder",
        dest="folder",
        help="Working folder",
        default=None,
        metavar="DIR",
        type=utilities.file_exists)
    parser.set_defaults()
    args = parser.parse_args(sys.argv[1:])
    if args.folder is None:
        args.folder = os.getcwd()
    if not args.filename.endswith(".exe"):
        args.filename += ".exe"
    pseudocap.make_autoloader(args.filename,
                              args.first,
                              args.second,
                              args.third,
                              args.fourth,
                              args.fifth,
                              args.sixth,
                              args.folder)

if __name__ == "__main__":
    cap_main()
