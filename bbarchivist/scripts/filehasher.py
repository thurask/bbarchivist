#!/usr/bin/env python3
"""Applies hash functions to files."""

import os  # path operations
import sys  # load arguments

from bbarchivist import argutils  # arguments
from bbarchivist import hashutils  # main program
from bbarchivist import utilities  # input validation

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "2015-2019 Thurask"


def filehasher_main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.hashutils.verifier` with those arguments.
    """
    hashdict = hashutils.verifier_config_loader()
    hashutils.verifier_config_writer(hashdict)
    if len(sys.argv) > 1:
        parser = argutils.default_parser("bb-filehasher", "Hash files")
        parser.add_argument(
            "folder",
            help="Working directory, default is local",
            nargs="?",
            default=None,
            type=argutils.file_exists)
        parser.add_argument(
            "-s",
            "--selective",
            dest="selective",
            help="Filter out files generated by this package",
            default=False,
            action="store_true")
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        args.folder = utilities.dirhandler(args.folder, os.getcwd())
        hashutils.verifier(args.folder, hashdict)
    else:
        folder = os.getcwd()
        print(" ")
        hashutils.verifier(folder, hashdict)


if __name__ == "__main__":
    filehasher_main()
