#!/usr/bin/env python3
"""Applies hash functions to files."""

import sys  # load arguments
import os  # path operations
from bbarchivist import filehashtools  # main program
from bbarchivist import utilities  # input validation
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015-2016 Thurask"


def filehasher_main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.filehashtools.verifier` with those arguments.
    """
    hashdict = filehashtools.verifier_config_loader()
    filehashtools.verifier_config_writer(hashdict)
    if len(sys.argv) > 1:
        parser = scriptutils.default_parser("bb-filehasher",
                                            "Hash files")
        parser.add_argument(
            "folder",
            help="Working directory, default is local",
            nargs="?",
            default=None,
            type=utilities.file_exists)
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        if args.folder is None:
            args.folder = os.getcwd()
        filehashtools.verifier(args.folder, hashdict)
    else:
        folder = os.getcwd()
        print(" ")
        filehashtools.verifier(folder, hashdict)


if __name__ == "__main__":
    filehasher_main()
