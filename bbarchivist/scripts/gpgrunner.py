#!/usr/bin/env python3
"""Use GPG to sign all files in a directory."""

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015 Thurask"

import argparse  # parse arguments
import sys  # load arguments
import os  # path operations
import getpass  # invisible passwords (cf. sudo)
from bbarchivist import filehashtools  # main program
from bbarchivist import bbconstants  # constants/versions
from bbarchivist import utilities  # bool parsing


def gpgrunner_main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.filehashtools.gpgrunner` with those arguments.
    """
    parser = argparse.ArgumentParser(
        prog="bb-gpgrunner",
        description="Use GPG to sign all files in a directory.",
        epilog="http://github.com/thurask/bbarchivist")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + bbconstants.VERSION)
    parser.add_argument(
        "folder",
        help="Working directory, default is local",
        nargs="?",
        default=None)
    parser.set_defaults()
    args = parser.parse_args(sys.argv[1:])
    if args.folder is None:
        args.folder = os.getcwd()
    workfolder = args.folder
    key, password = filehashtools.gpg_config_loader()
    if key is None or password is None:
        if key is None:
            key = input("PGP KEY (0x12345678): ")
        if password is None:
            password = getpass.getpass(prompt="PGP PASSPHRASE: ")
            write = utilities.s2b(input("SAVE PASSPHRASE (Y/N)?: "))
        if write:
            password2 = password
        else:
            password2 = None
        filehashtools.gpg_config_writer(key, password2)
    print(" ")
    filehashtools.gpgrunner(
        workfolder,
        key,
        password)

if __name__ == "__main__":
    gpgrunner_main()
