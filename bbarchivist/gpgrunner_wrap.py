#!/usr/bin/env python3

import argparse
import sys
import os
from . import hashwrapper
from . import bbconstants


def main():
    """
    Parse arguments from argparse/questionnaire.

    Invoke :func:`bbarchivist.hashwrapper.gpgrunner` with those arguments.
    """
    if len(sys.argv) > 1:
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
            default=os.getcwd())
        parser.add_argument(
            "key",
            help="Key to use, 8-character hexadecimal")
        parser.add_argument(
            "password",
            help="Passphrase for key; quote if multi-word")
        parser.set_defaults()
        args = parser.parse_args(sys.argv[1:])
        hashwrapper.gpgrunner(args.folder,
                              args.key,
                              args.password)
    else:
        folder = os.getcwd()
        key = input("KEY ID: ")
        password = input("PASSPHRASE: ")
        print(" ")
        hashwrapper.gpgrunner(
            folder,
            key,
            password)
        smeg = input("Press Enter to exit")  # @UnusedVariable
