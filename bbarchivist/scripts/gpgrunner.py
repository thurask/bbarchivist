#!/usr/bin/env python3
"""Use GPG to sign all files in a directory."""

import sys  # load arguments
import os  # path operations
import getpass  # invisible passwords (cf. sudo)
from bbarchivist import filehashtools  # main program
from bbarchivist import utilities  # bool parsing
from bbarchivist import scriptutils  # default parser

__author__ = "Thurask"
__license__ = "WTFPL v2"
__copyright__ = "Copyright 2015 Thurask"


def gpgrunner_main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.filehashtools.gpgrunner` with those arguments.
    """
    parser = scriptutils.default_parser("bb-gpgrunner",
                                        "GPG-sign files")
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
