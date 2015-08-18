#!/usr/bin/env python3

import argparse  # parse arguments
import sys  # load arguments
from os import getcwd  # local dir
from bbarchivist import bbconstants  # versions/constants
from bbarchivist import utilities  # path checking
from bbarchivist import pseudocap  # actually making the loader


def cap_main():
    """
    Parse arguments from argparse.

    Invoke :func:`bbarchivist.pseudocap.make_autoloader` with arguments.
    """
    parser = argparse.ArgumentParser(
        prog="bb-pseudocap",
        description="cap.exe, implemented in Python",
        epilog="http://github.com/thurask/bbarchivist")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " +
        bbconstants.VERSION)
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
        metavar="DIR")
    parser.set_defaults()
    args = parser.parse_args(sys.argv[1:])
    if args.folder is None:
        args.folder = getcwd()
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
