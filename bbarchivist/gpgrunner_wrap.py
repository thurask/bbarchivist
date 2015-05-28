#!/usr/bin/env python3

import argparse  # parse arguments
import sys  # load arguments
import os  # path operations
import configparser  # INI reading
import getpass  # invisible passwords (cf. sudo)
from . import hashwrapper  # main program
from . import bbconstants  # constants/versions


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.hashwrapper.gpgrunner` with those arguments.
    """
    parser = argparse.ArgumentParser(
        prog="bb-gpgrunner",
        description="GPG-sign all files in a directory.",
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
    workfolder = args.folder
    config = configparser.ConfigParser()
    homepath = os.path.expanduser("~")
    conffile = os.path.join(homepath, "bbarchivist.ini")
    config.read(conffile)
    key = config.get('gpgrunner', 'key', fallback=None)
    password = config.get('gpgrunner', 'pass', fallback=None)
    if key is None or password is None:
        key = input("PGP KEY (0x12345678): ")
        password = getpass.getpass(prompt="PGP PASSPHRASE: ")
        config['gpgrunner'] = {}
        config['gpgrunner']['key'] = key
        config['gpgrunner']['pass'] = password
        with open(conffile, "w") as configfile:
            config.write(configfile)
    print(" ")
    hashwrapper.gpgrunner(
                          workfolder,
                          key,
                          password)
