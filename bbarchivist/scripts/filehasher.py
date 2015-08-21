#!/usr/bin/env python3

"""Applies hash functions to files."""

import argparse  # parse arguments
import sys  # load arguments
import os  # path operations
from bbarchivist import filehashtools  # main program
from bbarchivist import bbconstants  # constants/versions
from bbarchivist import utilities  # input validation


def filehasher_main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.filehashtools.verifier` with those arguments.
    """
    hashdict = filehashtools.verifier_config_loader()
    filehashtools.verifier_config_writer(hashdict)
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="bb-filehasher",
            description="Applies hash functions to files.",
            epilog="http://github.com/thurask/bbarchivist")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " +
            bbconstants.VERSION)
        parser.add_argument(
            "folder",
            help="Working directory, default is local",
            nargs="?",
            default=None)
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        if args.folder is None:
            args.folder = os.getcwd()
        filehashtools.verifier(args.folder,
                               **hashdict)
    else:
        folder = os.getcwd()
        print(" ")
        filehashtools.verifier(
            folder,
            **hashdict)

if __name__ == "__main__":
    filehasher_main()
